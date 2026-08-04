import json
from collections import Counter

path = r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3a_u7u8.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Total items: %d' % len(data))
print()

counter = Counter(item['topic_name'] for item in data)
expected_topics = [
    '20 \u53e4\u8bd7\u4e09\u9996',
    '21 \u5927\u81ea\u7136\u7684\u58f0\u97f3',
    '22 \u8bfb\u4e0d\u5b8c\u7684\u5927\u4e66',
    '\u8bed\u6587\u56ed\u5730\u4e03',
    '23 \u53f8\u9a6c\u5149',
    '24 \u4e00\u5b9a\u8981\u4e89\u6c14',
    '25 \u624b\u672f\u53f0\u5c31\u662f\u9635\u5730',
    '26 \u4e00\u4e2a\u7c97\u74f7\u5927\u7897',
    '\u8bed\u6587\u56ed\u5730\u516b',
]
for topic in expected_topics:
    count = counter.get(topic, 0)
    status = 'OK' if count == 5 else 'FAIL'
    print('[%s] %s: %d' % (status, topic, count))

errors = []
for i, item in enumerate(data):
    if item.get('type') != 'reading':
        errors.append('Item %d: type != reading' % i)
    if not item.get('topic_name'):
        errors.append('Item %d: missing topic_name' % i)
    if not item.get('unit'):
        errors.append('Item %d: missing unit' % i)
    content = item.get('content', '')
    clen = len(content)
    if clen < 100 or clen > 200:
        errors.append('Item %d (%s): content length %d (should be 100-200)' % (i, item['topic_name'], clen))
    items = item.get('reading_items', [])
    if len(items) < 2 or len(items) > 3:
        errors.append('Item %d: reading_items count %d (should be 2-3)' % (i, len(items)))
    for j, ri in enumerate(items):
        if ri.get('type') != 'choice':
            errors.append('Item %d sub %d: type != choice' % (i, j))
        if len(ri.get('options', [])) != 4:
            errors.append('Item %d sub %d: options count != 4' % (i, j))
        answer = ri.get('answer', '')
        if answer not in ['0','1','2','3']:
            errors.append('Item %d sub %d: invalid answer %s' % (i, j, answer))
    sub_answers = ','.join(ri['answer'] for ri in items)
    if item.get('answer') != sub_answers:
        errors.append('Item %d: answer mismatch - expected "%s", got "%s"' % (i, sub_answers, item.get('answer')))

print()
if errors:
    print('Found %d issues:' % len(errors))
    for e in errors:
        print('  - ' + e)
else:
    print('All validation passed!')
