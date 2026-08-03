# -*- coding: utf-8 -*-
"""Python实操 每课新增10题（第11-20课），三年级趣味场景。
输出 python_coding_new_p2.json（expected_output 由实跑脚本补齐）。
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

# ===== 11 类型转换, int,float,str,bool等 =====
T = "类型转换, int,float,str,bool等"
q(T, "把字符串 '123' 用 int() 变成数字，再加 1 打印（应是 124）。",
  "print(int('123') + 1)",
  "int('123') 把字符串转成整数 123，加 1 得 124。")
q(T, "小明 9 岁，用 str() 把数字 9 变成字符串，和'我今年'、'岁'连起来打印（我今年9岁）。",
  "print('我今年' + str(9) + '岁')",
  "数字要和文字相加，得先用 str() 变成字符串。", 2)
q(T, "用 float() 把字符串 '3.5' 变成小数并打印。",
  "print(float('3.5'))",
  "float() 转成小数，打印 3.5。")
q(T, "用 int() 把小数 9.9 变成整数并打印（小数部分会被去掉）。",
  "print(int(9.9))",
  "int() 转整数会直接去掉小数部分，9.9 变 9。", 2)
q(T, "把 '2.5' 用 float() 转成小数，再加 0.5 打印（应是 3.0）。",
  "print(float('2.5') + 0.5)",
  "先转小数再相加，2.5+0.5=3.0。", 2)
q(T, "用 bool() 判断数字 1，打印结果（非0是 True）。",
  "print(bool(1))",
  "bool(1) 是 True，非零数字都为真。")
q(T, "用 bool() 判断数字 0，打印结果（0是 False）。",
  "print(bool(0))",
  "bool(0) 是 False，0 为假。")
q(T, "打印 '5' + '3' 的结果（注意它们是字符串，会连起来）。",
  "print('5' + '3')",
  "两个字符串相加是拼接，'5'+'3'='53'，不是 8。", 2)
q(T, "先把 '7' 用 int() 转成整数，再用 float() 转成小数打印（应是 7.0）。",
  "print(float(int('7')))",
  "先转整数 7，再转小数 7.0。", 2)
q(T, "用 str() 把 100 变成字符串并打印。",
  "print(str(100))",
  "str(100) 变成字符串 '100'，打印出来还是 100。")

# ===== 12 赋值,深浅拷贝,可变与不可变对象 =====
T = "赋值,深浅拷贝,可变与不可变对象"
q(T, "定义 a=[1,2,3]，让 b=a（直接赋值），给 b 追加 4，打印 a（a 也会变）。",
  "a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
  "b=a 让两个名字指向同一个列表，改 b 就是改 a。", 2)
q(T, "定义 a=[1,2,3]，用 a.copy() 复制出 b，给 b 追加 4，打印 a（a 不变）。",
  "a = [1, 2, 3]\nb = a.copy()\nb.append(4)\nprint(a)",
  "copy() 复制一份新列表，改 b 不影响 a。")
q(T, "定义 a=[1,2]，用 copy() 复制出 b，给 b 追加 3，打印 b。",
  "a = [1, 2]\nb = a.copy()\nb.append(3)\nprint(b)",
  "b 是复制出来的，追加 3 后 b 是 [1,2,3]。")
q(T, "定义字符串 s='hi'，让 s=s+'!'，打印 s（字符串能这样拼接出新值）。",
  "s = 'hi'\ns = s + '!'\nprint(s)",
  "字符串不可变，s+'!' 生成新字符串再赋给 s。", 2)
q(T, "定义 a=[5]，让 b=a，打印 b（和 a 一样）。",
  "a = [5]\nb = a\nprint(b)",
  "b=a 指向同一个列表，b 也是 [5]。")
q(T, "定义 a=[1,2,3]，用切片 a[:] 复制出 b，给 b 追加 4，打印 a（a 不变）。",
  "a = [1, 2, 3]\nb = a[:]\nb.append(4)\nprint(a)",
  "a[:] 也是复制一份，改 b 不影响 a。", 2)
q(T, "定义元组 t=(1,2)，打印 t（元组用圆括号）。",
  "t = (1, 2)\nprint(t)",
  "元组用圆括号定义，打印 (1, 2)。")
q(T, "定义 s='cat'，让 t=s，打印 t。",
  "s = 'cat'\nt = s\nprint(t)",
  "t=s 复制字符串的值，t 是 cat。")
q(T, "定义字典 a={'x':1}，用 copy() 复制出 b，给 b 加键 'y'，打印 a（a 不变）。",
  "a = {'x': 1}\nb = a.copy()\nb['y'] = 2\nprint(a)",
  "字典 copy() 复制一份，改 b 不影响 a。", 2)
q(T, "定义 n=10，让 m=n，然后 n=n+1，打印 m（m 还是 10）。",
  "n = 10\nm = n\nn = n + 1\nprint(m)",
  "数字不可变，m 记下的是当时的 10，n 自己加 1 不影响 m。", 2)

# ===== 13 函数,return返回值与形参实参 =====
T = "函数,return返回值与形参实参"
q(T, "定义函数 add(a,b) 返回两数之和，打印 add(3,4)（应是 7）。",
  "def add(a, b):\n    return a + b\nprint(add(3, 4))",
  "def 定义函数，return 返回结果，a、b 是形参。")
q(T, "定义函数 double(n) 返回 n 的 2 倍，打印 double(5)（应是 10）。",
  "def double(n):\n    return n * 2\nprint(double(5))",
  "double(5) 就是 5*2=10。")
q(T, "定义函数 greet(name) 返回 '你好,'加名字，打印 greet('小明')。",
  "def greet(name):\n    return '你好,' + name\nprint(greet('小明'))",
  "把参数 name 拼进问候语里。")
q(T, "定义函数 square(n) 返回 n 的平方，打印 square(6)（应是 36）。",
  "def square(n):\n    return n * n\nprint(square(6))",
  "6*6=36。")
q(T, "定义函数 say_hi() 直接打印 'hello'（没有 return），然后调用它。",
  "def say_hi():\n    print('hello')\nsay_hi()",
  "函数里直接 print，调用 say_hi() 就打印 hello。")
q(T, "定义函数 sub(a,b) 返回 a 减 b，打印 sub(10,3)（应是 7）。",
  "def sub(a, b):\n    return a - b\nprint(sub(10, 3))",
  "10-3=7，注意 a、b 顺序。")
q(T, "定义函数 is_adult(age) 返回 age 是否大于等于 18，打印 is_adult(9)（应是 False）。",
  "def is_adult(age):\n    return age >= 18\nprint(is_adult(9))",
  "9 不到 18，返回 False。", 2)
q(T, "定义函数 add3(a,b,c) 返回三个数的和，打印 add3(1,2,3)（应是 6）。",
  "def add3(a, b, c):\n    return a + b + c\nprint(add3(1, 2, 3))",
  "三个形参相加，1+2+3=6。")
q(T, "定义函数 repeat(s) 返回 s 重复 3 次，打印 repeat('哈')（哈哈哈）。",
  "def repeat(s):\n    return s * 3\nprint(repeat('哈'))",
  "字符串乘 3 重复三次。")
q(T, "定义函数 half(n) 返回 n 除以 2，打印 half(10)（应是 5.0）。",
  "def half(n):\n    return n / 2\nprint(half(10))",
  "10/2=5.0，除法结果是小数。", 2)

# ===== 14 函数的各类参数与函数嵌套 =====
T = "函数的各类参数与函数嵌套"
q(T, "定义 greet(name, greeting='你好')，打印 问候语,名字；调用 greet('小明')。",
  "def greet(name, greeting='你好'):\n    print(f'{greeting},{name}')\ngreet('小明')",
  "greeting 有默认值'你好'，不传就用默认。")
q(T, "定义 info(name, age)，用关键字参数调用 info(age=9, name='小红') 打印。",
  "def info(name, age):\n    print(name, age)\ninfo(age=9, name='小红')",
  "关键字参数可以打乱顺序，按名字对应。", 2)
q(T, "定义 add(a, b=10) 返回 a+b，打印 add(5)（b 用默认 10，应是 15）。",
  "def add(a, b=10):\n    return a + b\nprint(add(5))",
  "b 有默认值 10，add(5)=5+10=15。")
q(T, "定义 inner() 返回 3，outer() 返回 inner()*2，打印 outer()（应是 6）。",
  "def inner():\n    return 3\ndef outer():\n    return inner() * 2\nprint(outer())",
  "outer 里调用 inner，3*2=6，函数可以嵌套调用。", 2)
q(T, "定义 say_hi() 打印 'hi'，再定义 call(f) 调用传进来的函数，执行 call(say_hi)。",
  "def say_hi():\n    print('hi')\ndef call(f):\n    f()\ncall(say_hi)",
  "函数可以作为参数传给另一个函数。", 2)
q(T, "定义 power(base, exp=2) 返回 base 的 exp 次方，打印 power(3)（应是 9）。",
  "def power(base, exp=2):\n    return base ** exp\nprint(power(3))",
  "exp 默认 2，power(3)=3 的平方=9。", 2)
q(T, "定义 make(name='小明') 打印 name，调用 make()（用默认值）。",
  "def make(name='小明'):\n    print(name)\nmake()",
  "不传参数就用默认值'小明'。")
q(T, "定义 add(a,b) 返回和，打印 add(add(1,2),3)（先算里层，应是 6）。",
  "def add(a, b):\n    return a + b\nprint(add(add(1, 2), 3))",
  "里层 add(1,2)=3，再 add(3,3)=6。", 2)
q(T, "定义 show(x, y=1) 打印 x 和 y，调用 show(2)（y 用默认 1）。",
  "def show(x, y=1):\n    print(x, y)\nshow(2)",
  "只传 x=2，y 用默认 1，打印 2 1。")
q(T, "定义 mul(a,b) 返回乘积，再定义 sq(n) 用 mul(n,n) 算平方，打印 sq(4)（应是 16）。",
  "def mul(a, b):\n    return a * b\ndef sq(n):\n    return mul(n, n)\nprint(sq(4))",
  "sq 调用 mul 算平方，4*4=16。", 2)

# ===== 15 作用域,匿名函数和匿名函数的参数 =====
T = "作用域,匿名函数和匿名函数的参数"
q(T, "定义全局变量 g=10，定义函数 show() 打印 g，调用 show()（输出 10）。",
  "g = 10\ndef show():\n    print(g)\nshow()",
  "函数里能读取外面定义的全局变量 g。")
q(T, "定义函数 f()，在里面定义 x=5 并打印，调用 f()。",
  "def f():\n    x = 5\n    print(x)\nf()",
  "x 是函数里的局部变量，只在 f 内有效。")
q(T, "用 lambda 定义平方函数 sq，打印 sq(4)（应是 16）。",
  "sq = lambda x: x * x\nprint(sq(4))",
  "lambda x: x*x 是匿名函数，x 是它的参数。")
q(T, "用 lambda 定义加法 add(a,b)，打印 add(2,3)（应是 5）。",
  "add = lambda a, b: a + b\nprint(add(2, 3))",
  "lambda 可以有多个参数，用逗号分开。")
q(T, "用 lambda 定义无参函数 hello 返回 '你好'，打印 hello()。",
  "hello = lambda: '你好'\nprint(hello())",
  "lambda 后面不写参数就是无参函数。", 2)
q(T, "定义 n=100，函数 show() 打印 n，调用 show()。",
  "n = 100\ndef show():\n    print(n)\nshow()",
  "全局变量 n 在函数里能直接读。")
q(T, "用 lambda 定义 d 把数翻倍，打印 d(7)（应是 14）。",
  "d = lambda x: x * 2\nprint(d(7))",
  "7*2=14。")
q(T, "外面 x=1，函数 f() 里 x=2 并打印，调用 f()（打印的是函数里的 2）。",
  "x = 1\ndef f():\n    x = 2\n    print(x)\nf()",
  "函数里的 x 会盖住外面的，打印 2。", 2)
q(T, "用 lambda 定义 up 给字符串加 '!'，打印 up('哈')。",
  "up = lambda s: s + '!'\nprint(up('哈'))",
  "lambda 也能处理字符串，哈!。")
q(T, "定义 f() 返回 8，把结果存进 r，打印 r。",
  "def f():\n    return 8\nr = f()\nprint(r)",
  "函数返回值可以存进变量再用。")

# ===== 16 lambda结合if判断 , 内置函数与拆包 =====
T = "lambda结合if判断 , 内置函数与拆包"
q(T, "用 map 和 lambda 把 [1,2,3] 每个数乘 2，转成列表打印（[2,4,6]）。",
  "print(list(map(lambda x: x * 2, [1, 2, 3])))",
  "map 对每个元素执行 lambda，list 转回列表。")
q(T, "用 filter 和 lambda 从 [1,2,3,4] 挑出偶数，转成列表打印（[2,4]）。",
  "print(list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4])))",
  "filter 保留让 lambda 返回 True 的元素。", 2)
q(T, "用带 if 的 lambda：f=lambda x:'大' if x>10 else '小'，打印 f(5)（小）。",
  "f = lambda x: '大' if x > 10 else '小'\nprint(f(5))",
  "lambda 里也能写 if-else 三元表达式。", 2)
q(T, "用带 if 的 lambda：f=lambda x:'大' if x>10 else '小'，打印 f(20)（大）。",
  "f = lambda x: '大' if x > 10 else '小'\nprint(f(20))",
  "20>10，返回'大'。", 2)
q(T, "把列表 [1,2] 拆包给 a、b，打印 a 和 b。",
  "a, b = [1, 2]\nprint(a, b)",
  "拆包把列表元素分给多个变量。")
q(T, "用 first,*rest=[1,2,3] 拆包，打印 first 和 rest。",
  "first, *rest = [1, 2, 3]\nprint(first, rest)",
  "*rest 收集剩下的元素成列表，first 是 1。", 2)
q(T, "用 sorted 给 [3,1,2] 排序并打印（[1,2,3]）。",
  "print(sorted([3, 1, 2]))",
  "sorted 返回排好序的新列表。")
q(T, "用 map 和 lambda 给 [10,20] 每个数加 1，转列表打印（[11,21]）。",
  "print(list(map(lambda x: x + 1, [10, 20])))",
  "map 逐个加 1。")
q(T, "用 filter 和 lambda 从 [1,2,3] 挑出大于 2 的数，转列表打印（[3]）。",
  "print(list(filter(lambda x: x > 2, [1, 2, 3])))",
  "只保留大于 2 的 3。", 2)
q(T, "把元组 (5,6) 拆包给 x、y，打印 x+y（应是 11）。",
  "x, y = (5, 6)\nprint(x + y)",
  "拆包后相加，5+6=11。")

# ===== 17 内置函数与拆包 =====
T = "内置函数与拆包"
q(T, "用 len 打印列表 [1,2,3] 的长度（应是 3）。",
  "print(len([1, 2, 3]))",
  "len 返回元素个数。")
q(T, "用 max 打印 3、7、2 里最大的数（应是 7）。",
  "print(max(3, 7, 2))",
  "max 返回最大值 7。")
q(T, "用 min 打印 5、1、9 里最小的数（应是 1）。",
  "print(min(5, 1, 9))",
  "min 返回最小值 1。")
q(T, "用 sum 打印列表 [1,2,3,4] 的总和（应是 10）。",
  "print(sum([1, 2, 3, 4]))",
  "sum 把所有元素加起来。")
q(T, "用 abs 打印 -5 的绝对值（应是 5）。",
  "print(abs(-5))",
  "abs 去掉负号，返回绝对值。")
q(T, "有 names=['小明','小红'] 和 scores=[90,100]，用 zip 配对逐行打印 名字:分数。",
  "names = ['小明', '小红']\nscores = [90, 100]\nfor n, s in zip(names, scores):\n    print(f'{n}:{s}')",
  "zip 把两个列表配对，for 里拆包。", 2)
q(T, "用 sorted 给 [2,3,1] 从大到小排序打印（reverse=True）。",
  "print(sorted([2, 3, 1], reverse=True))",
  "reverse=True 降序，[3,2,1]。", 2)
q(T, "用 round 打印 3.6 四舍五入的结果（应是 4）。",
  "print(round(3.6))",
  "round 四舍五入，3.6 变 4。")
q(T, "用 enumerate 给 ['a','b'] 加上序号，逐行打印 序号 和 值。",
  "for i, v in enumerate(['a', 'b']):\n    print(i, v)",
  "enumerate 同时给出序号和元素。", 2)
q(T, "用 pow 打印 2 的 3 次方（应是 8）。",
  "print(pow(2, 3))",
  "pow(2,3) 等于 2**3=8。")

# ===== 18 异常模块与包 =====
T = "异常模块与包"
q(T, "用 try/except 尝试计算 10/0，出错就打印'出错了'。",
  "try:\n    print(10 / 0)\nexcept:\n    print('出错了')",
  "除以 0 会报错，except 接住并打印提示。")
q(T, "用 try/except 计算 10/2，没错就正常打印结果。",
  "try:\n    print(10 / 2)\nexcept:\n    print('错')",
  "10/2 没错，正常打印 5.0。")
q(T, "用 except ZeroDivisionError 专门接住除以 0 的错，打印'不能除以0'。",
  "try:\n    1 / 0\nexcept ZeroDivisionError:\n    print('不能除以0')",
  "指定错误类型更精确。", 2)
q(T, "try 里打印 1，再在 except 后面写 else 或继续打印'继续'（这里直接打印'继续'）。",
  "try:\n    x = 1\nexcept:\n    print('错')\nprint('继续')",
  "try 没错就跳过 except，继续往下打印。")
q(T, "导入 math 模块，用 math.floor 打印 3.7 向下取整（应是 3）。",
  "import math\nprint(math.floor(3.7))",
  "import math 后用 math.floor 向下取整。", 2)
q(T, "导入 math，用 math.ceil 打印 2.1 向上取整（应是 3）。",
  "import math\nprint(math.ceil(2.1))",
  "math.ceil 向上取整，2.1 变 3。", 2)
q(T, "用 try/except ValueError 尝试 int('abc')，出错打印'不是数字'。",
  "try:\n    int('abc')\nexcept ValueError:\n    print('不是数字')",
  "'abc' 转不了整数，抛 ValueError。", 2)
q(T, "用 try/finally：try 打印 1，finally 打印'结束'（finally 一定会执行）。",
  "try:\n    print(1)\nfinally:\n    print('结束')",
  "finally 里的代码无论是否出错都会执行。", 2)
q(T, "导入 math，用 math.sqrt 打印 16 的平方根（应是 4.0）。",
  "import math\nprint(math.sqrt(16))",
  "math.sqrt 算平方根，16 开方是 4.0。", 2)
q(T, "try 里打印 'ok'，except 里打印 'no'（没错就只打印 ok）。",
  "try:\n    print('ok')\nexcept:\n    print('no')",
  "没错不触发 except，只打印 ok。")

# ===== 19 闭包与装饰器A =====
T = "闭包与装饰器A"
q(T, "定义 make_adder(n) 返回能把参数加 n 的内层函数，造出 add5，打印 add5(3)（应是 8）。",
  "def make_adder(n):\n    def inner(x):\n        return x + n\n    return inner\nadd5 = make_adder(5)\nprint(add5(3))",
  "inner 记住外面的 n=5，add5(3)=3+5=8。", 2)
q(T, "定义 make_mul(n) 返回能把参数乘 n 的函数，造出 mul3，打印 mul3(4)（应是 12）。",
  "def make_mul(n):\n    def inner(x):\n        return x * n\n    return inner\nmul3 = make_mul(3)\nprint(mul3(4))",
  "mul3(4)=4*3=12，闭包记住 n=3。", 2)
q(T, "定义 outer()，里面 x=10，inner() 返回 x，outer 返回 inner；调用并打印结果（10）。",
  "def outer():\n    x = 10\n    def inner():\n        return x\n    return inner\nf = outer()\nprint(f())",
  "inner 是闭包，记住 outer 里的 x=10。", 2)
q(T, "make_greet(word) 返回 greet(name) 拼接问候语，造出 g，打印 g('小明')。",
  "def make_greet(word):\n    def greet(name):\n        return word + ',' + name\n    return greet\ng = make_greet('你好')\nprint(g('小明'))",
  "闭包记住 word='你好'，拼出 你好,小明。", 2)
q(T, "定义 outer()，里面 inner() 返回 5，outer 返回 inner()+1，打印 outer()（应是 6）。",
  "def outer():\n    def inner():\n        return 5\n    return inner() + 1\nprint(outer())",
  "outer 里调用 inner 得 5，再加 1。")
q(T, "make() 里 msg='秘密'，show() 打印 msg，make 返回 show；调用并执行（打印 秘密）。",
  "def make():\n    msg = '秘密'\n    def show():\n        print(msg)\n    return show\ns = make()\ns()",
  "show 是闭包，记住 msg。", 2)
q(T, "用 make_adder(2) 造出 add2，打印 add2(10)（应是 12）。",
  "def make_adder(n):\n    def inner(x):\n        return x + n\n    return inner\nadd2 = make_adder(2)\nprint(add2(10))",
  "10+2=12。", 2)
q(T, "outer() 里 inner() 返回 '内层'，outer 返回 inner；打印 outer()()（调用两次）。",
  "def outer():\n    def inner():\n        return '内层'\n    return inner\nprint(outer()())",
  "outer() 得到 inner，再 () 调用它。", 2)
q(T, "make_double() 返回把参数翻倍的函数 f，造出 d，打印 d(6)（应是 12）。",
  "def make_double():\n    def f(x):\n        return x * 2\n    return f\nd = make_double()\nprint(d(6))",
  "6*2=12。", 2)
q(T, "a() 里定义 b() 返回 3，a 返回 b；打印 a()()（调用两次）。",
  "def a():\n    def b():\n        return 3\n    return b\nprint(a()())",
  "a() 得 b，再 () 调用得 3。", 2)

# ===== 20 标准版装饰器与语法糖 =====
T = "标准版装饰器与语法糖"
q(T, "写装饰器 plus_one 让函数返回值加 1，用 @plus_one 装饰返回 9 的函数并打印（应是 10）。",
  "def plus_one(func):\n    def wrapper():\n        return func() + 1\n    return wrapper\n@plus_one\ndef nine():\n    return 9\nprint(nine())",
  "@plus_one 相当于 nine=plus_one(nine)，9+1=10。", 2)
q(T, "装饰器 add_mark 给返回值加 '!'，@add_mark 装饰返回'你好'的函数并打印。",
  "def add_mark(func):\n    def wrapper():\n        return func() + '!'\n    return wrapper\n@add_mark\ndef say():\n    return '你好'\nprint(say())",
  "装饰器给结果加感叹号，你好!。", 2)
q(T, "装饰器 double_it 让返回值翻倍，@double_it 装饰返回 5 的函数并打印（应是 10）。",
  "def double_it(func):\n    def wrapper():\n        return func() * 2\n    return wrapper\n@double_it\ndef five():\n    return 5\nprint(five())",
  "5*2=10。", 2)
q(T, "装饰器 log 先打印'开始'再调用原函数，@log 装饰返回'hi'的函数并打印。",
  "def log(func):\n    def wrapper():\n        print('开始')\n        return func()\n    return wrapper\n@log\ndef hi():\n    return 'hi'\nprint(hi())",
  "先打印开始，再返回 hi。", 2)
q(T, "装饰器 prefix 给返回值加 '★'，@prefix 装饰返回'小明'的函数并打印。",
  "def prefix(func):\n    def wrapper():\n        return '★' + func()\n    return wrapper\n@prefix\ndef name():\n    return '小明'\nprint(name())",
  "给名字加星星前缀，★小明。", 2)
q(T, "装饰器 sq 让返回值平方，@sq 装饰返回 3 的函数并打印（应是 9）。",
  "def sq(func):\n    def wrapper():\n        return func() ** 2\n    return wrapper\n@sq\ndef three():\n    return 3\nprint(three())",
  "3 的平方是 9。", 2)
q(T, "不用 @ 语法糖：定义 plus_one，再 nine=plus_one(nine) 手动装饰，打印 nine()（应是 10）。",
  "def plus_one(func):\n    def wrapper():\n        return func() + 1\n    return wrapper\ndef nine():\n    return 9\nnine = plus_one(nine)\nprint(nine())",
  "@ 语法糖本质就是 nine=plus_one(nine)。", 2)
q(T, "装饰器 neg 让返回值取相反数，@neg 装饰返回 5 的函数并打印（应是 -5）。",
  "def neg(func):\n    def wrapper():\n        return -func()\n    return wrapper\n@neg\ndef five():\n    return 5\nprint(five())",
  "取相反数，5 变 -5。", 2)
q(T, "装饰器 suf 给返回值加句号'。'，@suf 装饰返回'我学会了装饰器'的函数并打印。",
  "def suf(func):\n    def wrapper():\n        return func() + '。'\n    return wrapper\n@suf\ndef sentence():\n    return '我学会了装饰器'\nprint(sentence())",
  "给句子加句号。", 2)
q(T, "装饰器 up 让返回值变大写，@up 装饰返回'abc'的函数并打印（ABC）。",
  "def up(func):\n    def wrapper():\n        return func().upper()\n    return wrapper\n@up\ndef word():\n    return 'abc'\nprint(word())",
  ".upper() 变大写，abc→ABC。", 2)

with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\python_coding_new_p2.json", "w", encoding="utf-8") as f:
    json.dump(Q, f, ensure_ascii=False, indent=2)
from collections import Counter
print(f"第11-20课共 {len(Q)} 题")
print("分布:", dict(Counter(q['topic_name'] for q in Q)))
