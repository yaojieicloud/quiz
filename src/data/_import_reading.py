# -*- coding: utf-8 -*-
"""把 9 个 reading 文件依次导入线上语文科目(subject_id=4)，并校验导入结果"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

D = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese"
SRC = r"C:\Users\Yaojie\Documents\GitHub\quiz\src"

files = [f for f in sorted(os.listdir(D)) if f.endswith(".json")]

for f in files:
    p = os.path.join(D, f)
    cmd = [sys.executable, "data/import_array.py",
           "--subject-id", "4", "--json", p, "--label", f"语文阅读理解-{f}"]
    r = subprocess.run(cmd, cwd=SRC, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or "").strip().splitlines()
    print(f"[{f}]", tail[-1] if tail else r.stderr[:200])

# 导入后校验线上 reading 题数量
import importlib.util
spec = importlib.util.spec_from_file_location("push_ecs", os.path.join(SRC, "data", "push_ecs.py"))
pe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pe)


def http(method, url, tok=None, data=None):
    headers = {"Content-Type": "application/json"}
    if tok:
        headers["Authorization"] = "Bearer " + tok
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as x:
            return x.status, json.loads(x.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


st, d = http("POST", pe.DEFAULT_URL + "/api/auth/login", data={"username": pe.USER, "password": pe.PW})
tok = d["access_token"]
st, qs = http("GET", pe.DEFAULT_URL + "/api/questions?subject_id=4&type=reading", tok=tok)
print("\n线上语文 reading 题总数:", len(qs))
from collections import Counter
c = Counter(q["topic_name"] for q in qs)
print("覆盖课时数:", len(c), "| 每课篇数分布:", sorted(set(c.values())))
