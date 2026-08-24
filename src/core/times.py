"""时间工具：统一对外序列化口径。

数据库统一存储 UTC（naive datetime，由 datetime.utcnow() 写入）。
对外序列化时统一补 +00:00 时区标识，前端 new Date() 才能正确
换算为本地（北京）时间显示——否则无时区字符串会被当作本地时间，
导致显示时间比北京时间早 8 小时。
"""
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))  # UTC+8


def to_iso_utc(v):
    """把库里的时间值转成带 +00:00 的 ISO 字符串。

    支持：
    - None → None
    - naive datetime（视为 UTC）→ 补 +00:00
    - aware datetime → 转 UTC
    - str（SQLite 原始 text，如 "2026-08-22 14:45:25.654347"）→ 解析为 UTC 后输出
    """
    if v is None:
        return None
    if isinstance(v, str):
        raw = v.strip()
        if not raw:
            return None
        try:
            v = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return raw  # 无法解析则原样返回，不阻塞
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    else:
        v = v.astimezone(timezone.utc)
    return v.isoformat()


def to_beijing_date(v):
    """把库中时间值转成北京时间（UTC+8）的 'YYYY-MM-DD' 字符串。

    用于按"北京日历日"聚合的场景（今日答题量、周报日期分组）：
    库里是 UTC，直接取 UTC 日期会让北京凌晨 0-8 点的答题算到前一天。
    """
    if v is None:
        return None
    if isinstance(v, str):
        raw = v.strip()
        if not raw:
            return None
        try:
            v = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return raw[:10]
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(BEIJING_TZ).strftime("%Y-%m-%d")


def beijing_today_str():
    """当前北京日期 'YYYY-MM-DD'（与库里 UTC 时间的北京日历日对齐）。"""
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
