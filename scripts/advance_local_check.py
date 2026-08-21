"""进阶题参考解本地沙箱验证器（与生产判分沙箱同源）。

用法: python scripts/advance_local_check.py <模块名> [<模块名> ...]
例:   python scripts/advance_local_check.py advance_b1_l1l4_verify

对每个模块的 QUESTIONS 逐题:
1. 用 src/core/code_runner.run_python 实跑参考解(answer)，注入 sample_input；
2. 校验: 返回码 0、无 stderr、有输出；
3. 静态校验: 用到 input() 必须填 sample_input；content/answer/explanation 非空；
4. 汇总 PASS/FAIL。
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from core.code_runner import run_python  # noqa: E402  生产同源沙箱


def check_module(mod_name: str) -> bool:
    mod = __import__(mod_name)
    qs = getattr(mod, "QUESTIONS")
    print(f"\n===== 模块 {mod_name}: {len(qs)} 题 =====")
    ok_cnt = 0
    fails = []
    for i, q in enumerate(qs, 1):
        title = q.get("title", f"#{i}")
        problems = []
        # 静态检查
        for field in ("content", "answer", "explanation"):
            if not (q.get(field) or "").strip():
                problems.append(f"字段 {field} 为空")
        if "input(" in q.get("answer", "") and not (q.get("sample_input") or ""):
            problems.append("参考解含 input() 但 sample_input 为空（评分沙箱将 EOFError）")
        if not problems:
            out, err, rc = run_python(q["answer"], q.get("sample_input") or "", timeout=6.0)
            if rc != 0:
                problems.append(f"运行失败 rc={rc}: {err.strip()[:160]}")
            elif err.strip():
                problems.append(f"stderr 非空: {err.strip()[:160]}")
            elif not out.strip():
                problems.append("运行无任何输出")
        if problems:
            fails.append((title, problems))
            print(f"  [FAIL] topic{q.get('topic_id')} {title}")
            for p in problems:
                print(f"         - {p}")
        else:
            ok_cnt += 1
            first = out.strip().splitlines()[0][:50]
            print(f"  [PASS] topic{q.get('topic_id')} {title} | 首行: {first}")
    print(f"  小计: {ok_cnt}/{len(qs)} 通过")
    return not fails


def main():
    mods = sys.argv[1:] or ["advance_b1_l1l4_verify"]
    all_ok = True
    for m in mods:
        all_ok = check_module(m) and all_ok
    print("\n===== 总结:", "全部 PASS" if all_ok else "存在 FAIL", "=====")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
