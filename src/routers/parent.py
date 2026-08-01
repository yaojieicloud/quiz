"""家长视角路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, ParentChild, ExamRecord, WrongQuestion
from schemas import ExamRecordOut, WrongQuestionOut, StatsOverview
from routers.exam import _record_to_out
from routers.stats import overview as stats_overview
from core.deps import get_current_user

router = APIRouter(prefix="/api/parent", tags=["家长视角"])


def _check_child(parent: User, child_id: int, db: Session) -> User:
    if parent.role != "parent":
        raise HTTPException(status_code=403, detail="仅家长可访问")
    link = db.query(ParentChild).filter(ParentChild.parent_id == parent.id, ParentChild.child_id == child_id).first()
    if not link:
        raise HTTPException(status_code=403, detail="未绑定该孩子")
    child = db.query(User).filter(User.id == child_id, User.role == "student").first()
    if not child:
        raise HTTPException(status_code=404, detail="孩子不存在")
    return child


@router.get("/children/{child_id}/records", response_model=list[ExamRecordOut])
def child_records(child_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _check_child(user, child_id, db)
    records = db.query(ExamRecord).filter(ExamRecord.user_id == child_id).order_by(ExamRecord.started_at.desc()).all()
    return [_record_to_out(r, db, with_answers=False) for r in records]


@router.get("/children/{child_id}/wrong", response_model=list[WrongQuestionOut])
def child_wrong(child_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _check_child(user, child_id, db)
    from routers.exam import my_wrong_questions
    # 复用逻辑：用 child 的身份查
    items = db.query(WrongQuestion).filter(WrongQuestion.user_id == child_id).order_by(WrongQuestion.last_wrong_at.desc()).all()
    from routers.exam import _build_question_out
    result = []
    for w in items:
        out = WrongQuestionOut.model_validate(w)
        if w.question:
            out.question = _build_question_out(w.question)
        result.append(out)
    return result


@router.get("/children/{child_id}/stats", response_model=StatsOverview)
def child_stats(child_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _check_child(user, child_id, db)
    # 临时构造一个 child user 对象调用 overview 逻辑
    child = _check_child(user, child_id, db)
    return stats_overview(user=child, db=db)
