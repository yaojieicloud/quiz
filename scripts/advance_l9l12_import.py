"""L9-L12 (topic 53-56) 进阶题：导入 ECS + 组卷/评分验证 + 清理验证记录。"""
import urllib.request, json, sys
sys.path.insert(0, ".")
from advance_l9l12_verify import QUESTIONS

BASE = "http://106.14.99.100:8000"

def req(method, url, body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# ---- 登录 ----
st, body = req("POST", BASE + "/api/auth/login", {"username": "admin", "password": "admin123"})
assert st == 200, f"login failed {st} {body}"
TOK = body["access_token"]
print("登录 OK, admin id =", body["user"]["id"])

# ---- 现有 tier2 数量（避免重复导入） ----
print("\n[1] 导入前现状：")
for tid in range(53, 57):
    st, qs = req("GET", f"{BASE}/api/questions?topic_id={tid}", tok=TOK)
    t2 = [q for q in qs if q["tier"] == 2]
    print(f"  topic {tid}: 总题 {len(qs)}, 已有 tier2 = {len(t2)}")

# ---- 构造 payload 并批量导入 ----
payload = []
for q in QUESTIONS:
    payload.append({
        "subject_id": 3,
        "topic_id": q["topic_id"],
        "type": "code",
        "content": q["content"],
        "answer": q["answer"],
        "explanation": q["explanation"],
        "difficulty": 2,
        "tier": 2,
        "expected_output": None,
        "sample_input": q["sample_input"],
    })
st, body = req("POST", BASE + "/api/questions/batch", payload, tok=TOK)
print("\n[2] 批量导入:", st, body)
assert st == 200 and body.get("created") == len(QUESTIONS), f"batch fail {st} {body}"

# ---- 组卷验证：每 topic tier=2 应得 2 题（含新题） ----
print("\n[3] 组卷验证（tier=2, custom, topic 单课）：")
new_ids = []
for tid in range(53, 57):
    st, data = req("POST", BASE + "/api/exam/start", {
        "subject_id": 3, "topic_ids": [tid], "types": ["code"],
        "count": 10, "mode": "custom", "tier": 2
    }, tok=TOK)
    qs = data.get("questions", [])
    ids = [q["id"] for q in qs]
    new_ids.extend(ids)
    print(f"  topic {tid}: 返回 {len(qs)} 题, ids={ids}")

# ---- 反向验证：tier=1 组卷不应包含新题 ----
print("\n[4] 反向验证（tier=1 不应含新题）：")
for tid in range(53, 57):
    st, data = req("POST", BASE + "/api/exam/start", {
        "subject_id": 3, "topic_ids": [tid], "types": ["code"],
        "count": 50, "mode": "custom", "tier": 1
    }, tok=TOK)
    qs = data.get("questions", [])
    leak = [q["id"] for q in qs if q["id"] in new_ids]
    print(f"  topic {tid}: tier1 返回 {len(qs)} 题, 含新题={leak if leak else '无(正确)'}")

# ---- 评分验证：提交参考解（admin 作答），确认 score>=60 且积分>0 ----
print("\n[5] 评分验证（提交参考解，验证 sample_input 生效 / 不 EOFError）：")
record_ids = []
all_ok = True
for tid in range(53, 57):
    # admin 列表可见 answer
    st, qs = req("GET", f"{BASE}/api/questions?topic_id={tid}", tok=TOK)
    new = [q for q in qs if q["tier"] == 2]
    answers = [{"question_id": q["id"], "user_answer": q["answer"]} for q in new]
    st2, sub = req("POST", BASE + "/api/exam/submit", {
        "subject_id": 3, "mode": "custom", "topic_ids": [tid],
        "answers": answers, "tier": 2
    }, tok=TOK)
    assert st2 == 200, f"submit fail {st2} {sub}"
    record_ids.append(sub["id"])
    line = f"  topic {tid} (record {sub['id']}, points={sub['points_earned']}): "
    for ar in sub["answer_records"]:
        ok = (ar["llm_score"] or 0) >= 60
        all_ok = all_ok and ok
        line += f"[q{ar['question_id']} score={ar['llm_score']} correct={ar['is_correct']}] "
    print(line + ("OK" if all_ok else "FAIL"))

# ---- 清理验证产生的答题记录（避免污染真实数据） ----
print("\n[6] 清理验证记录：")
for rid in record_ids:
    st, _ = req("DELETE", f"{BASE}/api/admin/records/{rid}", tok=TOK)
    print(f"  delete record {rid}: {st}")

print("\n=== 结果：", "全部 PASS" if all_ok else "存在 FAIL，需检查", "===")
