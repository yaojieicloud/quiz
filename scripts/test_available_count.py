"""拉取线上全库(跳过内部表)到临时库，用 TestClient 真实验证 /api/exam/available-count。
验证点：
  - 语文单课时(topic 175) tier1 -> 应 <50 (已知 18)
  - 英语单课时(topic 169) tier1 -> 应 <50 (已知 26)
  - 数学单课时(topic 19)  tier1 -> 应 >=50 (已知 56)
  - 语文整科(topic_ids=[]) tier1 -> 应 >=50
"""
import os, sys, sqlite3, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

DB_PATH = os.path.join(os.path.dirname(__file__), "_test_live.db")
os.environ["QUIZ_DB_PATH"] = DB_PATH

BASE = "http://106.14.99.100:8000"

def login():
    r = requests.post(BASE + "/api/auth/login", json={"username": "admin", "password": "admin123"}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def exec_sql(token, sql):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(BASE + "/api/admin/exec-sql", headers=h, json={"sql": sql, "script": False}, timeout=60)
    r.raise_for_status()
    return r.json()

def pull():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    tok = login()
    tables = [r["name"] for r in exec_sql(tok, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")["rows"]]
    tables = [t for t in tables if not t.startswith("sqlite_")]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for t in tables:
        create = exec_sql(tok, f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")["rows"][0]["sql"]
        cur.execute(create)
        cols = [r["name"] for r in exec_sql(tok, f"PRAGMA table_info('{t}')")["rows"]]
        n = exec_sql(tok, f"SELECT COUNT(*) AS c FROM {t}")["rows"][0]["c"]
        off = 0
        while off < n:
            rows = exec_sql(tok, f"SELECT * FROM {t} LIMIT 500 OFFSET {off}")["rows"]
            if not rows:
                break
            ph = ", ".join(["?"] * len(cols))
            cur.executemany(f"INSERT INTO {t} ({', '.join(cols)}) VALUES ({ph})", [list(r.values()) for r in rows])
            off += len(rows)
        conn.commit()
        print(f"  拉取 {t}: {n} 行")
    conn.close()
    print("全库拉取完成 ->", DB_PATH)

def main():
    print("[1] 拉取线上库到临时库")
    pull()

    print("[2] 启动 TestClient 验证接口")
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    # 登录
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    tok = r.json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}

    def ac(subject_id, topic_ids, tier=1):
        body = {"subject_id": subject_id, "topic_ids": topic_ids, "tier": tier, "count": 50, "mode": "custom"}
        r = client.post("/api/exam/available-count", json=body, headers=H)
        assert r.status_code == 200, r.text
        return r.json()["available"]

    # 科目 id: 语文=4, 英语=5, 数学=2
    yw_single = ac(4, [175])      # 语文单课时
    en_single = ac(5, [169])      # 英语单课时
    math_single = ac(2, [19])     # 数学单课时
    yw_all = ac(4, [])            # 语文整科

    print(f"  语文 单课时(t175) tier1 可用: {yw_single}  (期望 <50)")
    print(f"  英语 单课时(t169) tier1 可用: {en_single}  (期望 <50)")
    print(f"  数学 单课时(t19)  tier1 可用: {math_single}  (期望 >=50)")
    print(f"  语文 整科        tier1 可用: {yw_all}  (期望 >=50)")

    ok = (yw_single < 50) and (en_single < 50) and (math_single >= 50) and (yw_all >= 50)
    print("\n结果:", "PASS ✅" if ok else "FAIL ❌")
    return ok

if __name__ == "__main__":
    main()
