"""批次1：L1-L4 (topic 45-48) 进阶题，每课 5 题，共 20 题。
参考解目标体量 10-15 行（软下限），全部本地沙箱实跑验证。
"""

QUESTIONS = [
    # ===================== L1 / topic 45 变量与标识符 =====================
    {
        "topic_id": 45,
        "title": "L1-45-A 宠物档案卡",
        "content": (
            "宠物档案卡。依次输入四行：宠物名字、年龄（整数）、体重（小数，单位千克）、最爱的玩具。"
            "请把它的档案打印出来：名字、实际年龄、体重、最爱的玩具各一行；"
            "再把年龄乘以 7 得到「换算年龄」并输出；最后判断：年龄小于 3 输出「它还小，要多陪它玩」，"
            "否则输出「它已经是大孩子啦」。"
        ),
        "answer": (
            "# 宠物档案卡\n"
            "name = input()           # 名字\n"
            "age = int(input())       # 年龄\n"
            "weight = float(input())  # 体重(千克)\n"
            "toy = input()            # 最爱的玩具\n"
            "dog_age = age * 7\n"
            "print(\"名字：\" + name)\n"
            "print(\"年龄：\" + str(age) + \" 岁\")\n"
            "print(\"体重：\" + str(weight) + \" 千克\")\n"
            "print(\"最爱的玩具：\" + toy)\n"
            "print(\"换算年龄：\" + str(dog_age) + \" 岁\")\n"
            "if age < 3:\n"
            "    print(\"它还小，要多陪它玩\")\n"
            "else:\n"
            "    print(\"它已经是大孩子啦\")\n"
        ),
        "explanation": (
            "思路：用 4 个变量分别接住四次 input() 的结果，年龄用 int()、体重用 float() 转换；"
            "再新建变量 dog_age 存换算年龄；最后用 if/else 按年龄输出不同评语。"
            "讲解：变量名要有意义（name/age/weight）；字符串和数字不能直接相加，要用 str() 转一下；"
            "input() 读进来的都是字符串，要参与计算必须先转类型。"
        ),
        "sample_input": "旺财\n3\n5.5\n皮球\n",
    },
    {
        "topic_id": 45,
        "title": "L1-45-B 文具小仓库",
        "content": (
            "文具小仓库。依次输入三行：铅笔支数、橡皮块数、尺子把数（都是整数）。"
            "请分别输出三种文具的数量，再输出文具总数；最后比较铅笔和橡皮："
            "如果铅笔更多，输出「铅笔比橡皮多 X 件」（X 是相差数量），否则输出「铅笔不比橡皮多」。"
        ),
        "answer": (
            "# 文具小仓库：统计三类文具\n"
            "pencil = int(input())\n"
            "eraser = int(input())\n"
            "ruler = int(input())\n"
            "total = pencil + eraser + ruler\n"
            "diff = pencil - eraser\n"
            "print(\"铅笔：\" + str(pencil) + \" 支\")\n"
            "print(\"橡皮：\" + str(eraser) + \" 块\")\n"
            "print(\"尺子：\" + str(ruler) + \" 把\")\n"
            "print(\"文具总数：\" + str(total) + \" 件\")\n"
            "if diff > 0:\n"
            "    print(\"铅笔比橡皮多 \" + str(diff) + \" 件\")\n"
            "else:\n"
            "    print(\"铅笔不比橡皮多\")\n"
        ),
        "explanation": (
            "思路：三个变量存三种文具数量，total 存总数、diff 存差值，先把算式结果存进变量再打印；"
            "用 if diff > 0 判断谁多。"
            "讲解：先把计算结果存进变量（total、diff）再用，代码更清楚；"
            "比较结果是 True/False，条件成立才执行缩进的语句。"
        ),
        "sample_input": "12\n4\n3\n",
    },
    {
        "topic_id": 45,
        "title": "L1-45-C 存钱罐计划",
        "content": (
            "存钱罐计划。依次输入四行：三次存钱的金额（整数，单位元）和一个玩具的价格（整数）。"
            "输出每次存了多少、一共存了多少；然后判断钱够不够买玩具："
            "够的话输出「买得起玩具，还剩 X 元」，不够的话输出「还差 X 元才能买玩具」。"
        ),
        "answer": (
            "# 存钱罐：三次存钱 + 买玩具\n"
            "money1 = int(input())\n"
            "money2 = int(input())\n"
            "money3 = int(input())\n"
            "price = int(input())\n"
            "total = money1 + money2 + money3\n"
            "print(\"第一次存：\" + str(money1) + \" 元\")\n"
            "print(\"第二次存：\" + str(money2) + \" 元\")\n"
            "print(\"第三次存：\" + str(money3) + \" 元\")\n"
            "print(\"一共存了：\" + str(total) + \" 元\")\n"
            "if total >= price:\n"
            "    left = total - price\n"
            "    print(\"买得起玩具，还剩 \" + str(left) + \" 元\")\n"
            "else:\n"
            "    print(\"还差 \" + str(price - total) + \" 元才能买玩具\")\n"
        ),
        "explanation": (
            "思路：三个变量记三次存钱，total 求和；用 total >= price 判断够不够，"
            "够的话再算剩余，不够就算差价。"
            "讲解：left 这种只在分支里用的变量可以放在 if 内部；"
            "「够不够」用 >= 判断，注意等号不能漏（正好够也算够）。"
        ),
        "sample_input": "20\n15\n10\n40\n",
    },
    {
        "topic_id": 45,
        "title": "L1-45-D 成长记录",
        "content": (
            "成长记录。依次输入三行：姓名、年龄（整数）、身高（小数，单位厘米）。"
            "请输出：姓名一行；今年年龄和身高一行；明年预计身高（每年按长 5 厘米算）；"
            "到 18 岁还能长多少年；预计成年身高（今年身高 + 剩余年数 × 5）。"
            "最后判断：预计成年身高大于等于 170 输出「会长得很高哦」，否则输出「多吃饭多运动，还能再长」。"
        ),
        "answer": (
            "# 成长记录：身高预测\n"
            "name = input()\n"
            "age = int(input())\n"
            "height = float(input())\n"
            "next_height = height + 5\n"
            "grow_years = 18 - age\n"
            "final_height = height + grow_years * 5\n"
            "print(\"姓名：\" + name)\n"
            "print(\"今年 \" + str(age) + \" 岁，身高 \" + str(height) + \" 厘米\")\n"
            "print(\"明年预计身高：\" + str(next_height) + \" 厘米\")\n"
            "print(\"到 18 岁大约还能长 \" + str(grow_years) + \" 年\")\n"
            "print(\"预计成年身高：\" + str(final_height) + \" 厘米\")\n"
            "if final_height >= 170:\n"
            "    print(\"会长得很高哦\")\n"
            "else:\n"
            "    print(\"多吃饭多运动，还能再长\")\n"
        ),
        "explanation": (
            "思路：先算明年身高（+5），再算还能长几年（18-age），最后算成年身高（身高+年数×5），"
            "一步一步把中间结果存进变量。"
            "讲解：复杂计算拆成几个小变量（next_height、grow_years、final_height），"
            "每步只做一件事，出错时容易检查；乘法 * 比加法优先，必要时加括号。"
        ),
        "sample_input": "小明\n10\n140.5\n",
    },
    {
        "topic_id": 45,
        "title": "L1-45-E 水果派对",
        "content": (
            "水果派对。准备三种水果，每种输入两行：水果名、数量（整数），共输入六行。"
            "先输出「水果清单：」，再逐行输出每种水果和数量，然后输出水果总数；"
            "最后判断：总数大于等于 10 输出「水果够开派对啦」，否则输出「水果还不够，再去买点吧」。"
        ),
        "answer": (
            "# 水果派对：三种水果入库\n"
            "fruit1 = input()\n"
            "count1 = int(input())\n"
            "fruit2 = input()\n"
            "count2 = int(input())\n"
            "fruit3 = input()\n"
            "count3 = int(input())\n"
            "total = count1 + count2 + count3\n"
            "print(\"水果清单：\")\n"
            "print(fruit1 + \"：\" + str(count1) + \" 个\")\n"
            "print(fruit2 + \"：\" + str(count2) + \" 个\")\n"
            "print(fruit3 + \"：\" + str(count3) + \" 个\")\n"
            "print(\"水果总数：\" + str(total) + \" 个\")\n"
            "if total >= 10:\n"
            "    print(\"水果够开派对啦\")\n"
            "else:\n"
            "    print(\"水果还不够，再去买点吧\")\n"
        ),
        "explanation": (
            "思路：水果名和数量成对出现，就用 fruit1/count1 这样成对的变量名；"
            "总数 = 三个数量相加；最后按总数判断够不够。"
            "讲解：输入顺序和 input() 的顺序要一一对应；"
            "成对的信息用成对的变量名（fruit1 配 count1），读代码时不容易乱。"
        ),
        "sample_input": "苹果\n5\n香蕉\n3\n橙子\n4\n",
    },

    # ===================== L2 / topic 46 注释与输出函数 =====================
    {
        "topic_id": 46,
        "title": "L2-46-A 火箭发射倒计时",
        "content": (
            "火箭发射倒计时。不需要输入。先打印「倒计时开始：」，然后用循环让数字 5 到 1 "
            "用空格连在同一行显示（如 `5 4 3 2 1 `），接着换行打印「点火！」；"
            "再用 sep 把「火箭」「升空」「成功」三个词用箭头 → 连成一行打印；"
            "最后用 end 让「任务完成」后面跟一个感叹号而不是换行。请给关键语句加上注释。"
        ),
        "answer": (
            "# 火箭发射倒计时\n"
            "print(\"倒计时开始：\")\n"
            "for i in range(5, 0, -1):      # 从 5 倒数到 1\n"
            "    print(i, end=\" \")          # 数字之间用空格连着\n"
            "print()                        # 补一个换行\n"
            "print(\"点火！\")\n"
            "# sep 决定多个参数之间的连接符号\n"
            "print(\"火箭\", \"升空\", \"成功\", sep=\"→\")\n"
            "# end 决定 print 结尾的字符，默认是换行\n"
            "print(\"任务完成\", end=\"！\")\n"
            "print()                        # 最后补换行，输出更整洁\n"
        ),
        "explanation": (
            "思路：range(5, 0, -1) 生成 5 到 1 的倒序数字，循环里用 end=\" \" 让它们连成一行；"
            "循环结束后补一个空 print() 换行；sep=\"→\" 把三个词连起来；end=\"！\" 改变结尾字符。"
            "讲解：end 控制 print 结尾，默认是换行符；sep 控制多个参数之间的分隔；"
            "关键语句写注释是好习惯，方便别人和自己看懂代码。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 46,
        "title": "L2-46-B 小餐厅菜单",
        "content": (
            "小餐厅菜单。输入四行：第一道菜的名字、价格，第二道菜的名字、价格（价格为整数）。"
            "先打印「今日菜单」并用 = 号连出 20 个等号做分隔线；然后每道菜一行，"
            "菜名和价格之间用「……」连接（用 sep 实现）；再打印一条 20 个等号的分隔线；"
            "最后用 end 让「谢谢光临」和「欢迎下次再来！」连在同一行。"
        ),
        "answer": (
            "# 小餐厅菜单\n"
            "dish1 = input()\n"
            "price1 = input()\n"
            "dish2 = input()\n"
            "price2 = input()\n"
            "print(\"今日菜单\", \"=\" * 20, sep=\"\")\n"
            "print(dish1, price1 + \" 元\", sep=\"……\")\n"
            "print(dish2, price2 + \" 元\", sep=\"……\")\n"
            "print(\"=\" * 20)\n"
            "# 用 end 把两句话连在同一行\n"
            "print(\"谢谢光临\", end=\"，\")\n"
            "print(\"欢迎下次再来！\")\n"
        ),
        "explanation": (
            "思路：四个 input() 读两道菜；\"=\" * 20 生成 20 个等号当分隔线；"
            "sep=\"……\" 让菜名和价格用省略号连接；结尾用 end=\"，\" 把两句感谢语连起来。"
            "讲解：字符串乘以数字会重复拼接（\"=\" * 20 就是 20 个等号）；"
            "sep 是两个参数之间的连接符，和 end（整句结尾）不一样，别搞混。"
        ),
        "sample_input": "番茄炒蛋\n12\n蒸蛋羹\n8\n",
    },
    {
        "topic_id": 46,
        "title": "L2-46-C 我的姓名徽章",
        "content": (
            "我的姓名徽章。输入三行：姓名、班级、座右铭。请用 print 拼出一个徽章框："
            "上下边框是 + 号加 18 个减号；中间三行分别是「姓名：」「班级：」「座右铭：」加上输入的内容；"
            "姓名行和班级行请用 end=\"\" 把标签和内容分两次 print 拼在同一行。"
        ),
        "answer": (
            "# 我的姓名徽章\n"
            "name = input()\n"
            "class_no = input()\n"
            "motto = input()\n"
            "print(\"+\" + \"-\" * 18 + \"+\")     # 上边框\n"
            "print(\"| 姓名：\", end=\"\")        # 先打印标签，不换行\n"
            "print(name)                      # 再接上名字\n"
            "print(\"| 班级：\", end=\"\")\n"
            "print(class_no)\n"
            "print(\"| 座右铭：\" + motto)\n"
            "print(\"+\" + \"-\" * 18 + \"+\")     # 下边框\n"
            "# 徽章完成\n"
        ),
        "explanation": (
            "思路：边框用 \"+\" + \"-\" * 18 + \"+\" 拼出来；姓名和班级两行先用 end=\"\" 打印标签不换行，"
            "再 print 内容，两次输出就拼在了同一行。"
            "讲解：end=\"\" 表示结尾什么都不加（连换行都没有），这样下一次 print 会紧跟着；"
            "字符串可以直接用 + 拼接，但数字要先 str() 再拼。"
        ),
        "sample_input": "小明\n三(2)班\n天天向上\n",
    },
    {
        "topic_id": 46,
        "title": "L2-46-D 3的乘法口诀一行展示",
        "content": (
            "3 的乘法口诀一行展示。不需要输入。先打印「3 的乘法口诀：」，"
            "然后用循环让 3x1=3、3x2=6 一直到 3x9=27 用两个空格连在同一行显示；"
            "循环结束后换行，再用 end 分三段打印「口诀一共」「9」「句」，让它们拼成一句话。"
        ),
        "answer": (
            "# 打印 3 的乘法口诀（一行展示）\n"
            "print(\"3 的乘法口诀：\")\n"
            "for i in range(1, 10):          # 1 到 9\n"
            "    result = 3 * i\n"
            "    print(\"3x\" + str(i) + \"=\" + str(result), end=\"  \")\n"
            "print()                          # 补换行\n"
            "# 用 end 把三段话拼成一句\n"
            "print(\"口诀一共\", end=\" \")\n"
            "print(9, end=\" \")\n"
            "print(\"句\")\n"
        ),
        "explanation": (
            "思路：循环 1 到 9，每次先算 3*i 存进 result，再拼成「3x2=6」这样的字符串；"
            "end=\"  \" 让每句口诀之间空两格且不换行；最后三段话用 end=\" \" 拼成一句。"
            "讲解：字符串拼接时数字必须 str()；range(1, 10) 包含 1 不包含 10；"
            "循环结束后记得 print() 补一个换行，不然后面的内容会粘在一起。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 46,
        "title": "L2-46-E 班级留言板",
        "content": (
            "班级留言板。输入三行：三条留言内容。先输出「三条留言：」，并用 sep 把三条留言用「 | 」"
            "连在一行展示；再输出「合并成一段话：」，用 end 把三条留言用分号连成一段；"
            "最后统计三条留言的总字数并输出「留言一共有 X 个字」。"
        ),
        "answer": (
            "# 留言板：把三条留言连成一段\n"
            "msg1 = input()\n"
            "msg2 = input()\n"
            "msg3 = input()\n"
            "print(\"三条留言：\")\n"
            "print(msg1, msg2, msg3, sep=\" | \")   # 竖线分隔展示\n"
            "print(\"合并成一段话：\")\n"
            "print(msg1, end=\"；\")\n"
            "print(msg2, end=\"；\")\n"
            "print(msg3)\n"
            "# 统计留言总字数\n"
            "total = len(msg1) + len(msg2) + len(msg3)\n"
            "print(\"留言一共有 \" + str(total) + \" 个字\")\n"
        ),
        "explanation": (
            "思路：三个变量存三条留言；一次 print 传三个参数用 sep=\" | \" 展示；"
            "再用 end=\"；\" 把前两条结尾换成分号，拼成一段话；len() 求每条字数再相加。"
            "讲解：sep 是「参数之间」的分隔符，一次 print 多个参数才有用；"
            "len(字符串) 返回字符个数，中文也算一个字符。"
        ),
        "sample_input": "今天很开心\n学会了print\n继续加油\n",
    },

    # ===================== L3 / topic 47 数值类型与字符串格式化 =====================
    {
        "topic_id": 47,
        "title": "L3-47-A 超市小票",
        "content": (
            "超市小票。输入三行：商品名、单价（小数）、购买数量（整数）。"
            "请用 f-string 打印一张小票：商品名、单价（保留 2 位小数）、数量、小计（单价×数量，保留 2 位小数）；"
            "再按付款 100 元计算并输出找零（保留 2 位小数）；若找零为负，输出「钱不够，还差 X 元」。"
        ),
        "answer": (
            "# 超市小票：f-string 格式化\n"
            "name = input()\n"
            "price = float(input())\n"
            "count = int(input())\n"
            "total = price * count\n"
            "print(f\"商品：{name}\")\n"
            "print(f\"单价：{price:.2f} 元\")\n"
            "print(f\"数量：{count}\")\n"
            "print(f\"小计：{total:.2f} 元\")\n"
            "pay = 100\n"
            "change = pay - total\n"
            "print(f\"付款：{pay} 元\")\n"
            "print(f\"找零：{change:.2f} 元\")\n"
            "if change < 0:\n"
            "    print(f\"钱不够，还差 {-change:.2f} 元\")\n"
        ),
        "explanation": (
            "思路：单价 float()、数量 int()，小计直接相乘；f-string 里 {price:.2f} 保留两位小数；"
            "找零 = 100 - 小计，为负时再输出差额。"
            "讲解：:.2f 表示保留 2 位小数，:.1f 保留 1 位；"
            "f-string 里可以直接写表达式（如 {-change:.2f}），负号会先取相反数再格式化。"
        ),
        "sample_input": "笔记本\n8.5\n3\n",
    },
    {
        "topic_id": 47,
        "title": "L3-47-B 体温记录单",
        "content": (
            "体温记录单。输入两行：姓名、体温（小数）。请输出："
            "「姓名 的体温是 X 摄氏度」（保留 1 位小数）；和标准体温 36.5 相差多少度（保留 1 位小数）；"
            "然后判断：体温大于 37.3 输出「体温偏高，要多喝水休息」，低于 36.0 输出「体温偏低，要注意保暖」，"
            "其余输出「体温正常，真棒」；最后用一行输出体温状态「正常」（不超过 37.3）或「偏高」。"
        ),
        "answer": (
            "# 体温记录单\n"
            "name = input()\n"
            "temp = float(input())\n"
            "diff = temp - 36.5\n"
            "print(f\"{name} 的体温是 {temp:.1f} 摄氏度\")\n"
            "print(f\"和标准体温 36.5 相差 {diff:.1f} 度\")\n"
            "if temp > 37.3:\n"
            "    print(\"体温偏高，要多喝水休息\")\n"
            "elif temp < 36.0:\n"
            "    print(\"体温偏低，要注意保暖\")\n"
            "else:\n"
            "    print(\"体温正常，真棒\")\n"
            "# 三元表达式给出简短状态\n"
            "status = \"正常\" if temp <= 37.3 else \"偏高\"\n"
            "print(f\"体温状态：{status}\")\n"
        ),
        "explanation": (
            "思路：体温 float() 后先算和 36.5 的差；用 if/elif/else 分三种情况输出建议；"
            "最后用「A if 条件 else B」的三元表达式一行得出状态。"
            "讲解：:.1f 保留 1 位小数；elif 是「否则如果」，多个分支从上往下找到第一个成立的；"
            "三元表达式适合简单二选一，复杂判断还是用 if/else 更清楚。"
        ),
        "sample_input": "小明\n36.8\n",
    },
    {
        "topic_id": 47,
        "title": "L3-47-C 长方形名片",
        "content": (
            "长方形名片。输入两行：长方形的长、宽（都可为小数，单位厘米）。"
            "请用 f-string 依次输出：长（1 位小数）、宽（1 位小数）、周长（1 位小数）、"
            "面积（2 位小数）、对角线长度（2 位小数，用「长的平方+宽的平方」再开方，即 ** 0.5）。"
            "最后判断：面积大于等于 100 输出「这是一张大名片」，否则输出「这是一张小名片」。"
        ),
        "answer": (
            "# 长方形名片\n"
            "length = float(input())\n"
            "width = float(input())\n"
            "perimeter = (length + width) * 2\n"
            "area = length * width\n"
            "diagonal = (length ** 2 + width ** 2) ** 0.5\n"
            "print(f\"长：{length:.1f} 厘米\")\n"
            "print(f\"宽：{width:.1f} 厘米\")\n"
            "print(f\"周长：{perimeter:.1f} 厘米\")\n"
            "print(f\"面积：{area:.2f} 平方厘米\")\n"
            "print(f\"对角线：{diagonal:.2f} 厘米\")\n"
            "if area >= 100:\n"
            "    print(\"这是一张大名片\")\n"
            "else:\n"
            "    print(\"这是一张小名片\")\n"
        ),
        "explanation": (
            "思路：长宽用 float() 读入；周长=(长+宽)×2；面积=长×宽；"
            "对角线用 length**2 + width**2 再 **0.5 开平方；最后按面积判断大小。"
            "讲解：** 是乘方，x**2 是平方，x**0.5 是开平方；"
            "先算中间结果存变量（perimeter/area/diagonal），print 时只做格式化，不容易出错。"
        ),
        "sample_input": "12.5\n8\n",
    },
    {
        "topic_id": 47,
        "title": "L3-47-D 零花钱换算器",
        "content": (
            "零花钱换算器。输入一行：一笔零花钱金额（小数，单位元）。"
            "请输出：人民币金额（2 位小数）；换算成多少角（整数，1 元=10 角）；换算成多少分（整数，1 元=100 分）；"
            "按 1 美元 = 7.2 元换算成美元（2 位小数）；最后用 type() 分别输出金额变量和「角」变量的类型。"
        ),
        "answer": (
            "# 零花钱换算器\n"
            "rmb = float(input())\n"
            "jiao = int(rmb * 10)\n"
            "fen = int(rmb * 100)\n"
            "usd = rmb / 7.2\n"
            "print(f\"人民币：{rmb:.2f} 元\")\n"
            "print(f\"换算成角：{jiao} 角\")\n"
            "print(f\"换算成分：{fen} 分\")\n"
            "print(f\"大约可换：{usd:.2f} 美元\")\n"
            "print(\"类型检查：\")\n"
            "print(\"rmb 是\", str(type(rmb)))\n"
            "print(\"jiao 是\", str(type(jiao)))\n"
        ),
        "explanation": (
            "思路：金额 float() 读入；乘 10、乘 100 后用 int() 取整得到角和分；"
            "除以 7.2 得美元；type() 可以看变量是什么类型。"
            "讲解：int() 会直接去掉小数部分（不是四舍五入）；"
            "type() 返回 <class 'float'> 这样的类型对象，打印时用 str() 包一下更清楚；"
            "float 是浮点数（小数），int 是整数，两者参与运算结果会不同。"
        ),
        "sample_input": "66.6\n",
    },
    {
        "topic_id": 47,
        "title": "L3-47-E 跑步成绩单",
        "content": (
            "跑步成绩单。输入三行：选手姓名、跑步距离（米，整数即可）、用时（秒，整数即可）。"
            "请输出：选手姓名；距离和用时一行；速度（米/秒，2 位小数）；换算成千米/小时（速度×3.6，2 位小数）；"
            "每千米用时（秒，取整）。最后判断：千米/小时大于等于 10 输出「选手名 跑得真快！」，"
            "否则输出「继续练习，会更快」。"
        ),
        "answer": (
            "# 跑步成绩单\n"
            "name = input()\n"
            "meters = float(input())\n"
            "seconds = float(input())\n"
            "speed = meters / seconds\n"
            "kmh = speed * 3.6\n"
            "per_km = seconds / (meters / 1000)\n"
            "print(f\"选手：{name}\")\n"
            "print(f\"距离：{meters:.0f} 米，用时 {seconds:.0f} 秒\")\n"
            "print(f\"速度：{speed:.2f} 米/秒\")\n"
            "print(f\"合 {kmh:.2f} 千米/小时\")\n"
            "print(f\"每千米用时：{per_km:.0f} 秒\")\n"
            "if kmh >= 10:\n"
            "    print(f\"{name} 跑得真快！\")\n"
            "else:\n"
            "    print(\"继续练习，会更快\")\n"
        ),
        "explanation": (
            "思路：速度=距离÷时间；米/秒乘 3.6 就是千米/小时；每千米用时 = 总时间 ÷ (距离/1000)；"
            "先算好中间变量再逐行打印，最后按 kmh 判断。"
            "讲解：:.0f 表示不保留小数（四舍五入到整数）；"
            "换算关系记住：1 米/秒 = 3.6 千米/小时；除法的除数是一个式子时要加括号。"
        ),
        "sample_input": "小明\n400\n95\n",
    },

    # ===================== L4 / topic 48 运算符、输入函数与转义字符 =====================
    {
        "topic_id": 48,
        "title": "L4-48-A 分糖果",
        "content": (
            "分糖果。输入两行：糖果总数、小朋友人数（都是整数）。"
            "请用 // 和 % 计算并输出：糖果总数、人数、每人分到几颗、剩下几颗；"
            "如果正好分完输出「正好分完，真公平」，否则输出「剩下的 X 颗给老师吧」；"
            "最后用「每人×人数+剩余」验算并输出结果。"
        ),
        "answer": (
            "# 分糖果\n"
            "candy = int(input())\n"
            "kids = int(input())\n"
            "each = candy // kids\n"
            "left = candy % kids\n"
            "print(f\"糖果总数：{candy} 颗\")\n"
            "print(f\"小朋友人数：{kids} 人\")\n"
            "print(f\"每人分到：{each} 颗\")\n"
            "print(f\"剩下：{left} 颗\")\n"
            "if left == 0:\n"
            "    print(\"正好分完，真公平\")\n"
            "else:\n"
            "    print(\"剩下的 \" + str(left) + \" 颗给老师吧\")\n"
            "double_check = each * kids + left\n"
            "print(f\"验算：{each}x{kids}+{left}={double_check}\")\n"
        ),
        "explanation": (
            "思路：// 是整除（每人几颗），% 是取余（剩下几颗）；用 left == 0 判断是否正好分完；"
            "最后用 each*kids+left 验算是否等于总数。"
            "讲解：// 和 / 不同：10/3 得 3.333…，10//3 得 3；"
            "判断「相等」用 ==（两个等号），一个等号是赋值；养成验算习惯可以及早发现错误。"
        ),
        "sample_input": "35\n6\n",
    },
    {
        "topic_id": 48,
        "title": "L4-48-B 秒数换算时分秒",
        "content": (
            "秒数换算。输入一行：总秒数（整数）。请用 // 和 % 把它换算成「X 小时 Y 分 Z 秒」："
            "先算小时（总秒数 // 3600），剩余秒数对 3600 取余；再算分钟（剩余 // 60）和秒（剩余 % 60）。"
            "输出三行：总秒数、「等于 X 小时 Y 分 Z 秒」、以及用制表符 \\t 分隔的三个数字；"
            "判断是否超过一小时并输出提示；最后验算回去（小时×3600+分×60+秒）并输出。"
        ),
        "answer": (
            "# 秒数换算成时分秒\n"
            "total = int(input())\n"
            "hours = total // 3600\n"
            "left = total % 3600\n"
            "minutes = left // 60\n"
            "seconds = left % 60\n"
            "print(f\"总秒数：{total} 秒\")\n"
            "print(f\"等于 {hours} 小时 {minutes} 分 {seconds} 秒\")\n"
            "print(f\"{hours}\\t{minutes}\\t{seconds}\")   # 制表符对齐\n"
            "if hours >= 1:\n"
            "    print(\"超过一个小时啦\")\n"
            "else:\n"
            "    print(\"还不到一小时\")\n"
            "# 验算回去\n"
            "back = hours * 3600 + minutes * 60 + seconds\n"
            "print(f\"验算：{back} 秒\")\n"
        ),
        "explanation": (
            "思路：1 小时=3600 秒，1 分=60 秒；先整除得小时，取余得剩余；剩余再整除得分、取余得秒；"
            "\\t 是制表符（跳格对齐），最后把时分秒换算回秒验算。"
            "讲解：大单位换算小单位用乘，小单位凑大单位用 // 和 % 组合；"
            "\\t、\\n 这类转义字符写在字符串里会变成特殊符号，不是字面的反斜杠。"
        ),
        "sample_input": "5025\n",
    },
    {
        "topic_id": 48,
        "title": "L4-48-C 幂运算小表",
        "content": (
            "幂运算小表。输入两行：底数 a、指数 n（都是整数）。"
            "请计算并输出：a 的 n 次方、a 的 n+1 次方、两者相差多少；"
            "然后用制表符 \\t 做一个两行的小表格（第一列是指数，第二列是结果）；"
            "最后判断：a 的 n+1 次方超过 1000 输出「增长速度真快！」，否则输出「还在慢慢增长」。"
        ),
        "answer": (
            "# 幂运算小表\n"
            "a = int(input())\n"
            "n = int(input())\n"
            "p1 = a ** n\n"
            "p2 = a ** (n + 1)\n"
            "gap = p2 - p1\n"
            "print(f\"底数 a = {a}，指数 n = {n}\")\n"
            "print(f\"{a} 的 {n} 次方 = {p1}\")\n"
            "print(f\"{a} 的 {n+1} 次方 = {p2}\")\n"
            "print(f\"两者相差：{gap}\")\n"
            "print(\"指数\\t结果\")          # 制表符排版\n"
            "print(str(n) + \"\\t\" + str(p1))\n"
            "print(str(n + 1) + \"\\t\" + str(p2))\n"
            "if p2 > 1000:\n"
            "    print(\"增长速度真快！\")\n"
            "else:\n"
            "    print(\"还在慢慢增长\")\n"
        ),
        "explanation": (
            "思路：** 是幂运算，a**n 表示 a 的 n 次方；先算两个幂和差值，再用 \\t 做对齐小表格；"
            "最后按 p2 是否超过 1000 输出不同评语。"
            "讲解：a ** (n+1) 要加括号，因为 ** 优先级很高；"
            "\\t 让前后内容跳到固定列对齐，适合做简单表格；幂增长非常快，这就是「指数爆炸」。"
        ),
        "sample_input": "3\n5\n",
    },
    {
        "topic_id": 48,
        "title": "L4-48-D 温度换算单",
        "content": (
            "温度换算单。输入一行：摄氏温度（可为小数）。按公式「华氏 = 摄氏 × 9 ÷ 5 + 32」换算。"
            "请输出：标题「温度换算单：」；用制表符 \\t 做一行表头「摄氏度\\t华氏度」和一行数据；"
            "再用 f-string 输出一句完整换算说明（各保留 1 位小数）；输出两种温标相差多少度（1 位小数）；"
            "最后判断：华氏度大于等于 100 输出「华氏度到 100 啦，很热」，否则输出「天气还算凉爽」。"
        ),
        "answer": (
            "# 摄氏度转华氏度\n"
            "c = float(input())\n"
            "f = c * 9 / 5 + 32\n"
            "diff = f - c\n"
            "print(\"温度换算单：\")\n"
            "print(\"摄氏度\\t华氏度\")           # 转义制表符\n"
            "print(str(c) + \"\\t\" + str(round(f, 1)))\n"
            "print(f\"{c:.1f} 摄氏度 = {f:.1f} 华氏度\")\n"
            "print(f\"两种温标相差 {diff:.1f} 度\")\n"
            "if f >= 100:\n"
            "    print(\"华氏度到 100 啦，很热\")\n"
            "else:\n"
            "    print(\"天气还算凉爽\")\n"
        ),
        "explanation": (
            "思路：float() 读摄氏温度，按公式 c*9/5+32 算华氏度；\\t 做表头和数据对齐；"
            "round(f, 1) 是四舍五入保留 1 位；最后按华氏度判断冷热。"
            "讲解：乘除从左到右算，c*9/5 等价于 (c*9)/5；"
            "round(x, 1) 是函数式四舍五入，:.1f 是格式化显示，两者结果可能有细微差别；"
            "转义字符 \\t 让表格列对齐。"
        ),
        "sample_input": "38.5\n",
    },
    {
        "topic_id": 48,
        "title": "L4-48-E 购物找零",
        "content": (
            "购物找零。输入四行：商品名、单价（小数）、数量（整数）、付款金额（小数）。"
            "请用制表符 \\t 输出表头「商品\\t单价\\t数量」和一行数据；再输出应付金额、付款金额（保留 2 位小数）；"
            "判断：钱够就输出「找零：X 元」，不够就输出「钱不够，还差 X 元」（保留 2 位小数）；"
            "最后用转义换行符 \\n 在一句 print 里分两行输出「谢谢惠顾」和「欢迎下次光临」。"
        ),
        "answer": (
            "# 购物找零\n"
            "item = input()\n"
            "price = float(input())\n"
            "count = int(input())\n"
            "pay = float(input())\n"
            "total = price * count\n"
            "change = pay - total\n"
            "print(\"商品\\t单价\\t数量\")\n"
            "print(item + \"\\t\" + str(price) + \"\\t\" + str(count))\n"
            "print(f\"应付：{total:.2f} 元\")\n"
            "print(f\"付款：{pay:.2f} 元\")\n"
            "if change >= 0:\n"
            "    print(f\"找零：{change:.2f} 元\")\n"
            "else:\n"
            "    print(f\"钱不够，还差 {-change:.2f} 元\")\n"
            "print(\"谢谢惠顾\\n欢迎下次光临\")     # 转义换行\n"
        ),
        "explanation": (
            "思路：应付=单价×数量，找零=付款-应付；\\t 对齐表格列；change 为负时用 -change 取正数输出差额；"
            "最后一句 print 里放 \\n 就能一条语句打两行。"
            "讲解：\\n 是换行转义符，一个 print 也能输出多行；"
            "f-string 中 {-change:.2f} 先把负数变正再保留两位小数；"
            "判断钱够不够用 change >= 0，正好够也算够。"
        ),
        "sample_input": "铅笔\n2.5\n4\n20\n",
    },
]
