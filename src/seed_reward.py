"""积分系统种子数据初始化（幂等，可重复执行）

填充初值：scoring_rules / wheel_prizes / redeem_items / config。
仅当对应记录不存在时写入，避免覆盖管理员手工配置。用法：
    python src/seed_reward.py

2026-08-24 积分档位化改造：
- 积分矩阵改为「题数档位 × 分数段」，全部走 scoring_rules 单表；
- subject_id：NULL=全局默认，非空=科目专属（替代废弃的 subject_points 表）；
- 旧 subject_points 存量数据迁入 scoring_rules 后清空；
- scoring_rules 由「每次 delete 覆盖」改为「已存在则跳过」（幂等，
  修复容器重启会重置管理员后台配置的问题）。
"""
from database import SessionLocal, engine, Base
import models  # noqa: F401 确保全部表已注册到 metadata

Base.metadata.create_all(bind=engine)

# 全局默认积分矩阵：(题数档位, 分数段, 积分)
# 发分规则：先按科目专属，再全局；各自内部先精确匹配题数，缺则回落题数=0；
# 分数段取 <= 实际得分的最大者。无命中=0（不再有 <80 硬编码）。
SCORING_MATRIX = [
    # 10题档：100→1，90~99→1（<90 无规则=0）
    (10, 100, 1), (10, 90, 1),
    # 20题档：100→2，90~99→1（<90=0）
    (20, 100, 2), (20, 90, 1),
    # 30题档：100→3，90~99→2，80~89→1（<80=0）
    (30, 100, 3), (30, 90, 2), (30, 80, 1),
    # 40题档：100→4，90~99→3，80~89→2，70~79→1（<70=0）
    (40, 100, 4), (40, 90, 3), (40, 80, 2), (40, 70, 1),
    # 50题档：100→5，90~99→4，80~89→3，70~79→2，60~69→1（<60=0）
    (50, 100, 5), (50, 90, 4), (50, 80, 3), (50, 70, 2), (50, 60, 1),
]

# 科目专属积分：科目名片段 → [(题数档位, 分数段, 积分), ...]
# Python基础实操：单题模式，100→2 / 90~99→1 / <90→0（防刷分，积分规则保持不变）
SUBJECT_SCORING = {
    "Python基础实操": [(1, 100, 2), (1, 90, 1)],
}

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


def _rule_exists(db, question_count, score_band, subject_id):
    q = db.query(models.ScoringRule).filter(
        models.ScoringRule.question_count == question_count,
        models.ScoringRule.score_band == score_band,
    )
    if subject_id is None:
        q = q.filter(models.ScoringRule.subject_id.is_(None))
    else:
        q = q.filter(models.ScoringRule.subject_id == subject_id)
    return q.count() > 0


def seed():
    db = SessionLocal()
    try:
        # ---- scoring_rules：仅缺失时写入（幂等，不覆盖管理员配置）----
        added = 0
        for qc, band, pts in SCORING_MATRIX:
            if not _rule_exists(db, qc, band, None):
                db.add(models.ScoringRule(question_count=qc, score_band=band,
                                          points=pts, subject_id=None, is_active=True))
                added += 1
        print(f"[seed] scoring_rules 全局规则补写 {added} 条（已存在不覆盖）")

        # 科目专属规则
        for frag, rules in SUBJECT_SCORING.items():
            sub = db.query(models.Subject).filter(models.Subject.name.contains(frag)).first()
            if not sub:
                print(f"[seed] 跳过科目专属积分(未找到匹配 '{frag}')")
                continue
            for qc, band, pts in rules:
                if not _rule_exists(db, qc, band, sub.id):
                    db.add(models.ScoringRule(question_count=qc, score_band=band,
                                              points=pts, subject_id=sub.id, is_active=True))
                    print(f"[seed] 科目专属积分 科目={sub.name} {qc}题 {band}分→{pts}分")
        db.flush()

        # ---- subject_points 存量迁移：迁入 scoring_rules 后清空（一次性）----
        # 原 subject_points 语义是「该科目任意题数都覆盖」，故迁移为
        # question_count=0（兜底）+ subject_id，严格保留旧行为；
        # 0 积分档不迁移（新机制无命中即 0）。
        legacy = db.query(models.SubjectPoints).all()
        for sp in legacy:
            bands = [(100, sp.p100), (90, sp.p90), (80, sp.p80)]
            for band, pts in bands:
                if pts and pts > 0 and not _rule_exists(db, 0, band, sp.subject_id):
                    db.add(models.ScoringRule(question_count=0, score_band=band,
                                              points=pts, subject_id=sp.subject_id, is_active=True))
                    print(f"[seed] 迁移 subject_points 科目id={sp.subject_id} {band}分→{pts}分")
            db.delete(sp)
        if legacy:
            print(f"[seed] subject_points 存量迁移完成，共 {len(legacy)} 条（表已废弃清空）")

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
