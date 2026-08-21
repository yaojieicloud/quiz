"""批次4：L13-L16 (topic 57-60) 进阶题，每课 5 题，共 20 题。
主题与既有题（成绩报告函数/四则计算器/档案构建器/闭包加法器/计数器工厂/学生排序器/成绩分级器/配对分析器）错开。
"""

QUESTIONS = [
    # ===================== L13 / topic 57 函数、return与形参实参 =====================
    {
        "topic_id": 57,
        "title": "L13-57-A 体温检查函数",
        "content": (
            "体温检查函数。请定义函数 `check_temp(temp)`，接收体温（小数），返回一个字典：\n"
            "- 'level'：'偏低'(<36.0) / '正常'(36.0-37.3) / '偏高'(>37.3)\n"
            "- 'need_doctor'：是否需要看医生（True 当 >38.5）\n"
            "- 'advice'：对应建议文字（偏低→注意保暖；正常→继续保持；偏高→多喝水休息）\n"
            "主程序：第一行输入 n，接下来 n 行每行一个体温值，逐个调用 check_temp 并按格式输出：\n"
            "体温X -> 等级Y，建议Z（需要看医生：True/False），最后统计需要看医生的人数。"
        ),
        "answer": (
            "# 体温检查函数\n"
            "def check_temp(temp):\n"
            "    if temp < 36.0:\n"
            "        level = \"偏低\"\n"
            "        advice = \"注意保暖\"\n"
            "    elif temp <= 37.3:\n"
            "        level = \"正常\"\n"
            "        advice = \"继续保持\"\n"
            "    else:\n"
            "        level = \"偏高\"\n"
            "        advice = \"多喝水休息\"\n"
            "    need_doctor = temp > 38.5\n"
            "    return {\n"
            "        \"level\": level,\n"
            "        \"need_doctor\": need_doctor,\n"
            "        \"advice\": advice,\n"
            "    }\n\n"
            "n = int(input())\n"
            "doctor_count = 0\n"
            "i = 0\n"
            "while i < n:\n"
            "    t = float(input())\n"
            "    result = check_temp(t)\n"
            "    print(\"体温\" + str(t) + \" -> 等级\" + result[\"level\"] + \"，建议\" + result[\"advice\"] + \"（需要看医生：\" + str(result[\"need_doctor\"]) + \"）\")\n"
            "    if result[\"need_doctor\"]:\n"
            "        doctor_count = doctor_count + 1\n"
            "    i = i + 1\n"
            "print(\"需要看医生的人数：\" + str(doctor_count))\n"
        ),
        "explanation": (
            "思路：函数内部用 if-elif-else 分档，把等级、建议、是否就医打包成字典一次 return；"
            "主程序只负责输入输出，循环里调用函数拿结果。"
            "讲解：函数返回字典可以一次传出多个相关结果，调用方用键取用；"
            "「形参传入、return 传出」让计算逻辑可以反复使用；"
            "布尔值直接 temp > 38.5 赋给变量，不用再写 if。"
        ),
        "sample_input": "4\n36.5\n39.0\n35.5\n37.8\n",
    },
    {
        "topic_id": 57,
        "title": "L13-57-B 长方形计算器",
        "content": (
            "长方形计算器。请定义函数 `rect_info(length, width)`，返回一个元组：\n"
            "(周长, 面积, 对角线长度)，其中对角线 = (长²+宽²)**0.5，结果都保留 2 位小数（用 round）。\n"
            "主程序：第一行输入 n，接下来 n 行每行「长 宽」，逐行调用函数并输出：\n"
            "长x宽 -> 周长A 面积B 对角线C；最后输出所有长方形中面积最大的那组的长和宽。"
        ),
        "answer": (
            "# 长方形计算器（元组返回多值）\n"
            "def rect_info(length, width):\n"
            "    perimeter = (length + width) * 2\n"
            "    area = length * width\n"
            "    diagonal = (length ** 2 + width ** 2) ** 0.5\n"
            "    return (round(perimeter, 2), round(area, 2), round(diagonal, 2))\n\n"
            "n = int(input())\n"
            "records = []\n"
            "i = 0\n"
            "while i < n:\n"
            "    l, w = map(float, input().split())\n"
            "    p, a, d = rect_info(l, w)\n"
            "    print(str(l) + \"x\" + str(w) + \" -> 周长\" + str(p) + \" 面积\" + str(a) + \" 对角线\" + str(d))\n"
            "    records.append((l, w, a))\n"
            "    i = i + 1\n"
            "# 找面积最大的一组\n"
            "best = records[0]\n"
            "for item in records:\n"
            "    if item[2] > best[2]:\n"
            "        best = item\n"
            "print(\"面积最大：长\" + str(best[0]) + \" 宽\" + str(best[1]) + \"（面积\" + str(best[2]) + \"）\")\n"
        ),
        "explanation": (
            "思路：函数算好三个量打包成元组 return；调用方用 p, a, d = rect_info(...) 拆包接收；"
            "同时把 (长,宽,面积) 存进 records，最后遍历找面积最大的一组。"
            "讲解：返回元组是「一次返回多个值」的常用方式，拆包赋值一一对应；"
            "round(x, 2) 在函数内完成，调用方拿到的就是干净的结果；"
            "找最大值用打擂台，比较元组的第 3 个元素 item[2]。"
        ),
        "sample_input": "3\n3 4\n5 12\n6 8\n",
    },
    {
        "topic_id": 57,
        "title": "L13-57-C 密码验证函数",
        "content": (
            "密码验证函数。请定义函数 `check_password(pwd)`，返回一个整数分数：\n"
            "长度>=8 得 1 分；含数字得 1 分；含大写字母得 1 分；含小写字母得 1 分（满分 4 分）。\n"
            "再定义函数 `score_to_level(score)`：4→「强」、3→「中」、其余→「弱」，返回等级字符串。\n"
            "主程序：输入 3 行密码，每行先调用 check_password 得分数，再调用 score_to_level 得等级，"
            "输出「密码X：分数Y/4，等级Z」；最后输出三个密码的平均分（1 位小数）。"
        ),
        "answer": (
            "# 密码验证函数（函数互相配合）\n"
            "def check_password(pwd):\n"
            "    score = 0\n"
            "    if len(pwd) >= 8:\n"
            "        score = score + 1\n"
            "    has_digit = False\n"
            "    has_upper = False\n"
            "    has_lower = False\n"
            "    for c in pwd:\n"
            "        if c.isdigit():\n"
            "            has_digit = True\n"
            "        if c.isupper():\n"
            "            has_upper = True\n"
            "        if c.islower():\n"
            "            has_lower = True\n"
            "    if has_digit:\n"
            "        score = score + 1\n"
            "    if has_upper:\n"
            "        score = score + 1\n"
            "    if has_lower:\n"
            "        score = score + 1\n"
            "    return score\n\n"
            "def score_to_level(score):\n"
            "    if score == 4:\n"
            "        return \"强\"\n"
            "    elif score == 3:\n"
            "        return \"中\"\n"
            "    else:\n"
            "        return \"弱\"\n\n"
            "total_score = 0\n"
            "i = 0\n"
            "while i < 3:\n"
            "    pwd = input()\n"
            "    s = check_password(pwd)\n"
            "    level = score_to_level(s)\n"
            "    print(\"密码\" + pwd + \"：分数\" + str(s) + \"/4，等级\" + level)\n"
            "    total_score = total_score + s\n"
            "    i = i + 1\n"
            "print(\"平均分：\" + str(round(total_score / 3, 1)))\n"
        ),
        "explanation": (
            "思路：check_password 用循环扫描字符得到分数并 return；score_to_level 把分数翻译成等级；"
            "主程序循环三次，把两个函数串起来使用——一个函数的输出当另一个函数的输入。"
            "讲解：把大任务拆成两个小函数，每个只做一件事，代码更清楚；"
            "函数里 for c in pwd 可以直接遍历字符串的每个字符；"
            "return 把结果交回调用处，函数本身不打印。"
        ),
        "sample_input": "Abc12345\nabc\nHello2026\n",
    },
    {
        "topic_id": 57,
        "title": "L13-57-D 找零计算器",
        "content": (
            "找零计算器。请定义函数 `make_change(price, pay)`：\n"
            "- 若 pay < price，返回字符串 '钱不够'\n"
            "- 否则返回找零金额（保留 2 位小数）\n"
            "主程序：连续读入若干行「价格 付款」，输入 end 结束。每行调用 make_change，"
            "成功就输出「价格X 付款Y 找零Z」并把找零累加到列表，钱不够输出「价格X 付款Y 钱不够」；"
            "结束后输出成功交易的次数和找零总额（2 位小数）。"
        ),
        "answer": (
            "# 找零计算器\n"
            "def make_change(price, pay):\n"
            "    if pay < price:\n"
            "        return \"钱不够\"\n"
            "    return round(pay - price, 2)\n\n"
            "changes = []\n"
            "success = 0\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    price, pay = map(float, line.split())\n"
            "    result = make_change(price, pay)\n"
            "    if result == \"钱不够\":\n"
            "        print(\"价格\" + str(price) + \" 付款\" + str(pay) + \" 钱不够\")\n"
            "    else:\n"
            "        print(\"价格\" + str(price) + \" 付款\" + str(pay) + \" 找零\" + str(result))\n"
            "        changes.append(result)\n"
            "        success = success + 1\n"
            "print(\"成功交易次数：\" + str(success))\n"
            "total = 0\n"
            "for c in changes:\n"
            "    total = total + c\n"
            "print(\"找零总额：\" + str(round(total, 2)))\n"
        ),
        "explanation": (
            "思路：函数先判断钱够不够，不够返回字符串标记，够则返回找零数字；"
            "主程序根据返回值类型（字符串==「钱不够」与否）分流处理，成功的找零收进列表最后求和。"
            "讲解：函数可以返回不同类型的值，调用方要能区分；"
            "这里用「特殊字符串」表示失败是一种简单做法；"
            "累加列表用 for 循环逐个相加，和 sum() 效果一样。"
        ),
        "sample_input": "5.5 10\n3 2\n8.8 20\nend\n",
    },
    {
        "topic_id": 57,
        "title": "L13-57-E 闰年判断函数",
        "content": (
            "闰年判断函数。请定义函数 `is_leap(year)`，是闰年返回 True，否则返回 False。\n"
            "再定义函数 `days_in_feb(year)`，调用 is_leap 决定返回 29 还是 28。\n"
            "主程序：输入一行若干个年份（空格分隔），对每个年份输出「年份X：闰年/平年，2月有Y天」；"
            "统计其中闰年的个数；最后输出距今最近的下一个闰年（从 2026 开始逐年用 is_leap 检查）。"
        ),
        "answer": (
            "# 闰年判断函数\n"
            "def is_leap(year):\n"
            "    if year % 400 == 0:\n"
            "        return True\n"
            "    if year % 100 == 0:\n"
            "        return False\n"
            "    if year % 4 == 0:\n"
            "        return True\n"
            "    return False\n\n"
            "def days_in_feb(year):\n"
            "    if is_leap(year):\n"
            "        return 29\n"
            "    return 28\n\n"
            "years = []\n"
            "for token in input().split():\n"
            "    years.append(int(token))\n"
            "leap_count = 0\n"
            "for year in years:\n"
            "    kind = \"闰年\" if is_leap(year) else \"平年\"\n"
            "    print(\"年份\" + str(year) + \"：\" + kind + \"，2月有\" + str(days_in_feb(year)) + \"天\")\n"
            "    if is_leap(year):\n"
            "        leap_count = leap_count + 1\n"
            "print(\"闰年个数：\" + str(leap_count))\n"
            "# 找 2026 之后最近的闰年\n"
            "y = 2026\n"
            "while not is_leap(y):\n"
            "    y = y + 1\n"
            "print(\"下一个闰年：\" + str(y))\n"
        ),
        "explanation": (
            "思路：is_leap 按「400→100→4」顺序逐步判断并提前 return；days_in_feb 复用 is_leap 的结果；"
            "主程序遍历年份列表调用函数，再用 while not is_leap(y) 找下一个闰年。"
            "讲解：函数里多个 return 可以提前结束，逻辑像漏斗一样层层过滤；"
            "函数调用函数（days_in_feb 调 is_leap）是复用的体现；"
            "while not is_leap(y) 把函数当条件用，非常简洁。"
        ),
        "sample_input": "1900 2000 2024 2023\n",
    },

    # ===================== L14 / topic 58 函数的各类参数与函数嵌套 =====================
    {
        "topic_id": 58,
        "title": "L14-58-A 奶茶点单器",
        "content": (
            "奶茶点单器。请定义函数 `order(name, size='中杯', sugar='正常糖', ice='正常冰')`，"
            "返回字符串「name(size, sugar, ice)」。\n"
            "主程序：输入 4 行订单，每行用空格分隔，可能是「名字」或「名字 杯型」或「名字 杯型 糖度」"
            "或「名字 杯型 糖度 冰度」（项数不定）。请按项数选择调用方式：1 项全用默认值，"
            "2 项传 size，3 项传 size 和 sugar，4 项全传（用关键字参数）。输出每单的完整描述。"
        ),
        "answer": (
            "# 奶茶点单器（默认参数）\n"
            "def order(name, size=\"中杯\", sugar=\"正常糖\", ice=\"正常冰\"):\n"
            "    return name + \"(\" + size + \", \" + sugar + \", \" + ice + \")\"\n\n"
            "i = 0\n"
            "while i < 4:\n"
            "    parts = input().split()\n"
            "    if len(parts) == 1:\n"
            "        result = order(parts[0])\n"
            "    elif len(parts) == 2:\n"
            "        result = order(parts[0], size=parts[1])\n"
            "    elif len(parts) == 3:\n"
            "        result = order(parts[0], size=parts[1], sugar=parts[2])\n"
            "    else:\n"
            "        result = order(parts[0], size=parts[1], sugar=parts[2], ice=parts[3])\n"
            "    print(\"第\" + str(i + 1) + \"单：\" + result)\n"
            "    i = i + 1\n"
        ),
        "explanation": (
            "思路：函数给 size/sugar/ice 设默认值，调用时缺省就用默认；"
            "主程序按输入项数用 if-elif 选择传几个参数，并用「参数名=值」的关键字形式更清楚。"
            "讲解：默认参数让函数调用更灵活，常见选项不传也行；"
            "关键字参数 size='大杯' 不依赖位置，可读性好；"
            "带默认值的参数必须放在不带默认值的参数后面。"
        ),
        "sample_input": "珍珠奶茶\n柠檬茶 大杯\n芒果冰沙 大杯 少糖\n可乐 小杯 无糖 去冰\n",
    },
    {
        "topic_id": 58,
        "title": "L14-58-B 平均分计算器",
        "content": (
            "平均分计算器。请定义函数 `avg_score(*scores)`，用可变参数接收任意多个分数，"
            "返回平均分（保留 1 位小数）；若没有传入任何分数，返回 0。\n"
            "主程序：输入 3 行，每行是若干个空格分隔的分数（个数不定），"
            "请把每行转成整数列表后用 avg_score(*列表) 的拆包方式调用，"
            "输出每行的分数个数和平均分；最后把三行所有分数合并成一个大列表再调用一次，输出总平均。"
        ),
        "answer": (
            "# 平均分计算器（可变参数）\n"
            "def avg_score(*scores):\n"
            "    if len(scores) == 0:\n"
            "        return 0\n"
            "    total = 0\n"
            "    for s in scores:\n"
            "        total = total + s\n"
            "    return round(total / len(scores), 1)\n\n"
            "all_scores = []\n"
            "i = 0\n"
            "while i < 3:\n"
            "    row = []\n"
            "    for token in input().split():\n"
            "        row.append(int(token))\n"
            "    avg = avg_score(*row)\n"
            "    print(\"第\" + str(i + 1) + \"行：\" + str(len(row)) + \" 个分数，平均 \" + str(avg))\n"
            "    for s in row:\n"
            "        all_scores.append(s)\n"
            "    i = i + 1\n"
            "print(\"总平均：\" + str(avg_score(*all_scores)))\n"
        ),
        "explanation": (
            "思路：*scores 把任意多个参数收进元组；先判空防除零，再求和除以个数；"
            "调用时 avg_score(*列表) 用 * 把列表拆开传进去，个数不定也能用。"
            "讲解：*参数 是「收集」，*列表 是「拆开」，方向相反但成对使用；"
            "可变参数适合个数不确定的场景（如任意门成绩求平均）；"
            "函数里先处理边界情况（空输入）再算主逻辑是好习惯。"
        ),
        "sample_input": "90 85 92\n78 88\n95 100 60 80\n",
    },
    {
        "topic_id": 58,
        "title": "L14-58-C 快递运费函数",
        "content": (
            "快递运费函数。请定义函数 `shipping_fee(weight, city='local', urgent=False)`：\n"
            "- 基础费 = 重量×5\n"
            "- city 为 'far' 时加 10 元\n"
            "- urgent 为 True 时加 15 元\n"
            "返回总费用（2 位小数）。\n"
            "主程序：输入 3 行，每行「重量 目的地 yes/no」，分别以位置参数、关键字参数、"
            "混合方式调用函数（urgent 按 yes/no 转布尔），输出每单费用；最后输出三单总费用。"
        ),
        "answer": (
            "# 快递运费函数（多种调用方式）\n"
            "def shipping_fee(weight, city=\"local\", urgent=False):\n"
            "    fee = weight * 5\n"
            "    if city == \"far\":\n"
            "        fee = fee + 10\n"
            "    if urgent:\n"
            "        fee = fee + 15\n"
            "    return round(fee, 2)\n\n"
            "total_all = 0\n"
            "i = 0\n"
            "while i < 3:\n"
            "    parts = input().split()\n"
            "    weight = float(parts[0])\n"
            "    city = parts[1]\n"
            "    urgent = parts[2] == \"yes\"\n"
            "    if i == 0:\n"
            "        fee = shipping_fee(weight, city, urgent)\n"
            "    elif i == 1:\n"
            "        fee = shipping_fee(weight, city=city, urgent=urgent)\n"
            "    else:\n"
            "        fee = shipping_fee(weight=weight, city=city, urgent=urgent)\n"
            "    print(\"第\" + str(i + 1) + \"单费用：\" + str(fee) + \" 元\")\n"
            "    total_all = total_all + fee\n"
            "    i = i + 1\n"
            "print(\"三单总费用：\" + str(round(total_all, 2)) + \" 元\")\n"
        ),
        "explanation": (
            "思路：函数按三个参数计算费用，布尔参数 urgent 直接 if urgent 判断；"
            "主程序故意用三种调用方式（全位置、混合、全关键字）演示灵活性，"
            "urgent 用 parts[2]=='yes' 一行转成布尔。"
            "讲解：布尔参数让函数支持「开关」式选项；"
            "关键字参数和位置参数可以混用，但位置参数必须在关键字参数前面；"
            "字符串比较结果是布尔值，可直接赋给变量。"
        ),
        "sample_input": "2 local no\n3 far yes\n1.5 far no\n",
    },
    {
        "topic_id": 58,
        "title": "L14-58-D 嵌套函数密码生成器",
        "content": (
            "嵌套函数密码生成器。请定义外层函数 `make_password(base, level)`，内部定义嵌套函数：\n"
            "- `add_digits(s)`：在 s 末尾加上 base 的长度两位数字（如长度 5 就加 '05'）\n"
            "- `add_marks(s)`：若 level 为 'high'，在末尾加 '!@'，否则加 '.'\n"
            "外层函数依次调用两个嵌套函数，返回最终密码。\n"
            "主程序：输入两行「base level」，分别调用 make_password 并输出结果和每个密码的长度。"
        ),
        "answer": (
            "# 嵌套函数密码生成器\n"
            "def make_password(base, level):\n"
            "    # 嵌套函数1：末尾加长度数字\n"
            "    def add_digits(s):\n"
            "        length = len(s)\n"
            "        if length < 10:\n"
            "            return s + \"0\" + str(length)\n"
            "        return s + str(length)\n"
            "    # 嵌套函数2：末尾加符号\n"
            "    def add_marks(s):\n"
            "        if level == \"high\":\n"
            "            return s + \"!@\"\n"
            "        return s + \".\"\n"
            "    pwd = add_digits(base)\n"
            "    pwd = add_marks(pwd)\n"
            "    return pwd\n\n"
            "i = 0\n"
            "while i < 2:\n"
            "    base, level = input().split()\n"
            "    result = make_password(base, level)\n"
            "    print(\"密码：\" + result)\n"
            "    print(\"长度：\" + str(len(result)))\n"
            "    i = i + 1\n"
        ),
        "explanation": (
            "思路：外层函数内部定义两个小函数各管一步加工，外层按顺序调用它们并返回结果；"
            "嵌套函数可以访问外层函数的参数（如 level），这是嵌套函数的便利之处。"
            "讲解：嵌套函数定义在外层函数内部，只有外层函数能调用它，起到「封装步骤」的作用；"
            "长度不足两位要补 0，用 if 判断处理；"
            "把复杂任务拆成内层小步骤，外层只负责编排。"
        ),
        "sample_input": "abc high\nhello low\n",
    },
    {
        "topic_id": 58,
        "title": "L14-58-E 餐厅账单函数",
        "content": (
            "餐厅账单函数。请定义函数 `bill(items, *discounts, note='无备注')`：\n"
            "- items 是 (菜名, 价格) 元组列表，计算总价\n"
            "- *discounts 接收任意多个折扣比例（如 0.9 表示打九折），依次叠加（价格依次乘每个折扣）\n"
            "- note 是备注（默认 '无备注'）\n"
            "返回 (总价, 折后价, 备注) 元组，金额保留 2 位小数。\n"
            "主程序：固定菜单 [('汉堡',15),('薯条',8),('可乐',5)]，分别按「不打折」「打九折」「先九折再减5元（折扣0.9后再乘0.95模拟）」"
            "三次调用（第三次的 note 传 '会员'），输出三张账单。"
        ),
        "answer": (
            "# 餐厅账单函数（位置+可变+关键字参数）\n"
            "def bill(items, *discounts, note=\"无备注\"):\n"
            "    total = 0\n"
            "    for name, price in items:\n"
            "        total = total + price\n"
            "    final = total\n"
            "    for d in discounts:\n"
            "        final = final * d\n"
            "    return (round(total, 2), round(final, 2), note)\n\n"
            "menu = [(\"汉堡\", 15), (\"薯条\", 8), (\"可乐\", 5)]\n"
            "# 账单1：不打折\n"
            "t, f, n = bill(menu)\n"
            "print(\"账单1：总价\" + str(t) + \" 折后\" + str(f) + \" 备注:\" + n)\n"
            "# 账单2：打九折\n"
            "t, f, n = bill(menu, 0.9)\n"
            "print(\"账单2：总价\" + str(t) + \" 折后\" + str(f) + \" 备注:\" + n)\n"
            "# 账单3：叠加折扣 + 备注\n"
            "t, f, n = bill(menu, 0.9, 0.95, note=\"会员\")\n"
            "print(\"账单3：总价\" + str(t) + \" 折后\" + str(f) + \" 备注:\" + n)\n"
            "print(\"三次调用演示了可变参数与关键字参数\")\n"
        ),
        "explanation": (
            "思路：形参顺序是「普通参数 items → 可变参数 *discounts → 关键字参数 note」；"
            "总价遍历 items 累加；折扣用 for d in discounts 依次相乘实现叠加；"
            "三次调用分别演示不传折扣、传一个折扣、传两个折扣加关键字备注。"
            "讲解：三类参数可以共存，顺序必须是（普通, *可变, 带默认/关键字）；"
            "元组列表 for name, price in items 可以直接拆包遍历；"
            "note='会员' 这种关键字传参不影响 *discounts 收集折扣。"
        ),
        "sample_input": "",
    },

    # ===================== L15 / topic 59 作用域、匿名函数和匿名函数的参数 =====================
    {
        "topic_id": 59,
        "title": "L15-59-A 计数器与作用域",
        "content": (
            "计数器与作用域。程序中先定义全局变量 count = 0。请定义函数 `visit(name)`：\n"
            "- 用 global 声明后把 count 加 1\n"
            "- 定义局部变量 message = '欢迎' + name\n"
            "- 返回 message\n"
            "主程序：输入若干行姓名，输入 end 结束；每行调用 visit 并输出返回值；"
            "结束后输出全局 count 的值；再尝试在函数外访问 message 是否可行——"
            "用一个 if 判断 'message' in dir() 输出「message 在函数外不存在」的说明。"
        ),
        "answer": (
            "# 计数器与作用域\n"
            "count = 0\n\n"
            "def visit(name):\n"
            "    global count\n"
            "    count = count + 1\n"
            "    message = \"欢迎\" + name\n"
            "    return message\n\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    result = visit(line)\n"
            "    print(result)\n"
            "print(\"总共接待：\" + str(count) + \" 人\")\n"
            "# 检查局部变量 message 是否泄漏到函数外\n"
            "if \"message\" in dir():\n"
            "    print(\"意外：message 存在于全局\")\n"
            "else:\n"
            "    print(\"message 是局部变量，函数外不存在\")\n"
            "print(\"结论：global 让函数修改全局 count；局部变量只在函数内有效\")\n"
        ),
        "explanation": (
            "思路：global count 让函数能修改全局变量；message 是局部变量，函数结束就消失；"
            "主程序循环调用 visit，最后用 dir() 检查全局名字里有没有 message。"
            "讲解：函数内直接给全局变量赋值会创建同名局部变量，要修改全局必须 global 声明；"
            "局部变量的生命周期只在函数调用期间；"
            "dir() 列出当前作用域的所有名字，可以用来验证作用域。"
        ),
        "sample_input": "小明\n小红\nend\n",
    },
    {
        "topic_id": 59,
        "title": "L15-59-B lambda 快速排序",
        "content": (
            "lambda 快速排序。输入两行：第一行若干姓名（空格分隔），第二行对应的分数（个数相同）。"
            "请完成：①用 zip 配对成 (姓名, 分数) 列表；"
            "②用 sorted + lambda 按分数从高到低排序并输出；"
            "③用 lambda 作为 key 找出分数最低的学生（min + lambda）；"
            "④用 filter + lambda 筛出及格(>=60)的学生并输出；"
            "⑤把排序结果的第一名和最后一名分别用 lambda 生成的格式化函数 show 输出「姓名(分数)」。"
        ),
        "answer": (
            "# lambda 快速排序\n"
            "names = input().split()\n"
            "scores = []\n"
            "for token in input().split():\n"
            "    scores.append(int(token))\n"
            "pairs = list(zip(names, scores))\n"
            "print(\"配对结果：\" + str(pairs))\n"
            "# 按分数从高到低\n"
            "ranked = sorted(pairs, key=lambda p: p[1], reverse=True)\n"
            "print(\"从高到低：\" + str(ranked))\n"
            "# 最低分学生\n"
            "lowest = min(pairs, key=lambda p: p[1])\n"
            "print(\"最低分：\" + lowest[0] + \"（\" + str(lowest[1]) + \"）\")\n"
            "# 及格筛选\n"
            "passed = list(filter(lambda p: p[1] >= 60, pairs))\n"
            "print(\"及格名单：\" + str(passed))\n"
            "# 用 lambda 做格式化函数\n"
            "show = lambda p: p[0] + \"(\" + str(p[1]) + \")\"\n"
            "print(\"第一名：\" + show(ranked[0]))\n"
            "print(\"最后一名：\" + show(ranked[-1]))\n"
        ),
        "explanation": (
            "思路：zip 配对后，sorted/min/filter 都用 lambda 指定「按什么比较/筛选」；"
            "最后把 lambda 赋给变量 show 当小函数用，格式化输出。"
            "讲解：lambda p: p[1] 读作「对每个 p 取第二个元素」；"
            "filter 保留条件为 True 的项，记得 list() 转换才能显示；"
            "lambda 只能写一个表达式，适合这种简单逻辑；复杂逻辑还是用 def。"
        ),
        "sample_input": "小明 小红 小刚 小美\n85 59 92 70\n",
    },
    {
        "topic_id": 59,
        "title": "L15-59-C 全局配置与局部覆盖",
        "content": (
            "全局配置与局部覆盖。定义全局变量 tax_rate = 0.1（税率）和 shop_name = '阳光小卖部'。"
            "请定义函数 `calc_price(price)`：返回含税价（price × (1+tax_rate)，2 位小数），"
            "函数内读取全局 tax_rate 但不修改；"
            "再定义函数 `promo_price(price)`：内部用局部变量 tax_rate = 0（免税促销）计算并返回，"
            "演示局部同名变量覆盖全局的现象。\n"
            "主程序：输入两个价格，分别调用两个函数输出结果，"
            "最后输出全局 tax_rate 是否被 promo_price 改变（应输出没变）。"
        ),
        "answer": (
            "# 全局配置与局部覆盖\n"
            "tax_rate = 0.1\n"
            "shop_name = \"阳光小卖部\"\n\n"
            "def calc_price(price):\n"
            "    # 只读取全局 tax_rate\n"
            "    return round(price * (1 + tax_rate), 2)\n\n"
            "def promo_price(price):\n"
            "    tax_rate = 0  # 局部变量，覆盖全局（仅在函数内）\n"
            "    return round(price * (1 + tax_rate), 2)\n\n"
            "p1 = float(input())\n"
            "p2 = float(input())\n"
            "print(shop_name + \" 价格\" + str(p1) + \" 含税价：\" + str(calc_price(p1)))\n"
            "print(shop_name + \" 价格\" + str(p2) + \" 含税价：\" + str(calc_price(p2)))\n"
            "print(\"促销价（免税）：\" + str(promo_price(p1)))\n"
            "print(\"促销价（免税）：\" + str(promo_price(p2)))\n"
            "print(\"全局 tax_rate 现在是：\" + str(tax_rate))\n"
            "if tax_rate == 0.1:\n"
            "    print(\"全局税率没被 promo_price 改变\")\n"
            "else:\n"
            "    print(\"全局税率被改了\")\n"
        ),
        "explanation": (
            "思路：calc_price 只读全局 tax_rate；promo_price 内部 tax_rate=0 创建的是局部变量，"
            "出了函数就消失，全局值不受影响；最后打印全局 tax_rate 验证。"
            "讲解：函数内「读」全局变量不需要 global，「赋值」才会创建局部变量；"
            "局部同名变量只在函数内生效，这种「覆盖」不会污染全局；"
            "全局变量适合放配置（税率、店名），函数内部逻辑用局部变量。"
        ),
        "sample_input": "10\n25.5\n",
    },
    {
        "topic_id": 59,
        "title": "L15-59-D lambda 裁判",
        "content": (
            "lambda 裁判。输入一行：若干空格分隔的整数（选手得分）。请用 lambda 完成："
            "①定义 square = lambda x: x*x，输出每个分数的平方；"
            "②定义 is_even = lambda x: x % 2 == 0，用 filter 筛出偶数分数；"
            "③定义 add = lambda a, b: a + b，用循环把分数累加（必须用 add 函数累加，不许直接 +）；"
            "④定义 describe = lambda x: '高分' if x >= 80 else '普通'，输出每个分数的标签；"
            "⑤输出总分、偶数分数列表、平方后的列表。"
        ),
        "answer": (
            "# lambda 裁判\n"
            "scores = []\n"
            "for token in input().split():\n"
            "    scores.append(int(token))\n"
            "print(\"原始分数：\" + str(scores))\n"
            "# 1. 平方\n"
            "square = lambda x: x * x\n"
            "squares = []\n"
            "for s in scores:\n"
            "    squares.append(square(s))\n"
            "print(\"平方后：\" + str(squares))\n"
            "# 2. 筛偶数\n"
            "is_even = lambda x: x % 2 == 0\n"
            "evens = list(filter(is_even, scores))\n"
            "print(\"偶数分数：\" + str(evens))\n"
            "# 3. 用 lambda 累加\n"
            "add = lambda a, b: a + b\n"
            "total = 0\n"
            "for s in scores:\n"
            "    total = add(total, s)\n"
            "print(\"总分：\" + str(total))\n"
            "# 4. 带 if 的 lambda 打标签\n"
            "describe = lambda x: \"高分\" if x >= 80 else \"普通\"\n"
            "for s in scores:\n"
            "    print(str(s) + \" -> \" + describe(s))\n"
        ),
        "explanation": (
            "思路：四个 lambda 分别做平方、判偶、加法、打标签；"
            "filter(is_even, scores) 直接用命名 lambda 筛选；"
            "describe 用「A if 条件 else B」的三元表达式在 lambda 里做分支。"
            "讲解：lambda 赋给变量后可以像函数一样反复调用；"
            "lambda 里写条件要用三元表达式，不能写 if 语句；"
            "filter/map/sorted 这些高阶函数是 lambda 的最佳搭档。"
        ),
        "sample_input": "85 60 92 77 40\n",
    },
    {
        "topic_id": 59,
        "title": "L15-59-E nonlocal 积分累计器",
        "content": (
            "nonlocal 积分累计器。请定义外层函数 `make_scorer(start)`，"
            "内部维护 total = start，并返回嵌套函数 `add_points(p)`：\n"
            "- 用 nonlocal 声明修改外层 total，累加 p\n"
            "- 返回当前 total\n"
            "主程序：读入第一行 start（初始积分），第二行若干得分（空格分隔）。"
            "创建 scorer = make_scorer(start)，对每个得分调用 scorer(p) 并输出「加X分后：Y」；"
            "再创建第二个 scorer2 = make_scorer(0)，加 100 分，输出两个累计器互不影响。"
        ),
        "answer": (
            "# nonlocal 积分累计器\n"
            "def make_scorer(start):\n"
            "    total = start\n"
            "    def add_points(p):\n"
            "        nonlocal total\n"
            "        total = total + p\n"
            "        return total\n"
            "    return add_points\n\n"
            "start = int(input())\n"
            "points = []\n"
            "for token in input().split():\n"
            "    points.append(int(token))\n"
            "scorer = make_scorer(start)\n"
            "for p in points:\n"
            "    result = scorer(p)\n"
            "    print(\"加\" + str(p) + \"分后：\" + str(result))\n"
            "# 第二个独立累计器\n"
            "scorer2 = make_scorer(0)\n"
            "print(\"新累计器加100分：\" + str(scorer2(100)))\n"
            "print(\"原累计器再加0分验证：\" + str(scorer(0)))\n"
            "print(\"两个累计器互不影响\")\n"
        ),
        "explanation": (
            "思路：make_scorer 的局部变量 total 被嵌套函数 add_points 用 nonlocal 捕获并修改；"
            "每次调用 make_scorer 都产生独立的 total，所以两个累计器互不干扰。"
            "讲解：nonlocal 用于修改「外层函数（非全局）」的变量，和 global 区分开；"
            "闭包 = 函数 + 它记住的外层变量，这里的 total 就是被记住的状态；"
            "调用 scorer(0) 不改变总分，可以用来查看当前值。"
        ),
        "sample_input": "10\n5 20 15\n",
    },

    # ===================== L16 / topic 60 lambda结合if判断、内置函数与拆包 =====================
    {
        "topic_id": 60,
        "title": "L16-60-A 成绩标签流水线",
        "content": (
            "成绩标签流水线。输入两行：第一行若干姓名，第二行对应分数。请完成："
            "①用 zip 配对；②用 map + 带 if 的 lambda 把每对变成字符串「姓名:等级」"
            "（>=90 优、>=60 合格、否则补考）；③用 filter + lambda 保留需要补考的项；"
            "④用 sorted + lambda 按等级排序（优在前）；⑤拆包输出：把第一个和最后一个学生分别用 a, b = ... 拆出并打印。"
        ),
        "answer": (
            "# 成绩标签流水线\n"
            "names = input().split()\n"
            "scores = []\n"
            "for token in input().split():\n"
            "    scores.append(int(token))\n"
            "pairs = list(zip(names, scores))\n"
            "# map + 带 if 的 lambda：生成标签\n"
            "label = lambda p: p[0] + \":\" + (\"优\" if p[1] >= 90 else (\"合格\" if p[1] >= 60 else \"补考\"))\n"
            "labels = list(map(label, pairs))\n"
            "print(\"标签：\" + str(labels))\n"
            "# filter：需要补考的\n"
            "retake = list(filter(lambda p: p[1] < 60, pairs))\n"
            "print(\"需要补考：\" + str(retake))\n"
            "# sorted：按分数降序\n"
            "ordered = sorted(pairs, key=lambda p: p[1], reverse=True)\n"
            "print(\"按分排序：\" + str(ordered))\n"
            "# 拆包：第一和最后\n"
            "first_name, first_score = ordered[0]\n"
            "last_name, last_score = ordered[-1]\n"
            "print(\"第一名：\" + first_name + \"（\" + str(first_score) + \"）\")\n"
            "print(\"最后一名：\" + last_name + \"（\" + str(last_score) + \"）\")\n"
        ),
        "explanation": (
            "思路：zip 配对→map 批量生成标签（lambda 内嵌套三元表达式分三档）→filter 筛补考→"
            "sorted 按分排序→对元组用「a, b = 元组」拆包。"
            "讲解：嵌套三元 (A if c1 else (B if c2 else C)) 可以实现多档分类，括号别漏；"
            "map 对每个元素加工、filter 按条件保留，两者都返回迭代器要 list() 化；"
            "拆包赋值让取元组元素更有语义。"
        ),
        "sample_input": "小明 小红 小刚 小美\n95 58 76 88\n",
    },
    {
        "topic_id": 60,
        "title": "L16-60-B 拆包传参计算器",
        "content": (
            "拆包传参计算器。请定义函数 `calc3(a, b, c)`，返回 (和, 积, 平均值) 元组。"
            "主程序：输入一行三个整数，先存成列表 nums；"
            "①用 * 拆包调用 calc3(*nums) 并拆包接收结果 s, p, avg；"
            "②输入第二行两个整数存成 pair，演示用 calc3(*pair, 0) 把两元素拆包再补一个 0 调用；"
            "③输入一行键值对风格的「x=数字 y=数字 z=数字」，解析后用关键字参数 calc3(a=x, b=y, c=z) 调用；"
            "输出三次调用的结果。"
        ),
        "answer": (
            "# 拆包传参计算器\n"
            "def calc3(a, b, c):\n"
            "    s = a + b + c\n"
            "    p = a * b * c\n"
            "    avg = round(s / 3, 1)\n"
            "    return (s, p, avg)\n\n"
            "# 1. 列表拆包\n"
            "nums = []\n"
            "for token in input().split():\n"
            "    nums.append(int(token))\n"
            "s, p, avg = calc3(*nums)\n"
            "print(\"三数：和\" + str(s) + \" 积\" + str(p) + \" 平均\" + str(avg))\n"
            "# 2. 两元素拆包 + 补 0\n"
            "pair = []\n"
            "for token in input().split():\n"
            "    pair.append(int(token))\n"
            "s2, p2, avg2 = calc3(*pair, 0)\n"
            "print(\"两数补0：和\" + str(s2) + \" 积\" + str(p2) + \" 平均\" + str(avg2))\n"
            "# 3. 解析 x=1 风格再用关键字参数\n"
            "kv = {}\n"
            "for token in input().split():\n"
            "    k, v = token.split(\"=\")\n"
            "    kv[k] = int(v)\n"
            "s3, p3, avg3 = calc3(a=kv[\"x\"], b=kv[\"y\"], c=kv[\"z\"])\n"
            "print(\"关键字调用：和\" + str(s3) + \" 积\" + str(p3) + \" 平均\" + str(avg3))\n"
        ),
        "explanation": (
            "思路：calc3(*nums) 把列表拆成三个位置参数；calc3(*pair, 0) 拆两个再补一个；"
            "第三段解析 x=1 形式的键值对存入字典，再用关键字参数调用。"
            "讲解：* 拆包可以和其他参数混用（*pair, 0）；"
            "关键字参数 a=值 与顺序无关，适合参数多的场景；"
            "函数返回元组时，左边也可以用拆包一次性接住。"
        ),
        "sample_input": "3 4 5\n7 8\nx=2 y=3 z=4\n",
    },
    {
        "topic_id": 60,
        "title": "L16-60-C 天气数据流水线",
        "content": (
            "天气数据流水线。输入两行：第一行 7 个星期缩写，第二行 7 个温度（整数）。请完成："
            "①zip 配对成列表；②用 map + lambda 把每对变成 (星期, 温度, 等级)，"
            "等级用带 if 的 lambda：>=30 热、>=20 舒适、否则凉；"
            "③用 filter + lambda 筛出「舒适」的日子；④用 max/min + lambda key 找最热和最冷的日子；"
            "⑤对最热那天用 d, t, level = ... 拆包输出一句话总结。"
        ),
        "answer": (
            "# 天气数据流水线\n"
            "days = input().split()\n"
            "temps = []\n"
            "for token in input().split():\n"
            "    temps.append(int(token))\n"
            "pairs = list(zip(days, temps))\n"
            "# map：加等级标签\n"
            "level = lambda t: \"热\" if t >= 30 else (\"舒适\" if t >= 20 else \"凉\")\n"
            "records = list(map(lambda p: (p[0], p[1], level(p[1])), pairs))\n"
            "print(\"带等级记录：\" + str(records))\n"
            "# filter：舒适的日子\n"
            "comfy = list(filter(lambda r: r[2] == \"舒适\", records))\n"
            "print(\"舒适的日子：\" + str(comfy))\n"
            "# 最热 / 最冷\n"
            "hottest = max(records, key=lambda r: r[1])\n"
            "coldest = min(records, key=lambda r: r[1])\n"
            "print(\"最热：\" + str(hottest))\n"
            "print(\"最冷：\" + str(coldest))\n"
            "# 拆包总结\n"
            "d, t, lv = hottest\n"
            "print(\"总结：\" + d + \" 最热，\" + str(t) + \" 度，感觉\" + lv)\n"
        ),
        "explanation": (
            "思路：zip 配对→map 生成三元组（lambda 内再调 lambda level 分档）→filter 按标签筛→"
            "max/min 用 key 指定按温度比较→最后对元组拆包输出。"
            "讲解：lambda 可以调用另一个 lambda（level(p[1])），实现组合；"
            "max(key=...) 返回的是元素本身而不是温度值；"
            "三元组 (星期, 温度, 等级) 比两个平行列表更好维护。"
        ),
        "sample_input": "Mon Tue Wed Thu Fri Sat Sun\n28 35 18 22 31 19 25\n",
    },
    {
        "topic_id": 60,
        "title": "L16-60-D 购物车折扣流水线",
        "content": (
            "购物车折扣流水线。内置商品表：[('牛奶', 12), ('面包', 8), ('饼干', 15), ('果汁', 10)]。"
            "输入一行：四个 0/1 数字（空格分隔），表示每种商品是否购买。请完成："
            "①用 zip 把商品表和购买标记配对；②用 filter + lambda 保留购买的商品；"
            "③用 map + lambda 给每件商品算折后价：价格大于 10 打九折，否则原价，生成 (名称, 折后价)；"
            "④用 sum + 生成器求总价（2 位小数）；⑤若总价超过 30，用带 if 的 lambda 输出「满30送贴纸」否则「谢谢惠顾」。"
        ),
        "answer": (
            "# 购物车折扣流水线\n"
            "goods = [(\"牛奶\", 12), (\"面包\", 8), (\"饼干\", 15), (\"果汁\", 10)]\n"
            "flags = []\n"
            "for token in input().split():\n"
            "    flags.append(int(token))\n"
            "# 1. 配对商品与购买标记\n"
            "combined = list(zip(goods, flags))\n"
            "# 2. 保留购买的\n"
            "bought = list(filter(lambda c: c[1] == 1, combined))\n"
            "# 3. 算折后价\n"
            "discount = lambda price: price * 0.9 if price > 10 else price\n"
            "priced = list(map(lambda c: (c[0][0], round(discount(c[0][1]), 2)), bought))\n"
            "print(\"购买清单：\" + str(priced))\n"
            "# 4. 总价\n"
            "total = round(sum(p for _, p in priced), 2)\n"
            "print(\"总价：\" + str(total) + \" 元\")\n"
            "# 5. 促销判断\n"
            "promo = lambda t: \"满30送贴纸\" if t > 30 else \"谢谢惠顾\"\n"
            "print(promo(total))\n"
        ),
        "explanation": (
            "思路：zip 把商品表和 0/1 标记配对；filter 按标记筛选；"
            "map 里用 discount lambda 算折后价（注意 c[0] 是商品元组，c[0][0] 是名称）；"
            "sum(p for _, p in priced) 用生成器表达式只取价格求和。"
            "讲解：嵌套结构里下标要看清：配对元素是 ((名称,价), 标记)；"
            "生成器表达式 (p for _, p in ...) 是「边遍历边取值」的简洁写法；"
            "_ 是约定俗成的「不用的变量」占位符。"
        ),
        "sample_input": "1 0 1 1\n",
    },
    {
        "topic_id": 60,
        "title": "L16-60-E 星级评价流水线",
        "content": (
            "星级评价流水线。输入两行：第一行若干商品名，第二行对应评分（0-10 的小数或整数）。"
            "请完成：①zip 配对；②用 map + lambda 把评分转成星数（评分//2，即每 2 分一星，lambda 内用 int 转换）；"
            "③生成 (商品, 星数) 列表并输出；④用 filter + lambda 保留 3 星及以上的商品；"
            "⑤用 sorted + lambda 按星数从高到低排序；⑥用 * 拆包把排序后列表的第一个元组解包为 name, stars，"
            "输出「最佳商品：name，stars星」。"
        ),
        "answer": (
            "# 星级评价流水线\n"
            "names = input().split()\n"
            "ratings = []\n"
            "for token in input().split():\n"
            "    ratings.append(float(token))\n"
            "pairs = list(zip(names, ratings))\n"
            "# 评分转星数：每 2 分一星\n"
            "to_stars = lambda r: int(r) // 2\n"
            "starred = list(map(lambda p: (p[0], to_stars(p[1])), pairs))\n"
            "print(\"星级表：\" + str(starred))\n"
            "# 保留 3 星及以上\n"
            "good = list(filter(lambda p: p[1] >= 3, starred))\n"
            "print(\"好评商品：\" + str(good))\n"
            "# 按星数排序\n"
            "ranked = sorted(starred, key=lambda p: p[1], reverse=True)\n"
            "print(\"排序后：\" + str(ranked))\n"
            "# 拆包输出最佳\n"
            "name, stars = ranked[0]\n"
            "print(\"最佳商品：\" + name + \"，\" + str(stars) + \"星\")\n"
            "low_name, low_stars = ranked[-1]\n"
            "print(\"待改进：\" + low_name + \"，\" + str(low_stars) + \"星\")\n"
        ),
        "explanation": (
            "思路：to_stars 用 int(r)//2 把评分转星数；map 生成 (商品,星数)；"
            "filter 筛好评；sorted 按星数降序；最后拆包取最佳和待改进。"
            "讲解：int(3.7)//2 先转整数再整除，避免小数干扰；"
            "map/filter/sorted 三件套可以串成「数据流水线」，每一步职责单一；"
            "拆包 name, stars = ranked[0] 比 ranked[0][0] 可读性好得多。"
        ),
        "sample_input": "牛奶 面包 饼干 果汁\n9.5 6 7.8 4\n",
    },
]
