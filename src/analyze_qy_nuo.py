"""分析覃禹诺今天是否有课程达到精通"""
import sqlite3

conn = sqlite3.connect('quiz.db')

# 覃禹诺 user_id=4, 今天 = 2026-08-24 北京时间
today_exams = conn.execute("""
  SELECT id, subject_id, tier, started_at, finished_at, total, correct, score, mode
  FROM exam_records
  WHERE user_id = 4
    AND date(started_at, '+8 hours') = '2026-08-24'
  ORDER BY started_at
""").fetchall()

print(f'=== 覃禹诺今天 {len(today_exams)} 场考试 ===')
for e in today_exams:
    print(f'  考试#{e[0]} | subject={e[1]} tier={e[2]} | {e[5]}题对{e[6]}题 ({e[7]}分) | {e[3][:16]} | mode={e[8]}')

# 按每场考试反推涉及的 topic_id
print(f'\n=== 各场考试涉及的课程 ===')
for e in today_exams:
    topics = conn.execute("""
      SELECT DISTINCT q.topic_id, t.name, t.subject_id
      FROM answer_records ar
      JOIN questions q ON q.id = ar.question_id
      JOIN topics t ON t.id = q.topic_id
      WHERE ar.exam_record_id = ?
    """, (e[0],)).fetchall()
    topic_names = ', '.join([f'{t[1]}(id={t[0]})' for t in topics])
    print(f'  考试#{e[0]}: {topic_names}')

# 计算覃禹诺所有 (topic_id, tier) 的完整掌握度
topic_totals = {r[0]: r[1] for r in conn.execute('SELECT topic_id, COUNT(*) FROM questions GROUP BY topic_id')}

mastery_check = conn.execute("""
  SELECT q.topic_id, er.tier,
         COUNT(*) as N,
         COUNT(DISTINCT q.id) as D,
         SUM(CASE WHEN ar.is_correct THEN 1 ELSE 0 END) as C
  FROM exam_records er
  JOIN answer_records ar ON ar.exam_record_id = er.id
  JOIN questions q ON q.id = ar.question_id
  WHERE er.user_id = 4
  GROUP BY q.topic_id, er.tier
  HAVING N > 0
""").fetchall()

print(f'\n=== 完整掌握度计算 ===')
mastered = []
for topic_id, tier, N, D, C in mastery_check:
    Q = topic_totals.get(topic_id, 0)
    R = C / N if N else 0
    Ccov = D / Q if Q else 0
    thr = max(int(Q * 0.8), 10)
    is_mastered = N >= thr and R >= 0.90 and Ccov >= 0.80

    topic_name = conn.execute('SELECT name FROM topics WHERE id=?', (topic_id,)).fetchone()[0]

    status = '✅精通' if is_mastered else ('⏳练习中' if (R >= 0.80 and Ccov >= 0.50) else '—')
    if is_mastered:
        mastered.append((topic_id, tier, topic_name))
    # 只打印接近精通或已达精通的
    if is_mastered or (R >= 0.75 and Ccov >= 0.40):
        print(f'  {status} topic_id={topic_id} "{topic_name}" tier={tier} | N={N}/{thr} D={D}/{Q} C={C} | R={R:.1%} Ccov={Ccov:.1%}')

print(f'\n=== 覃禹诺已达精通的课: {len(mastered)} 门 ===')
for t, tier, name in mastered:
    print(f'  ✅ "{name}" (topic_id={t}, tier={tier})')
