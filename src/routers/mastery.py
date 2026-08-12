"""掌握度 / 课通过模型（路由层）

判定算法见 core/mastery.py（被 routers.analytics 复用，确保掌握度与薄弱分析同一套口径）。
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, ParentChild, ExamRecord, AnswerRecord, Question, Subject, Topic
from core.deps import require_role, get_current_user
from core.mastery import (
    STATUS_LABEL, _topic_totals, _load_student_rows, _rows_to_sessions, _eval_topic,
    eval_topic_tier,
)
from core.tier import ACTIVE_TIERS, tier_label

router = APIRouter(prefix="/api", tags=["掌握度"])


def _build_student_mastery(db: Session, sid: int, tier: int = None) -> dict:
    """构造某学员（按 user.id）的掌握度结构，供学员端/家长端/管理端复用。

    tier 化：每个课按档位（初级/进阶/挑战）分别给出掌握度，results.topics[].tiers
    为 {tier: {status, status_label, rate, coverage, ...}}。tier 参数用于标记前端默认选中档位。
    """
    rows = _load_student_rows(db, sid)
    sessions_by_key = _rows_to_sessions(rows)  # key=(uid, topic_id, tier)
    totals = _topic_totals(db)  # key=(topic_id, tier)
    topics = db.query(Topic).all()

    out = []
    for sub in db.query(Subject).order_by(Subject.id).all():
        tlist = []
        for t in topics:
            if t.subject_id != sub.id:
                continue
            tiers = {}
            for tt in ACTIVE_TIERS:
                ev = eval_topic_tier(sessions_by_key, totals, sid, t.id, tt)
                tiers[tt] = {
                    "status": ev["status"],
                    "status_label": STATUS_LABEL[ev["status"]],
                    "rate": ev["rate"],
                    "coverage": ev["coverage"],
                    "total": ev["total"],
                    "correct": ev["correct"],
                    "sessions": ev["sessions"],
                    "topic_total": ev["topic_total"],
                }
            tlist.append(
                {
                    "topic_id": t.id,
                    "name": t.name,
                    "unit": t.unit,
                    "tiers": tiers,
                }
            )
        tlist.sort(key=lambda x: (x["unit"] or "", x["name"]))
        if tlist:
            out.append({"subject_id": sub.id, "name": sub.name, "topics": tlist})
    return {"student_id": sid, "selected_tier": tier or ACTIVE_TIERS[0], "subjects": out}


@router.get("/mastery/me")
def mastery_me(
    student_id: Optional[int] = Query(None, description="家长/管理员查看孩子时必填"),
    tier: Optional[int] = Query(None, description="分阶档位 1初级 2进阶 3挑战；不传返回全部档位"),
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
    return _build_student_mastery(db, sid, tier=tier)


@router.get("/admin/mastery/student/{student_id}")
def admin_student_mastery(
    student_id: int,
    tier: Optional[int] = Query(None, description="分阶档位；不传返回全部档位"),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：查看单个学员的掌握度（与学员端同一套算法，供薄弱分析联动跳转）。"""
    student = (
        db.query(User).filter(User.id == student_id, User.role == "student").first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    return _build_student_mastery(db, student_id, tier=tier)


@router.get("/admin/mastery")
def class_mastery(
    subject_id: int = Query(..., description="科目 ID"),
    tier: int = Query(1, description="分阶档位 1初级 2进阶 3挑战，默认初级"),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：某科目下每课、按每位学员拆分的掌握度矩阵（落实到人，按档位）。

    cells 结构由 {student_id: {...}} 升级为 {student_id: {tier: {...}}}，
    counts / pass_rate / mastery_rate 均按所选 tier 聚合。
    """
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
    totals = _topic_totals(db)  # key=(topic_id, tier)
    rows = (
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
        .filter(Question.id.in_(qids))
        .all()
    )
    sessions_by_key = _rows_to_sessions(rows)  # key=(uid, topic_id, tier)
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.id)
        .all()
    )
    total_students = len(students)

    result = []
    for t in topics:
        tt = totals.get((t.id, tier), 0)
        counts = {"passed": 0, "mastered": 0, "review": 0, "practicing": 0, "not_started": 0}
        started = 0
        cells = {}
        for s in students:
            sess = sessions_by_key.get((s.id, t.id, tier), [])
            ev = _eval_topic(sess, tt)
            counts[ev["status"]] += 1
            if ev["status"] != "not_started":
                started += 1
            cells[s.id] = {
                tier: {
                    "status": ev["status"],
                    "status_label": STATUS_LABEL[ev["status"]],
                    "rate": ev["rate"],
                    "coverage": ev["coverage"],
                }
            }
        passed_master = counts["passed"] + counts["mastered"]
        pass_rate = round(passed_master / total_students * 100, 1) if total_students else 0.0
        mastery_rate = round(counts["mastered"] / total_students * 100, 1) if total_students else 0.0
        result.append(
            {
                "topic_id": t.id,
                "name": t.name,
                "unit": t.unit,
                "tier": tier,
                "tier_name": tier_label(tier),
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
        "tier": tier,
        "tier_name": tier_label(tier),
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
