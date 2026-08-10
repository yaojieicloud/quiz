"""积分系统种子数据初始化（幂等，可重复执行）

填充初值：scoring_rules / wheel_prizes / redeem_items / config。
仅当对应表为空时写入，避免重复。用法：
    python src/seed_reward.py
"""
from database import SessionLocal, engine, Base
import models  # noqa: F401 确保全部表已注册到 metadata

Base.metadata.create_all(bind=engine)

# 初值矩阵：题数 × 得分段 → 积分
SCORING_MATRIX = [
    (10, 80, 1), (10, 90, 2), (10, 100, 3),
    (20, 80, 2), (20, 90, 3), (20, 100, 4),
    (50, 80, 8), (50, 90, 9), (50, 100, 10),
]

# 转盘奖品（mode=wheel）：name, type, virtual_payload, weight, sort_order
WHEEL_PRIZES = [
    ("谢谢参与", "virtual", None, 30, 1),
    ("小心愿券", "physical", None, 18, 2),
    ("小礼物券", "physical", None, 17, 3),
    ("零花钱券 1元", "physical", None, 15, 4),
    ("零花钱券 2元", "physical", None, 12, 5),
    ("零花钱券 5元", "physical", None, 8, 6),
]

# 直兑商城：name, type, cost, sort_order
REDEEM_ITEMS = [
    ("小心愿", "physical", 100, 1),
    ("小礼物", "physical", 200, 2),
    ("零花钱 1元", "physical", 100, 3),
    ("零花钱 2元", "physical", 200, 4),
    ("零花钱 5元", "physical", 500, 5),
]

# 全局配置
CONFIGS = {
    "wheel_cost": "20",
    "launch_popup_version": "v1",
}


def seed():
    db = SessionLocal()
    try:
        # scoring_rules
        if db.query(models.ScoringRule).count() == 0:
            for qc, band, pts in SCORING_MATRIX:
                db.add(models.ScoringRule(question_count=qc, score_band=band, points=pts, is_active=True))
            print(f"[seed] scoring_rules 写入 {len(SCORING_MATRIX)} 条")

        # wheel_prizes
        if db.query(models.WheelPrize).filter(models.WheelPrize.mode == "wheel").count() == 0:
            for name, typ, payload, w, order in WHEEL_PRIZES:
                db.add(models.WheelPrize(
                    mode="wheel", name=name, type=typ,
                    virtual_payload=payload, weight=w, is_active=True, sort_order=order,
                ))
            print(f"[seed] wheel_prizes 写入 {len(WHEEL_PRIZES)} 条")

        # redeem_items
        if db.query(models.RedeemItem).count() == 0:
            for name, typ, cost, order in REDEEM_ITEMS:
                db.add(models.RedeemItem(
                    name=name, type=typ, cost=cost, virtual_payload=None,
                    is_active=True, sort_order=order,
                ))
            print(f"[seed] redeem_items 写入 {len(REDEEM_ITEMS)} 条")

        # config
        for k, v in CONFIGS.items():
            if db.query(models.Config).filter(models.Config.key == k).count() == 0:
                db.add(models.Config(key=k, value=v))
                print(f"[seed] config 写入 {k}={v}")

        db.commit()
        print("[seed] 完成。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
