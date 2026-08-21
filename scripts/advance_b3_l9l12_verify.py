"""批次3：L9-L12 (topic 53-56) 进阶题，每课 5 题，共 20 题。
主题与既有题（成绩分析器/数字流水线/词频分析器/库存核算/温度转换台/混合数据清洗/深浅拷贝实验室/分组调度）错开。
"""

QUESTIONS = [
    # ===================== L9 / topic 53 列表与列表推导式 =====================
    {
        "topic_id": 53,
        "title": "L9-53-A 购物清单管理",
        "content": (
            "购物清单管理。第一行输入 n，接下来 n 行每行一个商品名（用 append 加入清单）；"
            "然后再输入一行要删除的商品名。请完成：输出添加后的清单和商品总数；"
            "用 in 检查要删除的商品是否在清单里：在则用 remove 删除并输出「已删除 X」，"
            "不在则输出「清单里没有 X」；输出删除后的清单；"
            "最后用列表推导式给每个商品加上「★」前缀，输出装饰后的清单。"
        ),
        "answer": (
            "# 购物清单管理\n"
            "n = int(input())\n"
            "shopping = []\n"
            "i = 0\n"
            "while i < n:\n"
            "    item = input()\n"
            "    shopping.append(item)\n"
            "    i = i + 1\n"
            "print(\"添加后的清单：\" + str(shopping))\n"
            "print(\"商品总数：\" + str(len(shopping)))\n"
            "target = input()\n"
            "if target in shopping:\n"
            "    shopping.remove(target)\n"
            "    print(\"已删除 \" + target)\n"
            "else:\n"
            "    print(\"清单里没有 \" + target)\n"
            "print(\"删除后的清单：\" + str(shopping))\n"
            "# 列表推导式：给每个商品加星星前缀\n"
            "fancy = [\"★\" + item for item in shopping]\n"
            "print(\"装饰后：\" + str(fancy))\n"
        ),
        "explanation": (
            "思路：while 循环读 n 个商品并 append；用 in 判断存在再 remove（避免报错）；"
            "最后列表推导式 [\"★\"+item for item in shopping] 批量加工。"
            "讲解：append 在末尾添加，remove 按值删除第一个匹配项；"
            "删除前先 in 检查是好习惯；列表推导式是「对每个元素加工生成新列表」的简洁写法。"
        ),
        "sample_input": "4\n牛奶\n面包\n苹果\n牛奶\n牛奶\n",
    },
    {
        "topic_id": 53,
        "title": "L9-53-B 跳绳计数统计",
        "content": (
            "跳绳计数统计。输入一行：若干个空格分隔的整数，表示每天的跳绳个数。"
            "请完成：转成整数列表并输出；用 max/min 找出最多和最少的一天；"
            "计算总个数和平均个数（1 位小数）；用列表推导式筛出大于平均值的天数（值本身）并输出；"
            "用 sort() 排序后输出「从少到多」和「从多到少」两个版本；最后输出训练天数。"
        ),
        "answer": (
            "# 跳绳计数统计\n"
            "nums = [int(x) for x in input().split()]\n"
            "print(\"每天跳绳数：\" + str(nums))\n"
            "most = max(nums)\n"
            "least = min(nums)\n"
            "total = sum(nums)\n"
            "avg = total / len(nums)\n"
            "print(\"最多一天：\" + str(most) + \" 个\")\n"
            "print(\"最少一天：\" + str(least) + \" 个\")\n"
            "print(\"总个数：\" + str(total) + \"，平均：\" + str(round(avg, 1)))\n"
            "# 筛出超过平均值的天数\n"
            "above = [x for x in nums if x > avg]\n"
            "print(\"超过平均的日子：\" + str(above))\n"
            "up = nums.copy()\n"
            "up.sort()\n"
            "down = nums.copy()\n"
            "down.sort(reverse=True)\n"
            "print(\"从少到多：\" + str(up))\n"
            "print(\"从多到少：\" + str(down))\n"
            "print(\"共训练 \" + str(len(nums)) + \" 天\")\n"
        ),
        "explanation": (
            "思路：列表推导式 [int(x) for x in input().split()] 一步完成切分和转换；"
            "max/min/sum/len 是内置统计函数；带条件的推导式 [x for x in nums if x>avg] 做筛选；"
            "排序前先 copy，避免破坏原列表。"
            "讲解：sort() 是原地排序会改变列表本身，所以先 copy() 再排；"
            "reverse=True 表示降序；sum(nums)/len(nums) 就是平均值。"
        ),
        "sample_input": "120 80 150 200 95\n",
    },
    {
        "topic_id": 53,
        "title": "L9-53-C 值日生排班表",
        "content": (
            "值日生排班表。第一行输入 n 个姓名（空格分隔）；第二行输入一个整数 k（表示要插入新同学的位置下标）；"
            "第三行输入新同学姓名。请完成：输出原排班表；用 insert(k, 名字) 把新同学插到指定位置并输出；"
            "用切片输出前一半和后一半的值日表（若奇数，前一半多一个）；"
            "用 pop() 弹出最后一位并输出「X 今天请假」；输出最终排班表；"
            "最后用 enumerate 输出「第几名是谁」的完整名单。"
        ),
        "answer": (
            "# 值日生排班表\n"
            "names = input().split()\n"
            "k = int(input())\n"
            "new_name = input()\n"
            "print(\"原排班表：\" + str(names))\n"
            "names.insert(k, new_name)\n"
            "print(\"插入后：\" + str(names))\n"
            "half = (len(names) + 1) // 2\n"
            "first_half = names[:half]\n"
            "second_half = names[half:]\n"
            "print(\"前一半：\" + str(first_half))\n"
            "print(\"后一半：\" + str(second_half))\n"
            "absent = names.pop()\n"
            "print(absent + \" 今天请假\")\n"
            "print(\"最终排班表：\" + str(names))\n"
            "# enumerate 带序号遍历\n"
            "for idx, name in enumerate(names):\n"
            "    print(\"第\" + str(idx + 1) + \"位：\" + name)\n"
        ),
        "explanation": (
            "思路：insert(k, x) 在下标 k 处插入；切片 names[:half] 和 names[half:] 分成两半，"
            "奇数长度时 (len+1)//2 让前一半多一个；pop() 弹出末尾元素并返回它；"
            "enumerate 同时拿到下标和元素。"
            "讲解：切片不会改变原列表，返回的是新列表；pop 和 remove 不同：pop 按位置、remove 按值；"
            "enumerate 让「第几名」这种带序号的输出特别方便。"
        ),
        "sample_input": "小明 小红 小刚\n1\n小美\n",
    },
    {
        "topic_id": 53,
        "title": "L9-53-D 停车场进出记录",
        "content": (
            "停车场进出记录。第一行输入场内已有车辆数 n，第二行输入 n 个车牌（空格分隔）。"
            "然后连续处理若干条指令，每行一条：「in 车牌」表示进场（append），「out 车牌」表示出场（remove），"
            "输入「end」结束。每条指令执行后输出当前场内车辆；"
            "若 out 的车牌不在场内，输出「找不到该车牌」。结束后输出：最终场内车辆数、"
            "用列表推导式筛出以「A」开头的车牌、以及按字典序排序后的车牌列表。"
        ),
        "answer": (
            "# 停车场进出记录\n"
            "n = int(input())\n"
            "cars = input().split()\n"
            "print(\"场内已有：\" + str(cars))\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    action, plate = line.split()\n"
            "    if action == \"in\":\n"
            "        cars.append(plate)\n"
            "        print(plate + \" 进场，当前：\" + str(cars))\n"
            "    elif action == \"out\":\n"
            "        if plate in cars:\n"
            "            cars.remove(plate)\n"
            "            print(plate + \" 出场，当前：\" + str(cars))\n"
            "        else:\n"
            "            print(\"找不到该车牌：\" + plate)\n"
            "print(\"最终场内车辆数：\" + str(len(cars)))\n"
            "a_cars = [c for c in cars if c.startswith(\"A\")]\n"
            "print(\"A 开头的车牌：\" + str(a_cars))\n"
            "sorted_cars = sorted(cars)\n"
            "print(\"字典序排序：\" + str(sorted_cars))\n"
        ),
        "explanation": (
            "思路：while True 循环读指令直到 end；split 拆出动作和车牌；"
            "in 就 append，out 先 in 检查再 remove；结束后推导式筛 A 开头、sorted() 排序。"
            "讲解：startswith() 判断字符串前缀；sorted() 返回新列表（和 sort() 原地排序不同）；"
            "指令式输入（动作+参数）是模拟真实系统的好方法。"
        ),
        "sample_input": "3\nA12 B88 C66\nin A99\nout B88\nout D01\nend\n",
    },
    {
        "topic_id": 53,
        "title": "L9-53-E 口算批改器",
        "content": (
            "口算批改器。第一行输入 n，接下来 n 行每行格式为「算式 学生答案」，"
            "算式形如「3+5」「12-4」（只有加法和减法，无空格）。请完成："
            "①解析每行：把算式按 + 或 - 拆开，计算正确答案；②和学生答案比较，记录对错；"
            "③用两个列表分别收集答对和答错的算式；④输出批改结果：每题一行「算式=正确答案 对/错」；"
            "⑤最后输出正确率（对题数÷总题数×100，保留 1 位小数）并给一句评语（>=80「很棒」，否则「再练练」）。"
        ),
        "answer": (
            "# 口算批改器\n"
            "n = int(input())\n"
            "right = []\n"
            "wrong = []\n"
            "results = []\n"
            "i = 0\n"
            "while i < n:\n"
            "    expr, ans = input().split()\n"
            "    ans = int(ans)\n"
            "    if \"+\" in expr:\n"
            "        a, b = expr.split(\"+\")\n"
            "        correct = int(a) + int(b)\n"
            "    else:\n"
            "        a, b = expr.split(\"-\")\n"
            "        correct = int(a) - int(b)\n"
            "    ok = ans == correct\n"
            "    results.append((expr, correct, ok))\n"
            "    if ok:\n"
            "        right.append(expr)\n"
            "    else:\n"
            "        wrong.append(expr)\n"
            "    i = i + 1\n"
            "for expr, correct, ok in results:\n"
            "    mark = \"对\" if ok else \"错\"\n"
            "    print(expr + \"=\" + str(correct) + \" \" + mark)\n"
            "rate = len(right) / n * 100\n"
            "print(\"答对：\" + str(right))\n"
            "print(\"答错：\" + str(wrong))\n"
            "print(\"正确率：\" + str(round(rate, 1)) + \"%\")\n"
            "if rate >= 80:\n"
            "    print(\"很棒\")\n"
            "else:\n"
            "    print(\"再练练\")\n"
        ),
        "explanation": (
            "思路：每行先拆算式和学生答案；算式里找 + 或 - 再 split 出两个数计算正确答案；"
            "用元组 (算式, 正确答案, 对错) 存入 results，同时分流到 right/wrong 列表；"
            "最后算正确率并评语。"
            "讲解：字符串可以当「小数据」用 in 判断含不含某符号；"
            "列表里存元组是记录「一组相关信息」的常用方式；"
            "三元表达式 \"对\" if ok else \"错\" 让输出标记很简洁。"
        ),
        "sample_input": "4\n3+5 8\n12-4 7\n9+6 15\n20-8 12\n",
    },

    # ===================== L10 / topic 54 元组与字典 =====================
    {
        "topic_id": 54,
        "title": "L10-54-A 通讯录",
        "content": (
            "通讯录。先输入 n，接下来 n 行每行「姓名 电话」建立字典。然后输入一个查询姓名："
            "若存在输出「姓名 的电话是 X」，不存在输出「没有这个联系人」；"
            "再输入两行：新联系人姓名和电话，把他加入字典；"
            "输出全部联系人（每行「姓名:电话」）和总人数；"
            "最后用元组列表记录前两个联系人（姓名,电话）并输出这个「快捷拨号」元组列表。"
        ),
        "answer": (
            "# 通讯录\n"
            "n = int(input())\n"
            "contacts = {}\n"
            "i = 0\n"
            "while i < n:\n"
            "    name, phone = input().split()\n"
            "    contacts[name] = phone\n"
            "    i = i + 1\n"
            "# 查询\n"
            "query = input()\n"
            "if query in contacts:\n"
            "    print(query + \" 的电话是 \" + contacts[query])\n"
            "else:\n"
            "    print(\"没有这个联系人\")\n"
            "# 新增\n"
            "new_name = input()\n"
            "new_phone = input()\n"
            "contacts[new_name] = new_phone\n"
            "print(\"全部联系人：\")\n"
            "for name in contacts:\n"
            "    print(name + \":\" + contacts[name])\n"
            "print(\"总人数：\" + str(len(contacts)))\n"
            "# 前两个联系人做成元组列表（快捷拨号）\n"
            "names = []\n"
            "for name in contacts:\n"
            "    names.append(name)\n"
            "quick = [(names[0], contacts[names[0]]), (names[1], contacts[names[1]])]\n"
            "print(\"快捷拨号：\" + str(quick))\n"
        ),
        "explanation": (
            "思路：字典 contacts[姓名]=电话 建立映射；in 判断键是否存在；"
            "直接 contacts[新名]=新电话 就是新增；for name in contacts 遍历键；"
            "元组列表把固定搭配的数据绑在一起。"
            "讲解：字典按键查找非常快，适合「名字→信息」这类对应关系；"
            "键必须是唯一的，重复赋值会覆盖旧值；元组不可变，适合表示「一旦确定就不该改」的组合数据。"
        ),
        "sample_input": "3\n小明 101\n小红 102\n小刚 103\n小红\n小美\n104\n",
    },
    {
        "topic_id": 54,
        "title": "L10-54-B 自动售货机",
        "content": (
            "自动售货机。商品表固定：可乐 3 元、矿泉水 2 元、面包 5 元、饼干 4 元（用字典存储）。"
            "输入两行：商品名、付款金额（整数）。请完成："
            "①若商品不存在输出「没有这个商品」；②存在则输出商品和价格，"
            "判断付款是否足够：足够输出找零并「交易成功」，不够输出「还差 X 元」；"
            "③输出所有商品的价目表（每行「商品:价格元」）；④用元组 (商品, 价格, 付款) 记录本次交易尝试并输出；"
            "⑤统计并输出商品总数和最贵的商品名。"
        ),
        "answer": (
            "# 自动售货机\n"
            "prices = {\"可乐\": 3, \"矿泉水\": 2, \"面包\": 5, \"饼干\": 4}\n"
            "item = input()\n"
            "pay = int(input())\n"
            "if item not in prices:\n"
            "    print(\"没有这个商品\")\n"
            "else:\n"
            "    price = prices[item]\n"
            "    print(\"商品：\" + item + \"，价格：\" + str(price) + \" 元\")\n"
            "    if pay >= price:\n"
            "        print(\"找零：\" + str(pay - price) + \" 元\")\n"
            "        print(\"交易成功\")\n"
            "    else:\n"
            "        print(\"还差 \" + str(price - pay) + \" 元\")\n"
            "# 价目表\n"
            "print(\"价目表：\")\n"
            "for name in prices:\n"
            "    print(name + \":\" + str(prices[name]) + \"元\")\n"
            "# 本次交易记录（元组）\n"
            "record = (item, pay)\n"
            "print(\"交易记录：\" + str(record))\n"
            "# 统计\n"
            "count = len(prices)\n"
            "most_expensive = \"\"\n"
            "max_price = -1\n"
            "for name in prices:\n"
            "    if prices[name] > max_price:\n"
            "        max_price = prices[name]\n"
            "        most_expensive = name\n"
            "print(\"商品总数：\" + str(count))\n"
            "print(\"最贵的商品：\" + most_expensive + \"（\" + str(max_price) + \" 元）\")\n"
        ),
        "explanation": (
            "思路：字典存价目表；not in 判断商品不存在；存在时取出价格再嵌套判断钱够不够；"
            "遍历找最贵商品用「打擂台」：维护 max_price 和对应的名字。"
            "讲解：字典初始化 {键:值, 键:值} 一行搞定；"
            "「打擂台」求最大值的套路：先设一个很小的初始值，遍历中遇到更大的就更新；"
            "元组适合打包一次交易的信息。"
        ),
        "sample_input": "面包\n10\n",
    },
    {
        "topic_id": 54,
        "title": "L10-54-C 一周天气记录",
        "content": (
            "一周天气记录。输入 7 行，每行「星期 温度」（星期用 Mon/Tue/Wed/Thu/Fri/Sat/Sun，温度为整数）。"
            "请完成：存入字典并输出完整记录；找出最高温和最低温对应的星期；"
            "计算平均温度（1 位小数）；用循环收集温度大于平均值的星期到一个列表并输出；"
            "再输入一行要修改的星期和新温度（如「Wed 30」），用字典更新它；输出修改后的记录。"
        ),
        "answer": (
            "# 一周天气记录\n"
            "weather = {}\n"
            "days = [\"Mon\", \"Tue\", \"Wed\", \"Thu\", \"Fri\", \"Sat\", \"Sun\"]\n"
            "i = 0\n"
            "while i < 7:\n"
            "    day, temp = input().split()\n"
            "    weather[day] = int(temp)\n"
            "    i = i + 1\n"
            "print(\"一周天气：\" + str(weather))\n"
            "# 找最高温和最低温\n"
            "hot_day = days[0]\n"
            "cold_day = days[0]\n"
            "for day in days:\n"
            "    if weather[day] > weather[hot_day]:\n"
            "        hot_day = day\n"
            "    if weather[day] < weather[cold_day]:\n"
            "        cold_day = day\n"
            "print(\"最热：\" + hot_day + \"（\" + str(weather[hot_day]) + \" 度）\")\n"
            "print(\"最冷：\" + cold_day + \"（\" + str(weather[cold_day]) + \" 度）\")\n"
            "total = 0\n"
            "for day in days:\n"
            "    total = total + weather[day]\n"
            "avg = total / 7\n"
            "print(\"平均温度：\" + str(round(avg, 1)))\n"
            "# 高于平均的星期\n"
            "above = []\n"
            "for day in days:\n"
            "    if weather[day] > avg:\n"
            "        above.append(day)\n"
            "print(\"高于平均的日子：\" + str(above))\n"
            "# 修改某天温度\n"
            "fix_day, fix_temp = input().split()\n"
            "weather[fix_day] = int(fix_temp)\n"
            "print(\"修改后：\" + str(weather))\n"
        ),
        "explanation": (
            "思路：字典按星期存温度；用 days 列表保证遍历顺序；"
            "找最值用「打擂台」同时维护最热和最冷两个候选；求平均后再次遍历收集高于平均的日子；"
            "最后字典赋值直接覆盖修改。"
            "讲解：字典本身不保证想要的展示顺序，配一个列表（days）控制顺序更稳妥；"
            "同一个循环里可以同时维护多个「擂台」；字典更新就是「同名键再赋值」。"
        ),
        "sample_input": "Mon 25\nTue 27\nWed 24\nThu 28\nFri 26\nSat 30\nSun 29\nWed 31\n",
    },
    {
        "topic_id": 54,
        "title": "L10-54-D 图书角借阅登记",
        "content": (
            "图书角借阅登记。先输入 n，接下来 n 行每行「书名 借阅人」建立字典（书→借阅人）。"
            "然后输入一行「书名」查询借阅状态：已借出输出「书名 被 X 借走了」，否则输出「书名 在图书角」；"
            "再输入两行「书名 借阅人」登记一次新借阅（若书已被借走，输出「这本书已被借走」并不修改）；"
            "输出最终借阅表和借出的书数量；最后把（书名, 借阅人）配对成元组列表输出。"
        ),
        "answer": (
            "# 图书角借阅登记\n"
            "n = int(input())\n"
            "borrow = {}\n"
            "i = 0\n"
            "while i < n:\n"
            "    book, person = input().split()\n"
            "    borrow[book] = person\n"
            "    i = i + 1\n"
            "# 查询\n"
            "query = input()\n"
            "if query in borrow:\n"
            "    print(query + \" 被 \" + borrow[query] + \" 借走了\")\n"
            "else:\n"
            "    print(query + \" 在图书角\")\n"
            "# 新借阅登记\n"
            "book, person = input().split()\n"
            "if book in borrow:\n"
            "    print(\"这本书已被借走\")\n"
            "else:\n"
            "    borrow[book] = person\n"
            "    print(book + \" 借给了 \" + person)\n"
            "# 输出最终状态\n"
            "print(\"借阅表：\" + str(borrow))\n"
            "print(\"借出的书数量：\" + str(len(borrow)))\n"
            "# 配对成元组列表\n"
            "pairs = []\n"
            "for book in borrow:\n"
            "    pairs.append((book, borrow[book]))\n"
            "print(\"配对列表：\" + str(pairs))\n"
        ),
        "explanation": (
            "思路：字典记录「书→借阅人」；查询用 in 判断；新借阅前先检查是否已借出，避免覆盖；"
            "最后遍历字典把键值配对成元组列表。"
            "讲解：字典的键存在就代表「已借出」，这是用「存在性」表达状态的典型用法；"
            "元组列表 [(键,值), ...] 是字典转「成对数据」的常见形式；"
            "先检查再写入能防止数据被意外覆盖。"
        ),
        "sample_input": "3\n西游记 小明\n三国演义 小红\n水浒传 小刚\n西游记\n红楼梦 小美\n",
    },
    {
        "topic_id": 54,
        "title": "L10-54-E 小组积分赛",
        "content": (
            "小组积分赛。第一行输入 4 个队员姓名（空格分隔）。然后输入若干行得分记录，"
            "每行「姓名 分数」，输入 end 结束（同一人可多次得分，要累加）。请完成："
            "①用字典累加每人总分；②输出每人的总分；③找出冠军（总分最高者）；"
            "④计算全队平均分（1 位小数）；⑤把 (姓名, 总分) 做成元组列表，"
            "用 sort(key=...) 按总分从高到低排序输出；最后输出「冠军是 X，共 Y 分」。"
        ),
        "answer": (
            "# 小组积分赛\n"
            "members = input().split()\n"
            "scores = {}\n"
            "for m in members:\n"
            "    scores[m] = 0\n"
            "# 累加得分\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    name, point = line.split()\n"
            "    if name in scores:\n"
            "        scores[name] = scores[name] + int(point)\n"
            "    else:\n"
            "        print(\"没有这个队员：\" + name)\n"
            "# 输出每人总分\n"
            "print(\"各队员总分：\")\n"
            "for name in scores:\n"
            "    print(name + \":\" + str(scores[name]))\n"
            "# 找冠军\n"
            "champion = members[0]\n"
            "for name in scores:\n"
            "    if scores[name] > scores[champion]:\n"
            "        champion = name\n"
            "total = 0\n"
            "for name in scores:\n"
            "    total = total + scores[name]\n"
            "avg = total / len(scores)\n"
            "print(\"全队平均分：\" + str(round(avg, 1)))\n"
            "# 元组列表排序\n"
            "pairs = []\n"
            "for name in scores:\n"
            "    pairs.append((name, scores[name]))\n"
            "pairs.sort(key=lambda p: p[1], reverse=True)\n"
            "print(\"从高到低：\" + str(pairs))\n"
            "print(\"冠军是 \" + champion + \"，共 \" + str(scores[champion]) + \" 分\")\n"
        ),
        "explanation": (
            "思路：先把每人初始分设为 0；循环读得分记录累加（scores[name]=scores[name]+分数）；"
            "打擂台找冠军；配对成元组列表后用 sort(key=lambda p: p[1]) 按分数排序。"
            "讲解：累加字典值要先初始化，否则键不存在会报错；"
            "lambda p: p[1] 表示「按元组第二个元素比较」，这是排序字典数据最常用的技巧；"
            "reverse=True 从高到低。"
        ),
        "sample_input": "小明 小红 小刚 小美\n小明 10\n小红 20\n小明 15\n小美 30\nend\n",
    },

    # ===================== L11 / topic 55 类型转换 =====================
    {
        "topic_id": 55,
        "title": "L11-55-A 输入体检站",
        "content": (
            "输入体检站。连续输入 4 行内容（每行可能是整数、小数或普通文字）。"
            "对每一行请判断它属于哪种类型：先试 int()（能转就是整数），再试 float()（能转就是小数），"
            "都不能转就是文字。注意：不能用 try（那是后面课的内容），"
            "请用字符串方法判断：只含数字（可带一个负号开头）的是整数；"
            "去掉一个小数点后其余全是数字的是小数。输出每行的判断结果和转换后的值，"
            "最后统计三种类型各出现了几次。"
        ),
        "answer": (
            "# 输入体检站：判断每行是什么类型\n"
            "int_cnt = 0\n"
            "float_cnt = 0\n"
            "str_cnt = 0\n"
            "i = 0\n"
            "while i < 4:\n"
            "    s = input()\n"
            "    body = s\n"
            "    if s.startswith(\"-\"):\n"
            "        body = s[1:]\n"
            "    if body.isdigit():\n"
            "        val = int(s)\n"
            "        int_cnt = int_cnt + 1\n"
            "        print(s + \" -> 整数，值为 \" + str(val))\n"
            "    elif body.count(\".\") == 1 and body.replace(\".\", \"\").isdigit():\n"
            "        val = float(s)\n"
            "        float_cnt = float_cnt + 1\n"
            "        print(s + \" -> 小数，值为 \" + str(val))\n"
            "    else:\n"
            "        str_cnt = str_cnt + 1\n"
            "        print(s + \" -> 文字，原样保留\")\n"
            "    i = i + 1\n"
            "print(\"整数个数：\" + str(int_cnt))\n"
            "print(\"小数个数：\" + str(float_cnt))\n"
            "print(\"文字个数：\" + str(str_cnt))\n"
        ),
        "explanation": (
            "思路：不用 try 的话，可以用字符串方法判断：先处理负号，body.isdigit() 判整数；"
            "小数要求恰好一个点且去点后全是数字；其余归为文字。转换用 int()/float()。"
            "讲解：isdigit() 只对纯数字字符串返回 True；"
            "count('.')==1 保证只有一个点；replace('.','').isdigit() 检查点之外都是数字；"
            "这种「先判断再转换」能避免程序报错。"
        ),
        "sample_input": "42\n3.14\nhello\n-7\n",
    },
    {
        "topic_id": 55,
        "title": "L11-55-B 成绩字符串解析",
        "content": (
            "成绩字符串解析。输入一行，格式为「姓名:语文,数学,英语」，例如「小明:90,85,92」。"
            "请完成：①用 split(':') 拆出姓名和成绩部分；②再用 split(',') 拆出三科成绩字符串；"
            "③用 int() 逐个转成整数；④计算总分、平均分（1 位小数）、最高分和最低分；"
            "⑤用 str() 把结果拼成一句话输出：「姓名 总分 X 平均 Y 最高 A 最低 B」；"
            "⑥输出转换前后类型对比：第一个成绩转换前是 str，转换后是 int（用 type 验证）。"
        ),
        "answer": (
            "# 成绩字符串解析\n"
            "line = input()\n"
            "name_part, score_part = line.split(\":\")\n"
            "score_strs = score_part.split(\",\")\n"
            "chinese = int(score_strs[0])\n"
            "math = int(score_strs[1])\n"
            "english = int(score_strs[2])\n"
            "total = chinese + math + english\n"
            "avg = total / 3\n"
            "highest = chinese\n"
            "if math > highest:\n"
            "    highest = math\n"
            "if english > highest:\n"
            "    highest = english\n"
            "lowest = chinese\n"
            "if math < lowest:\n"
            "    lowest = math\n"
            "if english < lowest:\n"
            "    lowest = english\n"
            "summary = name_part + \" 总分 \" + str(total) + \" 平均 \" + str(round(avg, 1)) + \" 最高 \" + str(highest) + \" 最低 \" + str(lowest)\n"
            "print(summary)\n"
            "print(\"转换前类型：\" + str(type(score_strs[0])))\n"
            "print(\"转换后类型：\" + str(type(chinese)))\n"
        ),
        "explanation": (
            "思路：两层 split 先拆姓名再拆三科；int() 逐个转换后才能参与计算；"
            "最值用两次「打擂台」；最后 str() 把数字转回字符串拼接输出。"
            "讲解：从文件或输入读来的数字都是字符串，必须转换才能计算；"
            "split(':') 和 split(',') 组合使用可以解析「结构化文本」；"
            "round(avg,1) 是数值四舍五入，str() 负责把它变回可拼接的文本。"
        ),
        "sample_input": "小明:90,85,92\n",
    },
    {
        "topic_id": 55,
        "title": "L11-55-C 布尔实验室",
        "content": (
            "布尔实验室。输入三行：一个字符串、一个整数、一个小数。请完成："
            "①用 bool() 分别转换这三个值并输出结果；②再用 bool() 转换四个特殊值：空字符串、0、0.0、\"0\"，输出结果；"
            "③判断输入的字符串长度是否大于 0（用 bool(len(s)) 和直接比较两种方式，输出两者是否一致）；"
            "④总结输出：哪些值转成了 False（把结果为 False 的收集到列表里）。"
        ),
        "answer": (
            "# 布尔实验室\n"
            "s = input()\n"
            "n = int(input())\n"
            "f = float(input())\n"
            "print(\"bool(\" + s + \") = \" + str(bool(s)))\n"
            "print(\"bool(\" + str(n) + \") = \" + str(bool(n)))\n"
            "print(\"bool(\" + str(f) + \") = \" + str(bool(f)))\n"
            "# 四个特殊值\n"
            "specials = [\"\", 0, 0.0, \"0\"]\n"
            "false_values = []\n"
            "for v in specials:\n"
            "    b = bool(v)\n"
            "    print(\"bool(\" + repr(v) + \") = \" + str(b))\n"
            "    if not b:\n"
            "        false_values.append(v)\n"
            "# 两种判断字符串非空的方式\n"
            "way1 = bool(len(s))\n"
            "way2 = len(s) > 0\n"
            "print(\"bool(len) 方式：\" + str(way1))\n"
            "print(\"len>0 方式：\" + str(way2))\n"
            "print(\"两种方式一致：\" + str(way1 == way2))\n"
            "print(\"转成 False 的值：\" + str(false_values))\n"
        ),
        "explanation": (
            "思路：bool() 可以把任何值转成 True/False；空字符串、0、0.0 都是 False，\"0\"（非空字符串）是 True；"
            "用列表收集结果为 False 的值；bool(len(s)) 和 len(s)>0 是等价的两种非空判断。"
            "讲解：Python 里「空/零」类的值转布尔是 False，其余一般是 True；"
            "\"0\" 是长度为 1 的字符串，不是空的，所以是 True——这是最容易搞错的点；"
            "repr() 显示值时会带引号，区分字符串和数字更清楚。"
        ),
        "sample_input": "abc\n0\n2.5\n",
    },
    {
        "topic_id": 55,
        "title": "L11-55-D 单位换算菜单",
        "content": (
            "单位换算菜单。支持三种换算：1）厘米→英寸（除以 2.54）；2）千克→磅（乘以 2.2）；"
            "3）摄氏度→华氏度（乘 9 除 5 加 32）。输入若干行，每行「类型 数值」，"
            "类型用 cm/kg/c 表示，输入 end 结束。每行根据类型选择对应公式换算并输出结果（2 位小数）；"
            "若类型不认识输出「未知类型」；结束后输出总换算次数和各类型的次数（用字典统计）。"
        ),
        "answer": (
            "# 单位换算菜单\n"
            "counts = {\"cm\": 0, \"kg\": 0, \"c\": 0}\n"
            "total_times = 0\n"
            "while True:\n"
            "    line = input()\n"
            "    if line == \"end\":\n"
            "        break\n"
            "    kind, value = line.split()\n"
            "    value = float(value)\n"
            "    if kind == \"cm\":\n"
            "        result = value / 2.54\n"
            "        print(str(value) + \" 厘米 = \" + str(round(result, 2)) + \" 英寸\")\n"
            "        counts[\"cm\"] = counts[\"cm\"] + 1\n"
            "    elif kind == \"kg\":\n"
            "        result = value * 2.2\n"
            "        print(str(value) + \" 千克 = \" + str(round(result, 2)) + \" 磅\")\n"
            "        counts[\"kg\"] = counts[\"kg\"] + 1\n"
            "    elif kind == \"c\":\n"
            "        result = value * 9 / 5 + 32\n"
            "        print(str(value) + \" 摄氏度 = \" + str(round(result, 2)) + \" 华氏度\")\n"
            "        counts[\"c\"] = counts[\"c\"] + 1\n"
            "    else:\n"
            "        print(\"未知类型：\" + kind)\n"
            "    total_times = total_times + 1\n"
            "print(\"总换算次数：\" + str(total_times))\n"
            "print(\"各类型次数：\" + str(counts))\n"
        ),
        "explanation": (
            "思路：while 循环读「类型 数值」，float() 转数值后按类型 if-elif 选择公式；"
            "字典 counts 记录每种类型用了多少次；total_times 统计总次数。"
            "讲解：输入统一是字符串，先 split 再 float() 转换是标准流程；"
            "字典计数器先初始化为 0，命中就 +1；"
            "不同单位换算公式不同，用 if-elif 分发到对应公式。"
        ),
        "sample_input": "cm 100\nkg 30\nc 25\nxx 9\nend\n",
    },
    {
        "topic_id": 55,
        "title": "L11-55-E 数字拼拼乐",
        "content": (
            "数字拼拼乐。输入两行：两个正整数 a 和 b（以字符串形式读入）。请完成："
            "①输出字符串拼接结果（a+b 直接拼接，如 \"12\"+\"34\"=\"1234\"）；"
            "②输出整数相加结果（先 int() 转换再相加）；③把拼接结果再转回整数，加上 b 的整数值输出；"
            "④把 a 转成 float 再除以 b 的整数值（2 位小数）；⑤用 str() 把「a×b 的积」转成字符串，"
            "前后加上「积是」和「哦」输出。通过这道题体会：同样的 + 在字符串和整数下行为完全不同。"
        ),
        "answer": (
            "# 数字拼拼乐：字符串与整数的 +\n"
            "a = input()\n"
            "b = input()\n"
            "# 1. 字符串拼接\n"
            "concat = a + b\n"
            "print(\"字符串拼接：\" + concat)\n"
            "# 2. 整数相加\n"
            "a_int = int(a)\n"
            "b_int = int(b)\n"
            "print(\"整数相加：\" + str(a_int + b_int))\n"
            "# 3. 拼接结果转回整数再加 b\n"
            "big = int(concat) + b_int\n"
            "print(\"拼接转整数再加 b：\" + str(big))\n"
            "# 4. float 除法\n"
            "div = float(a) / b_int\n"
            "print(\"a 除以 b：\" + str(round(div, 2)))\n"
            "# 5. 积转字符串包装\n"
            "product = a_int * b_int\n"
            "print(\"积是\" + str(product) + \"哦\")\n"
            "print(\"类型变化演示：\")\n"
            "print(\"  a 原始类型：\" + str(type(a)))\n"
            "print(\"  a_int 类型：\" + str(type(a_int)))\n"
            "print(\"  concat 类型：\" + str(type(concat)))\n"
        ),
        "explanation": (
            "思路：input() 读入的都是字符串，\"12\"+\"34\" 会拼成 \"1234\" 而不是 46；"
            "int() 转换后才是数学加法；拼接结果还能再 int() 转回大整数；最后体会 str() 包装输出。"
            "讲解：+ 对字符串是拼接、对数字是加法——类型决定行为；"
            "int(\"1234\") 可以把数字字符串变成整数；"
            "输出数字时必须 str() 转换才能和文字拼接，这是最常见的类型转换场景。"
        ),
        "sample_input": "12\n34\n",
    },

    # ===================== L12 / topic 56 赋值、深浅拷贝与可变对象 =====================
    {
        "topic_id": 56,
        "title": "L12-56-A 菜单备份实验",
        "content": (
            "菜单备份实验。输入一行：若干菜名（空格分隔）作为今日菜单。请完成："
            "①用 = 直接赋值 menu_b = menu_a，再修改 menu_a（append 一个新菜），观察 menu_b 是否跟着变并输出；"
            "②用 copy() 做浅拷贝 menu_c，再修改 menu_a，观察 menu_c 是否受影响并输出；"
            "③分别输出三个变量的 id 是否相同（用 id() 函数）；④总结：哪些变量其实是同一份数据。"
        ),
        "answer": (
            "# 菜单备份实验\n"
            "menu_a = input().split()\n"
            "print(\"原始菜单 menu_a：\" + str(menu_a))\n"
            "# 1. 直接赋值：只是起了个外号\n"
            "menu_b = menu_a\n"
            "menu_a.append(\"新菜\")\n"
            "print(\"menu_a 加菜后：\" + str(menu_a))\n"
            "print(\"menu_b 跟着变了吗：\" + str(menu_b))\n"
            "print(\"a 和 b 是同一份吗：\" + str(id(menu_a) == id(menu_b)))\n"
            "# 2. copy()：真正复制一份\n"
            "menu_c = menu_a.copy()\n"
            "menu_a.append(\"另一道新菜\")\n"
            "print(\"menu_a 再加菜：\" + str(menu_a))\n"
            "print(\"menu_c 受影响了吗：\" + str(menu_c))\n"
            "print(\"a 和 c 是同一份吗：\" + str(id(menu_a) == id(menu_c)))\n"
            "print(\"总结：menu_b 与 menu_a 同一份，menu_c 是独立副本\")\n"
        ),
        "explanation": (
            "思路：= 赋值只是让两个名字指向同一个列表，改一个两个都变；"
            "copy() 复制出新列表，之后互不影响；用 id() 比较两个变量是否指向同一对象。"
            "讲解：列表是可变对象，赋值不会复制数据；"
            "id() 返回对象的「身份证号」，相同就是同一份；"
            "想让备份不被后续修改影响，必须用 copy()（或切片 [:]）。"
        ),
        "sample_input": "番茄炒蛋 蒸蛋 炒青菜\n",
    },
    {
        "topic_id": 56,
        "title": "L12-56-B 二维棋盘与拷贝",
        "content": (
            "二维棋盘与拷贝。程序内建一个 3x3 棋盘（二维列表，元素都是 '·'）。请完成："
            "①用 copy.copy 做浅拷贝 board_shallow，用 copy.deepcopy 做深拷贝 board_deep；"
            "②在原棋盘 board[1][1] 放一个 'X'；③分别输出三个棋盘，观察谁跟着变了；"
            "④解释输出：浅拷贝为什么外层独立内层共享、深拷贝为什么完全独立；"
            "⑤输出三个棋盘各自的 id 和第一行的 id 对比（验证内层是否共享）。"
        ),
        "answer": (
            "# 二维棋盘与深浅拷贝\n"
            "import copy\n"
            "board = [['.', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]\n"
            "board_shallow = copy.copy(board)\n"
            "board_deep = copy.deepcopy(board)\n"
            "# 在原棋盘中心放 X\n"
            "board[1][1] = 'X'\n"
            "print(\"原棋盘：\" + str(board))\n"
            "print(\"浅拷贝：\" + str(board_shallow))\n"
            "print(\"深拷贝：\" + str(board_deep))\n"
            "# 外层 id 对比\n"
            "print(\"外层：浅拷贝独立吗 \" + str(id(board) != id(board_shallow)))\n"
            "print(\"外层：深拷贝独立吗 \" + str(id(board) != id(board_deep)))\n"
            "# 内层 id 对比（关键）\n"
            "print(\"内层：浅拷贝共享吗 \" + str(id(board[1]) == id(board_shallow[1])))\n"
            "print(\"内层：深拷贝共享吗 \" + str(id(board[1]) == id(board_deep[1])))\n"
            "print(\"结论：浅拷贝只复制外层，内层行仍共享；深拷贝层层都复制，完全独立\")\n"
        ),
        "explanation": (
            "思路：二维列表用 copy.copy 只复制外层（行的列表是新的，但行内的元素引用还是旧的）；"
            "copy.deepcopy 递归复制所有层；修改 board[1][1] 后观察浅拷贝跟着变、深拷贝不变；"
            "用 id 对比内层行验证「共享」关系。"
            "讲解：浅拷贝=只复制第一层；深拷贝=层层复制；"
            "id(board[1])==id(board_shallow[1]) 为 True 就说明内层是同一份；"
            "处理嵌套数据（棋盘、表格）要备份时用 deepcopy 才安全。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 56,
        "title": "L12-56-C 队伍拆分不互相影响",
        "content": (
            "队伍拆分不互相影响。输入一行：8 个姓名（空格分隔）。请完成："
            "①用切片拷贝出 team_all = names[:]；②把前 4 人切给 A 队、后 4 人切给 B 队（都用切片）；"
            "③给 A 队 append 一名替补，观察 names 和 team_all 是否受影响并输出；"
            "④A 队把第一个队员换成「队长」，再输出所有列表确认互不影响；"
            "⑤输出四个列表的长度对比。"
        ),
        "answer": (
            "# 队伍拆分\n"
            "names = input().split()\n"
            "print(\"全体：\" + str(names))\n"
            "# 切片拷贝（返回新列表）\n"
            "team_all = names[:]\n"
            "team_a = names[:4]\n"
            "team_b = names[4:]\n"
            "print(\"A 队：\" + str(team_a))\n"
            "print(\"B 队：\" + str(team_b))\n"
            "# A 队加替补\n"
            "team_a.append(\"替补\")\n"
            "print(\"A 队加替补后：\" + str(team_a))\n"
            "print(\"全体受影响了吗：\" + str(names))\n"
            "print(\"team_all 受影响了吗：\" + str(team_all))\n"
            "# A 队换队长\n"
            "team_a[0] = \"队长\"\n"
            "print(\"A 队换队长后：\" + str(team_a))\n"
            "print(\"全体：\" + str(names))\n"
            "print(\"team_all：\" + str(team_all))\n"
            "print(\"长度对比：全体\" + str(len(names)) + \" team_all\" + str(len(team_all)) + \" A队\" + str(len(team_a)) + \" B队\" + str(len(team_b)))\n"
        ),
        "explanation": (
            "思路：切片 names[:] 和 names[:4] 都会返回新列表，之后的修改互不影响；"
            "append 和按下标赋值都只改自己的列表；最后对比长度验证独立性。"
            "讲解：切片是「复制」，和直接赋值（起外号）完全不同；"
            "[:] 复制全部，[:4] 复制前 4 个，[4:] 复制第 5 个起；"
            "想从大列表拆出独立的小列表，用切片最放心。"
        ),
        "sample_input": "小明 小红 小刚 小美 小华 小丽 小强 小芳\n",
    },
    {
        "topic_id": 56,
        "title": "L12-56-D 可变与不可变对比",
        "content": (
            "可变与不可变对比。输入两行：一个字符串、一个整数。请完成："
            "①把字符串赋给两个变量，修改其中一个（用 + 拼接新内容），观察另一个变不变；"
            "②把整数赋给两个变量，给其中一个 +10，观察另一个变不变；"
            "③把列表 [1,2,3] 赋给两个变量，append 一个元素，观察另一个变不变；"
            "④输出三组实验结果，总结：字符串和整数是「不可变」——修改其实是新建对象；"
            "列表是「可变」——原地修改，所有引用都看得见。"
        ),
        "answer": (
            "# 可变与不可变对比实验\n"
            "s = input()\n"
            "n = int(input())\n"
            "# 1. 字符串实验\n"
            "s1 = s\n"
            "s2 = s\n"
            "s1 = s1 + \"（改过）\"\n"
            "print(\"字符串 s1：\" + s1)\n"
            "print(\"字符串 s2：\" + s2)\n"
            "print(\"s2 变了吗：\" + str(s1 == s2))\n"
            "# 2. 整数实验\n"
            "n1 = n\n"
            "n2 = n\n"
            "n1 = n1 + 10\n"
            "print(\"整数 n1：\" + str(n1) + \"，n2：\" + str(n2))\n"
            "print(\"n2 变了吗：\" + str(n1 == n2))\n"
            "# 3. 列表实验\n"
            "base = [1, 2, 3]\n"
            "l1 = base\n"
            "l2 = base\n"
            "l1.append(4)\n"
            "print(\"列表 l1：\" + str(l1))\n"
            "print(\"列表 l2：\" + str(l2))\n"
            "print(\"l2 变了吗：\" + str(l1 == l2))\n"
            "print(\"结论：字符串、整数不可变，赋值后各自独立；列表可变，共享同一份会一起变\")\n"
        ),
        "explanation": (
            "思路：三组对照实验——字符串「修改」其实是让 s1 指向新字符串，s2 还指着旧的；"
            "整数同理；列表 append 是原地修改，l1 和 l2 指向同一份所以一起变。"
            "讲解：不可变对象（str/int/float/tuple）任何「修改」都会产生新对象；"
            "可变对象（list/dict）可以原地改，所有引用它的变量都会看到变化；"
            "这是理解「赋值=起外号」和「拷贝=复制」区别的根本。"
        ),
        "sample_input": "hello\n5\n",
    },
    {
        "topic_id": 56,
        "title": "L12-56-E 购物车的后悔药",
        "content": (
            "购物车的后悔药。输入一行：若干商品名（空格分隔）作为初始购物车。程序模拟三步操作："
            "①在修改前用 copy() 存档 snapshot；②对购物车执行：删除第一个商品、追加「神秘礼物」；"
            "③输出修改后的购物车。然后模拟「后悔」：把存档 snapshot 复制回来恢复（cart = snapshot.copy()），"
            "输出恢复后的购物车；最后对比恢复结果和初始输入是否一致（输出 True/False），"
            "并说明为什么恢复时要再 copy 一次。"
        ),
        "answer": (
            "# 购物车的后悔药\n"
            "cart = input().split()\n"
            "print(\"初始购物车：\" + str(cart))\n"
            "# 1. 修改前存档\n"
            "snapshot = cart.copy()\n"
            "print(\"存档：\" + str(snapshot))\n"
            "# 2. 修改购物车\n"
            "cart.pop(0)\n"
            "cart.append(\"神秘礼物\")\n"
            "print(\"修改后：\" + str(cart))\n"
            "# 3. 后悔了，恢复存档\n"
            "cart = snapshot.copy()\n"
            "print(\"恢复后：\" + str(cart))\n"
            "# 验证恢复结果\n"
            "same = cart == snapshot\n"
            "print(\"恢复结果和存档一致：\" + str(same))\n"
            "print(\"为什么再 copy：如果直接 cart = snapshot，之后改 cart 会连存档一起改掉，再 copy 一次才能让存档保持干净\")\n"
        ),
        "explanation": (
            "思路：修改前先 copy() 存档；pop(0) 删第一个、append 加新商品；"
            "后悔时从存档再 copy 一份回来恢复；最后 == 比较两个列表内容是否一致。"
            "讲解：列表 == 比较的是内容，不是身份（内容相同就是 True）；"
            "恢复时 cart = snapshot.copy() 而不是 cart = snapshot，"
            "否则两者又变成同一份，后续修改会污染存档——这是「备份要隔离」的核心思想。"
        ),
        "sample_input": "牛奶 面包 饼干\n",
    },
]
