"""分析尧奕瑶「变量与标识符」课的掌握度显示问题"""
import sqlite3

conn = sqlite3.connect('quiz.db')
uid = 2  # 尧奕瑶

# 1. 找到 topic_id
tid = conn.execute("SELECT id FROM topics WHERE name LIKE '%变量%'").fetchone()
print(f'topic_id={tid[0] if tid else None}')

# 2. student_mastery 表记录
m = conn.execute("""
  SELECT sm.topic_id, t.name, sm.tier, sm.status, sm.rate, sm.coverage,
         sm.answered_count, sm.distinct_count, sm.correct_count, sm.topic_total
  FROM student_mastery sm
  JOIN topics t ON t.id = sm.topic_id
  WHERE sm.student_id = ? AND sm.topic_id = ?
""", (uid, tid[0])).fetchall()
print(f'\n=== student_mastery 表 ===')
for r in m:
  print(f'  topic_id={r[0]} "{r[1]}" tier={r[2]} | status={r[3]} | rate={r[4]} | coverage={r[5]} | N={r[6]} D={r[7]} C={r[8]} Q={r[9]}')

# 3. 用实际算法重新计算
N, D, C = conn.execute("""
  SELECT COUNT(*), COUNT(DISTINCT q.id), SUM(CASE WHEN ar.is_correct THEN 1 ELSE 0 END)
  FROM exam_records er
  JOIN answer_records ar ON ar.exam_record_id = er.id
  JOIN questions q ON q.id = ar.question_id
  WHERE er.user_id = ? AND q.topic_id = ?
""", (uid, tid[0])).fetchone()
Q = conn.execute("SELECT COUNT(*) FROM questions WHERE topic_id=?", (tid[0],)).fetchone()[0]
R = C / N * 100 if N else 0
Ccov = D / Q * 100 if Q else 0
thr = max(int(Q * 0.8), 10)
is_mastered = N >= thr and R >= 90 and Ccov >= 80
print(f'\n=== 实际算法重算 ===')
print(f'  N={N} (门槛>=max({Q}*0.8,10)={thr}) D={D}/{Q} C={C}')
print(f'  R={R:.2f}% (门槛>=90%) | Ccov={Ccov:.2f}% (门槛>=80%)')
print(f'  精通判定: {"✅精通" if is_mastered else "❌未精通"}')

# 4. 看前端展示的百分比是怎么算的
# 截图显示 101%，但正确率不可能 >100%。检查前端 mastery.html 的计算
print('\n=== 检查前端百分比计算 ===')
