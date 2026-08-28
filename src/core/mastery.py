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
RATE_WINDOW = 100               # 正确率只看最近 N 题（滑动窗口），防止历史欠账无限放大
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
    """加载某学员全部答题明细：返回 (is_correct, topic_id, qid, tier, exam_id, finished_at, uid)
    按 finished_at 降序排列（最新答题在前），用于滑动窗口计算。
    """
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
        .filter(Question.deprecated == False)  # noqa: E712
        .order_by(ExamRecord.finished_at.desc())  # 按时间降序，最新在前
    )
    if question_ids is not None:
        q = q.filter(Question.id.in_(question_ids))
    return q.all()


def _rows_to_stats(rows, window=RATE_WINDOW):
    """rows: 按 finished_at 降序排列的答题明细
    返回 key=(uid, topic_id, tier) 的统计 dict，包含全量统计和窗口统计。
    
    窗口统计：只取最近 window 道题（按时间倒序），用于计算"近期正确率"。
    """
    by_key = defaultdict(lambda: {
        "N": 0, "D": set(), "C": 0,              # 全量统计
        "recent_N": 0, "recent_C": 0             # 窗口统计（最近 window 题）
    })
    
    for is_correct, topic_id, qid, tier, exam_id, finished_at, uid in rows:
        k = (uid, topic_id, tier)
        # 全量统计
        by_key[k]["N"] += 1
        by_key[k]["D"].add(qid)
        if is_correct:
            by_key[k]["C"] += 1
        
        # 窗口统计（只取最近 window 题）
        if by_key[k]["recent_N"] < window:
            by_key[k]["recent_N"] += 1
            if is_correct:
                by_key[k]["recent_C"] += 1
    
    return by_key


def eval_topic_tier(sessions_by_key, totals_by_tier, student_id, topic_id, tier):
    """便捷封装：取某 (学员,课,档位) 的掌握度评估。

    sessions_by_key: _rows_to_stats 产出的 {key: {N,D,C,recent_N,recent_C}}
    totals_by_tier: _topic_totals 产出的 {(topic_id,tier): Q}
    返回字段与旧版兼容：status/rate/coverage/total/correct/sessions/topic_total
    其中 rate 使用窗口正确率（最近 RATE_WINDOW 题）。
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
    recent_N, recent_C = st["recent_N"], st["recent_C"]
    
    # 正确率使用窗口统计（最近 RATE_WINDOW 题）
    R = recent_C / recent_N if recent_N else 0.0
    
    # 覆盖度：只统计活跃题目（deprecated=0），防止 D > Q 导致超过 100%
    Ccov = min(D / Q, 1.0) if Q else 0.0
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


def calc_mastery_pct(status, rate, coverage, N, Q):
    """计算精通度百分比（0-100），供前端展示。

    逻辑：
    - status == 'mastered' → 100
    - 否则取 min(R/90%, Ccov/80%, N/threshold) × 100，封顶 99
    - 无答题 → 0

    参数：
        status: 当前状态（mastered/practicing/not_started 等）
        rate: 正确率（0-100）
        coverage: 覆盖度（0-100）
        N: 累计答题次数
        Q: 题库总量

    返回：0-100 的整数或浮点数
    """
    if status == "mastered":
        return 100
    if N == 0 or Q == 0:
        return 0
    thr_n = max(int(Q * MASTER_ANSWERS_RATIO), MIN_ANSWERS_FLOOR)
    rate_ratio = min(rate / (MASTER_RATE * 100), 1.0)
    cov_ratio = min(coverage / (MASTER_COV * 100), 1.0)
    n_ratio = min(N / thr_n, 1.0)
    return min(rate_ratio, cov_ratio, n_ratio) * 100


def diagnose_bottleneck(rate, coverage, N, Q):
    """诊断未提升的瓶颈原因，返回简化文案 key。

    优先级：按距门槛差距从大到小排序，返回差距最大的一项。

    参数：
        rate: 正确率（0-100）
        coverage: 覆盖度（0-100）
        N: 累计答题次数
        Q: 题库总量

    返回：
        "rate" / "coverage" / "count" / None（全部达标时应已精通）
    """
    if Q == 0:
        return None
    thr_n = max(int(Q * MASTER_ANSWERS_RATIO), MIN_ANSWERS_FLOOR)
    rate_gap = max(0, MASTER_RATE * 100 - rate)
    cov_gap = max(0, MASTER_COV * 100 - coverage)
    n_gap = max(0, thr_n - N)

    if rate_gap <= 0 and cov_gap <= 0 and n_gap <= 0:
        return None

    gaps = {"rate": rate_gap, "coverage": cov_gap, "count": n_gap}
    return max(gaps, key=gaps.get)
