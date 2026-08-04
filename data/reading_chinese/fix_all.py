import json

with open(r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3a_u5u6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Entry 33: 205 chars, need to cut 5
data[33]['content'] = (
    "香港有一条有名的街叫女人街，它不卖女人用的东西，而是因为早期很多女摊贩在这里做生意才得名。现在街上有许多摊位，东西五花八门。\n"
    "有卖玩具的、卖衣服的、卖电子产品的，还有各种纪念品。摊主们热情招呼客人，用粤语、普通话、英语跟游客交流。街上热热闹闹的，人挤人，肩碰肩。\n"
    "我最喜欢逛小吃摊位。鸡蛋仔的香味飘满整条街，鱼蛋在热油锅里滚来滚去，棉花糖软软甜甜的。逛累了坐在路边小板凳上歇歇，感受香港的热闹和活力。"
)

# Entry 34: 202 chars, need to cut 2
data[34]['content'] = (
    "香港的叮叮车是一种双层有轨电车，已经跑了一百多年。它叮叮叮地响着穿过大街小巷，是香港独有的风景。\n"
    "坐在叮叮车上层，可以看到街道两边的招牌和建筑。司机叔叔熟练地驾驶着，车不快但很稳当。沿途站牌上写着有趣的地名：铜锣湾、湾仔、金钟……\n"
    "老爷爷说，他小时候坐叮叮车上学，现在孙子也坐叮叮车上学。叮叮车陪伴了一代又一代香港人，是这座城市温暖的记忆。虽然有地铁和巴士，很多人仍喜欢坐叮叮车，因为那是一种情怀。"
)

# Verify
from collections import Counter
counts = Counter(item['topic_name'] for item in data)
print(f'Total entries: {len(data)}')
for k, v in counts.items():
    print(f'  {k}: {v}篇')

issues = []
for i, item in enumerate(data):
    if item['type'] != 'reading':
        issues.append(f'[{i}] type is not reading')
    if item['options'] is not None:
        issues.append(f'[{i}] options should be null')
    ri = item['reading_items']
    if len(ri) < 2 or len(ri) > 3:
        issues.append(f'[{i}] reading_items count {len(ri)} not in 2-3')
    ans_parts = item['answer'].split(',')
    if len(ans_parts) != len(ri):
        issues.append(f'[{i}] answer count {len(ans_parts)} != items count {len(ri)}')
    for j, sub in enumerate(ri):
        if sub['type'] != 'choice':
            issues.append(f'[{i}][{j}] sub type not choice')
        if len(sub['options']) != 4:
            issues.append(f'[{i}][{j}] options not 4')
        if sub['answer'] not in ('0','1','2','3'):
            issues.append(f'[{i}][{j}] answer {sub["answer"]} out of range')
        if ans_parts[j] != sub['answer']:
            issues.append(f'[{i}][{j}] answer mismatch: top={ans_parts[j]} sub={sub["answer"]}')
    content_len = len(item['content'])
    if content_len < 100:
        issues.append(f'[{i}] content too short: {content_len} chars')
    if content_len > 200:
        issues.append(f'[{i}] content too long: {content_len} chars')

if issues:
    print(f'\nISSUES ({len(issues)}):')
    for iss in issues:
        print(f'  {iss}')
else:
    print('\nAll checks passed!')

with open(r'C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3a_u5u6.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('File saved successfully.')
