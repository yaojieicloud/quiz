"""端到端验证：allowed_types 科目题型配置 + reading 阅读理解题型。
用法: python data/test_reading_feature.py [base_url]
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8123"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 保证能导入 core.security


def http(method, url, auth=None, data=None):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + auth
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def check(name, cond, extra=""):
    mark = "[PASS]" if cond else "[FAIL]"
    print(f"  {mark} {name}" + (f" | {extra}" if extra and not cond else ""))
    return cond


def main():
    ok = True
    st, res = http("POST", f"{BASE}/api/auth/login", data={"username": "admin", "password": "***"})
    if isinstance(res, dict) and res.get("access_token"):
        tk = res["access_token"]
    else:
        # 本地库 admin 密码未知时，直接用应用自己的 JWT 模块给 admin(id=3) 签 token
        from core.security import create_access_token
        tk = create_access_token({"sub": "3", "role": "admin"})
        print("[提示] 登录失败，已用 JWT 直签 admin token（仅本地测试）")

    print("\n===== 需求1: allowed_types 科目题型配置 =====")
    # 给语文(id=4)配置: 禁用 essay
    st, res = http("PUT", f"{BASE}/api/subjects/4", auth=tk,
                   data={"allowed_types": ["choice", "judge", "fill", "match", "sort"]})
    ok &= check("PUT allowed_types HTTP 200", st == 200, str(res)[:200])
    st, subs = http("GET", f"{BASE}/api/subjects", auth=tk)
    yw = [s for s in subs if s["id"] == 4][0]
    ok &= check("语文 available_types 已过滤 essay", "essay" not in yw["available_types"], str(yw["available_types"]))
    # 恢复为不限制
    st, res = http("PUT", f"{BASE}/api/subjects/4", auth=tk, data={"allowed_types": None})
    ok &= check("PUT null 恢复不限制 HTTP 200", st == 200)
    st, subs = http("GET", f"{BASE}/api/subjects", auth=tk)
    yw = [s for s in subs if s["id"] == 4][0]
    ok &= check("恢复后 essay 重新出现", "essay" in yw["available_types"])

    # 组卷过滤: 配置禁用 essay 后, 组卷抽不到 essay
    st, res = http("PUT", f"{BASE}/api/subjects/4", auth=tk,
                   data={"allowed_types": ["choice", "judge", "fill", "match", "sort"]})
    st, res = http("POST", f"{BASE}/api/exam/start", auth=tk,
                   data={"subject_id": 4, "types": [], "count": 50, "mode": "random"})
    types_in = {q["type"] for q in res.get("questions", [])}
    ok &= check("allowed_types 生效于组卷（essay 不被抽出）", "essay" not in types_in, str(types_in))
    # 显式请求 essay 也应被科目配置拦住（取交集）
    st, res2 = http("POST", f"{BASE}/api/exam/start", auth=tk,
                    data={"subject_id": 4, "types": ["essay"], "count": 10, "mode": "custom"})
    types2 = {q["type"] for q in res2.get("questions", [])}
    ok &= check("显式请求 essay 被科目配置拦截", "essay" not in types2, str(types2))
    # 恢复
    http("PUT", f"{BASE}/api/subjects/4", auth=tk, data={"allowed_types": None})

    print("\n===== 需求2: reading 阅读理解题型 =====")
    # 建一个测试章节
    st, topic = http("POST", f"{BASE}/api/topics", auth=tk,
                     data={"subject_id": 4, "name": "__测试阅读理解__", "unit": "上册-测试"})
    ok &= check("建测试章节 HTTP 200", st == 200, str(topic)[:200])
    tid = topic["id"]

    reading_q = {
        "subject_id": 4, "topic_id": tid, "type": "reading",
        "content": "春天来了，小明和小红去公园放风筝。\n风筝飞得很高，他们非常开心。",
        "options": None,
        "reading_items": [
            {"type": "choice", "q": "他们去公园做什么？", "options": ["放风筝", "游泳", "爬山", "钓鱼"], "answer": "0", "explanation": "文中说去公园放风筝。"},
            {"type": "choice", "q": "风筝飞得怎么样？", "options": ["很低", "很高", "飞走了", "掉下来了"], "answer": "1", "explanation": "文中说风筝飞得很高。"},
        ],
        "answer": "0,1",
        "explanation": "",
        "difficulty": 2,
    }
    st, q = http("POST", f"{BASE}/api/questions", auth=tk, data=reading_q)
    ok &= check("创建 reading 题 HTTP 200", st == 200, str(q)[:200])
    qid = q["id"]
    _created_records = []

    # 组卷抽到该题，检查子题答案未泄露
    st, res = http("POST", f"{BASE}/api/exam/start", auth=tk,
                   data={"subject_id": 4, "topic_ids": [tid], "types": ["reading"], "count": 1, "mode": "custom"})
    got = res.get("questions", [])
    ok &= check("组卷能抽到 reading 题", len(got) == 1)
    if got:
        items = got[0].get("reading_items") or []
        leaked = any(("answer" in it) or ("explanation" in it) for it in items)
        ok &= check("下发子题不含 answer/explanation（防泄题）", not leaked and len(items) == 2, str(items))

    # 提交判分: 2 题全对 → 100
    st, rec = http("POST", f"{BASE}/api/exam/submit", auth=tk,
                   data={"subject_id": 4, "answers": [{"question_id": qid, "user_answer": "0,1"}], "duration_seconds": 30})
    ok &= check("全对: score=100 correct=1", st == 200 and rec.get("score") == 100 and rec.get("correct") == 1, json.dumps(rec, ensure_ascii=False)[:300])
    _created_records.append(rec["id"])
    # 对一半 → answer_record 得 50 分，但 <60 不算对，试卷层面该题计错
    st, rec = http("POST", f"{BASE}/api/exam/submit", auth=tk,
                   data={"subject_id": 4, "answers": [{"question_id": qid, "user_answer": "0,0"}], "duration_seconds": 30})
    ok &= check("半对: correct=0 (50分<60不计对)", st == 200 and rec.get("correct") == 0, json.dumps(rec, ensure_ascii=False)[:300])
    _created_records.append(rec["id"])
    st, detail = http("GET", f"{BASE}/api/exam/records/{rec['id']}", auth=tk)
    ar = (detail.get("answer_records") or [{}])[0]
    ok &= check("半对: answer_record llm_score=50", ar.get("llm_score") == 50, str(ar.get("llm_score")))
    # 空答案 → 0 分
    st, rec = http("POST", f"{BASE}/api/exam/submit", auth=tk,
                   data={"subject_id": 4, "answers": [{"question_id": qid, "user_answer": None}], "duration_seconds": 30})
    ok &= check("未作答: score=0", st == 200 and rec.get("score") == 0)
    _created_records.append(rec["id"])

    # 清理: 先删答题记录（会级联删 answer_records），再删错题记录，最后删题删章节
    for rec_id in _created_records:
        http("DELETE", f"{BASE}/api/admin/records/{rec_id}", auth=tk)
    # 错题本里若残留该题（半对提交时写入），逐条删除
    st, wqs = http("GET", f"{BASE}/api/wrong-questions", auth=tk)
    if st == 200 and isinstance(wqs, list):
        for w in wqs:
            if w.get("question_id") == qid:
                http("DELETE", f"{BASE}/api/wrong-questions/{w['id']}", auth=tk)
    st, msg = http("DELETE", f"{BASE}/api/questions/{qid}", auth=tk)
    ok &= check("清理测试题", st == 200, str(msg)[:200])
    st, msg = http("DELETE", f"{BASE}/api/topics/{tid}", auth=tk)
    ok &= check("清理测试章节", st == 200, str(msg)[:200])

    print("\n" + ("[ALL PASS]" if ok else "[HAS FAILURES]"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
