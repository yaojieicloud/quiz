"""L17-L20 (topic 61-64) 进阶题参考解本地验证：跑通每题 answer（含 sample_input）。"""
import subprocess, sys, os, tempfile

QUESTIONS = [
    # ===================== L17 / topic 61 内置函数与拆包 =====================
    {
        "topic_id": 61,
        "title": "L17-61-A 多列成绩单分析（zip/enumerate/*解包）",
        "content": (
            "多列成绩单分析。第一行输入 n，随后 n 行，每行『姓名 分数1 分数2 ...』"
            "（每个学生的分数个数可能不同）。请综合使用内置函数完成：\n"
            "- 用 * 解包把每行拆成『姓名』与『剩余分数列表 scores』（name, *scores = line.split()）；\n"
            "- 用 sum/len 计算该生平均分；\n"
            "- 用 zip 把『姓名, 平均分』配对；\n"
            "- 用 sorted + 匿名函数 key 按平均分降序排序；\n"
            "- 用 enumerate 输出名次（从 1 开始）；\n"
            "- 用 max/min 找出最高/最低平均分。\n"
            "输出：排序后的『第k名 姓名 平均分』、以及状元与垫底者姓名、全员平均分。"
        ),
        "answer": (
            "def analyze(lines):\n"
            "    rows = []\n"
            "    for line in lines:\n"
            "        line = line.strip()\n"
            "        if not line:\n"
            "            continue\n"
            "        name, *scores = line.split()\n"
            "        scores = [int(x) for x in scores]\n"
            "        avg = sum(scores) / len(scores) if scores else 0\n"
            "        rows.append((name, avg))\n"
            "    ranked = sorted(rows, key=lambda r: r[1], reverse=True)\n"
            "    return ranked\n\n"
            "n = int(input())\n"
            "lines = [input() for _ in range(n)]\n"
            "ranked = analyze(lines)\n\n"
            "print('排名结果：')\n"
            "for idx, (name, avg) in enumerate(ranked, start=1):\n"
            "    print(f'  第{idx}名 {name} 平均分 {avg:.1f}')\n\n"
            "pairs = list(zip([r[0] for r in ranked], [round(r[1], 1) for r in ranked]))\n"
            "top = max(ranked, key=lambda r: r[1])\n"
            "bottom = min(ranked, key=lambda r: r[1])\n"
            "print(f'全部配对：{pairs}')\n"
            "print(f'状元：{top[0]}（{top[1]:.1f}）')\n"
            "print(f'垫底：{bottom[0]}（{bottom[1]:.1f}）')\n"
            "print(f'共 {len(ranked)} 人，全员平均分 {sum(r[1] for r in ranked)/len(ranked):.1f}')\n"
        ),
        "explanation": (
            "思路：① 每行用 name, *scores = line.split() 把『姓名』与『可变分数』一次性解包，"
            "体现 * 解包在赋值中的用法；② sum(scores)/len(scores) 用内置聚合求平均；"
            "③ zip 把姓名与平均分配对成可打印结构；④ sorted(key=lambda r:r[1], reverse=True) "
            "按平均分降序；⑤ enumerate(ranked, start=1) 生成名次；⑥ max/min 用 key 找极值；"
            "综合展示内置函数 + 解包 + lambda 的组合威力。"
        ),
        "sample_input": "3\nAlice 88 92 75\nBob 60 55\nCindy 99 100 98 97\n",
    },
    {
        "topic_id": 61,
        "title": "L17-61-B 参数拆包聚合器（*args 调用 + map/any/all/max）",
        "content": (
            "参数拆包聚合器。第一行为若干用空格分隔的数字（代表若干商品的『单价』）；"
            "第二行为同样个数的数字（代表『数量』，可能含 0 表示缺货）。请：\n"
            "- 用 zip 把两行配成 (单价, 数量) 对；\n"
            "- 用 * 把配对列表解包传入函数 calc(*pairs)；\n"
            "- calc 内部用 map + lambda 计算每件商品小计，用 sum 求总价；\n"
            "- 用 all/any 判断『是否全部有货』与『是否存在缺货』；\n"
            "- 用 max + lambda key 找出最贵单件小计。\n"
            "输出：每件小计列表、总价、全有货/存在缺货标志、最贵单件小计、平均小计。"
        ),
        "answer": (
            "def calc(*pairs):\n"
            "    subtotals = list(map(lambda pq: pq[0] * pq[1], pairs))\n"
            "    total = sum(p * q for p, q in pairs)\n"
            "    return subtotals, total\n\n"
            "prices = [int(x) for x in input().split()]\n"
            "qtys = [int(x) for x in input().split()]\n"
            "pairs = list(zip(prices, qtys))\n\n"
            "subtotals, total = calc(*pairs)\n"
            "all_in_stock = all(q > 0 for _, q in pairs)\n"
            "any_out = any(q == 0 for _, q in pairs)\n"
            "costliest = max(pairs, key=lambda pq: pq[0] * pq[1])\n"
            "cheapest = min(pairs, key=lambda pq: pq[0] * pq[1])\n\n"
            "print('逐件明细：')\n"
            "for (p, q), st in zip(pairs, subtotals):\n"
            "    tag = '缺货' if q == 0 else '有货'\n"
            "    print(f'  单价{p} × 数量{q} = {st}（{tag}）')\n"
            "print('每件小计：', subtotals)\n"
            "print(f'总价：{total}')\n"
            "print(f'全有货：{all_in_stock}，存在缺货：{any_out}')\n"
            "print(f'最贵单件小计：{costliest[0]*costliest[1]}（单价{costliest[0]}×数量{costliest[1]}）')\n"
            "print(f'最便宜单件小计：{cheapest[0]*cheapest[1]}（单价{cheapest[0]}×数量{cheapest[1]}）')\n"
            "print(f'商品数：{len(pairs)}，平均小计：{total/len(pairs):.1f}')\n"
        ),
        "explanation": (
            "思路：① zip(prices, qtys) 把两个平行列表配成元组对；"
            "② calc(*pairs) 用 * 把列表解包为位置参数传入，体现调用端拆包；"
            "③ 函数内 map(lambda pq: pq[0]*pq[1], pairs) 批量算小计，sum 聚合；"
            "④ all(q>0 ...) 与 any(q==0 ...) 用生成器表达式做布尔聚合；"
            "⑤ max(pairs, key=lambda pq: pq[0]*pq[1]) 按小计找最贵；综合演示拆包调用与内置聚合函数。"
        ),
        "sample_input": "10 20 5 8\n3 1 0 2\n",
    },
    # ===================== L18 / topic 62 异常模块与包 =====================
    {
        "topic_id": 62,
        "title": "L18-62-A 安全除法器（多 except + else + finally）",
        "content": (
            "安全除法器。连续读入若干行『a b』直到输入 'end'。对每行：\n"
            "- 用 try 尝试把 a,b 转 float 并相除；\n"
            "- 捕获 ZeroDivisionError 输出『除数为0，无法计算』、捕获 ValueError 输出『输入格式错误』；\n"
            "- else 分支在成功时输出商（保留 2 位小数）；\n"
            "- finally 分支每次都输出『----』分隔。\n"
            "结束用 from math import gcd 计算最后一次成功除法的『整数分子分母』最大公约数"
            "（若全程无成功则跳过）。输出总运算次数与成功次数。"
        ),
        "answer": (
            "from math import gcd\n\n"
            "def divide(a, b):\n"
            "    return a / b\n\n"
            "total = 0\n"
            "success = 0\n"
            "last_pair = None\n"
            "print('安全除法器（输入 end 结束）：')\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == 'end':\n"
            "        break\n"
            "    total += 1\n"
            "    try:\n"
            "        a, b = line.split()\n"
            "        a, b = float(a), float(b)\n"
            "        result = divide(a, b)\n"
            "    except ZeroDivisionError:\n"
            "        print('  除数为0，无法计算')\n"
            "    except ValueError:\n"
            "        print('  输入格式错误，应为 \\'数字 数字\\'')\n"
            "    else:\n"
            "        success += 1\n"
            "        last_pair = (a, b)\n"
            "        print(f'  {a} / {b} = {result:.2f}')\n"
            "    finally:\n"
            "        print('  ----')\n\n"
            "print(f'总运算 {total} 次，成功 {success} 次')\n"
            "if last_pair:\n"
            "    na, nb = int(last_pair[0]), int(last_pair[1])\n"
            "    g = gcd(na, nb) if nb != 0 else 0\n"
            "    print(f'最后一次成功运算 {na}/{nb} 的最大公约数 = {g}')\n"
        ),
        "explanation": (
            "思路：① try 包裹可能出错的转换与除法；② 多个 except 分别捕获不同异常类型，"
            "针对性提示；③ else 在无异常时执行成功逻辑（计数+输出）；"
            "④ finally 无论成败都执行，保证分隔符打印；⑤ 循环结束用 math.gcd 对已成功的整数对"
            "做最大公约数；综合展示『异常处理四件套 + 模块导入』。"
        ),
        "sample_input": "10 2\n5 0\nabc\ndef 3\n10 4\nend\n",
    },
    {
        "topic_id": 62,
        "title": "L18-62-B 健壮解析器（自定义异常 + collections + 多重捕获）",
        "content": (
            "健壮数据解析。读入若干行『姓名 年龄 分数』直到 'end'。要求：\n"
            "- 用 try/except 捕获 IndexError（列数不足）、ValueError（数字转换失败），把『行号+原因』收集到 errors；\n"
            "- 定义自定义异常 class InvalidRecordError(Exception)，当分数为负时主动 raise 并在 except 中捕获；\n"
            "- 用 collections.Counter 统计及格/不及格人数；\n"
            "- finally 输出『解析结束』。\n"
            "输出：有效记录数、错误明细、及格/不及格统计、平均分数。"
        ),
        "answer": (
            "from collections import Counter\n\n"
            "class InvalidRecordError(Exception):\n"
            "    pass\n\n"
            "def parse(lines):\n"
            "    records = []\n"
            "    errors = []\n"
            "    for idx, line in enumerate(lines, start=1):\n"
            "        try:\n"
            "            parts = line.split()\n"
            "            if len(parts) < 3:\n"
            "                raise IndexError('列数不足')\n"
            "            name, age, score = parts[0], int(parts[1]), int(parts[2])\n"
            "            if score < 0:\n"
            "                raise InvalidRecordError('分数为负')\n"
            "        except (IndexError, ValueError) as e:\n"
            "            errors.append(f'第{idx}行 错误：{e}')\n"
            "            continue\n"
            "        except InvalidRecordError as e:\n"
            "            errors.append(f'第{idx}行 {name} 无效：{e}')\n"
            "            continue\n"
            "        records.append((name, age, score))\n"
            "    return records, errors\n\n"
            "raw = []\n"
            "while True:\n"
            "    line = input().strip()\n"
            "    if line == 'end':\n"
            "        break\n"
            "    raw.append(line)\n\n"
            "records, errors = parse(raw)\n"
            "status = Counter('及格' if s >= 60 else '不及格' for _, _, s in records)\n"
            "print(f'有效记录：{len(records)} 条')\n"
            "print(f'错误明细：{errors}')\n"
            "print(f'及格/不及格统计：{dict(status)}')\n"
            "if records:\n"
            "    print(f'平均分数：{sum(s for _, _, s in records)/len(records):.1f}')\n"
            "else:\n"
            "    print('无有效记录')\n"
        ),
        "explanation": (
            "思路：① 自定义异常 InvalidRecordError 表达『业务非法』语义；"
            "② 主动 raise 后用 except InvalidRecordError 精准捕获，与内置异常分组处理；"
            "③ (IndexError, ValueError) 用同一 except 合并常见解析错误；"
            "④ collections.Counter 一行统计及格/不及格分布；⑤ 解析逻辑封装成 parse 函数，主程序只管读取；"
            "综合展示异常处理 + 自定义异常 + 标准库模块。"
        ),
        "sample_input": "Alice 20 88\nBob 19\nCindy 21 -5\nDavid 22 45\nend\n",
    },
    # ===================== L19 / topic 63 闭包与装饰器A =====================
    {
        "topic_id": 63,
        "title": "L19-63-A 计时装饰器（@ + functools.wraps + *args）",
        "content": (
            "计时装饰器。请用闭包实现一个装饰器 `timer(func)`：\n"
            "- 用 functools.wraps 保留原函数元信息；\n"
            "- 在调用前后用 time 模块记录耗时，打印『函数名 结果=... 用时 X.XXXX 秒』并返回原函数结果；\n"
            "- 用 *args, **kwargs 透传任意参数。\n"
            "将 @timer 应用于 compute_sum(n) 与 compute_sq(n) 两个示例函数，主程序对 n=100000 与 "
            "n=1000000 循环演示，并验证装饰后函数名仍被保留（__name__）。"
        ),
        "answer": (
            "import time\n"
            "from functools import wraps\n\n"
            "def timer(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        start = time.perf_counter()\n"
            "        result = func(*args, **kwargs)\n"
            "        cost = time.perf_counter() - start\n"
            "        print(f'函数 {func.__name__} 用时 {cost:.6f} 秒，结果={result}')\n"
            "        return result\n"
            "    return wrapper\n\n"
            "@timer\n"
            "def compute_sum(n):\n"
            "    return sum(range(1, n + 1))\n\n"
            "@timer\n"
            "def compute_sq(n):\n"
            "    return sum(x * x for x in range(1, n + 1))\n\n"
            "for n in (100000, 1000000):\n"
            "    s = compute_sum(n)\n"
            "    q = compute_sq(n)\n"
            "    print(f'n={n}: 和={s}, 平方和={q}')\n"
            "print(f'装饰后函数名保留：{compute_sum.__name__}, {compute_sq.__name__}')\n"
        ),
        "explanation": (
            "思路：① timer 是一个闭包，内部 wrapper 捕获 func；@wraps(func) 把原函数的 "
            "__name__/__doc__ 复制过来，避免被装饰后元信息丢失；② wrapper(*args, **kwargs) "
            "透传任意参数，前后用 time.perf_counter() 计时；③ 用 @ 语法糖把装饰器应用到两个函数，"
            "无需手动赋值；④ 演示装饰器的『无侵入增强』——原函数代码不变却获得计时能力。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 63,
        "title": "L19-63-B 重试装饰器（参数化装饰器 + 闭包）",
        "content": (
            "重试装饰器。实现参数化装饰器 `retry(times)`：它返回一个装饰器，被装饰的函数若抛出异常，"
            "则最多重试 `times` 次，全部失败才把异常抛给调用者；每次重试打印『第k次重试（原因）』。\n"
            "将 @retry(3) 应用于 `may_fail(x)`：当 x<=0 时 raise ValueError，否则返回 x*2。"
            "主程序对 x=5（一次成功）与 x=-1（始终失败）分别调用，演示重试与最终失败处理。"
        ),
        "answer": (
            "from functools import wraps\n\n"
            "def retry(times):\n"
            "    def deco(func):\n"
            "        @wraps(func)\n"
            "        def wrapper(*args, **kwargs):\n"
            "            for attempt in range(times + 1):\n"
            "                try:\n"
            "                    return func(*args, **kwargs)\n"
            "                except Exception as e:\n"
            "                    if attempt < times:\n"
            "                        print(f'  {func.__name__} 第{attempt+1}次重试（原因：{e}）')\n"
            "                    else:\n"
            "                        print(f'  {func.__name__} 重试{times}次仍失败：{e}')\n"
            "                        raise\n"
            "        return wrapper\n"
            "    return deco\n\n"
            "@retry(3)\n"
            "def may_fail(x):\n"
            "    if x <= 0:\n"
            "        raise ValueError('x 必须为正')\n"
            "    return x * 2\n\n"
            "print('测试 x=5（应一次成功）：')\n"
            "print('  结果 =', may_fail(5))\n"
            "print('测试 x=-1（应重试3次后抛错）：')\n"
            "try:\n"
            "    may_fail(-1)\n"
            "except ValueError as e:\n"
            "    print(f'  最终捕获：{e}')\n"
        ),
        "explanation": (
            "思路：① retry(times) 是『装饰器工厂』：外层接收参数 times，返回真正装饰器 deco，"
            "再返回 wrapper——三层闭包；② wrapper 用 for 循环重试，range(times+1) 含首次共 times+1 次；"
            "③ except Exception 捕获后判断是否还能重试，不能则重新 raise；④ @retry(3) 语法糖演示参数化装饰器；"
            "综合展示『闭包 + 参数化装饰器 + 异常再抛出』。"
        ),
        "sample_input": "",
    },
    # ===================== L20 / topic 64 标准版装饰器与语法糖 =====================
    {
        "topic_id": 64,
        "title": "L20-64-A 装饰器栈（log + require_positive 叠加）",
        "content": (
            "装饰器栈演示。实现两个装饰器：\n"
            "- `log_call`：调用前打印『调用 函数名，参数=args』；\n"
            "- `require_positive`：检查第一个位置参数是否 >0，否则 raise ValueError。\n"
            "将两者**叠加**（@require_positive 在最上、@log_call 在下）应用到 `sqrt_like(x)`："
            "返回 x 的平方根（x**0.5）。主程序分别用 x=9（成功）与 x=-4（被拦截）调用，"
            "说明装饰器叠加的自下而上执行顺序与拦截效果。"
        ),
        "answer": (
            "from functools import wraps\n\n"
            "def log_call(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(f'  调用 {func.__name__}，参数={args}')\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n\n"
            "def require_positive(func):\n"
            "    @wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        if args and args[0] <= 0:\n"
            "            raise ValueError(f'{func.__name__} 的首参数必须为正，收到 {args[0]}')\n"
            "        return func(*args, **kwargs)\n"
            "    return wrapper\n\n"
            "@require_positive\n"
            "@log_call\n"
            "def sqrt_like(x):\n"
            "    return x ** 0.5\n\n"
            "print('测试 x=9：')\n"
            "print('  结果 =', sqrt_like(9))\n"
            "print('测试 x=-4：')\n"
            "try:\n"
            "    sqrt_like(-4)\n"
            "except ValueError as e:\n"
            "    print(f'  被拦截：{e}')\n"
        ),
        "explanation": (
            "思路：① 两个装饰器都用 @wraps 保留元信息；② @require_positive 在最外层、@log_call 在内层，"
            "按『自下而上包裹、自上而下执行』，调用时先经 require_positive 校验，非法直接抛错不会进入 log_call；"
            "③ sqrt_like = require_positive(log_call(sqrt_like))，演示装饰器本质是函数组合；"
            "④ 叠加顺序影响行为（校验优先于日志），这是语法糖下的关键细节。"
        ),
        "sample_input": "",
    },
    {
        "topic_id": 64,
        "title": "L20-64-B 手动缓存装饰器（@cache + 记忆化 + 语法糖）",
        "content": (
            "缓存装饰器。实现装饰器 `cache(func)`，用字典保存『参数->结果』：被装饰函数调用前先查缓存，"
            "命中则打印『命中缓存』并直接返回，否则计算并存入。\n"
            "将 @cache 应用于递归斐波那契 `fib(n)`（返回 fib(n)）以演示记忆化避免重复计算；"
            "主程序计算 fib(20) 并输出，再重复计算 fib(20) 演示缓存命中，最后打印缓存条目数。"
        ),
        "answer": (
            "from functools import wraps\n\n"
            "def cache(func):\n"
            "    store = {}\n"
            "    @wraps(func)\n"
            "    def wrapper(*args):\n"
            "        if args in store:\n"
            "            print(f'  命中缓存 {func.__name__}{args}')\n"
            "            return store[args]\n"
            "        result = func(*args)\n"
            "        store[args] = result\n"
            "        return result\n"
            "    wrapper.cache_info = lambda: len(store)\n"
            "    return wrapper\n\n"
            "@cache\n"
            "def fib(n):\n"
            "    if n < 2:\n"
            "        return n\n"
            "    return fib(n - 1) + fib(n - 2)\n\n"
            "print('首次计算 fib(20)：', fib(20))\n"
            "print('再次计算 fib(20)（应命中缓存）：', fib(20))\n"
            "print('缓存条目数：', fib.cache_info())\n"
        ),
        "explanation": (
            "思路：① cache 内部用闭包变量 store 字典缓存结果，args 作为键；"
            "② 命中时直接返回避免重复计算，否则算完存入——这就是记忆化（memoization）；"
            "③ 应用在递归 fib 上，把指数级重复调用降到线性；④ wrapper.cache_info 暴露缓存状态；"
            "⑤ @cache 语法糖让『递归函数 + 自动缓存』一行搞定，体现标准装饰器的工程价值。"
        ),
        "sample_input": "",
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
                nlines = len([x for x in q["answer"].split(chr(10)) if x.strip()])
                print(f"[OK]   {q['title']}  ({nlines} 行)")
                out = res.stdout.strip()
                print("       out:", out.replace("\n", " | ")[:200])
            else:
                print(f"[FAIL] {q['title']}")
                print("       STDERR:", res.stderr.strip()[:400])
        finally:
            os.unlink(path)
    print(f"\n本地验证通过 {ok}/{len(QUESTIONS)}")
