"""科目与章节路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Subject, Topic, Question
from schemas import SubjectOut, TopicOut, UnitOut, SubjectCreate, SubjectUpdate, TopicCreate, TopicUpdate
from core.deps import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["科目与章节"])


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db), _=Depends(get_current_user)):
    subjects = db.query(Subject).order_by(Subject.sort_order, Subject.id).all()
    result = []
    for s in subjects:
        out = SubjectOut.model_validate(s)
        out.question_count = db.query(Question).filter(Question.subject_id == s.id).count()
        result.append(out)
    return result


@router.post("/subjects", response_model=SubjectOut)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    if db.query(Subject).filter(Subject.name == data.name).first():
        raise HTTPException(status_code=400, detail="科目已存在")
    s = Subject(name=data.name, description=data.description, icon=data.icon,
                grade=data.grade, category=data.category)
    db.add(s)
    db.commit()
    db.refresh(s)
    return SubjectOut.model_validate(s)


@router.get("/subjects/{subject_id}/topics", response_model=list[TopicOut])
def list_topics(subject_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).order_by(Topic.sort_order, Topic.id).all()
    result = []
    for t in topics:
        out = TopicOut.model_validate(t)
        out.question_count = db.query(Question).filter(Question.topic_id == t.id).count()
        result.append(out)
    return result


@router.get("/subjects/{subject_id}/units", response_model=list[UnitOut])
def list_units(subject_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """返回该科目的单元列表（去重），供前端按单元分组。
    文化类科目用于折叠展示；编程类科目 unit 全为 None，仅返回一条"未分单元"。
    """
    topics = db.query(Topic).filter(Topic.subject_id == subject_id).all()
    topic_ids = [t.id for t in topics]
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
        qcount = 0
        if info["topic_ids"]:
            qcount = db.query(Question).filter(Question.topic_id.in_(info["topic_ids"])).count()
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
