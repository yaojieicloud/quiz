"""进阶题 100 道（L1-L20 每课5题）导入 ECS + 组卷/评分验证 + 清理验证记录。
聚合 advance_b1..b5 五个批次模块的 QUESTIONS。
"""
import urllib.request, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advance_b1_l1l4_verify import QUESTIONS as B1
from advance_b2_l5l8_verify import QUESTIONS as B2
from advance_b3_l9l12_verify import QUESTIONS as B3
from advance_b4_l13l16_verify import QUESTIONS as B4
from advance_b5_l17l20_verify import QUESTIONS as B5

QUESTIONS = B1 + B2 + B3 + B4 + B5

BASE = "http://106.14.99.100:8000"

def req(method, url, body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# ---- 登录 ----
st, body = req("POST", BASE + "/api/auth/login", {"username": "admin", "password": "admin123"})
assert st == 200, f"login failed {st} {body}"
TOK = body["access_token"]
print("登录 OK, admin id =", body["user"]["id"])

TOPICS = list(range(45, 65))

# ---- 现有 tier2 数量（避免重复导入） ----
print("\n[1] 导入前现状（每课已有进阶题数）：")
before = {}
for tid in TOPICS:
    st, qs = req("GET", f"{BASE}/api/questions?topic_id={tid}", tok=TOK)
    t2 = [q for q in qs if q["tier"] == 2]
    before[tid] = len(t2)
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
print(f"\n[2] 准备导入 {len(payload)} 题")
st, body = req("POST", BASE + "/api/questions/batch", payload, tok=TOK)
print("批量导入:", st, body)
assert st == 200, f"batch fail {st} {body}"
print(f"实际 created = {body.get('created')}")

# ---- 组卷验证：每 topic tier=2 ----
print("\n[3] 组卷验证（tier=2, custom, 单课）：")
new_ids = []
for tid in TOPICS:
    st, data = req("POST", BASE + "/api/exam/start", {
        "subject_id": 3, "topic_ids": [tid], "types": ["code"],
        "count": 50, "mode": "custom", "tier": 2
    }, tok=TOK)
    qs = data.get("questions", [])
    ids = [q["id"] for q in qs]
    new_ids.extend(ids)
    print(f"  topic {tid}: tier2 现有 {len(qs)} 题")

# ---- 反向验证：tier=1 组卷不应包含新题 ----
print("\n[4] 反向验证（tier=1 不应含新题）：")
new_id_set = set(new_ids)
leak_any = False
for tid in TOPICS:
    st, data = req("POST", BASE + "/api/exam/start", {
        "subject_id": 3, "topic_ids": [tid], "types": ["code"],
        "count": 50, "mode": "custom", "tier": 1
    }, tok=TOK)
    qs = data.get("questions", [])
    leak = [q["id"] for q in qs if q["id"] in new_id_set]
    if leak:
        leak_any = True
        print(f"  topic {tid}: 泄漏新题 {leak} !!!")
print("  tier1 泄漏检查:", "发现泄漏" if leak_any else "无泄漏(正确)")

# ---- 评分验证：提交参考解，确认 LLM 判分 ----
print("\n[5] 评分验证（提交参考解，验证 sample_input 生效 / LLM>=60）：")
record_ids = []
all_ok = True
low_scores = []
for tid in TOPICS:
    st, qs = req("GET", f"{BASE}/api/questions?topic_id={tid}", tok=TOK)
    t2 = [q for q in qs if q["tier"] == 2]
    # 取本次导入的该课 5 题（以 content 匹配本地 QUESTIONS）
    local_contents = {q["content"] for q in QUESTIONS if q["topic_id"] == tid}
    new_here = [q for q in t2 if q["content"] in local_contents]
    if not new_here:
        print(f"  topic {tid}: 未匹配到新题，跳过")
        continue
    answers = [{"question_id": q["id"], "user_answer": q["answer"]} for q in new_here]
    st2, sub = req("POST", BASE + "/api/exam/submit", {
        "subject_id": 3, "mode": "custom", "topic_ids": [tid],
        "answers": answers, "tier": 2
    }, tok=TOK)
    assert st2 == 200, f"submit fail {st2} {sub}"
    record_ids.append(sub["id"])
    line = f"  topic {tid} (record {sub['id']}, points={sub['points_earned']}): "
    for ar in sub["answer_records"]:
        sc = ar["llm_score"] or 0
        ok = sc >= 60
        all_ok = all_ok and ok
        if not ok:
            low_scores.append((tid, ar["question_id"], sc))
        line += f"[q{ar['question_id']}={sc}] "
    print(line)

# ---- 清理验证产生的答题记录 + 回滚 admin 积分 ----
print("\n[6] 清理验证记录：")
for rid in record_ids:
    st, _ = req("DELETE", f"{BASE}/api/admin/records/{rid}", tok=TOK)
print(f"  共清理 {len(record_ids)} 条验证记录")

# 评分验证会给 admin(id=3) 发放积分(exam_reward, ref_id=record.id)，
# DELETE records 不回滚积分，这里手动回滚：删流水 + 扣余额。
ADMIN_ID = 3
rids = ",".join(map(str, record_ids))
st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": f"SELECT id, delta FROM points_ledger WHERE ref_id IN ({rids}) AND reason='exam_reward' AND student_id={ADMIN_ID}", "script": False},
              tok=TOK)
rows = res.get("rows", []) if isinstance(res, dict) else []
if rows:
    total_pts = sum(r["delta"] for r in rows)
    ids = ",".join(str(r["id"]) for r in rows)
    st, _ = req("POST", BASE + "/api/admin/exec-sql",
                {"sql": f"DELETE FROM points_ledger WHERE id IN ({ids})", "script": False}, tok=TOK)
    st, _ = req("POST", BASE + "/api/admin/exec-sql",
                {"sql": f"UPDATE student_points SET balance = balance - {total_pts} WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
    print(f"  已回滚 admin 积分：删除 {len(rows)} 条流水，扣减 {total_pts} 分")
else:
    print("  未发现 admin 验证积分流水，无需回滚")

# 验证回滚结果
st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": f"SELECT balance FROM student_points WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
print("  回滚后 admin 余额:", res.get("rows") if isinstance(res, dict) else res)

print("\n=== 结果：", "全部 PASS" if (all_ok and not leak_any) else "存在异常，需检查", "===")
if low_scores:
    print("低分题目(<60):", low_scores)
