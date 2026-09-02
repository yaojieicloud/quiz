"""科目与章节路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Subject, Topic, Question, AnswerRecord
from schemas import SubjectOut, TopicOut, UnitOut, SubjectCreate, SubjectUpdate, TopicCreate, TopicUpdate, DeleteTopicResult, ReorderTopicRequest
from core.deps import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["科目与章节"])


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(tier: int = 1, db: Session = Depends(get_db), _=Depends(get_current_user)):
    # 过滤软删：只显示 deprecated=0/null（软删后学员端完全不可见，与课程/题目口径一致）
    subjects = db.query(Subject).filter(
        (Subject.deprecated == 0) | (Subject.deprecated == None)
    ).order_by(Subject.sort_order, Subject.id).all()
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
    # 软删科目下的课程也直接不可见（与 list_subjects 口径一致）
    subj = db.query(Subject).filter(
        Subject.id == subject_id,
        (Subject.deprecated == 0) | (Subject.deprecated == None)
    ).first()
    if not subj:
        return []
    topics = db.query(Topic).filter(
        Topic.subject_id == subject_id,
        (Topic.deprecated == 0) | (Topic.deprecated == None)
    ).order_by(Topic.sort_order, Topic.id).all()
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
    # 各课时被学员做过的题目数（answer_records.question_id，REQ-6 删除预览用）
    done_counts = {}
    if topic_ids:
        done_rows = db.query(Question.topic_id, func.count(func.distinct(AnswerRecord.question_id))).join(
            AnswerRecord, AnswerRecord.question_id == Question.id
        ).filter(
            Question.topic_id.in_(topic_ids),
        ).group_by(Question.topic_id).all()
        for tid, c in done_rows:
            done_counts[tid] = c
    result = []
    for t in topics:
        out = TopicOut.model_validate(t)
        out.question_count = counts.get((t.id, tier), 0)          # 当前档位有效题数
        out.valid_by_tier = {k: counts.get((t.id, k), 0) for k in (1, 2, 3)}  # 各档位有效题数
        out.done_count = done_counts.get(t.id, 0)  # 被学员做过的题目数
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
    # sort_order 默认插到末尾（max + 1024），REQ-6 浮点插入算法
    max_sort = db.query(func.max(Topic.sort_order)).filter(
        Topic.subject_id == data.subject_id
    ).scalar() or 0.0
    t = Topic(subject_id=data.subject_id, name=data.name, unit=data.unit,
              sort_order=max_sort + 1024.0,
              tutorial_video_url=data.tutorial_video_url,  # REQ-7
              tutorial_book_url=data.tutorial_book_url,     # REQ-7
              tutorial_embed_html=data.tutorial_embed_html)  # REQ-7
    db.add(t)
    db.commit()
    db.refresh(t)
    out = TopicOut.model_validate(t)
    out.question_count = 0
    return out


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


# REQ-5（2026-08-25）：科目状态更新（active ↔ completed）
# ⚠️ 必须放在 /subjects/{id} DELETE 之前，避免 DELETE 路由先捕获子路径
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


@router.delete("/subjects/{subject_id}", response_model=DeleteTopicResult)
def delete_subject(subject_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """软/硬删除分流（REQ-6-2），口径与 delete_topic 完全一致。

    软删：科目+课程+题目全 deprecated=1，学员端完全不可见（做题记录保留）
    硬删：物理删（级联清题目和课程）
    """
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="科目不存在")

    # 统计：题数 / 有做题的题数（⚠️ 必须查 answer_records.question_id，勿查 exam_records）
    q_ids = [r[0] for r in db.query(Question.id).filter(Question.subject_id == subject_id).all()]
    done_q = db.query(func.count(func.distinct(AnswerRecord.question_id))).filter(
        AnswerRecord.question_id.in_(q_ids)
    ).scalar() if q_ids else 0
    qcount = len(q_ids)

    if qcount > 0 and done_q > 0:
        # 软删：subjects/topics/questions 全置 deprecated=1
        s.deprecated = 1
        db.query(Topic).filter(Topic.subject_id == subject_id).update({"deprecated": 1})
        db.query(Question).filter(Question.subject_id == subject_id).update({"deprecated": 1})
        db.commit()
        return DeleteTopicResult(
            mode="soft", topic_count=1, question_count=qcount,
            message=f"科目「{s.name}」及{qcount}道题目已软删，学员端不可见"
        )
    else:
        # 物理删：cascade 删课程+题目+科目
        db.query(Topic).filter(Topic.subject_id == subject_id).delete()
        db.query(Question).filter(Question.subject_id == subject_id).delete()
        db.delete(s)
        db.commit()
        return DeleteTopicResult(
            mode="hard", topic_count=1, question_count=qcount,
            message=f"科目「{s.name}」及{qcount}道题目已永久删除"
        )


@router.put("/topics/reorder", response_model=dict)
def reorder_topic(body: ReorderTopicRequest, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """拖拽重排（REQ-6）：浮点插入算法 new_sort = (prev + next) / 2。

    ⚠️ 路由声明顺序：本路由必须在 /topics/{topic_id} 之前，
       否则 FastAPI 会把 "reorder" 误解析为 topic_id。
    """
    topic = db.query(Topic).filter(Topic.id == body.id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="课程不存在")

    prev_sort = None
    next_sort = None

    if body.prev_id is not None:
        prev = db.query(Topic).filter(Topic.id == body.prev_id).first()
        if prev:
            prev_sort = prev.sort_order

    if body.next_id is not None:
        nxt = db.query(Topic).filter(Topic.id == body.next_id).first()
        if nxt:
            next_sort = nxt.sort_order

    if prev_sort is None and next_sort is None:
        return {"id": topic.id, "sort_order": topic.sort_order}

    if prev_sort is None:
        new_sort = next_sort / 2.0           # 拖到最前
    elif next_sort is None:
        new_sort = prev_sort + 1024.0        # 拖到最后
    else:
        new_sort = (prev_sort + next_sort) / 2.0  # 两者之间

    topic.sort_order = new_sort
    db.commit()
    return {"id": topic.id, "sort_order": new_sort}


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


@router.delete("/topics/{topic_id}", response_model=DeleteTopicResult)
def delete_topic(topic_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    """软/硬删除分流（REQ-6）。

    硬删：无题目 或 题目无学员做题记录 → 物理删除课程+题目。
    软删：有题目 且 有学员做题记录 → 课程+题目置 deprecated=1，历史数据保留。
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 1. 查题目数量
    q_count = db.query(Question).filter(Question.topic_id == topic_id).count()

    # 2. 查有学员做题记录的题目数量
    # ⚠️ 必须查 answer_records.question_id（单题作答明细表，存 question_id）
    # exam_records 是聚合表（无 question_id），查错会导致所有有历史数据的课程被硬删
    if q_count > 0:
        q_ids = [r.id for r in
                 db.query(Question.id).filter(Question.topic_id == topic_id).all()]
        done_count = db.query(AnswerRecord.id).filter(
            AnswerRecord.question_id.in_(q_ids)
        ).distinct().count()
    else:
        done_count = 0

    # 3. 分流
    if q_count > 0 and done_count > 0:
        topic.deprecated = 1
        db.query(Question).filter(Question.topic_id == topic_id).update(
            {Question.deprecated: True}, synchronize_session=False
        )
        db.commit()
        return DeleteTopicResult(
            mode="soft",
            topic_count=1,
            question_count=q_count,
            message=f"课程「{topic.name}」及{q_count}道题目已软删除（不可见，历史记录保留）",
        )
    else:
        db.query(Question).filter(Question.topic_id == topic_id).delete(synchronize_session=False)
        db.delete(topic)
        db.commit()
        return DeleteTopicResult(
            mode="hard",
            topic_count=1,
            question_count=q_count,
            message=f"课程「{topic.name}」及{q_count}道题目已永久删除",
        )



