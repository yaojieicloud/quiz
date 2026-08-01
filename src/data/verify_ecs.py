"""ECS 端到端验证：
1) subject 3(Python基础实操) 的 200 题是否都带 expected_output / sample_input
2) 注册测试学生 -> 单题闯关(count=1) -> 提交「参考代码(应判对)」/「改坏的代码(应判错)」/「语法错误(应判错)」
3) 验证返回 is_correct 与 run_output 合理
4) 清理测试账号
"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://106.14.99.100:8000"
REGKEY = "openschool2026"
ADMIN = ("admin", "admin123")
TEST_USER = f"__verify_{int(time.time())}"


def http(method, url, token=None, data=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    b = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=b, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            return x.status, json.loads(x.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa
        return None, str(e)


def login(u, p):
    st, res = http("POST", f"{BASE}/api/auth/login", data={"username": u, "password": p})
    if st != 200 or "access_token" not in res:
        print(f"[FAIL] 登录 {u}: {st} {res}"); return None
    return res["access_token"]


def exec_sql(tok, sql, script=False):
    return http("POST", f"{BASE}/api/admin/exec-sql", token=tok,
               data={"sql": sql, "script": script})


def main():
    atok = login(*ADMIN)
    assert atok, "admin 登录失败"

    print("\n=== 1) 题目数据完整性 ===")
    st, res = exec_sql(atok,
        "SELECT "
        "SUM(CASE WHEN expected_output IS NOT NULL AND expected_output<>'' THEN 1 ELSE 0 END) AS with_exp,"
        "SUM(CASE WHEN sample_input IS NOT NULL AND sample_input<>'' THEN 1 ELSE 0 END) AS with_in,"
        "COUNT(*) AS total "
        "FROM questions WHERE subject_id=3 AND type='code'")
    r = res["rows"][0]
    print(f"  subject3 code 题共 {r['total']} | 有 expected_output: {r['with_exp']} | 有 sample_input: {r['with_in']}")
    assert int(r["total"]) == 173 and int(r["with_exp"]) == 173, "题目数/expected_output 不匹配"
    print("  ✅ 173 道唯一 code 题均带 expected_output")

    print("\n=== 2) 注册测试学生并单题闯关 ===")
    st, res = http("POST", f"{BASE}/api/auth/register?regkey={REGKEY}",
                    data={"username": TEST_USER, "nickname": "验证生", "password": "test123456", "role": "student"})
    assert st == 200 and "access_token" in res, f"注册失败 {st} {res}"
    stok = res["access_token"]
    uid = res["user"]["id"]
    print(f"  测试账号 {TEST_USER} (uid={uid}) 注册成功")

    # 取 subject3 全部 code 题的 id->answer 映射（用于拿到「参考答案」）
    st, qlist = http("GET", f"{BASE}/api/questions?subject_id=3&type=code", token=stok)
    ans_map = {q["id"]: q["answer"] for q in qlist}
    print(f"  取到 {len(ans_map)} 道 code 题的参考答案")

    def start_one():
        st, res = http("POST", f"{BASE}/api/exam/start", token=stok,
                         data={"subject_id": 3, "topic_ids": [], "types": [], "count": 1, "mode": "custom"})
        assert st == 200 and len(res["questions"]) == 1, f"start 异常 {st} {res}"
        q = res["questions"][0]
        assert q["type"] == "code", "返回的题不是 code"
        assert q.get("explanation"), "code 题未下发 指导思路(explanation)"
        return res["exam_record_id"], q

    # --- 正确提交：用参考答案 ---
    print("\n=== 3) 提交「参考答案」应判对 ===")
    exid, q = start_one()
    ans = ans_map[q["id"]]
    st, rec = http("POST", f"{BASE}/api/exam/{exid}/submit", token=stok,
                       data={"answers": [{"question_id": q["id"], "user_answer": ans}]})
    ar = rec["answer_records"][0]
    print(f"  question_id={q['id']} is_correct={ar['is_correct']}")
    print(f"  run_output: {ar['run_output'][:120]!r}")
    assert ar["is_correct"] is True, "参考答案竟然判错！"
    assert "✅" in ar["run_output"], "run_output 缺少通过标记"
    print("  ✅ 参考答案判对，run_output 正确")

    # --- 错误提交：把参考代码改坏（追加语法错误）---
    print("\n=== 4) 提交「改坏的代码」应判错 ===")
    exid, q = start_one()
    ans = ans_map[q["id"]]
    broken = ans + "\nthis is a syntax error @@@\n"
    st, rec = http("POST", f"{BASE}/api/exam/{exid}/submit", token=stok,
                       data={"answers": [{"question_id": q["id"], "user_answer": broken}]})
    ar = rec["answer_records"][0]
    print(f"  question_id={q['id']} is_correct={ar['is_correct']}")
    print(f"  run_output: {ar['run_output'][:120]!r}")
    assert ar["is_correct"] is False, "改坏的代码竟判对！"
    assert ("❌" in ar["run_output"] or "错误" in ar["run_output"]), "run_output 缺少错误说明"
    print("  ✅ 改坏代码判错，run_output 给出说明")

    # --- 语法错误提交 ---
    print("\n=== 5) 提交「语法错误代码」应判错且给出报错 ===")
    exid, q = start_one()
    bad = "print(1"  # 未闭合括号
    st, rec = http("POST", f"{BASE}/api/exam/{exid}/submit", token=stok,
                       data={"answers": [{"question_id": q["id"], "user_answer": bad}]})
    ar = rec["answer_records"][0]
    print(f"  question_id={q['id']} is_correct={ar['is_correct']}")
    print(f"  run_output: {ar['run_output'][:120]!r}")
    assert ar["is_correct"] is False and "出错" in ar["run_output"], "语法错误未正确判分"
    print("  ✅ 语法错误代码判错并给出运行报错")

    print("\n=== 6) 清理测试账号 ===")
    st, res = exec_sql(atok,
        f"DELETE FROM answer_records WHERE exam_record_id IN (SELECT id FROM exam_records WHERE user_id={uid});"
        f"DELETE FROM exam_records WHERE user_id={uid};"
        f"DELETE FROM wrong_questions WHERE user_id={uid};"
        f"DELETE FROM users WHERE id={uid};")
    print(f"  清理结果: {st} {res}")

    print("\n🎉 全部端到端验证通过！")


if __name__ == "__main__":
    main()
