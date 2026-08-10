#!/usr/bin/env python3
# 连线题自动化语义校验：对每道活跃连线题，将左侧可执行的 Python 表达式/代码
# 实际运行得到真实右侧值，与答案指向的右侧选项比对，抓出语义错误。
import sqlite3, json, io, contextlib, re

DB = "quiz.db"

def norm(s):
    return (s or "").replace(" ", "").replace("　", "").replace("\u3000", "").strip()

def eval_left(left):
    """返回 ('VAL', repr) | ('OUT', stdout) | ('EXC', exc_name) | ('SKIP', reason)"""
    left = (left or "").strip()
    if not left:
        return ("SKIP", "empty")
    # 含 input() 这类交互/阻塞调用：跳过
    if "input(" in left:
        return ("SKIP", "has input()")
    # 多语句 / 含赋值 / 含换行 / 含 def / 含 print -> exec 取 stdout
    multi = ("\n" in left) or (";" in left) or ("=" in left) or left.startswith("def ") or ("print(" in left) or left.startswith("for ") or left.startswith("while ")
    ns = {}
    if multi:
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(left, ns)
            out = buf.getvalue().strip()
            return ("OUT", out) if out != "" else ("VAL", "None")
        except Exception as e:
            return ("EXC", type(e).__name__)
    else:
        try:
            val = eval(left, ns)
            return ("VAL", repr(val))
        except Exception as e:
            return ("EXC", type(e).__name__)

def match(computed, right):
    """computed: ('VAL'/'OUT'/'EXC', text); right: str -> (ok, detail)
    ok=True 匹配; ok=False 运行成功但值不符(真实疑似错误); ok=None 无法自动判定(跳过)
    """
    kind, text = computed
    nr = norm(right)
    if kind == "SKIP":
        return (None, "skip")
    if kind == "EXC":
        # 非代码题（词汇/概念连线）运行抛异常，无法自动验证，跳过
        return (None, "skip")
    # VAL / OUT
    nt = norm(text)
    if nt == nr:
        return (True, f"={text}")
    if nr in nt or nt in nr:
        return (True, f"~{text}")
    # 排除 repr 包装差异：如右侧 '<class 'str'>' 与 str(type(...))
    if kind == "VAL" and nr.replace("'", "") == nt.replace("'", ""):
        return (True, f"={text}")
    return (False, f"got={text}")

def main():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; cur = con.cursor()
    cur.execute("""SELECT q.id, q.content, q.options, q.match_options, q.answer
                   FROM questions q WHERE q.type='match'
                   AND (q.deprecated IS NULL OR q.deprecated=0)""")
    rows = cur.fetchall()
    report = []        # 结构异常
    strong = []        # 强信号：真实值其实匹配了另一个右侧选项（张冠李戴）
    weak = []          # 弱信号：值不符但未匹配其它选项（多为含义类题）
    unknown = 0
    checked = 0
    for r in rows:
        L = json.loads(r['options']) or []
        M = json.loads(r['match_options']) or []
        if len(L) != len(M) or len(L) != len(set(L)) or len(M) != len(set(M)):
            report.append((r['id'], "结构非双射/重复", (len(L), len(M))))
            continue
        pairs = [p.split(":") for p in r['answer'].split(",") if ":" in p]
        for li, ri in pairs:
            li, ri = int(li), int(ri)
            if not (0 <= li < len(L) and 0 <= ri < len(M)):
                report.append((r['id'], "索引越界", r['answer']))
                continue
            comp = eval_left(L[li])
            if comp[0] in ("SKIP", "EXC"):
                unknown += 1
                continue
            checked += 1
            kind, text = comp
            nt = norm(text); nr = norm(M[ri])
            correct = (nt == nr) or (nr in nt) or (nt in nr) or (kind == "VAL" and nr.replace("'", "") == nt.replace("'", ""))
            if correct:
                continue
            # 是否真实值其实匹配了另一个右侧选项 -> 强信号（答案错位）
            matched_other = [k for k in range(len(M)) if k != ri and (norm(M[k]) == nt or nt in norm(M[k]) or norm(M[k]) in nt)]
            entry = {"id": r['id'], "content": r['content'], "left": L[li],
                     "expected_right": M[ri], "computed": comp,
                     "all_L": L, "all_R": M, "answer": r['answer']}
            if matched_other:
                entry["match_other"] = [M[k] for k in matched_other]
                strong.append(entry)
            else:
                weak.append(entry)
    con.close()
    print(f"活跃连线题: {len(rows)}")
    print(f"结构异常: {len(report)}")
    for x in report[:50]:
        print("  [结构]", x)
    print(f"自动语义检查(可运行出值): {checked} 处 | 跳过(非代码/含义类): {unknown}")
    print(f"【强信号·疑似答案错位】 {len(strong)}")
    print(f"【弱信号·待人工判】 {len(weak)}")
    with open("match_strong_findings.json", "w", encoding="utf-8") as f:
        json.dump(strong, f, ensure_ascii=False, indent=1)
    with open("match_weak_findings.json", "w", encoding="utf-8") as f:
        json.dump(weak, f, ensure_ascii=False, indent=1)
    for s in strong:
        print(f"  [强] Q{s['id']} | {s['left']} -> 答案='{s['expected_right']}' | 实际={s['computed'][1]} | 应连={s.get('match_other')}")

if __name__ == "__main__":
    main()
