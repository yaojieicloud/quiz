"""导入 Python 500 题到数据库
读取 data/py500/batch1-4.json，合并后导入 Python入门 科目
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database import Base, engine, SessionLocal  # noqa: E402
from models import Subject, Topic, Question  # noqa: E402

PY500_DIR = Path(__file__).resolve().parent / "py500"
SUBJECT_NAME = "Python入门"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 找/建科目
        subject = db.query(Subject).filter(Subject.name == SUBJECT_NAME).first()
        if not subject:
            subject = Subject(name=SUBJECT_NAME, icon="🐍", grade="入门",
                              category="programming", sort_order=0)
            db.add(subject)
            db.flush()
            print(f"[新建科目] {SUBJECT_NAME} id={subject.id}")
        else:
            # 确保category正确
            if not subject.category:
                subject.category = "programming"
            print(f"[复用科目] {SUBJECT_NAME} id={subject.id} category={subject.category}")

        # 合并所有batch（含补充）
        all_questions = []
        import glob
        for f in sorted(glob.glob(str(PY500_DIR / "batch*.json"))):
            fname = Path(f).name
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            all_questions.extend(data)
            print(f"  读取 {fname}: {len(data)} 题")
        print(f"  合计 {len(all_questions)} 题")

        # topic_name -> Topic
        topic_map = {}
        created = 0
        skipped = 0
        for q in all_questions:
            tname = q["topic_name"]
            if tname not in topic_map:
                topic = db.query(Topic).filter(
                    Topic.subject_id == subject.id, Topic.name == tname
                ).first()
                if not topic:
                    topic = Topic(subject_id=subject.id, name=tname,
                                  unit=None, sort_order=len(topic_map))
                    db.add(topic)
                    db.flush()
                topic_map[tname] = topic

            topic = topic_map[tname]
            # 去重：同科目同题干
            exists = db.query(Question).filter(
                Question.subject_id == subject.id, Question.content == q["content"]
            ).first()
            if exists:
                skipped += 1
                continue

            question = Question(
                subject_id=subject.id,
                topic_id=topic.id,
                type=q["type"],
                content=q["content"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", 1),
            )
            db.add(question)
            created += 1

        db.commit()

        # 汇总
        print(f"\n=== 导入结果 ===")
        print(f"科目: {subject.name} (id={subject.id})")
        print(f"章节: {len(topic_map)} 个")
        for tname, t in topic_map.items():
            cnt = db.query(Question).filter(Question.topic_id == t.id).count()
            print(f"  {tname}: {cnt} 题")
        print(f"新增题目: {created} 题")
        print(f"跳过重复: {skipped} 题")

        # 总题数校验
        total = db.query(Question).filter(Question.subject_id == subject.id).count()
        print(f"\nPython 科目总题数: {total}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
