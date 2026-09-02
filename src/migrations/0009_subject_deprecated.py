"""为 subjects 表新增 deprecated 字段（软删除科目用）。

与 Topic/Question 的 deprecated 机制一致：
- deprecated=0 → 正常可见
- deprecated=1 → 软删，学员端完全不可见（但 answer_records 做题记录保留）
"""
from sqlalchemy import text
from database import engine

MIGRATION_ID = "0009_subject_deprecated"

def up(engine):
    with engine.begin() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(subjects)")).fetchall()]
        if "deprecated" in cols:
            print(f"[{MIGRATION_ID}] deprecated 列已存在，跳过")
            return
        conn.execute(text("ALTER TABLE subjects ADD COLUMN deprecated INTEGER NOT NULL DEFAULT 0"))
        print(f"[{MIGRATION_ID}] 完成：subjects.deprecated 已添加，默认 0")

def down(engine):
    # SQLite 不支持 DROP COLUMN，记录即可
    print(f"[{MIGRATION_ID}] 回滚：SQLite 不支持 DROP COLUMN，请手动重建表")

if __name__ == "__main__":
    up(engine)
