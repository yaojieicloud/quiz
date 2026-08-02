"""答题路由：组卷 / 提交判分 / 历史记录 / 错题本"""
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Subject, Question, ExamRecord, AnswerRecord, WrongQuestion
from schemas import (
    ExamStartRequest, ExamStartResponse, ExamSubmitRequest,
    ExamRecordOut, AnswerRecordOut, WrongQuestionOut, QuestionOut, QuestionForExam,
)
from core.deps import get_current_user
from core.code_runner import run_python, normalize_output
from core.llm_grader import grade_code
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
    """连线题判分：比对左右索引匹配，全对=100(5星)。

    answer 格式: "0:2,1:0,2:1" 表示 左0→右2, 左1→右0, 左2→右1
    user_answer 格式相同
    """
    if user_answer is None or str(user_answer).strip() == "":
        return False, "", {"stars": 0, "score": 0, "feedback": ""}

    # 标准化后比对
    user_normalized = _normalize(str(user_answer).replace(" ", ""))
    answer_normalized = _normalize(str(question.answer).replace(" ", ""))
    ok = user_normalized == answer_normalized
    return ok, "", {"stars": 5 if ok else 0, "score": 100 if ok else 0, "feedback": ""}


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
@router.post("/exam/start", response_model=ExamStartResponse)
def start_exam(data: ExamStartRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")

    # 抽题（注意：不创建 exam_record，未交卷不会产生空记录，提交时才落库）
    if data.mode == "wrong":
        wrongs = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user.id, WrongQuestion.mastered == False
        ).all()
        q_ids = [w.question_id for w in wrongs]
        pool = db.query(Question).filter(
            Question.id.in_(q_ids), Question.subject_id == data.subject_id
        ).all() if q_ids else []
    else:
        q = db.query(Question).filter(Question.subject_id == data.subject_id)
        if data.topic_ids:
            q = q.filter(Question.topic_id.in_(data.topic_ids))
        if data.types:
            q = q.filter(Question.type.in_(data.types))
        pool = q.all()

    random.shuffle(pool)
    selected = pool[: data.count]

    questions = []
    for q in selected:
        topic_name = q.topic.name if q.topic else None
        questions.append(QuestionForExam(
            id=q.id, type=q.type, content=q.content, options=q.options,
            match_options=q.match_options,
            topic_name=topic_name, difficulty=q.difficulty,
            explanation=q.explanation if q.type == "code" else None
        ))
    return ExamStartResponse(questions=questions)


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
    db.commit()
    db.refresh(record)
    return _record_to_out(record, db)


# ============ 历史记录 ============
@router.get("/exam/records", response_model=list[ExamRecordOut])
def my_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ExamRecord).filter(ExamRecord.user_id == user.id).order_by(ExamRecord.started_at.desc()).all()
    return [_record_to_out(r, db, with_answers=False) for r in records]


@router.get("/exam/records/{record_id}", response_model=ExamRecordOut)
def record_detail(record_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id, ExamRecord.user_id == user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _record_to_out(record, db, with_answers=True)


def _record_to_out(record: ExamRecord, db: Session, with_answers: bool = True) -> ExamRecordOut:
    out = ExamRecordOut.model_validate(record)
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
