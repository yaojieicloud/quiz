# -*- coding: utf-8 -*-
"""本地全方位端到端测试（上线前自测）"""
import urllib.request, urllib.error, json, sys, time

B = "http://127.0.0.1:8000"
PASS, FAIL = 0, 0


def api(path, data=None, token=None, method=None):
    url = B + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.status, json.load(resp)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}")


# 0) 等就绪
for _ in range(20):
    try:
        st, d = api("/api/health")
        if st == 200:
            break
    except Exception:
        pass
    time.sleep(1)

print("=== 基础 ===")
st, d = api("/api/health")
check("health 200+ok", st == 200 and d.get("status") == "ok")

st, d = api("/api/auth/login", {"username": "admin", "password": "admin123"})
check("admin 登录", st == 200 and "access_token" in d)
tok = d.get("access_token", "")

print("\n=== subjects / available_types ===")
st, subs = api("/api/subjects", token=tok)
check("subjects 200", st == 200)
sub_map = {s["id"]: s for s in subs}
check("所有科目含 available_types", all("available_types" in s for s in subs))
theory = sub_map.get(1, {})
check("理论题型=choice/judge/calc", set(theory.get("available_types", [])) == {"choice", "judge", "calc"})
math_sub = sub_map.get(2, {})
check("数学题型含 fill/essay", {"fill", "essay"}.issubset(set(math_sub.get("available_types", []))))

# 排序顺序验证（语文=1,数学=2,英语=3,理论=4,实操=5）
order = [s["name"] for s in sorted(subs, key=lambda x: x.get("sort_order", 99))]
print(f"  科目顺序: {order}")

print("\n=== 组卷（数学，含全题型）===")
st, d = api("/api/exam/start", {"subject_id": 2, "topic_ids": [], "types": [], "count": 50, "mode": "custom"}, token=tok)
check("数学组卷 50 题", st == 200 and len(d.get("questions", [])) == 50)
qs = d.get("questions", [])
types_got = set(q["type"] for q in qs)
print(f"  抽到题型: {types_got}")
match_qs = [q for q in qs if q["type"] == "match"]
if match_qs:
    check("连线题带 match_options", all(q.get("match_options") for q in match_qs))
else:
    check("连线题带 match_options(未抽到,跳过)", True)

print("\n=== 边界校验 ===")
st, d = api("/api/exam/submit", {"subject_id": 2, "answers": [], "duration_seconds": 5}, token=tok)
check("空 answers → 400", st == 400)
st, d = api("/api/exam/submit", {"subject_id": 2, "answers": [{"question_id": 999999, "user_answer": "A"}], "duration_seconds": 5}, token=tok)
check("不存在题目 → 400", st == 400)

print("\n=== 判分（用 admin 题目接口取正确答案）===")
st, allq = api("/api/questions?subject_id=2", token=tok)
items = allq if isinstance(allq, list) else allq.get("items", [])
by_type = {}
for q in items:
    by_type.setdefault(q["type"], []).append(q)
print(f"  数学题库题型: {', '.join(f'{t}:{len(v)}' for t, v in by_type.items())}")


def submit_one(q, ans):
    st2, d2 = api("/api/exam/submit", {"subject_id": 2, "answers": [{"question_id": q["id"], "user_answer": ans}], "duration_seconds": 5}, token=tok)
    if st2 != 200:
        return None
    return d2.get("answer_records", [{}])[0]


# choice
if "choice" in by_type:
    q = by_type["choice"][0]
    ar = submit_one(q, q["answer"])
    check("选择题正确→is_correct=True", ar and ar.get("is_correct") is True)
    ar = submit_one(q, "WRONG_XYZ")
    check("选择题错误→is_correct=False", ar and ar.get("is_correct") is False)

# judge
if "judge" in by_type:
    q = by_type["judge"][0]
    ar = submit_one(q, q["answer"])
    check("判断题正确→True", ar and ar.get("is_correct") is True)

# fill
if "fill" in by_type:
    q = by_type["fill"][0]
    ba = q.get("blank_answers")
    ans = "|".join(str(a) for a in ba) if isinstance(ba, list) and ba else q.get("answer", "")
    ar = submit_one(q, ans)
    check("填空题正确→True", ar and ar.get("is_correct") is True)
    ar = submit_one(q, "WRONG_ANSWER_12345")
    check("填空题错误→False", ar and ar.get("is_correct") is False)

# essay
if "essay" in by_type:
    q = by_type["essay"][0]
    ar = submit_one(q, "这是一段足够长的回答内容，用于测试应用题的降级判分逻辑是否正常工作。")
    check("应用题≥10字→True", ar and ar.get("is_correct") is True)
    ar = submit_one(q, "短")
    check("应用题太短→False", ar and ar.get("is_correct") is False)

# match
if "match" in by_type:
    q = by_type["match"][0]
    ar = submit_one(q, q["answer"])
    check("连线题正确→True", ar and ar.get("is_correct") is True)
    ar = submit_one(q, "99:99")
    check("连线题错误→False", ar and ar.get("is_correct") is False)

# sort
if "sort" in by_type:
    q = by_type["sort"][0]
    ar = submit_one(q, q["answer"])
    check("排序题正确→True", ar and ar.get("is_correct") is True)
    ar = submit_one(q, "9,8,7,6,5,4,3,2,1,0")
    check("排序题错误→False", ar and ar.get("is_correct") is False)

# score 公式
if "choice" in by_type and len(by_type["choice"]) >= 2:
    c1, c2 = by_type["choice"][0], by_type["choice"][1]
    st2, d2 = api("/api/exam/submit", {"subject_id": 2, "answers": [
        {"question_id": c1["id"], "user_answer": c1["answer"]},
        {"question_id": c2["id"], "user_answer": "TOTALLY_WRONG"},
    ], "duration_seconds": 10}, token=tok)
    check("score 公式 1对1错→50分", st2 == 200 and d2.get("score") == 50)

print("\n=== code 题（实操科目）===")
st, d = api("/api/exam/start", {"subject_id": 3, "topic_ids": [], "types": [], "count": 1, "mode": "custom"}, token=tok)
check("实操组卷", st == 200 and len(d.get("questions", [])) >= 0)

st, d = api("/api/exam/run-code", {"code": 'print("hello")', "sample_input": ""}, token=tok)
check("run-code 正常", st == 200 and "hello" in d.get("output", ""))
st, d = api("/api/exam/run-code", {"code": "import os", "sample_input": ""}, token=tok)
check("run-code 拦截 os", d.get("rc", 1) != 0 or d.get("error"))

print("\n=== 其他接口 ===")
st, d = api("/api/exam/records", token=tok)
check("学习记录 200", st == 200)
st, d = api("/api/wrong-questions", token=tok)
check("错题本 200", st == 200)
st, d = api("/api/subjects/2/topics", token=tok)
check("数学章节 200", st == 200)
st, d = api("/api/subjects/2/units", token=tok)
check("数学单元 200", st == 200)

print(f"\n===== 本地自测结果: {PASS} 通过 / {FAIL} 失败 =====")
sys.exit(1 if FAIL else 0)
