"""积分系统 + 大转盘抽奖接口（阶段 1）

学员侧：
- GET  /api/points/balance    当前积分
- GET  /api/points/ledger     积分流水（分页）
- GET  /api/wheel/prizes      当前启用转盘奖品与权重
- POST /api/wheel/spin        扣积分→服务端加权随机→写 plays（事务原子）
- GET  /api/redeem/items      直兑商城列表
- POST /api/redeem/direct     扣积分→写 direct_redemptions
- GET  /api/redeem/mine       我的奖品/待兑换/已兑换

设计原则：参数全可配置、概率服务端决定、原子记账。详见 docs/积分系统与大转盘方案.md
"""
import random
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User, ScoringRule, StudentPoints, PointsLedger,
    WheelPrize, Play, DirectRedemption, RedeemItem, Config,
)
from core.deps import get_current_user

router = APIRouter(prefix="/api", tags=["积分系统"])

DEFAULT_WHEEL_COST = 20


# ---------------- 请求/响应模型 ----------------
class SpinRequest(BaseModel):
    mode: str = "wheel"  # wheel / blindbox（盲盒预留）


class DirectRedeemRequest(BaseModel):
    item_id: int


# ---------------- 内部辅助 ----------------
def _ensure_student_points(db: Session, student_id: int) -> StudentPoints:
    sp = db.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
    if not sp:
        sp = StudentPoints(student_id=student_id, balance=0)
        db.add(sp)
        db.flush()
    return sp


def _cfg_int(db: Session, key: str, default: int) -> int:
    row = db.query(Config).filter(Config.key == key).first()
    if not row:
        return default
    try:
        return int(row.value)
    except (ValueError, TypeError):
        return default


def _cfg_str(db: Session, key: str, default: str) -> str:
    row = db.query(Config).filter(Config.key == key).first()
    return row.value if row else default


def _weighted_pick(prizes) -> WheelPrize:
    weights = [max(p.weight, 0) for p in prizes]
    return random.choices(prizes, weights=weights, k=1)[0]


def _grant_virtual_payload(db: Session, sp: StudentPoints, payload: Optional[str]) -> int:
    """处理虚拟奖品载荷（如 "+2积分" 安慰分），返回实际返还的积分数。"""
    if not payload:
        return 0
    payload = payload.strip()
    if payload.startswith("+"):
        try:
            amount = int(payload[1:])
        except ValueError:
            return 0
        if amount > 0:
            sp.balance += amount
            db.add(PointsLedger(
                student_id=sp.student_id, delta=amount,
                reason="wheel_spin", ref_id=None, balance_after=sp.balance,
            ))
            return amount
    return 0


# ---------------- 学员侧 ----------------
@router.get("/meta")
def public_meta(db: Session = Depends(get_db)):
    """公开元信息（无需登录）：上线弹窗版本号、抽奖费等非敏感配置。"""
    return {
        "launch_popup_version": _cfg_str(db, "launch_popup_version", "v1"),
        "wheel_cost": _cfg_int(db, "wheel_cost", DEFAULT_WHEEL_COST),
    }


@router.get("/points/balance")
def get_balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sp = db.query(StudentPoints).filter(StudentPoints.student_id == user.id).first()
    return {"balance": sp.balance if sp else 0}


@router.get("/points/ledger")
def get_ledger(
    page: int = 1, page_size: int = 20,
    user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    q = db.query(PointsLedger).filter(PointsLedger.student_id == user.id)
    total = q.count()
    items = (
        q.order_by(PointsLedger.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": it.id, "delta": it.delta, "reason": it.reason,
                "ref_id": it.ref_id, "balance_after": it.balance_after,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            }
            for it in items
        ],
    }


@router.get("/wheel/prizes")
def get_wheel_prizes(mode: str = "wheel", db: Session = Depends(get_db)):
    prizes = (
        db.query(WheelPrize)
        .filter(WheelPrize.mode == mode, WheelPrize.is_active == True)  # noqa: E712
        .order_by(WheelPrize.sort_order)
        .all()
    )
    return [
        {"id": p.id, "name": p.name, "type": p.type, "weight": p.weight}
        for p in prizes
    ]


@router.post("/wheel/spin")
def spin(req: SpinRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mode = req.mode or "wheel"
    cost = _cfg_int(db, "wheel_cost", DEFAULT_WHEEL_COST)

    # 1) 锁定并扣减积分（事务原子，防超抽）
    sp = _ensure_student_points(db, user.id)
    if sp.balance < cost:
        raise HTTPException(status_code=400, detail=f"积分不足，需要 {cost} 积分")
    sp.balance -= cost

    # 2) 服务端加权随机出奖
    prizes = (
        db.query(WheelPrize)
        .filter(WheelPrize.mode == mode, WheelPrize.is_active == True)  # noqa: E712
        .order_by(WheelPrize.sort_order)
        .all()
    )
    if not prizes:
        raise HTTPException(status_code=500, detail="转盘奖品池未配置")
    chosen = _weighted_pick(prizes)

    # 3) 记账：本次抽奖扣费
    db.add(PointsLedger(
        student_id=user.id, delta=-cost,
        reason="wheel_spin", ref_id=None, balance_after=sp.balance,
    ))

    # 4) 写抽奖记录 + 处理虚拟奖品
    is_physical = chosen.type == "physical"
    if is_physical:
        status = "pending"
    else:
        status = "granted"
        _grant_virtual_payload(db, sp, chosen.virtual_payload)

    play = Play(
        student_id=user.id, mode=mode, prize_id=chosen.id,
        prize_name=chosen.name, is_physical=is_physical, status=status,
    )
    db.add(play)
    db.flush()

    db.commit()
    db.refresh(play)
    return {
        "play_id": play.id,
        "prize_name": chosen.name,
        "type": chosen.type,
        "is_physical": is_physical,
        "status": status,
        "balance": sp.balance,
        "granted_points": sp.balance,  # 冗余：便于前端展示最新余额
    }


@router.get("/redeem/items")
def get_redeem_items(db: Session = Depends(get_db)):
    items = (
        db.query(RedeemItem)
        .filter(RedeemItem.is_active == True)  # noqa: E712
        .order_by(RedeemItem.sort_order)
        .all()
    )
    return [
        {"id": it.id, "name": it.name, "type": it.type, "cost": it.cost}
        for it in items
    ]


@router.post("/redeem/direct")
def direct_redeem(req: DirectRedeemRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(RedeemItem).filter(RedeemItem.id == req.item_id, RedeemItem.is_active == True).first()  # noqa: E712
    if not item:
        raise HTTPException(status_code=404, detail="兑换项不存在或已下架")

    sp = _ensure_student_points(db, user.id)
    if sp.balance < item.cost:
        raise HTTPException(status_code=400, detail=f"积分不足，需要 {item.cost} 积分")

    sp.balance -= item.cost
    db.add(PointsLedger(
        student_id=user.id, delta=-item.cost,
        reason="direct_redeem", ref_id=None, balance_after=sp.balance,
    ))

    is_physical = item.type == "physical"
    status = "pending" if is_physical else "granted"
    if not is_physical:
        _grant_virtual_payload(db, sp, item.virtual_payload)

    rec = DirectRedemption(
        student_id=user.id, item_id=item.id, cost=item.cost, status=status,
    )
    db.add(rec)
    db.flush()

    db.commit()
    db.refresh(rec)
    return {
        "id": rec.id,
        "name": item.name,
        "is_physical": is_physical,
        "status": status,
        "balance": sp.balance,
    }


@router.get("/redeem/mine")
def my_rewards(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plays = (
        db.query(Play)
        .filter(Play.student_id == user.id)
        .order_by(Play.created_at.desc())
        .all()
    )
    directs = (
        db.query(DirectRedemption)
        .filter(DirectRedemption.student_id == user.id)
        .order_by(DirectRedemption.created_at.desc())
        .all()
    )
    result = []
    for p in plays:
        result.append({
            "source": "wheel", "id": p.id, "name": p.prize_name,
            "is_physical": p.is_physical, "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    for d in directs:
        item = db.query(RedeemItem).filter(RedeemItem.id == d.item_id).first()
        result.append({
            "source": "direct", "id": d.id,
            "name": item.name if item else f"兑换项#{d.item_id}",
            "is_physical": True, "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })
    # 合并后按时间倒序
    result.sort(key=lambda x: x["created_at"] or "", reverse=True)
    return {"items": result}
