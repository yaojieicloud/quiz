# -*- coding: utf-8 -*-
"""校验并修复 reading_chinese 目录下所有 JSON：
1. JSON 合法性
2. 每课篇数
3. 顶层 answer 与子题索引一致性（不一致则用子题重建）
4. 抽查子题 answer 与 explanation 的语义一致性无法自动做，仅报告
"""
import json
import io
import os
import sys

D = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese"

fixed_total = 0
for f in sorted(os.listdir(D)):
    if not f.endswith(".json"):
        continue
    p = os.path.join(D, f)
    try:
        data = json.loads(io.open(p, encoding="utf-8").read())
    except Exception as e:
        print(f"{f}: 非法JSON，跳过 -> {str(e)[:80]}")
        continue
    fixed = 0
    for q in data:
        items = q.get("reading_items") or []
        expect = ",".join(str(it.get("answer")) for it in items)
        if expect != q.get("answer"):
            q["answer"] = expect
            fixed += 1
    if fixed:
        io.open(p, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
        fixed_total += fixed
    from collections import Counter
    c = Counter(x["topic_name"] for x in data)
    ok5 = sorted(set(c.values())) == [5]
    print(f"{f}: {len(data)}条 | 每课5篇={ok5} | 修复answer {fixed} 处")
    if not ok5:
        print("   明细:", dict(c))
print(f"\n共修复 {fixed_total} 处")
