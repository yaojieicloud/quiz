# -*- coding: utf-8 -*-
"""Python实操 每课新增10题（第1-10课），三年级趣味场景。
输出 python_coding_new_p1.json（expected_output 由 run_expected.py 实跑补齐）。
课时名用线上精确名。"""
import json

Q = []

def q(topic, content, code, expl, diff=1):
    Q.append({
        "type": "code", "topic_name": topic, "unit": None,
        "content": content, "options": None,
        "answer": code, "explanation": expl,
        "difficulty": diff, "sample_input": "",
        "expected_output": "",
    })

# ===== 1 变量与标识符 =====
T = "变量与标识符"
q(T, "小明养了一只小猫叫'花花'。定义一个变量 cat，把'花花'存进去，然后打印这个变量。",
  "cat = '花花'\nprint(cat)",
  "cat = '花花'，字符串要加引号；print(cat) 打印变量里的值。")
q(T, "玩具箱里有 8 辆小汽车。定义变量 cars 存数字 8，然后打印它。",
  "cars = 8\nprint(cars)",
  "cars = 8，数字不用加引号；print(cars) 打印。")
q(T, "先定义 fruit = '苹果'，打印它；再把 fruit 改成 '香蕉'，再打印一次。",
  "fruit = '苹果'\nprint(fruit)\nfruit = '香蕉'\nprint(fruit)",
  "变量可以重新赋值，后一次赋值会覆盖前一次。", 2)
q(T, "定义两个变量：pen = 3，book = 5，然后分别打印它们（打印两行）。",
  "pen = 3\nbook = 5\nprint(pen)\nprint(book)",
  "两个变量分开定义，用两个 print 分别打印。")
q(T, "小红有 12 颗糖，定义 candy = 12，打印'小红有'加上糖果数（用逗号连起来打印）。",
  "candy = 12\nprint('小红有', candy)",
  "print('小红有', candy) 用逗号把文字和变量连起来。")
q(T, "定义 animal = '小兔子'，age = 2，一行打印这两个变量（逗号分隔）。",
  "animal = '小兔子'\nage = 2\nprint(animal, age)",
  "print(animal, age) 用逗号一次打印两个变量。")
q(T, "把数字 100 存进变量 score，打印 score 两次，分两行。",
  "score = 100\nprint(score)\nprint(score)",
  "同一个变量可以打印多次，值不变。")
q(T, "定义 ball = '足球'，把 ball 打印出来，再定义 racket = '球拍' 并打印。",
  "ball = '足球'\nprint(ball)\nracket = '球拍'\nprint(racket)",
  "依次定义两个变量并各自打印。")
q(T, "定义 my_name = '小华'，然后用一个 print 打印 my_name 和数字 9（用逗号连接）。",
  "my_name = '小华'\nprint(my_name, 9)",
  "print(my_name, 9) 变量和数字用逗号连接。")
q(T, "先让 x = 5，再让 x = x + 1（在原来的值上加1），然后打印 x。",
  "x = 5\nx = x + 1\nprint(x)",
  "x = x + 1 表示在原值基础上加1，5+1=6。", 2)

# ===== 2 debug注释与输出函数 =====
T = "debug注释与输出函数"
q(T, "用 print 打印一句话：今天天气真好！",
  "print('今天天气真好！')",
  "print() 里放要打印的文字，文字要加引号。")
q(T, "用一个 print 同时打印三个水果名：苹果 香蕉 橘子（用逗号分开）。",
  "print('苹果', '香蕉', '橘子')",
  "逗号分隔的多个内容，打印时会自动用空格连起来。")
q(T, "写一行注释'# 这是注释不会运行'，然后打印'注释下面的话'（注释那行不会显示）。",
  "# 这是注释不会运行\nprint('注释下面的话')",
  "# 开头的是注释，电脑不会执行，所以只打印第二行。")
q(T, "打印两行：第一行'早上好'，第二行'开始学习啦'。",
  "print('早上好')\nprint('开始学习啦')",
  "两个 print 各打印一行。")
q(T, "用 print 打印一个空行（括号里什么都不放）。",
  "print()",
  "print() 括号里什么都不放，会打印一个空行。", 2)
q(T, "打印三个数字 1 2 3（用逗号分开写）。",
  "print(1, 2, 3)",
  "数字不用加引号，逗号分隔会连成一行。")
q(T, "先写注释'# 计算星星数量'，再打印'⭐⭐⭐'三颗星星。",
  "# 计算星星数量\nprint('⭐⭐⭐')",
  "注释说明代码用途，print 打印星星。")
q(T, "用 print 打印 '我'、'爱'、'编'、'程' 四个字（逗号分隔）。",
  "print('我', '爱', '编', '程')",
  "四个字用逗号分开，打印时连成一行。")
q(T, "打印变量 msg = '你好呀'，并在打印前加一行注释说明。",
  "# 打印问候语\nmsg = '你好呀'\nprint(msg)",
  "先写注释，再定义变量，最后打印。")
q(T, "连续打印 5 个 print，内容分别是数字 1 到 5（每个一行）。",
  "print(1)\nprint(2)\nprint(3)\nprint(4)\nprint(5)",
  "五个 print 各打印一个数字，分五行显示。", 2)

# ===== 3 数值类型,字符串与格式化输出 =====
T = "数值类型,字符串与格式化输出"
q(T, "定义 name='小美'，用 f-string 打印出：我叫小美。",
  "name = '小美'\nprint(f'我叫{name}')",
  "f-string 写法：f'我叫{name}'，大括号里放变量。")
q(T, "定义 age=9，用 f-string 打印出：我今年9岁。",
  "age = 9\nprint(f'我今年{age}岁')",
  "f'我今年{age}岁'，大括号里的 age 会被替换成 9。")
q(T, "定义 fruit='西瓜' 和 num=3，用 f-string 打印：我有3个西瓜。",
  "fruit = '西瓜'\nnum = 3\nprint(f'我有{num}个{fruit}')",
  "f-string 里可以放多个变量：f'我有{num}个{fruit}'。", 2)
q(T, "打印小数 3.5（直接 print 一个小数）。",
  "print(3.5)",
  "小数（float）可以直接打印，如 print(3.5)。")
q(T, "定义 pi=3.14，用 f-string 打印：圆周率约等于3.14。",
  "pi = 3.14\nprint(f'圆周率约等于{pi}')",
  "f'圆周率约等于{pi}'，小数也能放进 f-string。")
q(T, "把字符串'快乐'重复打印 3 次连在一起（用乘法 *）。",
  "print('快乐' * 3)",
  "字符串乘 3 会重复 3 次：快乐快乐快乐。", 2)
q(T, "定义 a=7，b=2，用 f-string 打印出 a 和 b，格式：a=7,b=2。",
  "a = 7\nb = 2\nprint(f'a={a},b={b}')",
  "f'a={a},b={b}' 会打印 a=7,b=2。")
q(T, "打印一个整数 2026 和一个字符串 '新年'（逗号分隔）。",
  "print(2026, '新年')",
  "整数和字符串用逗号一起打印。")
q(T, "定义 toy='机器人'，price=15，用 f-string 打印：机器人要15元。",
  "toy = '机器人'\nprice = 15\nprint(f'{toy}要{price}元')",
  "f'{toy}要{price}元' 把两个变量嵌进句子里。")
q(T, "用 f-string 打印算式结果：把 4+6 放进大括号，打印出 4+6=10。",
  "print(f'4+6={4+6}')",
  "f-string 大括号里可以放算式，会先算出结果再放进去。", 2)

# ===== 4 算数与赋值运算符,输入函数与转义字符 =====
T = "算数与赋值运算符,输入函数与转义字符"
q(T, "计算 6 加 4 的结果并打印（应是 10）。",
  "print(6 + 4)",
  "加号是加法，print(6 + 4) 打印 10。")
q(T, "计算 20 减 8 的结果并打印。",
  "print(20 - 8)",
  "减号是减法，20-8=12。")
q(T, "计算 7 乘 3 的结果并打印。",
  "print(7 * 3)",
  "星号 * 是乘法，7*3=21。")
q(T, "计算 16 除以 4 的结果并打印（整除后的数）。",
  "print(16 // 4)",
  "双斜杠 // 是整除，16//4=4。", 2)
q(T, "计算 10 除以 3 的余数并打印（用 % 取余）。",
  "print(10 % 3)",
  "% 是取余数，10除以3余1。", 2)
q(T, "定义 n=5，用 n += 3 让 n 增加 3，然后打印 n。",
  "n = 5\nn += 3\nprint(n)",
  "n += 3 等于 n = n + 3，5+3=8。")
q(T, "定义 m=12，用 m -= 4 让 m 减少 4，然后打印 m。",
  "m = 12\nm -= 4\nprint(m)",
  "m -= 4 等于 m = m - 4，12-4=8。")
q(T, "打印带换行的句子：第一行'上山'，第二行'下山'（用一个 print 加 \\n）。",
  "print('上山\\n下山')",
  "\\n 是换行转义符，会把内容分成两行。", 2)
q(T, "计算 2 的 5 次方并打印（用 ** 幂运算）。",
  "print(2 ** 5)",
  "双星号 ** 是幂，2**5=32。", 2)
q(T, "定义 apples=9，用 apples *= 2 让苹果翻倍，然后打印 apples。",
  "apples = 9\napples *= 2\nprint(apples)",
  "apples *= 2 等于 apples = apples * 2，9*2=18。")

# ===== 5 if判断,比较运算符,逻辑运算符 =====
T = "if判断,比较运算符,逻辑运算符"
q(T, "定义 score=90，如果 score 大于等于 60，就打印'及格'。",
  "score = 90\nif score >= 60:\n    print('及格')",
  "if score >= 60: 条件成立就执行缩进的 print。")
q(T, "定义 age=9，如果 age 大于 6，打印'可以上小学啦'。",
  "age = 9\nif age > 6:\n    print('可以上小学啦')",
  "9>6 成立，所以会打印。")
q(T, "定义 money=50，如果 money 等于 50，打印'正好五十元'。",
  "money = 50\nif money == 50:\n    print('正好五十元')",
  "双等号 == 是判断相等，money==50 成立。")
q(T, "定义 n=7，如果 n 不等于 5，打印'不是5'。",
  "n = 7\nif n != 5:\n    print('不是5')",
  "!= 是不等于，7!=5 成立。")
q(T, "定义 candy=3，如果 candy 小于 5，打印'糖果不够啦'。",
  "candy = 3\nif candy < 5:\n    print('糖果不够啦')",
  "3<5 成立，打印提示。")
q(T, "定义 x=8，如果 x 大于 5 并且（and）x 小于 10，打印'在范围内'。",
  "x = 8\nif x > 5 and x < 10:\n    print('在范围内')",
  "and 表示两个条件都要成立，8>5 且 8<10 都成立。", 2)
q(T, "定义 a=3，如果 a 等于 3 或者（or）a 等于 4，打印'是3或4'。",
  "a = 3\nif a == 3 or a == 4:\n    print('是3或4')",
  "or 表示只要一个成立就行，a==3 成立。", 2)
q(T, "定义 h=130，如果 h 大于等于 120，打印'可以玩过山车'。",
  "h = 130\nif h >= 120:\n    print('可以玩过山车')",
  "130>=120 成立，打印可以玩。")
q(T, "定义 t=25，如果 t 大于 30 就打印'好热'（这句不会打印，因为25不大于30）。再打印'完成'。",
  "t = 25\nif t > 30:\n    print('好热')\nprint('完成')",
  "25>30 不成立，不打印'好热'；print('完成')在 if 外面，一定会打印。", 2)
q(T, "定义 b=0，如果 not b（b 是假），打印'b是0'。",
  "b = 0\nif not b:\n    print('b是0')",
  "not 取反；0 是假，not 0 为真，所以打印。", 2)

# ===== 6 if-else,if-elif与嵌套if =====
T = "if-else,if-elif与嵌套if"
q(T, "定义 score=55，如果大于等于60打印'及格'，否则打印'不及格'。",
  "score = 55\nif score >= 60:\n    print('及格')\nelse:\n    print('不及格')",
  "55<60，条件不成立走 else，打印'不及格'。")
q(T, "定义 age=8，如果 age 大于等于 10 打印'大孩子'，否则打印'小朋友'。",
  "age = 8\nif age >= 10:\n    print('大孩子')\nelse:\n    print('小朋友')",
  "8<10，走 else，打印'小朋友'。")
q(T, "定义 num=0，如果 num 大于 0 打印'正数'，否则打印'不是正数'。",
  "num = 0\nif num > 0:\n    print('正数')\nelse:\n    print('不是正数')",
  "0 不大于 0，走 else。")
q(T, "定义 score=75，用 if-elif-else：大于等于90打印'优秀'，大于等于60打印'良好'，否则打印'加油'。",
  "score = 75\nif score >= 90:\n    print('优秀')\nelif score >= 60:\n    print('良好')\nelse:\n    print('加油')",
  "75不到90但大于等于60，走 elif 打印'良好'。", 2)
q(T, "定义 grade=88，用 if-elif：大于等于85打印'A'，大于等于70打印'B'，否则打印'C'。",
  "grade = 88\nif grade >= 85:\n    print('A')\nelif grade >= 70:\n    print('B')\nelse:\n    print('C')",
  "88>=85，打印'A'。", 2)
q(T, "定义 light='绿灯'，如果 light 是'绿灯'打印'走'，是'红灯'打印'停'，否则打印'等一等'。",
  "light = '绿灯'\nif light == '绿灯':\n    print('走')\nelif light == '红灯':\n    print('停')\nelse:\n    print('等一等')",
  "light 是绿灯，打印'走'。", 2)
q(T, "定义 n=4，先判断 n 是不是偶数（n%2==0），如果是，再判断是否大于2，是就打印'大于2的偶数'。",
  "n = 4\nif n % 2 == 0:\n    if n > 2:\n        print('大于2的偶数')",
  "嵌套 if：4是偶数，再判断4>2成立，打印。", 2)
q(T, "定义 a=5，b=3，如果 a>b 打印'a大'，否则打印'b大或相等'。",
  "a = 5\nb = 3\nif a > b:\n    print('a大')\nelse:\n    print('b大或相等')",
  "5>3 成立，打印'a大'。")
q(T, "定义 temp=15，如果 temp 小于 10 打印'冷'，小于 20 打印'凉爽'，否则打印'热'。",
  "temp = 15\nif temp < 10:\n    print('冷')\nelif temp < 20:\n    print('凉爽')\nelse:\n    print('热')",
  "15不小于10但小于20，打印'凉爽'。", 2)
q(T, "定义 score=100，如果 score 等于 100 打印'满分'，否则打印'继续努力'。",
  "score = 100\nif score == 100:\n    print('满分')\nelse:\n    print('继续努力')",
  "100==100 成立，打印'满分'。")

# ===== 7 while循环与嵌套循环 =====
T = "while循环与嵌套循环"
q(T, "用 while 循环打印数字 1 到 5（每个一行）。",
  "i = 1\nwhile i <= 5:\n    print(i)\n    i += 1",
  "i 从1开始，每次打印后加1，直到5。", 2)
q(T, "用 while 循环打印 3 遍'你好'。",
  "n = 0\nwhile n < 3:\n    print('你好')\n    n += 1",
  "循环 3 次，每次打印'你好'。")
q(T, "用 while 循环打印偶数 2、4、6、8（每个一行）。",
  "i = 2\nwhile i <= 8:\n    print(i)\n    i += 2",
  "i 从2开始每次加2，打印 2 4 6 8。", 2)
q(T, "用 while 循环从 5 倒数到 1（每个一行）。",
  "i = 5\nwhile i >= 1:\n    print(i)\n    i -= 1",
  "i 从5开始每次减1，倒数到1。", 2)
q(T, "用 while 循环累加 1+2+3+4+5，最后打印总和。",
  "i = 1\ns = 0\nwhile i <= 5:\n    s += i\n    i += 1\nprint(s)",
  "s 不断累加 i，最后 s=15。", 2)
q(T, "用 while 循环打印'⭐'一行，循环5次（每次打印后不换行，用 end=''，最后print换行）。",
  "i = 0\nwhile i < 5:\n    print('⭐', end='')\n    i += 1\nprint()",
  "end='' 让打印不换行，5颗星连在一行。", 2)
q(T, "用 while 循环打印 2 的乘法表前5个：2x1=2 到 2x5=10。",
  "i = 1\nwhile i <= 5:\n    print(f'2x{i}={2*i}')\n    i += 1",
  "每次打印 2xi=结果，i 从1到5。", 2)
q(T, "用 while 循环计算 1 到 4 的乘积（1*2*3*4），打印结果。",
  "i = 1\np = 1\nwhile i <= 4:\n    p *= i\n    i += 1\nprint(p)",
  "p 不断乘 i，最后 p=24。", 2)
q(T, "嵌套 while 循环：外层 i=1到2，内层 j=1到2，打印 i 和 j 的组合（如 1 1）。",
  "i = 1\nwhile i <= 2:\n    j = 1\n    while j <= 2:\n        print(i, j)\n        j += 1\n    i += 1",
  "内层循环每次都重新走一遍，打印 1 1 / 1 2 / 2 1 / 2 2。", 2)
q(T, "用 while 循环打印'加油'两遍，再打印'成功'。",
  "n = 0\nwhile n < 2:\n    print('加油')\n    n += 1\nprint('成功')",
  "先循环打印两遍加油，循环结束后打印成功。")

# ===== 8 字符串的查找,判断,修改 =====
T = "字符串的查找,判断,修改"
q(T, "定义 s='apple'，打印 s 的第一个字符（索引0）。",
  "s = 'apple'\nprint(s[0])",
  "索引从0开始，s[0]是第一个字符 a。")
q(T, "定义 s='banana'，打印字符串的长度（用 len）。",
  "s = 'banana'\nprint(len(s))",
  "len(s) 返回字符个数，banana是6。")
q(T, "定义 s='hello world'，打印'world'在不在 s 里（用 in，打印 True/False）。",
  "s = 'hello world'\nprint('world' in s)",
  "in 判断子串是否存在，存在打印 True。")
q(T, "定义 s='cat'，把它变成大写并打印（用 .upper()）。",
  "s = 'cat'\nprint(s.upper())",
  ".upper() 把字母全变大写，CAT。")
q(T, "定义 s='DOG'，把它变成小写并打印（用 .lower()）。",
  "s = 'DOG'\nprint(s.lower())",
  ".lower() 把字母全变小写，dog。")
q(T, "定义 s='I like dogs'，把'dogs'替换成'cats'并打印（用 .replace）。",
  "s = 'I like dogs'\nprint(s.replace('dogs', 'cats'))",
  ".replace(旧,新) 替换子串。", 2)
q(T, "定义 s='abc'，打印 s 重复 3 次的结果。",
  "s = 'abc'\nprint(s * 3)",
  "字符串乘3重复3次，abcabcabc。")
q(T, "定义 s='a,b,c'，用逗号拆分成列表并打印（用 .split）。",
  "s = 'a,b,c'\nprint(s.split(','))",
  ".split(',') 按逗号切成列表 ['a','b','c']。", 2)
q(T, "定义 words=['我','爱','你']，用''连成一个字符串并打印（用 .join）。",
  "words = ['我', '爱', '你']\nprint(''.join(words))",
  "'.join() 把列表连成字符串，我爱你。", 2)
q(T, "定义 s='  hi  '（两边有空格），去掉两边空格后打印（用 .strip）。",
  "s = '  hi  '\nprint(s.strip())",
  ".strip() 去掉首尾空格，打印 hi。", 2)

# ===== 9 列表的定义与增删改查,列表推导式 =====
T = "列表的定义与增删改查,列表推导式"
q(T, "定义一个列表 fruits=['苹果','香蕉']，打印这个列表。",
  "fruits = ['苹果', '香蕉']\nprint(fruits)",
  "列表用方括号定义，print 打印整个列表。")
q(T, "定义 nums=[1,2,3]，打印列表的长度（用 len）。",
  "nums = [1, 2, 3]\nprint(len(nums))",
  "len(nums) 返回元素个数 3。")
q(T, "定义 animals=['猫','狗']，用 .append 加上'兔子'，然后打印列表。",
  "animals = ['猫', '狗']\nanimals.append('兔子')\nprint(animals)",
  ".append() 在末尾添加一个元素。")
q(T, "定义 colors=['红','绿','蓝']，打印第一个元素（索引0）。",
  "colors = ['红', '绿', '蓝']\nprint(colors[0])",
  "索引0是第一个元素，红。")
q(T, "定义 nums=[1,2,3]，把第2个元素（索引1）改成 9，然后打印列表。",
  "nums = [1, 2, 3]\nnums[1] = 9\nprint(nums)",
  "nums[1]=9 修改索引1的元素。", 2)
q(T, "定义 lst=['a','b','c']，用 .remove('b') 删掉'b'，然后打印。",
  "lst = ['a', 'b', 'c']\nlst.remove('b')\nprint(lst)",
  ".remove() 按值删除元素。", 2)
q(T, "定义 nums=[3,1,2]，用 .sort() 排序后打印。",
  "nums = [3, 1, 2]\nnums.sort()\nprint(nums)",
  ".sort() 从小到大排序，[1,2,3]。", 2)
q(T, "用列表推导式生成 1 到 5 的平方，打印这个列表。",
  "squares = [i * i for i in range(1, 6)]\nprint(squares)",
  "[i*i for i in range(1,6)] 生成平方列表。", 2)
q(T, "用列表推导式从 [1,2,3,4,5] 中挑出偶数，打印结果。",
  "nums = [1, 2, 3, 4, 5]\nevens = [n for n in nums if n % 2 == 0]\nprint(evens)",
  "列表推导式加 if 过滤，挑出偶数 [2,4]。", 2)
q(T, "定义 toys=['车','球']，用 .insert(1,'娃娃') 在中间插入，然后打印。",
  "toys = ['车', '球']\ntoys.insert(1, '娃娃')\nprint(toys)",
  ".insert(位置,值) 在指定位置插入。", 2)

# ===== 10 元组,字典的定义与字典的增删改查 =====
T = "元组,字典的定义与字典的增删改查"
q(T, "定义一个元组 point=(3, 4)，打印这个元组。",
  "point = (3, 4)\nprint(point)",
  "元组用小括号定义，print 打印。")
q(T, "定义元组 t=('a','b','c')，打印它的长度。",
  "t = ('a', 'b', 'c')\nprint(len(t))",
  "len(t) 返回元素个数 3。")
q(T, "定义字典 person={'name':'小明','age':9}，打印这个字典。",
  "person = {'name': '小明', 'age': 9}\nprint(person)",
  "字典用花括号定义，键值对用冒号。")
q(T, "定义字典 d={'cat':'猫','dog':'狗'}，打印键'cat'对应的值。",
  "d = {'cat': '猫', 'dog': '狗'}\nprint(d['cat'])",
  "d['cat'] 按键取值，打印 猫。")
q(T, "定义字典 scores={'语文':90}，添加一个键'数学'值为95，然后打印字典。",
  "scores = {'语文': 90}\nscores['数学'] = 95\nprint(scores)",
  "字典[新键]=值 就是添加新键值对。", 2)
q(T, "定义字典 d={'a':1,'b':2}，把键'a'的值改成 10，然后打印。",
  "d = {'a': 1, 'b': 2}\nd['a'] = 10\nprint(d)",
  "d['a']=10 修改已有键的值。", 2)
q(T, "定义字典 d={'x':1,'y':2}，用 del 删除键'x'，然后打印字典。",
  "d = {'x': 1, 'y': 2}\ndel d['x']\nprint(d)",
  "del d['x'] 删除键值对。", 2)
q(T, "定义字典 d={'name':'小红'}，用 .get('age', 0) 安全地取'age'（没有就返回0），打印结果。",
  "d = {'name': '小红'}\nprint(d.get('age', 0))",
  ".get(键,默认值) 键不存在时返回默认值0。", 2)
q(T, "定义字典 d={'a':1,'b':2,'c':3}，打印字典所有键（用 .keys()）。",
  "d = {'a': 1, 'b': 2, 'c': 3}\nprint(d.keys())",
  ".keys() 返回所有键。", 2)
q(T, "定义元组 nums=(10,20,30)，打印索引1的元素。",
  "nums = (10, 20, 30)\nprint(nums[1])",
  "元组也能用索引取值，nums[1]=20。")

with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\python_coding_new_p1.json", "w", encoding="utf-8") as f:
    json.dump(Q, f, ensure_ascii=False, indent=2)
from collections import Counter
print(f"第1-10课共 {len(Q)} 题")
print("分布:", dict(Counter(q['topic_name'] for q in Q)))
