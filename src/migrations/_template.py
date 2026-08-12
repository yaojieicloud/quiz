# 迁移模板：复制本文件并重命名为 00xx_xxx.py（不要带下划线前缀，否则不会被加载）。
# 然后在 MIGRATION_ID / up() 里写逻辑。up() 必须幂等（先查后改）。
#
# 可用辅助函数见 migrations/__init__.py：
#   add_column(engine, table, column, coltype, default=None) -> bool
#   create_index(engine, name, table, columns, unique=False) -> bool
#   table_exists / column_exists

MIGRATION_ID = "0000_template"


def up(engine):
    from migrations import add_column

    # 示例：给 questions 表幂等加一列（列已存在会自动跳过）
    add_column(engine, "questions", "example_col", "TEXT")
