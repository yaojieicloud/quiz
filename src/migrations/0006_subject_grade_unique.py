"""科目唯一约束改造：name 单列唯一 -> (name, grade) 复合唯一。

背景：设计约定「科目名不带年级，年级存 grade」（科目与知识点体系.md）。
但旧模型 name = unique=True，导致「数学(三年级)」与「数学(四年级)」无法共存，
新增 4 年级会触发 IntegrityError。本迁移把唯一约束改为 (name, grade) 复合，
允许同名校科目跨年级并存。

同时按业务约定，将无年级概念的编程类科目（Python基础理论 / Python基础实操）
的 grade 统一置为占位串「通用」，与小学科目的「三年级/四年级」区分。

实现：SQLite 由 unique=True 生成的隐式索引 sqlite_autoindex_subjects_1 无法 ALTER
删除，故重建表。利用 SQLite 外键按父表名解析的特性：RENAME 后新父表仍叫 subjects、
被引用列 id 不变，6 张子表（topics/questions/exam_records/student_mastery/
subject_points/mastery_rewards）的外键不受影响，无需重建子表。

幂等：检测到已存在 (name, grade) 复合唯一索引则直接跳过。
"""
from sqlalchemy import text


MIGRATION_ID = "0006_subject_grade_unique"


def up(engine):
    with engine.begin() as conn:
        # ---- 幂等检查：是否已含 (name, grade) 复合唯一 ----
        idxs = conn.execute(text("PRAGMA index_list(subjects)")).fetchall()
        for ix in idxs:
            if ix[2]:  # unique 标志位
                info = conn.execute(text(f"PRAGMA index_info({ix[1]})")).fetchall()
                cols = [c[2] for c in info]
                if cols == ["name", "grade"]:
                    return  # 已迁移，跳过

        # ---- SQLite FK 按父表名解析：新表仍叫 subjects，子表 FK 不受影响 ----
        conn.execute(text("PRAGMA legacy_alter_table=ON"))
        conn.execute(text("ALTER TABLE subjects RENAME TO subjects_old"))

        conn.execute(
            text(
                """
                CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    description VARCHAR(200),
                    icon VARCHAR(20),
                    grade VARCHAR(20),
                    sort_order INTEGER,
                    created_at DATETIME,
                    category VARCHAR(50),
                    allowed_types TEXT,
                    UNIQUE(name, grade)
                )
                """
            )
        )

        conn.execute(
            text(
                """
                INSERT INTO subjects
                    (id, name, description, icon, grade, sort_order, created_at,
                     category, allowed_types)
                SELECT
                    id, name, description, icon, grade, sort_order, created_at,
                    category, allowed_types
                FROM subjects_old
                """
            )
        )

        # ---- 编程类科目无年级，grade 置「通用」占位 ----
        conn.execute(
            text(
                "UPDATE subjects SET grade = '通用' "
                "WHERE name IN ('Python基础理论', 'Python基础实操')"
            )
        )

        conn.execute(text("DROP TABLE subjects_old"))
        conn.execute(text("PRAGMA legacy_alter_table=OFF"))
