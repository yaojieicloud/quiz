# -*- coding: utf-8 -*-
"""上册阅读补缺：读取现有 JSON，精确统计每 (unit, topic) 篇数，生成缺额篇目补齐到 5。"""
import json
from collections import Counter

path = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_upper.json"
Q = json.load(open(path, encoding="utf-8"))
cnt = Counter((q["unit"], q["topic_name"]) for q in Q)
missing = [(u, t, 5 - c) for (u, t), c in cnt.items() if c < 5]
print("缺额:", missing)

def r(topic, unit, content, pairs, diff=1):
    items = [{"type": "choice", "q": q, "options": opts, "answer": str(ans), "explanation": expl}
             for q, opts, ans, expl in pairs]
    return {
        "type": "reading", "topic_name": topic, "unit": unit,
        "content": content, "options": None, "reading_items": items,
        "answer": ",".join(it["answer"] for it in items),
        "explanation": "", "difficulty": diff,
    }

U2 = "上册-Unit 2 Different families"
U3 = "上册-Unit 3 Amazing animals"
U4 = "上册-Unit 4 Plants around us"
U5 = "上册-Unit 5 The colourful world"
U6 = "上册-Unit 6 Useful numbers"
PD = "字母与语音"

extra = [
    r(PD, U2, "Letter Q q says /kw/. Queen starts with Q. Letter R r says /r/. Rose starts with R.", [
        ("What starts with Q?", ["Queen", "Rose", "Quilt", "Quick"], "0", "文中说 Queen starts with Q。"),
        ("What starts with R?", ["Queen", "Rose", "Rain", "Red"], "1", "文中说 Rose starts with R。"),
    ]),
    r(PD, U3, "Letter S s says /s/. Snake starts with S. Letter T t says /t/. Tiger starts with T.", [
        ("What starts with S?", ["Snake", "Tiger", "Sun", "Sit"], "0", "文中说 Snake starts with S。"),
        ("What starts with T?", ["Snake", "Tiger", "Top", "Ten"], "1", "文中说 Tiger starts with T。"),
    ]),
    r(PD, U4, "Letter U u says /ʌ/. Under starts with U. Letter V v says /v/. Vest starts with V.", [
        ("What starts with U?", ["Under", "Vest", "Up", "Us"], "0", "文中说 Under starts with U。"),
        ("What starts with V?", ["Under", "Vest", "Van", "Very"], "1", "文中说 Vest starts with V。"),
    ]),
    r(PD, U5, "Letter W w says /w/. Wind starts with W. Letter X x says /ks/. Fox starts with X.", [
        ("What starts with W?", ["Wind", "Fox", "Wet", "Win"], "0", "文中说 Wind starts with W。"),
        ("What starts with X?", ["Wind", "Fox", "Wax", "Well"], "1", "文中说 Fox starts with X。"),
    ]),
    r(PD, U6, "Number 7 looks like a walking stick. Number 8 looks like a pair of glasses. Numbers are everywhere.", [
        ("What does 7 look like?", ["A walking stick", "Glasses", "A ball", "A cup"], "0", "文中说 7 looks like a walking stick。"),
        ("What does 8 look like?", ["Glasses", "A stick", "A ring", "A hook"], "0", "文中说 8 looks like a pair of glasses。"),
    ]),
]
Q.extend(extra)
with open(path, "w", encoding="utf-8") as f:
    json.dump(Q, f, ensure_ascii=False, indent=2)
cnt2 = Counter((q["unit"], q["topic_name"]) for q in Q)
print(f"补缺 {len(extra)} 篇，合计 {len(Q)} 篇")
bad = [(k, c) for k, c in cnt2.items() if c != 5]
print("仍有缺额/超额:", bad if bad else "无 ✓ 全部 5 篇/课时")
