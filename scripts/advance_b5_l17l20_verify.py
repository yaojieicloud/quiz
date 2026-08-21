"""批次5：L17-L20 (topic 61-64) 进阶题，每课 5 题，共 20 题。
主题与既有题（多列成绩单/参数拆包聚合器/安全除法器/健壮数据解析/计时装饰器/重试装饰器/装饰器栈演示/缓存装饰器）错开。
"""

QUESTIONS = [
    # ===================== L17 / topic 61 内置函数与拆包 =====================
    {
        "topic_id": 61,
        "title": "L17-61-A 购物清单汇总",
        "content": (
            "购物清单汇总。输入两行：第一行若干商品名（空格分隔），第二行对应价格（个数相同）。"
            "请完成：①zip 配对成 (商品, 价格) 列表；②用 enumerate 带序号输出每件商品；"
            "③用 sum + 生成器表达式求总价（2 位小数）；④用 any 判断是否有价格超过 50 的商品；"
            "⑤用 max/min + lambda key 找出最贵和最便宜的商品，并对最贵的用「名称, 价格 = ...」拆包输出。"
        ),
        "answer": (
            "# 购物清单汇总\n"
            "names = input().split()\n"
            "prices = []\n"
            "for token in input().split():\n"
            "    prices.append(float(token))\n"
            "pairs = list(zip(names, prices))\n"
            "print(\"商品与价格：\")\n"
            "for idx, item in enumerate(pairs, 1):\n"
            "    name, price = item\n"
            "    print(str(idx) + \". \" + name + \"：\" + str(price) + \" 元\")\n"
            "total = sum(p for _, p in pairs)\n"
            "print(\"总价：\" + str(round(total, 2)) + \" 元\")\n"
            "has_expensive = any(p > 50 for _, p in pairs)\n"
            "print(\"有超过50元的商品吗：\" + str(has_expensive))\n"
            "top_name, top_price = max(pairs, key=lambda x: x[1])\n"
            "cheapest = min(pairs, key=lambda x: x[1])\n"
            "print(\"最贵：\" + top_name + \"（\" + str(top_price) + \" 元）\")\n"
            "print(\"最便宜：\" + cheapest[0] + \"（\" + str(cheapest[1]) + \" 元）\")\n"
            "all_valid = all(p >= 0 for _, p in pairs)\n"
            "print(\"价格都合法吗：\" + str(all_valid))\n"
        ),
        "explanation": (
            "思路：zip 配对→enumerate 带序号遍历→sum(生成器) 求总价→any/all 做整体判断→"
            "max/min 配 lambda 找极值，max 的结果直接用「a, b = ...」拆包。"
            "讲解：enumerate(iter, 1) 让序号从 1 开始；"
            "any 是「存在一个就 True」，all 是「全部满足才 True」，后面跟生成器表达式最简洁；"
            "拆包赋值让「取元组两个元素」一行搞定。"
        ),
        "sample_input": "牛奶 面包 玩具车 饼干\n12.5 8 66 9.9\n",
    },
    {
        "topic_id": 61,
        "title": "L17-61-B 值日轮转表",
        "content": (
            "值日轮转表。第一行输入若干姓名（空格分隔），第二行输入轮转数 k。"
            "请完成：①用切片把前 k 个姓名移到队尾，实现轮转；"
            "②用 enumerate 从 1 开始编号输出轮转后的值日顺序；"
            "③把星期列表 ['周一','周二','周三','周四','周五','周六','周日'] 与轮转后姓名 zip 配对"
            "（人数不够 7 个就配到没有为止），输出每天的值日生；"
            "④用 * 拆包 print('全体', *names) 一次性打印所有姓名；⑤输出总人数和轮转数。"
        ),
        "answer": (
            "# 值日轮转表\n"
            "names = input().split()\n"
            "k = int(input())\n"
            "weekdays = [\"周一\", \"周二\", \"周三\", \"周四\", \"周五\", \"周六\", \"周日\"]\n"
            "# 轮转：前 k 个移到队尾\n"
            "k = k % len(names)\n"
            "rotated = names[k:] + names[:k]\n"
            "print(\"轮转后的值日顺序：\")\n"
            "for no, name in enumerate(rotated, 1):\n"
            "    print(\"第\" + str(no) + \"位：\" + name)\n"
            "# 和星期配对\n"
            "schedule = list(zip(weekdays, rotated))\n"
            "print(\"本周值日表：\")\n"
            "for day, name in schedule:\n"
            "    print(day + \" -> \" + name)\n"
            "# * 拆包一次性打印\n"
            "print(\"全体姓名：\", *names)\n"
            "print(\"总人数：\" + str(len(names)) + \"，轮转数：\" + str(k))\n"
        ),
        "explanation": (
            "思路：names[k:] + names[:k] 是列表轮转的经典切片写法；k 先对人数取余避免转一整圈；"
            "zip 会自动按较短的一方配对；print(*names) 用 * 把列表拆成多个参数。"
            "讲解：切片拼接实现轮转，不用一个个 append；"
            "zip 配对时若两边长度不同，多出来的部分自动忽略；"
            "* 在调用处是「拆开」，和定义处的 *args「收集」正好相反。"
        ),
        "sample_input": "小明 小红 小刚 小美 小华\n2\n",
    },
    {
        "topic_id": 61,
        "title": "L17-61-C 两组 PK 赛",
        "content": (
            "两组 PK 赛。输入两行：A 组和 B 组每轮得分（整数，个数相同，空格分隔）。"
            "请完成：①zip 配对逐轮比较，用 enumerate 输出「第X轮 a分 vs b分 -> A胜/B胜/平」；"
            "②统计 A 胜、B 胜、平局的轮数；③用列表推导式 + abs 算每轮分差，再用 max 找最大分差；"
            "④输出最终结果：胜轮多的一组获胜，相同则平局；⑤用 sum 分别输出两组总分。"
        ),
        "answer": (
            "# 两组 PK 赛\n"
            "a_scores = []\n"
            "for token in input().split():\n"
            "    a_scores.append(int(token))\n"
            "b_scores = []\n"
            "for token in input().split():\n"
            "    b_scores.append(int(token))\n"
            "a_win = 0\n"
            "b_win = 0\n"
            "tie = 0\n"
            "for idx, pair in enumerate(zip(a_scores, b_scores), 1):\n"
            "    a, b = pair\n"
            "    if a > b:\n"
            "        a_win = a_win + 1\n"
            "        mark = \"A胜\"\n"
            "    elif a < b:\n"
            "        b_win = b_win + 1\n"
            "        mark = \"B胜\"\n"
            "    else:\n"
            "        tie = tie + 1\n"
            "        mark = \"平\"\n"
            "    print(\"第\" + str(idx) + \"轮：\" + str(a) + \" vs \" + str(b) + \" -> \" + mark)\n"
            "diffs = [abs(a - b) for a, b in zip(a_scores, b_scores)]\n"
            "print(\"A胜\" + str(a_win) + \"轮，B胜\" + str(b_win) + \"轮，平\" + str(tie) + \"轮\")\n"
            "print(\"最大分差：\" + str(max(diffs)))\n"
            "if a_win > b_win:\n"
            "    print(\"最终获胜：A 组\")\n"
            "elif b_win > a_win:\n"
            "    print(\"最终获胜：B 组\")\n"
            "else:\n"
            "    print(\"最终结果：平局\")\n"
            "print(\"A组总分：\" + str(sum(a_scores)) + \"，B组总分：\" + str(sum(b_scores)))\n"
        ),
        "explanation": (
            "思路：zip 把两组分数配对，enumerate 带轮次遍历比较并计数；"
            "推导式 [abs(a-b) for a,b in zip(...)] 一次算出所有分差；最后按胜轮数定胜负。"
            "讲解：for idx, pair in enumerate(zip(...)) 是「序号+配对」的组合写法；"
            "推导式里也可以直接 for a, b in zip(...) 拆包；"
            "sum 直接对列表求和，比手写循环简洁。"
        ),
        "sample_input": "10 15 8 20\n12 9 8 18\n",
    },
    {
        "topic_id": 61,
        "title": "L17-61-D 双城气温对比",
        "content": (
            "双城气温对比。输入三行：第一行 7 个星期缩写，第二行城市A 的 7 个温度，第三行城市B 的 7 个温度。"
            "请完成：①用 zip 把 (星期, A温, B温) 配成三元组列表；"
            "②用 map + lambda 生成每天温差（A-B，可为负）；"
            "③用 enumerate 找出温差绝对值最大的那一天；"
            "④用 sum/len 计算平均温差（1 位小数）；⑤输出温差为正（A更热）的天数。"
        ),
        "answer": (
            "# 双城气温对比\n"
            "days = input().split()\n"
            "a_temps = []\n"
            "for token in input().split():\n"
            "    a_temps.append(int(token))\n"
            "b_temps = []\n"
            "for token in input().split():\n"
            "    b_temps.append(int(token))\n"
            "# 三元组配对\n"
            "records = list(zip(days, a_temps, b_temps))\n"
            "print(\"星期\\tA城\\tB城\")\n"
            "for d, a, b in records:\n"
            "    print(d + \"\\t\" + str(a) + \"\\t\" + str(b))\n"
            "# 温差\n"
            "diffs = list(map(lambda t: t[1] - t[2], records))\n"
            "print(\"每天温差(A-B)：\" + str(diffs))\n"
            "# 温差绝对值最大的一天\n"
            "big_idx = 0\n"
            "for idx, diff in enumerate(diffs):\n"
            "    if abs(diff) > abs(diffs[big_idx]):\n"
            "        big_idx = idx\n"
            "print(\"温差最大：\" + days[big_idx] + \"（\" + str(diffs[big_idx]) + \" 度）\")\n"
            "avg_diff = sum(diffs) / len(diffs)\n"
            "print(\"平均温差：\" + str(round(avg_diff, 1)))\n"
            "a_hotter = len([d for d in diffs if d > 0])\n"
            "print(\"A城更热的天数：\" + str(a_hotter))\n"
        ),
        "explanation": (
            "思路：zip 支持两个以上列表配对成三元组；map+lambda 批量算温差；"
            "enumerate 遍历找绝对值最大的下标；正温差计数用带条件的列表推导式。"
            "讲解：zip(三个列表) 得到 (a,b,c) 三元组，遍历时可直接 for d, a, b in 拆包；"
            "\\t 制表符让多列数据对齐；"
            "len([x for x in ... if ...]) 是「计数满足条件元素」的常用写法。"
        ),
        "sample_input": "Mon Tue Wed Thu Fri Sat Sun\n28 30 26 24 27 31 29\n25 32 26 20 28 30 27\n",
    },
    {
        "topic_id": 61,
        "title": "L17-61-E 拆包统计站",
        "content": (
            "拆包统计站。请定义函数 `stats(*nums)`，用可变参数接收任意多个数字，"
            "返回 (总和, 平均值, 最大值, 最小值) 元组（平均值保留 2 位小数）。\n"
            "主程序：输入一行若干整数。①存入列表后用 stats(*列表) 拆包调用，结果也用拆包接收；"
            "②对列表做「first, *middle, last = 列表」拆包，分别输出第一个、中间列表、最后一个；"
            "③输出中间部分的和；④把列表倒序后重复一次 stats 调用，验证结果不变。"
        ),
        "answer": (
            "# 拆包统计站\n"
            "def stats(*nums):\n"
            "    total = sum(nums)\n"
            "    avg = round(total / len(nums), 2)\n"
            "    return total, avg, max(nums), min(nums)\n\n"
            "nums = []\n"
            "for token in input().split():\n"
            "    nums.append(int(token))\n"
            "# 拆包调用 + 拆包接收\n"
            "t, avg, mx, mn = stats(*nums)\n"
            "print(\"数字：\" + str(nums))\n"
            "print(\"总和：\" + str(t) + \" 平均：\" + str(avg))\n"
            "print(\"最大：\" + str(mx) + \" 最小：\" + str(mn))\n"
            "# 序列拆包：首、中、尾\n"
            "first, *middle, last = nums\n"
            "print(\"第一个：\" + str(first))\n"
            "print(\"中间：\" + str(middle))\n"
            "print(\"最后一个：\" + str(last))\n"
            "print(\"中间部分的和：\" + str(sum(middle)))\n"
            "# 倒序再验证\n"
            "reversed_nums = nums[::-1]\n"
            "t2, avg2, mx2, mn2 = stats(*reversed_nums)\n"
            "print(\"倒序后统计一致吗：\" + str((t, mx, mn) == (t2, mx2, mn2)))\n"
        ),
        "explanation": (
            "思路：stats(*nums) 收集可变参数；调用时 stats(*列表) 拆开传入；"
            "first, *middle, last 是「带星号拆包」，middle 收集中间所有元素成列表；"
            "nums[::-1] 切片倒序后重新统计验证。"
            "讲解：拆包可以带一个 * 收集「剩余部分」，位置可在前/中/后；"
            "函数返回元组时左边拆包接收，一一对应；"
            "顺序不影响总和/最值，这个验证能加深对「聚合与顺序无关」的理解。"
        ),
        "sample_input": "8 15 3 27 9\n",
    },

    # ===================== L18 / topic 62 异常模块与包 =====================
    {
        "topic_id": 62,
        "title": "L18-62-A 安全计算站",
        "content": (
            "安全计算站。连续读入若干行算式，格式为「a 运算符 b」（运算符用 + - x /），"
            "输入 end 结束。对每行用 try 处理："
            "①split 后把 a、b 转 int（失败捕获 ValueError）；②按运算符计算（/ 用浮点除）；"
            "③除零捕获 ZeroDivisionError；④运算符不认识时主动 raise ValueError 并捕获；"
            "成功的用 else 分支输出结果（2 位小数），最后输出成功和失败次数。"
        ),
        "answer": (
            "# 安全计算站\n"
            "ok_count = 0\n"
            "bad_count = 0\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    try:\n"
            "        a_str, op, b_str = line.split()\n"
            "        a = int(a_str)\n"
            "        b = int(b_str)\n"
            "        if op == \"+\":\n"
            "            result = a + b\n"
            "        elif op == \"-\":\n"
            "            result = a - b\n"
            "        elif op == \"x\":\n"
            "            result = a * b\n"
            "        elif op == \"/\":\n"
            "            result = a / b\n"
            "        else:\n"
            "            raise ValueError(\"未知运算符 \" + op)\n"
            "    except ZeroDivisionError:\n"
            "        print(\"除零错误：\" + line)\n"
            "        bad_count = bad_count + 1\n"
            "    except ValueError as e:\n"
            "        print(\"格式错误：\" + line + \"（\" + str(e) + \"）\")\n"
            "        bad_count = bad_count + 1\n"
            "    else:\n"
            "        print(line + \" = \" + str(round(result, 2)))\n"
            "        ok_count = ok_count + 1\n"
            "print(\"成功 \" + str(ok_count) + \" 次，失败 \" + str(bad_count) + \" 次\")\n"
        ),
        "explanation": (
            "思路：整个解析+计算放在 try 里，按异常类型分别 except；"
            "遇到不认识的运算符用 raise ValueError 主动抛错，让错误处理统一走 except；"
            "else 分支只在没出异常时执行，输出结果。"
            "讲解：try/except/else 结构中 else 表示「一切顺利时做什么」；"
            "raise 可以主动制造异常，配合 except 统一处理；"
            "except ValueError as e 能拿到错误信息用于提示。"
        ),
        "sample_input": "3 + 4\n10 / 0\n5 x 6\n2 ? 3\nabc + 1\nend\n",
    },
    {
        "topic_id": 62,
        "title": "L18-62-B 数学工具箱",
        "content": (
            "数学工具箱。第一行输入 n，接下来 n 行每行一个小数（保证为正数）。请用模块完成："
            "①from math import floor, ceil, sqrt；②对每个数输出向下取整、向上取整、平方根（2 位小数）；"
            "③用总和除以个数再对 100 取余加 1，算出一个 1-100 的「幸运数字」并输出；"
            "④计算所有数的和与平均值（2 位小数）；⑤输出最大数和最小数。"
        ),
        "answer": (
            "# 数学工具箱\n"
            "from math import floor, ceil, sqrt\n\n"
            "n = int(input())\n"
            "nums = []\n"
            "i = 0\n"
            "while i < n:\n"
            "    nums.append(float(input()))\n"
            "    i = i + 1\n"
            "print(\"数字列表：\" + str(nums))\n"
            "for x in nums:\n"
            "    print(str(x) + \" -> 向下取整 \" + str(floor(x)) + \"，向上取整 \" + str(ceil(x)) + \"，平方根 \" + str(round(sqrt(x), 2)))\n"
            "total = 0\n"
            "for x in nums:\n"
            "    total = total + x\n"
            "avg = total / n\n"
            "print(\"和：\" + str(round(total, 2)) + \"，平均：\" + str(round(avg, 2)))\n"
            "print(\"最大：\" + str(max(nums)) + \"，最小：\" + str(min(nums)))\n"
            "# 由数据算出的「幸运数字」（1-100）\n"
            "lucky = int(total) % 100 + 1\n"
            "print(\"幸运数字：\" + str(lucky))\n"
        ),
        "explanation": (
            "思路：from math import ... 只导入要用的函数；floor 向下取整、ceil 向上取整、sqrt 开平方；"
            "幸运数字用 int(总和)%100+1 算出，保证落在 1-100；统计用循环累加和 max/min。"
            "讲解：模块是 Python 的「工具箱」，math 是标准库自带的；"
            "import 整个模块要用 模块名.函数()，from 导入后可直接写函数名；"
            "%100+1 是把任意整数「收拢」到 1-100 范围的常用技巧。"
        ),
        "sample_input": "3\n3.7\n16\n8.2\n",
    },
    {
        "topic_id": 62,
        "title": "L18-62-C 年龄验证器",
        "content": (
            "年龄验证器（自定义异常）。请定义 `class InvalidAgeError(Exception)`。\n"
            "连续读入若干行「姓名 年龄」，输入 end 结束。对每行："
            "①split 后年龄 int() 转换（失败捕获 ValueError，记入 errors）；"
            "②年龄小于 0 或大于 150 时 raise InvalidAgeError 并捕获，记入 errors；"
            "③合法则加入 records 列表。结束后输出有效记录、错误明细；"
            "若有有效记录，输出平均年龄（1 位小数）和最大年龄者姓名。"
        ),
        "answer": (
            "# 年龄验证器（自定义异常）\n"
            "class InvalidAgeError(Exception):\n"
            "    pass\n\n"
            "records = []\n"
            "errors = []\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    name = \"\"\n"
            "    try:\n"
            "        name, age_str = line.split()\n"
            "        age = int(age_str)\n"
            "        if age < 0 or age > 150:\n"
            "            raise InvalidAgeError(\"年龄 \" + str(age) + \" 不合理\")\n"
            "    except ValueError:\n"
            "        errors.append(line + \"：年龄不是数字\")\n"
            "        continue\n"
            "    except InvalidAgeError as e:\n"
            "        errors.append(name + \"：\" + str(e))\n"
            "        continue\n"
            "    records.append((name, age))\n"
            "print(\"有效记录：\" + str(records))\n"
            "print(\"错误明细：\" + str(errors))\n"
            "if records:\n"
            "    ages = [a for _, a in records]\n"
            "    print(\"平均年龄：\" + str(round(sum(ages) / len(ages), 1)))\n"
            "    oldest = max(records, key=lambda r: r[1])\n"
            "    print(\"年龄最大：\" + oldest[0] + \"（\" + str(oldest[1]) + \" 岁）\")\n"
            "else:\n"
            "    print(\"没有有效记录\")\n"
        ),
        "explanation": (
            "思路：自定义异常类只需继承 Exception；业务规则（年龄范围）不满足就 raise 自己的异常，"
            "和「格式错误」的 ValueError 分开捕获，错误信息更清晰；continue 跳过坏数据继续处理。"
            "讲解：自定义异常让「业务错误」和「语法/转换错误」区分开；"
            "raise 后当前 try 立刻中断，跳到对应 except；"
            "errors 列表收集所有问题，最后统一汇报是数据清洗的常见模式。"
        ),
        "sample_input": "小明 10\n小红 abc\n小刚 200\n小美 12\nend\n",
    },
    {
        "topic_id": 62,
        "title": "L18-62-D try 四件套演示",
        "content": (
            "try 四件套演示。连续读入若干行，每行一个整数（表示得分），输入 end 结束。"
            "请用完整的 try/except/else/finally 结构处理每一行："
            "①try 里转 int 并累加到总分、计数加一；②except ValueError 捕获坏数据并记录；"
            "③else 输出「本条有效，当前总分 X」；④finally 每次输出「---第N条处理完毕」。"
            "全部结束后输出：有效条数、坏数据条数、总分、平均分（1 位小数，若无有效数据输出 0）。"
        ),
        "answer": (
            "# try/except/else/finally 四件套\n"
            "total = 0\n"
            "ok_count = 0\n"
            "bad_count = 0\n"
            "no = 0\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    no = no + 1\n"
            "    try:\n"
            "        score = int(line)\n"
            "        total = total + score\n"
            "        ok_count = ok_count + 1\n"
            "    except ValueError:\n"
            "        bad_count = bad_count + 1\n"
            "        print(\"坏数据：\" + line)\n"
            "    else:\n"
            "        print(\"本条有效，当前总分 \" + str(total))\n"
            "    finally:\n"
            "        print(\"---第\" + str(no) + \"条处理完毕\")\n"
            "print(\"有效 \" + str(ok_count) + \" 条，坏数据 \" + str(bad_count) + \" 条\")\n"
            "print(\"总分：\" + str(total))\n"
            "if ok_count > 0:\n"
            "    print(\"平均分：\" + str(round(total / ok_count, 1)))\n"
            "else:\n"
            "    print(\"平均分：0\")\n"
        ),
        "explanation": (
            "思路：try 做转换和累加；except 捕坏数据；else 在成功时输出当前总分；"
            "finally 无论成败都输出分隔线，演示四者执行顺序；最后汇总并防除零。"
            "讲解：finally 里的代码「无论如何都会执行」，适合做收尾（打印分隔、关闭资源）；"
            "执行顺序是 try → (except 或 else) → finally；"
            "平均分计算前判断 ok_count>0，避免除零异常。"
        ),
        "sample_input": "85\nabc\n90\n70\nend\n",
    },
    {
        "topic_id": 62,
        "title": "L18-62-E 最大公约数计算器",
        "content": (
            "最大公约数计算器。用 from math import gcd 导入最大公约数函数。"
            "连续读入若干行「a b」，输入 end 结束。对每行："
            "①用 gcd(a, b) 求最大公约数；②用「a×b÷最大公约数」求最小公倍数（整除）；"
            "③输出结果；④记录最小公倍数最大的那一对；⑤结束后输出共计算了几对、"
            "最小公倍数最大的一对及其值；若某行格式错误（非两个整数），用 try/except 捕获并提示。"
        ),
        "answer": (
            "# 最大公约数与最小公倍数\n"
            "from math import gcd\n\n"
            "count = 0\n"
            "best_pair = None\n"
            "best_lcm = -1\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    try:\n"
            "        a, b = map(int, line.split())\n"
            "    except ValueError:\n"
            "        print(\"格式错误：\" + line)\n"
            "        continue\n"
            "    g = gcd(a, b)\n"
            "    lcm = a * b // g\n"
            "    count = count + 1\n"
            "    print(str(a) + \" 和 \" + str(b) + \"：最大公约数 \" + str(g) + \"，最小公倍数 \" + str(lcm))\n"
            "    if lcm > best_lcm:\n"
            "        best_lcm = lcm\n"
            "        best_pair = (a, b)\n"
            "print(\"共计算 \" + str(count) + \" 对\")\n"
            "if best_pair is not None:\n"
            "    print(\"最小公倍数最大的一对：\" + str(best_pair) + \"，值为 \" + str(best_lcm))\n"
            "else:\n"
            "    print(\"没有有效数据\")\n"
        ),
        "explanation": (
            "思路：gcd 由 math 模块提供；最小公倍数 = a*b//gcd；try 包住输入解析，"
            "坏数据 continue 跳过；用 best_pair/best_lcm 打擂台记录最大的一对。"
            "讲解：from math import gcd 后可以不加模块前缀直接用；"
            "公式「最小公倍数 = 两数乘积 ÷ 最大公约数」要用整除 //；"
            "best_pair 初始为 None，用 is not None 判断是否有有效数据。"
        ),
        "sample_input": "12 18\n4 6\n7 5\nxx yy\nend\n",
    },

    # ===================== L19 / topic 63 闭包与装饰器 =====================
    {
        "topic_id": 63,
        "title": "L19-63-A 小银行（闭包账户）",
        "content": (
            "小银行（闭包账户）。请定义外层函数 `make_account(name)`，内部维护 balance = 0，"
            "返回三个嵌套函数组成的元组 (deposit, withdraw, query)："
            "deposit(amount) 存钱并返回余额；withdraw(amount) 取钱，余额不足返回 -1 否则返回余额；"
            "query() 返回当前余额。\n"
            "主程序：输入账户名，然后读入若干行指令「in 金额」或「out 金额」，输入 end 结束；"
            "每条指令调用对应函数并输出「存/取X元后余额Y」或「余额不足」；最后输出账户总结。"
        ),
        "answer": (
            "# 小银行：闭包账户\n"
            "def make_account(name):\n"
            "    balance = 0\n"
            "    def deposit(amount):\n"
            "        nonlocal balance\n"
            "        balance = balance + amount\n"
            "        return balance\n"
            "    def withdraw(amount):\n"
            "        nonlocal balance\n"
            "        if amount > balance:\n"
            "            return -1\n"
            "        balance = balance - amount\n"
            "        return balance\n"
            "    def query():\n"
            "        return balance\n"
            "    return deposit, withdraw, query\n\n"
            "owner = input()\n"
            "deposit, withdraw, query = make_account(owner)\n"
            "print(owner + \" 的账户已开通\")\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    action, amount_str = line.split()\n"
            "    amount = int(amount_str)\n"
            "    if action == \"in\":\n"
            "        balance = deposit(amount)\n"
            "        print(\"存\" + str(amount) + \"元后余额：\" + str(balance))\n"
            "    else:\n"
            "        balance = withdraw(amount)\n"
            "        if balance == -1:\n"
            "            print(\"余额不足，无法取\" + str(amount) + \"元\")\n"
            "        else:\n"
            "            print(\"取\" + str(amount) + \"元后余额：\" + str(balance))\n"
            "print(\"账户总结：\" + owner + \" 最终余额 \" + str(query()) + \" 元\")\n"
        ),
        "explanation": (
            "思路：make_account 的局部变量 balance 被三个嵌套函数用 nonlocal 共享；"
            "返回三个函数组成的元组，调用方拆包使用；余额状态「藏」在闭包里，外部无法直接改。"
            "讲解：闭包 = 函数 + 它记住的外层变量，这里 balance 就是账户状态；"
            "每次调用 make_account 都会产生独立的 balance，天然支持多账户；"
            "用函数而不是全局变量管理状态，更安全也更清晰。"
        ),
        "sample_input": "小明\nin 100\nout 30\nout 200\nin 50\nend\n",
    },
    {
        "topic_id": 63,
        "title": "L19-63-B 问候语工厂（闭包）",
        "content": (
            "问候语工厂（闭包）。请定义外层函数 `make_greeter(prefix, suffix)`，"
            "返回嵌套函数 `greet(name)`，它用外层的 prefix 和 suffix 拼出「prefix + name + suffix」。\n"
            "主程序：读入两行，每行「前缀 后缀」，分别创建两个 greeter；"
            "然后读入若干姓名，输入 end 结束，对每个姓名分别用两个 greeter 问候并输出；"
            "最后说明两个 greeter 各自记住不同的前后缀（输出各自的示例）。"
        ),
        "answer": (
            "# 问候语工厂\n"
            "def make_greeter(prefix, suffix):\n"
            "    def greet(name):\n"
            "        return prefix + name + suffix\n"
            "    return greet\n\n"
            "p1, s1 = input().split()\n"
            "p2, s2 = input().split()\n"
            "greeter1 = make_greeter(p1, s1)\n"
            "greeter2 = make_greeter(p2, s2)\n"
            "while True:\n"
            "    name = input()\n"
            "    if name == \"end\":\n"
            "        break\n"
            "    print(\"风格1：\" + greeter1(name))\n"
            "    print(\"风格2：\" + greeter2(name))\n"
            "print(\"greeter1 示例：\" + greeter1(\"朋友\"))\n"
            "print(\"greeter2 示例：\" + greeter2(\"朋友\"))\n"
            "print(\"两个 greeter 记住了各自的前后缀，互不影响\")\n"
        ),
        "explanation": (
            "思路：make_greeter 把 prefix/suffix 「装进」返回的 greet 函数里；"
            "两次调用 make_greeter 生成两个记住不同配置的 greeter；对同一姓名输出两种风格。"
            "讲解：闭包让函数「携带配置」，像工厂生产不同型号的产品；"
            "greet 没有定义 prefix 参数却能使用它，因为闭包捕获了外层变量；"
            "这种模式适合「同一逻辑、不同配置」的场景。"
        ),
        "sample_input": "你好， ！\n欢迎回来， ~\n小明\n小红\nend\n",
    },
    {
        "topic_id": 63,
        "title": "L19-63-C 调用计数器（闭包装饰器）",
        "content": (
            "调用计数器（闭包装饰器）。请定义装饰器 `count_calls(func)`：\n"
            "- 用闭包变量 count 记录被装饰函数的调用次数（nonlocal）；\n"
            "- 每次调用先 count+1，打印「函数名 第X次调用」，再执行并返回原结果；\n"
            "- 用 functools.wraps 保留原函数名。\n"
            "被装饰函数 `square(n)` 返回 n 的平方。主程序：读入若干整数，输入 end 结束；"
            "对每个数调用 square 并输出结果；最后再调用一次 square(0) 展示总调用次数。"
        ),
        "answer": (
            "# 调用计数器装饰器\n"
            "from functools import wraps\n\n"
            "def count_calls(func):\n"
            "    count = 0\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        nonlocal count\n"
            "        count = count + 1\n"
            "        print(func.__name__ + \" 第\" + str(count) + \"次调用\")\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n\n"
            "@count_calls\n"
            "def square(n):\n"
            "    return n * n\n\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    n = int(line)\n"
            "    print(\"  结果：\" + str(square(n)))\n"
            "print(\"最后再调用一次：\")\n"
            "print(\"  结果：\" + str(square(0)))\n"
            "print(\"函数名仍为：\" + square.__name__)\n"
        ),
        "explanation": (
            "思路：count_calls 的闭包变量 count 被 wrapper 用 nonlocal 修改，实现跨调用记忆；"
            "@count_calls 等价于 square = count_calls(square)；@wraps 保留原函数名。"
            "讲解：装饰器本质是「接收函数、返回新函数」的闭包；"
            "nonlocal count 让次数在多次调用间累积，这正是闭包保存状态的用途；"
            "*args, **kwargs 透传让装饰器适用于任何参数的函数。"
        ),
        "sample_input": "3\n5\n8\nend\n",
    },
    {
        "topic_id": 63,
        "title": "L19-63-D 范围检查装饰器",
        "content": (
            "范围检查装饰器。请定义装饰器 `check_range(func)`：调用前检查所有位置参数是否都在 0-100 之间，"
            "若有任何一个越界，打印「参数越界：参数列表」并直接返回 None，不执行原函数；"
            "否则正常执行并返回结果。用 functools.wraps 保留元信息。\n"
            "被装饰函数 `grade_report(name, score)` 返回「name：score分」。\n"
            "主程序：读入若干行「姓名 分数」，输入 end 结束，逐行调用 grade_report；"
            "若返回 None 输出「该条记录被拦截」，否则输出返回值。"
        ),
        "answer": (
            "# 范围检查装饰器\n"
            "from functools import wraps\n\n"
            "def check_range(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        for value in args:\n"
            "            if isinstance(value, int) and (value < 0 or value > 100):\n"
            "                print(\"参数越界：\" + str(args))\n"
            "                return None\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n\n"
            "@check_range\n"
            "def grade_report(name, score):\n"
            "    return name + \"：\" + str(score) + \"分\"\n\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    name, score_str = line.split()\n"
            "    result = grade_report(name, int(score_str))\n"
            "    if result is None:\n"
            "        print(\"该条记录被拦截\")\n"
            "    else:\n"
            "        print(result)\n"
        ),
        "explanation": (
            "思路：wrapper 先遍历 args，发现 int 类型且越界的就拦截返回 None；"
            "isinstance(value, int) 保证只检查数字参数（姓名是字符串不受影响）；"
            "主程序根据返回值是否为 None 判断是否被拦截。"
            "讲解：装饰器做「前置检查」非常典型：参数校验、权限检查都属于这类；"
            "返回 None 作为拦截信号时，调用方要用 is None 判断；"
            "把校验逻辑抽到装饰器里，业务函数 grade_report 保持干净。"
        ),
        "sample_input": "小明 85\n小红 120\n小刚 -5\n小美 60\nend\n",
    },
    {
        "topic_id": 63,
        "title": "L19-63-E 结果翻倍装饰器",
        "content": (
            "结果翻倍装饰器。请定义装饰器 `double_result(func)`：调用原函数后把返回值乘 2 再返回，"
            "并打印「原结果X -> 翻倍后Y」。用 functools.wraps 保留元信息。\n"
            "被装饰函数：`add(a, b)` 返回 a+b；`length_of(s)` 返回字符串长度。\n"
            "主程序：读入两行整数调用 add（输出翻倍后结果）；再读入一行文字调用 length_of"
            "（输出长度翻倍结果）；最后输出「装饰器让同样的函数返回双倍结果，而函数本身没改」。"
        ),
        "answer": (
            "# 结果翻倍装饰器\n"
            "from functools import wraps\n\n"
            "def double_result(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        original = func(*args, **kwargs)\n"
            "        doubled = original * 2\n"
            "        print(\"原结果\" + str(original) + \" -> 翻倍后\" + str(doubled))\n"
            "        return doubled\n"
            "    return wrapper\n\n"
            "@double_result\n"
            "def add(a, b):\n"
            "    return a + b\n\n"
            "@double_result\n"
            "def length_of(s):\n"
            "    return len(s)\n\n"
            "a = int(input())\n"
            "b = int(input())\n"
            "print(\"add(\" + str(a) + \",\" + str(b) + \") 最终返回：\" + str(add(a, b)))\n"
            "text = input()\n"
            "print(\"length_of 最终返回：\" + str(length_of(text)))\n"
            "print(\"装饰器让同样的函数返回双倍结果，而函数本身没改\")\n"
        ),
        "explanation": (
            "思路：wrapper 先拿到原函数结果 original，再返回 original*2，实现「后置加工」；"
            "同一个装饰器同时用在 add 和 length_of 上，体现复用性；"
            "主程序像平常一样调用，完全感知不到翻倍逻辑的存在。"
            "讲解：装饰器可以「前置检查」也可以「后置加工」，这题是后者；"
            "函数定义没有任何改动，增强全靠装饰器——这就是装饰器的价值；"
            "对数字是乘 2，对字符串会是重复两遍，这里 length_of 返回数字所以是乘 2。"
        ),
        "sample_input": "3\n4\n你好世界\n",
    },

    # ===================== L20 / topic 64 标准版装饰器与语法糖 =====================
    {
        "topic_id": 64,
        "title": "L20-64-A 输出美化装饰器",
        "content": (
            "输出美化装饰器。请定义装饰器 `banner(func)`：在被装饰函数执行前后各打印一行边框："
            "「==== 函数名 开始 ====」和「==== 函数名 结束 ====」，中间执行原函数并返回结果。"
            "用 @wraps 保留函数名。\n"
            "被装饰函数 `intro(name, age)` 打印两行自我介绍并返回名字。\n"
            "主程序：读入一行「姓名 年龄」，调用 intro；再读入一行，第二次调用；"
            "最后输出两次调用返回的名字，验证装饰器不影响返回值。"
        ),
        "answer": (
            "# 输出美化装饰器\n"
            "from functools import wraps\n\n"
            "def banner(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(\"==== \" + func.__name__ + \" 开始 ====\")\n"
            "        result = func(*args, **kwargs)\n"
            "        print(\"==== \" + func.__name__ + \" 结束 ====\")\n"
            "        return result\n"
            "    return wrapper\n\n"
            "@banner\n"
            "def intro(name, age):\n"
            "    print(\"大家好，我叫\" + name)\n"
            "    print(\"今年\" + str(age) + \"岁\")\n"
            "    return name\n\n"
            "name1, age1 = input().split()\n"
            "r1 = intro(name1, int(age1))\n"
            "name2, age2 = input().split()\n"
            "r2 = intro(name2, int(age2))\n"
            "print(\"两次调用返回：\" + r1 + \"、\" + r2)\n"
            "print(\"装饰器只加了边框，没有改变返回值\")\n"
        ),
        "explanation": (
            "思路：banner 在调用原函数前后各打一行边框，中间 result = func(...) 保存结果并原样返回；"
            "@banner 是语法糖，等价于 intro = banner(intro)；@wraps 让 func.__name__ 仍是原名。"
            "讲解：「@装饰器」写在 def 上方就是语法糖，比手写 intro = banner(intro) 直观；"
            "装饰器要返回原函数的结果，否则会「吞掉」返回值；"
            "边框、日志、分隔线这类输出增强是装饰器最常见的练手场景。"
        ),
        "sample_input": "小明 10\n小红 11\n",
    },
    {
        "topic_id": 64,
        "title": "L20-64-B 类型检查装饰器",
        "content": (
            "类型检查装饰器。请定义装饰器 `ensure_int(func)`：检查所有位置参数，"
            "若存在不是 int 类型的参数，打印「类型错误：期望整数，得到 X(类型)」并返回 None；"
            "否则执行原函数。用 @wraps 保留元信息。\n"
            "被装饰函数 `area(width, height)` 返回宽×高的面积。\n"
            "主程序：先用两个整数调用并输出面积；再用「整数+小数」调用演示拦截；"
            "再用「整数+字符串」调用演示拦截；最后说明装饰器在函数执行前守住了类型关。"
        ),
        "answer": (
            "# 类型检查装饰器\n"
            "from functools import wraps\n\n"
            "def ensure_int(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        for value in args:\n"
            "            if not isinstance(value, int):\n"
            "                print(\"类型错误：期望整数，得到 \" + repr(value) + \"(\" + str(type(value)) + \")\")\n"
            "                return None\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n\n"
            "@ensure_int\n"
            "def area(width, height):\n"
            "    return width * height\n\n"
            "print(\"正常调用：\")\n"
            "print(\"  面积 = \" + str(area(5, 8)))\n"
            "print(\"小数参数调用：\")\n"
            "result = area(5, 2.5)\n"
            "print(\"  返回：\" + str(result))\n"
            "print(\"字符串参数调用：\")\n"
            "result = area(5, \"八\")\n"
            "print(\"  返回：\" + str(result))\n"
            "print(\"装饰器在函数执行前守住了类型关\")\n"
        ),
        "explanation": (
            "思路：ensure_int 遍历 args 用 isinstance 检查类型，发现非 int 立刻拦截返回 None；"
            "repr(value) 显示值（字符串会带引号），type(value) 显示类型；"
            "主程序三次调用分别演示通过与两种拦截。"
            "讲解：isinstance(x, int) 是判断类型的标准做法；"
            "装饰器做前置校验可以让业务函数假设「参数一定合法」，逻辑更简单；"
            "被拦截时返回 None，调用方要能识别这种情况。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 64,
        "title": "L20-64-C 装饰器叠加顺序",
        "content": (
            "装饰器叠加顺序。请定义两个装饰器："
            "`first(func)` 打印「first 外层开始」→执行→打印「first 外层结束」；"
            "`second(func)` 打印「second 内层开始」→执行→打印「second 内层结束」。\n"
            "把两者叠加到函数 `say_hello(name)`（打印「你好，name」）上：@first 在上、@second 在下。\n"
            "主程序：读入一个姓名调用 say_hello；观察输出顺序，总结「装饰从下往上包、执行从上往下进」；"
            "再调用一次验证顺序稳定，并输出函数名（@wraps 保留）。"
        ),
        "answer": (
            "# 装饰器叠加顺序\n"
            "from functools import wraps\n\n"
            "def first(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(\"first 外层开始\")\n"
            "        result = func(*args, **kwargs)\n"
            "        print(\"first 外层结束\")\n"
            "        return result\n"
            "    return wrapper\n\n"
            "def second(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(\"second 内层开始\")\n"
            "        result = func(*args, **kwargs)\n"
            "        print(\"second 内层结束\")\n"
            "        return result\n"
            "    return wrapper\n\n"
            "@first\n"
            "@second\n"
            "def say_hello(name):\n"
            "    print(\"你好，\" + name)\n\n"
            "name = input()\n"
            "say_hello(name)\n"
            "print(\"顺序：first 先包在最外层，执行时最先进、最后出\")\n"
            "print(\"再调用一次验证：\")\n"
            "say_hello(name)\n"
            "print(\"函数名保留：\" + say_hello.__name__)\n"
        ),
        "explanation": (
            "思路：@first @second 叠加等价于 say_hello = first(second(say_hello))；"
            "执行时先走 first 的 wrapper（打印 first 开始），再进 second 的 wrapper，最后到原函数；"
            "返回时按相反顺序收尾，像套娃一样。"
            "讲解：装饰器「应用顺序从下往上」（second 先被包），「执行顺序从上往下」（first 先执行）；"
            "每层 @wraps 都要写，函数名才能一路保留；"
            "理解叠加顺序对日志、权限、缓存的组合使用很重要。"
        ),
        "sample_input": "小明\n",
    },
    {
        "topic_id": 64,
        "title": "L20-64-D 权限检查装饰器（参数化）",
        "content": (
            "权限检查装饰器（参数化）。请定义参数化装饰器 `require_role(role)`：\n"
            "- 外层接收要求的角色 role，返回真正的装饰器 deco；\n"
            "- deco 装饰的函数约定第一个参数是当前用户角色 current_role；\n"
            "- 若 current_role != role，打印「权限不足：需要X，当前Y」并返回 None，否则执行原函数。\n"
            "被装饰函数 `delete_item(current_role, item)` 返回「已删除 item」。\n"
            "主程序：读入三行角色（如 admin/teacher/student），分别调用 delete_item('角色', '旧作业')，"
            "输出结果或拦截提示；说明参数化装饰器可以「带配置地」装饰函数。"
        ),
        "answer": (
            "# 权限检查装饰器（参数化）\n"
            "from functools import wraps\n\n"
            "def require_role(role):\n"
            "    def deco(func):\n"
            "        @wraps(func)\n"
            "        def wrapper(current_role, *args, **kwargs):\n"
            "            if current_role != role:\n"
            "                print(\"权限不足：需要\" + role + \"，当前\" + current_role)\n"
            "                return None\n"
            "            return func(current_role, *args, **kwargs)\n"
            "        return wrapper\n"
            "    return deco\n\n"
            "@require_role(\"admin\")\n"
            "def delete_item(current_role, item):\n"
            "    return \"已删除 \" + item\n\n"
            "i = 0\n"
            "while i < 3:\n"
            "    role = input()\n"
            "    result = delete_item(role, \"旧作业\")\n"
            "    if result is None:\n"
            "        print(role + \" 的操作被拦截\")\n"
            "    else:\n"
            "        print(role + \"：\" + result)\n"
            "    i = i + 1\n"
            "print(\"参数化装饰器可以带配置地装饰函数\")\n"
        ),
        "explanation": (
            "思路：参数化装饰器是三层结构——require_role(role) 接收配置返回 deco，"
            "deco(func) 返回 wrapper，wrapper 里用闭包记住的 role 做权限比对；"
            "@require_role('admin') 先执行外层拿配置，再装饰函数。"
            "讲解：普通装饰器两层（接收函数返回函数），参数化要三层（多一层接收配置）；"
            "role 通过闭包传进 wrapper，不同配置可以装饰出不同权限的函数；"
            "权限、重试次数、限流阈值这类「可配置」需求都用参数化装饰器。"
        ),
        "sample_input": "admin\nteacher\nstudent\n",
    },
    {
        "topic_id": 64,
        "title": "L20-64-E 单位换算装饰器",
        "content": (
            "单位换算装饰器。请定义装饰器 `cm_to_inch(func)`：把被装饰函数的返回值（厘米）"
            "换算成英寸（除以 2.54，保留 2 位小数），打印「X厘米 = Y英寸」并返回英寸值；"
            "用 @wraps 保留元信息。\n"
            "被装饰函数：`rect_diagonal(a, b)` 返回长 a 宽 b 的对角线长（厘米）；"
            "`tv_size(n)` 直接返回 n（模拟电视尺寸厘米数）。\n"
            "主程序：读入两个整数作为长宽，调用 rect_diagonal；再读入一个整数调用 tv_size；"
            "输出两次调用的最终返回值（英寸），说明原函数只算厘米，换算由装饰器完成。"
        ),
        "answer": (
            "# 单位换算装饰器\n"
            "from functools import wraps\n\n"
            "def cm_to_inch(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        cm = func(*args, **kwargs)\n"
            "        inch = round(cm / 2.54, 2)\n"
            "        print(str(cm) + \"厘米 = \" + str(inch) + \"英寸\")\n"
            "        return inch\n"
            "    return wrapper\n\n"
            "@cm_to_inch\n"
            "def rect_diagonal(a, b):\n"
            "    return round((a ** 2 + b ** 2) ** 0.5, 2)\n\n"
            "@cm_to_inch\n"
            "def tv_size(n):\n"
            "    return n\n\n"
            "a = int(input())\n"
            "b = int(input())\n"
            "d = rect_diagonal(a, b)\n"
            "print(\"对角线最终返回：\" + str(d) + \" 英寸\")\n"
            "n = int(input())\n"
            "size = tv_size(n)\n"
            "print(\"电视尺寸最终返回：\" + str(size) + \" 英寸\")\n"
            "print(\"原函数只算厘米，换算由装饰器完成\")\n"
        ),
        "explanation": (
            "思路：cm_to_inch 是「后置加工」型装饰器：拿到原函数的厘米结果后换算成英寸再返回；"
            "两个不同业务函数（算对角线、报尺寸）共用同一个换算装饰器；"
            "主程序拿到的已经是英寸值。"
            "讲解：单位换算、格式化、加密这类「对结果统一加工」的逻辑抽成装饰器，业务函数不用各自重复写；"
            "round 在装饰器里统一处理精度，保证两个函数输出格式一致；"
            "这就是装饰器「横切关注点统一处理」的思想。"
        ),
        "sample_input": "30\n40\n102\n",
    },
]
