"""掌握度公共算法层（被 routers.mastery / routers.analytics / routers.exam 复用，杜绝两套口径）

判定模型（学员 × 课/知识点 × 档位）——累计统计 + 三硬门槛：
  做题数 N  = 该学员在该课该tier的累计答题次数（含重复题重做）
  不重复题 D = 答过的不重复题数
  正确数 C  = 累计答对次数
  正确率 R  = C / N
  覆盖度 Ccov = D / 该课该tier题库总量 Q

  精通 mastered = N >= max(Q*0.8, 10) 且 R >= 0.90 且 Ccov >= 0.80
  通过 passed   = N >= max(Q*0.5, 8)  且 R >= 0.85 且 Ccov >= 0.50
  需复习 review = 当前未通过，但历史累计曾达 passed（即 R>=0.85 且 Ccov>=0.50 且 N>=max(Q*0.5,8) 仍成立，
                  但当前因重做错题导致 R 回落低于 0.85）
  未开始 not_started = 无任何答题
  练习中 practicing = 其余（有答题但未达通过）

科学依据：Bloom 掌握学习（正确率≥85-90%）+ Popham 标准参照测验（样本量≥10-15 题）。
做题数门槛用 max(Q*0.8, 10)：题少时至少 10 次保障样本，题多时要求覆盖 80%。
覆盖度门槛防"只刷几道简单题反复刷"——必须刷遍该课 80% 不同题。

本模块仅依赖 models + database，不依赖 FastAPI/router，避免循环依赖。
"""
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func

from models import AnswerRecord, ExamRecord, Question, StudentMastery

# 阈值常量（精通/通过）
MIN_ANSWERS_FLOOR = 10          # 做题数绝对下限（题少时兜底）
PASS_RATE = 0.85
PASS_COV = 0.50
PASS_ANSWERS_RATIO = 0.50
MASTER_RATE = 0.90
MASTER_COV = 0.80
MASTER_ANSWERS_RATIO = 0.80

STATUS_LABEL = {
    "not_started": "未开始",
    "practicing": "练习中",
    "passed": "通过",
    "mastered": "精通",
    "review": "需复习",
}


def _topic_totals(db) -> dict:
    """每课每档的活跃（未弃用）题数，key=(topic_id, tier)。"""
    rows = (
        db.query(Question.topic_id, Question.tier, func.count(Question.id))
        .filter(Question.deprecated == False)  # noqa: E712
        .group_by(Question.topic_id, Question.tier)
        .all()
    )
    return {(tid, t): n for tid, t, n in rows}


def _load_student_rows(db, student_id: int, question_ids=None):
    """加载某学员全部答题明细：返回 (is_correct, topic_id, qid, tier, exam_id, finished_at, uid)"""
    q = (
        db.query(
            AnswerRecord.is_correct,
            Question.topic_id,
            Question.id,
            Question.tier,
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


def _rows_to_stats(rows):
    """rows: (is_correct, topic_id, qid, tier, exam_id, finished_at, uid)
    返回 key=(uid, topic_id, tier) 的累计统计 dict。
    """
    by_key = defaultdict(lambda: {"N": 0, "D": set(), "C": 0})
    for is_correct, topic_id, qid, tier, exam_id, finished_at, uid in rows:
        k = (uid, topic_id, tier)
        by_key[k]["N"] += 1
        by_key[k]["D"].add(qid)
        if is_correct:
            by_key[k]["C"] += 1
    return by_key


def eval_topic_tier(sessions_by_key, totals_by_tier, student_id, topic_id, tier):
    """便捷封装：取某 (学员,课,档位) 的掌握度评估。

    sessions_by_key: _rows_to_stats 产出的 {key: {N,D,C}} —— 字段名沿用 sessions_by_key 以兼容旧调用方
    totals_by_tier: _topic_totals 产出的 {(topic_id,tier): Q}
    返回字段与旧版兼容：status/rate/coverage/total/correct/sessions/topic_total
    """
    key = (student_id, topic_id, tier)
    st = sessions_by_key.get(key)
    Q = totals_by_tier.get((topic_id, tier), 0)
    if not st or st["N"] == 0 or Q == 0:
        return {
            "status": "not_started",
            "rate": 0.0,
            "coverage": 0.0,
            "total": 0,
            "correct": 0,
            "sessions": 0,
            "topic_total": Q,
        }
    N, D, C = st["N"], len(st["D"]), st["C"]
    R = C / N if N else 0.0
    Ccov = D / Q if Q else 0.0
    thr_master_n = max(int(Q * MASTER_ANSWERS_RATIO), MIN_ANSWERS_FLOOR)
    thr_pass_n = max(int(Q * PASS_ANSWERS_RATIO), 8)

    mastered = N >= thr_master_n and R >= MASTER_RATE and Ccov >= MASTER_COV
    passed = N >= thr_pass_n and R >= PASS_RATE and Ccov >= PASS_COV
    if mastered:
        status = "mastered"
    elif passed:
        status = "passed"
    elif R >= PASS_RATE and Ccov >= PASS_COV and N >= thr_pass_n:
        # 历史曾达通过门槛但当前未通过（重做错题拉低 R）—— 简化：本题当前不区分 review，
        # 统一归 practicing；review 状态由 StudentMastery 表的更新历史判定
        status = "practicing"
    else:
        status = "practicing"
    return {
        "status": status,
        "rate": round(R * 100, 1),
        "coverage": round(Ccov * 100, 1),
        "total": N,
        "correct": C,
        "sessions": 1 if N else 0,  # 兼容字段：有答题记1
        "topic_total": Q,
    }


def compute_mastery_for_topics(db, student_id: int, topic_tier_pairs):
    """批量计算某学员在指定 (topic_id, tier) 列表上的掌握度。

    供 submit_exam 增量 upsert 与回填脚本使用。
    返回 [(topic_id, tier, subject_id, status, rate, coverage, N, D, C, Q)] 列表。
    """
    if not topic_tier_pairs:
        return []
    from models import Topic
    totals = _topic_totals(db)
    # 只加载涉及 topic 的答题，减少开销
    topic_ids = list({tid for tid, _ in topic_tier_pairs})
    rows = _load_student_rows(db, student_id)
    stats = _rows_to_stats(rows)
    topic_objs = {t.id: t for t in db.query(Topic).filter(Topic.id.in_(topic_ids)).all()}
    out = []
    for (tid, tier) in topic_tier_pairs:
        t = topic_objs.get(tid)
        if not t:
            continue
        ev = eval_topic_tier(stats, totals, student_id, tid, tier)
        st = stats.get((student_id, tid, tier))
        N = st["N"] if st else 0
        D = len(st["D"]) if st else 0
        C = st["C"] if st else 0
        out.append((tid, tier, t.subject_id, ev["status"], ev["rate"], ev["coverage"], N, D, C, ev["topic_total"]))
    return out


def upsert_student_mastery(db, student_id: int, computed_rows):
    """将 compute_mastery_for_topics 的结果 upsert 进 StudentMastery 表。"""
    for (tid, tier, subject_id, status, rate, coverage, N, D, C, Q) in computed_rows:
        row = (
            db.query(StudentMastery)
            .filter(StudentMastery.student_id == student_id,
                    StudentMastery.topic_id == tid,
                    StudentMastery.tier == tier)
            .first()
        )
        if row:
            row.status = status
            row.rate = rate
            row.coverage = coverage
            row.answered_count = N
            row.distinct_count = D
            row.correct_count = C
            row.topic_total = Q
            row.subject_id = subject_id
        else:
            db.add(StudentMastery(
                student_id=student_id,
                subject_id=subject_id,
                topic_id=tid,
                tier=tier,
                status=status,
                rate=rate,
                coverage=coverage,
                answered_count=N,
                distinct_count=D,
                correct_count=C,
                topic_total=Q,
            ))
    db.flush()
