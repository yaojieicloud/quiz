"""答题路由：组卷 / 提交判分 / 历史记录 / 错题本"""
import random
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import User, Subject, Question, ExamRecord, AnswerRecord, WrongQuestion, ScoringRule, StudentPoints, PointsLedger, SubjectPoints, StudentMastery, Topic
from schemas import (
    ExamStartRequest, ExamStartResponse, ExamSubmitRequest,
    ExamRecordOut, AnswerRecordOut, WrongQuestionOut, QuestionOut, QuestionForExam,
    AvailableCountOut,
)
from core.deps import get_current_user
from core.tier import get_tier_multiplier
from core.code_runner import run_python, normalize_output
from core.llm_grader import grade_code
from core.mastery import compute_mastery_for_topics, upsert_student_mastery
from pydantic import BaseModel
router = APIRouter(prefix="/api", tags=["答题"])


def _normalize(s) -> str:
    """答案标准化：去空格(含全角)、全角标点转半角、转小写"""
    if s is None:
        return ""
    s = str(s).strip()
    s = s.replace(" ", "").replace("\u3000", "")
    s = s.replace("，", ",").replace("：", ":").replace("（", "(").replace("）", ")")
    return s.lower()


def _judge(question: Question, user_answer):
    """判分，返回 (is_correct_bool, run_output, llm_info)。

    统一评分体系：llm_score 为唯一评分字段。
    - choice/judge：对=100(5星)，错=0(0星)，不调 LLM。
      多选题需要全部选对才算对。
    - fill（填空题）：逐空比对，支持数字容差；全对=100(5星)。
    - essay（应用题）：调 LLM 评星反馈；降级为有内容即通过。
    - code（编程题）：先沙箱实跑，再调 LLM 评星反馈；LLM 不可用时降级回 stdout 匹配。
    - match（连线题）：比对左右索引匹配，全对=100(5星)。
    - sort（排序题）：比对顺序索引，全对=100(5星)。
    - reading（阅读理解）：按子题比例给分，≥60分算通过。
    """
    if question.type == "code":
        return _judge_code(question, user_answer)
    if question.type == "fill":
        return _judge_fill(question, user_answer)
    if question.type == "essay":
        return _judge_essay(question, user_answer)
    if question.type == "match":
        return _judge_match(question, user_answer)
    if question.type == "sort":
        return _judge_sort(question, user_answer)
    if question.type == "reading":
        return _judge_reading(question, user_answer)
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}
    # choice / judge
    if question.type == "choice" and question.is_multiple:
        # 多选题：逗号分隔索引，全部选对才算对
        ok = _normalize(str(user_answer).replace(" ", "").replace("，", ",")) == _normalize(question.answer.replace(" ", ""))
    else:
        ok = _normalize(str(user_answer)) == _normalize(str(question.answer))
    return ok, "", {"stars": 5 if ok else 0, "score": 100 if ok else 0, "feedback": ""}


def _judge_fill(question: Question, user_answer):
    """填空题判分：逐空比对，支持数字容差。

    - 单空题：直接比对 question.answer，支持容差
    - 多空题：按 | 分割用户答案，与 blank_answers 逐空比对
    """
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    tolerance = question.tolerance if question.tolerance else 0.01

    # 多空题
    if question.blank_count and question.blank_count > 1 and question.blank_answers:
        user_parts = str(user_answer).split("|")
        std_answers = question.blank_answers
        if len(user_parts) != len(std_answers):
            return False, "", {"stars": 0, "score": 0, "feedback": ""}
        for u_part, s_ans in zip(user_parts, std_answers):
            if not _fill_match(u_part, s_ans, tolerance):
                return False, "", {"stars": 0, "score": 0, "feedback": ""}
        return True, "", {"stars": 5, "score": 100, "feedback": ""}

    # 单空题（包括原来的 calc 兼容）
    ok = _fill_match(str(user_answer), question.answer, tolerance)
    return ok, "", {"stars": 5 if ok else 0, "score": 100 if ok else 0, "feedback": ""}


def _fill_match(user_val: str, std_val: str, tolerance: float) -> bool:
    """填空答案比对：先精确匹配，失败后尝试数字容差比对。"""
    # 精确匹配（标准化后）
    if _normalize(user_val) == _normalize(std_val):
        return True
    # 数字容差匹配
    try:
        u = float(user_val.replace(" ", ""))
        s = float(std_val.replace(" ", ""))
        return abs(u - s) <= tolerance
    except (ValueError, TypeError):
        pass
    return False


def _judge_essay(question: Question, user_answer):
    """应用题判分：调 LLM 评星，降级为有内容即通过。"""
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    text = str(user_answer).strip()
    # 降级策略：≥10个字即算通过（60分/3星）
    if len(text) >= 10:
        return True, "", {"stars": 3, "score": 60, "feedback": "有作答，等待老师点评。"}
    # 内容太少
    return False, "", {"stars": 0, "score": 0, "feedback": "回答太简短了，再想想看？"}


def _judge_match(question: Question, user_answer):
    """连线题判分：主判据为 (左索引, 右索引) 索引对集合，顺序无关；全对=100(5星)。

    设计原则（与产品约定一致）：索引对索引本身正确，应作为主判据。
    仅在「右侧选项存在重复文本」时才回退到"右项文本"判分，
    以避免"点了第 2 个 True 而非第 0 个 True"这类误判。

    相比旧逻辑（直接比对字符串顺序）修正：
    1. 判分基于规范索引对集合，忽略学员连线顺序。
    2. 前端提交的右项索引始终为规范索引（data-idx 锁定），不受右侧乱序显示影响。
    3. 重复标签场景下按文本容忍不同实例，保留连线互动乐趣。

    answer / user_answer 格式: "0:2,1:0,2:1"（左索引:右索引，逗号分隔）
    """
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    match_options = question.match_options or []
    # 右侧是否存在重复标签（如多个 True）→ 需要文本回退判分
    norm_opts = [_normalize(str(o)) for o in match_options]
    has_dup = len(norm_opts) != len(set(norm_opts))

    def _index_pairs(s):
        out = set()
        for part in _normalize(str(s)).split(","):
            if ":" not in part:
                continue
            l, r = part.split(":", 1)
            try:
                li, ri = int(l), int(r)
            except ValueError:
                continue
            out.add((li, ri))
        return out

    def _value_pairs(s):
        out = set()
        for part in _normalize(str(s)).split(","):
            if ":" not in part:
                continue
            l, r = part.split(":", 1)
            try:
                li, ri = int(l), int(r)
            except ValueError:
                continue
            if match_options and 0 <= ri < len(match_options):
                out.add((li, norm_opts[ri]))
            else:
                out.add((li, ri))
        return out

    std_idx, usr_idx = _index_pairs(question.answer), _index_pairs(user_answer)
    # 主判据：索引对集合（顺序无关）
    if std_idx == usr_idx:
        return True, "", {"stars": 5, "score": 100, "feedback": ""}
    # 回退判据：仅当右侧有重复标签时，按"右项文本"容忍不同实例
    if has_dup and _value_pairs(question.answer) == _value_pairs(user_answer):
        return True, "", {"stars": 5, "score": 100, "feedback": ""}
    return False, "", {"stars": 0, "score": 0, "feedback": ""}


def _judge_sort(question: Question, user_answer):
    """排序题判分：比对顺序索引，全对=100(5星)。

    answer 格式: "1,0,2,3" 表示正确顺序是 options[1], options[0], options[2], options[3]
    user_answer 格式相同
    """
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    # 标准化后比对
    user_normalized = _normalize(str(user_answer).replace(" ", ""))
    answer_normalized = _normalize(str(question.answer).replace(" ", ""))
    ok = user_normalized == answer_normalized
    return ok, "", {"stars": 5 if ok else 0, "score": 100 if ok else 0, "feedback": ""}


def _judge_reading(question: Question, user_answer):
    """阅读理解判分：逐子题比对，按正确比例给分。

    answer 格式: "1,0,2" 依次是各子题的正确选项索引。
    user_answer 格式相同；未作答的子题按错处理。
    得分 = round(正确数/子题数 * 100)，≥60 算通过；星级 = round(比例*5)。
    """
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    std = _normalize(question.answer).split(",")
    usr = _normalize(str(user_answer)).split(",")
    total = len(std)
    if total == 0:
        return False, "", {"stars": 0, "score": 0, "feedback": ""}
    correct = sum(1 for i in range(total) if i < len(usr) and usr[i] == std[i])
    score = round(correct / total * 100)
    stars = round(correct / total * 5)
    return score >= 60, "", {"stars": stars, "score": score, "feedback": ""}


def _judge_code(question: Question, user_code):
    """实跑孩子代码 + LLM 评星反馈。

    1. 先沙箱执行代码，得到运行结果
    2. 调用 LLM 做星级评分 + 个性化反馈
    3. LLM 不可用时，降级回 stdout 精确匹配的二元判分

    Returns:
        (is_correct: bool, run_output: str, llm_info: dict | None)
        llm_info = {"stars": int, "score": int, "feedback": str} 或 None（降级时）
    """
    run_output = ""
    llm_info = None

    if not user_code or not str(user_code).strip():
        return False, "未提交代码，无法判分。", {"stars": 0, "score": 0, "feedback": ""}

    # ── 第一步：沙箱执行 ──
    sample = question.sample_input or ""
    out, err, rc = run_python(str(user_code), sample)

    if rc != 0:
        # 运行出错（语法/异常/超时）—— 仍尝试 LLM 评分，让其给出诊断
        run_output = f"运行出错：{err.strip()[:300]}" if err else "运行超时"
        llm_info = _try_llm_grade(question, user_code, run_output)
        if llm_info:
            is_ok = llm_info["score"] >= 60
            return is_ok, _format_llm_output(llm_info, run_output), llm_info
        return False, f"❌ 代码运行出错：\n{(err or '').strip()[:500]}", {"stars": 0, "score": 0, "feedback": ""}

    # 正常执行
    run_output = out.strip() or "(代码执行成功，无输出)"
    expected = normalize_output(question.expected_output or "")
    actual = normalize_output(out)

    # ── 第二步：LLM 评分 ──
    llm_info = _try_llm_grade(question, user_code, run_output)
    if llm_info:
        is_ok = llm_info["score"] >= 60  # 三星(60分)及以上算通过
        return is_ok, _format_llm_output(llm_info, run_output), llm_info

    # ── 降级：stdout 精确匹配（返回统一 llm_info 格式）──
    if expected and actual == expected:
        return True, f"✅ 运行通过，输出正确：\n{out.strip()}", {"stars": 5, "score": 100, "feedback": ""}
    if not expected:
        return True, f"✅ 代码运行通过：\n{out.strip()}", {"stars": 5, "score": 100, "feedback": ""}
    return False, (
        f"❌ 输出与预期不符。\n"
        f"【预期】\n{(question.expected_output or '').strip()}\n"
        f"【你的输出】\n{out.strip()}"
    ), {"stars": 0, "score": 0, "feedback": ""}


def _try_llm_grade(question: Question, user_code: str, run_output: str) -> dict | None:
    """尝试调用 LLM 评分，不可用时返回 None。"""
    result = grade_code(
        question_content=question.content or "",
        expected_output=question.expected_output or "",
        user_code=str(user_code),
        run_result=run_output,
    )
    if result["stars"] < 0:
        return None
    return result


def _format_llm_output(llm_info: dict, run_output: str) -> str:
    """将 LLM 评分格式化为前端显示的 run_output 字符串。"""
    stars_str = "★" * llm_info["stars"] + "☆" * (5 - llm_info["stars"])
    return (
        f"{stars_str}  {llm_info['score']}分\n\n"
        f"【老师点评】\n{llm_info['feedback']}\n\n"
        f"【运行结果】\n{run_output}"
    )


def _build_question_out(q: Question) -> QuestionOut:
    out = QuestionOut.model_validate(q)
    if q.topic:
        out.topic_name = q.topic.name
    # 编程题的参考代码不下发给学生（答题记录/错题本接口都走这里）
    if q.type == "code":
        out.answer = None
    return out


# ============ 组卷 ============
def _build_pool(db: Session, subject: Subject, data: ExamStartRequest, user: User = None):
    """构建组卷抽题池（不含 count 截断 / 不含 shuffle）。

    与 start_exam 的抽题口径完全一致：
    - 排除弃用题（deprecated）
    - 仅取所选 tier 档位
    - 指定 topic_ids 时仅取这些课时（多个课时即「合计」）
    - 题型取 请求 types 与 科目 allowed_types 的交集（科目配置为权威闸门）
    返回该选择下「实际可用题数」，供 available-count 接口与前端守卫使用。
    """
    _active = (Question.deprecated == None) | (Question.deprecated == False)
    _tier = Question.tier == data.tier
    if data.mode == "wrong":
        if user is None:
            return []
        wrongs = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user.id, WrongQuestion.mastered == False
        ).all()
        q_ids = [w.question_id for w in wrongs]
        pool = (
            db.query(Question)
            .filter(Question.id.in_(q_ids), Question.subject_id == data.subject_id, _active, _tier)
            .all()
        ) if q_ids else []
        # 错题重做同样受科目题型配置约束（被禁用的题型不参与组卷）
        if subject.allowed_types:
            pool = [q for q in pool if q.type in subject.allowed_types]
        return pool
    q = db.query(Question).filter(Question.subject_id == data.subject_id, _active, _tier)
    if data.topic_ids:
        q = q.filter(Question.topic_id.in_(data.topic_ids))
    # 题型过滤：请求 types 与科目配置 allowed_types 取交集（科目配置是权威闸门，
    # 防止前端隐藏后仍被 API 绕过）；两者都不设则不限制
    if data.types and subject.allowed_types:
        allowed = [t for t in data.types if t in subject.allowed_types]
        if not allowed:
            return []  # 交集为空，无可抽题目
    elif data.types:
        allowed = data.types
    elif subject.allowed_types:
        allowed = subject.allowed_types
    else:
        allowed = None
    if allowed:
        q = q.filter(Question.type.in_(allowed))
    return q.all()


def _rank_pool(db: Session, pool, user: User):
    """4 层优先抽题排序（normal 模式用）。

    层1 未答过的题        → 随机洗牌置最前
    层2 答过且有错的题    → 错次降序（先shuffle再稳定sort保证并列随机）
    层3 答过无错的题      → 做题次数升序（少做的优先），并列随机
    兜底：层2/3 已涵盖全部答过的题，层内随机破并列。
    返回排序后的题列表（未截断）。
    """
    if not pool:
        return pool
    qids = [q.id for q in pool]
    # 该学员在 pool 内每题的做题次数
    ans_rows = (
        db.query(AnswerRecord.question_id, func.count(AnswerRecord.id))
        .join(ExamRecord, AnswerRecord.exam_record_id == ExamRecord.id)
        .filter(ExamRecord.user_id == user.id, AnswerRecord.question_id.in_(qids))
        .group_by(AnswerRecord.question_id)
        .all()
    )
    cnt = {qid: n for qid, n in ans_rows}
    answered = set(cnt.keys())
    # 错题次数
    wrong_rows = (
        db.query(WrongQuestion.question_id, WrongQuestion.wrong_count)
        .filter(WrongQuestion.user_id == user.id, WrongQuestion.question_id.in_(qids))
        .all()
    )
    wrong = {qid: wc for qid, wc in wrong_rows}

    layer1 = [q for q in pool if q.id not in answered]
    random.shuffle(layer1)
    layer2 = [q for q in pool if q.id in answered]
    random.shuffle(layer2)  # 先随机，稳定 sort 后并列项保持随机序
    layer2.sort(key=lambda q: (-wrong.get(q.id, 0), cnt.get(q.id, 0)))
    return layer1 + layer2


@router.post("/exam/available-count", response_model=AvailableCountOut)
def available_count(data: ExamStartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """返回当前选择（科目 + 课时 + 档位 + 题型）下的「实际可用题数」。

    与 start_exam 抽题池逻辑 100% 一致。前端在课时/tier/题型选择变化时调用，
    若 available < 50 则禁用「50题」选项，从而避免学员选了不满 50 题的课时却误选 50 题档位。
    """
    subject = db.query(Subject).filter(Subject.id == data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")
    pool = _build_pool(db, subject, data, user)
    return AvailableCountOut(available=len(pool))


@router.post("/exam/start", response_model=ExamStartResponse)
def start_exam(data: ExamStartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")

    # 题目数量只允许标准档位：1（实操单题）、10、20、50；防止出现 40 题等非预期组卷
    if data.count not in (1, 10, 20, 50):
        raise HTTPException(status_code=400, detail="题目数量只能选择 1、10、20、50 题")

    # 抽题（注意：不创建 exam_record，未交卷不会产生空记录，提交时才落库）
    pool = _build_pool(db, subject, data, user)
    if data.mode == "wrong":
        # 错题重做：仅刷错题，保留纯随机
        random.shuffle(pool)
    else:
        # normal：4 层优先（未答过 > 错次多 > 做题少 > 随机）
        pool = _rank_pool(db, pool, user)
    selected = pool[: data.count]

    questions = []
    for q in selected:
        topic_name = q.topic.name if q.topic else None
        # 阅读理解：子题下发时去掉 answer/explanation（防泄题）
        reading_items = None
        if q.type == "reading" and q.reading_items:
            reading_items = [
                {"q": it.get("q"), "options": it.get("options")}
                for it in q.reading_items
            ]
        questions.append(QuestionForExam(
            id=q.id, type=q.type, content=q.content, options=q.options,
            match_options=q.match_options,
            reading_items=reading_items,
            topic_name=topic_name, difficulty=q.difficulty, tier=q.tier,
            explanation=q.explanation if q.type == "code" else None
        ))
    return ExamStartResponse(questions=questions)


# ============ 积分辅助 ============
def _ensure_student_points(db: Session, student_id: int) -> StudentPoints:
    """获取或创建学员积分余额行，返回最新余额对象。"""
    sp = db.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
    if not sp:
        sp = StudentPoints(student_id=student_id, balance=0)
        db.add(sp)
        db.flush()
    return sp


def _award_exam_points(db: Session, student_id: int, record: ExamRecord) -> int:
    """提交试卷后发放积分。

    优先级：
      0. 掌握度闸门：本次涉及课全部 mastered → 不发分（防刷分）；
      1. 若该科目在 subject_points 有覆盖设置，按 p100/p90/p80 三档命中；
      2. 否则走全局默认 scoring_rules（得分档：100→5、90→4、80→3、<80→0）。
    低于 80 分一律 0 分。
    """
    # 掌握度闸门：本次涉及课若全部精通，不发分（按课×tier 查 StudentMastery 表）
    topic_ids = (
        db.query(Question.topic_id)
        .join(AnswerRecord, AnswerRecord.question_id == Question.id)
        .filter(AnswerRecord.exam_record_id == record.id)
        .distinct()
        .all()
    )
    topic_ids = [t[0] for t in topic_ids]
    if topic_ids:
        mastered_rows = (
            db.query(StudentMastery)
            .filter(
                StudentMastery.student_id == student_id,
                StudentMastery.tier == record.tier,
                StudentMastery.topic_id.in_(topic_ids),
            )
            .all()
        )
        # 必须每课都有记录且全部 mastered 才拦；缺记录说明未精通
        if len(mastered_rows) == len(topic_ids) and all(r.status == "mastered" for r in mastered_rows):
            return 0
    override = (
        db.query(SubjectPoints)
        .filter(SubjectPoints.subject_id == record.subject_id)
        .first()
    )
    if override:
        if record.score >= 100:
            pts = override.p100
        elif record.score >= 90:
            pts = override.p90
        elif record.score >= 80:
            pts = override.p80
        else:
            pts = 0
    else:
        rule = (
            db.query(ScoringRule)
            .filter(
                ScoringRule.score_band <= record.score,
                ScoringRule.is_active == True,  # noqa: E712
            )
            .order_by(ScoringRule.score_band.desc())
            .first()
        )
        pts = rule.points if rule else 0
    # 分阶档位倍率：进阶=初阶×2 等（倍率以 tier_config 表为准）
    if pts > 0:
        pts = pts * get_tier_multiplier(db, record.tier)
    if pts <= 0:
        return 0
    sp = _ensure_student_points(db, student_id)
    sp.balance += pts
    db.add(PointsLedger(
        student_id=student_id,
        delta=pts,
        reason="exam_reward",
        ref_id=record.id,
        balance_after=sp.balance,
    ))
    db.flush()
    return pts


# ============ 提交判分 ============
@router.post("/exam/submit", response_model=ExamRecordOut)
def submit_exam(data: ExamSubmitRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")
    if not data.answers:
        raise HTTPException(status_code=400, detail="没有作答内容，无法提交")
    # 校验所有 question_id 都存在，避免 total 与实际判分题数不一致
    q_ids = [item.question_id for item in data.answers]
    existing = {q.id for q in db.query(Question).filter(Question.id.in_(q_ids)).all()}
    missing = [qid for qid in q_ids if qid not in existing]
    if missing:
        raise HTTPException(status_code=400, detail=f"题目不存在: {missing[:5]}")

    now = datetime.utcnow()
    started_at = now - timedelta(seconds=data.duration_seconds) if data.duration_seconds > 0 else now
    record = ExamRecord(
        user_id=user.id,
        subject_id=data.subject_id,
        subject_name=subject.name,
        mode=data.mode,
        tier=data.tier,  # 记录本次所选分阶档位，积分倍率据此计算
        total=len(data.answers),
        started_at=started_at,
        finished_at=now,
        duration_seconds=data.duration_seconds,
    )
    db.add(record)
    db.flush()

    correct = 0
    for item in data.answers:
        question = db.query(Question).filter(Question.id == item.question_id).first()
        is_correct, run_output, llm_info = _judge(question, item.user_answer)
        ar_score = llm_info["score"]
        if ar_score >= 60:
            correct += 1
        ar = AnswerRecord(
            exam_record_id=record.id,
            question_id=question.id,
            user_answer=item.user_answer,
            run_output=run_output,
            is_correct=(ar_score >= 60),
            llm_score=ar_score,
            llm_stars=llm_info["stars"],
            llm_feedback=llm_info.get("feedback") or None,
        )
        db.add(ar)
        if ar_score < 60:
            wq = db.query(WrongQuestion).filter(
                WrongQuestion.user_id == user.id, WrongQuestion.question_id == question.id
            ).first()
            if wq:
                wq.wrong_count += 1
                wq.last_wrong_at = datetime.utcnow()
                wq.mastered = False
            else:
                db.add(WrongQuestion(user_id=user.id, question_id=question.id))

    record.correct = correct
    record.wrong = record.total - correct
    record.score = int(correct / record.total * 100) if record.total else 0

    db.flush()  # 确保 AnswerRecord 落库可被同事务查询（掌握度闸门/upsert 依赖）

    # 本次涉及的不重复 topic（供掌握度闸门与增量 upsert 共用）
    topic_ids = [t[0] for t in (
        db.query(Question.topic_id)
        .join(AnswerRecord, AnswerRecord.question_id == Question.id)
        .filter(AnswerRecord.exam_record_id == record.id)
        .distinct()
        .all()
    )]

    # ---- 积分获取钩子：按 scoring_rules 查表计分，与成绩同一事务提交 ----
    points_earned = _award_exam_points(db, user.id, record)

    # ---- 掌握度增量更新：对本次涉及的 (topic, tier) 重算并 upsert StudentMastery ----
    if topic_ids:
        pairs = [(tid, record.tier) for tid in topic_ids]
        computed = compute_mastery_for_topics(db, user.id, pairs)
        upsert_student_mastery(db, user.id, computed)

    db.commit()
    db.refresh(record)
    return _record_to_out(record, db, points_earned=points_earned)


# ============ 历史记录 ============
@router.get("/exam/records", response_model=list[ExamRecordOut])
def my_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ExamRecord).filter(ExamRecord.user_id == user.id).order_by(ExamRecord.started_at.desc()).all()
    return [_record_to_out(r, db, with_answers=False) for r in records]


@router.get("/exam/recent-activity")
def my_recent_activity(
    subject_ids: Optional[str] = Query(None, description="逗号分隔的科目 ID，如 '1,2,3'"),
    days: int = Query(7, ge=1, le=90),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """学员端：本人最近刷题动态（与 admin 端结构一致，学员固定为当前用户）。"""
    from routers.analytics import build_recent_activity
    return build_recent_activity(db, user.id, subject_ids, days, 100)


@router.get("/exam/records/{record_id}", response_model=ExamRecordOut)
def record_detail(record_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id, ExamRecord.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _record_to_out(record, db, with_answers=True)


def _record_to_out(record: ExamRecord, db: Session, with_answers: bool = True, points_earned: int = 0) -> ExamRecordOut:
    out = ExamRecordOut.model_validate(record)
    # 兼容旧数据：调用方没传积分时，从 points_ledger 回填（历史记录也能显示）
    if points_earned == 0:
        ledger = db.query(PointsLedger).filter_by(
            student_id=record.user_id, reason="exam_reward", ref_id=record.id
        ).first()
        if ledger:
            points_earned = ledger.delta
    out.points_earned = points_earned
    if with_answers:
        ars = db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record.id).all()
        out.answer_records = []
        for ar in ars:
            aro = AnswerRecordOut.model_validate(ar)
            if ar.question:
                aro.question = _build_question_out(ar.question)
            out.answer_records.append(aro)
    return out


# ============ 错题本 ============
@router.get("/wrong-questions", response_model=list[WrongQuestionOut])
def my_wrong_questions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WrongQuestion).filter(WrongQuestion.user_id == user.id).order_by(WrongQuestion.last_wrong_at.desc()).all()
    result = []
    for w in items:
        out = WrongQuestionOut.model_validate(w)
        if w.question:
            out.question = _build_question_out(w.question)
            # 顺便填入最近一次错答的代码/运行结果/评语/科目名（用于 code 题复盘）
            out.subject_name = w.question.subject.name if w.question.subject else None
            last_ar = db.query(AnswerRecord).join(
                ExamRecord, AnswerRecord.exam_record_id == ExamRecord.id
            ).filter(
                ExamRecord.user_id == user.id,
                AnswerRecord.question_id == w.question_id,
            ).order_by(AnswerRecord.id.desc()).first()
            if last_ar:
                out.user_answer = last_ar.user_answer
                out.run_output = last_ar.run_output
                out.llm_feedback = last_ar.llm_feedback
        result.append(out)
    return result


@router.post("/wrong-questions/{wq_id}/master")
def master_wrong(wq_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id, WrongQuestion.user_id == user.id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")
    wq.mastered = True
    db.commit()
    return {"ok": True}


@router.delete("/wrong-questions/{wq_id}")
def delete_wrong(wq_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wq = db.query(WrongQuestion).filter(WrongQuestion.id == wq_id, WrongQuestion.user_id == user.id).first()
    if not wq:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(wq)
    db.commit()
    return {"ok": True}


# ============ 运行代码（实操题答题时试跑，不判分不落库）============
class RunCodeRequest(BaseModel):
    code: str
    sample_input: str = ""


@router.post("/exam/run-code")
def run_code(data: RunCodeRequest, user: User = Depends(get_current_user)):
    """在沙箱中运行学员代码，返回 stdout/stderr/rc。

    - 不判分、不落库，仅供答题时「▶ 运行」按钮试跑。
    - 复用 core/code_runner.py 的受限沙箱。
    """
    if not data.code or not data.code.strip():
        raise HTTPException(status_code=400, detail="代码不能为空")
    out, err, rc = run_python(data.code, data.sample_input or "")
    return {"output": out, "error": err, "rc": rc}
