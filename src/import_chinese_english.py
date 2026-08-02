"""导入语文和英语题目到本地数据库"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "quiz.db"
CHINESE_JSON = Path(__file__).parent / "data" / "chinese_grade3_questions.json"
ENGLISH_JSON = Path(__file__).parent / "data" / "english_grade3_questions.json"


def import_subject(json_file, subject_id, subject_name):
    """导入一个科目的题目"""
    print(f"\n{'='*50}")
    print(f"导入 {subject_name} (ID={subject_id})")
    print(f"{'='*50}")
    
    # 读取题目
    questions = json.loads(json_file.read_text(encoding="utf-8"))
    print(f"题目数量: {len(questions)}")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取已有章节
    cursor.execute("SELECT id, name FROM topics WHERE subject_id = ?", (subject_id,))
    topic_map = {name: tid for tid, name in cursor.fetchall()}
    print(f"已有章节: {len(topic_map)} 个")
    
    # 按题型统计
    type_count = {}
    topic_count = {}
    imported = 0
    skipped = 0
    
    for q in questions:
        qtype = q["type"]
        type_count[qtype] = type_count.get(qtype, 0) + 1
        
        topic_name = q["topic_name"]
        topic_count[topic_name] = topic_count.get(topic_name, 0) + 1
        
        # 检查是否已存在（按content去重）
        cursor.execute(
            "SELECT id FROM questions WHERE subject_id = ? AND content = ?",
            (subject_id, q["content"])
        )
        if cursor.fetchone():
            skipped += 1
            continue
        
        # 创建章节（如果不存在）
        if topic_name not in topic_map:
            cursor.execute(
                "INSERT INTO topics (subject_id, name, unit) VALUES (?, ?, ?)",
                (subject_id, topic_name, q.get("unit"))
            )
            topic_map[topic_name] = cursor.lastrowid
            print(f"  新建章节: {topic_name}")
        
        # 插入题目
        cursor.execute("""
            INSERT INTO questions (
                subject_id, topic_id, type, content, options, match_options,
                answer, explanation, difficulty, blank_count, blank_answers, tolerance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subject_id,
            topic_map[topic_name],
            q["type"],
            q["content"],
            q.get("options"),
            q.get("match_options"),
            str(q["answer"]),
            q.get("explanation", ""),
            q.get("difficulty", 1),
            q.get("blank_count", 1),
            q.get("blank_answers"),
            q.get("tolerance", 0.01)
        ))
        imported += 1
    
    conn.commit()
    conn.close()
    
    # 打印统计
    print(f"\n导入完成:")
    print(f"  新增: {imported} 题")
    print(f"  跳过: {skipped} 题（重复）")
    print(f"\n题型分布:")
    for t, c in sorted(type_count.items()):
        print(f"  {t}: {c} 题")
    print(f"\n章节分布:")
    for t, c in sorted(topic_count.items()):
        print(f"  {t}: {c} 题")


def main():
    print(f"数据库: {DB_PATH}")
    
    # 导入语文（ID=4）
    import_subject(CHINESE_JSON, 4, "语文")
    
    # 导入英语（ID=5）
    import_subject(ENGLISH_JSON, 5, "英语")
    
    print(f"\n{'='*50}")
    print("全部导入完成！")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
