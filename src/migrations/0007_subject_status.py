"""科目完成状态：subjects 表增加 status 字段。

背景：REQ-5，学生首页需区分「当前科目」和「历史科目」，
管理员可将科目标记为已完成（completed），已完成科目在首页置灰显示。

幂等：检测到 status 列已存在则跳过。
"""
from sqlalchemy import text


MIGRATION_ID = "0007_subject_status"


def up(engine):
    with engine.begin() as conn:
        # ---- 幂等检查 ----
        cols = [c[1] for c in conn.execute(text("PRAGMA table_info(subjects)")).fetchall()]
        if "status" in cols:
            return  # 已迁移，跳过

        # ---- 新增 status 列（默认 'active'，与 REQ-5 设计一致）----
        conn.execute(text("ALTER TABLE subjects ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'"))

        # ---- 旧数据（已完成年级）可手动在管理后台标记 ----
        # 不自动完成任何科目，避免误操作

        print(f"[{MIGRATION_ID}] 迁移完成：subjects.status 已添加，默认值 active")


def down(engine):
    """回滚：删除 status 列（SQLite 不支持 DROP COLUMN，跳过）"""
    with engine.begin() as conn:
        cols = [c[1] for c in conn.execute(text("PRAGMA table_info(subjects)")).fetchall()]
        if "status" not in cols:
            return  # 未迁移，跳过
        # SQLite 旧版本（< 3.35.0）不支持 DROP COLUMN，此处仅打印提示
        print(f"[{MIGRATION_ID}] 回滚：SQLite 不支持 DROP COLUMN，请手动处理")
