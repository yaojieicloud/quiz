"""REQ-7-1-3：topics 表加 tutorial_embed_html 字段。

支持管理员直接粘贴 <iframe> HTML，学员端 study.html 直接 innerHTML 渲染。
"""
from sqlalchemy import text
from database import engine

MIGRATION_ID = "0011_topic_embed_html"


def up(engine):
    with engine.begin() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(topics)")).fetchall()]
        if "tutorial_embed_html" in cols:
            print(f"[{MIGRATION_ID}] tutorial_embed_html 列已存在，跳过")
            return
        conn.execute(text("ALTER TABLE topics ADD COLUMN tutorial_embed_html TEXT"))
        print(f"[{MIGRATION_ID}] 完成：topics.tutorial_embed_html 已添加")


def down(engine):
    print(f"[{MIGRATION_ID}] 回滚：SQLite 不支持 DROP COLUMN，请手动重建表")


if __name__ == "__main__":
    up(engine)
