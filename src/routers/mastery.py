"""掌握度 / 课通过模型（路由层）

判定算法见 core/mastery.py（被 routers.analytics 复用，确保掌握度与薄弱分析同一套口径）。
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, ParentChild, ExamRecord, AnswerRecord, Question, Subject, Topic, StudentMastery
from core.deps import require_role, get_current_user
from core.mastery import STATUS_LABEL, _topic_totals, compute_mastery_for_topics, upsert_student_mastery, compute_mastery_for_topics, upsert_student_mastery
from core.tier import ACTIVE_TIERS, tier_label

router = APIRouter(prefix="/api", tags=["掌握度"])


def _build_student_mastery(db: Session, sid: int, tier: int = None) -> dict:
    """构造某学员的掌握度结构，读 StudentMastery 缓存表（不再实时全算）。

    tier 化：每个课按档位（初级/进阶/挑战）分别给出掌握度，results.topics[].tiers
    为 {tier: {status, status_label, rate, coverage, ...}}。tier 参数用于标记前端默认选中档位。
    表中无记录的 (课,档位) 视为 not_started。
    """
    # 一次性查该学员全部 mastery 行，按 (topic_id, tier) 索引
    rows = db.query(StudentMastery).filter(StudentMastery.student_id == sid).all()
    mmap = {(r.topic_id, r.tier): r for r in rows}
    topics = db.query(Topic).all()

    out = []
    for sub in db.query(Subject).order_by(Subject.id).all():
        tlist = []
        for t in topics:
            if t.subject_id != sub.id:
                continue
            tiers = {}
            for tt in ACTIVE_TIERS:
                r = mmap.get((t.id, tt))
                if r:
                    status = r.status
                    rate = r.rate
                    coverage = r.coverage
                    total = r.answered_count
                    correct = r.correct_count
                    sessions = 1 if r.answered_count else 0
                    topic_total = r.topic_total
                else:
                    status = "not_started"
                    rate = 0.0
                    coverage = 0.0
                    total = 0
                    correct = 0
                    sessions = 0
                    topic_total = 0
                tiers[tt] = {
                    "status": status,
                    "status_label": STATUS_LABEL[status],
                    "rate": rate,
                    "coverage": coverage,
                    "total": total,
                    "correct": correct,
                    "sessions": sessions,
                    "topic_total": topic_total,
                }
            tlist.append(
                {
                    "topic_id": t.id,
                    "name": t.name,
                    "unit": t.unit,
                    "sort_order": t.sort_order,
                    "tiers": tiers,
                }
            )
        # 排序键：sort_order 优先（编程类递进序），unit+name 兜底（文化类无 sort_order 时按单元分组）
        tlist.sort(key=lambda x: (x["sort_order"] or 0, x["unit"] or "", x["name"]))
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
    subject_ids: Optional[str] = Query(None, description="逗号分隔的科目 ID，如 '1,2,3'，为空则查全部"),
    tier: int = Query(1, description="分阶档位 1初级 2进阶 3挑战，默认初级"),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：某科目下每课、按每位学员拆分的掌握度矩阵（落实到人，按档位）。

    cells 结构由 {student_id: {...}} 升级为 {student_id: {tier: {...}}}，
    counts / pass_rate / mastery_rate 均按所选 tier 聚合。
    """
    # 解析科目 ID 列表
    if subject_ids:
        ids = [int(x.strip()) for x in subject_ids.split(',') if x.strip()]
        subs = db.query(Subject).filter(Subject.id.in_(ids)).all()
    else:
        subs = db.query(Subject).all()
    if not subs:
        return {"subjects": [], "total_students": 0, "topics": []}

    topic_ids = [t.id for t in db.query(Topic).filter(Topic.subject_id.in_([s.id for s in subs])).all()]
    topics = (
        db.query(Topic)
        .filter(Topic.id.in_(topic_ids))
        .order_by(Topic.sort_order, Topic.unit, Topic.name)
        .all()
    )
    if not topics:
        return {"subjects": [{"id": s.id, "name": s.name} for s in subs], "total_students": 0, "topics": []}

    # 读 StudentMastery 缓存表（不再实时全算）
    mastery_rows = (
        db.query(StudentMastery)
        .filter(StudentMastery.subject_id.in_([s.id for s in subs]), StudentMastery.tier == tier)
        .all()
    )
    mmap = {(r.student_id, r.topic_id): r for r in mastery_rows}
    # 每课该档位的题库总量（覆盖度计算用）
    totals = _topic_totals(db)  # key=(topic_id, tier)
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.id)
        .all()
    )
    total_students = len(students)

    subject_name = {s.id: s.name for s in subs}
    result = []
    for t in topics:
        tt = totals.get((t.id, tier), 0)
        counts = {"passed": 0, "mastered": 0, "review": 0, "practicing": 0, "not_started": 0}
        started = 0
        cells = {}
        for s in students:
            r = mmap.get((s.id, t.id))
            if r:
                status = r.status
                rate = r.rate
                coverage = r.coverage
            else:
                status = "not_started"
                rate = 0.0
                coverage = 0.0
            counts[status] += 1
            if status != "not_started":
                started += 1
            cells[s.id] = {
                tier: {
                    "status": status,
                    "status_label": STATUS_LABEL[status],
                    "rate": rate,
                    "coverage": coverage,
                }
            }
        passed_master = counts["passed"] + counts["mastered"]
        pass_rate = round(passed_master / total_students * 100, 1) if total_students else 0.0
        mastery_rate = round(counts["mastered"] / total_students * 100, 1) if total_students else 0.0
        result.append(
            {
                "topic_id": t.id,
                "name": t.name,
                "subject_name": subject_name.get(t.subject_id, ""),
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
        "subjects": [{"id": s.id, "name": s.name} for s in subs],
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


@router.post("/admin/mastery/recalculate")
def recalculate_student_mastery(
    student_id: int,
    topic_id: int,
    tier: int = 1,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """管理端：重算某学员在某课某档位的精通度。

    仅重算指定的 topic_id，不越界。已达 mastered 的锁定不动。
    """
    # 验证学员存在
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    # 验证 topic 存在
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 重算精通度
    computed = compute_mastery_for_topics(db, student_id, [(topic_id, tier)])
    if not computed:
        raise HTTPException(status_code=400, detail="无法计算精通度")

    # upsert 前检查：如果已达精通，锁定不动
    existing = (
        db.query(StudentMastery)
        .filter(
            StudentMastery.student_id == student_id,
            StudentMastery.topic_id == topic_id,
            StudentMastery.tier == tier,
        )
        .first()
    )
    if existing and existing.status == "mastered":
        return {
            "message": "该学员在此课程已达精通，锁定不动",
            "status": existing.status,
            "rate": existing.rate,
            "coverage": existing.coverage,
        }

    # 执行 upsert
    upsert_student_mastery(db, student_id, computed)
    db.commit()

    # 返回新状态
    new_mastery = (
        db.query(StudentMastery)
        .filter(
            StudentMastery.student_id == student_id,
            StudentMastery.topic_id == topic_id,
            StudentMastery.tier == tier,
        )
        .first()
    )
    return {
        "message": "精通度重算完成",
        "status": new_mastery.status if new_mastery else "not_started",
        "rate": new_mastery.rate if new_mastery else 0.0,
        "coverage": new_mastery.coverage if new_mastery else 0.0,
    }
