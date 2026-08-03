# -*- coding: utf-8 -*-
"""实跑 p1+p2 的参考代码，用 core.code_runner 沙箱算出 expected_output 写回，
合并输出 python_coding_new200.json。同时报告运行失败的题（必须为 0）。"""
import sys, json
sys.path.insert(0, r"C:\Users\Yaojie\Documents\GitHub\quiz\src")
from core.code_runner import run_python

p1 = json.load(open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\python_coding_new_p1.json", encoding="utf-8"))
p2 = json.load(open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\python_coding_new_p2.json", encoding="utf-8"))
all_q = p1 + p2
print(f"合并题数: {len(all_q)}")

fails = []
for i, q in enumerate(all_q):
    out, err, rc = run_python(q["answer"], q.get("sample_input", ""))
    if rc != 0:
        fails.append((i, q["topic_name"], q["content"][:40], rc, err.strip()[:120]))
        q["expected_output"] = ""
    else:
        q["expected_output"] = out

print(f"运行失败: {len(fails)} 题")
for f in fails:
    print("  ✗", f)

with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\python_coding_new200.json", "w", encoding="utf-8") as f:
    json.dump(all_q, f, ensure_ascii=False, indent=2)
print("已写出 python_coding_new200.json")

# 抽查几道
for q in all_q[:2] + all_q[100:102]:
    print(f"  [{q['topic_name']}] expected={q['expected_output']!r}")
