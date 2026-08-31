"""科目与章节路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Subject, Topic, Question
from schemas import SubjectOut, TopicOut, UnitOut, SubjectCreate, SubjectUpdate, TopicCreate, TopicUpdate
from core.deps import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["科目与章节"])


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(tier: int = 1, db: Session = Depends(get_db), _=Depends(get_current_user)):
    subjects = db.query(Subject).order_by(Subject.sort_order, Subject.id).all()
    # 有效题数 = 排除弃用 + 按档位过滤（所有出题都必须带档位/弃用过滤，避免把弃用题或跨档题算进来）
    sub_ids = [s.id for s in subjects]
    counts = {}
    if sub_ids:
        rows = db.query(Question.subject_id, Question.tier, func.count()).filter(
            Question.subject_id.in_(sub_ids),
            (Question.deprecated == None) | (Question.deprecated == False),
        ).group_by(Question.subject_id, Question.tier).all()
        for sid, t, c in rows:
            counts[(sid, t)] = c
    result = []
    for s in subjects:
        out = SubjectOut.model_validate(s)
        out.question_count = counts.get((s.id, tier), 0)
        out.available_types = [
            r[0] for r in db.query(Question.type)
            .filter(
                Question.subject_id == s.id,
                (Question.deprecated == None) | (Question.deprecated == False),  # 排除废弃题，与组卷/掌握度口径一致
            )
            .distinct().all()
        ]
        # 有效题型 = allowed_types ∩ available_types（未配置时不限制）
        if s.allowed_types:
            allowed = set(s.allowed_types)
            out.available_types = [t for t in out.available_types if t in allowed]
        result.append(out)
    return result


@router.post("/subjects", response_model=SubjectOut)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    if db.query(Subject).filter(
        Subject.name == data.name,
        Subject.grade == data.grade,
    ).first():
        raise HTTPException(status_code=400, detail="同名同年级科目已存在")
    s = Subject(name=data.name, description=data.description, icon=data.icon,
                grade=data.grade, category=data.category)
    db.add(s)
    db.commit()
    db.refresh(s)
    return SubjectOut.model_validate(s)


@router.get("/subjects/{subject_id}/topics", response_model=list[TopicOut])
def list_topics(subject_id: int, tier: int = 1, db: Session = Depends(get_db), _=Depends(get_current_user)):
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).order_by(Topic.sort_order, Topic.id).all()
    topic_ids = [t.id for t in topics]
    # 各课时按(课时,档位)统计有效题数（排除弃用）；一次聚合，避免 N 次查询
    counts = {}
    if topic_ids:
        rows = db.query(Question.topic_id, Question.tier, func.count()).filter(
            Question.topic_id.in_(topic_ids),
            (Question.deprecated == None) | (Question.deprecated == False),
        ).group_by(Question.topic_id, Question.tier).all()
        for tid, t, c in rows:
            counts[(tid, t)] = c
    result = []
    for t in topics:
        out = TopicOut.model_validate(t)
        out.question_count = counts.get((t.id, tier), 0)          # 当前档位有效题数
        out.valid_by_tier = {k: counts.get((t.id, k), 0) for k in (1, 2, 3)}  # 各档位有效题数
        result.append(out)
    return result


@router.get("/subjects/{subject_id}/units", response_model=list[UnitOut])
def list_units(subject_id: int, tier: int = 1, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """返回该科目的单元列表（去重），供前端按单元分组。
    文化类科目用于折叠展示；编程类科目 unit 全为 None，仅返回一条"未分单元"。
    question_count 为当前档位下、排除弃用的有效题数合计。
    """
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
    topic_ids = [t.id for t in topics]
    cnt = {}
    if topic_ids:
        rows = db.query(Question.topic_id, func.count()).filter(
            Question.topic_id.in_(topic_ids),
            (Question.deprecated == None) | (Question.deprecated == False),
            Question.tier == tier,
        ).group_by(Question.topic_id).all()
        for tid, c in rows:
            cnt[tid] = c
    # 按 unit 分组
    groups = {}
    for t in topics:
        key = t.unit  # 可能为 None
        if key not in groups:
            groups[key] = {"topic_ids": [], "topic_count": 0}
        groups[key]["topic_ids"].append(t.id)
        groups[key]["topic_count"] += 1
    result = []
    for unit, info in groups.items():
        qcount = sum(cnt.get(tid, 0) for tid in info["topic_ids"])
        result.append(UnitOut(unit=unit, topic_count=info["topic_count"], question_count=qcount))
    return result


@router.post("/topics", response_model=TopicOut)
def create_topic(data: TopicCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    t = Topic(subject_id=data.subject_id, name=data.name, unit=data.unit)
    db.add(t)
    db.commit()
    db.refresh(t)
    return TopicOut.model_validate(t)


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="科目不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "allowed_types" and v is not None:
            # 空数组 = 不限制（存 NULL）
            v = v if len(v) else None
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    out = SubjectOut.model_validate(s)
    out.question_count = db.query(Question).filter(Question.subject_id == s.id).count()
    return out


@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="科目不存在")
    qcount = db.query(Question).filter(Question.subject_id == subject_id).count()
    if qcount > 0:
        raise HTTPException(status_code=400, detail=f"该科目下还有 {qcount} 道题目，请先删除题目后再删除科目")
    db.query(Topic).filter(Topic.subject_id == subject_id).delete()
    db.delete(s)
    db.commit()
    return {"deleted": subject_id}


# REQ-5：科目状态更新（active ↔ completed）
@router.patch("/subjects/{subject_id}/status")
def update_subject_status(
    subject_id: int,
    status: str,  # query param: "active" | "completed"
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="科目不存在")
    if status not in ("active", "completed"):
        raise HTTPException(status_code=400, detail="status 必须是 active 或 completed")
    s.status = status
    db.commit()
    return {"id": subject_id, "status": status}


@router.put("/topics/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, data: TopicUpdate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="章节不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    out = TopicOut.model_validate(t)
    out.question_count = db.query(Question).filter(Question.topic_id == t.id).count()
    return out


@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    t = db.query(Topic).filter(Topic.id == topic_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="章节不存在")
    qcount = db.query(Question).filter(Question.topic_id == topic_id).count()
    if qcount > 0:
        raise HTTPException(status_code=400, detail=f"该章节下还有 {qcount} 道题目，请先删除题目后再删除章节")
    db.delete(t)
    db.commit()
    return {"deleted": topic_id}
