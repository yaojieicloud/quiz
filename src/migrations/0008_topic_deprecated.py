"""为 topics 表新增 deprecated 字段（软删除课程用）。

幂等：重复执行不报错。
MIGRATION_ID = "0008_topic_deprecated"
"""
from database import engine
from migrations import add_column

MIGRATION_ID = "0008_topic_deprecated"


def up(e):
    # 幂等：列已存在则跳过（add_column 内部已处理）
    add_column(e, "topics", "deprecated", "INTEGER", default=0)


def down(e):
    """不提供撤销（历史数据不可逆）"""
    pass
