"""把本地语文/英语科目及章节结构同步到线上 ECS"""
import urllib.request, json, sqlite3, sys

B = "http://106.14.99.100:8000"
LOCAL_DB = r"C:\Users\Yaojie\Documents\GitHub\quiz\src\quiz.db"

def api(method, path, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(B + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:
        return None, str(e)

def main():
    # 1. 登录
    st, d = api("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"})
    if st != 200:
        print("登录失败:", d); sys.exit(1)
    tok = d["access_token"]
    print("✓ 登录成功")

    # 2. 检查线上已有哪些科目
    st, subjects = api("GET", "/api/subjects", token=tok)
    existing = {s["name"]: s["id"] for s in subjects}
    print(f"线上已有科目: {list(existing.keys())}")

    # 3. 读本地库
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row

    # 要同步的科目：语文(4)、英语(5)
    target_ids = [4, 5]
    for sid in target_ids:
        row = conn.execute(
            "SELECT id, name, icon, grade, category, sort_order, description FROM subjects WHERE id=?", (sid,)
        ).fetchone()
        if not row:
            print(f"  本地无科目 id={sid}，跳过"); continue
        name = row["name"]
        if name in existing:
            print(f"  线上已有「{name}」(id={existing[name]})，跳过科目创建")
            subject_id_online = existing[name]
        else:
            # 创建科目
            payload = {
                "name": name,
                "icon": row["icon"],
                "grade": row["grade"],
                "category": row["category"],
                "description": row["description"] or "",
            }
            st2, resp = api("POST", "/api/subjects", token=tok, data=payload)
            if st2 != 200:
                print(f"  ✗ 创建科目「{name}」失败: {st2} {resp}"); continue
            subject_id_online = resp["id"]
            print(f"  ✓ 创建科目「{name}」→ id={subject_id_online}")
            # 设置 sort_order
            api("PUT", f"/api/subjects/{subject_id_online}", token=tok, data={"sort_order": row["sort_order"]})

        # 4. 同步章节
        topics = conn.execute(
            "SELECT id, name, unit, sort_order FROM topics WHERE subject_id=? ORDER BY id", (sid,)
        ).fetchall()
        print(f"  「{name}」共 {len(topics)} 个章节，开始同步...")
        ok = 0
        for t in topics:
            payload = {
                "subject_id": subject_id_online,
                "name": t["name"],
                "unit": t["unit"],
            }
            if t["sort_order"] is not None:
                payload["sort_order"] = t["sort_order"]
            st3, resp = api("POST", "/api/topics", token=tok, data=payload)
            if st3 == 200:
                ok += 1
            else:
                print(f"    ✗ 章节「{t['name']}」失败: {st3} {resp}")
        print(f"  ✓ 「{name}」章节同步完成 {ok}/{len(topics)}")

    conn.close()
    print("\n=== 同步完成 ===")

if __name__ == "__main__":
    main()
