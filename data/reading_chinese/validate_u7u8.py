# -*- coding: utf-8 -*-
import json
from collections import Counter

with open(r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3b_u7u8.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f'Total items: {len(items)}')
print(f'JSON valid: YES')

topic_counts = Counter()
unit_counts = Counter()
for item in items:
    topic_counts[item['topic_name']] += 1
    unit_counts[item['unit']] += 1

print('\n=== Per-topic counts ===')
all_ok = True
for topic, count in sorted(topic_counts.items()):
    status = 'OK' if count == 5 else 'ERROR'
    if count != 5:
        all_ok = False
    print(f'  {topic}: {count} [{status}]')

print('\n=== Per-unit counts ===')
for unit, count in sorted(unit_counts.items()):
    print(f'  {unit}: {count}')

errors = []
for i, item in enumerate(items):
    if item['type'] != 'reading':
        errors.append(f'Item {i}: type != reading')
    if not item.get('topic_name'):
        errors.append(f'Item {i}: missing topic_name')
    if not item.get('unit'):
        errors.append(f'Item {i}: missing unit')
    if not item.get('content'):
        errors.append(f'Item {i}: missing content')
    if item.get('options') is not None:
        errors.append(f'Item {i}: options should be null')
    ri = item.get('reading_items', [])
    if len(ri) < 2 or len(ri) > 3:
        errors.append(f'Item {i}: reading_items count = {len(ri)}, expected 2-3')
    for j, sub in enumerate(ri):
        if sub.get('type') != 'choice':
            errors.append(f'Item {i}, sub {j}: type != choice')
        if len(sub.get('options', [])) != 4:
            errors.append(f'Item {i}, sub {j}: options count != 4')
        ans = sub.get('answer', '')
        if ans not in ('0','1','2','3'):
            errors.append(f'Item {i}, sub {j}: invalid answer {ans}')
    # Top-level answer = comma-joined correct option indices from each sub-item
    expected_answer = ','.join(sub['answer'] for sub in ri)
    actual_answer = item.get('answer', '')
    if actual_answer != expected_answer:
        errors.append(f'Item {i}: answer="{actual_answer}", expected="{expected_answer}" (concat of sub-item answers)')
    if item.get('difficulty') not in (1, 2):
        errors.append(f'Item {i}: invalid difficulty {item.get("difficulty")}')
    content_len = len(item.get('content', ''))
    if content_len < 100 or content_len > 200:
        errors.append(f'Item {i}: content length = {content_len}, expected 100-200')

if errors:
    print(f'\n=== ERRORS ({len(errors)}) ===')
    for e in errors:
        print(f'  {e}')
else:
    print('\n=== All validation checks passed! ===')
