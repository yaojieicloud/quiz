# -*- coding: utf-8 -*-
"""部署 LLM 评分器切换：写入 key 文件 + 推送 llm_grader.py + restart"""
import urllib.request, urllib.error, json, sys
from pathlib import Path

BASE = "http://106.14.99.100:8000"
KEY = "sk-sp-H.XIRYR.qxbw.MEUCIQDXPYWFktl-mSJUsDTRzxat2ZN6rB6ze3xdAj9CeIT-BwIgOegL2v0X5iwMDjcrsI78ATRsVZ1y1ON3W8tiS7SBKa8"
LOCAL_FILE = Path(r"C:\Users\Yaojie\Documents\GitHub\quiz\src\core\llm_grader.py")


def http(method, path, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)


# 1) 登录
st, res = http("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"})
assert st == 200, f"登录失败 {st} {res}"
tok = res["access_token"]
print("[1] 登录成功")

# 2) 写入新 key 文件到数据卷（/app/data/llm_key.txt，不进代码）
st, res = http("POST", "/api/admin/update-file", token=tok,
               data={"path": "/app/data/llm_key.txt", "content": KEY + "\n"})
assert st == 200, f"写 key 失败 {st} {res}"
print(f"[2] key 文件已写入: /app/data/llm_key.txt ({res.get('bytes')} bytes)")

# 3) 推送新版 llm_grader.py
content = LOCAL_FILE.read_text(encoding="utf-8")
st, res = http("POST", "/api/admin/update-file", token=tok,
               data={"path": "/app/core/llm_grader.py", "content": content})
assert st == 200, f"推送失败 {st} {res}"
print(f"[3] llm_grader.py 已推送 ({len(content)} chars)")

# 4) restart 加载新代码（后端改动必须重启）
st, res = http("POST", "/api/admin/restart", token=tok, data={})
print(f"[4] restart 触发: {res}")
