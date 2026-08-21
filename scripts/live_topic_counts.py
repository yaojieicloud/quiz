"""直接查线上 ECS，统计每课时在各档位(tier)与全题型合计的有效题量（非弃用）。
用于回答：语文/英语/数学 单课时所有题型加起来是否够 50 题。
"""
import requests, json, statistics

BASE = "http://106.14.99.100:8000"

def login():
    r = requests.post(BASE + "/api/auth/login", json={"username": "admin", "password": "admin123"})
    r.raise_for_status()
    return r.json()["access_token"]

def exec_sql(token, sql):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(BASE + "/api/admin/exec-sql", headers=h, json={"sql": sql, "script": False})
    r.raise_for_status()
    return r.json()

def main():
    tok = login()
    sql = """
    SELECT s.name AS sname, t.id AS tid, t.name AS tname,
      COUNT(q.id) AS valid_all,
      SUM(CASE WHEN q.tier=1 THEN 1 ELSE 0 END) AS t1,
      SUM(CASE WHEN q.tier=2 THEN 1 ELSE 0 END) AS t2,
      SUM(CASE WHEN q.tier=3 THEN 1 ELSE 0 END) AS t3
    FROM topics t
    JOIN subjects s ON t.subject_id = s.id
    LEFT JOIN questions q ON q.topic_id = t.id AND (q.deprecated IS NULL OR q.deprecated = 0)
    GROUP BY t.id
    ORDER BY s.name, valid_all
    """
    res = exec_sql(tok, sql)
    rows = res["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["sname"], []).append(r)

    def show(name):
        rs = by.get(name, [])
        if not rs:
            print(f"\n=== {name}: 未找到 ==="); return
        va = [r["valid_all"] for r in rs]
        t1 = [r["t1"] for r in rs]
        t2 = [r["t2"] for r in rs]
        t3 = [r["t3"] for r in rs]
        print(f"\n=== {name}（{len(rs)} 课时）===")
        print(f"  全题型全档位合计 ≥50 的课时 : {sum(1 for x in va if x>=50)}/{len(rs)}")
        print(f"  仅 tier1(初级) ≥50 的课时   : {sum(1 for x in t1 if x>=50)}/{len(rs)}")
        print(f"  仅 tier2(进阶) ≥50 的课时   : {sum(1 for x in t2 if x>=50)}/{len(rs)}")
        print(f"  仅 tier3(挑战) ≥50 的课时   : {sum(1 for x in t3 if x>=50)}/{len(rs)}")
        print(f"  全合计题量  min/median/max : {min(va)}/{int(statistics.median(va))}/{max(va)}")
        print(f"  tier1 题量   min/median/max : {min(t1)}/{int(statistics.median(t1))}/{max(t1)}")
        print("  题量最少 5 个课时 (合计/t1/t2/t3):")
        for r in sorted(rs, key=lambda x: x["valid_all"])[:5]:
            print(f"    t{r['tid']:>3} {r['tname'][:12]:<12} 全={r['valid_all']:>3} t1={r['t1']:>3} t2={r['t2']:>3} t3={r['t3']:>3}")

    for n in ["语文","英语","数学","Python基础理论","Python基础实操"]:
        show(n)

if __name__ == "__main__":
    main()
