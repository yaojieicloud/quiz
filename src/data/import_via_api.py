"""通过 HTTP API 把数学 1000 题导入 ECS 上的运行实例

用法:
    python data/import_via_api.py
    python data/import_via_api.py --url http://106.14.99.100:8000 --user admin --pw admin123

流程：登录(admin) -> 取科目ID -> 取已有章节 -> 复用/新建章节 -> 批量导入题目
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = ROOT / "python_coding200.json"


def http(method, url, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        try:
            detail = json.loads(detail).get("detail", detail)
        except Exception:
            pass
        return e.code, detail
    except Exception as e:  # 网络等错误
        return None, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://106.14.99.100:8000")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--pw", default="admin123")
    ap.add_argument("--json", default=str(DEFAULT_JSON))
    args = ap.parse_args()

    base = args.url.rstrip("/")
    payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
    subject_name = payload["subject"]["name"]
    questions = payload["questions"]
    print(f"题目文件: {args.json} ({len(questions)} 题), 目标科目: {subject_name}")

    # 1) 登录
    st, res = http("POST", f"{base}/api/auth/login",
                   data={"username": args.user, "password": args.pw})
    if st != 200 or "access_token" not in res:
        print(f"[错误] 登录失败 (HTTP {st}): {res}")
        sys.exit(1)
    token = res["access_token"]
    print(f"[登录] 成功，用户: {res.get('user', {}).get('username')} / 角色: {res.get('user', {}).get('role')}")

    # 2) 取科目列表，找目标
    st, subs = http("GET", f"{base}/api/subjects", token=token)
    subject_id = None
    if st == 200:
        for s in subs:
            if s["name"] == subject_name:
                subject_id = s["id"]
                break
    if not subject_id:
        # 科目不存在则自动创建
        sub_info = payload.get("subject", {})
        st, new_sub = http("POST", f"{base}/api/subjects", token=token, data={
            "name": subject_name,
            "description": sub_info.get("desc"),
            "icon": sub_info.get("icon", "📚"),
            "grade": sub_info.get("grade"),
            "category": sub_info.get("category", "culture"),
        })
        if st != 200:
            print(f"[错误] 创建科目失败 (HTTP {st}): {new_sub}")
            sys.exit(1)
        subject_id = new_sub["id"]
        print(f"[科目] 自动创建: {subject_name} (id={subject_id}, category={new_sub.get('category')})")
    print(f"[科目] id={subject_id} ({subject_name})")

    # 2.5) 去重：拉取该科目已有题目的 content，避免重复导入（重跑脚本不会翻倍）
    st, exist = http("GET", f"{base}/api/questions?subject_id={subject_id}", token=token)
    existing_contents = set()
    if st == 200:
        for q in exist:
            existing_contents.add((q.get("content") or "").strip())
    print(f"[去重] 科目内已有 {len(existing_contents)} 题，重复 content 将跳过")

    # 3) 取已有章节，建立 章节名->id 映射
    st, topics = http("GET", f"{base}/api/subjects/{subject_id}/topics", token=token)
    topic_map = {}
    if st == 200:
        for t in topics:
            topic_map[t["name"]] = t["id"]
    print(f"[章节] 已有 {len(topic_map)} 个: {list(topic_map.keys())}")

    # 4) 组装批量导入 payload（复用章节；缺失则新建）
    items = []
    new_topic_count = 0
    skipped = 0
    for q in questions:
        # 去重：content 已存在则跳过（重跑脚本不会翻倍）
        if (q.get("content") or "").strip() in existing_contents:
            skipped += 1
            continue
        tname = q["topic_name"]
        if tname not in topic_map:
            st, t = http("POST", f"{base}/api/topics", token=token,
                         data={"subject_id": subject_id, "name": tname, "unit": q.get("unit")})
            if st != 200:
                print(f"[警告] 创建章节「{tname}」失败 (HTTP {st}): {t}")
                continue
            topic_map[tname] = t["id"]
            new_topic_count += 1
        items.append({
            "subject_id": subject_id,
            "topic_id": topic_map[tname],
            "type": q["type"],
            "content": q["content"],
            "options": q.get("options"),
            "answer": str(q["answer"]),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", 1),
            "expected_output": q.get("expected_output") or None,
            "sample_input": q.get("sample_input", "") or "",
        })

    # 5) 批量导入
    st, res = http("POST", f"{base}/api/questions/batch", token=token, data=items)
    if st == 200:
        print(f"[完成] HTTP {st} | 新增 {res.get('created')} 题"
              f"（新建章节 {new_topic_count} 个，跳过重复 {skipped} 题）")
    else:
        print(f"[错误] 批量导入失败 HTTP {st}: {res}")


if __name__ == "__main__":
    main()
