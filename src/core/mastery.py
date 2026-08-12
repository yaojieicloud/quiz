"""掌握度公共算法层（被 routers.mastery 与 routers.analytics 复用，杜绝两套口径）

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

本模块仅依赖 models + database，不依赖 FastAPI/router，避免循环依赖。
"""
from collections import defaultdict
from datetime import datetime

from sqlalchemy import func

from models import AnswerRecord, ExamRecord, Question

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


def _topic_totals(db) -> dict:
    """每课每档的活跃（未弃用）题数，key=(topic_id, tier)。

    tier 化后掌握度按「课 × 档位」分别计覆盖度，故题数也按 (课,档) 维度统计。
    """
    rows = (
        db.query(Question.topic_id, Question.tier, func.count(Question.id))
        .filter(Question.deprecated == False)  # noqa: E712
        .group_by(Question.topic_id, Question.tier)
        .all()
    )
    return {(tid, t): n for tid, t, n in rows}


def _load_student_rows(db, student_id: int, question_ids=None):
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


def _rows_to_sessions(rows):
    """rows: (is_correct, topic_id, qid, tier, exam_id, finished_at, user_id)
    返回 key=(uid, topic_id, tier) 的 sessions（掌握度作用域升为 学员×课×档位）。"""
    by_key = defaultdict(lambda: defaultdict(list))
    for is_correct, topic_id, qid, tier, exam_id, finished_at, uid in rows:
        by_key[(uid, topic_id, tier)][exam_id].append((is_correct, qid, finished_at))
    result = {}
    for key, exams in by_key.items():
        sess = []
        for exam_id, items in exams.items():
            fa = items[0][2]
            sess.append({"finished_at": fa, "answers": [(c, q) for c, q, _ in items]})
        sess.sort(key=lambda s: s["finished_at"] or datetime.min, reverse=True)
        result[key] = sess
    return result


def eval_topic_tier(sessions_by_key, totals_by_tier, student_id, topic_id, tier):
    """便捷封装：取某 (学员,课,档位) 的掌握度评估（算法同 _eval_topic，零口径漂移）。"""
    sess = sessions_by_key.get((student_id, topic_id, tier), [])
    return _eval_topic(sess, totals_by_tier.get((topic_id, tier), 0))


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
