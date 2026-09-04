"""BUG-8：错误日志表 error_logs（前端 JS 报错 + 后端 API 错误统一记录）。

- 普通表 create_all 不会在已有库执行（sqlite_master 已存在则跳过 CREATE TABLE），
  但 SQLAlchemy 的 create_all 是条件性的；为幂等，这里手动建表（已存在则跳过）。
- 同时建 user_id 索引便于按学员排查。
"""
from sqlalchemy import text
from database import engine

MIGRATION_ID = "0012_error_logs"


def up(engine):
    with engine.begin() as conn:
        # 检查表是否已存在
        existing = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='error_logs'"
        )).fetchone()
        if existing:
            print(f"[{MIGRATION_ID}] error_logs 表已存在，跳过")
            return

        conn.execute(text("""
            CREATE TABLE error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind VARCHAR(30) NOT NULL,
                status_code INTEGER,
                http_method VARCHAR(10),
                request_url VARCHAR(500),
                message TEXT NOT NULL,
                stack TEXT,
                content_json TEXT,
                source VARCHAR(200),
                page_url VARCHAR(500),
                user_id INTEGER,
                username VARCHAR(50),
                role VARCHAR(20),
                created_at DATETIME
            )
        """))
        # 索引：按 kind / user_id / 时间 三类高频查询
        conn.execute(text("CREATE INDEX ix_error_logs_kind ON error_logs (kind)"))
        conn.execute(text("CREATE INDEX ix_error_logs_user_id ON error_logs (user_id)"))
        conn.execute(text("CREATE INDEX ix_error_logs_created_at ON error_logs (created_at)"))
        print(f"[{MIGRATION_ID}] 完成：error_logs 表 + 3 索引已创建")


def down(engine):
    print(f"[{MIGRATION_ID}] 回滚：SQLite 不支持 DROP TABLE 强回滚，请手动 DROP TABLE error_logs")


if __name__ == "__main__":
    up(engine)
