# -*- coding: utf-8 -*-
"""修复 c3b_u7u8 分片文件：JSON 字符串值内部的未转义英文直引号 -> 中文引号
然后合并 part1+part2 为 c3b_u7u8.json，并清理多余分片文件。
"""
import json
import io
import os

D = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese"
CLOSERS = set(",:]}")


def repair(s: str) -> str:
    out = []
    in_str = False
    n = len(s)
    open_q = True  # 中文引号开合交替
    for i, ch in enumerate(s):
        if ch == '"':
            if not in_str:
                in_str = True
                out.append(ch)
                continue
            # in_str: 判断是合法收尾引号还是内部脏引号
            j = i + 1
            while j < n and s[j] in " \t\r\n":
                j += 1
            if j < n and s[j] in CLOSERS:
                in_str = False
                out.append(ch)
                open_q = True
            else:
                out.append("“" if open_q else "”")
                open_q = not open_q
        else:
            if ch == "\\":
                out.append(ch)
            else:
                out.append(ch)
    return "".join(out)


total = []
for f in ["c3b_u7u8_part1.json", "c3b_u7u8_part2.json"]:
    p = os.path.join(D, f)
    s = io.open(p, encoding="utf-8").read()
    fixed = repair(s)
    data = json.loads(fixed)  # 失败会抛异常
    print(f, "->", len(data), "条 修复并解析成功")
    total.extend(data)

out_path = os.path.join(D, "c3b_u7u8.json")
io.open(out_path, "w", encoding="utf-8").write(json.dumps(total, ensure_ascii=False, indent=2))
print("合并写入 c3b_u7u8.json:", len(total), "条")

# 清理分片文件
for f in ["c3b_u7u8_part1.json", "c3b_u7u8_part2.json", "c3b_u5u6_part1.json", "c3b_u5u6_part2.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        os.remove(p)
        print("已删除分片:", f)
