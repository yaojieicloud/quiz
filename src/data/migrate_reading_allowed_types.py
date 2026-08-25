"""数据库迁移：为 reading 题型与科目题型配置加字段（幂等，可重复执行）。

变更：
  - subjects 表新增 allowed_types（JSON/TEXT，NULL=不限制）
  - questions 表新增 reading_items（JSON/TEXT，仅 reading 题型用）

用法:
    python data/migrate_reading_allowed_types.py            # 默认迁移 quiz-data/quiz.db（唯一合法路径）
    python data/migrate_reading_allowed_types.py --db /path/to/quiz.db
"""
import argparse
import sqlite3
import sys
from pathlib import Path

MIGRATIONS = [
    ("subjects", "allowed_types", "TEXT"),
    ("questions", "reading_items", "TEXT"),
]


def migrate(db_path: str) -> bool:
    path = Path(db_path)
    if not path.exists():
        print(f"[错误] 数据库不存在: {path}")
        return False
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.cursor()
        for table, column, coltype in MIGRATIONS:
            existing = {row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()}
            if column in existing:
                print(f"[跳过] {table}.{column} 已存在")
                continue
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
            print(f"[完成] {table}.{column} 已添加")
        conn.commit()
        print("[迁移完成]")
        return True
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    # 数据库唯一合法路径 = <项目根>/quiz-data/quiz.db（旧版误用 src/data/../quiz.db=src/quiz.db，已修正）
    default_db = Path(__file__).resolve().parent.parent.parent / "quiz-data" / "quiz.db"
    ap.add_argument("--db", default=str(default_db), help="数据库文件路径")
    args = ap.parse_args()
    ok = migrate(args.db)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
