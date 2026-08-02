"""把本地改动通过热更新 API 推送到 ECS 实例（/app 目录），无需重建镜像。

用法:
    python data/push_ecs.py            # 推送下列文件
    python data/push_ecs.py --url http://106.14.99.100:8000
"""
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # quiz_system/
DEFAULT_URL = "http://106.14.99.100:8000"
USER, PW = "admin", "admin123"

# (本地相对路径, 容器内绝对路径)
FILES = [
    ("models.py", "/app/models.py"),
    ("schemas.py", "/app/schemas.py"),
    ("routers/exam.py", "/app/routers/exam.py"),
    ("routers/subjects.py", "/app/routers/subjects.py"),
    ("routers/questions.py", "/app/routers/questions.py"),
    ("routers/admin.py", "/app/routers/admin.py"),
    ("core/code_runner.py", "/app/core/code_runner.py"),
    ("core/llm_grader.py", "/app/core/llm_grader.py"),
    ("static/admin.html", "/app/static/admin.html"),
    ("static/js/common.js", "/app/static/js/common.js"),
    ("static/quiz.html", "/app/static/quiz.html"),
    ("static/home.html", "/app/static/home.html"),
    ("static/records.html", "/app/static/records.html"),
    ("static/wrong.html", "/app/static/wrong.html"),
    ("static/css/common.css", "/app/static/css/common.css"),
]


def http(method, url, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa
        return None, str(e)


def login(base):
    st, res = http("POST", f"{base}/api/auth/login", data={"username": USER, "password": PW})
    if st != 200 or "access_token" not in res:
        print(f"[错误] 登录失败 (HTTP {st}): {res}")
        sys.exit(1)
    return res["access_token"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    args = ap.parse_args()
    base = args.url.rstrip("/")
    tok = login(base)

    ok = 0
    for local, remote in FILES:
        p = ROOT / local
        if not p.exists():
            print(f"[跳过] 本地不存在: {local}")
            continue
        content = p.read_text(encoding="utf-8")
        st, res = http("POST", f"{base}/api/admin/update-file", token=tok,
                        data={"path": remote, "content": content})
        mark = "OK " if st == 200 else "FAIL"
        print(f"[{mark}] {st}  {remote}  ({len(content)} chars)"
              + ("" if st == 200 else f"  -> {res}"))
        if st == 200:
            ok += 1
    print(f"\n已推送 {ok}/{len(FILES)} 个文件。下一步：ALTER TABLE + restart。")


if __name__ == "__main__":
    main()
