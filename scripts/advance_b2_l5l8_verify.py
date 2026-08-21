"""批次2：L5-L8 (topic 49-52) 进阶题，每课 5 题，共 20 题。
L5+ 参考解目标体量 20-50 行，综合前面课知识。
"""

QUESTIONS = [
    # ===================== L5 / topic 49 if判断、比较运算符、逻辑运算符 =====================
    {
        "topic_id": 49,
        "title": "L5-49-A 游乐园身高检票",
        "content": (
            "游乐园身高检票。依次输入三行：姓名、身高（厘米，整数）、年龄（整数）。"
            "检票规则：身高大于等于 140 才能玩「过山车」；身高大于等于 120 且年龄大于等于 6 才能玩「碰碰车」；"
            "身高小于 120 只能玩「旋转木马」。请逐条用 if 判断并输出该小朋友能玩的项目；"
            "每个项目一行：能玩输出「可以玩：项目名」，不能玩输出「暂不能玩：项目名」。"
            "最后输出一句总结：能玩的项目数量。"
        ),
        "answer": (
            "# 游乐园身高检票\n"
            "name = input()\n"
            "height = int(input())\n"
            "age = int(input())\n"
            "can_play = 0\n"
            "print(name + \" 的身高 \" + str(height) + \" 厘米，年龄 \" + str(age))\n"
            "# 过山车：身高 >= 140\n"
            "if height >= 140:\n"
            "    print(\"可以玩：过山车\")\n"
            "    can_play = can_play + 1\n"
            "else:\n"
            "    print(\"暂不能玩：过山车\")\n"
            "# 碰碰车：身高 >= 120 且 年龄 >= 6\n"
            "if height >= 120 and age >= 6:\n"
            "    print(\"可以玩：碰碰车\")\n"
            "    can_play = can_play + 1\n"
            "else:\n"
            "    print(\"暂不能玩：碰碰车\")\n"
            "# 旋转木马：身高 < 120\n"
            "if height < 120:\n"
            "    print(\"可以玩：旋转木马\")\n"
            "    can_play = can_play + 1\n"
            "else:\n"
            "    print(\"旋转木马对所有人开放，可以玩\")\n"
            "    can_play = can_play + 1\n"
            "print(\"一共能玩 \" + str(can_play) + \" 个项目\")\n"
        ),
        "explanation": (
            "思路：每个项目用独立的 if/else 判断，条件用到 and（并且）连接两个条件；"
            "用 can_play 计数器统计能玩的项目数，每满足一个就 +1。"
            "讲解：and 表示两个条件都要成立；or 表示任一成立即可；"
            "计数器模式（先设 0，满足就 +1）是统计数量的常用套路。"
        ),
        "sample_input": "小明\n135\n9\n",
    },
    {
        "topic_id": 49,
        "title": "L5-49-B 三科成绩评优",
        "content": (
            "三科成绩评优。输入四行：姓名、语文、数学、英语成绩（后三个为整数）。"
            "评优规则（用 and/or/not 组合判断）："
            "①三科都大于等于 90 → 输出「三好学生」；"
            "②平均分大于等于 85 且没有一科低于 60 → 输出「优秀学生」；"
            "③至少有一科大于等于 95 → 输出「单科小达人」；"
            "④以上都不满足 → 输出「继续加油」。请每条规则单独判断（不互斥，可同时满足多条），"
            "最后输出三科总分和平均分（1 位小数）。"
        ),
        "answer": (
            "# 三科成绩评优\n"
            "name = input()\n"
            "chinese = int(input())\n"
            "math = int(input())\n"
            "english = int(input())\n"
            "total = chinese + math + english\n"
            "avg = total / 3\n"
            "print(name + \" 的成绩：语文 \" + str(chinese) + \"，数学 \" + str(math) + \"，英语 \" + str(english))\n"
            "# 规则1：三科都 >= 90\n"
            "if chinese >= 90 and math >= 90 and english >= 90:\n"
            "    print(\"荣誉：三好学生\")\n"
            "# 规则2：平均 >= 85 且没有一科 < 60\n"
            "no_fail = not (chinese < 60 or math < 60 or english < 60)\n"
            "if avg >= 85 and no_fail:\n"
            "    print(\"荣誉：优秀学生\")\n"
            "# 规则3：至少一科 >= 95\n"
            "if chinese >= 95 or math >= 95 or english >= 95:\n"
            "    print(\"荣誉：单科小达人\")\n"
            "# 规则4：都不满足\n"
            "r1 = chinese >= 90 and math >= 90 and english >= 90\n"
            "r2 = avg >= 85 and no_fail\n"
            "r3 = chinese >= 95 or math >= 95 or english >= 95\n"
            "if not (r1 or r2 or r3):\n"
            "    print(\"继续加油\")\n"
            "print(\"总分：\" + str(total))\n"
            "print(\"平均分：\" + str(round(avg, 1)))\n"
        ),
        "explanation": (
            "思路：四条规则各自独立判断；no_fail 用 not 取反「有科目不及格」得到「没有科目不及格」；"
            "规则 4 先把前三条结果存成 r1/r2/r3，再用 not(r1 or r2 or r3) 判断全不满足。"
            "讲解：not 把 True 变 False、False 变 True；德摩根思想：「没有一科低于60」=「不是（有一科低于60）」；"
            "把复杂条件拆成中间变量（r1/r2/r3）能让逻辑更清楚。"
        ),
        "sample_input": "小明\n92\n88\n95\n",
    },
    {
        "topic_id": 49,
        "title": "L5-49-C 密码强度检测",
        "content": (
            "密码强度检测。输入一行：一个密码字符串。用 len() 和字符串判断方法检测："
            "长度是否大于等于 8；是否包含数字（用 any(c.isdigit() for c in pwd) 或循环判断）；"
            "是否包含大写字母；是否包含小写字母。请分别输出这四项的检测结果（True/False）；"
            "然后统计满足的项数：4 项全满足输出「强密码」，满足 3 项输出「中等密码」，"
            "否则输出「弱密码，请加强」。"
        ),
        "answer": (
            "# 密码强度检测\n"
            "pwd = input()\n"
            "length_ok = len(pwd) >= 8\n"
            "has_digit = False\n"
            "has_upper = False\n"
            "has_lower = False\n"
            "# 用循环逐个字符判断\n"
            "i = 0\n"
            "while i < len(pwd):\n"
            "    c = pwd[i]\n"
            "    if c.isdigit():\n"
            "        has_digit = True\n"
            "    if c.isupper():\n"
            "        has_upper = True\n"
            "    if c.islower():\n"
            "        has_lower = True\n"
            "    i = i + 1\n"
            "print(\"长度>=8：\" + str(length_ok))\n"
            "print(\"含数字：\" + str(has_digit))\n"
            "print(\"含大写字母：\" + str(has_upper))\n"
            "print(\"含小写字母：\" + str(has_lower))\n"
            "score = 0\n"
            "if length_ok:\n"
            "    score = score + 1\n"
            "if has_digit:\n"
            "    score = score + 1\n"
            "if has_upper:\n"
            "    score = score + 1\n"
            "if has_lower:\n"
            "    score = score + 1\n"
            "print(\"满足项数：\" + str(score) + \" / 4\")\n"
            "if score == 4:\n"
            "    print(\"强密码\")\n"
            "elif score == 3:\n"
            "    print(\"中等密码\")\n"
            "else:\n"
            "    print(\"弱密码，请加强\")\n"
        ),
        "explanation": (
            "思路：先设三个 False 标志位，用 while 循环逐字符判断 isdigit/isupper/islower，"
            "发现就置 True；再用四个独立 if 累加满足项数 score，最后按 score 分档。"
            "讲解：标志位（flag）模式：先假设不满足，遍历中发现满足就翻成 True；"
            "isdigit()/isupper()/islower() 是字符串方法，判断单个字符类型；"
            "分档判断用 if/elif/else。"
        ),
        "sample_input": "Abc12345\n",
    },
    {
        "topic_id": 49,
        "title": "L5-49-D 闰年与世纪年",
        "content": (
            "闰年与世纪年判断。输入一行：一个年份（整数）。"
            "请分步判断并输出：①该年能否被 4 整除；②能否被 100 整除；③能否被 400 整除（各输出 True/False）；"
            "然后按闰年规则（能被400整除，或能被4整除但不能被100整除）判断是否闰年并输出；"
            "再判断是否「世纪年」（能被100整除的年份）并输出；"
            "最后输出该年 2 月的天数（闰年 29，平年 28）。"
        ),
        "answer": (
            "# 闰年与世纪年\n"
            "year = int(input())\n"
            "div4 = year % 4 == 0\n"
            "div100 = year % 100 == 0\n"
            "div400 = year % 400 == 0\n"
            "print(\"年份：\" + str(year))\n"
            "print(\"能被4整除：\" + str(div4))\n"
            "print(\"能被100整除：\" + str(div100))\n"
            "print(\"能被400整除：\" + str(div400))\n"
            "# 闰年规则：能被400整除，或（能被4整除 且 不能被100整除）\n"
            "is_leap = div400 or (div4 and not div100)\n"
            "print(\"是否闰年：\" + str(is_leap))\n"
            "# 世纪年：能被100整除\n"
            "is_century = div100\n"
            "print(\"是否世纪年：\" + str(is_century))\n"
            "if is_leap:\n"
            "    feb = 29\n"
            "else:\n"
            "    feb = 28\n"
            "print(\"该年2月有 \" + str(feb) + \" 天\")\n"
        ),
        "explanation": (
            "思路：先把三个整除判断结果存成 div4/div100/div400；"
            "闰年 = div400 or (div4 and not div100)，用 or 和 and、not 组合；"
            "世纪年就是能被 100 整除；最后按 is_leap 决定 2 月天数。"
            "讲解：% 取余为 0 就是能整除；把判断结果存成布尔变量再组合，比写一长串条件更清楚；"
            "括号能改变 and/or 的优先级，这里的括号不能省。"
        ),
        "sample_input": "2000\n",
    },
    {
        "topic_id": 49,
        "title": "L5-49-E 三角形判断",
        "content": (
            "三角形判断。输入一行：三个整数 a、b、c（空格分隔），代表三条边长。"
            "请先判断能否构成三角形（任意两边之和大于第三边，需同时满足三个条件）并输出；"
            "若能构成三角形，再判断类型：三边相等输出「等边三角形」；"
            "有两条边相等输出「等腰三角形」；满足 a²+b²=c²（c 为最长边）输出「直角三角形」；"
            "其余输出「普通三角形」。若不能构成三角形，输出「不能构成三角形」。"
        ),
        "answer": (
            "# 三角形判断\n"
            "a, b, c = map(int, input().split())\n"
            "print(\"三条边：\" + str(a) + \"、\" + str(b) + \"、\" + str(c))\n"
            "# 能否构成三角形：任意两边之和大于第三边\n"
            "valid = (a + b > c) and (a + c > b) and (b + c > a)\n"
            "print(\"能构成三角形：\" + str(valid))\n"
            "if not valid:\n"
            "    print(\"不能构成三角形\")\n"
            "else:\n"
            "    # 找出最长边\n"
            "    longest = a\n"
            "    if b > longest:\n"
            "        longest = b\n"
            "    if c > longest:\n"
            "        longest = c\n"
            "    sides = [a, b, c]\n"
            "    sides.sort()\n"
            "    x, y, z = sides\n"
            "    if a == b and b == c:\n"
            "        print(\"等边三角形\")\n"
            "    elif a == b or b == c or a == c:\n"
            "        print(\"等腰三角形\")\n"
            "    elif x * x + y * y == z * z:\n"
            "        print(\"直角三角形\")\n"
            "    else:\n"
            "        print(\"普通三角形\")\n"
            "    print(\"最长边：\" + str(longest))\n"
        ),
        "explanation": (
            "思路：map(int, input().split()) 一次读三个整数；valid 用三个 and 条件判断能否构成三角形；"
            "能构成时先排序找出最长边，再按等边→等腰→直角→普通的顺序用 if/elif 判断类型。"
            "讲解：判断顺序很重要，等边是特殊的等腰，要先判等边；"
            "直角判断用最短两边平方和 == 最长边平方（勾股定理）；"
            "sort() 原地排序列表，排序后 x<=y<=z。"
        ),
        "sample_input": "3 4 5\n",
    },

    # ===================== L6 / topic 50 if-else、if-elif与嵌套if =====================
    {
        "topic_id": 50,
        "title": "L6-50-A 成绩等级与评语",
        "content": (
            "成绩等级与评语。输入两行：姓名、分数（整数 0-100）。"
            "用 if-elif-else 把分数分成五档：90及以上「优秀」、80-89「良好」、70-79「中等」、"
            "60-69「及格」、60以下「不及格」。每档输出「姓名 的等级是 X」；"
            "再用嵌套 if：如果是「优秀」或「良好」，进一步判断分数是否大于等于 95，"
            "是则追加「太棒了，接近满分！」，否则追加「继续保持！」；"
            "如果是「不及格」，输出「别灰心，我们下次再战！」。"
        ),
        "answer": (
            "# 成绩等级与评语\n"
            "name = input()\n"
            "score = int(input())\n"
            "print(name + \" 考了 \" + str(score) + \" 分\")\n"
            "if score >= 90:\n"
            "    grade = \"优秀\"\n"
            "elif score >= 80:\n"
            "    grade = \"良好\"\n"
            "elif score >= 70:\n"
            "    grade = \"中等\"\n"
            "elif score >= 60:\n"
            "    grade = \"及格\"\n"
            "else:\n"
            "    grade = \"不及格\"\n"
            "print(name + \" 的等级是：\" + grade)\n"
            "# 嵌套 if：对优秀/良好再细分\n"
            "if grade == \"优秀\" or grade == \"良好\":\n"
            "    if score >= 95:\n"
            "        print(\"太棒了，接近满分！\")\n"
            "    else:\n"
            "        print(\"继续保持！\")\n"
            "if grade == \"不及格\":\n"
            "    print(\"别灰心，我们下次再战！\")\n"
        ),
        "explanation": (
            "思路：先用 if-elif-else 从上往下分五档，把等级存进 grade 变量；"
            "再用嵌套 if 对「优秀/良好」做二级判断（是否 >=95），对「不及格」单独鼓励。"
            "讲解：if-elif 从上往下，命中第一个成立的分支就停止；"
            "先把结果存变量（grade）再复用，避免重复写条件；嵌套 if 用于「大分类里再细分」。"
        ),
        "sample_input": "小明\n96\n",
    },
    {
        "topic_id": 50,
        "title": "L6-50-B 出租车计费器",
        "content": (
            "出租车计费器。输入一行：行驶公里数（可为小数）。计费规则："
            "起步价 10 元（含 3 公里）；超过 3 公里的部分每公里 2 元；"
            "超过 10 公里的部分每公里 3 元（长途加价）。请用 if-elif-else 分段计算总费用："
            "若公里数 <=3，费用=10；若 3<公里数<=10，费用=10+(公里数-3)×2；"
            "若公里数 >10，费用=10+7×2+(公里数-10)×3。输出公里数、各段费用和总费用（2 位小数）。"
        ),
        "answer": (
            "# 出租车分段计费\n"
            "km = float(input())\n"
            "print(\"行驶公里数：\" + str(km))\n"
            "if km <= 3:\n"
            "    base = 10\n"
            "    mid = 0\n"
            "    far = 0\n"
            "elif km <= 10:\n"
            "    base = 10\n"
            "    mid = (km - 3) * 2\n"
            "    far = 0\n"
            "else:\n"
            "    base = 10\n"
            "    mid = 7 * 2\n"
            "    far = (km - 10) * 3\n"
            "total = base + mid + far\n"
            "print(\"起步价（含3公里）：\" + str(round(base, 2)) + \" 元\")\n"
            "print(\"3-10公里段费用：\" + str(round(mid, 2)) + \" 元\")\n"
            "print(\"10公里以上段费用：\" + str(round(far, 2)) + \" 元\")\n"
            "print(\"总费用：\" + str(round(total, 2)) + \" 元\")\n"
        ),
        "explanation": (
            "思路：分三段计费，用 if-elif-else 判断落在哪一段，分别算出 base/mid/far 三段费用再相加；"
            "关键点：超过 10 公里时，3-10 这段固定是 7 公里 ×2 元。"
            "讲解：分段计费是 if-elif 的典型应用；每段费用先单独算再求和，比一个式子写到底更不容易错；"
            "round(x, 2) 保留两位小数。"
        ),
        "sample_input": "15\n",
    },
    {
        "topic_id": 50,
        "title": "L6-50-C 快递运费计算",
        "content": (
            "快递运费计算。输入三行：包裹重量（千克，小数）、是否加急（输入 yes 或 no）、目的地类型（输入 local 本地 / far 外地）。"
            "基础运费：重量 ×5 元/千克；外地额外 +10 元；加急额外 +15 元。"
            "请用嵌套 if 计算：先按目的地判断基础费，再在内部用 if 判断是否加急并叠加；"
            "输出重量、目的地、是否加急、各项费用和总费用（2 位小数）；"
            "最后判断：总费用超过 50 输出「运费有点贵」，否则输出「运费合理」。"
        ),
        "answer": (
            "# 快递运费（嵌套 if）\n"
            "weight = float(input())\n"
            "urgent = input()\n"
            "dest = input()\n"
            "base = weight * 5\n"
            "# 外层：按目的地\n"
            "if dest == \"far\":\n"
            "    extra_dest = 10\n"
            "else:\n"
            "    extra_dest = 0\n"
            "# 内层：在外层基础上叠加加急费（演示嵌套结构）\n"
            "fee = base + extra_dest\n"
            "if dest == \"far\":\n"
            "    if urgent == \"yes\":\n"
            "        fee = fee + 15\n"
            "else:\n"
            "    if urgent == \"yes\":\n"
            "        fee = fee + 15\n"
            "print(\"重量：\" + str(weight) + \" 千克\")\n"
            "print(\"目的地附加：\" + str(extra_dest) + \" 元\")\n"
            "print(\"加急：\" + urgent)\n"
            "print(\"总运费：\" + str(round(fee, 2)) + \" 元\")\n"
            "if fee > 50:\n"
            "    print(\"运费有点贵\")\n"
            "else:\n"
            "    print(\"运费合理\")\n"
        ),
        "explanation": (
            "思路：先算基础运费和目的地附加费，再用嵌套 if（外层判目的地、内层判加急）叠加费用；"
            "最后按总费用判断贵不贵。"
            "讲解：嵌套 if 适合「先分大类，再在大类里细分」的场景；"
            "== 用来比较字符串是否相等；这里两个分支都加 15，其实可合并，但为了演示嵌套结构分开写。"
        ),
        "sample_input": "3.5\nyes\nfar\n",
    },
    {
        "topic_id": 50,
        "title": "L6-50-D BMI健康评估",
        "content": (
            "BMI 健康评估。输入两行：身高（米，小数）、体重（千克，小数）。"
            "BMI = 体重 ÷ (身高×身高)。用 if-elif-else 分档：BMI<18.5「偏瘦」、"
            "18.5<=BMI<24「正常」、24<=BMI<28「偏胖」、BMI>=28「肥胖」。"
            "输出 BMI（1 位小数）和对应档位；再用嵌套 if 给出建议："
            "偏瘦→「多吃点，注意营养」；正常→内层再判断 BMI 是否 >=20，是则「很健康」否则「偏瘦的正常」；"
            "偏胖/肥胖→「多运动，注意饮食」。"
        ),
        "answer": (
            "# BMI 健康评估\n"
            "height = float(input())\n"
            "weight = float(input())\n"
            "bmi = weight / (height * height)\n"
            "print(\"BMI = \" + str(round(bmi, 1)))\n"
            "if bmi < 18.5:\n"
            "    level = \"偏瘦\"\n"
            "elif bmi < 24:\n"
            "    level = \"正常\"\n"
            "elif bmi < 28:\n"
            "    level = \"偏胖\"\n"
            "else:\n"
            "    level = \"肥胖\"\n"
            "print(\"健康档位：\" + level)\n"
            "# 嵌套 if 给建议\n"
            "if level == \"偏瘦\":\n"
            "    print(\"建议：多吃点，注意营养\")\n"
            "elif level == \"正常\":\n"
            "    if bmi >= 20:\n"
            "        print(\"建议：很健康\")\n"
            "    else:\n"
            "        print(\"建议：偏瘦的正常\")\n"
            "else:\n"
            "    print(\"建议：多运动，注意饮食\")\n"
        ),
        "explanation": (
            "思路：先算 BMI，用 if-elif 按区间分四档（因为从小到大排，elif 只需写上界）；"
            "再用 if-elif-else 按档位给建议，「正常」档内嵌套判断 BMI 是否 >=20。"
            "讲解：区间判断从小到大写，elif bmi<24 其实隐含了 bmi>=18.5（前面已排除）；"
            "这种「省略下界」的写法依赖 if-elif 的顺序，不能乱。"
        ),
        "sample_input": "1.45\n40\n",
    },
    {
        "topic_id": 50,
        "title": "L6-50-E 商场满减活动",
        "content": (
            "商场满减活动。输入一行：消费金额（小数）。满减规则（从高到低，只享受一档）："
            "满 500 减 100；满 300 减 50；满 100 减 10；不满 100 不打折。"
            "请用 if-elif-else 判断适用哪一档，输出消费金额、减免金额、实付金额（2 位小数）；"
            "再用嵌套 if：如果实付金额仍大于 400，输出「消费真不少」；如果实付小于 50，输出「省了不少钱」；"
            "否则输出「消费适中」。"
        ),
        "answer": (
            "# 商场满减\n"
            "amount = float(input())\n"
            "print(\"消费金额：\" + str(round(amount, 2)) + \" 元\")\n"
            "if amount >= 500:\n"
            "    discount = 100\n"
            "    tier = \"满500减100\"\n"
            "elif amount >= 300:\n"
            "    discount = 50\n"
            "    tier = \"满300减50\"\n"
            "elif amount >= 100:\n"
            "    discount = 10\n"
            "    tier = \"满100减10\"\n"
            "else:\n"
            "    discount = 0\n"
            "    tier = \"不打折\"\n"
            "pay = amount - discount\n"
            "print(\"适用活动：\" + tier)\n"
            "print(\"减免：\" + str(discount) + \" 元\")\n"
            "print(\"实付：\" + str(round(pay, 2)) + \" 元\")\n"
            "# 嵌套 if 评价\n"
            "if pay > 400:\n"
            "    print(\"消费真不少\")\n"
            "elif pay < 50:\n"
            "    print(\"省了不少钱\")\n"
            "else:\n"
            "    print(\"消费适中\")\n"
        ),
        "explanation": (
            "思路：满减档从高到低判断，用 if-elif 保证只命中一档；"
            "把减免额和档名都存进变量，实付=消费-减免；最后用 if-elif-else 对实付金额做评价。"
            "讲解：「从高到低」判断满减是关键，若从低到高会命中错误的档；"
            "把档位信息存成变量（tier/discount）便于统一输出。"
        ),
        "sample_input": "388\n",
    },

    # ===================== L7 / topic 51 while循环与嵌套循环 =====================
    {
        "topic_id": 51,
        "title": "L7-51-A 猜数字游戏计分版",
        "content": (
            "猜数字游戏（计分版）。答案固定为 42。程序会连续读入若干次猜测（每次一行整数），"
            "直到猜中 42 或输入 0（放弃）为止。请用 while 循环逐次处理："
            "每次输出「第 X 次猜：Y」，若 Y==42 输出「猜对了！用了 X 次」并结束；"
            "若 Y>42 输出「太大了」，若 Y<42 输出「太小了」；若输入 0 输出「放弃，答案是 42」并结束。"
            "最后输出总共猜了几次。"
        ),
        "answer": (
            "# 猜数字游戏（答案 42）\n"
            "answer = 42\n"
            "times = 0\n"
            "guessed = False\n"
            "while not guessed:\n"
            "    guess = int(input())\n"
            "    times = times + 1\n"
            "    print(\"第 \" + str(times) + \" 次猜：\" + str(guess))\n"
            "    if guess == answer:\n"
            "        print(\"猜对了！用了 \" + str(times) + \" 次\")\n"
            "        guessed = True\n"
            "    elif guess == 0:\n"
            "        print(\"放弃，答案是 42\")\n"
            "        guessed = True\n"
            "    elif guess > answer:\n"
            "        print(\"太大了\")\n"
            "    else:\n"
            "        print(\"太小了\")\n"
            "print(\"总共猜了 \" + str(times) + \" 次\")\n"
        ),
        "explanation": (
            "思路：用 while not guessed 持续循环，guessed 是标志位；每次读入猜测、次数+1、"
            "用 if-elif 判断猜对/放弃/太大/太小，猜对或放弃就把 guessed 置 True 结束循环。"
            "讲解：标志位控制循环是 while 的常见用法；break 也能退出循环，但标志位让结束条件更明确；"
            "注意先判断 ==answer 再判断 ==0，避免把 0 当成普通猜测。"
        ),
        "sample_input": "20\n50\n42\n",
    },
    {
        "topic_id": 51,
        "title": "L7-51-B 九九乘法表",
        "content": (
            "九九乘法表。不需要输入。请用嵌套 while 循环打印完整的九九乘法表："
            "外层 i 从 1 到 9，内层 j 从 1 到 i，每行打印 j×i=结果（用 end 让同一行的式子连在一起，"
            "式子之间用两个空格分隔），每行结束换行。最后输出「乘法表打印完成，共 9 行」。"
        ),
        "answer": (
            "# 九九乘法表（嵌套 while）\n"
            "i = 1\n"
            "rows = 0\n"
            "while i <= 9:\n"
            "    j = 1\n"
            "    while j <= i:\n"
            "        result = i * j\n"
            "        print(str(j) + \"x\" + str(i) + \"=\" + str(result), end=\"  \")\n"
            "        j = j + 1\n"
            "    print()          # 每行结束换行\n"
            "    rows = rows + 1\n"
            "    i = i + 1\n"
            "print(\"乘法表打印完成，共 \" + str(rows) + \" 行\")\n"
        ),
        "explanation": (
            "思路：外层 while 控制行（i 从 1 到 9），内层 while 控制每行的列（j 从 1 到 i）；"
            "内层用 end=\"  \" 让式子连在一行，内层结束后 print() 换行；rows 统计行数。"
            "讲解：嵌套循环里内层变量 j 每次外层循环都要重新设回 1；"
            "第 i 行只打印 i 个式子（j<=i），这就是下三角乘法表；"
            "忘记在内层 i/j 自增会导致死循环。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 51,
        "title": "L7-51-C 累加与阶乘",
        "content": (
            "累加与阶乘。输入一行：正整数 n（建议不超过 10）。请用 while 循环完成："
            "①计算 1+2+…+n 的和；②计算 n 的阶乘（1×2×…×n）；③统计 1 到 n 中能被 3 整除的数并累加它们的和。"
            "分别输出这三个结果；最后判断：若阶乘超过 1000000 输出「阶乘增长真快」，否则输出「阶乘还不算大」。"
        ),
        "answer": (
            "# 累加、阶乘与 3 的倍数\n"
            "n = int(input())\n"
            "# 1) 累加 1+2+...+n\n"
            "i = 1\n"
            "total = 0\n"
            "while i <= n:\n"
            "    total = total + i\n"
            "    i = i + 1\n"
            "# 2) 阶乘 1*2*...*n\n"
            "i = 1\n"
            "factorial = 1\n"
            "while i <= n:\n"
            "    factorial = factorial * i\n"
            "    i = i + 1\n"
            "# 3) 3 的倍数之和\n"
            "i = 1\n"
            "three_sum = 0\n"
            "while i <= n:\n"
            "    if i % 3 == 0:\n"
            "        three_sum = three_sum + i\n"
            "    i = i + 1\n"
            "print(\"1到\" + str(n) + \"的和：\" + str(total))\n"
            "print(str(n) + \"的阶乘：\" + str(factorial))\n"
            "print(\"3的倍数之和：\" + str(three_sum))\n"
            "if factorial > 1000000:\n"
            "    print(\"阶乘增长真快\")\n"
            "else:\n"
            "    print(\"阶乘还不算大\")\n"
        ),
        "explanation": (
            "思路：三个任务各用一个 while 循环，累加用 total=total+i，累乘用 factorial=factorial*i；"
            "第三个循环里加 if i%3==0 筛选 3 的倍数再累加。"
            "讲解：累加器初始为 0，累乘器初始为 1（乘 1 不影响结果）；"
            "每个循环结束 i 会超出范围，下一个循环要重新把 i 设回 1；"
            "阶乘增长极快，这就是为什么 n 不建议太大。"
        ),
        "sample_input": "8\n",
    },
    {
        "topic_id": 51,
        "title": "L7-51-D 存钱翻倍计划",
        "content": (
            "存钱翻倍计划。输入两行：初始金额（小数）、目标金额（小数，大于初始金额）。"
            "假设每年利息为 5%（即每年金额变为原来的 1.05 倍）。请用 while 循环逐年累加，"
            "直到金额达到目标，输出每年末的金额（2 位小数）；循环结束后输出「经过 X 年达成目标」；"
            "最后判断：若年数小于等于 10 输出「目标不远，加油」，否则输出「需要长期坚持」。"
        ),
        "answer": (
            "# 存钱翻倍（复利 5%）\n"
            "money = float(input())\n"
            "target = float(input())\n"
            "print(\"初始金额：\" + str(round(money, 2)) + \" 元\")\n"
            "print(\"目标金额：\" + str(round(target, 2)) + \" 元\")\n"
            "years = 0\n"
            "while money < target:\n"
            "    money = money * 1.05\n"
            "    years = years + 1\n"
            "    print(\"第 \" + str(years) + \" 年末：\" + str(round(money, 2)) + \" 元\")\n"
            "print(\"经过 \" + str(years) + \" 年达成目标\")\n"
            "if years <= 10:\n"
            "    print(\"目标不远，加油\")\n"
            "else:\n"
            "    print(\"需要长期坚持\")\n"
        ),
        "explanation": (
            "思路：while money < target 持续循环，每年 money×1.05、years+1 并打印当年金额；"
            "循环结束时 money 已达标，输出年数并按年数给评语。"
            "讲解：复利就是「利滚利」，每年在上一年的基础上乘 1.05；"
            "while 循环适合「不知道要循环几次、只知停止条件」的场景；"
            "years 初始为 0，每次循环 +1 就是计数器。"
        ),
        "sample_input": "100\n200\n",
    },
    {
        "topic_id": 51,
        "title": "L7-51-E 数字反转与回文",
        "content": (
            "数字反转与回文判断。输入一行：一个正整数 n。请用 while 循环把 n 的各位数字反转："
            "每次取 n 的个位（n%10），拼到结果 reversed_num 上（reversed_num = reversed_num*10 + 个位），"
            "再让 n 整除 10 去掉个位，直到 n 为 0。输出原数、反转后的数；"
            "判断两者是否相等：相等输出「是回文数」，否则输出「不是回文数」；"
            "最后输出原数的位数。"
        ),
        "answer": (
            "# 数字反转与回文\n"
            "n = int(input())\n"
            "original = n\n"
            "reversed_num = 0\n"
            "digits = 0\n"
            "temp = n\n"
            "# 反转数字\n"
            "while temp > 0:\n"
            "    digit = temp % 10\n"
            "    reversed_num = reversed_num * 10 + digit\n"
            "    temp = temp // 10\n"
            "# 统计位数\n"
            "temp2 = original\n"
            "while temp2 > 0:\n"
            "    digits = digits + 1\n"
            "    temp2 = temp2 // 10\n"
            "print(\"原数：\" + str(original))\n"
            "print(\"反转后：\" + str(reversed_num))\n"
            "if original == reversed_num:\n"
            "    print(\"是回文数\")\n"
            "else:\n"
            "    print(\"不是回文数\")\n"
            "print(\"位数：\" + str(digits))\n"
        ),
        "explanation": (
            "思路：反转的核心是「取个位→拼到结果尾部→原数去掉个位」三步循环；"
            "reversed_num*10+digit 相当于把已有数字左移一位再加新个位；位数用另一个循环数。"
            "讲解：%10 取个位，//10 去掉个位，这是处理数字各位的经典组合；"
            "要用临时变量 temp 操作，保留 original 原值用于比较；"
            "回文数就是正着读反着读都一样的数。"
        ),
        "sample_input": "12321\n",
    },

    # ===================== L8 / topic 52 字符串的查找、判断、修改 =====================
    {
        "topic_id": 52,
        "title": "L8-52-A 单词统计器",
        "content": (
            "单词统计器。输入一行：一句英文（单词用空格分隔）。请完成："
            "①用 split() 切成单词列表并输出单词总数；②用 count() 统计第一个单词出现了几次；"
            "③用 find() 找出第二个单词第一次出现的位置（若不存在输出 -1）；"
            "④用 upper() 和 lower() 分别输出整句大写版和小写版；⑤用 replace() 把第一个单词替换成「CAT」并输出。"
        ),
        "answer": (
            "# 单词统计器\n"
            "sentence = input()\n"
            "words = sentence.split()\n"
            "print(\"原句：\" + sentence)\n"
            "print(\"单词总数：\" + str(len(words)))\n"
            "first = words[0]\n"
            "second = words[1]\n"
            "# count 统计第一个单词出现次数\n"
            "cnt = sentence.count(first)\n"
            "print(\"「\" + first + \"」出现了 \" + str(cnt) + \" 次\")\n"
            "# find 找第二个单词的位置\n"
            "pos = sentence.find(second)\n"
            "print(\"「\" + second + \"」首次出现在位置 \" + str(pos))\n"
            "# 大小写转换\n"
            "print(\"大写版：\" + sentence.upper())\n"
            "print(\"小写版：\" + sentence.lower())\n"
            "# 替换第一个单词\n"
            "new_sentence = sentence.replace(first, \"CAT\", 1)\n"
            "print(\"替换后：\" + new_sentence)\n"
        ),
        "explanation": (
            "思路：split() 按空格切成列表；count() 数某子串出现次数；find() 返回首次出现下标（没有则-1）；"
            "upper()/lower() 整体转换大小写；replace(旧, 新, 1) 只替换第一处。"
            "讲解：split() 不带参数按任意空白切并自动去空；find 从 0 开始计数；"
            "replace 第三个参数限制替换次数，避免把后面相同的词也换掉；"
            "字符串方法都返回新字符串，不改变原字符串。"
        ),
        "sample_input": "the cat and the dog\n",
    },
    {
        "topic_id": 52,
        "title": "L8-52-B 敏感词过滤",
        "content": (
            "敏感词过滤。输入两行：第一行是一句话，第二行是用空格分隔的若干敏感词。"
            "请逐个检查每个敏感词是否出现在句子里（用 in 或 find），输出每个敏感词的检测结果；"
            "统计命中的敏感词个数；然后用 replace() 把命中的每个敏感词都替换成「***」，输出过滤后的句子；"
            "最后判断：命中 0 个输出「内容安全」，命中 1-2 个输出「轻度违规」，3 个及以上输出「严重违规」。"
        ),
        "answer": (
            "# 敏感词过滤\n"
            "sentence = input()\n"
            "bad_words = input().split()\n"
            "print(\"原句：\" + sentence)\n"
            "hit = 0\n"
            "result = sentence\n"
            "# 逐个敏感词检测并替换\n"
            "i = 0\n"
            "while i < len(bad_words):\n"
            "    word = bad_words[i]\n"
            "    if word in sentence:\n"
            "        print(\"发现敏感词：\" + word)\n"
            "        hit = hit + 1\n"
            "        result = result.replace(word, \"***\")\n"
            "    else:\n"
            "        print(\"未发现：\" + word)\n"
            "    i = i + 1\n"
            "print(\"命中敏感词个数：\" + str(hit))\n"
            "print(\"过滤后：\" + result)\n"
            "if hit == 0:\n"
            "    print(\"内容安全\")\n"
            "elif hit <= 2:\n"
            "    print(\"轻度违规\")\n"
            "else:\n"
            "    print(\"严重违规\")\n"
        ),
        "explanation": (
            "思路：把敏感词 split 成列表，用 while 逐个遍历；用 in 判断是否命中，命中就计数+1 并 replace 成***；"
            "result 累积替换结果；最后按命中数分档。"
            "讲解：in 判断子串是否存在，比 find!=-1 更直观；"
            "替换要累积到 result 上（result=result.replace(...)），否则每次都在原句上替换会丢失之前的结果；"
            "while 遍历列表用下标 i 从 0 到 len-1。"
        ),
        "sample_input": "今天天气不错我们去玩吧\n玩 坏蛋\n",
    },
    {
        "topic_id": 52,
        "title": "L8-52-C 字符分类统计",
        "content": (
            "字符分类统计。输入一行：一串混合字符（可含字母、数字、空格、标点）。"
            "请用 while 循环逐个字符判断，分别统计：大写字母、小写字母、数字、空格、其他字符的个数，"
            "并输出五类计数；再统计字母总数（大写+小写）和数字字符的总和（把每个数字字符转成整数相加）；"
            "最后判断：若字母多于数字输出「字母占多数」，否则输出「数字占多数或一样多」。"
        ),
        "answer": (
            "# 字符分类统计\n"
            "s = input()\n"
            "upper_cnt = 0\n"
            "lower_cnt = 0\n"
            "digit_cnt = 0\n"
            "space_cnt = 0\n"
            "other_cnt = 0\n"
            "digit_sum = 0\n"
            "i = 0\n"
            "while i < len(s):\n"
            "    c = s[i]\n"
            "    if c.isupper():\n"
            "        upper_cnt = upper_cnt + 1\n"
            "    elif c.islower():\n"
            "        lower_cnt = lower_cnt + 1\n"
            "    elif c.isdigit():\n"
            "        digit_cnt = digit_cnt + 1\n"
            "        digit_sum = digit_sum + int(c)\n"
            "    elif c == \" \":\n"
            "        space_cnt = space_cnt + 1\n"
            "    else:\n"
            "        other_cnt = other_cnt + 1\n"
            "    i = i + 1\n"
            "print(\"大写字母：\" + str(upper_cnt))\n"
            "print(\"小写字母：\" + str(lower_cnt))\n"
            "print(\"数字：\" + str(digit_cnt))\n"
            "print(\"空格：\" + str(space_cnt))\n"
            "print(\"其他：\" + str(other_cnt))\n"
            "print(\"字母总数：\" + str(upper_cnt + lower_cnt))\n"
            "print(\"数字字符之和：\" + str(digit_sum))\n"
            "if upper_cnt + lower_cnt > digit_cnt:\n"
            "    print(\"字母占多数\")\n"
            "else:\n"
            "    print(\"数字占多数或一样多\")\n"
        ),
        "explanation": (
            "思路：while 逐字符遍历，用 if-elif 链按 isupper/islower/isdigit/空格/其他分类计数；"
            "遇到数字字符顺手 int(c) 累加到 digit_sum；最后汇总并比较。"
            "讲解：if-elif 链保证每个字符只归入一类；"
            "int(c) 把单个数字字符转成整数（如 '5'→5）；"
            "多个计数器同时维护是「分类统计」的标准写法。"
        ),
        "sample_input": "Hello World 2026!\n",
    },
    {
        "topic_id": 52,
        "title": "L8-52-D 姓名拼音规范化",
        "content": (
            "姓名拼音规范化。输入一行：一个英文姓名（可能大小写混乱、前后有空格，如「  toM sMith 」）。"
            "请依次处理并输出每一步结果：①用 strip() 去掉首尾空格；②用 split() 拆成名字和姓氏；"
            "③把名字和姓氏分别用 capitalize() 规范成首字母大写；④用「姓, 名」格式拼接输出；"
            "⑤输出姓名的缩写（各部分首字母大写，如 T.S.）；最后输出原长度和规范后长度。"
        ),
        "answer": (
            "# 姓名拼音规范化\n"
            "raw = input()\n"
            "print(\"原始输入：[\" + raw + \"]\")\n"
            "# 1. 去首尾空格\n"
            "cleaned = raw.strip()\n"
            "print(\"去空格后：[\" + cleaned + \"]\")\n"
            "# 2. 拆分名字和姓\n"
            "parts = cleaned.split()\n"
            "first = parts[0]\n"
            "last = parts[1]\n"
            "# 3. 首字母大写规范\n"
            "first_ok = first.capitalize()\n"
            "last_ok = last.capitalize()\n"
            "print(\"名字规范：\" + first_ok)\n"
            "print(\"姓氏规范：\" + last_ok)\n"
            "# 4. 姓, 名 格式\n"
            "full = last_ok + \", \" + first_ok\n"
            "print(\"规范全名：\" + full)\n"
            "# 5. 缩写\n"
            "abbr = first_ok[0].upper() + \".\" + last_ok[0].upper() + \".\"\n"
            "print(\"缩写：\" + abbr)\n"
            "print(\"原长度：\" + str(len(raw)) + \"，规范后长度：\" + str(len(full)))\n"
        ),
        "explanation": (
            "思路：strip 去首尾空格→split 拆成部分→capitalize 规范各部分→拼接成「姓, 名」→"
            "取各部分首字母做缩写；最后比较处理前后长度。"
            "讲解：strip 只去首尾，中间空格保留；capitalize 把首字母大写其余小写；"
            "字符串可以用下标取单个字符（s[0] 是第一个）；"
            "用 [ ] 包住输出能看清首尾有没有空格。"
        ),
        "sample_input": "  toM sMith \n",
    },
    {
        "topic_id": 52,
        "title": "L8-52-E 回文短语检测",
        "content": (
            "回文短语检测。输入一行：一个短语（可能含空格和大小写）。"
            "请判断它是否回文（忽略空格和大小写）：先用 replace() 去掉所有空格，再用 lower() 转小写得到 cleaned；"
            "然后用 while 循环从两端向中间逐字符比较（左指针和右指针），输出每一对比较的字符；"
            "全部相等则输出「是回文短语」，否则输出「不是回文短语」并指出第一处不相等的位置；"
            "最后输出去空格后的长度。"
        ),
        "answer": (
            "# 回文短语检测\n"
            "phrase = input()\n"
            "# 去空格、转小写\n"
            "cleaned = phrase.replace(\" \", \"\").lower()\n"
            "print(\"去空格小写后：\" + cleaned)\n"
            "left = 0\n"
            "right = len(cleaned) - 1\n"
            "is_palindrome = True\n"
            "bad_pos = -1\n"
            "# 双指针从两端向中间比较\n"
            "while left < right:\n"
            "    print(\"比较：\" + cleaned[left] + \" 和 \" + cleaned[right])\n"
            "    if cleaned[left] != cleaned[right]:\n"
            "        is_palindrome = False\n"
            "        bad_pos = left\n"
            "        break\n"
            "    left = left + 1\n"
            "    right = right - 1\n"
            "if is_palindrome:\n"
            "    print(\"是回文短语\")\n"
            "else:\n"
            "    print(\"不是回文短语，第一处不等在位置 \" + str(bad_pos))\n"
            "print(\"去空格后长度：\" + str(len(cleaned)))\n"
        ),
        "explanation": (
            "思路：先去空格转小写统一格式；用双指针 left/right 从两端向中间走，逐对比较；"
            "发现不等就标记位置并 break；循环结束按 is_palindrome 输出结论。"
            "讲解：双指针是判断回文的经典方法，只需比一半字符；"
            "break 立即跳出循环；先把格式统一（去空格、小写）再比较，才能正确判断「上海自来水来自海上」这类短语。"
        ),
        "sample_input": "Shanghai tap water comes from the sea\n",
    },
]
