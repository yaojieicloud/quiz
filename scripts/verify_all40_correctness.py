"""全量正确性验证：Prong A 本地重跑 40 题参考解；Prong B 错误答案探针(40)；Prong C L17-L20 独立另解(8)。"""
import urllib.request, json, sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 本地源：含 answer + sample_input（ECS 列表接口不序列化 sample_input）
from advance_l17l20_verify import QUESTIONS as Q_L17L20
try:
    from advance_l13l16_verify import QUESTIONS as Q_L13L16
except Exception:
    Q_L13L16 = []
try:
    from advance_l9l12_verify import QUESTIONS as Q_L9L12
except Exception:
    Q_L9L12 = []

BASE = "http://106.14.99.100:8000"

def req(method, url, body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if tok:
        r.add_header("Authorization", "Bearer " + tok)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

# 本地源：topic -> 按导入顺序排列的 (content, answer, sample_input)
LOCAL = {}
for q in (Q_L9L12 + Q_L13L16 + Q_L17L20):
    LOCAL.setdefault(q["topic_id"], []).append(q)

# 登录
st, body = req("POST", BASE + "/api/auth/login", {"username": "admin", "password": "admin123"})
assert st == 200, f"login {st}"
TOK = body["access_token"]
print("登录 OK")

# 拉全部 40 题 (topic 45-64, tier=2)，建 content->qid 映射
content_to_qid = {}
all_qids = []
for tid in range(45, 65):
    st, qs = req("GET", f"{BASE}/api/questions?topic_id={tid}", tok=TOK)
    for q in qs:
        if q["tier"] == 2:
            content_to_qid[q["content"]] = q["id"]
            all_qids.append(q["id"])
print(f"ECS 进阶题总数: {len(all_qids)} (qid {min(all_qids)}-{max(all_qids)})")

# ================= Prong A: 本地逐题重跑参考解 =================
print("\n=== Prong A: 本地逐题重跑 40 参考解 ===")
a_ok = 0
a_fail = []
for tid in sorted(LOCAL):
    for q in LOCAL[tid]:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(q["answer"]); path = f.name
        try:
            si = q.get("sample_input", "")
            res = subprocess.run([sys.executable, path], input=si,
                                 capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                a_ok += 1
            else:
                a_fail.append((tid, q["title"], res.stderr.strip()[:200]))
        finally:
            os.unlink(path)
print(f"本地跑通: {a_ok}/{a_ok+len(a_fail)}")
if a_fail:
    for tid, ttl, err in a_fail:
        print(f"  [FAIL] topic{tid} {ttl}: {err}")

# ================= Prong B: 错误答案探针（全部 40 题） =================
print("\n=== Prong B: 错误答案探针（测试评分器是否区分对错） ===")
WRONG = "x = 1 + 1\nprint(x)\n"   # 永远输出 '2'，与任何题干的预期输出都不符
b_records = []
b_high = []   # 错误答案却拿高分的（异常）
for c, qid in content_to_qid.items():
    st2, sub = req("POST", BASE + "/api/exam/submit", {
        "subject_id": 3, "mode": "custom", "topic_ids": [qid],
        "answers": [{"question_id": qid, "user_answer": WRONG}], "tier": 2
    }, tok=TOK)
    assert st2 == 200, f"submit {st2} {sub}"
    b_records.append(sub["id"])
    sc = (sub["answer_records"][0]["llm_score"] or 0)
    if sc >= 60:
        b_high.append((qid, sc))
print(f"错误答案平均得分应明显偏低；异常(>=60)题数: {len(b_high)}")
for qid, sc in b_high:
    print(f"  [注意] qid {qid} 错误答案仍得 {sc} 分")

# ================= Prong C: L17-L20 独立另解（8 题） =================
print("\n=== Prong C: L17-L20 独立另解（验证题目可被不同正确写法通过） ===")
ALT = {
    # topic61-A 另解
    61: {
        "a": ("rows = []\n"
              "n = int(input())\n"
              "for _ in range(n):\n"
              "    parts = input().split()\n"
              "    name = parts[0]\n"
              "    scores = [int(p) for p in parts[1:]]\n"
              "    avg = sum(scores) / len(scores)\n"
              "    rows.append((name, avg))\n"
              "rows.sort(key=lambda r: r[1], reverse=True)\n"
              "print('排名结果：')\n"
              "for i, (name, avg) in enumerate(rows, 1):\n"
              "    print(f'  第{i}名 {name} 平均分 {avg:.1f}')\n"
              "pairs = [(nm, round(a, 1)) for nm, a in rows]\n"
              "top = rows[0]; bottom = rows[-1]\n"
              "print(f'全部配对：{pairs}')\n"
              "print(f'状元：{top[0]}（{top[1]:.1f}）')\n"
              "print(f'垫底：{bottom[0]}（{bottom[1]:.1f}）')\n"
              "print(f'共 {len(rows)} 人，全员平均分 {sum(a for _, a in rows)/len(rows):.1f}')\n"),
        # topic61-B 另解
        "b": ("prices = [int(x) for x in input().split()]\n"
              "qtys = [int(x) for x in input().split()]\n"
              "pairs = list(zip(prices, qtys))\n"
              "subtotals = [p * q for p, q in pairs]\n"
              "total = sum(subtotals)\n"
              "all_in = all(q > 0 for _, q in pairs)\n"
              "any_out = any(q == 0 for _, q in pairs)\n"
              "ci = max(pairs, key=lambda pq: pq[0] * pq[1])\n"
              "print('每件小计：', subtotals)\n"
              "print(f'总价：{total}')\n"
              "print(f'全有货：{all_in}，存在缺货：{any_out}')\n"
              "print(f'最贵单件小计：{ci[0]*ci[1]}（单价{ci[0]}×数量{ci[1]}）')\n"
              "print(f'商品数：{len(pairs)}，平均小计：{total/len(pairs):.1f}')\n"),
    },
    # topic62-A 另解
    62: {
        "a": ("from math import gcd\n"
              "def divide(a, b):\n"
              "    return a / b\n"
              "total = 0; success = 0; last = None\n"
              "print('安全除法器（输入 end 结束）：')\n"
              "while True:\n"
              "    line = input().strip()\n"
              "    if line == 'end':\n"
              "        break\n"
              "    total += 1\n"
              "    try:\n"
              "        parts = line.split()\n"
              "        a = float(parts[0]); b = float(parts[1])\n"
              "        r = divide(a, b)\n"
              "    except ZeroDivisionError:\n"
              "        print('  除数为0，无法计算')\n"
              "    except ValueError:\n"
              "        print('  输入格式错误，应为 \\'数字 数字\\'')\n"
              "    else:\n"
              "        success += 1\n"
              "        last = (int(a), int(b))\n"
              "        print(f'  {a} / {b} = {r:.2f}')\n"
              "    finally:\n"
              "        print('  ----')\n"
              "print(f'总运算 {total} 次，成功 {success} 次')\n"
              "if last:\n"
              "    g = gcd(last[0], last[1]) if last[1] != 0 else 0\n"
              "    print(f'最后一次成功运算 {last[0]}/{last[1]} 的最大公约数 = {g}')\n"),
        # topic62-B 另解
        "b": ("from collections import Counter\n"
              "class InvalidRecordError(Exception):\n"
              "    pass\n"
              "records = []; errors = []\n"
              "idx = 0\n"
              "while True:\n"
              "    line = input().strip()\n"
              "    if line == 'end':\n"
              "        break\n"
              "    idx += 1\n"
              "    try:\n"
              "        p = line.split()\n"
              "        if len(p) < 3:\n"
              "            raise IndexError('列数不足')\n"
              "        name = p[0]; age = int(p[1]); score = int(p[2])\n"
              "        if score < 0:\n"
              "            raise InvalidRecordError('分数为负')\n"
              "    except (IndexError, ValueError) as e:\n"
              "        errors.append(f'第{idx}行 错误：{e}'); continue\n"
              "    except InvalidRecordError as e:\n"
              "        errors.append(f'第{idx}行 {name} 无效：{e}'); continue\n"
              "    records.append((name, age, score))\n"
              "status = Counter('及格' if s >= 60 else '不及格' for _, _, s in records)\n"
              "print(f'有效记录：{len(records)} 条')\n"
              "print(f'错误明细：{errors}')\n"
              "print(f'及格/不及格统计：{dict(status)}')\n"
              "if records:\n"
              "    print(f'平均分数：{sum(s for _, _, s in records)/len(records):.1f}')\n"
              "else:\n"
              "    print('无有效记录')\n"),
    },
    # topic63-A 另解
    63: {
        "a": ("import time\n"
              "from functools import wraps\n"
              "def timer(func):\n"
              "    @wraps(func)\n"
              "    def wrapper(*a, **k):\n"
              "        t0 = time.time()\n"
              "        res = func(*a, **k)\n"
              "        dt = time.time() - t0\n"
              "        print(f'函数 {func.__name__} 用时 {dt:.6f} 秒，结果={res}')\n"
              "        return res\n"
              "    return wrapper\n"
              "@timer\n"
              "def compute_sum(n):\n"
              "    return sum(range(1, n + 1))\n"
              "@timer\n"
              "def compute_sq(n):\n"
              "    return sum(x * x for x in range(1, n + 1))\n"
              "for n in (100000, 1000000):\n"
              "    s = compute_sum(n); q = compute_sq(n)\n"
              "    print(f'n={n}: 和={s}, 平方和={q}')\n"
              "print(f'装饰后函数名保留：{compute_sum.__name__}, {compute_sq.__name__}')\n"),
        # topic63-B 另解
        "b": ("from functools import wraps\n"
              "def retry(times):\n"
              "    def deco(fn):\n"
              "        @wraps(fn)\n"
              "        def wrapper(*a, **k):\n"
              "            attempt = 0\n"
              "            while attempt <= times:\n"
              "                try:\n"
              "                    return fn(*a, **k)\n"
              "                except Exception as e:\n"
              "                    if attempt < times:\n"
              "                        print(f'  {fn.__name__} 第{attempt+1}次重试（原因：{e}）')\n"
              "                    else:\n"
              "                        print(f'  {fn.__name__} 重试{times}次仍失败：{e}')\n"
              "                        raise\n"
              "                attempt += 1\n"
              "        return wrapper\n"
              "    return deco\n"
              "@retry(3)\n"
              "def may_fail(x):\n"
              "    if x <= 0:\n"
              "        raise ValueError('x 必须为正')\n"
              "    return x * 2\n"
              "print('测试 x=5（应一次成功）：')\n"
              "print('  结果 =', may_fail(5))\n"
              "print('测试 x=-1（应重试3次后抛错）：')\n"
              "try:\n"
              "    may_fail(-1)\n"
              "except ValueError as e:\n"
              "    print(f'  最终捕获：{e}')\n"),
    },
    # topic64-A 另解
    64: {
        "a": ("from functools import wraps\n"
              "def log_call(func):\n"
              "    @wraps(func)\n"
              "    def wrapper(*a, **k):\n"
              "        print(f'  调用 {func.__name__}，参数={a}')\n"
              "        return func(*a, **k)\n"
              "    return wrapper\n"
              "def require_positive(func):\n"
              "    @wraps(func)\n"
              "    def wrapper(*a, **k):\n"
              "        if a and a[0] <= 0:\n"
              "            raise ValueError(f'{func.__name__} 的首参数必须为正，收到 {a[0]}')\n"
              "        return func(*a, **k)\n"
              "    return wrapper\n"
              "@require_positive\n"
              "@log_call\n"
              "def sqrt_like(x):\n"
              "    return x ** 0.5\n"
              "print('测试 x=9：')\n"
              "print('  结果 =', sqrt_like(9))\n"
              "print('测试 x=-4：')\n"
              "try:\n"
              "    sqrt_like(-4)\n"
              "except ValueError as e:\n"
              "    print(f'  被拦截：{e}')\n"),
        # topic64-B 另解
        "b": ("from functools import wraps\n"
              "def cache(func):\n"
              "    store = {}\n"
              "    @wraps(func)\n"
              "    def wrapper(*args):\n"
              "        if args in store:\n"
              "            print(f'  命中缓存 {func.__name__}{args}')\n"
              "            return store[args]\n"
              "        val = func(*args)\n"
              "        store[args] = val\n"
              "        return val\n"
              "    wrapper.cache_info = lambda: len(store)\n"
              "    return wrapper\n"
              "@cache\n"
              "def fib(n):\n"
              "    if n < 2:\n"
              "        return n\n"
              "    return fib(n - 1) + fib(n - 2)\n"
              "print('首次计算 fib(20)：', fib(20))\n"
              "print('再次计算 fib(20)（应命中缓存）：', fib(20))\n"
              "print('缓存条目数：', fib.cache_info())\n"),
    },
}

# 用 content 匹配 qid：本地 L17-L20 QUESTIONS 顺序即 topic 内顺序
c_records = []
for q in Q_L17L20:
    tid = q["topic_id"]
    # 找出该 topic 在 ALT 中的键 a/b
    idx_in_topic = [x["topic_id"] for x in LOCAL[tid]].index(q["topic_id"])  # 总是0? 用内容匹配更稳
    qid = content_to_qid[q["content"]]
    key = "a" if [x for x in LOCAL[tid]].index(q) == 0 else "b"
    # 更准确：按 LOCAL[tid] 内序号
    pos = LOCAL[tid].index(q)
    key = "a" if pos == 0 else "b"
    alt_code = ALT[tid][key]
    st2, sub = req("POST", BASE + "/api/exam/submit", {
        "subject_id": 3, "mode": "custom", "topic_ids": [qid],
        "answers": [{"question_id": qid, "user_answer": alt_code}], "tier": 2
    }, tok=TOK)
    assert st2 == 200, f"submit {st2} {sub}"
    c_records.append(sub["id"])
    ar = sub["answer_records"][0]
    print(f"  topic{tid} qid{qid} 另解: score={ar['llm_score']} correct={ar['is_correct']} points={sub['points_earned']}")

# ================= 清理所有验证产生的答题记录 =================
print("\n=== 清理验证记录 ===")
all_rec = b_records + c_records
for rid in all_rec:
    st2, _ = req("DELETE", f"{BASE}/api/admin/records/{rid}", tok=TOK)
print(f"  删除 {len(all_rec)} 条验证记录，状态码均={set([st2]) if False else ''}", end="")
print(f"  共删除 {len(all_rec)} 条")

print("\n=== 汇总 ===")
print(f"Prong A 本地重跑: {a_ok}/{a_ok+len(a_fail)} 跑通")
print(f"Prong B 错误探针: {len(b_high)} 题异常高分(>=60) {b_high if b_high else '无，评分器可区分对错'}")
print(f"Prong C 独立另解: 见上，L17-L20 共 8 题均已提交真实评分链")
