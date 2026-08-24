"""积分系统 · 管理端接口（核销 + 配置 CRUD）

- GET  /api/admin/redeem/pending          全部待兑换实物（转盘 + 直兑）
- POST /api/admin/redeem/approve          核销（{source: play|direct, id}）
- GET  /api/admin/points/ledger           按学员查流水（?student_id=）
- GET/POST/PUT/DELETE /api/admin/scoring-rules     积分矩阵配置
- GET/POST/PUT/DELETE /api/admin/wheel-prizes      转盘奖品配置
- GET/POST/PUT/DELETE /api/admin/redeem-items       直兑商城配置
- GET/PUT /api/admin/config                全局键值配置
均 require_role("admin")。详见 docs/积分系统与大转盘方案.md
"""
from datetime import datetime

from core.times import to_iso_utc
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User, StudentPoints, PointsLedger, WheelPrize, Play,
    DirectRedemption, RedeemItem, ScoringRule, Config, LLMCall,
    StudentMastery, Subject, Topic,
)
from core.deps import require_role

router = APIRouter(prefix="/api/admin", tags=["积分系统·管理端"])
admin_user = Depends(require_role("admin"))


# ---------------- 请求模型 ----------------
class ApproveRequest(BaseModel):
    source: str  # play | direct
    id: int


class ScoringRuleIn(BaseModel):
    question_count: int
    score_band: int
    points: int
    subject_id: Optional[int] = None  # NULL=全局默认；非空=科目专属
    is_active: bool = True


class WheelPrizeIn(BaseModel):
    mode: str = "wheel"
    name: str
    type: str = "physical"  # virtual / physical
    virtual_payload: Optional[str] = None
    weight: int = 1
    is_active: bool = True
    sort_order: int = 0


class RedeemItemIn(BaseModel):
    name: str
    type: str = "physical"
    cost: int
    virtual_payload: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class ConfigIn(BaseModel):
    value: str


class PointsAdjustIn(BaseModel):
    student_id: int
    delta: int          # 正为发放，负为扣减
    reason: str = "admin_adjust"


# ---------------- 积分调整（验收/补偿用） ----------------
@router.post("/points/adjust")
def adjust_points(req: PointsAdjustIn, _: User = admin_user, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == req.student_id, User.role.in_(["student", "admin"])).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员/管理员不存在")
    if req.delta == 0:
        raise HTTPException(status_code=400, detail="delta 不能为 0")
    sp = _ensure_student_points(db, student.id)
    new_balance = sp.balance + req.delta
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="调整后余额不能为负")
    sp.balance = new_balance
    db.add(PointsLedger(
        student_id=student.id, delta=req.delta,
        reason=req.reason, ref_id=None, balance_after=sp.balance,
    ))
    db.commit()
    return {"ok": True, "student_id": student.id, "balance": sp.balance}


def _ensure_student_points(db: Session, student_id: int) -> StudentPoints:
    sp = db.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
    if not sp:
        sp = StudentPoints(student_id=student_id, balance=0)
        db.add(sp)
        db.flush()
    return sp
@router.get("/redeem/pending")
def pending_redeemments(_: User = admin_user, db: Session = Depends(get_db)):
    plays = (
        db.query(Play)
        .filter(Play.is_physical == True, Play.status == "pending")  # noqa: E712
        .order_by(Play.created_at.desc())
        .all()
    )
    directs = (
        db.query(DirectRedemption)
        .filter(DirectRedemption.status == "pending")
        .order_by(DirectRedemption.created_at.desc())
        .all()
    )
    # 一次性取回涉及的学员姓名（nickname 优先，缺则 username）
    ids = {p.student_id for p in plays} | {d.student_id for d in directs}
    name_map = {
        u.id: (u.nickname or u.username)
        for u in db.query(User).filter(User.id.in_(ids)).all()
    } if ids else {}
    out = []
    for p in plays:
        out.append({
            "source": "play", "id": p.id, "student_id": p.student_id,
            "student_name": name_map.get(p.student_id, f"学员#{p.student_id}"),
            "name": p.prize_name, "mode": p.mode,
            "created_at": to_iso_utc(p.created_at),
        })
    for d in directs:
        item = db.query(RedeemItem).filter(RedeemItem.id == d.item_id).first()
        out.append({
            "source": "direct", "id": d.id, "student_id": d.student_id,
            "student_name": name_map.get(d.student_id, f"学员#{d.student_id}"),
            "name": item.name if item else f"兑换项#{d.item_id}",
            "mode": "direct",
            "created_at": to_iso_utc(d.created_at),
        })
    return {"items": out}


@router.post("/redeem/approve")
def approve_redeemment(req: ApproveRequest, admin: User = admin_user, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    if req.source == "play":
        rec = db.query(Play).filter(Play.id == req.id).first()
        if not rec:
            raise HTTPException(status_code=404, detail="记录不存在")
        if rec.status != "pending":
            raise HTTPException(status_code=400, detail="该记录已核销或已发放")
        rec.status = "redeemed"
        rec.redeemed_at = now
        rec.redeemed_by = admin.id
    elif req.source == "direct":
        rec = db.query(DirectRedemption).filter(DirectRedemption.id == req.id).first()
        if not rec:
            raise HTTPException(status_code=404, detail="记录不存在")
        if rec.status != "pending":
            raise HTTPException(status_code=400, detail="该记录已核销或已发放")
        rec.status = "redeemed"
        rec.redeemed_at = now
        rec.redeemed_by = admin.id
    else:
        raise HTTPException(status_code=400, detail="未知 source")
    db.commit()
    return {"ok": True}


@router.get("/points/ledger")
def admin_ledger(student_id: int, _: User = admin_user, db: Session = Depends(get_db)):
    q = db.query(PointsLedger).filter(PointsLedger.student_id == student_id)
    items = q.order_by(PointsLedger.created_at.desc()).all()
    sp = db.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
    return {
        "balance": sp.balance if sp else 0,
        "items": [
            {
                "id": it.id, "delta": it.delta, "reason": it.reason,
                "ref_id": it.ref_id, "balance_after": it.balance_after,
                "created_at": to_iso_utc(it.created_at),
            }
            for it in items
        ],
    }


# ---------------- 配置：scoring_rules ----------------
@router.get("/scoring-rules")
def list_scoring_rules(_: User = admin_user, db: Session = Depends(get_db)):
    rows = db.query(ScoringRule).order_by(ScoringRule.subject_id, ScoringRule.question_count, ScoringRule.score_band).all()
    return [{"id": r.id, "question_count": r.question_count, "score_band": r.score_band,
             "points": r.points, "subject_id": r.subject_id, "is_active": r.is_active} for r in rows]


@router.post("/scoring-rules")
def create_scoring_rule(body: ScoringRuleIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = ScoringRule(**body.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id}


@router.put("/scoring-rules/{rid}")
def update_scoring_rule(rid: int, body: ScoringRuleIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(ScoringRule).filter(ScoringRule.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="规则不存在")
    for k, v in body.dict().items():
        setattr(r, k, v)
    db.commit()
    return {"ok": True}


@router.delete("/scoring-rules/{rid}")
def delete_scoring_rule(rid: int, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(ScoringRule).filter(ScoringRule.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ---------------- 配置：wheel_prizes ----------------
@router.get("/wheel-prizes")
def list_wheel_prizes(_: User = admin_user, db: Session = Depends(get_db)):
    rows = db.query(WheelPrize).order_by(WheelPrize.mode, WheelPrize.sort_order).all()
    return [{"id": r.id, "mode": r.mode, "name": r.name, "type": r.type,
             "virtual_payload": r.virtual_payload, "weight": r.weight,
             "is_active": r.is_active, "sort_order": r.sort_order} for r in rows]


@router.post("/wheel-prizes")
def create_wheel_prize(body: WheelPrizeIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = WheelPrize(**body.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id}


@router.put("/wheel-prizes/{pid}")
def update_wheel_prize(pid: int, body: WheelPrizeIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(WheelPrize).filter(WheelPrize.id == pid).first()
    if not r:
        raise HTTPException(status_code=404, detail="奖品不存在")
    for k, v in body.dict().items():
        setattr(r, k, v)
    db.commit()
    return {"ok": True}


@router.delete("/wheel-prizes/{pid}")
def delete_wheel_prize(pid: int, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(WheelPrize).filter(WheelPrize.id == pid).first()
    if not r:
        raise HTTPException(status_code=404, detail="奖品不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ---------------- 配置：redeem_items ----------------
@router.get("/redeem-items")
def list_redeem_items(_: User = admin_user, db: Session = Depends(get_db)):
    rows = db.query(RedeemItem).order_by(RedeemItem.sort_order).all()
    return [{"id": r.id, "name": r.name, "type": r.type, "cost": r.cost,
             "virtual_payload": r.virtual_payload, "is_active": r.is_active,
             "sort_order": r.sort_order} for r in rows]


@router.post("/redeem-items")
def create_redeem_item(body: RedeemItemIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = RedeemItem(**body.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id}


@router.put("/redeem-items/{iid}")
def update_redeem_item(iid: int, body: RedeemItemIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(RedeemItem).filter(RedeemItem.id == iid).first()
    if not r:
        raise HTTPException(status_code=404, detail="兑换项不存在")
    for k, v in body.dict().items():
        setattr(r, k, v)
    db.commit()
    return {"ok": True}


@router.delete("/redeem-items/{iid}")
def delete_redeem_item(iid: int, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(RedeemItem).filter(RedeemItem.id == iid).first()
    if not r:
        raise HTTPException(status_code=404, detail="兑换项不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ---------------- 配置：config ----------------
@router.get("/config")
def list_config(_: User = admin_user, db: Session = Depends(get_db)):
    rows = db.query(Config).all()
    return {r.key: r.value for r in rows}


# ---------------- LLM 调用审计日志 ----------------
@router.get("/llm-calls")
def list_llm_calls(
    scenario: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 30,
    _: User = admin_user,
    db: Session = Depends(get_db),
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    q = db.query(LLMCall)
    if scenario:
        q = q.filter(LLMCall.scenario == scenario)
    if provider:
        q = q.filter(LLMCall.provider == provider)
    if status:
        q = q.filter(LLMCall.status == status)
    total = q.count()
    items = (
        q.order_by(LLMCall.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": it.id, "scenario": it.scenario, "provider": it.provider,
                "model": it.model, "prompt_tokens": it.prompt_tokens,
                "completion_tokens": it.completion_tokens, "total_tokens": it.total_tokens,
                "status": it.status, "latency_ms": it.latency_ms,
                "error": it.error, "created_at": to_iso_utc(it.created_at),
            }
            for it in items
        ],
    }


@router.put("/config/{key}")
def put_config(key: str, body: ConfigIn, _: User = admin_user, db: Session = Depends(get_db)):
    r = db.query(Config).filter(Config.key == key).first()
    if r:
        r.value = body.value
    else:
        r = Config(key=key, value=body.value)
        db.add(r)
    db.commit()
    return {"ok": True, "key": key, "value": body.value}


# ============ 精通奖励测试（仅预览，不写任何数据） ============
@router.post("/test-mastery-reward")
def test_mastery_reward(_: User = admin_user, db: Session = Depends(get_db)):
    """模拟达成精通的弹窗预览：取真实精通样本 + 当前 wheel_cost，纯只读不发积分。"""
    cost = 20
    row = db.query(Config).filter(Config.key == "wheel_cost").first()
    if row:
        try:
            cost = int(row.value)
        except (ValueError, TypeError):
            pass

    rewards = []
    # 优先取真实精通记录做样本（更像真的）
    samples = (
        db.query(StudentMastery)
        .filter(StudentMastery.status == "mastered")
        .order_by(StudentMastery.updated_at.desc())
        .limit(2)
        .all()
    )
    if samples:
        topic_map = {t.id: t for t in db.query(Topic).filter(
            Topic.id.in_([s.topic_id for s in samples])).all()}
        subject_map = {s.id: s for s in db.query(Subject).filter(
            Subject.id.in_([s.subject_id for s in samples])).all()}
        for i, m in enumerate(samples):
            t = topic_map.get(m.topic_id)
            sub = subject_map.get(m.subject_id)
            rewards.append({
                "subject_name": sub.name if sub else "科目",
                "topic_name": t.name if t else "课程",
                "tier": m.tier,
                "points": cost,
                "mode": "new" if i == 0 else "retroactive",  # 演示两种标签
            })
    else:
        rewards = [
            {"subject_name": "数学", "topic_name": "示例课程A", "tier": 1, "points": cost, "mode": "new"},
            {"subject_name": "语文", "topic_name": "示例课程B", "tier": 2, "points": cost, "mode": "retroactive"},
        ]
    return {"nickname": "测试学员", "wheel_cost": cost, "rewards": rewards}
