"""统计路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Subject, ExamRecord, WrongQuestion, Question
from schemas import StatsOverview, SubjectStats
from core.deps import get_current_user

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/overview", response_model=StatsOverview)
def overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(ExamRecord).filter(ExamRecord.user_id == user.id, ExamRecord.finished_at != None).all()
    total_exams = len(records)
    avg_score = round(sum(r.score for r in records) / total_exams, 1) if total_exams else 0
    best_score = max((r.score for r in records), default=0)
    total_wrong = db.query(WrongQuestion).filter(WrongQuestion.user_id == user.id, WrongQuestion.mastered == False).count()

    subjects = db.query(Subject).order_by(Subject.sort_order, Subject.id).all()
    sub_stats = []
    for s in subjects:
        sub_records = [r for r in records if r.subject_id == s.id]
        sub_wrong = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == user.id, WrongQuestion.mastered == False,
            WrongQuestion.question_id.in_(db.query(Question.id).filter(Question.subject_id == s.id))
        ).count() if db.query(Question).filter(Question.subject_id == s.id).count() else 0
        q_count = db.query(Question).filter(Question.subject_id == s.id).count()
        sub_stats.append(SubjectStats(
            subject_id=s.id,
            subject_name=s.name,
            exam_count=len(sub_records),
            avg_score=round(sum(r.score for r in sub_records) / len(sub_records), 1) if sub_records else 0,
            best_score=max((r.score for r in sub_records), default=0),
            wrong_count=sub_wrong,
            question_count=q_count,
        ))
    return StatsOverview(
        total_exams=total_exams,
        avg_score=avg_score,
        best_score=best_score,
        total_wrong=total_wrong,
        subjects=sub_stats,
    )
