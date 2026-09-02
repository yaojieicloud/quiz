"""REQ-7-1-1：topics 表加两列教程 URL 字段。

- tutorial_video_url: B站视频嵌入 URL（player.bilibili.com/...）
- tutorial_book_url:  在线课本 URL（人教版 book.pep.com.cn/...）
两列均 TEXT 可空，默认 NULL。
"""

MIGRATION_ID = "0010_topic_tutorial_urls"


def up(engine):
    from migrations import add_column
    add_column(engine, "topics", "tutorial_video_url", "TEXT", default=None)
    add_column(engine, "topics", "tutorial_book_url", "TEXT", default=None)
