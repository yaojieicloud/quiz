"""掌握度 / 课通过模型

判定模型（学员 × 科目 × 课/知识点）：
  取该课「最近 3 次练习」的答题作为近期窗口：
    R = 近期答对 / 近期总答            # 近期正确率
    C = 近期答过的不重复题数 / 该课活跃题数   # 覆盖度
  通过   = 样本够(近期总答≥min(8,课总题数) 且 场次≥2)
          且 R≥90% 且 C≥50% 且 最近3次练习各自正确率均≥85%
  精通   = 样本够 且 R≥95% 且 C≥80% 且 最近3次练习各自正确率均≥90%
  需复习 = 当前未通过，但历史上任一段连续3次练习曾达标（怕遗忘）
  未开始 = 该课无任何答题
  练习中 = 其余（有答题但未达通过）
"""
from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User, ParentChild, ExamRecord, AnswerRecord, Question, Subject, Topic,
)
from core.deps import require_role, get_current_user

router = APIRouter(prefix="/api", tags=["掌握度"])

RECENT = 3
MIN_ANSWERS = 8
MIN_SESSIONS = 2
PASS_R = 0.90
PASS_C = 0.50
PASS_SESSION_R = 0.85
MASTER_R = 0.95
MASTER_C = 0.80
MASTER_SESSION_R = 0.90

STATUS_LABEL = {
    "not_started": "未开始",
    "practicing": "练习中",
    "passed": "通过",
    "mastered": "精通",
    "review": "需复习",
}


def _topic_totals(db: Session) -> dict:
    """每课活跃（未弃用）题数。"""
    rows = (
        db.query(Question.topic_id, func.count(Question.id))
        .filter(Question.deprecated == False)  # noqa: E712
        .group_by(Question.topic_id)
        .all()
    )
    return {tid: n for tid, n in rows}


def _load_student_rows(db: Session, student_id: int, question_ids=None):
    q = (
        db.query(
            AnswerRecord.is_correct,
            Question.topic_id,
            Question.id,
            ExamRecord.id,
            ExamRecord.finished_at,
            ExamRecord.user_id,
        )
        .join(ExamRecord, AnswerRecord.exam_record_id == ExamRecord.id)
        .join(Question, AnswerRecord.question_id == Question.id)
        .filter(ExamRecord.user_id == student_id)
    )
    if question_ids is not None:
        q = q.filter(Question.id.in_(question_ids))
    return q.all()


def _rows_to_sessions(rows):
    """rows: (is_correct, topic_id, qid, exam_id, finished_at, user_id)
    返回 {(topic_id 或 (uid,topic_id)): [session, ...]}，session 按时间倒序。"""
    by_key = defaultdict(lambda: defaultdict(list))
    for is_correct, topic_id, qid, exam_id, finished_at, uid in rows:
        by_key[(uid, topic_id)][exam_id].append((is_correct, qid, finished_at))
    result = {}
    for key, exams in by_key.items():
        sess = []
        for exam_id, items in exams.items():
            fa = items[0][2]
            sess.append({"finished_at": fa, "answers": [(c, q) for c, q, _ in items]})
        sess.sort(key=lambda s: s["finished_at"] or datetime.min, reverse=True)
        result[key] = sess
    return result


def _eval_window(sessions, topic_total, recent_only=True):
    """对给定 sessions（已倒序）的【最近 RECENT 次】窗口做判定。"""
    recent = sessions[:RECENT]
    total = sum(len(s["answers"]) for s in recent)
    correct = sum(1 for s in recent for (c, _) in s["answers"] if c)
    R = correct / total if total else 0.0
    distinct = len(set(q for s in recent for (_, q) in s["answers"]))
    C = distinct / topic_total if topic_total else 0.0
    per = []
    for s in recent:
        t = len(s["answers"])
        cc = sum(1 for (c, _) in s["answers"] if c)
        per.append(cc / t if t else 1.0)
    sample_ok = total >= min(MIN_ANSWERS, topic_total or MIN_ANSWERS) and len(recent) >= MIN_SESSIONS
    passed = (
        sample_ok
        and R >= PASS_R
        and C >= PASS_C
        and all(r >= PASS_SESSION_R for r in per)
    )
    mastered = (
        sample_ok
        and R >= MASTER_R
        and C >= MASTER_C
        and all(r >= MASTER_SESSION_R for r in per)
    )
    return {
        "sample_ok": sample_ok,
        "R": R,
        "C": C,
        "per": per,
        "total": total,
        "correct": correct,
        "passed": passed,
        "mastered": mastered,
        "topic_total": topic_total,
    }


def _eval_topic(sessions, topic_total):
    if not sessions:
        return {
            "status": "not_started",
            "rate": 0.0,
            "coverage": 0.0,
            "total": 0,
            "correct": 0,
            "sessions": 0,
            "topic_total": topic_total,
        }
    cur = _eval_window(sessions, topic_total)
    # 是否已通过：当前窗口通过，或历史上任一段连续 RECENT 次练习通过
    ever_passed = cur["passed"]
    if not ever_passed:
        n = len(sessions)
        for i in range(max(0, n - RECENT + 1)):
            w = _eval_window(sessions[i : i + RECENT], topic_total)
            if w["passed"]:
                ever_passed = True
                break
    if cur["mastered"]:
        status = "mastered"
    elif cur["passed"]:
        status = "passed"
    elif ever_passed:
        status = "review"
    else:
        status = "practicing"
    return {
        "status": status,
        "rate": round(cur["R"] * 100, 1),
        "coverage": round(cur["C"] * 100, 1),
        "total": cur["total"],
        "correct": cur["correct"],
        "sessions": len(sessions[:RECENT]),
        "topic_total": topic_total,
    }


def _build_student_mastery(db: Session, sid: int) -> dict:
    """构造某学员（按 user.id）的掌握度结构，供学员端/家长端/管理端复用。"""
    rows = _load_student_rows(db, sid)
    sessions_by_key = _rows_to_sessions(rows)  # key=(uid, topic_id)
    totals = _topic_totals(db)
    topics = db.query(Topic).all()

    out = []
    for sub in db.query(Subject).order_by(Subject.id).all():
        tlist = []
        for t in topics:
            if t.subject_id != sub.id:
                continue
            sess = sessions_by_key.get((sid, t.id), [])
            ev = _eval_topic(sess, totals.get(t.id, 0))
            tlist.append(
                {
                    "topic_id": t.id,
                    "name": t.name,
                    "unit": t.unit,
                    "status": ev["status"],
                    "status_label": STATUS_LABEL[ev["status"]],
                    "rate": ev["rate"],
                    "coverage": ev["coverage"],
                    "total": ev["total"],
                    "correct": ev["correct"],
                    "sessions": ev["sessions"],
                    "topic_total": ev["topic_total"],
                }
            )
        tlist.sort(key=lambda x: (x["unit"] or "", x["name"]))
        if tlist:
            out.append({"subject_id": sub.id, "name": sub.name, "topics": tlist})
    return {"student_id": sid, "subjects": out}


@router.get("/mastery/me")
def mastery_me(
    student_id: Optional[int] = Query(None, description="家长/管理员查看孩子时必填"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """学员看自己的掌握度；家长看已绑定孩子的掌握度；管理员查看指定学员。"""
    if user.role == "student":
        sid = user.id
    elif user.role == "parent":
        if not student_id:
            raise HTTPException(status_code=400, detail="家长需指定 student_id")
        link = (
            db.query(ParentChild)
            .filter(ParentChild.parent_id == user.id, ParentChild.child_id == student_id)
            .first()
        )
        if not link:
            raise HTTPException(status_code=403, detail="未绑定该孩子")
        sid = student_id
    elif user.role == "admin":
        if not student_id:
            raise HTTPException(status_code=400, detail="管理员需指定 student_id")
        sid = student_id
    else:
        raise HTTPException(status_code=403, detail="无权限")
    return _build_student_mastery(db, sid)


@router.get("/admin/mastery/student/{student_id}")
def admin_student_mastery(
    student_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：查看单个学员的掌握度（与学员端同一套算法，供薄弱分析联动跳转）。"""
    student = (
        db.query(User).filter(User.id == student_id, User.role == "student").first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    return _build_student_mastery(db, student_id)


@router.get("/admin/mastery")
def class_mastery(
    subject_id: int = Query(..., description="科目 ID"),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：某科目下每课、按每位学员拆分的掌握度矩阵（落实到人）。"""
    sub = db.query(Subject).filter(Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="科目不存在")
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.unit, Topic.name)
        .all()
    )
    if not topics:
        return {"subject": {"id": subject_id, "name": sub.name}, "total_students": 0, "topics": []}

    qids = [q.id for q in db.query(Question.id).filter(Question.subject_id == subject_id).all()]
    totals = _topic_totals(db)
    rows = (
        db.query(
            AnswerRecord.is_correct,
            Question.topic_id,
            Question.id,
            ExamRecord.id,
            ExamRecord.finished_at,
            ExamRecord.user_id,
        )
        .join(ExamRecord, AnswerRecord.exam_record_id == ExamRecord.id)
        .join(Question, AnswerRecord.question_id == Question.id)
        .filter(Question.id.in_(qids))
        .all()
    )
    sessions_by_key = _rows_to_sessions(rows)  # key=(uid, topic_id)
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.id)
        .all()
    )
    total_students = len(students)

    result = []
    for t in topics:
        tt = totals.get(t.id, 0)
        counts = {"passed": 0, "mastered": 0, "review": 0, "practicing": 0, "not_started": 0}
        started = 0
        cells = {}
        for s in students:
            sess = sessions_by_key.get((s.id, t.id), [])
            ev = _eval_topic(sess, tt)
            counts[ev["status"]] += 1
            if ev["status"] != "not_started":
                started += 1
            cells[s.id] = {
                "status": ev["status"],
                "status_label": STATUS_LABEL[ev["status"]],
                "rate": ev["rate"],
                "coverage": ev["coverage"],
            }
        passed_master = counts["passed"] + counts["mastered"]
        pass_rate = round(passed_master / total_students * 100, 1) if total_students else 0.0
        mastery_rate = round(counts["mastered"] / total_students * 100, 1) if total_students else 0.0
        result.append(
            {
                "topic_id": t.id,
                "name": t.name,
                "unit": t.unit,
                "topic_total": tt,
                "counts": counts,
                "started": started,
                "pass_rate": pass_rate,
                "mastery_rate": mastery_rate,
                "cells": cells,
            }
        )
    return {
        "subject": {"id": subject_id, "name": sub.name},
        "total_students": total_students,
        "students": [
            {
                "id": s.id,
                "name": s.nickname or s.username,
                "username": s.username,
            }
            for s in students
        ],
        "topics": result,
    }
