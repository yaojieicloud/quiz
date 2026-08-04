# -*- coding: utf-8 -*-
"""给 c3a_u3u4.json 补第 40 篇（10 小狗学叫 的第 5 篇）"""
import json
import io

P = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\reading_chinese\c3a_u3u4.json"

new_item = {
    "type": "reading",
    "topic_name": "10 小狗学叫",
    "unit": "上册-第三单元 预测策略",
    "content": "小鸭子想学捉虫子，可是它一低头就把水花溅得到处都是，虫子全吓跑了。\n它看见小翠鸟一伸脖子就能捉到虫子，羡慕极了：\"翠鸟姐姐，教教我吧！\"\n小翠鸟说：\"别着急，先盯住水面，看准了再伸脖子。\"\n小鸭子照着做，盯呀盯，眼睛都酸了。忽然，一条小虫浮上水面。它看准时机，伸脖子一啄——真的啄到了！\n\"我捉到啦！\"小鸭子举着小虫又蹦又跳。\n小翠鸟笑着说：\"看，只要耐心看准时机，你也能学会。\"\n从那以后，小鸭子天天练习，捉虫的本领越来越厉害了。",
    "options": None,
    "reading_items": [
        {"type": "choice", "q": "小鸭子一开始为什么捉不到虫子？", "options": ["一低头就溅起水花吓跑了虫子", "它不喜欢吃虫子", "虫子太少了", "妈妈不让它捉"], "answer": "0", "explanation": "文中说小鸭子一低头就把水花溅得到处都是，虫子全吓跑了。"},
        {"type": "choice", "q": "小翠鸟教小鸭子的方法是什么？", "options": ["盯住水面，看准了再伸脖子", "使劲拍翅膀", "把水搅浑", "用脚去踩"], "answer": "0", "explanation": "小翠鸟说先盯住水面，看准了再伸脖子。"}
    ],
    "answer": "0,0",
    "explanation": "",
    "difficulty": 1
}

data = json.loads(io.open(P, encoding="utf-8").read())
data.append(new_item)
io.open(P, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
from collections import Counter
c = Counter(x["topic_name"] for x in data)
print("total:", len(data))
for k, v in c.items():
    print(v, k)
