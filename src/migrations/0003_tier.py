"""分阶档位（tier）迁移：建配置表 + 题目/记录加 tier 列。

tier: 1=初级 2=进阶 3=挑战。存量题目全部归入初级（TierConfig 决策 A）。
"""
from sqlalchemy import text

from migrations import add_column


MIGRATION_ID = "0003_tier"


def up(engine):
    # ---- tier_config：档位名称 + 积分倍率（权威来源，倍率走表而非硬编码）----
    # 注意：models.py 里的 TierConfig 模型会让 create_all 预建空表，
    # 因此这里用 CREATE TABLE IF NOT EXISTS + INSERT OR IGNORE 幂等播种，
    # 不依赖「表是否存在」来判断是否要写入种子数据。
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS tier_config ("
            "  tier INTEGER PRIMARY KEY,"
            "  name TEXT NOT NULL,"
            "  points_multiplier INTEGER NOT NULL DEFAULT 1"
            ")"
        ))
        conn.execute(text(
            "INSERT OR IGNORE INTO tier_config (tier, name, points_multiplier) VALUES "
            "(1, '初级', 1), (2, '进阶', 2), (3, '挑战', 3)"
        ))

    # ---- questions.tier：存量题 SQLite 自动填 default=1（全量初级）----
    add_column(engine, "questions", "tier", "INTEGER", default=1)

    # ---- exam_records.tier：历史记录无档位概念，默认 1，新提交会写入真实档位----
    add_column(engine, "exam_records", "tier", "INTEGER", default=1)
