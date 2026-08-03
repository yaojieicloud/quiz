"""把纯数组格式的题库 JSON 导入 ECS 线上系统。

适配 english_grade3_vol1/vol2.json、chinese_grade3_vol1.json 这类纯数组格式，
完整传递 match_options / blank_count / blank_answers / tolerance 等字段，
按 topic_name 自动建/复用章节（带 unit），按 content 去重。

用法:
    python data/import_array.py --subject-id 5 --json data/english_grade3_vol1.json --label 英语三上
"""
import argparse
import json
import sys
import urllib.request
import urllib.error


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
    except Exception as e:
        return None, str(e)


def import_one(base, token, subject_id, json_path, label, unit_prefix=""):
    print(f"\n===== 导入 {label} ({json_path}) → subject_id={subject_id} =====")
    questions = json.loads(open(json_path, encoding="utf-8").read())
    if not isinstance(questions, list):
        print(f"[错误] {json_path} 不是纯数组格式")
        return False
    print(f"[读取] {len(questions)} 题" + (f" | 单元前缀: {unit_prefix}" if unit_prefix else ""))

    # 去重：拉取该科目已有题目的 content
    st, exist = http("GET", f"{base}/api/questions?subject_id={subject_id}", token=token)
    existing = set()
    if st == 200:
        for q in (exist if isinstance(exist, list) else exist.get("items", [])):
            existing.add((q.get("content") or "").strip())
    print(f"[去重] 科目内已有 {len(existing)} 题")

    # 取已有章节，建立 (章节名, 单元)->id 映射（按 名称+单元 精确匹配，避免跨册重名误复用）
    st, topics = http("GET", f"{base}/api/subjects/{subject_id}/topics", token=token)
    topic_map = {}
    if st == 200:
        for t in topics:
            topic_map[(t["name"], t.get("unit"))] = t["id"]
    print(f"[章节] 已有 {len(topic_map)} 个")

    # 组装批量导入 payload
    items = []
    new_topic = 0
    skipped = 0
    for q in questions:
        if (q.get("content") or "").strip() in existing:
            skipped += 1
            continue
        tname = q["topic_name"]
        unit = (unit_prefix + q.get("unit")) if q.get("unit") else unit_prefix or None
        key = (tname, unit)
        if key not in topic_map:
            st, t = http("POST", f"{base}/api/topics", token=token,
                         data={"subject_id": subject_id, "name": tname, "unit": unit})
            if st != 200:
                print(f"[警告] 建章节「{tname}」失败 HTTP {st}: {t}")
                continue
            topic_map[key] = t["id"]
            new_topic += 1
        items.append({
            "subject_id": subject_id,
            "topic_id": topic_map[key],
            "type": q["type"],
            "content": q["content"],
            "options": q.get("options"),
            "match_options": q.get("match_options"),
            "reading_items": q.get("reading_items"),
            "answer": str(q["answer"]),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", 1),
            "is_multiple": q.get("is_multiple", False),
            "blank_count": q.get("blank_count", 1),
            "blank_answers": q.get("blank_answers"),
            "tolerance": q.get("tolerance", 0.01),
        })

    if not items:
        print(f"[完成] 无新题可导入（全部重复或章节创建失败）")
        return True

    st, res = http("POST", f"{base}/api/questions/batch", token=token, data=items)
    if st == 200:
        print(f"[完成] HTTP {st} | 新增 {res.get('created')} 题（新建章节 {new_topic}，跳过重复 {skipped}）")
        return True
    else:
        print(f"[错误] 批量导入失败 HTTP {st}: {res}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://106.14.99.100:8000")
    ap.add_argument("--user", default="admin")
    ap.add_argument("--pw", default="admin123")
    ap.add_argument("--subject-id", type=int, required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--unit-prefix", default="", help="给单元名统一加前缀（如 '下册-'），用于区分上下册")
    args = ap.parse_args()

    base = args.url.rstrip("/")
    st, res = http("POST", f"{base}/api/auth/login", data={"username": args.user, "password": args.pw})
    if st != 200 or "access_token" not in res:
        print(f"[错误] 登录失败 HTTP {st}: {res}")
        sys.exit(1)
    token = res["access_token"]
    print(f"[登录] 成功")

    ok = import_one(base, token, args.subject_id, args.json, args.label, args.unit_prefix)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
