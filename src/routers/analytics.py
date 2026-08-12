"""管理端学情分析 / 记录管理 / AI 周报接口（admin 专用）

- 学情分析：overview / student / weakness（含与掌握度联动的 student_id 口径）/ report
- 学员答题记录管理：列表 / 详情 / 改评 / 删除
- AI 周报管理：生成 / 列表 / 详情 / 删除

薄弱分析复用 core.mastery 的同一套掌握度算法，与学员端掌握度永不矛盾。
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text, func, case
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User, ExamRecord, AnswerRecord, AIReport, PointsLedger,
    WrongQuestion, Question, Topic, Subject,
)
from schemas import ExamRecordOut, AnswerRecordOut, QuestionOut
from core.deps import require_role
from core.mastery import (
    STATUS_LABEL, _topic_totals, _load_student_rows, _rows_to_sessions, _eval_topic,
)
from core.tier import tier_label

router = APIRouter(prefix="/api/admin", tags=["管理端学情分析"])


# ============ 工具 ============
def _fetch_all(db: Session, sql: str, params: dict = None) -> list:
    """执行查询返回 list[dict]（SQLAlchemy 2.x 用 RowMapping，勿用 row.keys()）"""
    rows = db.execute(text(sql), params or {}).mappings().all()
    return [dict(r) for r in rows]


# ============ 学员答题记录（管理员查看/管理） ============
def _admin_record_out(record: ExamRecord, db: Session, with_answers: bool = True) -> ExamRecordOut:
    """管理员视角的记录序列化：不隐藏任何信息。

    与学生端 exam._record_to_out 的区别：
    - code 题的参考代码（question.answer）不置空，管理员可对照批阅；
    - answer_records 里的 user_answer 即学生提交的代码/答案，run_output 为后台实跑结果。
    """
    out = ExamRecordOut.model_validate(record)
    # 兼容旧数据：从积分流水回填本次答题获得的积分
    if out.points_earned == 0:
        ledger = db.query(PointsLedger).filter_by(
            student_id=record.user_id, reason="exam_reward", ref_id=record.id
        ).first()
        if ledger:
            out.points_earned = ledger.delta
    if with_answers:
        ars = db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record.id).all()
        out.answer_records = []
        for ar in ars:
            aro = AnswerRecordOut.model_validate(ar)
            if ar.question:
                qo = QuestionOut.model_validate(ar.question)
                if ar.question.topic:
                    qo.topic_name = ar.question.topic.name
                aro.question = qo  # 管理员可见参考代码，不做隐藏
            out.answer_records.append(aro)
    return out


class AnswerRecordUpdate(BaseModel):
    """管理员修改某题评分/评语"""
    llm_score: int  # 0-100
    llm_feedback: Optional[str] = None


@router.get("/students")
def list_students(_=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """学员列表（含答题次数、最近一次答题时间），供管理端下拉选择。"""
    students = db.query(User).filter(User.role == "student").order_by(User.created_at.asc()).all()
    result = []
    for s in students:
        exam_count = db.query(ExamRecord).filter(ExamRecord.user_id == s.id).count()
        last = (
            db.query(ExamRecord)
            .filter(ExamRecord.user_id == s.id)
            .order_by(ExamRecord.started_at.desc())
            .first()
        )
        result.append({
            "id": s.id,
            "username": s.username,
            "nickname": s.nickname,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "exam_count": exam_count,
            "last_exam_at": last.started_at.isoformat() if last and last.started_at else None,
        })
    return result


@router.get("/students/{student_id}/records", response_model=list[ExamRecordOut])
def student_records(student_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """某学员的全部答题记录列表（不含每题明细，点详情再查）。"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    records = (
        db.query(ExamRecord)
        .filter(ExamRecord.user_id == student_id)
        .order_by(ExamRecord.started_at.desc())
        .all()
    )
    return [_admin_record_out(r, db, with_answers=False) for r in records]


@router.get("/records/{record_id}", response_model=ExamRecordOut)
def admin_record_detail(record_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """某次答题记录的完整明细：每题的题干、学生答案/提交代码、运行结果、正确答案、讲解。"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _admin_record_out(record, db, with_answers=True)


@router.put("/answer-records/{ar_id}")
def admin_update_answer_record(ar_id: int, data: AnswerRecordUpdate, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """管理员修改某道题的评分和评语，修改后自动重算所属答题记录的 score/correct/wrong。"""
    ar = db.query(AnswerRecord).filter(AnswerRecord.id == ar_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="答题明细不存在")
    if data.llm_score < 0 or data.llm_score > 100:
        raise HTTPException(status_code=400, detail="评分必须在 0-100 之间")
    ar.llm_score = data.llm_score
    ar.llm_stars = min(5, max(0, data.llm_score // 20))  # 按分数折算星级
    ar.is_correct = data.llm_score >= 60
    if data.llm_feedback is not None:
        ar.llm_feedback = data.llm_feedback.strip() or None
    # 重算所属 exam_record 的 correct/wrong/score
    record = db.query(ExamRecord).filter(ExamRecord.id == ar.exam_record_id).first()
    if record:
        all_ars = db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record.id).all()
        record.correct = sum(1 for a in all_ars if (a.llm_score or 0) >= 60)
        record.wrong = record.total - record.correct
        record.score = int(record.correct / record.total * 100) if record.total else 0
    db.commit()
    return {"ok": True, "llm_score": ar.llm_score, "is_correct": ar.is_correct,
            "record_score": record.score if record else None,
            "record_correct": record.correct if record else None,
            "record_wrong": record.wrong if record else None}


@router.delete("/records/{record_id}")
def admin_delete_record(record_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """删除某次答题记录（含关联的答题明细），用于清理 0 分/无效记录。"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    # 先删关联答题明细（虽然 cascade=all,delete-orphan 会自动删，显式删更稳妥）
    db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record_id).delete()
    db.delete(record)
    db.commit()
    return {"ok": True}


# ============ 学情分析（4 个接口） ============
@router.get("/analytics/overview")
def analytics_overview(grade: Optional[str] = None, subject_id: Optional[int] = None,
                      tier: Optional[int] = None,
                      _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """总览仪表盘：核心指标 + 近14天趋势(按科目) + 科目/题型正确率 + 活跃榜

    可选过滤: grade(年级, 精确匹配 subjects.grade) / subject_id(科目) / tier(档位)。
    顶部 KPI 始终为全局总量；趋势/正确率/活跃榜受过滤影响（含 tier）。
    """
    # 过滤条件（基于 exam_records.subject_id -> subjects）
    conds, params = [], {}
    if subject_id is not None:
        conds.append("er.subject_id = :sid")
        params["sid"] = subject_id
    if grade:
        conds.append("s.grade = :grade")
        params["grade"] = grade
    if tier is not None:
        conds.append("er.tier = :tier")
        params["tier"] = tier
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    total_ar = db.execute(text(
        "SELECT COUNT(*) c, SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END) ok FROM answer_records")).fetchone()
    total_exams = db.execute(text("SELECT COUNT(*) c FROM exam_records")).fetchone().c
    active_students = db.execute(text(
        "SELECT COUNT(DISTINCT user_id) c FROM exam_records")).fetchone().c
    today = datetime.now().strftime("%Y-%m-%d")
    today_ar = db.execute(text(
        "SELECT COUNT(*) c FROM answer_records ar JOIN exam_records er ON er.id=ar.exam_record_id "
        "WHERE date(er.started_at)=:d"), {"d": today}).fetchone().c
    week_ar = db.execute(text(
        "SELECT COUNT(*) c FROM answer_records ar JOIN exam_records er ON er.id=ar.exam_record_id "
        "WHERE julianday('now') - julianday(er.started_at) <= 7")).fetchone().c

    # 全局聚合趋势（向后兼容）
    _trend_where = ("WHERE julianday('now') - julianday(er.started_at) <= 14"
                    + ((" AND " + " AND ".join(conds)) if conds else ""))
    trend = _fetch_all(db, f"""
        SELECT date(er.started_at) d,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {_trend_where}
        GROUP BY date(er.started_at) ORDER BY d
    """, params)

    # 按科目分组趋势（前端画多线用）
    trend_by_subject = _fetch_all(db, f"""
        SELECT date(er.started_at) d, er.subject_id, s.name subject,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {_trend_where}
        GROUP BY date(er.started_at), er.subject_id ORDER BY d, er.subject_id
    """, params)

    by_subject = _fetch_all(db, f"""
        SELECT s.id subject_id, s.name subject, s.grade, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY s.id ORDER BY total DESC
    """, params)

    by_type = _fetch_all(db, f"""
        SELECT q.type, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY q.type ORDER BY total DESC
    """, params)

    top_students = _fetch_all(db, f"""
        SELECT u.nickname, u.username, COUNT(er.id) exams,
               MAX(er.started_at) last_at
        FROM exam_records er
        JOIN users u ON u.id=er.user_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY er.user_id ORDER BY exams DESC LIMIT 10
    """, params)

    total_cnt = total_ar.c or 0
    ok_cnt = total_ar.ok or 0
    return {
        "totals": {
            "answers": total_cnt,
            "correct_rate": round(ok_cnt / total_cnt * 100, 1) if total_cnt else 0,
            "exams": total_exams,
            "active_students": active_students,
            "today_answers": today_ar,
            "week_answers": week_ar,
        },
        "trend": trend,
        "trend_by_subject": trend_by_subject,
        "by_subject": by_subject,
        "by_type": by_type,
        "top_students": top_students,
        "tier": tier,
        "tier_name": tier_label(tier) if tier is not None else None,
    }


@router.get("/analytics/student/{student_id}")
def analytics_student(student_id: int, subject_id: Optional[int] = None,
                      wrong_limit: int = 10, tier: Optional[int] = None,
                      _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """学员深度档案：成绩趋势 + 科目/知识点正确率 + 高频错题 + 最近动态

    可选 subject_id 过滤 by_topic / top_wrong（知识点正确率与高频错题）。
    tier: 分阶档位（1初级/2进阶/3挑战），不传默认初级；传入后全档案管理口径锁到该档位，
          与掌握度、薄弱榜同一套口径。
    wrong_limit: 高频错题条数，仅允许 10/20/30/50。
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    if wrong_limit not in (10, 20, 30, 50):
        wrong_limit = 10
    if tier is None:
        tier = 1

    # 该学员个人掌握度状态映射（topic_id -> status/label），供 by_topic / top_wrong 联动标注
    mmap = _student_mastery_map(db, student_id, tier)

    # 科目 / 档位过滤条件（复用给 score_trend / by_subject / by_topic / top_wrong / recent）
    _subj_cond = "AND er.subject_id = :sid" if subject_id else ""
    _tier_cond = "AND er.tier = :tier" if tier else ""
    _q_tier_cond = "AND q.tier = :tier" if tier else ""
    _subj_params = {"uid": student_id, "tier": tier, **({"sid": subject_id} if subject_id else {})}

    score_trend = _fetch_all(db, f"""
        SELECT er.id, er.started_at, er.score, er.total, er.correct, s.name subject
        FROM exam_records er JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid {_subj_cond} {_tier_cond} ORDER BY er.started_at
    """, _subj_params)

    by_subject = _fetch_all(db, f"""
        SELECT s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid {_subj_cond} {_tier_cond} GROUP BY s.id ORDER BY total DESC
    """, _subj_params)
    by_topic = _fetch_all(db, f"""
        SELECT t.id topic_id, t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid {_subj_cond} {_q_tier_cond} GROUP BY q.topic_id HAVING COUNT(*)>=2
        ORDER BY (ok*1.0/total) ASC LIMIT 20
    """, _subj_params)
    for r in by_topic:
        m = mmap.get(r["topic_id"]) or {"status": "not_started", "status_label": "未开始"}
        r["status"] = m["status"]
        r["status_label"] = m["status_label"]

    top_wrong = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.id topic_id, t.name topic, s.name subject,
               COUNT(*) wrong_times
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid AND ar.is_correct=0 {_subj_cond} {_q_tier_cond}
        GROUP BY q.id ORDER BY wrong_times DESC LIMIT {wrong_limit}
    """, _subj_params)
    for r in top_wrong:
        m = mmap.get(r["topic_id"]) or {"status": "not_started", "status_label": "未开始"}
        r["status"] = m["status"]
        r["status_label"] = m["status_label"]

    recent = _fetch_all(db, f"""
        SELECT er.id, er.started_at, er.score, er.total, er.correct, s.name subject
        FROM exam_records er JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid {_tier_cond} ORDER BY er.started_at DESC LIMIT 10
    """, {"uid": student_id, "tier": tier})

    return {
        "student": {"id": student.id, "nickname": student.nickname, "username": student.username},
        "tier": tier,
        "tier_name": tier_label(tier),
        "score_trend": score_trend,
        "by_subject": by_subject,
        "by_topic": by_topic,
        "top_wrong": top_wrong,
        "recent": recent,
    }


def _student_mastery_map(db: Session, student_id: int, tier: int = 1) -> dict:
    """复用掌握度算法（core.mastery），返回 {topic_id: {status, status_label, rate, coverage}}。

    tier 化：仅计算指定档位（默认初级）。作用域与学员端掌握度一致 (uid, topic, tier)。
    """
    rows = _load_student_rows(db, student_id)
    sessions = _rows_to_sessions(rows)   # key=(uid, topic_id, tier)
    totals = _topic_totals(db)            # key=(topic_id, tier)
    out = {}
    for (tid, tt_tier), tt in totals.items():
        if tt_tier != tier:
            continue
        ev = _eval_topic(sessions.get((student_id, tid, tt_tier), []), tt)
        out[tid] = {
            "status": ev["status"],
            "status_label": STATUS_LABEL[ev["status"]],
            "rate": ev["rate"],
            "coverage": ev["coverage"],
        }
    return out


@router.get("/analytics/weakness")
def analytics_weakness(subject_id: Optional[int] = None, grade: Optional[str] = None,
                      student_id: Optional[int] = None, tier: Optional[int] = None,
                      _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """知识点薄弱分析：薄弱知识点TOP10 + 反复错题榜 + 低正确率题目

    可选过滤: subject_id(科目) / grade(年级) / student_id(指定学员，联动其个人掌握度) / tier(档位)。
    tier 不传 = 不过滤档位（保留原「全体/个人历史」口径，向后兼容）；传入则三张表均按该档位过滤。
    - 传 student_id 时，薄弱榜按「该学员个人掌握度（指定档位）」口径计算，已通过/精通的课不进榜，
      从根本上与 mastery 一致。
    - 不传 student_id 时保持原「全体学员历史」口径，但每条仍带 topic_id 便于联动。
    """
    conds, params = [], {}
    if subject_id is not None:
        conds.append("q.subject_id = :sid")
        params["sid"] = subject_id
    if grade:
        conds.append("s.grade = :grade")
        params["grade"] = grade
    if tier is not None:
        conds.append("q.tier = :tier")
        params["tier"] = tier
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    # ---------- 学员级（联动个人掌握度）----------
    if student_id is not None:
        mmap = _student_mastery_map(db, student_id, tier or 1)

        # 薄弱知识点：仅列「未通过 / 需复习 / 未开始」的课，按近期正确率升序
        topics = db.query(Topic).all()
        subs = {s.id: s.name for s in db.query(Subject).all()}
        wt = []
        for t in topics:
            if subject_id is not None and t.subject_id != subject_id:
                continue
            sub = db.query(Subject).filter(Subject.id == t.subject_id).first()
            if grade and (sub is None or sub.grade != grade):
                continue
            m = mmap.get(t.id)
            # 只列「练习中 / 需复习」的课：从未练习(not_started)不是薄弱，已通过/精通更不会进榜
            if not m or m["status"] in ("passed", "mastered", "not_started"):
                continue  # 已掌握或从未开始 → 不计入薄弱，与掌握度口径一致
            wt.append({
                "topic_id": t.id,
                "topic": t.name,
                "subject": subs.get(t.subject_id, ""),
                "status": m["status"],
                "status_label": m["status_label"],
                "rate": m["rate"],
                "coverage": m["coverage"],
                "total": None,
            })
        wt.sort(key=lambda x: (x["rate"], x["topic"]))
        wt = wt[:10]

        # 反复错题榜（该学员本人，未掌握的题；tier 给定时只统计该档位）
        rw_filter = [
            WrongQuestion.user_id == student_id,
            WrongQuestion.mastered == False,  # noqa: E712
        ]
        if tier is not None:
            rw_filter.append(Question.tier == tier)
        rw_rows = (
            db.query(
                WrongQuestion.question_id, func.sum(WrongQuestion.wrong_count),
                Question.content, Question.type, Question.topic_id,
                Topic.name, Subject.name,
            )
            .join(Question, WrongQuestion.question_id == Question.id)
            .join(Topic, Question.topic_id == Topic.id)
            .join(Subject, Question.subject_id == Subject.id)
            .filter(*rw_filter)
            .group_by(WrongQuestion.question_id)
            .having(func.sum(WrongQuestion.wrong_count) >= 2)
            .order_by(func.sum(WrongQuestion.wrong_count).desc())
            .limit(15)
            .all()
        )
        repeat_wrong = []
        for qid, times, content, qtype, tid, tname, sname in rw_rows:
            m = mmap.get(tid) or {"status": "not_started", "status_label": "未开始"}
            repeat_wrong.append({
                "qid": qid, "content": content, "type": qtype,
                "topic_id": tid, "topic": tname, "subject": sname,
                "times": int(times),
                "topic_status": m["status"], "topic_status_label": m["status_label"],
            })

        # 低正确率题目（该学员本人；tier 给定时只统计该档位）
        hq_q = (
            db.query(
                AnswerRecord.question_id,
                func.count(AnswerRecord.id),
                func.sum(case((AnswerRecord.is_correct == True, 1), else_=0)),  # noqa: E712
                Question.content, Question.type, Question.topic_id,
                Topic.name, Subject.name,
            )
            .join(Question, AnswerRecord.question_id == Question.id)
            .join(Topic, Question.topic_id == Topic.id)
            .join(Subject, Question.subject_id == Subject.id)
            .filter(AnswerRecord.exam_record_id.in_(
                db.query(ExamRecord.id).filter(ExamRecord.user_id == student_id)
            ))
        )
        if tier is not None:
            hq_q = hq_q.filter(Question.tier == tier)
        hq_rows = (
            hq_q
            .group_by(AnswerRecord.question_id)
            .having(func.count(AnswerRecord.id) >= 3)
            .order_by((func.sum(case((AnswerRecord.is_correct == True, 1), else_=0)) * 100.0 / func.count(AnswerRecord.id)).asc())
            .limit(15)
            .all()
        )
        hard_questions = []
        for qid, total, ok, content, qtype, tid, tname, sname in hq_rows:
            rate = round(ok * 100.0 / total, 1) if total else 0.0
            m = mmap.get(tid) or {"status": "not_started", "status_label": "未开始"}
            hard_questions.append({
                "qid": qid, "content": content, "type": qtype,
                "topic_id": tid, "topic": tname, "subject": sname,
                "total": int(total), "ok": int(ok), "rate": rate,
                "topic_status": m["status"], "topic_status_label": m["status_label"],
            })

        return {
            "mode": "student",
            "student_id": student_id,
            "tier": tier,
            "tier_name": tier_label(tier) if tier is not None else None,
            "weak_topics": wt,
            "repeat_wrong": repeat_wrong,
            "hard_questions": hard_questions,
        }

    # ---------- 原口径（全体学员历史，向后兼容）----------
    weak_topics = _fetch_all(db, f"""
        SELECT t.id topic_id, t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok,
               ROUND(SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) rate
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        {where}
        GROUP BY q.topic_id HAVING COUNT(*)>=5
        ORDER BY rate ASC LIMIT 10
    """, params)

    weak_conds = ["w.mastered=0"]
    if subject_id is not None:
        weak_conds.append("q.subject_id = :sid")
    if grade:
        weak_conds.append("s.grade = :grade")
    if tier is not None:
        weak_conds.append("q.tier = :tier")
    repeat_wrong = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.id topic_id, t.name topic, s.name subject,
               COUNT(DISTINCT w.user_id) students, SUM(w.wrong_count) times
        FROM wrong_questions w
        JOIN questions q ON q.id=w.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        WHERE {' AND '.join(weak_conds)}
        GROUP BY q.id HAVING SUM(w.wrong_count)>=2
        ORDER BY times DESC LIMIT 15
    """, params)

    hard_questions = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.id topic_id, t.name topic, s.name subject,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok,
               ROUND(SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) rate
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        {where}
        GROUP BY q.id HAVING COUNT(*)>=3
        ORDER BY rate ASC LIMIT 15
    """, params)

    return {
        "mode": "global",
        "tier": tier,
        "tier_name": tier_label(tier) if tier is not None else None,
        "weak_topics": weak_topics,
        "repeat_wrong": repeat_wrong,
        "hard_questions": hard_questions,
    }


class ReportRequest(BaseModel):
    student_id: int
    force: bool = False  # True 时强制重新生成，忽略 7 天缓存


@router.post("/analytics/report")
def analytics_report(data: ReportRequest, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """AI 学情周报：聚合学员数据 → LLM 生成自然语言评语（失败返回 502，不造假）"""
    from core import llm_client

    student = db.query(User).filter(User.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    # LLM key 检查交给 llm_client：阿里云不通自动兜底 DeepSeek，全失败才 502

    # 检查7天内是否有缓存的周报（除非强制重新生成）
    if not data.force:
        cached_report = db.query(AIReport).filter(
            AIReport.student_id == data.student_id,
            AIReport.created_at >= text("datetime('now', '-7 days')")
        ).order_by(AIReport.created_at.desc()).first()

        if cached_report:
            return {
                "student": {"id": student.id, "nickname": student.nickname},
                "report": cached_report.report_text,
                "data_summary": cached_report.data_summary,
                "cached": True,  # 标记为缓存返回
                "report_id": cached_report.id
            }

    by_subject = _fetch_all(db, """
        SELECT s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid GROUP BY s.id
    """, {"uid": data.student_id})
    by_topic = _fetch_all(db, """
        SELECT t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid GROUP BY q.topic_id HAVING COUNT(*)>=2
        ORDER BY (ok*1.0/total) ASC LIMIT 8
    """, {"uid": data.student_id})
    exams = _fetch_all(db, """
        SELECT er.score, er.started_at FROM exam_records er
        WHERE er.user_id=:uid ORDER BY er.started_at
    """, {"uid": data.student_id})
    wrong_cnt = db.execute(text(
        "SELECT COUNT(*) c FROM wrong_questions WHERE user_id=:uid AND mastered=0"),
        {"uid": data.student_id}).fetchone().c

    if not exams:
        raise HTTPException(status_code=400, detail="该学员还没有答题记录，无法生成报告")

    subj_lines = []
    for r in by_subject:
        rate = round((r["ok"] or 0) / r["total"] * 100, 1) if r["total"] else 0
        subj_lines.append(f"- {r['subject']}：作答{r['total']}次，正确率{rate}%")
    topic_lines = []
    for r in by_topic:
        rate = round((r["ok"] or 0) / r["total"] * 100, 1) if r["total"] else 0
        topic_lines.append(f"- {r['subject']}/{r['topic']}：作答{r['total']}次，正确率{rate}%")
    scores = [e["score"] for e in exams]
    recent_scores = scores[-5:]
    early_scores = scores[:5] if len(scores) >= 5 else scores

    prompt_data = f"""学员：{student.nickname}
总考试次数：{len(exams)}
未掌握错题数：{wrong_cnt}
各科正确率：
{chr(10).join(subj_lines)}
正确率最低的知识点（最薄弱）：
{chr(10).join(topic_lines) if topic_lines else '（数据不足）'}
最早5次考试分数：{early_scores}
最近5次考试分数：{recent_scores}"""

    system_prompt = """你是一位温暖专业的少儿学习顾问，请根据数据为一位小学生家长写一份学习周报。
要求：
1. 用中文，语气温和鼓励，200-350字
2. 分三段：【学习概况】【进步与亮点】【薄弱点与建议】
3. 基于数据客观分析，不要编造数据里没有的信息
4. 建议要具体可操作（如"建议多练习XX知识点"）
5. 直接输出周报内容，不要额外说明"""

    try:
        report_text = llm_client.llm_chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_data},
            ],
            scenario="weekly_report",
            temperature=0.7,
            max_tokens=800,
            timeout=90,
        ).strip()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI 报告生成失败（含兜底）：{e}")

    # 构建完整的图表数据
    score_trend = []
    for i, exam in enumerate(exams):
        score_trend.append({
            "index": i + 1,
            "score": exam["score"],
            "date": exam["started_at"].strftime("%Y-%m-%d") if hasattr(exam["started_at"], "strftime") else str(exam["started_at"])[:10]
        })

    # 保存报告到数据库
    data_summary = {
        "exams": len(exams),
        "unmastered_wrong": wrong_cnt,
        "avg_score": round(sum(scores) / len(scores), 1),
        "best_score": max(scores),
        "score_trend": score_trend,
        "by_subject": [{"subject": r["subject"], "total": r["total"], "ok": r["ok"],
                        "rate": round(r["ok"] / r["total"] * 100, 1) if r["total"] > 0 else 0}
                       for r in by_subject],
        "weak_topics": [{"topic": r["topic"], "subject": r["subject"], "total": r["total"], "ok": r["ok"],
                         "rate": round(r["ok"] / r["total"] * 100, 1) if r["total"] > 0 else 0}
                        for r in by_topic]
    }

    new_report = AIReport(
        student_id=student.id,
        student_name=student.nickname,
        report_text=report_text,
        data_summary=data_summary
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "student": {"id": student.id, "nickname": student.nickname},
        "report": report_text,
        "data_summary": data_summary,
        "cached": False,  # 新生成的报告
        "report_id": new_report.id
    }


# ============ AI 周报管理 ============
@router.get("/ai-reports")
def list_reports(
    student_id: Optional[int] = None,
    _=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """获取AI周报列表"""
    query = db.query(AIReport)

    if student_id:
        query = query.filter(AIReport.student_id == student_id)

    reports = query.order_by(AIReport.created_at.desc()).all()

    return [{
        "id": r.id,
        "student_id": r.student_id,
        "student_name": r.student_name,
        "report_preview": r.report_text[:100] + "..." if len(r.report_text) > 100 else r.report_text,
        "data_summary": r.data_summary,
        "created_at": r.created_at
    } for r in reports]


@router.get("/ai-reports/{report_id}")
def get_report(
    report_id: int,
    _=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """获取单个AI报告详情"""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    student = db.query(User).filter(User.id == report.student_id).first()

    return {
        "id": report.id,
        "student_id": report.student_id,
        "student_name": report.student_name,
        "report": report.report_text,
        "data_summary": report.data_summary,
        "created_at": report.created_at
    }


@router.delete("/ai-reports/{report_id}")
def delete_report(
    report_id: int,
    _=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """删除AI报告"""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    db.delete(report)
    db.commit()

    return {"message": "报告已删除"}
