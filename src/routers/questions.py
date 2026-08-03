"""题目路由：查询 / 创建 / 批量导入"""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Subject, Topic, Question
from schemas import QuestionOut, QuestionCreate, QuestionUpdate
from core.deps import get_current_user, require_role

router = APIRouter(prefix="/api/questions", tags=["题目"])


@router.get("", response_model=list[QuestionOut])
def list_questions(
    subject_id: int = Query(None),
    topic_id: int = Query(None),
    type: str = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Question)
    if subject_id:
        q = q.filter(Question.subject_id == subject_id)
    if topic_id:
        q = q.filter(Question.topic_id == topic_id)
    if type:
        q = q.filter(Question.type == type)
    items = q.order_by(Question.id).all()
    is_admin = getattr(user, "role", "") == "admin"
    result = []
    for it in items:
        out = QuestionOut.model_validate(it)
        if it.topic:
            out.topic_name = it.topic.name
        # 编程题参考代码对非管理员隐藏（防止学生直接拉接口抄答案）
        if it.type == "code" and not is_admin:
            out.answer = None
        # 阅读理解子题答案/讲解对非管理员隐藏
        if it.type == "reading" and not is_admin:
            out.answer = None
            if out.reading_items:
                out.reading_items = [
                    {"q": x.get("q"), "options": x.get("options")}
                    for x in out.reading_items
                ]
        result.append(out)
    return result


@router.post("", response_model=QuestionOut)
def create_question(data: QuestionCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    q = Question(
        subject_id=data.subject_id,
        topic_id=data.topic_id,
        type=data.type,
        content=data.content,
        options=data.options,
        match_options=data.match_options,
        reading_items=data.reading_items,
        answer=str(data.answer),
        explanation=data.explanation,
        difficulty=data.difficulty,
        is_multiple=data.is_multiple,
        blank_count=data.blank_count,
        blank_answers=data.blank_answers,
        tolerance=data.tolerance,
        expected_output=data.expected_output,
        sample_input=data.sample_input or "",
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return QuestionOut.model_validate(q)


@router.post("/batch", response_model=dict)
def batch_import(items: list[QuestionCreate], db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """批量导入题目"""
    created = 0
    for it in items:
        q = Question(
            subject_id=it.subject_id,
            topic_id=it.topic_id,
            type=it.type,
            content=it.content,
            options=it.options,
            match_options=it.match_options,
            reading_items=it.reading_items,
            answer=str(it.answer),
            explanation=it.explanation,
            difficulty=it.difficulty,
            is_multiple=it.is_multiple,
            blank_count=it.blank_count,
            blank_answers=it.blank_answers,
            tolerance=it.tolerance,
            expected_output=it.expected_output,
            sample_input=it.sample_input or "",
        )
        db.add(q)
        created += 1
    db.commit()
    return {"created": created}


@router.put("/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, data: QuestionUpdate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "answer":
            q.answer = str(v)
        else:
            setattr(q, k, v)
    db.commit()
    db.refresh(q)
    out = QuestionOut.model_validate(q)
    if q.topic:
        out.topic_name = q.topic.name
    return out


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(q)
    db.commit()
    return {"deleted": question_id}
