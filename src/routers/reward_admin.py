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
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User, StudentPoints, PointsLedger, WheelPrize, Play,
    DirectRedemption, RedeemItem, ScoringRule, Config, LLMCall,
    Subject, SubjectPoints,
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
    out = []
    for p in plays:
        out.append({
            "source": "play", "id": p.id, "student_id": p.student_id,
            "name": p.prize_name, "mode": p.mode,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    for d in directs:
        item = db.query(RedeemItem).filter(RedeemItem.id == d.item_id).first()
        out.append({
            "source": "direct", "id": d.id, "student_id": d.student_id,
            "name": item.name if item else f"兑换项#{d.item_id}",
            "mode": "direct",
            "created_at": d.created_at.isoformat() if d.created_at else None,
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
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in items
        ],
    }


# ---------------- 配置：scoring_rules ----------------
@router.get("/scoring-rules")
def list_scoring_rules(_: User = admin_user, db: Session = Depends(get_db)):
    rows = db.query(ScoringRule).order_by(ScoringRule.question_count, ScoringRule.score_band).all()
    return [{"id": r.id, "question_count": r.question_count, "score_band": r.score_band,
             "points": r.points, "is_active": r.is_active} for r in rows]


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
                "error": it.error, "created_at": it.created_at.isoformat() if it.created_at else None,
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


# ============ 科目课程积分设置 ============
class SubjectPointsBatchIn(BaseModel):
    subject_ids: list[int]
    p100: int = 5
    p90: int = 4
    p80: int = 3


@router.get("/subject-points")
def list_subject_points(_: User = admin_user, db: Session = Depends(get_db)):
    """列出全部科目及其积分覆盖设置（无覆盖则 has_override=false）。"""
    subs = db.query(Subject).order_by(Subject.sort_order, Subject.id).all()
    ov_map = {sp.subject_id: sp for sp in db.query(SubjectPoints).all()}
    return {
        "items": [
            {
                "subject_id": s.id,
                "subject_name": s.name,
                "category": s.category,
                "has_override": s.id in ov_map,
                "p100": ov_map[s.id].p100 if s.id in ov_map else None,
                "p90": ov_map[s.id].p90 if s.id in ov_map else None,
                "p80": ov_map[s.id].p80 if s.id in ov_map else None,
            }
            for s in subs
        ]
    }


@router.post("/subject-points/batch")
def batch_set_subject_points(req: SubjectPointsBatchIn, _: User = admin_user, db: Session = Depends(get_db)):
    """批量设置/覆盖多个科目的三档积分（upsert）。"""
    if req.p100 < 0 or req.p90 < 0 or req.p80 < 0:
        raise HTTPException(status_code=400, detail="积分不能为负")
    updated = 0
    for sid in req.subject_ids:
        sub = db.query(Subject).filter(Subject.id == sid).first()
        if not sub:
            continue
        sp = db.query(SubjectPoints).filter(SubjectPoints.subject_id == sid).first()
        if not sp:
            sp = SubjectPoints(subject_id=sid)
            db.add(sp)
        sp.p100, sp.p90, sp.p80 = req.p100, req.p90, req.p80
        updated += 1
    db.commit()
    return {"ok": True, "updated": updated}


@router.delete("/subject-points/{subject_id}")
def reset_subject_points(subject_id: int, _: User = admin_user, db: Session = Depends(get_db)):
    """删除某科目的积分覆盖，恢复为全局默认。"""
    n = db.query(SubjectPoints).filter(SubjectPoints.subject_id == subject_id).delete()
    db.commit()
    return {"ok": True, "deleted": n}
