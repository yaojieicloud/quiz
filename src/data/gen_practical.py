"""生成 Python 基础实操题库（20 课 × 10 题 = 200 题，递进式）。

设计原则：
- 每课 10 题，难度由浅入深；后一课的题目综合运用前面所有课的知识点。
- 每题包含：
    content         题干（给出确定的数据，要求学生编码输出确定结果）
    explanation     指引思路（讲怎么想、用什么概念，但不直接给完整代码）
    answer          参考代码（仅用于后台实跑判分，接口层对学生隐藏）
    sample_input    若参考代码用到 input()，给出样例输入
    expected_output 由本脚本实跑 answer 得到，作为判分标准
- 所有题目输出确定（大多不依赖 input），保证判分稳定。

运行：python data/gen_practical.py  → 覆盖写 data/python_coding200.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from core.code_runner import run_python  # noqa: E402

OUT = ROOT / "python_coding200.json"

SUBJECT = {
    "name": "Python基础实操",
    "icon": "💻",
    "grade": "L1-L20 递进",
    "desc": "Python 编程实操：20 课循序渐进，后一课综合运用前面所有知识点",
    "category": "programming",
}

# 每章 (content, explanation, answer, sample_input)
CHAPTERS = []


def ch(name, items):
    CHAPTERS.append((name, items))


# ================= 第1课 变量与标识符 =================
ch("变量与标识符", [
    ("定义一个变量 name，赋值为字符串 小明，然后用 print 打印这个变量。",
     "先写 name = '小明'，注意变量名不加引号、字符串的值要加引号；再用 print(name) 打印。",
     'name = "小明"\nprint(name)', ""),
    ("定义一个变量 age，表示年龄 10，把它打印出来。",
     "整数不用加引号：age = 10，然后 print(age)。",
     'age = 10\nprint(age)', ""),
    ("定义变量 a = 3 和 b = 8，先打印 a，再打印 b（各占一行）。",
     "写两个赋值语句，再用两次 print 分别打印。",
     'a = 3\nb = 8\nprint(a)\nprint(b)', ""),
    ("定义变量 school，保存学校名字 阳光小学，把它打印出来。",
     "school = '阳光小学'，然后 print(school)。",
     'school = "阳光小学"\nprint(school)', ""),
    ("有两个变量 a = 1、b = 2。请交换它们的值，交换后先打印 a 再打印 b（应输出 2 和 1）。",
     "可以用第三个变量中转：t=a; a=b; b=t；也可以用 Python 的 a, b = b, a 一步交换。",
     'a = 1\nb = 2\na, b = b, a\nprint(a)\nprint(b)', ""),
    ("定义圆周率变量 pi = 3.14，把它打印出来。",
     "小数直接写：pi = 3.14，再 print(pi)。",
     'pi = 3.14\nprint(pi)', ""),
    ("用连续赋值让 x 和 y 同时等于 7，然后分别打印 x 和 y（各一行）。",
     "可以写 x = y = 7，一次给两个变量赋同样的值。",
     'x = y = 7\nprint(x)\nprint(y)', ""),
    ("定义变量 color 保存 红色，再把 color 重新赋值为 蓝色，最后打印 color（应输出 蓝色）。",
     "变量可以被重新赋值，最后一次赋的值才是它当前的值。",
     'color = "红色"\ncolor = "蓝色"\nprint(color)', ""),
    ("定义变量 score = 95 并打印；再用 score = score + 5 让它增加 5，打印新的 score。",
     "score = score + 5 的意思是：把 score 现在的值加 5，再存回 score。",
     'score = 95\nprint(score)\nscore = score + 5\nprint(score)', ""),
    ("定义三个变量：chinese = 90、math = 100、english = 85，把它们分别打印出来（三行）。",
     "写三个赋值语句，再用三次 print。",
     'chinese = 90\nmath = 100\nenglish = 85\nprint(chinese)\nprint(math)\nprint(english)', ""),
])

# ================= 第2课 debug注释与输出函数 =================
ch("debug注释与输出函数", [
    ("用一个 print 一次性打印三个词：早上 好 呀（用逗号分开写，默认用空格连接）。",
     "print('早上','好','呀')，逗号分隔的多个内容会自动用空格连起来。",
     'print("早上", "好", "呀")', ""),
    ("用 print 打印 1、2、3，要求用 - 号连接，输出成 1-2-3。",
     "用 sep 参数指定分隔符：print(1,2,3,sep='-')。",
     'print(1, 2, 3, sep="-")', ""),
    ("先写一行以 # 开头的注释（内容随意），再用 print 打印 hello。",
     "注释用 # 开头，Python 运行时会忽略它；下一行再 print('hello')。",
     '# 打印一句问候\nprint("hello")', ""),
    ("用两个 print 分别打印 猫 和 狗，但让它们出现在同一行、且中间没有空格，最终输出 猫狗。",
     "print 默认在末尾换行，把第一个 print 的 end 设为空字符串：print('猫', end='')。",
     'print("猫", end="")\nprint("狗")', ""),
    ("用一个 print 打印 姓名: 和 小红，两部分用逗号分开写（会以空格连接成 姓名: 小红）。",
     "print('姓名:', '小红')，逗号会让两部分之间出现一个空格。",
     'print("姓名:", "小红")', ""),
    ("用 print 打印 100、200、300，参数用逗号分开，分隔符用 /，输出 100/200/300。",
     "print(100,200,300,sep='/')。",
     'print(100, 200, 300, sep="/")', ""),
    ("用三个 print 打印 A、B、C，让它们在同一行显示成 ABC。",
     "前两个 print 用 end=''，最后一个正常换行。",
     'print("A", end="")\nprint("B", end="")\nprint("C")', ""),
    ("把整句话 Python 很好玩 作为一个字符串打印出来。",
     "把整句放进一对引号里：print('Python 很好玩')。",
     'print("Python 很好玩")', ""),
    ("用两个 print 打印两行诗：床前明月光 和 疑是地上霜。",
     "写两个 print，各打印一句，print 默认会换行。",
     'print("床前明月光")\nprint("疑是地上霜")', ""),
    ("用一个 print 打印 2026、1、1 三个数字，用 sep='-' 连接，输出 2026-1-1。",
     "print(2026,1,1,sep='-')。",
     'print(2026, 1, 1, sep="-")', ""),
])

# ================= 第3课 数值类型,字符串与格式化输出 =================
ch("数值类型,字符串与格式化输出", [
    ("定义 name='小明'，用 f-string 打印出 我叫小明。",
     "f-string 写法：print(f'我叫{name}')，大括号里放变量名。",
     'name = "小明"\nprint(f"我叫{name}")', ""),
    ("定义 a=3、b=4，用 f-string 打印 3加4等于7（7 用 {a+b} 现算）。",
     "大括号里可以放表达式：f'{a}加{b}等于{a+b}'。",
     'a = 3\nb = 4\nprint(f"{a}加{b}等于{a+b}")', ""),
    ("定义字符串 word='python'，打印它的长度（应是 6）。",
     "用 len(word) 求长度，再 print 出来。",
     'word = "python"\nprint(len(word))', ""),
    ("用字符串加法把 Hello 和 World 连接成 HelloWorld 并打印。",
     "字符串用 + 号直接拼接：'Hello' + 'World'。",
     'print("Hello" + "World")', ""),
    ("定义 price=5、count=3，用 f-string 打印 一共15元（15 由 price*count 算出）。",
     "f'一共{price*count}元'。",
     'price = 5\ncount = 3\nprint(f"一共{price*count}元")', ""),
    ("把字符串 ha 重复 3 次打印出来，得到 hahaha。",
     "字符串乘以整数表示重复：'ha' * 3。",
     'print("ha" * 3)', ""),
    ("定义 pi=3.14159，用 f-string 保留 2 位小数打印（应是 3.14）。",
     "f'{pi:.2f}' 表示把 pi 保留两位小数。",
     'pi = 3.14159\nprint(f"{pi:.2f}")', ""),
    ("定义 name='小红'、age=9，用一个 f-string 打印 小红今年9岁。",
     "f'{name}今年{age}岁'。",
     'name = "小红"\nage = 9\nprint(f"{name}今年{age}岁")', ""),
    ("定义字符串 s='abcdef'，打印它的第一个字符（用 s[0]，应是 a）。",
     "字符串可以用下标取字符，下标从 0 开始，s[0] 就是第一个。",
     's = "abcdef"\nprint(s[0])', ""),
    ("定义 a=10、b=3，用 f-string 打印 10除以3约等于3.33（结果保留 2 位小数）。",
     "f'{a}除以{b}约等于{a/b:.2f}'。",
     'a = 10\nb = 3\nprint(f"{a}除以{b}约等于{a/b:.2f}")', ""),
])

# ================= 第4课 算数与赋值运算符,输入函数与转义字符 =================
ch("算数与赋值运算符,输入函数与转义字符", [
    ("计算 7 加 5 的结果并打印（应是 12）。",
     "直接 print(7 + 5)，加号是加法运算符。",
     'print(7 + 5)', ""),
    ("计算 17 除以 5 的整数商和余数，分两行打印（应是 3 和 2）。",
     "// 是整除（取商），% 是取余数；分别打印 17//5 和 17%5。",
     'print(17 // 5)\nprint(17 % 5)', ""),
    ("计算 2 的 10 次方并打印（应是 1024）。",
     "** 是乘方运算符：2 ** 10。",
     'print(2 ** 10)', ""),
    ("定义 total=10，用增量赋值 total += 5 让它加 5，打印结果（应是 15）。",
     "total += 5 等价于 total = total + 5。",
     'total = 10\ntotal += 5\nprint(total)', ""),
    ("用一个 print 打印两行：你好 和 再见（中间用换行转义字符 \\n）。",
     "在字符串里写 \\n 表示换行：print('你好\\n再见')。",
     'print("你好\\n再见")', ""),
    ("用 print 打印 姓名 和 年龄 两个词，中间用制表符 \\t 隔开。",
     "\\t 是制表符（Tab）：print('姓名\\t年龄')。",
     'print("姓名\\t年龄")', ""),
    ("用 input() 读入一个整数（代表苹果数量），把它的 2 倍打印出来。（判分时会输入 6，应输出 12）",
     "input() 读到的是字符串，要用 int() 转成整数：n = int(input())，再打印 n*2。",
     'n = int(input())\nprint(n * 2)', "6\n"),
    ("用 input() 分两行读入两个整数，打印它们的和。（判分时输入 4 和 9，应输出 13）",
     "调用两次 input() 并各用 int() 转换，再把两个数相加打印。",
     'a = int(input())\nb = int(input())\nprint(a + b)', "4\n9\n"),
    ("计算 (3 + 5) * 2 并打印（应是 16），注意先算括号里的。",
     "括号可以改变运算顺序：print((3 + 5) * 2)。",
     'print((3 + 5) * 2)', ""),
    ("定义 n=3，用增量赋值 n *= 4 让它乘以 4，打印结果（应是 12）。",
     "n *= 4 等价于 n = n * 4。",
     'n = 3\nn *= 4\nprint(n)', ""),
])

# ================= 第5课 if判断,比较运算符,逻辑运算符 =================
ch("if判断,比较运算符,逻辑运算符", [
    ("定义 score=85，如果 score 大于等于 60，就打印 及格。",
     "用 if score >= 60: 判断，条件成立时（注意缩进）执行 print('及格')。",
     'score = 85\nif score >= 60:\n    print("及格")', ""),
    ("定义 x=8，如果 x 是偶数（x % 2 == 0），就打印 偶数。",
     "偶数的特点是除以 2 余数为 0，即 x % 2 == 0。",
     'x = 8\nif x % 2 == 0:\n    print("偶数")', ""),
    ("定义 a=5、b=3，如果 a 大于 b，打印 a大。",
     "用 if a > b: 比较两个数。",
     'a = 5\nb = 3\nif a > b:\n    print("a大")', ""),
    ("定义 age=20，如果 age 大于等于 18 并且 小于 60，打印 青壮年。",
     "两个条件都要满足，用 and 连接：if age >= 18 and age < 60:。",
     'age = 20\nif age >= 18 and age < 60:\n    print("青壮年")', ""),
    ("定义 n=15，如果 n 能被 3 整除 或者 能被 5 整除，打印 符合。",
     "满足其中一个即可，用 or 连接：if n % 3 == 0 or n % 5 == 0:。",
     'n = 15\nif n % 3 == 0 or n % 5 == 0:\n    print("符合")', ""),
    ("定义 is_rain=True，如果下雨（is_rain 为真），打印 带伞。",
     "布尔变量可直接作条件：if is_rain:。",
     'is_rain = True\nif is_rain:\n    print("带伞")', ""),
    ("定义 money=50、price=30，如果钱够（money 大于等于 price），打印 买得起。",
     "if money >= price: 判断钱是否足够。",
     'money = 50\nprice = 30\nif money >= price:\n    print("买得起")', ""),
    ("定义 ch='G'，如果它是大写字母（在 'A' 到 'Z' 之间），打印 大写字母。",
     "字符可以比较大小：if ch >= 'A' and ch <= 'Z':。",
     'ch = "G"\nif ch >= "A" and ch <= "Z":\n    print("大写字母")', ""),
    ("定义 num=0，如果 num 等于 0，打印 零。",
     "判断相等用两个等号 ==：if num == 0:。",
     'num = 0\nif num == 0:\n    print("零")', ""),
    ("定义 done=False，如果任务没完成（not done），打印 继续加油。",
     "not 表示取反，not False 就是 True：if not done:。",
     'done = False\nif not done:\n    print("继续加油")', ""),
])

# ================= 第6课 if-else,if-elif与嵌套if =================
ch("if-else,if-elif与嵌套if", [
    ("定义 score=55，如果大于等于 60 打印 及格，否则打印 不及格。",
     "用 if...else...：条件不成立时走 else 分支。",
     'score = 55\nif score >= 60:\n    print("及格")\nelse:\n    print("不及格")', ""),
    ("定义 num=7，判断它是偶数还是奇数，偶数打印 偶数、奇数打印 奇数。",
     "num % 2 == 0 为偶数，否则为奇数，用 if-else。",
     'num = 7\nif num % 2 == 0:\n    print("偶数")\nelse:\n    print("奇数")', ""),
    ("定义 age=20，大于等于 18 打印 成年，否则打印 未成年。",
     "if age >= 18: ... else: ...。",
     'age = 20\nif age >= 18:\n    print("成年")\nelse:\n    print("未成年")', ""),
    ("定义 score=75，用 if-elif-else 分档：>=90 打印 优秀，>=60 打印 及格，否则打印 不及格。",
     "elif 用来写多个条件，从上往下依次判断，命中一个就不再往下走。",
     'score = 75\nif score >= 90:\n    print("优秀")\nelif score >= 60:\n    print("及格")\nelse:\n    print("不及格")', ""),
    ("定义 year=2024，判断是否闰年（能被 4 整除且不能被 100 整除，或能被 400 整除），是打印 闰年、否则打印 平年。",
     "闰年条件：(year%4==0 and year%100!=0) or year%400==0。",
     'year = 2024\nif (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:\n    print("闰年")\nelse:\n    print("平年")', ""),
    ("定义 a=3、b=8、c=5，找出三个数里最大的并打印（应是 8）。",
     "先假设 a 最大，再依次和 b、c 比较，用 if 更新最大值。",
     'a = 3\nb = 8\nc = 5\nm = a\nif b > m:\n    m = b\nif c > m:\n    m = c\nprint(m)', ""),
    ("定义 temp=35，用 if-elif-else：>=30 打印 热，>=10 打印 舒适，否则打印 冷。",
     "从最高档往下写 elif。",
     'temp = 35\nif temp >= 30:\n    print("热")\nelif temp >= 10:\n    print("舒适")\nelse:\n    print("冷")', ""),
    ("定义 n=-5，判断它是正数、负数还是零，分别打印 正数/负数/零。",
     "先判断 n>0，再 elif n<0，else 就是零。",
     'n = -5\nif n > 0:\n    print("正数")\nelif n < 0:\n    print("负数")\nelse:\n    print("零")', ""),
    ("定义 score=88，按等级打印：>=90 打印 A，>=80 打印 B，>=60 打印 C，否则打印 D。",
     "用 if-elif 链，从高分档到低分档依次判断。",
     'score = 88\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelif score >= 60:\n    print("C")\nelse:\n    print("D")', ""),
    ("定义 age=20、has_ticket=True，用嵌套 if：先判断是否成年（>=18），成年后再判断有没有票，都满足才打印 可入场。",
     "外层 if 判断年龄，里层 if 判断是否有票，注意里层要多缩进一层。",
     'age = 20\nhas_ticket = True\nif age >= 18:\n    if has_ticket:\n        print("可入场")', ""),
])

# ================= 第7课 while循环与嵌套循环 =================
ch("while循环与嵌套循环", [
    ("用 while 循环打印 1 到 5，每个数字占一行。",
     "先设 i=1，循环条件 while i<=5，每次打印后 i+=1。",
     'i = 1\nwhile i <= 5:\n    print(i)\n    i += 1', ""),
    ("用 while 循环计算 1+2+3+...+100 的总和并打印（应是 5050）。",
     "用变量 s 累加，i 从 1 到 100，每次 s += i。",
     's = 0\ni = 1\nwhile i <= 100:\n    s += i\n    i += 1\nprint(s)', ""),
    ("用 while 循环，打印 1 到 10 之间的所有偶数（每行一个）。",
     "循环里用 if i%2==0 判断是不是偶数，是就打印。",
     'i = 1\nwhile i <= 10:\n    if i % 2 == 0:\n        print(i)\n    i += 1', ""),
    ("用 while 循环倒着打印 5 4 3 2 1（每行一个）。",
     "让 i 从 5 开始，条件 i>=1，每次 i-=1。",
     'i = 5\nwhile i >= 1:\n    print(i)\n    i -= 1', ""),
    ("用 while 循环计算 5 的阶乘 5*4*3*2*1 并打印（应是 120）。",
     "用 result 从 1 开始，i 从 1 到 5，每次 result *= i。",
     'result = 1\ni = 1\nwhile i <= 5:\n    result *= i\n    i += 1\nprint(result)', ""),
    ("用 while 循环打印 1、2、3 的平方（1 4 9，每行一个）。",
     "i 从 1 到 3，每次打印 i*i。",
     'i = 1\nwhile i <= 3:\n    print(i * i)\n    i += 1', ""),
    ("用嵌套 while 打印一个 3 行、每行 3 个星号的方块（每行 ***）。",
     "外层循环控制行数，内层循环用 end='' 打印 3 个星号，内层结束后 print() 换行。",
     'row = 1\nwhile row <= 3:\n    col = 1\n    while col <= 3:\n        print("*", end="")\n        col += 1\n    print()\n    row += 1', ""),
    ("用 while 循环统计 1 到 100 中能被 7 整除的数有多少个，打印这个个数。",
     "循环里用 if i%7==0 计数，count += 1。",
     'count = 0\ni = 1\nwhile i <= 100:\n    if i % 7 == 0:\n        count += 1\n    i += 1\nprint(count)', ""),
    ("用 while 循环从 1 开始累加（1+2+3+...），当总和第一次超过 50 时停止，打印这个总和。",
     "边加边判断，s 超过 50 就 break 跳出循环。",
     's = 0\ni = 1\nwhile True:\n    s += i\n    if s > 50:\n        break\n    i += 1\nprint(s)', ""),
    ("用嵌套 while 打印一个直角三角形：第 1 行 1 个星、第 2 行 2 个……到第 4 行 4 个星。",
     "外层控制行 row（1~4），内层打印 row 个星号（end=''），每行末尾换行。",
     'row = 1\nwhile row <= 4:\n    col = 1\n    while col <= row:\n        print("*", end="")\n        col += 1\n    print()\n    row += 1', ""),
])

# ================= 第8课 字符串的查找,判断,修改 =================
ch("字符串的查找,判断,修改", [
    ("定义 s='hello world'，把它全部变成大写并打印。",
     "字符串方法 upper() 返回大写形式：s.upper()。",
     's = "hello world"\nprint(s.upper())', ""),
    ("定义 s='Python'，把它全部变成小写并打印。",
     "用 lower() 方法：s.lower()。",
     's = "Python"\nprint(s.lower())', ""),
    ("定义 s='hello'，把里面所有的 l 换成大写 L 并打印（结果 heLLo）。",
     "replace('l','L') 把所有 l 替换成 L。",
     's = "hello"\nprint(s.replace("l", "L"))', ""),
    ("定义 s='banana'，统计字母 a 出现了几次并打印（应是 3）。",
     "count('a') 统计某个字符出现的次数。",
     's = "banana"\nprint(s.count("a"))', ""),
    ("定义 s='hello world'，用 find 找出 world 第一次出现的位置并打印（应是 6）。",
     "find('world') 返回子串第一次出现的下标（从 0 数）。",
     's = "hello world"\nprint(s.find("world"))', ""),
    ("定义 s='  hi  '（两边有空格），用 strip 去掉两边空格后打印。",
     "strip() 去掉字符串首尾的空白。",
     's = "  hi  "\nprint(s.strip())', ""),
    ("定义 s='apple,banana,pear'，用逗号把它切成一个列表并打印。",
     "split(',') 按逗号切分成列表。",
     's = "apple,banana,pear"\nprint(s.split(","))', ""),
    ("定义 s='python'，判断它是否以 py 开头，打印判断结果（True 或 False）。",
     "startswith('py') 判断是否以某段开头，返回 True/False。",
     's = "python"\nprint(s.startswith("py"))', ""),
    ("定义 s='HELLO'，判断 ELL 是否包含在其中，打印结果（True 或 False）。",
     "用 in 判断子串是否存在：'ELL' in s。",
     's = "HELLO"\nprint("ELL" in s)', ""),
    ("定义 s='2026-01-01'，把里面的 - 全部换成 / 并打印（结果 2026/01/01）。",
     "replace('-','/') 把所有短横线换成斜杠。",
     's = "2026-01-01"\nprint(s.replace("-", "/"))', ""),
])

# ================= 第9课 列表的定义与增删改查,列表推导式 =================
ch("列表的定义与增删改查,列表推导式", [
    ("定义一个列表 nums = [1, 2, 3] 并打印它。",
     "列表用方括号定义，元素用逗号分开。",
     'nums = [1, 2, 3]\nprint(nums)', ""),
    ("定义列表 fruits = ['苹果', '香蕉']，用 append 加入 橘子，然后打印整个列表。",
     "append('橘子') 会把元素加到列表末尾。",
     'fruits = ["苹果", "香蕉"]\nfruits.append("橘子")\nprint(fruits)', ""),
    ("定义列表 nums = [5, 3, 8, 1]，从小到大排序后打印。",
     "列表的 sort() 方法会把列表就地排好序。",
     'nums = [5, 3, 8, 1]\nnums.sort()\nprint(nums)', ""),
    ("定义列表 nums = [10, 20, 30]，打印它的第二个元素（下标 1，应是 20）。",
     "列表下标从 0 开始，第二个就是 nums[1]。",
     'nums = [10, 20, 30]\nprint(nums[1])', ""),
    ("定义列表 nums = [1, 2, 3, 4]，用 sum 求所有元素的和并打印（应是 10）。",
     "sum(nums) 直接求列表元素之和。",
     'nums = [1, 2, 3, 4]\nprint(sum(nums))', ""),
    ("用列表推导式生成 1 到 5 的平方组成的列表并打印（[1, 4, 9, 16, 25]）。",
     "列表推导式写法：[i*i for i in range(1, 6)]。",
     'squares = [i * i for i in range(1, 6)]\nprint(squares)', ""),
    ("定义 nums = [1, 2, 3, 4, 5, 6]，用列表推导式挑出所有偶数组成新列表并打印（[2, 4, 6]）。",
     "在推导式后面加 if 条件：[x for x in nums if x % 2 == 0]。",
     'nums = [1, 2, 3, 4, 5, 6]\nevens = [x for x in nums if x % 2 == 0]\nprint(evens)', ""),
    ("定义列表 data = [3, 1, 2]，用 len 打印它的长度（应是 3）。",
     "len(data) 求列表里有几个元素。",
     'data = [3, 1, 2]\nprint(len(data))', ""),
    ("定义列表 names = ['a', 'b', 'c']，用 for 循环把每个元素单独打印一行。",
     "for name in names: 逐个取出元素并打印。",
     'names = ["a", "b", "c"]\nfor name in names:\n    print(name)', ""),
    ("定义列表 nums = [4, 8, 15]，用 max 找出最大值并打印（应是 15）。",
     "max(nums) 返回列表里最大的元素。",
     'nums = [4, 8, 15]\nprint(max(nums))', ""),
])

# ================= 第10课 元组,字典的定义与字典的增删改查 =================
ch("元组,字典的定义与字典的增删改查", [
    ("定义一个元组 t = (1, 2, 3) 并打印它。",
     "元组用小括号定义，元素用逗号分开，定义后不能修改。",
     't = (1, 2, 3)\nprint(t)', ""),
    ("定义字典 d = {'name': '小明', 'age': 10}，打印 name 对应的值（小明）。",
     "用键取值：d['name']。",
     'd = {"name": "小明", "age": 10}\nprint(d["name"])', ""),
    ("定义字典 d = {'a': 1}，新增一个键值对 'b': 2，然后打印整个字典。",
     "给字典一个新键赋值即可新增：d['b'] = 2。",
     'd = {"a": 1}\nd["b"] = 2\nprint(d)', ""),
    ("定义字典 scores = {'语文': 90, '数学': 100}，打印 数学 的分数（100）。",
     "scores['数学'] 取出数学对应的值。",
     'scores = {"语文": 90, "数学": 100}\nprint(scores["数学"])', ""),
    ("定义字典 d = {'x': 1, 'y': 2}，用 get 取键 'z'（不存在时返回默认值 0）并打印（应是 0）。",
     "d.get('z', 0)：键不存在时返回你给的默认值，不会报错。",
     'd = {"x": 1, "y": 2}\nprint(d.get("z", 0))', ""),
    ("定义字典 d = {'a': 1, 'b': 2}，用 for 循环逐行打印成 键=值 的形式。",
     "for k, v in d.items(): 同时取出键和值，再用 f-string 打印 f'{k}={v}'。",
     'd = {"a": 1, "b": 2}\nfor k, v in d.items():\n    print(f"{k}={v}")', ""),
    ("定义元组 t = (10, 20)，用拆包 a, b = t 分别得到两个值，打印 a 和 b（各一行）。",
     "拆包：a, b = t 会把元组里的两个值分别给 a 和 b。",
     't = (10, 20)\na, b = t\nprint(a)\nprint(b)', ""),
    ("定义字典 d = {'苹果': 3, '香蕉': 5}，把所有水果数量加起来打印（应是 8）。",
     "sum(d.values()) 对字典所有的值求和。",
     'd = {"苹果": 3, "香蕉": 5}\nprint(sum(d.values()))', ""),
    ("定义字典 d = {'a': 1, 'b': 2, 'c': 3}，把它的所有键组成一个列表打印（['a', 'b', 'c']）。",
     "list(d.keys()) 把所有键收集成列表。",
     'd = {"a": 1, "b": 2, "c": 3}\nprint(list(d.keys()))', ""),
    ("定义字典 d = {'name': 'Tom'}，把 name 修改成 Jerry，然后打印整个字典。",
     "给已存在的键重新赋值即可修改：d['name'] = 'Jerry'。",
     'd = {"name": "Tom"}\nd["name"] = "Jerry"\nprint(d)', ""),
])

# ================= 第11课 类型转换 =================
ch("类型转换, int,float,str,bool等", [
    ("把字符串 '123' 转成整数后加 1，打印结果（应是 124）。",
     "int('123') 把字符串转成整数，再加 1。",
     'print(int("123") + 1)', ""),
    ("把小数 3.9 用 int() 转成整数并打印（会直接去掉小数部分，得到 3）。",
     "int(3.9) 只保留整数部分，不会四舍五入。",
     'print(int(3.9))', ""),
    ("把整数 100 转成字符串，和 分 拼接成 100分 并打印。",
     "str(100) 转成字符串后才能和 '分' 用 + 拼接。",
     'print(str(100) + "分")', ""),
    ("把字符串 '3.14' 转成小数（float）并打印。",
     "float('3.14') 把字符串转成小数。",
     'print(float("3.14"))', ""),
    ("把列表 [1, 2, 3] 转成元组并打印。",
     "tuple([1,2,3]) 把列表转成元组。",
     'print(tuple([1, 2, 3]))', ""),
    ("把字符串 'hello' 转成字符列表并打印（['h', 'e', 'l', 'l', 'o']）。",
     "list('hello') 会把字符串拆成单个字符组成列表。",
     'print(list("hello"))', ""),
    ("把整数 3.0（小数）转成整数打印，再把 True 转成整数打印（两行，分别是 3 和 1）。",
     "int(3.0) 得 3；bool 转 int 时 True 是 1、False 是 0。",
     'print(int(3.0))\nprint(int(True))', ""),
    ("把两个字符串 '10' 和 '20' 都转成整数后相加并打印（应是 30，而不是拼成 1020）。",
     "字符串直接相加会拼接，先各用 int() 转成数字再加。",
     'print(int("10") + int("20"))', ""),
    ("把数字 0 转成布尔值打印，再把数字 5 转成布尔值打印（两行，分别是 False 和 True）。",
     "bool(0) 是 False，非 0 数字转成布尔都是 True。",
     'print(bool(0))\nprint(bool(5))', ""),
    ("有一个字符串 '8'，请把它转成整数后判断是不是偶数，是就打印 偶数。",
     "先 int('8') 转成数字，再用 % 2 == 0 判断（结合第 5 课的 if）。",
     'n = int("8")\nif n % 2 == 0:\n    print("偶数")', ""),
])

# ================= 第12课 赋值,深浅拷贝,可变与不可变对象 =================
ch("赋值,深浅拷贝,可变与不可变对象", [
    ("定义 a = [1, 2, 3]，用 a.copy() 复制出 b，再给 b 追加 4，最后打印 a（应还是 [1, 2, 3]）。",
     "copy() 得到的是独立的新列表，改 b 不影响 a。",
     'a = [1, 2, 3]\nb = a.copy()\nb.append(4)\nprint(a)', ""),
    ("定义 a = [1, 2]，直接写 b = a，再给 b 追加 3，最后打印 a（会变成 [1, 2, 3]）。",
     "b = a 只是给同一个列表起了别名，两者指向同一份数据。",
     'a = [1, 2]\nb = a\nb.append(3)\nprint(a)', ""),
    ("定义 a = [1, 2, 3]，用切片 a[:] 复制出 b，给 b 追加 9，打印 a（应还是 [1, 2, 3]）。",
     "a[:] 是常用的整段切片拷贝，得到独立副本。",
     'a = [1, 2, 3]\nb = a[:]\nb.append(9)\nprint(a)', ""),
    ("定义数字 a = 5，令 b = a，再让 b = b + 1，打印 a（应还是 5）。",
     "数字是不可变对象，b 改变不会影响 a。",
     'a = 5\nb = a\nb = b + 1\nprint(a)', ""),
    ("定义字符串 s = 'abc'，用 replace 生成 s2（把 a 换成 x），打印 s（应还是 abc）。",
     "字符串不可变，replace 返回新字符串，原字符串不变。",
     's = "abc"\ns2 = s.replace("a", "x")\nprint(s)', ""),
    ("定义 a = [[1, 2], [3, 4]]，用 copy 模块的 deepcopy 复制成 b，修改 b[0][0]=99，打印 a（应还是 [[1, 2], [3, 4]]）。",
     "嵌套列表要用 import copy 后的 copy.deepcopy 才能彻底独立。",
     'import copy\na = [[1, 2], [3, 4]]\nb = copy.deepcopy(a)\nb[0][0] = 99\nprint(a)', ""),
    ("定义 a = [[1, 2]]，用 a.copy() 做浅拷贝得到 b，修改 b[0][0]=99，打印 a，观察浅拷贝对里层的影响（会变成 [[99, 2]]）。",
     "浅拷贝只复制最外层，里层的小列表还是共享的，所以里层会一起变。",
     'a = [[1, 2]]\nb = a.copy()\nb[0][0] = 99\nprint(a)', ""),
    ("定义元组 t = (1, 2, 3)，打印它的第一个元素（应是 1）。元组不可修改，但可以读取。",
     "元组用下标读取和列表一样：t[0]。",
     't = (1, 2, 3)\nprint(t[0])', ""),
    ("定义 a = [1, 2, 3]，用 list(a) 复制成 b，给 b 追加 4，打印 a（应还是 [1, 2, 3]）。",
     "list(a) 也能生成一个独立的新列表。",
     'a = [1, 2, 3]\nb = list(a)\nb.append(4)\nprint(a)', ""),
    ("定义 a = [1, 2]，用切片得到 b = a[:]，打印 a == b（比较内容）和 a is b（比较是否同一个对象）两行（应是 True 和 False）。",
     "== 比较内容是否相同，is 比较是不是同一个对象；拷贝后内容相同但不是同一个。",
     'a = [1, 2]\nb = a[:]\nprint(a == b)\nprint(a is b)', ""),
])

# ================= 第13课 函数,return返回值与形参实参 =================
ch("函数,return返回值与形参实参", [
    ("定义函数 add(a, b) 返回两数之和，调用 add(3, 4) 并打印结果（应是 7）。",
     "用 def 定义函数，return 返回结果；再 print(add(3,4)) 打印返回值。",
     'def add(a, b):\n    return a + b\nprint(add(3, 4))', ""),
    ("定义函数 greet(name)，功能是打印 你好,加上名字；调用 greet('小明')（输出 你好,小明）。",
     "函数体里直接 print(f'你好,{name}')，然后调用它。",
     'def greet(name):\n    print(f"你好,{name}")\ngreet("小明")', ""),
    ("定义函数 square(n) 返回 n 的平方，打印 square(5)（应是 25）。",
     "return n * n。",
     'def square(n):\n    return n * n\nprint(square(5))', ""),
    ("定义函数 max2(a, b) 返回两个数里较大的那个，打印 max2(3, 8)（应是 8）。",
     "函数里用 if a > b: return a else: return b。",
     'def max2(a, b):\n    if a > b:\n        return a\n    else:\n        return b\nprint(max2(3, 8))', ""),
    ("定义函数 is_even(n)，n 是偶数返回 True 否则返回 False，打印 is_even(4)（应是 True）。",
     "return n % 2 == 0，直接把比较结果返回。",
     'def is_even(n):\n    return n % 2 == 0\nprint(is_even(4))', ""),
    ("定义函数 mysum(lst) 返回列表所有元素之和，打印 mysum([1, 2, 3, 4])（应是 10）。",
     "函数里可以直接 return sum(lst)，或用循环累加。",
     'def mysum(lst):\n    return sum(lst)\nprint(mysum([1, 2, 3, 4]))', ""),
    ("定义函数 area(w, h) 返回矩形面积，打印 area(3, 4)（应是 12）。",
     "面积 = 宽 × 高：return w * h。",
     'def area(w, h):\n    return w * h\nprint(area(3, 4))', ""),
    ("定义函数 count_down(n)，用循环从 n 打印到 1（每行一个），调用 count_down(3)。",
     "函数里写 while 循环，i 从 n 递减到 1（结合第 7 课）。",
     'def count_down(n):\n    i = n\n    while i >= 1:\n        print(i)\n        i -= 1\ncount_down(3)', ""),
    ("定义函数 power(base, exp=2)，返回 base 的 exp 次方，exp 默认是 2；打印 power(3)（不传 exp，应是 9）。",
     "默认参数写在形参里：def power(base, exp=2)，不传时用默认值。",
     'def power(base, exp=2):\n    return base ** exp\nprint(power(3))', ""),
    ("定义函数 factorial(n) 返回 n 的阶乘（n*(n-1)*...*1），打印 factorial(5)（应是 120）。",
     "用循环把 1 到 n 连乘（结合第 7 课）。",
     'def factorial(n):\n    result = 1\n    i = 1\n    while i <= n:\n        result *= i\n        i += 1\n    return result\nprint(factorial(5))', ""),
])

# ================= 第14课 函数的各类参数与函数嵌套 =================
ch("函数的各类参数与函数嵌套", [
    ("定义函数 greet(name, greeting='你好')，打印 问候语,名字；调用 greet('小明')（输出 你好,小明）。",
     "greeting 有默认值，不传时用 '你好'：print(f'{greeting},{name}')。",
     'def greet(name, greeting="你好"):\n    print(f"{greeting},{name}")\ngreet("小明")', ""),
    ("定义函数 sub(a, b) 返回 a-b，用关键字参数 sub(b=2, a=10) 调用并打印（应是 8）。",
     "关键字参数可以不按顺序传：sub(b=2, a=10) 等于 a=10, b=2。",
     'def sub(a, b):\n    return a - b\nprint(sub(b=2, a=10))', ""),
    ("定义函数 total(*nums) 用 *args 接收任意多个数字，返回它们的和；打印 total(1, 2, 3, 4)（应是 10）。",
     "*nums 会把所有传入的数字收进一个元组，return sum(nums)。",
     'def total(*nums):\n    return sum(nums)\nprint(total(1, 2, 3, 4))', ""),
    ("定义函数 info(**kw) 用 **kwargs 接收，逐行打印每个 键=值；调用 info(name='Tom', age=10)。",
     "**kw 收成字典，for k,v in kw.items(): print(f'{k}={v}')。",
     'def info(**kw):\n    for k, v in kw.items():\n        print(f"{k}={v}")\ninfo(name="Tom", age=10)', ""),
    ("定义外层函数 outer()，在它里面再定义 inner() 返回 5，outer 调用 inner 并返回结果；打印 outer()（应是 5）。",
     "函数里可以再定义函数；outer 里 return inner()。",
     'def outer():\n    def inner():\n        return 5\n    return inner()\nprint(outer())', ""),
    ("定义函数 minmax(lst) 返回列表的最小值和最大值（两个值），用拆包接收并打印 最小 和 最大（两行）。",
     "return min(lst), max(lst) 会返回一个元组；调用处用 a, b = minmax(...) 拆包。",
     'def minmax(lst):\n    return min(lst), max(lst)\nlo, hi = minmax([3, 1, 8, 5])\nprint(lo)\nprint(hi)', ""),
    ("定义函数 repeat(s, n=2) 返回把字符串 s 重复 n 次的结果，n 默认 2；打印 repeat('ab')（应是 abab）。",
     "return s * n，不传 n 时重复 2 次。",
     'def repeat(s, n=2):\n    return s * n\nprint(repeat("ab"))', ""),
    ("定义函数 mymax(*nums) 用 *args 接收任意多个数字，返回最大值；打印 mymax(3, 7, 2)（应是 7）。",
     "return max(nums)，nums 是收集起来的元组。",
     'def mymax(*nums):\n    return max(nums)\nprint(mymax(3, 7, 2))', ""),
    ("定义外层函数 add_maker(x)，里面定义 inner(y) 返回 x+y，add_maker 返回 inner(10) 的结果；打印 add_maker(5)（应是 15）。",
     "内层函数能用到外层的参数 x，return inner(10)。",
     'def add_maker(x):\n    def inner(y):\n        return x + y\n    return inner(10)\nprint(add_maker(5))', ""),
    ("定义函数 make(name, age=8) 返回一句 f-string：xxx今年x岁；打印 make('小红')（输出 小红今年8岁）。",
     "默认参数 age=8，return f'{name}今年{age}岁'。",
     'def make(name, age=8):\n    return f"{name}今年{age}岁"\nprint(make("小红"))', ""),
])

# ================= 第15课 作用域,匿名函数和匿名函数的参数 =================
ch("作用域,匿名函数和匿名函数的参数", [
    ("定义全局变量 g = 10，再定义函数 show() 读取并打印 g；调用 show()（输出 10）。",
     "函数内部可以直接读取全局变量。",
     'g = 10\ndef show():\n    print(g)\nshow()', ""),
    ("定义全局变量 count = 0，函数 add_one() 里用 global count 把它加 1；调用后打印 count（应是 1）。",
     "要在函数里修改全局变量，必须先写 global count。",
     'count = 0\ndef add_one():\n    global count\n    count += 1\nadd_one()\nprint(count)', ""),
    ("用 lambda 定义一个函数 f，功能是把参数乘以 2；打印 f(5)（应是 10）。",
     "lambda 写法：f = lambda x: x * 2。",
     'f = lambda x: x * 2\nprint(f(5))', ""),
    ("用 lambda 定义两个参数的加法函数 add；打印 add(3, 4)（应是 7）。",
     "add = lambda a, b: a + b。",
     'add = lambda a, b: a + b\nprint(add(3, 4))', ""),
    ("用 lambda 定义函数 f：参数是偶数返回 偶、否则返回 奇；打印 f(4)（应是 偶）。",
     "lambda 里可以用条件表达式：lambda x: '偶' if x%2==0 else '奇'（结合第 6 课）。",
     'f = lambda x: "偶" if x % 2 == 0 else "奇"\nprint(f(4))', ""),
    ("定义函数 make(), 里面有局部变量 msg='内部'，函数返回 msg；打印 make()（输出 内部）。",
     "局部变量只在函数内部有效，通过 return 把它带出来。",
     'def make():\n    msg = "内部"\n    return msg\nprint(make())', ""),
    ("用 lambda 定义 bigger，返回两个参数里较大的一个；打印 bigger(3, 9)（应是 9）。",
     "bigger = lambda a, b: a if a > b else b。",
     'bigger = lambda a, b: a if a > b else b\nprint(bigger(3, 9))', ""),
    ("用 lambda 定义一个无参数的函数 answer，直接返回 42；打印 answer()（应是 42）。",
     "无参数 lambda：answer = lambda: 42。",
     'answer = lambda: 42\nprint(answer())', ""),
    ("定义全局变量 base = 100，函数 plus(n) 返回 base + n（读取全局的 base）；打印 plus(5)（应是 105）。",
     "函数里可以读取全局 base，不修改就不需要 global。",
     'base = 100\ndef plus(n):\n    return base + n\nprint(plus(5))', ""),
    ("用 lambda 定义三个参数求和的函数 add3；打印 add3(1, 2, 3)（应是 6）。",
     "add3 = lambda a, b, c: a + b + c。",
     'add3 = lambda a, b, c: a + b + c\nprint(add3(1, 2, 3))', ""),
])

# ================= 第16课 lambda结合if判断 , 内置函数与拆包 =================
ch("lambda结合if判断 , 内置函数与拆包", [
    ("用 map 和 lambda 把列表 [1, 2, 3] 里每个数乘以 2，转成列表打印（[2, 4, 6]）。",
     "map(lambda x: x*2, 列表) 后用 list() 转成列表。",
     'nums = [1, 2, 3]\nprint(list(map(lambda x: x * 2, nums)))', ""),
    ("用 filter 和 lambda 从 [1, 2, 3, 4, 5, 6] 里筛出所有偶数，转成列表打印（[2, 4, 6]）。",
     "filter(lambda x: x%2==0, 列表) 保留条件为真的元素，再 list()。",
     'nums = [1, 2, 3, 4, 5, 6]\nprint(list(filter(lambda x: x % 2 == 0, nums)))', ""),
    ("用 sorted 和 lambda 把 ['bbb', 'a', 'cc'] 按字符串长度从短到长排序并打印（['a', 'cc', 'bbb']）。",
     "sorted(列表, key=lambda s: len(s))，key 决定按什么排序。",
     'words = ["bbb", "a", "cc"]\nprint(sorted(words, key=lambda s: len(s)))', ""),
    ("有列表 words = ['pear', 'watermelon', 'fig']，用 max 配合 key=len 找出最长的单词并打印（watermelon）。",
     "max(words, key=len) 按长度找最长的。",
     'words = ["pear", "watermelon", "fig"]\nprint(max(words, key=len))', ""),
    ("用 map 和带 if 的 lambda 把 [3, -1, 5, -2] 每个数变成 正 或 负，转成列表打印。",
     "lambda x: '正' if x>=0 else '负'，配合 map。",
     'nums = [3, -1, 5, -2]\nprint(list(map(lambda x: "正" if x >= 0 else "负", nums)))', ""),
    ("用 sum 配合 map 求 [1, 2, 3] 各元素平方的和并打印（1+4+9=14）。",
     "sum(map(lambda x: x*x, 列表))。",
     'nums = [1, 2, 3]\nprint(sum(map(lambda x: x * x, nums)))', ""),
    ("用 sorted 把 [3, 1, 2] 从大到小排序并打印（[3, 2, 1]）。",
     "sorted(列表, reverse=True) 降序排列。",
     'print(sorted([3, 1, 2], reverse=True))', ""),
    ("有列表 nums = [12, 3, 25, 7]，用 min 配合 key=lambda 找出个位数最小的数并打印（提示：key=lambda x: x%10，25 的个位是 5……最小个位是 12 的 2）。",
     "min(nums, key=lambda x: x % 10)，按个位数比较。",
     'nums = [12, 3, 25, 7]\nprint(min(nums, key=lambda x: x % 10))', ""),
    ("用 filter 和 lambda 从 [5, 12, 8, 3, 20] 里筛出大于 10 的数，转成列表打印（[12, 20]）。",
     "filter(lambda x: x > 10, 列表) 再 list()。",
     'nums = [5, 12, 8, 3, 20]\nprint(list(filter(lambda x: x > 10, nums)))', ""),
    ("用 map 和 lambda 把 [1, 2, 3] 每个数字转成字符串，转成列表打印（['1', '2', '3']）。",
     "lambda x: str(x)（结合第 11 课的类型转换）。",
     'nums = [1, 2, 3]\nprint(list(map(lambda x: str(x), nums)))', ""),
])

# ================= 第17课 内置函数与拆包 =================
ch("内置函数与拆包", [
    ("有 names = ['小明', '小红'] 和 scores = [90, 100]，用 zip 把它们配对，逐行打印成 名字:分数。",
     "for n, s in zip(names, scores): print(f'{n}:{s}')。",
     'names = ["小明", "小红"]\nscores = [90, 100]\nfor n, s in zip(names, scores):\n    print(f"{n}:{s}")', ""),
    ("有列表 fruits = ['苹果', '香蕉', '橘子']，用 enumerate 逐行打印成 序号:水果（序号从 0 开始）。",
     "for i, f in enumerate(fruits): print(f'{i}:{f}')。",
     'fruits = ["苹果", "香蕉", "橘子"]\nfor i, f in enumerate(fruits):\n    print(f"{i}:{f}")', ""),
    ("用星号拆包：a, *b = [1, 2, 3, 4]，打印 a（1）和 b（[2, 3, 4]）两行。",
     "a 拿第一个，*b 收集剩下所有元素组成列表。",
     'a, *b = [1, 2, 3, 4]\nprint(a)\nprint(b)', ""),
    ("有 a = [1, 2, 3] 和 b = [10, 20, 30]，用 zip 把对应位置相加，结果组成列表打印（[11, 22, 33]）。",
     "[x + y for x, y in zip(a, b)]（结合第 9 课列表推导式）。",
     'a = [1, 2, 3]\nb = [10, 20, 30]\nprint([x + y for x, y in zip(a, b)])', ""),
    ("有 items = ['a', 'b', 'c']，用 enumerate 从 1 开始编号，逐行打印 序号.元素（1.a、2.b、3.c）。",
     "enumerate(items, 1) 让序号从 1 开始。",
     'items = ["a", "b", "c"]\nfor i, x in enumerate(items, 1):\n    print(f"{i}.{x}")', ""),
    ("定义 a = 1、b = 2，用拆包一行交换它们，交换后打印 a 和 b（应是 2 和 1）。",
     "a, b = b, a 是最简洁的交换写法。",
     'a = 1\nb = 2\na, b = b, a\nprint(a)\nprint(b)', ""),
    ("定义函数 add3(x, y, z) 返回三数之和；有列表 nums = [1, 2, 3]，用星号 add3(*nums) 解包传参并打印（应是 6）。",
     "调用时用 *nums 把列表拆成三个参数传进去。",
     'def add3(x, y, z):\n    return x + y + z\nnums = [1, 2, 3]\nprint(add3(*nums))', ""),
    ("有 keys = ['a', 'b'] 和 vals = [1, 2]，用 zip 和 dict 组成字典并打印（{'a': 1, 'b': 2}）。",
     "dict(zip(keys, vals)) 把两个列表配对成字典（结合第 10 课）。",
     'keys = ["a", "b"]\nvals = [1, 2]\nprint(dict(zip(keys, vals)))', ""),
    ("有列表 nums = [4, 8, 15, 16, 23]，分四行打印它的和、最大值、最小值、元素个数。",
     "分别用 sum / max / min / len。",
     'nums = [4, 8, 15, 16, 23]\nprint(sum(nums))\nprint(max(nums))\nprint(min(nums))\nprint(len(nums))', ""),
    ("有 scores = [88, 95, 70]，用 enumerate 从 1 开始，逐行打印 第x名 y分（结合 f-string）。",
     "for i, s in enumerate(scores, 1): print(f'第{i}名 {s}分')。",
     'scores = [88, 95, 70]\nfor i, s in enumerate(scores, 1):\n    print(f"第{i}名 {s}分")', ""),
])

# ================= 第18课 异常模块与包 =================
ch("异常模块与包", [
    ("用 try/except 尝试计算 10 / 0，如果出错就打印 出错了。",
     "把可能出错的代码放进 try，用 except 捕获异常后打印提示。",
     'try:\n    print(10 / 0)\nexcept:\n    print("出错了")', ""),
    ("用 try/except 尝试把字符串 'abc' 转成整数，失败就打印 转换失败。",
     "int('abc') 会抛 ValueError，用 except 捕获后打印。",
     'try:\n    int("abc")\nexcept:\n    print("转换失败")', ""),
    ("导入 math 模块，用 math.sqrt 计算 16 的平方根并打印（应是 4.0）。",
     "import math 后用 math.sqrt(16)。",
     'import math\nprint(math.sqrt(16))', ""),
    ("导入 math 模块，用 f-string 打印 math.pi 保留 2 位小数（应是 3.14）。",
     "f'{math.pi:.2f}'（结合第 3 课）。",
     'import math\nprint(f"{math.pi:.2f}")', ""),
    ("用 try/except/else：尝试计算 8 / 2，没出错就在 else 里打印结果（应是 4.0）。",
     "没有异常时会执行 else 分支。",
     'try:\n    r = 8 / 2\nexcept:\n    print("出错")\nelse:\n    print(r)', ""),
    ("导入 math 模块，用 math.ceil（向上取整）和 math.floor（向下取整）分别处理 3.2，打印两行（4 和 3）。",
     "math.ceil(3.2) 向上取整，math.floor(3.2) 向下取整。",
     'import math\nprint(math.ceil(3.2))\nprint(math.floor(3.2))', ""),
    ("有列表 nums = [1, 2, 3]，用 try/except 访问不存在的 nums[10]，捕获错误后打印 越界了。",
     "下标越界会抛 IndexError，用 except 捕获。",
     'nums = [1, 2, 3]\ntry:\n    print(nums[10])\nexcept:\n    print("越界了")', ""),
    ("导入 math 模块，用 math.factorial 计算 5 的阶乘并打印（应是 120）。",
     "math.factorial(5) 直接算阶乘。",
     'import math\nprint(math.factorial(5))', ""),
    ("用 try/finally：在 try 里打印 尝试，无论如何都在 finally 里打印 结束（输出两行）。",
     "finally 里的代码一定会执行，常用来做收尾。",
     'try:\n    print("尝试")\nfinally:\n    print("结束")', ""),
    ("导入 math 模块，用 math.pow 计算 2 的 3 次方并打印（应是 8.0）。",
     "math.pow(2, 3) 返回小数结果 8.0。",
     'import math\nprint(math.pow(2, 3))', ""),
])

# ================= 第19课 闭包与装饰器A =================
ch("闭包与装饰器A", [
    ("定义外层函数 make_adder(n)，返回一个能把参数加 n 的内层函数；用它造出 add5，打印 add5(3)（应是 8）。",
     "内层函数记住了外层的 n，这就是闭包：def make_adder(n): def inner(x): return x+n; return inner。",
     'def make_adder(n):\n    def inner(x):\n        return x + n\n    return inner\nadd5 = make_adder(5)\nprint(add5(3))', ""),
    ("定义外层函数 make_multiplier(n)，返回把参数乘以 n 的内层函数；造出 double，打印 double(6)（应是 12）。",
     "和加法闭包类似，内层做乘法：return x * n。",
     'def make_multiplier(n):\n    def inner(x):\n        return x * n\n    return inner\ndouble = make_multiplier(2)\nprint(double(6))', ""),
    ("定义一个装饰器 shout，让被装饰的函数返回值后面加上感叹号；用它装饰返回 hello 的函数并打印（hello!）。",
     "装饰器里定义 wrapper，调用原函数拿到结果再加 '!' 返回。",
     'def shout(func):\n    def wrapper():\n        return func() + "!"\n    return wrapper\n@shout\ndef say():\n    return "hello"\nprint(say())', ""),
    ("定义装饰器 double_result，让被装饰函数的返回值翻倍；装饰一个返回 10 的函数并打印（应是 20）。",
     "wrapper 里 return func() * 2。",
     'def double_result(func):\n    def wrapper():\n        return func() * 2\n    return wrapper\n@double_result\ndef ten():\n    return 10\nprint(ten())', ""),
    ("定义外层 counter_maker()，内部用列表保存计数，返回一个每次调用就把计数加 1 并返回的函数；连续调用 3 次，打印第 3 次的结果（应是 3）。",
     "闭包保存状态：用 box=[0]，inner 里 box[0]+=1 再 return box[0]。",
     'def counter_maker():\n    box = [0]\n    def inner():\n        box[0] += 1\n        return box[0]\n    return inner\nc = counter_maker()\nc()\nc()\nprint(c())', ""),
    ("定义装饰器 add_prefix，让被装饰函数的返回值前面加上 结果: ；装饰一个返回 100 的函数并打印（结果:100）。",
     "wrapper 里 return '结果:' + str(func())（注意用 str 转换）。",
     'def add_prefix(func):\n    def wrapper():\n        return "结果:" + str(func())\n    return wrapper\n@add_prefix\ndef value():\n    return 100\nprint(value())', ""),
    ("定义外层 make_power(exp)，返回把参数做 exp 次方的内层函数；造出 cube（3 次方），打印 cube(2)（应是 8）。",
     "内层 return x ** exp。",
     'def make_power(exp):\n    def inner(x):\n        return x ** exp\n    return inner\ncube = make_power(3)\nprint(cube(2))', ""),
    ("定义装饰器 log，在调用被装饰函数前先打印 开始，再返回函数结果；装饰返回 done 的函数，先打印 开始 再打印 done。",
     "wrapper 里先 print('开始')，再 return func()。",
     'def log(func):\n    def wrapper():\n        print("开始")\n        return func()\n    return wrapper\n@log\ndef task():\n    return "done"\nprint(task())', ""),
    ("定义外层 greeting_maker(word)，返回一个接收名字、打印 word,名字 的内层函数；造出 hi = greeting_maker('嗨')，调用 hi('小明')（输出 嗨,小明）。",
     "内层用到外层的 word：def inner(name): print(f'{word},{name}')。",
     'def greeting_maker(word):\n    def inner(name):\n        print(f"{word},{name}")\n    return inner\nhi = greeting_maker("嗨")\nhi("小明")', ""),
    ("定义装饰器 square_it，让被装饰函数的返回值变成平方；装饰返回 5 的函数并打印（应是 25）。",
     "wrapper 里 r = func(); return r * r。",
     'def square_it(func):\n    def wrapper():\n        r = func()\n        return r * r\n    return wrapper\n@square_it\ndef five():\n    return 5\nprint(five())', ""),
])

# ================= 第20课 标准版装饰器与语法糖 =================
ch("标准版装饰器与语法糖", [
    ("写一个装饰器 plus_one，让被装饰函数的返回值加 1；用 @plus_one 语法糖装饰一个返回 9 的函数并打印（应是 10）。",
     "@plus_one 写在函数定义上方，等价于 f = plus_one(f)。",
     'def plus_one(func):\n    def wrapper():\n        return func() + 1\n    return wrapper\n@plus_one\ndef n():\n    return 9\nprint(n())', ""),
    ("写一个装饰器 keep_name，用 functools.wraps 保留原函数名；装饰名为 hello 的函数后，打印被装饰函数的 __name__（应是 hello）。",
     "from functools import wraps，在 wrapper 上加 @wraps(func) 就能保留原名。",
     'from functools import wraps\ndef keep_name(func):\n    @wraps(func)\n    def wrapper():\n        return func()\n    return wrapper\n@keep_name\ndef hello():\n    return "hi"\nprint(hello.__name__)', ""),
    ("写一个带参数的装饰器 repeat(n)，让被装饰函数执行后把返回字符串重复 n 次；用 @repeat(3) 装饰返回 ab 的函数并打印（ababab）。",
     "带参装饰器需要三层：repeat(n) 返回真正的装饰器，装饰器里的 wrapper 把结果重复 n 次。",
     'def repeat(n):\n    def deco(func):\n        def wrapper():\n            return func() * n\n        return wrapper\n    return deco\n@repeat(3)\ndef ab():\n    return "ab"\nprint(ab())', ""),
    ("写一个装饰器 announce，用 @语法糖 装饰函数，调用时先打印 调用函数，再返回结果；装饰返回 42 的函数，先打印 调用函数 再打印 42。",
     "wrapper 里先 print('调用函数')，再 return func()。",
     'def announce(func):\n    def wrapper():\n        print("调用函数")\n        return func()\n    return wrapper\n@announce\ndef get():\n    return 42\nprint(get())', ""),
    ("用 functools.reduce 计算列表 [1, 2, 3, 4] 所有元素的乘积并打印（应是 24）。",
     "from functools import reduce，reduce(lambda a, b: a*b, 列表)。",
     'from functools import reduce\nprint(reduce(lambda a, b: a * b, [1, 2, 3, 4]))', ""),
    ("用 functools.reduce 计算列表 [1, 2, 3, 4, 5] 的总和并打印（应是 15）。",
     "reduce(lambda a, b: a+b, 列表) 从左到右累加。",
     'from functools import reduce\nprint(reduce(lambda a, b: a + b, [1, 2, 3, 4, 5]))', ""),
    ("写两个装饰器 add_hi（结果前加 hi-）和 add_bye（结果后加 -bye），叠加装饰返回 ok 的函数（@add_hi 在上、@add_bye 在下），打印结果（hi-ok-bye）。",
     "叠加时靠近函数的先生效：先 add_bye 变成 ok-bye，再 add_hi 变成 hi-ok-bye。",
     'def add_hi(func):\n    def wrapper():\n        return "hi-" + func()\n    return wrapper\ndef add_bye(func):\n    def wrapper():\n        return func() + "-bye"\n    return wrapper\n@add_hi\n@add_bye\ndef msg():\n    return "ok"\nprint(msg())', ""),
    ("用 functools.lru_cache 装饰一个求斐波那契数的函数 fib，计算并打印 fib(10)（应是 55）。",
     "from functools import lru_cache，@lru_cache 能缓存结果加速递归。",
     'from functools import lru_cache\n@lru_cache\ndef fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\nprint(fib(10))', ""),
    ("写一个带参数的装饰器 times(n)，让被装饰函数的返回数字乘以 n；用 @times(5) 装饰返回 4 的函数并打印（应是 20）。",
     "三层结构：times(n) -> deco(func) -> wrapper 返回 func()*n。",
     'def times(n):\n    def deco(func):\n        def wrapper():\n            return func() * n\n        return wrapper\n    return deco\n@times(5)\ndef four():\n    return 4\nprint(four())', ""),
    ("综合：写一个装饰器 to_upper，把被装饰函数返回的字符串变成大写；用 @to_upper 装饰返回 hello 的函数并打印（HELLO）。",
     "wrapper 里 return func().upper()（结合第 8 课字符串方法）。",
     'def to_upper(func):\n    def wrapper():\n        return func().upper()\n    return wrapper\n@to_upper\ndef word():\n    return "hello"\nprint(word())', ""),
])


def build():
    questions = []
    fail = []
    empty = []
    for name, items in CHAPTERS:
        for content, expl, answer, sample_in in items:
            out, err, rc = run_python(answer, sample_in)
            if rc != 0:
                fail.append((name, content[:30], err[:120]))
            if not out.strip():
                empty.append((name, content[:30]))
            questions.append({
                "topic_name": name,
                "unit": None,
                "type": "code",
                "content": content,
                "options": None,
                "answer": answer,
                "explanation": expl,
                "difficulty": 1,
                "sample_input": sample_in,
                "expected_output": out,
            })
    return questions, fail, empty


def main():
    questions, fail, empty = build()
    total = len(questions)
    print(f"题目总数: {total}")
    # 每章计数
    from collections import OrderedDict
    cc = OrderedDict()
    for q in questions:
        cc[q["topic_name"]] = cc.get(q["topic_name"], 0) + 1
    for i, (k, v) in enumerate(cc.items(), 1):
        flag = "" if v == 10 else "  <-- 不是10题!"
        print(f"  {i:2d}. {k}  ({v}题){flag}")
    print(f"\n参考代码运行失败: {len(fail)}")
    for f in fail:
        print("  ❌", f)
    print(f"输出为空(无法判分): {len(empty)}")
    for e in empty:
        print("  ⚠️", e)
    if fail or empty:
        print("\n存在问题，未写出 JSON。请修正后重跑。")
        sys.exit(1)
    data = {"subject": SUBJECT, "questions": questions}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 全部 {total} 题参考代码跑通、输出非空，已写入 {OUT.name}")


if __name__ == "__main__":
    main()
