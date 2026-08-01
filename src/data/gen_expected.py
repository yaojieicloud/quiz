"""后置处理：为 200 道编程题补上判分所需的 expected_output / sample_input。

做法（不改动原生成器）：
1. 读 python_coding200.json；
2. 若参考代码(answer)用到 input()，从题干的「参考 …）」里解析出
   逐个输入值，拼成 sample_input（多行用 \\n 分隔）；
3. 用受限执行器实跑参考代码（喂入 sample_input），捕获 stdout 作为 expected_output；
4. 写回 JSON（覆盖原文件，新增两个字段）；
5. 校验：全部 expected_output 非空、参考代码可运行，否则报错退出。

运行：python data/gen_expected.py
"""
import os
import re
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.code_runner import run_python  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "python_coding200.json")


def derive_sample_input(content: str, answer: str) -> str:
    """从题干「参考 …）」解析出 input() 需要的输入值，拼成多行字符串。"""
    if "input(" not in answer:
        return ""
    m = re.search(r"参考(.+?)）", content or "")
    if not m:
        # 兜底：按 input() 数量给默认数值
        n = answer.count("input(")
        return "\n".join(["10"] * n) + ("\n" if n else "")
    clause = m.group(1)
    vals = []
    for part in re.split(r"[，,、\s]+", clause):
        # 取「=」之后的值（r=10 → 10；name=小明 → 小明）
        mm = re.search(r"=\s*(-?\d+\.?\d*|\S+)", part)
        if mm:
            vals.append(mm.group(1))
        else:
            # 整段即一个值（如 "12" / "小明"）
            mm2 = re.search(r"(-?\d+\.?\d*|\S+)", part)
            vals.append(mm2.group(1) if mm2 else "10")
    if not vals:
        vals = ["10"]
    return "\n".join(vals) + "\n"


def compute(answer: str, content: str):
    """返回 (sample_input, expected_output)；expected 为空表示参考代码跑不通。"""
    if "input(" not in answer:
        sample = ""
    else:
        sample = derive_sample_input(content, answer)
        # 若参考代码报 EOF（输入不够），逐步补足
        for _ in range(6):
            _, _, rc = run_python(answer, sample)
            if rc == 0:
                break
            sample = sample + "10\n"
    out, err, rc = run_python(answer, sample)
    expected = out if rc == 0 else ""
    return sample, expected


def main():
    print("读取:", JSON_PATH)
    data = json.load(open(JSON_PATH, encoding="utf-8"))
    qs = data["questions"]
    print("题目数:", len(qs))

    fail = 0
    for i, q in enumerate(qs, 1):
        ans = q.get("answer") or ""
        sample, expected = compute(ans, q.get("content", ""))
        q["sample_input"] = sample
        q["expected_output"] = expected
        if not expected.strip():
            fail += 1
            print(f"  ⚠️ [{i}] 参考代码跑不通，expected 为空：{q.get('content','')[:40]}")

    # 写回（覆盖）
    json.dump(data, open(JSON_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n已写回 {JSON_PATH}（新增 sample_input / expected_output）")
    print(f"含 input() 的题已填入 sample_input；参考代码全部跑通：{len(qs)-fail}/{len(qs)}")
    if fail:
        print(f"\n❌ 有 {fail} 道题参考代码跑不通，请检查后重跑。")
        sys.exit(1)
    print("\n✅ 全部参考代码运行通过，expected_output 已就绪。")


if __name__ == "__main__":
    main()
