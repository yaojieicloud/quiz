# -*- coding: utf-8 -*-
import json

with open(r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3b_u7u8.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f'Loaded {len(items)} items')

# Fix: top-level answer should be sub-item indices (0,1,2 or 0,1)
for i, item in enumerate(items):
    n = len(item['reading_items'])
    new_answer = ','.join(str(j) for j in range(n))
    old_answer = item['answer']
    item['answer'] = new_answer
    if old_answer != new_answer:
        print(f'  Item {i}: "{old_answer}" -> "{new_answer}"')

with open(r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3b_u7u8.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f'\nFixed and saved {len(items)} items')
