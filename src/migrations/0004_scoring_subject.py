"""积分档位化改造：scoring_rules 加 subject_id 列 + 清理旧种子。

背景：积分由「仅看得分率」改为「题数档位 × 分数段 × 科目」一套机制。
- subject_id：NULL=全局默认规则，非空=科目专属规则（如 Python基础实操）。
- 清理旧版 3 条 question_count=0 的种子（80→3 / 90→4 / 100→5）：
  新机制下 question_count=0 是「兜底」含义，旧种子残留会让非标题数拿到旧积分，
  重新引入档位漏洞，故移除。
"""
from sqlalchemy import text

from migrations import add_column, create_index


MIGRATION_ID = "0004_scoring_subject"


def up(engine):
    # ---- scoring_rules.subject_id：NULL=全局，非空=科目专属 ----
    add_column(engine, "scoring_rules", "subject_id", "INTEGER")

    # ---- 索引：按科目查专属规则是发分热路径 ----
    create_index(engine, "ix_scoring_rules_subject_id", "scoring_rules", "subject_id")

    # ---- 清理旧版种子：question_count=0 且分数段为 80/90/100 的三条默认规则 ----
    # 注意：只删「旧种子签名」，不误删管理员后续手工新增的 question_count=0 兜底规则。
    with engine.begin() as conn:
        conn.execute(text(
            "DELETE FROM scoring_rules "
            "WHERE question_count = 0 AND score_band IN (80, 90, 100)"
        ))
