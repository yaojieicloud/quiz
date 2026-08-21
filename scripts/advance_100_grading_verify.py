"""进阶题 100 道：评分验证续跑脚本（导入已完成 qid 5294-5393）。
改进：逐题提交（单请求只含 1 道题，避免多题串行 LLM 评分超时）；
先清理之前超时残留的记录并回滚积分。
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
ADMIN_ID = 3

def req(method, url, body=None, tok=None, timeout=180):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

st, body = req("POST", BASE + "/api/auth/login", {"username": "admin", "password": "admin123"})
assert st == 200, f"login failed {st} {body}"
TOK = body["access_token"]
print("登录 OK")

# ---- 步骤0：清理上次超时残留（今日 admin 记录） ----
print("\n[0] 清理今日残留验证记录：")
st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": "SELECT id FROM exam_records WHERE user_id=3 AND date(started_at)=date('now')", "script": False}, tok=TOK)
old_ids = [r["id"] for r in res.get("rows", [])]
for rid in old_ids:
    req("DELETE", f"{BASE}/api/admin/records/{rid}", tok=TOK)
if old_ids:
    rids = ",".join(map(str, old_ids))
    st, res = req("POST", BASE + "/api/admin/exec-sql",
                  {"sql": f"SELECT id, delta FROM points_ledger WHERE ref_id IN ({rids}) AND reason='exam_reward' AND student_id={ADMIN_ID}", "script": False}, tok=TOK)
    rows = res.get("rows", [])
    if rows:
        total_pts = sum(r["delta"] for r in rows)
        ids = ",".join(str(r["id"]) for r in rows)
        req("POST", BASE + "/api/admin/exec-sql", {"sql": f"DELETE FROM points_ledger WHERE id IN ({ids})", "script": False}, tok=TOK)
        req("POST", BASE + "/api/admin/exec-sql", {"sql": f"UPDATE student_points SET balance = balance - {total_pts} WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
        print(f"  清理记录 {old_ids}，回滚积分 {total_pts}")
    else:
        print(f"  清理记录 {old_ids}，无积分流水")
else:
    print("  无残留")

st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": f"SELECT balance FROM student_points WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
baseline = res["rows"][0]["balance"]
print(f"  admin 积分基线: {baseline}")

# ---- 拉取新题 qid->content 映射 ----
print("\n[1] 拉取 ECS 新题（qid>4978, tier=2）：")
st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": "SELECT id, topic_id, content FROM questions WHERE subject_id=3 AND tier=2 AND id>4978", "script": False}, tok=TOK)
ecs_questions = res["rows"]
print(f"  共 {len(ecs_questions)} 题")

# content -> 本地参考解
local_map = {q["content"]: q["answer"] for q in QUESTIONS}
missing = [q["id"] for q in ecs_questions if q["content"] not in local_map]
assert not missing, f"有 {len(missing)} 题在本地找不到参考解: {missing[:5]}"

# ---- 步骤2：逐题提交参考解验证 ----
print("\n[2] 逐题评分验证（100 题，逐题提交）：")
record_ids = []
low_scores = []
done = 0
for q in ecs_questions:
    qid = q["id"]
    tid = q["topic_id"]
    answers = [{"question_id": qid, "user_answer": local_map[q["content"]]}]
    st2, sub = req("POST", BASE + "/api/exam/submit", {
        "subject_id": 3, "mode": "custom", "topic_ids": [tid],
        "answers": answers, "tier": 2
    }, tok=TOK, timeout=180)
    if st2 != 200:
        print(f"  [ERROR] q{qid} submit {st2}: {sub}")
        continue
    record_ids.append(sub["id"])
    ar = sub["answer_records"][0]
    sc = ar["llm_score"] or 0
    done += 1
    if sc < 60:
        low_scores.append((tid, qid, sc))
        print(f"  [LOW] q{qid} topic{tid} score={sc}")
    if done % 10 == 0:
        print(f"  进度 {done}/100 ...")

print(f"\n  完成 {done}/100，低分(<60) {len(low_scores)} 题")
if low_scores:
    print("  低分明细:", low_scores)

# ---- 步骤3：清理验证记录 + 回滚积分 ----
print("\n[3] 清理验证记录：")
for rid in record_ids:
    req("DELETE", f"{BASE}/api/admin/records/{rid}", tok=TOK)
print(f"  删除 {len(record_ids)} 条")

rids = ",".join(map(str, record_ids))
st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": f"SELECT id, delta FROM points_ledger WHERE ref_id IN ({rids}) AND reason='exam_reward' AND student_id={ADMIN_ID}", "script": False}, tok=TOK)
rows = res.get("rows", [])
if rows:
    total_pts = sum(r["delta"] for r in rows)
    ids = ",".join(str(r["id"]) for r in rows)
    req("POST", BASE + "/api/admin/exec-sql", {"sql": f"DELETE FROM points_ledger WHERE id IN ({ids})", "script": False}, tok=TOK)
    req("POST", BASE + "/api/admin/exec-sql", {"sql": f"UPDATE student_points SET balance = balance - {total_pts} WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
    print(f"  回滚积分：删 {len(rows)} 条流水，扣 {total_pts} 分")

st, res = req("POST", BASE + "/api/admin/exec-sql",
              {"sql": f"SELECT balance FROM student_points WHERE student_id={ADMIN_ID}", "script": False}, tok=TOK)
final = res["rows"][0]["balance"]
print(f"  积分基线 {baseline} -> 清理后 {final}", "（一致）" if final == baseline else "（不一致！）")

print("\n=== 结果：", "全部 PASS" if (done == 100 and not low_scores and final == baseline) else "存在异常", "===")
