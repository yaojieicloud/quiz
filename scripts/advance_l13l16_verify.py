"""L13-L16 (topic 57-60) 进阶题参考解本地验证：跑通每题 answer（含 sample_input）。"""
import subprocess, sys, os, tempfile

QUESTIONS = [
    # ===================== L13 / topic 57 函数,return返回值与形参实参 =====================
    {
        "topic_id": 57,
        "title": "L13-57-A 成绩报告函数（return 字典）",
        "content": (
            "成绩报告函数。请定义函数 `grade_report(records)`，其中 `records` 是若干 (姓名, 分数) "
            "元组组成的列表。函数必须返回一个字典，包含：\n"
            "- 'avg'：平均分（保留 1 位小数）\n"
            "- 'top_name'：最高分学生姓名（并列取第一个）\n"
            "- 'pass_cnt'：及格人数（分数 >= 60）\n"
            "- 'total'：总人数\n"
            "主程序：第一行输入整数 n，随后 n 行每行『姓名 分数』，构建 records 后调用 grade_report "
            "并输出：\n平均分：x.x\n最高分：姓名\n及格人数：x / 总人数 x"
        ),
        "answer": (
            "def grade_report(records):\n"
            "    total = len(records)\n"
            "    scores = [s for _, s in records]\n"
            "    avg = sum(scores) / total if total else 0.0\n"
            "    top_name, top_score = records[0]\n"
            "    for name, score in records:\n"
            "        if score > top_score:\n"
            "            top_score = score\n"
            "            top_name = name\n"
            "    pass_cnt = len([r for r in records if r[1] >= 60])\n"
            "    return {\n"
            "        'avg': round(avg, 1),\n"
            "        'top_name': top_name,\n"
            "        'pass_cnt': pass_cnt,\n"
            "        'total': total,\n"
            "    }\n\n"
            "n = int(input())\n"
            "records = []\n"
            "for _ in range(n):\n"
            "    name, score = input().split()\n"
            "    records.append((name, int(score)))\n\n"
            "rep = grade_report(records)\n"
            "print(f\"平均分：{rep['avg']}\")\n"
            "print(f\"最高分：{rep['top_name']}\")\n"
            "print(f\"及格人数：{rep['pass_cnt']} / 总人数 {rep['total']}\")\n"
        ),
        "explanation": (
            "思路：① 函数负责核心计算并以字典一次性返回多个结果（体现 return 多值聚合）；"
            "② 平均用生成器表达式 sum(scores)/total，注意空列表保护；"
            "③ 最高分先取首元素再遍历比较更新，并列取首个；"
            "④ 及格人数用列表推导式按条件过滤统计；"
            "⑤ 主程序只负责读入与打印，计算全交给 grade_report，体现『形参传入、return 传出』的函数职责分离。"
        ),
        "sample_input": "4\nAlice 80\nBob 50\nCindy 90\nDavid 60\n",
    },
    {
        "topic_id": 57,
        "title": "L13-57-B 四则计算器（多返回值元组）",
        "content": (
            "四则计算器函数。请定义函数 `calc(a, b)`，接收两个数字，以**元组**形式返回四则结果 "
            "`(和, 差, 积, 商)`：\n- 和 = a + b；差 = a - b；积 = a * b；"
            "商 = a / b（若 b 为 0，商返回字符串 'NA'）。\n"
            "主程序：连续读入若干行『a b』直到输入 'end'。每行调用 calc 并输出：\n"
            "a + b = 和, a - b = 差, a * b = 积, a / b = 商\n"
            "同时累计所有『和』放入列表，结束输出运算次数、所有和之和与平均和（保留1位小数）。"
        ),
        "answer": (
            "def calc(a, b):\n"
            "    s = a + b\n"
            "    d = a - b\n"
            "    p = a * b\n"
            "    q = a / b if b != 0 else 'NA'\n"
            "    return (s, d, p, q)\n\n"
            "sums = []\n"
            "count = 0\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == 'end':\n"
            "        break\n"
            "    a, b = line.split()\n"
            "    a, b = float(a), float(b)\n"
            "    s, d, p, q = calc(a, b)\n"
            "    print(f\"{a} + {b} = {s}, {a} - {b} = {d}, {a} * {b} = {p}, {a} / {b} = {q}\")\n"
            "    print('  (' + ('可除' if b != 0 else '除数为0，商为NA') + ')')\n"
            "    sums.append(s)\n"
            "    count += 1\n"
            "print(f\"共完成 {count} 次运算，所有和之和 = {sum(sums):.1f}，平均和 = {sum(sums)/count:.1f}\")\n"
        ),
        "explanation": (
            "思路：① calc 用 return (s, d, p, q) 一次性返回四个值，主程序用 a, b = calc(...) "
            "解包接收（体现多返回值与形参实参传递）；"
            "② 除法用条件表达式处理除零，返回 'NA' 而非抛异常；"
            "③ 主程序用 while 循环处理不定行输入，a, b = line.split() 解包；"
            "④ sums 列表收集每次的『和』，结束用 sum/len 统计；综合了函数定义、元组返回、解包与循环。"
        ),
        "sample_input": "10 5\n7 0\n3 4\nend\n",
    },
    # ===================== L14 / topic 58 函数的各类参数与函数嵌套 =====================
    {
        "topic_id": 58,
        "title": "L14-58-A 档案构建器（*args / 默认 / **kwargs + 嵌套）",
        "content": (
            "档案构建器。请定义函数 `build_profile(name, *skills, level='junior', **extra)`：\n"
            "- `name` 姓名（必填位置参数）；\n"
            "- `*skills` 接收任意个技能（可变位置参数）；\n"
            "- `level` 等级（默认 'junior'）；\n"
            "- `**extra` 接收任意额外键值对。\n"
            "请定义**嵌套函数** `format_line(k, v)` 把键值对格式化为『k: v』；函数返回由嵌套函数生成的档案字符串，"
            "包含姓名、等级、技能列表、以及 extra 中每一项。\n"
            "主程序：读入一行『姓名 技能1 技能2 ...』，用 * 拆包技能，分别用默认 level 和 level='senior' "
            "调用，并都传入 city='BJ' 作为 extra，输出两次结果。"
        ),
        "answer": (
            "def build_profile(name, *skills, level='junior', **extra):\n"
            "    def format_line(k, v):\n"
            "        return f'{k}: {v}'\n"
            "    skills_upper = [s.upper() for s in skills]\n"
            "    lines = [format_line('姓名', name), format_line('等级', level)]\n"
            "    lines.append(format_line('技能', ', '.join(skills_upper) if skills_upper else '无'))\n"
            "    for k, v in extra.items():\n"
            "        lines.append(format_line(k, v))\n"
            "    lines.append(format_line('技能数', len(skills)))\n"
            "    return '\\n'.join(lines)\n\n"
            "line = input().strip()\n"
            "parts = line.split()\n"
            "name = parts[0]\n"
            "skills = parts[1:]\n"
            "print('【默认档案】')\n"
            "print(build_profile(name, *skills, city='BJ'))\n"
            "print('\\n【高级档案】')\n"
            "print(build_profile(name, *skills, level='senior', city='BJ', age=30))\n"
            "print(f'提示：本次共解析 {len(skills)} 项技能，level 默认 junior。')\n"
        ),
        "explanation": (
            "思路：① build_profile 同时展示了三类参数——必填位置参数、*args 可变位置、默认参数 level、**kwargs 额外键值；"
            "② 嵌套函数 format_line 留在函数内部，只服务于本函数；"
            "③ *skills 收集为元组，', '.join 拼成字符串；**extra 在 for 循环里逐项格式化；"
            "④ 主程序用 build_profile(name, *skills, ...) 把列表拆包成位置参数传入，演示 * 拆包调用。"
        ),
        "sample_input": "Alice Python SQL Git\n",
    },
    {
        "topic_id": 58,
        "title": "L14-58-B 闭包加法器（函数嵌套 + 调用）",
        "content": (
            "闭包加法器。请定义函数 `make_adder(n)`，它返回一个**嵌套函数** `add(x)`，add 把参数 x "
            "加上外层 n 后返回（演示闭包捕获变量）。\n"
            "主程序：读一行两个整数 a b。先调用 make_adder(a) 得到 adder，对 b 调用 adder(b) 输出结果；"
            "再用 make_adder(10) 得到 plus10，对 [1,2,3,4,5] 逐个作用并输出列表与累积和；"
            "最后演示 make_adder 在不同 n 下的闭包独立性（输出 make_adder(base)(7) 对 base=0/5/100 的结果）。"
        ),
        "answer": (
            "def make_adder(n):\n"
            "    def add(x):\n"
            "        return x + n\n"
            "    return add\n\n"
            "def make_subtractor(n):\n"
            "    def sub(x):\n"
            "        return x - n\n"
            "    return sub\n\n"
            "line = input().strip()\n"
            "a, b = (int(x) for x in line.split())\n"
            "adder_ab = make_adder(a)\n"
            "print(f'make_adder({a}) 作用于 {b} = {adder_ab(b)}')\n\n"
            "plus10 = make_adder(10)\n"
            "nums = [1, 2, 3, 4, 5]\n"
            "boosted = [plus10(x) for x in nums]\n"
            "print(f'plus10 作用于 {nums} = {boosted}')\n"
            "print(f'plus10 累积和 = {sum(boosted)}')\n"
            "print('说明：make_adder 返回的内部函数 add 捕获了创建时的 n（闭包）。')\n"
            "sub5 = make_subtractor(5)\n"
            "print(f'make_subtractor(5) 作用于 20 = {sub5(20)}')\n"
            "for base in (0, 5, 100):\n"
            "    print(f'make_adder({base})(7) = {make_adder(base)(7)}')\n"
        ),
        "explanation": (
            "思路：① make_adder(n) 返回 add，add 引用了外层参数 n，因此『记住』了创建时的偏移量——这是闭包；"
            "② 主程序先演示用输入 a 构造的 adder 对 b 生效；"
            "③ plus10 演示对一组数批量作用（列表推导式）；"
            "④ 末尾用不同 base 调用证明每个 make_adder 实例都有独立的 n，互不影响；"
            "⑤ 综合展示『函数嵌套 + 闭包捕获 + 调用』。"
        ),
        "sample_input": "3 7\n",
    },
    # ===================== L15 / topic 59 作用域,匿名函数和匿名函数的参数 =====================
    {
        "topic_id": 59,
        "title": "L15-59-A 计数器工厂（nonlocal 作用域）",
        "content": (
            "计数器工厂。请定义函数 `make_counter()`，它内部维护一个计数器变量 `count`，并返回一个"
            "**嵌套函数** `inc()`：每次调用 inc() 都把 count 加 1 并返回当前值（需用 `nonlocal` 声明修改外层变量）。\n"
            "主程序：读一个整数 n，创建计数器 c 连续调用 n 次并打印每次计数值；再新建独立计数器 c2 "
            "调用一次，随后再调用一次 c，证明两者作用域独立、互不干扰。"
        ),
        "answer": (
            "def make_counter():\n"
            "    count = 0\n"
            "    def inc():\n"
            "        nonlocal count\n"
            "        count += 1\n"
            "        return count\n"
            "    return inc\n\n"
            "def make_counter_with_step(step):\n"
            "    count = 0\n"
            "    def inc():\n"
            "        nonlocal count\n"
            "        count += step\n"
            "        return count\n"
            "    return inc\n\n"
            "n = int(input())\n"
            "c = make_counter()\n"
            "print('计数器 c 连续调用：')\n"
            "for i in range(n):\n"
            "    print(f'  第{i+1}次 -> {c()}')\n\n"
            "c2 = make_counter()\n"
            "print(f'新建 c2 第一次 -> {c2()}')\n"
            "print(f'c 再次调用(独立作用域) -> {c()}')\n"
            "print(f'两个计数器当前值对比：c 停在 {c()}，c2 停在 {c2()}')\n"
            "print('每个 make_counter() 调用都生成独立闭包，互不影响。')\n"
        ),
        "explanation": (
            "思路：① make_counter 内定义 count 局部变量，inc 用 nonlocal 声明后才能修改它（否则按 LEGB "
            "会在局部新建变量）；"
            "② 每次调用 inc 返回递增后的值，状态保存在闭包里；"
            "③ 主程序创建两个计数器 c、c2，分别调用验证它们各自维护独立的 count；"
            "④ 体现『嵌套函数 + nonlocal 作用域』这一本课核心。"
        ),
        "sample_input": "3\n",
    },
    {
        "topic_id": 59,
        "title": "L15-59-B 匿名函数排序（lambda 作 key）",
        "content": (
            "学生排序器。输入若干行，每行『姓名 分数 年龄』，以 'end' 结束。请用**匿名函数(lambda)**作为 "
            "key，按『分数降序，分数相同则年龄升序』对学生排序，输出排序后的姓名序列；并额外用 lambda "
            "借助 filter 提取出所有及格(分数>=60)学生的姓名列表。要求排序与过滤必须使用 lambda 表达式。"
        ),
        "answer": (
            "students = []\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == 'end':\n"
            "        break\n"
            "    name, score, age = line.split()\n"
            "    students.append((name, int(score), int(age)))\n\n"
            "ranked = sorted(students, key=lambda s: (-s[1], s[2]))\n"
            "ranked_names = [s[0] for s in ranked]\n\n"
            "passed = list(filter(lambda s: s[1] >= 60, students))\n"
            "passed_names = [s[0] for s in passed]\n\n"
            "print('排序结果（分数降序, 年龄升序）：')\n"
            "for name in ranked_names:\n"
            "    print('  ', name)\n"
            "top = ranked[0]\n"
            "print(f'状元：{top[0]}（{top[1]}分, {top[2]}岁）')\n"
            "print('及格学生：', passed_names)\n"
            "print(f'共 {len(students)} 人，及格 {len(passed_names)} 人。')\n"
            "print('说明：lambda 作为 sorted 的 key 与 filter 的谓词，参数即被处理的元素。')\n"
        ),
        "explanation": (
            "思路：① lambda s: (-s[1], s[2]) 把排序键设为 (分数取负=降序, 年龄升序)，实现复合排序；"
            "② lambda 的参数 s 就是 students 里的每个元组，无需单独 def；"
            "③ filter(lambda s: s[1]>=60, students) 用 lambda 作谓词过滤及格项；"
            "④ 列表推导式提取姓名；综合展示『匿名函数 + 参数 + 排序/过滤』。"
        ),
        "sample_input": "Alice 88 20\nBob 45 19\nCindy 92 21\nDavid 60 22\nend\n",
    },
    # ===================== L16 / topic 60 lambda结合if判断, 内置函数与拆包 =====================
    {
        "topic_id": 60,
        "title": "L16-60-A 成绩分级（lambda + if 条件表达式 + map）",
        "content": (
            "成绩分级器。第一行输入 n，第二行输入 n 个整数分数。请用 `map` 配合**带 if 的 lambda** 把每个分数"
            "映射为等级：>=90 'A'、>=80 'B'、>=60 'C'、否则 'D'；用 `filter` + lambda 过滤出不及格(<60)的分数；"
            "用 `zip` 把分数与等级配对后输出每对『分数->等级』；最后输出不及格分数列表、及格人数、以及完整等级分布。"
        ),
        "answer": (
            "n = int(input())\n"
            "scores = [int(x) for x in input().split()]\n"
            "avg = sum(scores) / len(scores)\n\n"
            "grade = lambda s: 'A' if s >= 90 else 'B' if s >= 80 else 'C' if s >= 60 else 'D'\n"
            "grades = list(map(grade, scores))\n\n"
            "failed = list(filter(lambda s: s < 60, scores))\n"
            "passed = [s for s in scores if s >= 60]\n"
            "fail_info = list(map(lambda s: f'{s}分不及格', failed))\n\n"
            "print('分数->等级：')\n"
            "for sc, gr in zip(scores, grades):\n"
            "    print(f'  {sc} -> {gr}')\n"
            "print('不及格分数：', failed)\n"
            "print('不及格详情：', fail_info)\n"
            "print(f'总人数：{n}，不及格人数：{len(failed)}，及格人数：{len(passed)}')\n"
            "dist = {g: grades.count(g) for g in set(grades)}\n"
            "print(f'平均分：{avg:.1f}')\n"
            "print(f'等级分布：{grades}，各等级人数：{dist}')\n"
            "print(f'最优等级：{max(grades)}，最差等级：{min(grades)}')\n"
            "print('说明：lambda 配合 if 条件表达式实现多级分数映射。')\n"
        ),
        "explanation": (
            "思路：① lambda + 嵌套 if 条件表达式一步完成多级映射（A/B/C/D）；"
            "② map(grade, scores) 把分级函数批量应用到每个分数；"
            "③ filter(lambda s: s<60, ...) 过滤不及格项；"
            "④ zip(scores, grades) 把原分数与等级配对，循环里自动拆包为 sc, gr；"
            "⑤ 综合展示『lambda+if、map/filter、zip 拆包』三大本课要点。"
        ),
        "sample_input": "6\n95 82 73 58 90 45\n",
    },
    {
        "topic_id": 60,
        "title": "L16-60-B 配对分析器（map/filter/zip/sorted + 拆包）",
        "content": (
            "配对分析器。输入两行：第一行 n 个姓名（空格分隔），第二行 n 个对应分数（数量一致）。请使用内置函数完成：\n"
            "- 用 `zip` 把姓名与分数配对成 (姓名, 分数)；\n"
            "- 用 `sorted` + lambda key 按分数降序排序；\n"
            "- 用 `map` + lambda 把每对格式化为『姓名:分数』；\n"
            "- 用 `filter` + lambda 保留及格(>=60)项；\n"
            "- 用 `max` / `min` + lambda key 求出最高分与最低分姓名。\n"
            "输出：原始配对、排序后、及格项、最高分、最低分及统计。"
        ),
        "answer": (
            "names = input().split()\n"
            "scores = [int(x) for x in input().split()]\n"
            "avg_score = sum(scores) / len(scores)\n\n"
            "pairs = list(zip(names, scores))\n"
            "ranked = sorted(pairs, key=lambda p: p[1], reverse=True)\n"
            "formatted = list(map(lambda p: f'{p[0]}:{p[1]}', ranked))\n"
            "passed = list(filter(lambda p: p[1] >= 60, pairs))\n"
            "top = max(pairs, key=lambda p: p[1])\n"
            "lowest = min(pairs, key=lambda p: p[1])\n"
            "grade_of = {name: ('及格' if sc >= 60 else '不及格') for name, sc in pairs}\n\n"
            "print('原始配对：', pairs)\n"
            "print('按分数降序：', formatted)\n"
            "print('前三名：', formatted[:3])\n"
            "print('及格项：', passed)\n"
            "print(f'最高分：{top[0]} ({top[1]})')\n"
            "print(f'最低分：{lowest[0]} ({lowest[1]})')\n"
            "print(f'平均分：{avg_score:.1f}')\n"
            "print(f'及格判定：{grade_of}')\n"
            "print(f'统计：共 {len(pairs)} 人，及格 {len(list(passed))} 人。')\n"
        ),
        "explanation": (
            "思路：① zip(names, scores) 把两个列表按位置配对成元组；"
            "② sorted(..., key=lambda p: p[1], reverse=True) 按分数降序；"
            "③ map(lambda p: f'...', ranked) 批量格式化；"
            "④ filter(lambda p: p[1]>=60, pairs) 保留及格；"
            "⑤ max/min 用 lambda 指定比较键，循环里用 p[0],p[1] 拆包；综合展现内置函数 + lambda + 拆包。"
        ),
        "sample_input": "Alice Bob Cindy David\n88 45 92 60\n",
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
                print(f"[OK]   {q['title']}  ({len([x for x in q['answer'].split(chr(10)) if x.strip()])} 行)")
                out = res.stdout.strip()
                print("       out:", out.replace("\n", " | ")[:200])
            else:
                print(f"[FAIL] {q['title']}")
                print("       STDERR:", res.stderr.strip()[:400])
        finally:
            os.unlink(path)
    print(f"\n本地验证通过 {ok}/{len(QUESTIONS)}")
