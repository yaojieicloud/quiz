"""拉线上全库到临时库，测试：
  1) GET /api/subjects/{id}/topics?tier=1 的 question_count / valid_by_tier 是否排除弃用+按档位过滤
  2) topics 接口的 question_count 是否与 /api/exam/available-count 一致（同一口径）
"""
import os, sys, sqlite3, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

DB_PATH = os.path.join(os.path.dirname(__file__), "_test_live.db")
os.environ["QUIZ_DB_PATH"] = DB_PATH
BASE = "http://106.14.99.100:8000"

def login():
    r = requests.post(BASE + "/api/auth/login", json={"username": "admin", "password": "admin123"}, timeout=30)
    r.raise_for_status(); return r.json()["access_token"]

def exec_sql(token, sql):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(BASE + "/api/admin/exec-sql", headers=h, json={"sql": sql, "script": False}, timeout=60)
    r.raise_for_status(); return r.json()

def pull():
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    tok = login()
    tables = [r["name"] for r in exec_sql(tok, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")["rows"]]
    tables = [t for t in tables if not t.startswith("sqlite_")]
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    for t in tables:
        cur.execute(exec_sql(tok, f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'")["rows"][0]["sql"])
        cols = [r["name"] for r in exec_sql(tok, f"PRAGMA table_info('{t}')")["rows"]]
        n = exec_sql(tok, f"SELECT COUNT(*) AS c FROM {t}")["rows"][0]["c"]
        off = 0
        while off < n:
            rows = exec_sql(tok, f"SELECT * FROM {t} LIMIT 500 OFFSET {off}")["rows"]
            if not rows: break
            cur.executemany(f"INSERT INTO {t} ({', '.join(cols)}) VALUES ({', '.join(['?']*len(cols))})", [list(r.values()) for r in rows])
            off += len(rows)
        conn.commit()
    conn.close()

def main():
    print("[1] 拉取线上库")
    pull()
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    tok = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}

    def ac(subject_id, topic_ids, tier=1):
        r = client.post("/api/exam/available-count", json={"subject_id": subject_id, "topic_ids": topic_ids, "tier": tier, "count": 50, "mode": "custom"}, headers=H)
        return r.json()["available"]

    print("[2] 测试 topics 接口 tier 过滤 + 与 available-count 一致性")
    # 语文=4, 英语=5, 数学=2, Python理论=1
    checks = []
    for sid, tid, name in [(4,175,"语文t175"), (5,169,"英语t169"), (2,19,"数学t19"), (1,27,"Python理论t27")]:
        tr = client.get(f"/api/subjects/{sid}/topics?tier=1", headers=H).json()
        t = next((x for x in tr if x["id"] == tid), None)
        assert t, f"{name} 未在 topics 返回中找到"
        qc = t["question_count"]
        vbt = t["valid_by_tier"]
        ac_v = ac(sid, [tid], tier=1)
        ok_qc_eq_t1 = (qc == vbt.get("1", 0))
        ok_match_avail = (qc == ac_v)
        checks.append((name, qc, vbt, ac_v, ok_qc_eq_t1, ok_match_avail))
        print(f"  {name}: question_count(tier1)={qc}  valid_by_tier={vbt}  available-count={ac_v}  | qc==t1:{ok_qc_eq_t1}  qc==avail:{ok_match_avail}")

    print("[3] 测试 subjects 列表 tier 过滤")
    subs = client.get("/api/subjects?tier=1", headers=H).json()
    for s in subs:
        print(f"  科目 {s['name']}(id={s['id']}): question_count(tier1)={s['question_count']}")

    all_ok = all(c[4] and c[5] for c in checks)
    print("\n结果:", "PASS ✅" if all_ok else "FAIL ❌")
    return all_ok

if __name__ == "__main__":
    main()
