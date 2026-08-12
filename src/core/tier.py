"""分阶档位（tier）常量层与倍率读取。

tier 是比题内微难度(difficulty)更高一层的维度：初级/进阶/挑战。
参与：组卷抽题、错题重做、积分倍率、掌握度、学情分析。
倍率以 tier_config 表为权威来源（seed 见迁移 0003_tier），读取失败回退本文件常量。
"""
from sqlalchemy.orm import Session

from models import TierConfig

TIER_PRIMARY = 1
TIER_ADVANCED = 2
TIER_CHALLENGE = 3

TIER_NAMES = {
    TIER_PRIMARY: "初级",
    TIER_ADVANCED: "进阶",
    TIER_CHALLENGE: "挑战",
}

# 默认倍率（tier_config 表缺失时的回退；表优先级更高）
DEFAULT_MULTIPLIERS = {
    TIER_PRIMARY: 1,
    TIER_ADVANCED: 2,
    TIER_CHALLENGE: 3,
}

ACTIVE_TIERS = [TIER_PRIMARY, TIER_ADVANCED, TIER_CHALLENGE]
DEFAULT_TIER = TIER_PRIMARY


def tier_label(tier) -> str:
    """档位数字 → 中文名；未知值原样返回。"""
    try:
        return TIER_NAMES.get(int(tier), str(tier))
    except (TypeError, ValueError):
        return str(tier)


def get_tier_multiplier(db: Session, tier) -> int:
    """读取某档位的积分倍率：优先 tier_config 表，回退 DEFAULT_MULTIPLIERS。"""
    try:
        t = int(tier)
    except (TypeError, ValueError):
        return 1
    row = db.query(TierConfig).filter(TierConfig.tier == t).first()
    if row is not None:
        return row.points_multiplier
    return DEFAULT_MULTIPLIERS.get(t, 1)
