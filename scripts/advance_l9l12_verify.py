"""L9-L12 (topic 53-56) 进阶题参考解本地验证：跑通每题 answer（含 sample_input）。"""
import subprocess, sys, os, tempfile

QUESTIONS = [
    # ===================== L9 / topic 53 列表与列表推导式 =====================
    {
        "topic_id": 53,
        "title": "L9-53-A 成绩分析器（列表推导式）",
        "content": (
            "成绩分析器。第一行输入一个整数 n（0<n<=100），随后 n 行，每行格式为「姓名 分数」"
            "（姓名不含空格，分数为整数）。\n"
            "请完成：\n"
            "1. 用列表推导式，将每行解析为 (姓名, 分数) 的元组，存入列表 records；\n"
            "2. 计算平均分（保留 1 位小数）；\n"
            "3. 找出分数最高的学生（若有并列，取第一个）；\n"
            "4. 用列表推导式统计及格（分数 >= 60）的人数，并列出不及格学生的姓名；\n"
            "5. 将成绩从高到低排序，输出前三名「姓名:分数」。\n"
            "按以下格式输出：\n"
            "平均分：xx.x\n最高分：姓名(分数)\n及格人数：x\n不及格：姓名1 姓名2（无则输出『无』）\n前三名：姓名1:分,姓名2:分,姓名3:分"
        ),
        "answer": (
            "n = int(input())\n"
            "raw = [input() for _ in range(n)]\n"
            "# 列表推导式：解析每行 -> (姓名, 分数)\n"
            "records = [(p[0], int(p[1])) for p in (line.split() for line in raw)]\n\n"
            "# 平均分（保留1位）\n"
            "total = sum(s for _, s in records)\n"
            "avg = total / len(records)\n\n"
            "# 最高分（取首个并列）\n"
            "best = records[0]\n"
            "for name, score in records:\n"
            "    if score > best[1]:\n"
            "        best = (name, score)\n\n"
            "# 及格 / 不及格（列表推导式过滤）\n"
            "passed = [r for r in records if r[1] >= 60]\n"
            "failed = [r[0] for r in records if r[1] < 60]\n\n"
            "# 成绩降序排序\n"
            "ranked = sorted(records, key=lambda x: x[1], reverse=True)\n\n"
            "print(f\"平均分：{avg:.1f}\")\n"
            "print(f\"最高分：{best[0]}({best[1]})\")\n"
            "print(f\"及格人数：{len(passed)}\")\n"
            "print(\"不及格：\" + (\" \".join(failed) if failed else \"无\"))\n"
            "print(\"前三名：\" + \"，\".join(f\"{n}:{s}\" for n, s in ranked[:3]))\n"
        ),
        "explanation": (
            "思路：① 先读 n，再用 [input() for _ in range(n)] 一次读入所有行；"
            "② 用嵌套生成器 + 列表推导式把每行 split 后转成 (姓名, 分数) 元组；"
            "③ 平均分用 sum 配合生成器表达式；④ 最高分先取首元素再遍历比较更新；"
            "⑤ 及格/不及格人数与名单都用列表推导式按条件过滤；"
            "⑥ 排序用 sorted(..., key=lambda, reverse=True)，取切片 [:3] 得前三名。"
        ),
        "sample_input": "5\nAlice 88\nBob 45\nCindy 92\nDavid 60\nEve 73\n",
    },
    {
        "topic_id": 53,
        "title": "L9-53-B 数字流水线（多重列表推导式）",
        "content": (
            "数字流水线。输入一行，包含若干个空格分隔的整数（数量不定，不超过 50 个）。\n"
            "请完成：\n"
            "1. 用列表推导式将输入转为整数列表 nums；\n"
            "2. 用列表推导式生成 doubled = [x*2 for x in nums]；\n"
            "3. 用列表推导式过滤出 doubled 中的偶数，得到 evens（并去重排序）；\n"
            "4. 计算 nums 中正数之和、doubled 的平均值（保留2位小数）、负数个数、最大值；\n"
            "5. 输出：原始列表、doubled、evens，以及正数之和、平均值、负数个数、最大值。"
        ),
        "answer": (
            "line = input().strip()\n"
            "# 列表推导式：转整数\n"
            "nums = [int(x) for x in line.split()]\n"
            "# 列表推导式：每个数乘 2\n"
            "doubled = [x * 2 for x in nums]\n"
            "# 列表推导式：过滤偶数并去重排序\n"
            "evens = sorted(set(x for x in doubled if x % 2 == 0))\n"
            "# 正数之和（列表推导式）\n"
            "pos_sum = sum(x for x in nums if x > 0)\n"
            "# doubled 平均值\n"
            "avg = sum(doubled) / len(doubled) if doubled else 0\n"
            "# 负数个数 / 最大值\n"
            "neg_cnt = len([x for x in nums if x < 0])\n"
            "mx = max(nums) if nums else 0\n"
            "print(\"原始：\", nums)\n"
            "print(\"乘2：\", doubled)\n"
            "print(\"偶数：\", evens)\n"
            "print(f\"正数之和：{pos_sum}\")\n"
            "print(f\"平均值：{avg:.2f}\")\n"
            "print(f\"负数个数：{neg_cnt}\")\n"
            "print(f\"最大值：{mx}\")\n"
        ),
        "explanation": (
            "思路：① nums 用列表推导式一行完成 str->int；② doubled 同样是列表推导式；"
            "③ evens 用生成器表达式过滤偶数，再 set 去重、sorted 排序；"
            "④ 正数之和、负数个数都用带条件的列表推导式 + sum/len；"
            "⑤ max 注意空列表保护；所有需求都能用列表推导式组合完成，体现本课重点。"
        ),
        "sample_input": "3 -2 5 8 4 10 -7 6\n",
    },
    # ===================== L10 / topic 54 元组字典 =====================
    {
        "topic_id": 54,
        "title": "L10-54-A 词频分析器（字典统计）",
        "content": (
            "词频分析器。输入一行英文句子（单词由空格分隔，可能含大小写混合）。\n"
            "请完成：\n"
            "1. 将句子转为小写并按空格切分为单词列表（用列表推导式去除空串）；\n"
            "2. 用字典统计每个单词出现的次数；\n"
            "3. 按出现次数从高到低排序（次数相同按单词字典序）；\n"
            "4. 输出不同单词总数、总词数、出现最多的前 3 个单词及其次数、以及仅出现一次的单词列表。"
        ),
        "answer": (
            "sentence = input().strip().lower()\n"
            "# 列表推导式：切分并去空\n"
            "words = [w for w in sentence.split() if w]\n"
            "# 字典统计词频\n"
            "freq = {}\n"
            "for w in words:\n"
            "    freq[w] = freq.get(w, 0) + 1\n"
            "# 按 (次数降序, 单词升序) 排序\n"
            "ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))\n"
            "top3 = ranked[:3]\n"
            "total_words = len(words)\n"
            "once = [w for w, c in freq.items() if c == 1]\n"
            "print(\"不同单词总数：\", len(freq))\n"
            "print(\"总词数：\", total_words)\n"
            "print(\"词频前三：\")\n"
            "for word, cnt in top3:\n"
            "    print(f\"  {word}: {cnt}\")\n"
            "print(\"仅出现一次的单词：\", once)\n"
        ),
        "explanation": (
            "思路：① 小写化后用 split 切词，列表推导式顺手过滤空串；"
            "② 字典计数用 freq.get(w, 0) + 1 的惯用法；"
            "③ 排序 key 用 lambda 返回元组 (-次数, 单词)，实现『次数降序、同次字典序』；"
            "④ sorted 返回 (单词, 次数) 元组列表，切片取前三；"
            "⑤ 仅出现一次的单词同样用列表推导式按条件过滤 freq.items()。"
        ),
        "sample_input": "Apple apple Banana apple cherry Banana cherry apple\n",
    },
    {
        "topic_id": 54,
        "title": "L10-54-B 库存核算（字典 + 循环累加）",
        "content": (
            "库存核算。连续输入若干行，每行格式为「商品名 单价 数量」（单价浮点、数量整数），"
            "直到输入 'end' 为止。\n"
            "请完成：\n"
            "1. 用字典存储每个商品的 (单价, 数量)；\n"
            "2. 用字典推导式计算每个商品的价值 = 单价 * 数量；\n"
            "3. 计算所有商品总价值（保留2位小数）；\n"
            "4. 找出总价值最高的商品；\n"
            "5. 输出每个商品明细（商品名 单价 数量 价值）与合计、最高价值商品。"
        ),
        "answer": (
            "inventory = {}\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    name, price, qty = line.split()\n"
            "    inventory[name] = (float(price), int(qty))\n\n"
            "# 字典推导式：每个商品价值\n"
            "values = {name: price * qty for name, (price, qty) in inventory.items()}\n\n"
            "# 总价值\n"
            "total_value = sum(values.values())\n"
            "# 价值最高的商品\n"
            "best_name = max(values, key=values.get)\n"
            "best_value = values[best_name]\n\n"
            "print(\"商品明细：\")\n"
            "for name, (price, qty) in inventory.items():\n"
            "    print(f\"  {name}: 单价{price} 数量{qty} 价值{values[name]:.2f}\")\n"
            "print(f\"总价值：{total_value:.2f}\")\n"
            "print(f\"价值最高：{best_name} ({best_value:.2f})\")\n"
        ),
        "explanation": (
            "思路：① 用 while + 判断 'end' 实现不定行输入，字典以商品名为键存 (单价,数量) 元组；"
            "② 字典推导式 {k: 单价*数量 for ...} 一次性算出各商品价值；"
            "③ 总价值用 sum(values.values())；"
            "④ 找最大值用 max(字典, key=字典.get) 拿到对应键；"
            "⑤ 遍历原字典输出明细，体现字典与循环、元组 unpacking 的综合运用。"
        ),
        "sample_input": "apple 3.5 10\nbanana 2.0 5\nmilk 8.0 2\nbread 5.0 4\nend\n",
    },
    # ===================== L11 / topic 55 类型转换 =====================
    {
        "topic_id": 55,
        "title": "L11-55-A 温度转换台（float/try-except）",
        "content": (
            "温度转换台。每行输入格式为「C 25」或「F 77」，表示摄氏或华氏温度。\n"
            "C 转 F：F = C*9/5 + 32；F 转 C：C = (F-32)*5/9。\n"
            "输入 'q' 结束。对每个有效输入，输出转换后的温度（保留1位小数），并累计转换次数。\n"
            "若格式无法识别（如缺少数值、单位非 C/F、数值非数字），输出『格式错误』并跳过。"
        ),
        "answer": (
            "count = 0\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == \"q\":\n"
            "        break\n"
            "    parts = line.split()\n"
            "    if len(parts) != 2:\n"
            "        print(\"格式错误\")\n"
            "        continue\n"
            "    unit = parts[0].upper()\n"
            "    try:\n"
            "        val = float(parts[1])\n"
            "    except ValueError:\n"
            "        print(\"格式错误\")\n"
            "        continue\n"
            "    if unit == \"C\":\n"
            "        result = val * 9 / 5 + 32\n"
            "        print(f\"{val}°C = {result:.1f}°F\")\n"
            "    elif unit == \"F\":\n"
            "        result = (val - 32) * 5 / 9\n"
            "        print(f\"{val}°F = {result:.1f}°C\")\n"
            "    else:\n"
            "        print(\"格式错误\")\n"
            "        continue\n"
            "    count += 1\n"
            "print(f\"共完成 {count} 次转换\")\n"
        ),
        "explanation": (
            "思路：① 用 while True 循环直到输入 'q'；"
            "② 拆分后先校验长度与单位，再对数值用 float() 转换并 try/except 捕获非数字；"
            "③ 温度公式就是简单的算术与类型转换（字符串->float）；"
            "④ 用 if/elif 分流 C/F，非法单位输出『格式错误』；"
            "⑤ count 只在成功转换时自增，最后汇报。综合了输入、类型转换、异常处理、格式化输出。"
        ),
        "sample_input": "C 25\nF 77\nX 10\nC abc\nq\n",
    },
    {
        "topic_id": 55,
        "title": "L11-55-B 混合数据清洗（int/float/str 转换）",
        "content": (
            "混合数据清洗。输入一行空格分隔的若干 token（可能是整数、小数或普通文本）。\n"
            "请完成：\n"
            "1. 用类型转换尝试把每个 token 转为数字：能转成 int 的转 int，能转成 float 的转 float，"
            "都不能的保留原字符串；\n"
            "2. 分别统计数字个数与非数字个数；\n"
            "3. 计算所有数字之和（保留2位小数）；\n"
            "4. 输出：清洗后的列表、数字个数、非数字个数、数字之和。"
        ),
        "answer": (
            "line = input().strip()\n"
            "tokens = line.split()\n"
            "cleaned = []\n"
            "numbers = []\n"
            "for t in tokens:\n"
            "    try:\n"
            "        num = int(t)\n"
            "    except ValueError:\n"
            "        try:\n"
            "            num = float(t)\n"
            "        except ValueError:\n"
            "            num = t\n"
            "    if isinstance(num, (int, float)):\n"
            "        numbers.append(num)\n"
            "        cleaned.append(num)\n"
            "    else:\n"
            "        cleaned.append(t)\n\n"
            "num_cnt = len(numbers)\n"
            "text_cnt = len(cleaned) - num_cnt\n"
            "total = sum(numbers)\n"
            "print(\"清洗结果：\", cleaned)\n"
            "print(f\"数字个数：{num_cnt}\")\n"
            "print(f\"非数字个数：{text_cnt}\")\n"
            "print(f\"数字之和：{total:.2f}\")\n"
        ),
        "explanation": (
            "思路：① 先尝试 int(t)，失败再尝试 float(t)，都失败则保留原字符串——这就是『逐级类型转换』；"
            "② 用 isinstance(num, (int, float)) 判断是否为数字，分别收集；"
            "③ numbers 列表专门存数字用于求和；cleaned 保留混合结果；"
            "④ 数字个数=len(numbers)，非数字个数=总长-数字个数；"
            "⑤ 体现 int/float/str 三种类型之间转换与判别的综合运用。"
        ),
        "sample_input": "10 3.14 hello 20 world 5.5 100 python 7\n",
    },
    # ===================== L12 / topic 56 深浅拷贝/可变不可变 =====================
    {
        "topic_id": 56,
        "title": "L12-56-A 深浅拷贝实验室（copy 模块）",
        "content": (
            "深浅拷贝实验室。现有原始矩阵（二维列表）：\n"
            "matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n"
            "请完成：\n"
            "1. 创建 matrix 的浅拷贝 sh（用 copy.copy）；\n"
            "2. 创建 matrix 的深拷贝 dp（用 copy.deepcopy）；\n"
            "3. 修改原矩阵 matrix[0][0] = 999；\n"
            "4. 观察并输出：修改后原矩阵、浅拷贝、深拷贝各自的第一行，说明浅拷贝受影响而深拷贝不受影响；\n"
            "5. 再对原矩阵追加一行 [10,11,12]，输出三者行数，说明浅/深拷贝都不受 append 影响"
            "（它们是独立的顶层对象）。\n要求使用 copy 模块，并通过打印对比展示结论。"
        ),
        "answer": (
            "import copy\n"
            "matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n"
            "# 浅拷贝\n"
            "sh = copy.copy(matrix)\n"
            "# 深拷贝\n"
            "dp = copy.deepcopy(matrix)\n\n"
            "# 修改原矩阵内部元素\n"
            "matrix[0][0] = 999\n"
            "print(\"修改内部元素后：\")\n"
            "print(\"原矩阵首行:\", matrix[0])\n"
            "print(\"浅拷贝首行:\", sh[0])      # 受影响\n"
            "print(\"深拷贝首行:\", dp[0])      # 不受影响\n\n"
            "# 对原矩阵顶层追加一行\n"
            "matrix.append([10, 11, 12])\n"
            "print(\"\\n追加一行后：\")\n"
            "print(\"原矩阵行数:\", len(matrix))\n"
            "print(\"浅拷贝行数:\", len(sh))\n"
            "print(\"深拷贝行数:\", len(dp))\n"
            "print(\"\\n结论：浅拷贝共享内部子对象，深拷贝完全独立；但三者顶层对象独立，append 互不影响。\")\n"
        ),
        "explanation": (
            "思路：① import copy 后用 copy.copy 做浅拷贝、copy.deepcopy 做深拷贝；"
            "② 浅拷贝只复制顶层列表，内部子列表与原矩阵共享引用——所以改 matrix[0][0] 会殃及 sh；"
            "③ 深拷贝递归复制所有层级，dp 完全独立，不受任何改动影响；"
            "④ append 是在顶层列表上加元素，浅/深拷贝各自的顶层对象独立，因此行数不变；"
            "⑤ 通过三组打印对比，直观展示『可变对象 + 拷贝层级』的区别。"
        ),
        "sample_input": None,  # 纯 print 题，无 input
    },
    {
        "topic_id": 56,
        "title": "L12-56-B 分组调度（列表拷贝 vs 赋值）",
        "content": (
            "分组调度。第一行输入整数 n，第二行输入 n 个姓名（空格分隔）。\n"
            "请完成：\n"
            "1. 将姓名存入列表 original（直接由输入构建，最多取前 n 个）；\n"
            "2. 创建 original 的浅拷贝 group_all = original.copy()；\n"
            "3. 从 original 中移除前 k 个姓名（k = n // 2），放入 group_b；\n"
            "4. 输出 original（剩余）、group_b、group_all，并验证 group_all 不受 original 变化影响；\n"
            "5. 再演示：令 alias = original（直接赋值），修改 alias 也会改变 original，输出印证『赋值不是拷贝』。"
        ),
        "answer": (
            "n = int(input())\n"
            "names = input().split()\n"
            "original = names[:n] if len(names) > n else names\n"
            "# 浅拷贝（独立顶层对象）\n"
            "group_all = original.copy()\n"
            "k = len(original) // 2\n"
            "group_b = []\n"
            "for _ in range(k):\n"
            "    group_b.append(original.pop(0))\n"
            "print(\"original 剩余：\", original)\n"
            "print(\"group_b：\", group_b)\n"
            "print(\"group_all（拷贝，不变）：\", group_all)\n\n"
            "# 演示直接赋值不是拷贝\n"
            "alias = original\n"
            "alias.append(\"测试\")\n"
            "print(\"alias 追加后 original：\", original)\n"
            "print(\"结论：alias = original 是引用别名，改 alias 即改 original；.copy() 才是独立副本。\")\n"
        ),
        "explanation": (
            "思路：① 用 names[:n] 安全截取前 n 个姓名；"
            "② .copy() 创建顶层独立的浅拷贝，所以对 original 做 pop 不影响 group_all；"
            "③ k = n // 2 决定分组大小，pop(0) 从头部取出放入 group_b；"
            "④ 关键对比：alias = original 只是让两个变量指向『同一个列表对象』，"
            "因此对 alias 的 append 会同步反映到 original；而 .copy() 才是真正的副本；"
            "⑤ 本题综合展示『赋值(引用) vs 拷贝(副本)』这一可变对象核心概念。"
        ),
        "sample_input": "6\nAlice Bob Cindy David Eve Frank\n",
    },
]

if __name__ == "__main__":
    ok = 0
    for q in QUESTIONS:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(q["answer"])
            path = f.name
        try:
            si = q["sample_input"]
            res = subprocess.run([sys.executable, path], input=si,
                                 capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                ok += 1
                print(f"[OK]   {q['title']}")
                out = res.stdout.strip()
                print("       out:", out.replace("\n", " | ")[:160])
            else:
                print(f"[FAIL] {q['title']}")
                print("       STDERR:", res.stderr.strip()[:400])
        finally:
            os.unlink(path)
    print(f"\n本地验证通过 {ok}/{len(QUESTIONS)}")
