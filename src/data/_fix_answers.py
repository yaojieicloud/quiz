# -*- coding: utf-8 -*-
"""修复所有 reading 文件：顶层 answer 从 reading_items 子题答案重新生成"""
import json
import io
import os

D = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese"
fixed_total = 0
for f in sorted(os.listdir(D)):
    if not f.endswith(".json"):
        continue
    p = os.path.join(D, f)
    data = json.loads(io.open(p, encoding="utf-8").read())
    changed = 0
    for q in data:
        correct = ",".join(str(it["answer"]) for it in q["reading_items"])
        if q.get("answer") != correct:
            q["answer"] = correct
            changed += 1
    if changed:
        io.open(p, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
    print(f, "修正", changed, "条 / 共", len(data))
    fixed_total += changed
print("合计修正:", fixed_total)
