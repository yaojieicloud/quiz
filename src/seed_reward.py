"""积分系统种子数据初始化（幂等，可重复执行）

填充初值：scoring_rules / wheel_prizes / redeem_items / config。
仅当对应表为空时写入，避免重复。用法：
    python src/seed_reward.py
"""
from database import SessionLocal, engine, Base
import models  # noqa: F401 确保全部表已注册到 metadata

Base.metadata.create_all(bind=engine)

# 积分矩阵：得分档位 → 积分（与题数无关，单题/多题统一适用）
# question_count 列保留为兼容占位（0 表示"任意题数"），发分仅按 score_band 命中
SCORING_MATRIX = [
    (0, 80, 3),   # 得分>=80 → 3 分
    (0, 90, 4),   # 得分>=90 → 4 分
    (0, 100, 5),  # 得分=100 → 5 分（低于80分不配置，默认0分）
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

# 科目积分覆盖（可选，按科目名片段匹配；无则走全局默认 5/4/3）
# python 实操积分：100->2 / 90->1 / <90->0（防刷分，用户 2026-08-21 确认）
SUBJECT_POINT_OVERRIDES = {
    "Python基础实操": (2, 1, 0),
}


def seed():
    db = SessionLocal()
    try:
        # scoring_rules：按最新积分矩阵覆盖（积分规则属配置，非用户数据；流水不受影响）
        db.query(models.ScoringRule).delete()
        for qc, band, pts in SCORING_MATRIX:
            db.add(models.ScoringRule(question_count=qc, score_band=band, points=pts, is_active=True))
        print(f"[seed] scoring_rules 覆盖写入 {len(SCORING_MATRIX)} 条")

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

        # subject_points：科目积分初始值（仅首次创建，已存在则不覆盖，保留管理员手动调整）
        for frag, (p100, p90, p80) in SUBJECT_POINT_OVERRIDES.items():
            sub = db.query(models.Subject).filter(models.Subject.name.contains(frag)).first()
            if not sub:
                print(f"[seed] 跳过科目积分(未找到匹配 '{frag}')")
                continue
            sp = db.query(models.SubjectPoints).filter(models.SubjectPoints.subject_id == sub.id).first()
            if sp:
                print(f"[seed] subject_points 已存在 科目={sub.name} -> {sp.p100}/{sp.p90}/{sp.p80}（不覆盖）")
                continue
            db.add(models.SubjectPoints(subject_id=sub.id, p100=p100, p90=p90, p80=p80))
            print(f"[seed] subject_points 初始化 科目={sub.name} -> {p100}/{p90}/{p80}")

        db.commit()
        print("[seed] 完成。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
