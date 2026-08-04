# -*- coding: utf-8 -*-
"""抽查 c3b_u5u6.json 子题答案与文章/讲解是否一致"""
import json
import io

P = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3b_u5u6.json"
data = json.loads(io.open(P, encoding="utf-8").read())

for qi in [0, 1, 15]:
    q = data[qi]
    print("=" * 60)
    print(q["unit"], "/", q["topic_name"], "| 顶层answer:", q["answer"])
    print("文章:", q["content"][:120].replace("\n", " "), "...")
    for i, it in enumerate(q["reading_items"]):
        a = int(it["answer"])
        print(f"  子题{i+1}: {it['q']}")
        print(f"    选项: {it['options']}")
        print(f"    answer={a} -> {it['options'][a]}")
        print(f"    讲解: {it['explanation']}")
