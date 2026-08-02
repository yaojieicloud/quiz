"""验证三个题库 JSON 文件的数据完整性"""
import json
from collections import Counter

files = [
    (r'C:\Users\Yaojie\Documents\GitHub\quiz\data\english_grade3_vol1.json', '英语三上'),
    (r'C:\Users\Yaojie\Documents\GitHub\quiz\data\english_grade3_vol2.json', '英语三下'),
    (r'C:\Users\Yaojie\Documents\GitHub\quiz\data\chinese_grade3_vol1.json', '语文三上'),
]

VALID_TYPES = {'choice','judge','fill','essay','match','sort','code'}
total_all = 0
all_ok = True

for path, label in files:
    print(f'===== {label} ({path.split(chr(92))[-1]}) =====')
    try:
        data = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        print(f'  X JSON 解析失败: {e}')
        all_ok = False
        continue
    if not isinstance(data, list):
        print(f'  X 顶层不是数组')
        all_ok = False
        continue
    print(f'  题目总数: {len(data)}')
    total_all += len(data)

    types = Counter(q.get('type') for q in data)
    print(f'  题型分布: {dict(types)}')

    units = Counter(q.get('unit') for q in data)
    topics = Counter(q.get('topic_name') for q in data)
    print(f'  单元: {dict(units)}')
    print(f'  章节数: {len(topics)} 个 -> {list(topics.keys())}')

    errors = []
    for i, q in enumerate(data):
        for f in ['type','topic_name','unit','content','answer']:
            if f not in q or q[f] in (None, ''):
                errors.append(f'  [{i}] 缺字段 {f}')
        t = q.get('type')
        if t not in VALID_TYPES:
            errors.append(f'  [{i}] 非法题型 {t}')
        if not isinstance(q.get('answer'), str):
            errors.append(f'  [{i}] answer 非字符串: {type(q.get("answer")).__name__}')
        if t in ('choice','judge') and not q.get('options'):
            errors.append(f'  [{i}] {t} 题缺 options')
        if t in ('choice','judge') and q.get('options'):
            try:
                idx = int(q['answer'])
                if idx < 0 or idx >= len(q['options']):
                    errors.append(f'  [{i}] {t} answer={idx} 越界(options长度{len(q["options"])})')
            except ValueError:
                errors.append(f'  [{i}] {t} answer="{q["answer"]}" 非整数索引')
        if t == 'match':
            if not q.get('match_options'):
                errors.append(f'  [{i}] match 题缺 match_options')
            else:
                pairs = str(q['answer']).split(',')
                for p in pairs:
                    if ':' not in p:
                        errors.append(f'  [{i}] match answer 格式错误: {p}')
        if t == 'sort' and not q.get('options'):
            errors.append(f'  [{i}] sort 题缺 options')

    if errors:
        all_ok = False
        print(f'  X 发现 {len(errors)} 个问题:')
        for e in errors[:20]:
            print(e)
        if len(errors) > 20:
            print(f'    ... 还有 {len(errors)-20} 个')
    else:
        print(f'  OK 全部 {len(data)} 题校验通过')
    print()

print('=' * 40)
print(f'三个文件合计: {total_all} 题')
print(f'总体结论: {"OK 全部通过，可导入" if all_ok else "X 存在问题需修复"}')
