# -*- coding: utf-8 -*-
"""验证英语阅读理解题：格式、子题答案、与线上 content 比对去重"""
import json, urllib.request
from collections import Counter

files = [
    r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_upper.json",
    r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_lower.json",
]
all_q = []
for f in files:
    all_q.extend(json.load(open(f, encoding="utf-8")))
print(f"合计 {len(all_q)} 篇")

errors = []
for i, q in enumerate(all_q):
    if q.get("type") != "reading":
        errors.append(f"[{i}] type 不是 reading")
    for f in ["topic_name", "unit", "content", "answer"]:
        if not str(q.get(f, "")).strip():
            errors.append(f"[{i}] 缺字段 {f}")
    items = q.get("reading_items") or []
    if not items:
        errors.append(f"[{i}] reading_items 为空")
    ans_list = str(q.get("answer", "")).split(",")
    if len(ans_list) != len(items):
        errors.append(f"[{i}] answer 个数({len(ans_list)})与子题数({len(items)})不一致")
    for j, it in enumerate(items):
        if it.get("type") != "choice":
            errors.append(f"[{i}.{j}] 子题 type 不是 choice")
        opts = it.get("options") or []
        if len(opts) < 2:
            errors.append(f"[{i}.{j}] 子题选项不足")
        a = str(it.get("answer", ""))
        if not a.isdigit() or int(a) >= len(opts):
            errors.append(f"[{i}.{j}] 子题 answer 非法: {a!r} (选项{len(opts)}个)")
        elif j < len(ans_list) and ans_list[j] != a:
            errors.append(f"[{i}.{j}] 顶层 answer 与子题 answer 不一致")

if errors:
    print(f"✗ 发现 {len(errors)} 个问题:")
    for e in errors[:20]:
        print("  ", e)
else:
    print("✓ 格式校验全部通过")

# 内部重复检查
c = Counter(q["content"].strip() for q in all_q)
dup = {k: v for k, v in c.items() if v > 1}
print(f"批内重复 content: {len(dup)} 个" + ("" if not dup else f" -> {list(dup)[:3]}"))

# 与线上比对
B = "http://106.14.99.100:8000"
r = urllib.request.urlopen(urllib.request.Request(B + "/api/auth/login",
    data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
    headers={"Content-Type": "application/json"}), timeout=10)
tok = json.load(r)["access_token"]
qs = json.load(urllib.request.urlopen(urllib.request.Request(
    B + "/api/questions?subject_id=5", headers={"Authorization": "Bearer " + tok}), timeout=20))
items = qs if isinstance(qs, list) else qs.get("items", [])
online = {(x.get("content") or "").strip() for x in items}
clash = [q["content"][:30] for q in all_q if q["content"].strip() in online]
print(f"线上现有题: {len(items)}，本批与线上重复: {len(clash)} 个")
