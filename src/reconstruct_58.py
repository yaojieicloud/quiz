#!/usr/bin/env python3
# 重构那 58 道连线题为严格 1-to-1 双射：
# - 左右选项数相等
# - 左/右各自文本无重复
# - 每个左侧唯一对应一个右侧（双射）
# - 右侧顺序打乱（按 id 作随机种子，保证可复现且每次不同）
import sqlite3, json, random

DB = "quiz.db"

# id -> [(left, right), ...]  每个 (left,right) 即一条正确连线，右侧互异
PAIRS = {
2654: [("早上","绿色（花朵合拢）"),("中午","金色（花朵张开）")],
2935: [("裁缝","慢性子"),("顾客","急性子"),("老虎","胆小多疑")],
3743: [("a is a","True"),("a is b（值同对象异）","False")],
3746: [("x = 5; print(x)","5"),("x = '5'; print(type(x))","<class 'str'>"),("print(len('abc'))","3")],
3749: [("f'{2+3}'","5"),("'{}'.format(7)","7"),("'{name}'.format(name='Li')","Li"),("f'{3*4}'","12")],
3761: [("'a' in 'abc'","True"),("'d' in 'abc'","False")],
3771: [("print('5' + '3')","53"),("print(int('5') + 3)","8"),("print(float('2.5') * 2)","5.0")],
3772: [("7 % 2","1"),("7 // 2","3"),("-7 // 2","-4")],
3777: [("3 > 2","True"),("1 != 1","False")],
3780: [("bool(0)","False"),("bool('0')","True")],
3795: [("5 > 3 and 8 > 6","True"),("5 > 3 and 8 < 6","False")],
3796: [("x=10\nif x>=10:\n  if x==10:\n    print('A')","A"),("x=9\nif x>=10:\n  print('A')\nelse:\n  print('B')","B"),("x=10\nif x>5:\n  print('A')\n  print('B')","A 和 B")],
3801: [("for i in range(5):\n  if i==3: break\nprint(i)","3"),("for i in range(5):\n  if i==3: continue\n  print(i)","0 1 2 4"),("for i in range(3):\n  pass\nprint('done')","done")],
3809: [("'hello'.find('l')","2"),("'hello'.find('z')","-1"),("'hello'.replace('l','L')","heLLo")],
3811: [("isalpha()","是否全为字母"),("isdigit()","是否全为数字"),("isalnum()","是否字母或数字"),("isspace()","是否全为空白")],
3816: [("find","返回 -1"),("index","抛出 ValueError"),("get（字典）","返回 None 或默认值")],
3823: [("2 in [1,2,3]","True"),("5 in [1,2,3]","False")],
3827: [("t=(1,2,3); t[0]","1"),("t=(1,2); t+(3,)","(1,2,3)"),("len((1,2,3))","3")],
3830: [("tuple","不可变"),("list","可变")],
3836: [("str","可以"),("list","不可以（可变）")],
3839: [("bool(0)","False"),("bool('False')","True（非空字符串）"),("bool(-1)","True")],
3844: [("int('abc')","非数字字符串"),("int('3.5')","含小数点不能直接转int"),("int('')","空字符串")],
3846: [("round(3.7)","4"),("int(3.7)","3")],
3849: [("a=[1]; b=a; a is b","True"),("a=[1]; b=a.copy(); a is b","False")],
3852: [("a=[1,[2]]; b=a; b[1].append(3); a[1]","[2,3]"),("a={'x':[1]}; b=a.copy(); b['x'].append(2); a['x']","[1,2]"),("a=[1]; b=a*2; b[0]=9; print(a)","[1]")],
3853: [("b = a（列表）后修改 b","影响 a"),("b = a[:] 后修改 b","不影响 a")],
3858: [("def f(): return 1","1"),("def f(): return","None"),("def f(): return 1, 2","(1, 2) 元组")],
3870: [("def f(a, *b): return b\nf(1, 2, 3)","(2, 3)"),("def f(a, b=2, *c): return c\nf(1)","()"),("def f(*a, k): return k\nf(1, 2, k=3)","3")],
3882: [("def make():\n  x=10\n  def g(): return x\n  return g\nmake()()","10"),("def counter():\n  c=[0]\n  def inc(): c[0]+=1; return c[0]\n  return inc\nf=counter(); f(); f()","2"),("def outer(x):\n  def inner(y): return x+y\n  return inner\nouter(3)(4)","7")],
3890: [("any([0, '', 1])","True"),("all([1, 0, 3])","False")],
3895: [("map(...)","迭代器"),("sorted(...)","列表")],
3902: [("isinstance(1, int)","True"),("callable(5)","False")],
4009: [("'123'.isdigit()","True"),("'12.3'.isdigit()","False（含小数点）")],
4017: [("int(input()) 输入 abc","ValueError"),("input() 直接回车","返回空字符串")],
4027: [("if 语句后不缩进","IndentationError"),("else 对不齐 if","SyntaxError"),("缩进过深","逻辑可能出错")],
4030: [("(5 > 3) and (2 > 1)","True"),("(1 == 1) and (2 == 3)","False")],
4032: [("i=0\nwhile i<5: i+=1","5 次"),("i=0\nwhile i<10: i+=3","4 次")],
4041: [("'Python3'.isalpha()","False（含数字）"),("'Python3'.isalnum()","True"),("'python'.istitle()","False")],
4044: [("'test.py'.startswith('test')","True"),("'img.png'.endswith('.jpg')","False")],
4045: [("'a|b|c'.split('|')","['a','b','c']"),("'a,,b'.split(',')","['a','','b']"),("'abc'.split('')  → ?","ValueError")],
4048: [("s[0] = 'x'","报错 TypeError"),("s += 'x'","生成新字符串再绑定"),("s.upper()","返回新字符串")],
4050: [("[x*3 for x in range(3)]","[0,3,6]"),("[c.upper() for c in 'abc']","['A','B','C']"),("[len(w) for w in ['hi','hey']]","[2,3]")],
4056: [("append","None"),("pop","被弹出的元素"),("index","找到的索引")],
4058: [("(1,2,3)[1]","2"),("(1,2,3) + (4,)","(1,2,3,4)"),("(1,) * 3","(1,1,1)")],
4062: [("d['str']","合法"),("d[[1,2]] → ?","TypeError")],
4068: [("int('abc')","ValueError"),("int(None)","TypeError")],
4069: [("bool(0.0)","False"),("bool(2)","True")],
4075: [("a=[1]; b=a; b.append(2)","[1,2]"),("a=[1]; b=a[:]; b.append(2)","[1]")],
4079: [("b = a","别名"),("b = a.copy()","浅拷贝"),("b = copy.deepcopy(a)","完全独立副本")],
4080: [("a=[1,2]; b=a; b[0]=9; a[0]","9"),("a=[1,2]; b=a[:]; b[0]=9; a[0]","1"),("a=[1]; b=a+[2]; a","[1]")],
4083: [("f()（未定义）","NameError"),("def f(: pass","SyntaxError"),("f(1)（需要2个参数）","TypeError")],
4088: [("def f(a, b=1): return a+b\nf(2)","3"),("def f(a, b=1): return a+b\nf(2, 3)","5")],
4089: [("def f(a, *b, **c)","合法"),("def f(a=1, b)","非法"),("def f(*, k)","合法（k 必须关键字传）")],
4090: [("def f(x, l=[])","共享列表（陷阱）"),("def f(x, l=None)","安全写法"),("def f(x, d={})","共享字典（陷阱）")],
4097: [("修改外层嵌套变量","nonlocal"),("修改模块级变量","global")],
4106: [("all(x > 0 for x in [1,2,3])","True"),("any(x == 5 for x in [1,2])","False")],
4109: [("map 对象","惰性"),("列表推导式","立即求值")],
4114: [("isinstance([], list)","True"),("isinstance(True, int)","True（bool是int子类）"),("repr('a')","'a'")],
}

# 仅 3811 需改写题干（原为退化题，仅 1 个右侧选项）
CONTENT = {3811: "将字符串方法与它的判断功能连线。"}

def main():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; cur = con.cursor()
    assert len(PAIRS) == 58, f"应有58道，实际 {len(PAIRS)}"
    updated = 0
    for qid, pairs in PAIRS.items():
        L = [p[0] for p in pairs]
        R = [p[1] for p in pairs]
        # 校验：左侧唯一、右侧唯一
        assert len(L) == len(set(L)), f"Q{qid} 左侧重复"
        assert len(R) == len(set(R)), f"Q{qid} 右侧重复"
        # 打乱右侧（按 id 作种子，可复现）
        rnd = random.Random(qid)
        shuffled = R[:]
        rnd.shuffle(shuffled)
        # 构造答案：每个左侧对应其在 shuffled 中的索引
        ans = []
        for i, (left, right) in enumerate(pairs):
            j = shuffled.index(right)
            ans.append(f"{i}:{j}")
        answer = ",".join(ans)
        cur.execute(
            "UPDATE questions SET options=?, match_options=?, answer=? WHERE id=?",
            (json.dumps(L, ensure_ascii=False), json.dumps(shuffled, ensure_ascii=False), answer, qid)
        )
        if qid in CONTENT:
            cur.execute("UPDATE questions SET content=? WHERE id=?", (CONTENT[qid], qid))
        updated += 1
        print(f"Q{qid}: L={len(L)} R={len(R)} answer={answer}")
    con.commit()
    print(f"\n已更新 {updated} 道为 1-to-1 双射。")
    con.close()

if __name__ == "__main__":
    main()
