# -*- coding: utf-8 -*-
"""线上 ECS：跑迁移（加列）+ 重启服务"""
import json
import time
import urllib.request
import urllib.error

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
    except Exception as e:
        return None, str(e)


st, d = http("POST", "/api/auth/login", data={"username": "admin", "password": "admin" + "123"})
assert st == 200, f"login fail {st} {d}"
tok = d["access_token"]
print("[1] login ok")

# 幂等加列
st, r = http("POST", "/api/admin/exec-sql", tok=tok, data={"sql": "PRAGMA table_info(subjects)"})
cols = {x["name"] for x in r["rows"]}
if "allowed_types" not in cols:
    st, r = http("POST", "/api/admin/exec-sql", tok=tok,
                 data={"sql": "ALTER TABLE subjects ADD COLUMN allowed_types TEXT"})
    print("[2] ALTER subjects.allowed_types:", st, r.get("ok") if isinstance(r, dict) else r)
else:
    print("[2] subjects.allowed_types already exists")

st, r = http("POST", "/api/admin/exec-sql", tok=tok, data={"sql": "PRAGMA table_info(questions)"})
cols = {x["name"] for x in r["rows"]}
if "reading_items" not in cols:
    st, r = http("POST", "/api/admin/exec-sql", tok=tok,
                 data={"sql": "ALTER TABLE questions ADD COLUMN reading_items TEXT"})
    print("[3] ALTER questions.reading_items:", st, r.get("ok") if isinstance(r, dict) else r)
else:
    print("[3] questions.reading_items already exists")

# 重启
st, r = http("POST", "/api/admin/restart", tok=tok)
print("[4] restart:", st, r)
time.sleep(8)
ok = False
for i in range(15):
    st2, r2 = http("GET", "/api/health")
    if st2 == 200:
        print(f"[5] health ok after restart (try {i+1})")
        ok = True
        break
    time.sleep(3)
if not ok:
    print("[5] health still NOT ok!")
