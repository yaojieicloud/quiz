# -*- coding: utf-8 -*-
"""查询线上语文/英语的课时结构（复用 push_ecs.py 里可用的账号）"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from push_ecs import USER, PW  # noqa: E402

B = "http://106.14.99.100:8000"


def http(method, path, tok=None, data=None):
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    b = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(B + path, data=b, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return x.status, json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


st, d = http("POST", "/api/auth/login", data={"username": USER, "password": PW})
if st != 200:
    print("login fail:", st, d)
    sys.exit(1)
tok = d["access_token"]

for sid, name in [(4, "语文"), (5, "英语")]:
    st, topics = http("GET", f"/api/subjects/{sid}/topics", tok=tok)
    print(f"\n===== {name} (id={sid}) 共 {len(topics)} 个课时 =====")
    units = {}
    for t in topics:
        units.setdefault(t.get("unit") or "(无单元)", []).append(f"{t['name']}({t['question_count']}题)")
    for u, ts in units.items():
        print(f"[{u}] {len(ts)} 课时: " + "、".join(ts))
