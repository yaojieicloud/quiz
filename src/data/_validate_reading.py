# -*- coding: utf-8 -*-
"""全量深度校验所有 reading 题文件"""
import json
import io
import os
from collections import Counter

D = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese"
grand = 0
allitems = []
problems = []

for f in sorted(os.listdir(D)):
    if not f.endswith(".json"):
        continue
    p = os.path.join(D, f)
    data = json.loads(io.open(p, encoding="utf-8").read())
    c = Counter(x["topic_name"] for x in data)
    grand += len(data)
    allitems.extend(data)
    bad = {k: v for k, v in c.items() if v != 5}
    if bad:
        problems.append(f"{f}: 篇数异常 {bad}")
    print(f, len(data), "条", "OK" if not bad else bad)

for q in allitems:
    err = None
    if q.get("type") != "reading":
        err = "type错误"
    elif q.get("options") is not None:
        err = "options应为null"
    else:
        items = q.get("reading_items") or []
        if not (2 <= len(items) <= 3):
            err = "子题数=%d" % len(items)
        else:
            idxs = []
            for j, it in enumerate(items):
                if it.get("type") != "choice":
                    err = "子题type错"
                    break
                opts = it.get("options") or []
                if len(opts) != 4:
                    err = "子题%d选项数=%d" % (j, len(opts))
                    break
                a = it.get("answer")
                if not (a and str(a).isdigit() and 0 <= int(a) < 4):
                    err = "子题%d answer=%r" % (j, a)
                    break
                if not (it.get("q") or "").strip():
                    err = "子题%d缺q" % j
                    break
                idxs.append(str(a))
            if not err:
                L = len(q.get("content", ""))
                if L < 80:
                    err = "文章太短%d字" % L
                elif ",".join(idxs) != q.get("answer"):
                    err = "answer不一致 期望%s 实际%r" % (",".join(idxs), q.get("answer"))
    if err:
        problems.append("%s / %s: %s" % (q.get("unit"), q.get("topic_name"), err))

print()
print("总计:", grand, "条 | 单元数:", len(set(q["unit"] for q in allitems)), "| 课时数:", len(set(q["topic_name"] for q in allitems)))
print("问题数:", len(problems))
for p in problems[:30]:
    print(" -", p)
