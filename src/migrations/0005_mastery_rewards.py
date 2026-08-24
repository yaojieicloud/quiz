"""精通奖励发放记录表：防重复派发 + 历史补发追溯。

背景：答题后达成精通 → 奖励一次「玩转大转盘」等额积分（动态读 config.wheel_cost）。
- (student_id, topic_id, tier) 联合唯一：同一课同一档位的精通奖励只发一次（防重复闸门）；
- points 为发放时的积分快照（发放当时的 wheel_cost）；
- mode：new=新达成 / retroactive=历史补发（功能上线前已精通、未发过奖的课）。
"""
from sqlalchemy import text

MIGRATION_ID = "0005_mastery_rewards"


def up(engine):
    # 注意：models.py 里的 MasteryReward 会让 create_all 预建空表，
    # 因此用 CREATE TABLE IF NOT EXISTS 幂等（与 0003_tier 同套路）。
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS mastery_rewards ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  student_id INTEGER NOT NULL,"
            "  topic_id INTEGER NOT NULL,"
            "  tier INTEGER NOT NULL DEFAULT 1,"
            "  subject_id INTEGER NOT NULL,"
            "  points INTEGER NOT NULL,"
            "  mode VARCHAR(20) NOT NULL DEFAULT 'new',"
            "  granted_at DATETIME NOT NULL DEFAULT (datetime('now')),"
            "  UNIQUE (student_id, topic_id, tier)"
            ")"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_mastery_rewards_student_id "
            "ON mastery_rewards (student_id)"
        ))
