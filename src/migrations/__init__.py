"""轻量数据库迁移器（零依赖，适配 SQLite）。

为什么需要它
------------
`main.py` 启动时只跑 `Base.metadata.create_all()`，它**只建不升级**：
表一旦存在，后续在 model 里新增的列、新建的索引都不会自动落到已存在的库上。
过去加字段靠「删库重建」或「手写 ALTER」（散落在 src/data/*_fix_*.py），
没有版本记录、本地与 ECS 各跑各的，库结构逐渐不可追溯、越来越脆。

本模块提供一个最小可用的迁移机制：
- 一张 `schema_migrations` 表记录已执行的迁移版本；
- `src/migrations/` 下每个文件是一个迁移，文件名以数字序号开头；
- 应用启动时自动执行「未执行过」的迁移，已执行的跳过。

迁移文件写法（参考 `_template.py`）
-----------------------------------
新建 `src/migrations/0003_xxx.py`：

    MIGRATION_ID = "0003_xxx"          # 唯一，建议与文件名一致

    def up(engine):
        from migrations import add_column
        add_column(engine, "questions", "hot", "INTEGER", default=0)

`up()` 必须幂等：先查后改，列/表/索引已存在就跳过，保证可重复执行、可跨环境重放。
"""
from __future__ import annotations

import glob
import importlib
import os

from sqlalchemy import text

from database import engine as _default_engine

MIGRATIONS_DIR = os.path.dirname(__file__)
_IGNORE = {"__init__"}


def _ensure_table(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                "  version TEXT PRIMARY KEY,"
                "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
                ")"
            )
        )


def _applied_versions(engine):
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {r[0] for r in rows}


# ---- 幂等辅助函数（迁移文件里直接调用）----


def table_exists(engine, table: str) -> bool:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
            {"t": table},
        ).fetchall()
    return bool(rows)


def column_exists(engine, table: str, column: str) -> bool:
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def add_column(engine, table: str, column: str, coltype: str, default=None) -> bool:
    """幂等加列。列已存在则跳过，返回是否真的加了。

    table / column / coltype 均为代码常量（非用户输入），用 f-string 拼接安全。
    """
    if not table_exists(engine, table):
        raise RuntimeError(f"add_column: 表不存在 {table}")
    if column_exists(engine, table, column):
        return False
    sql = f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"
    if default is not None:
        sql += f" DEFAULT {default}"
    with engine.begin() as conn:
        conn.execute(text(sql))
    return True


def create_index(engine, name: str, table: str, columns: str, unique: bool = False) -> bool:
    """幂等建索引。索引已存在则跳过。columns 形如 'col1, col2'。"""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='index' AND name=:n"),
            {"n": name},
        ).fetchall()
        if rows:
            return False
    with engine.begin() as conn:
        kw = "UNIQUE " if unique else ""
        conn.execute(text(f"CREATE {kw}INDEX {name} ON {table} ({columns})"))
    return True


# ---- 迁移执行器 ----


def run_migrations(engine=None):
    """扫描 src/migrations/ 下未执行过的迁移并依次执行。

    以 `_` 开头的文件（如 _template.py）和 __init__.py 会被跳过。
    """
    engine = engine or _default_engine
    _ensure_table(engine)
    applied = _applied_versions(engine)

    files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.py")))
    for path in files:
        name = os.path.basename(path)[:-3]
        if name in _IGNORE or name.startswith("_"):
            continue
        mod = importlib.import_module(f"migrations.{name}")
        mid = getattr(mod, "MIGRATION_ID", name)
        if mid in applied:
            continue
        print(f"[migrate] applying {mid}")
        mod.up(engine)
        with engine.begin() as conn:
            conn.execute(
                text("INSERT OR IGNORE INTO schema_migrations(version) VALUES (:v)"),
                {"v": mid},
            )
    print("[migrate] schema up to date")
