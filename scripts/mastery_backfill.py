import sys
sys.path.insert(0, 'C:/Users/Yaojie/Documents/GitHub/quiz/src')
from database import SessionLocal, engine, Base
from models import User, Topic, Question, StudentMastery
from core.mastery import _topic_totals, compute_mastery_for_topics, upsert_student_mastery

db = SessionLocal()
# 建表（若不存在）
Base.metadata.create_all(bind=engine, tables=[StudentMastery.__table__])
print('table ensured: student_mastery')

# 清空旧数据（回填幂等）
db.query(StudentMastery).delete()
db.commit()

totals = _topic_totals(db)
pairs = list(totals.keys())  # 全部 (topic_id, tier)
students = db.query(User).filter(User.role == 'student').all()

for s in students:
    computed = compute_mastery_for_topics(db, s.id, pairs)
    upsert_student_mastery(db, s.id, computed)
    db.commit()
    mc = sum(1 for c in computed if c[3] == 'mastered')
    pc = sum(1 for c in computed if c[3] == 'passed')
    tc = sum(1 for c in computed if c[6] > 0)
    print('%s(id=%d): rows=%d tried=%d mastered=%d passed=%d' % (s.username, s.id, len(computed), tc, mc, pc))

# 验证表内总数
total_rows = db.query(StudentMastery).count()
print('total student_mastery rows=%d' % total_rows)
# 抽样诺诺精通课
for r in db.query(StudentMastery).filter(StudentMastery.status == 'mastered').all():
    t = db.query(Topic).filter(Topic.id == r.topic_id).first()
    print('  mastered: student=%d subject=%s topic=%s tier=%d rate=%s cov=%s' % (
        r.student_id, t.subject.name if t else '?', t.name if t else '?', r.tier, r.rate, r.coverage))
db.close()
