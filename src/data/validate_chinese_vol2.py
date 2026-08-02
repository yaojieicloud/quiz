# -*- coding: utf-8 -*-
import json
from collections import Counter, defaultdict

path = r'C:\Users\Yaojie\Documents\GitHub\quiz\data\chinese_grade3_vol2.json'
data = json.load(open(path, encoding='utf-8'))
VALID_TYPES = {'choice', 'judge', 'fill', 'essay', 'match', 'sort', 'code'}
print(f'题目总数: {len(data)}, 题型: {dict(Counter(q.get("type") for q in data))}')

errors = []
for i, q in enumerate(data):
    for f in ['type', 'topic_name', 'unit', 'content', 'answer']:
        if f not in q or q[f] in (None, ''):
            errors.append(f'[{i}] 缺字段 {f}')
    t = q.get('type')
    if t not in VALID_TYPES:
        errors.append(f'[{i}] 非法题型 {t}')
    if not isinstance(q.get('answer'), str):
        errors.append(f'[{i}] answer 非字符串: {type(q.get("answer")).__name__}')
    if t in ('choice', 'judge'):
        opts = q.get('options')
        if not opts:
            errors.append(f'[{i}] {t} 缺 options')
        else:
            try:
                idx = int(q['answer'])
                if idx < 0 or idx >= len(opts):
                    errors.append(f'[{i}] {t} answer={idx} 越界(len={len(opts)})')
            except ValueError:
                errors.append(f'[{i}] {t} answer="{q["answer"]}" 非整数索引')
    if t == 'match':
        if not q.get('match_options'):
            errors.append(f'[{i}] match 缺 match_options')
        else:
            lo, ro = len(q.get('options', [])), len(q['match_options'])
            for p in str(q['answer']).split(','):
                if ':' not in p:
                    errors.append(f'[{i}] match answer 格式错: {p}'); continue
                l, r = p.split(':')
                if not (l.isdigit() and r.isdigit()):
                    errors.append(f'[{i}] match answer 非数字: {p}'); continue
                if int(l) >= lo or int(r) >= ro:
                    errors.append(f'[{i}] match 索引越界 {p} (左{lo}/右{ro})')
    if t == 'sort':
        opts = q.get('options')
        if not opts:
            errors.append(f'[{i}] sort 缺 options')
        else:
            idxs = [x for x in str(q['answer']).split(',') if x.strip() != '']
            for x in idxs:
                if not (x.isdigit() and int(x) < len(opts)):
                    errors.append(f'[{i}] sort 索引越界 {x} (len={len(opts)})')
            if sorted(int(x) for x in idxs) != list(range(len(opts))):
                errors.append(f'[{i}] sort answer 未覆盖全部项: {q["answer"]}')

if errors:
    print(f'X 发现 {len(errors)} 个问题:')
    for e in errors[:25]:
        print('  ' + e)
    if len(errors) > 25:
        print(f'  ... 还有 {len(errors)-25} 个')
else:
    print(f'OK 全部 {len(data)} 题校验通过（含连线/排序答案有效性）')

# 课时->单元映射检查：同一 topic_name 是否 unit 一致
print()
print('=== 课时(topic_name) -> 单元(unit) 映射 ===')
tu = defaultdict(set)
cnt = defaultdict(int)
for q in data:
    tu[q['topic_name']].add(q.get('unit'))
    cnt[q['topic_name']] += 1
conflict = False
for tname, units in tu.items():
    flag = '' if len(units) == 1 else '  <-- 单元不一致!'
    if len(units) != 1:
        conflict = True
    print(f'  课时「{tname}」({cnt[tname]}题) -> {sorted(units)}{flag}')
print('单元映射一致性:', 'OK' if not conflict else 'X 存在冲突')
