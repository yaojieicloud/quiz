"""验证最近100题窗口机制改造效果"""
import sys
sys.path.insert(0, '/c/Users/Yaojie/Documents/GitHub/quiz/src')

from database import SessionLocal
from core.mastery import compute_mastery_for_topics, _topic_totals, _load_student_rows, _rows_to_stats, eval_topic_tier

db = SessionLocal()

# 覃禹诺 user_id=4，"注释与输出函数" topic_id=26
student_id = 4
topic_id = 26
tier = 1

print("=" * 70)
print("验证最近100题窗口机制改造效果")
print("=" * 70)
print(f"\n学员ID: {student_id}（覃禹诺）")
print(f"课程ID: {topic_id}（注释与输出函数）")
print(f"档位: tier={tier}")

# 计算题库总量
totals = _topic_totals(db)
Q = totals.get((topic_id, tier), 0)
print(f"\n题库总量 Q = {Q}")

# 加载答题明细
rows = _load_student_rows(db, student_id, question_ids=None)
print(f"\n加载答题明细：共 {len(rows)} 条记录")

# 过滤出该课程的答题记录
topic_rows = [r for r in rows if r[1] == topic_id and r[3] == tier]
print(f"该课程的答题记录：{len(topic_rows)} 条")

# 统计信息
stats = _rows_to_stats(rows)
key = (student_id, topic_id, tier)
st = stats.get(key, {"N": 0, "D": set(), "C": 0, "recent_N": 0, "recent_C": 0})

print(f"\n" + "-" * 70)
print("【改造前】全量统计")
print("-" * 70)
print(f"全量做题数 N = {st['N']}")
print(f"全量答对数 C = {st['C']}")
print(f"全量正确率 R = {st['C']/st['N']*100:.1f}% (如果 N>0)")

print(f"\n" + "-" * 70)
print("【改造后】窗口统计（最近100题）")
print("-" * 70)
print(f"窗口做题数 recent_N = {st['recent_N']}")
print(f"窗口答对数 recent_C = {st['recent_C']}")
print(f"窗口正确率 recent_R = {st['recent_C']/st['recent_N']*100:.1f}% (如果 recent_N>0)")

# 调用完整的评估函数
result = eval_topic_tier(stats, totals, student_id, topic_id, tier)

print(f"\n" + "=" * 70)
print("【最终掌握度评估结果】")
print("=" * 70)
print(f"状态: {result['status']}")
print(f"正确率: {result['rate']}%")
print(f"覆盖度: {result['coverage']}%")
print(f"总做题数: {result['total']}")
print(f"总答对数: {result['correct']}")

# 分析变化
print(f"\n" + "=" * 70)
print("【改造效果分析】")
print("=" * 70)

old_rate = st['C']/st['N']*100 if st['N'] > 0 else 0
new_rate = result['rate']

if new_rate > old_rate:
    print(f"✅ 正确率提升: {old_rate:.1f}% → {new_rate:.1f}% (+{new_rate - old_rate:.1f}%)")
elif new_rate < old_rate:
    print(f"❌ 正确率下降: {old_rate:.1f}% → {new_rate:.1f}% ({new_rate - old_rate:.1f}%)")
else:
    print(f"➖ 正确率不变: {new_rate:.1f}%")

if result['status'] == 'mastered':
    print(f"✅ 已达精通！")
elif result['status'] == 'passed':
    print(f"✓ 已通过")
elif result['status'] == 'practicing':
    print(f"○ 仍在练习中")
else:
    print(f"- 未开始")

# 如果还没精通，计算还差多少
if result['status'] != 'mastered':
    print(f"\n【距离精通还差多少？】")
    rate_gap = 90 - result['rate']
    cov_gap = 80 - result['coverage']
    
    if rate_gap > 0:
        print(f"  正确率还差: {rate_gap:.1f}%")
        # 计算需要再答对多少题（假设继续答100题）
        # 当前窗口正确率 = recent_C / recent_N
        # 目标：(recent_C + x) / (recent_N + x) >= 0.90
        # 解方程：recent_C + x >= 0.90 * (recent_N + x)
        # recent_C + x >= 0.90*recent_N + 0.90*x
        # x - 0.90*x >= 0.90*recent_N - recent_C
        # 0.10*x >= 0.90*recent_N - recent_C
        # x >= (0.90*recent_N - recent_C) / 0.10
        
        current_recent_C = st['recent_C']
        current_recent_N = st['recent_N']
        needed = (0.90 * current_recent_N - current_recent_C) / 0.10
        
        if needed > 0:
            print(f"  如果接下来全部答对，需要再答对约 {int(needed)} 题")
        else:
            print(f"  窗口内答对数已经足够，继续刷即可")
    
    if cov_gap > 0:
        print(f"  覆盖度还差: {cov_gap:.1f}%")
        # 覆盖度 = D / Q * 100
        # 需要 D >= 0.80 * Q
        needed_distinct = int(0.80 * Q) - len(st['D'])
        if needed_distinct > 0:
            print(f"  还需要答对约 {needed_distinct} 道不同的题")

db.close()
print("\n" + "=" * 70)
