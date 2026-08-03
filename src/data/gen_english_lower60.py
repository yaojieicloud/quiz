# -*- coding: utf-8 -*-
"""生成三年级下册英语题：6 题型 x 10 题 = 60 题
参考线上题库风格，关联线上已有下册课时。
课时分布：Part A 词汇（词汇类：choice/judge/fill/match 为主）、
         Part B 句型（句型类：fill/judge）、Part C 对话（对话类：sort/essay）。
"""
import json

# 线上英语下册课时 topic_name（与线上完全一致，导入时按 name+unit 复用，不新建）
# 每个 Unit 下已有：Part A 词汇 / Part B 句型 / Part C 对话 / 拼读与语音
PART_A = "Part A 词汇"
PART_B = "Part B 句型"
PART_C = "Part C 对话"
UA = "下册-Unit 1 Meeting new people"
UB = "下册-Unit 2 Expressing yourself"
UC = "下册-Unit 3 Learning better"
UD = "下册-Unit 4 Healthy food"
UE = "下册-Unit 5 Old toys"
UF = "下册-Unit 6 Numbers in life"

questions = []

# ============ 选择题 choice x10（词汇为主，分布到各单元）============
choice_qs = [
    ("Meeting new people", UA, "'student' 是什么意思？", ["老师", "学生", "朋友", "同学"], "1", "student是学生，teacher才是老师。", 1),
    ("Meeting new people", UA, "'Where are you from?' 是在问什么？", ["你叫什么名字？", "你几岁了？", "你来自哪里？", "你好吗？"], "2", "Where are you from问来自哪里。", 1),
    ("Expressing yourself", UB, "'tall' 是什么意思？", ["矮的", "高的", "胖的", "瘦的"], "1", "tall是高的，short是矮的。", 1),
    ("Expressing yourself", UB, "'She has long hair.' 是什么意思？", ["她有短头发。", "她有长头发。", "他有长头发。", "她是长头发吗？"], "1", "She她，has有，long hair长头发。", 2),
    ("Learning better", UC, "'read' 是什么意思？", ["写", "读", "听", "说"], "1", "read是读，write是写。", 1),
    ("Learning better", UC, "'Let's study together.' 是什么意思？", ["让我们一起玩吧。", "让我们一起学习吧。", "让我们去吃饭吧。", "让我们回家吧。"], "1", "study学习，together一起。", 2),
    ("Healthy food", UD, "'apple' 是什么意思？", ["香蕉", "苹果", "橘子", "葡萄"], "1", "apple是苹果。", 1),
    ("Healthy food", UD, "'I'd like some milk.' 是什么意思？", ["我喜欢牛奶。", "我想要一些牛奶。", "牛奶在哪里？", "这是牛奶。"], "1", "I'd like是我想要。", 2),
    ("Old toys", UE, "'ball' 是什么意思？", ["球", "娃娃", "汽车", "风筝"], "0", "ball是球，doll是娃娃。", 1),
    ("Numbers in life", UF, "'seven' 是数字几？", ["6", "7", "8", "9"], "1", "seven是7，six是6，eight是8。", 1),
]
for tname, unit, content, opts, ans, expl, diff in choice_qs:
    questions.append({
        "type": "choice", "topic_name": tname, "unit": unit,
        "content": content, "options": opts, "answer": ans,
        "explanation": expl, "difficulty": diff,
    })

# ============ 判断题 judge x10 ============
judge_qs = [
    ("Meeting new people", UA, "'friend' 的意思是敌人。", "1", "friend是朋友，不是敌人。", 1),
    ("Meeting new people", UA, "'Nice to meet you.' 是初次见面时的问候语。", "0", "对的，Nice to meet you用于初次见面。", 1),
    ("Expressing yourself", UB, "'thin' 的意思是胖的。", "1", "thin是瘦的，fat才是胖的。", 1),
    ("Expressing yourself", UB, "'He is short.' 意思是他很高。", "1", "short是矮的，这句话意思是他很矮。", 1),
    ("Learning better", UC, "'listen' 的意思是听。", "0", "对的，listen是听。", 1),
    ("Learning better", UC, "'write' 和 'read' 意思相同。", "1", "write是写，read是读，意思不同。", 2),
    ("Healthy food", UD, "'banana' 的意思是香蕉。", "0", "对的，banana是香蕉。", 1),
    ("Healthy food", UD, "'healthy' 的意思是不健康的。", "1", "healthy是健康的，unhealthy才是不健康的。", 2),
    ("Old toys", UE, "'kite' 的意思是风筝。", "0", "对的，kite是风筝。", 1),
    ("Numbers in life", UF, "'ten' 的意思是九。", "1", "ten是十，nine才是九。", 1),
]
for tname, unit, content, ans, expl, diff in judge_qs:
    questions.append({
        "type": "judge", "topic_name": tname, "unit": unit,
        "content": content, "options": ["对", "错"], "answer": ans,
        "explanation": expl, "difficulty": diff,
    })

# ============ 填空题 fill x10 ============
fill_qs = [
    ("Meeting new people", UA, "'朋友'的英文是____。", "friend", "friend是朋友。", 1),
    ("Meeting new people", UA, "你来自哪里：Where are you ____?", "from", "Where are you from问来自哪里。", 2),
    ("Expressing yourself", UB, "'高的'的英文是____。", "tall", "tall是高的。", 1),
    ("Expressing yourself", UB, "她有一双大眼睛：She has big ____.", "eyes", "eyes是眼睛（复数）。", 2),
    ("Learning better", UC, "'学习'的英文是____。", "study", "study是学习。", 1),
    ("Learning better", UC, "让我们一起读书：Let's ____ books.", "read", "read是读书。", 2),
    ("Healthy food", UD, "'牛奶'的英文是____。", "milk", "milk是牛奶。", 1),
    ("Healthy food", UD, "我想要一些鸡蛋：I'd like some ____.", "eggs", "eggs是鸡蛋（复数）。", 2),
    ("Old toys", UE, "'玩具汽车'的英文是 toy ____.", "car", "car是汽车，toy car是玩具汽车。", 1),
    ("Numbers in life", UF, "'十二'的英文是____。", "twelve", "twelve是12。", 2),
]
for tname, unit, content, ans, expl, diff in fill_qs:
    questions.append({
        "type": "fill", "topic_name": tname, "unit": unit,
        "content": content, "answer": ans,
        "explanation": expl, "difficulty": diff,
        "blank_count": 1, "tolerance": 0.01,
    })

# ============ 应用题 essay x10（对话/写作）============
essay_qs = [
    ("Meeting new people", UA, "用英文写一段认识新朋友的对话，包括问候和询问来自哪里。（至少4句）", "参考：Hi! I'm Li Ming. What's your name? I'm Amy. Where are you from? I'm from the USA. Nice to meet you!", 1),
    ("Meeting new people", UA, "用英文介绍你的好朋友，说说他/她的名字和来自哪里。（3-5句话）", "参考：My friend is Zhang Peng. He is from Beijing. He is a student. We like to play together.", 1),
    ("Expressing yourself", UB, "用英文描述你自己的外貌，比如高矮、头发。（3-5句话）", "参考：I am tall. I have short hair. I have big eyes. I like myself.", 2),
    ("Expressing yourself", UB, "写一段你夸赞同学外貌的对话。（至少4句）", "参考：You are so tall! Yes, I'm tall. You have long hair. Thank you!", 2),
    ("Learning better", UC, "用英文写写你在学校里喜欢做什么学习活动。（3-5句话）", "参考：I like to study. I like to read books. I listen to the teacher. I learn English.", 1),
    ("Learning better", UC, "写一段和同学约定一起学习的对话。（至少4句）", "参考：Let's study together. OK! Let's read books. Good idea! Let's go!", 2),
    ("Healthy food", UD, "用英文写写你喜欢的健康食物，说说为什么喜欢。（3-5句话）", "参考：I like apples. They are sweet. I like milk too. Healthy food is good for us.", 1),
    ("Healthy food", UD, "写一段在食堂点餐的对话。（至少4句）", "参考：I'd like some rice, please. Here you are. Thank you! You're welcome.", 2),
    ("Old toys", UE, "用英文介绍你最喜欢的玩具。（3-5句话）", "参考：My favorite toy is a car. It's blue. It's so cool. I love my toy car.", 1),
    ("Numbers in life", UF, "用英文写写你家的电话号码或你的年龄，并拼出数字。（3-5句话）", "参考：I'm nine years old. My phone number is one-two-three-four. I can count numbers.", 2),
]
for tname, unit, content, expl, diff in essay_qs:
    questions.append({
        "type": "essay", "topic_name": tname, "unit": unit,
        "content": content, "answer": "待老师点评",
        "explanation": expl, "difficulty": diff,
    })

# ============ 连线题 match x10 ============
match_qs = [
    ("Meeting new people", UA, "将身份英文与中文连线。",
     ["boy", "friend", "teacher", "student"], ["学生", "男孩", "朋友", "老师"],
     "0:1,1:2,2:3,3:0", "boy男孩，friend朋友，teacher老师，student学生。", 1),
    ("Meeting new people", UA, "将问候语与中文连线。",
     ["Nice to meet you", "Where are you from?", "I'm from...", "Welcome"], ["欢迎", "认识你很高兴", "我来自...", "你来自哪里？"],
     "0:1,1:3,2:2,3:0", "Nice to meet you认识你很高兴，Where are you from你来自哪里，I'm from我来自，Welcome欢迎。", 2),
    ("Expressing yourself", UB, "将外貌英文与中文连线。",
     ["tall", "short", "long hair", "big eyes"], ["矮的", "大眼睛", "高的", "长头发"],
     "0:2,1:0,2:3,3:1", "tall高的，short矮的，long hair长头发，big eyes大眼睛。", 1),
    ("Expressing yourself", UB, "将身体部位英文与中文连线。",
     ["hair", "eye", "nose", "ear"], ["鼻子", "耳朵", "头发", "眼睛"],
     "0:2,1:3,2:0,3:1", "hair头发，eye眼睛，nose鼻子，ear耳朵。", 1),
    ("Learning better", UC, "将学习活动英文与中文连线。",
     ["read", "write", "listen", "study"], ["听", "写", "学习", "读"],
     "0:3,1:1,2:0,3:2", "read读，write写，listen听，study学习。", 1),
    ("Learning better", UC, "将学习用品英文与中文连线。",
     ["book", "pen", "bag", "ruler"], ["尺子", "书包", "书", "钢笔"],
     "0:2,1:3,2:1,3:0", "book书，pen钢笔，bag书包，ruler尺子。", 1),
    ("Healthy food", UD, "将食物英文与中文连线。",
     ["apple", "milk", "bread", "egg"], ["鸡蛋", "面包", "苹果", "牛奶"],
     "0:2,1:3,2:1,3:0", "apple苹果，milk牛奶，bread面包，egg鸡蛋。", 1),
    ("Healthy food", UD, "将水果英文与中文连线。",
     ["banana", "pear", "grape", "watermelon"], ["葡萄", "西瓜", "梨", "香蕉"],
     "0:3,1:2,2:0,3:1", "banana香蕉，pear梨，grape葡萄，watermelon西瓜。", 2),
    ("Old toys", UE, "将玩具英文与中文连线。",
     ["car", "ball", "kite", "doll"], ["娃娃", "风筝", "球", "汽车"],
     "0:3,1:2,2:1,3:0", "car汽车，ball球，kite风筝，doll娃娃。", 1),
    ("Numbers in life", UF, "将数字英文与中文连线。",
     ["seven", "eleven", "fifteen", "twenty"], ["二十", "十五", "十一", "七"],
     "0:3,1:2,2:1,3:0", "seven七，eleven十一，fifteen十五，twenty二十。", 2),
]
for tname, unit, content, left, right, ans, expl, diff in match_qs:
    questions.append({
        "type": "match", "topic_name": tname, "unit": unit,
        "content": content, "options": left, "match_options": right,
        "answer": ans, "explanation": expl, "difficulty": diff,
    })

# ============ 排序题 sort x10 ============
sort_qs = [
    ("Meeting new people", UA, "将下列对话按正确顺序排列。",
     ["Nice to meet you, Amy.", "Hi, Amy. Nice to meet you.", "Where are you from?", "I'm from the USA."],
     "1,0,2,3", "先打招呼Nice to meet you，对方回应，再问来自哪里，最后回答。", 2),
    ("Meeting new people", UA, "将下列对话按正确顺序排列。",
     ["Welcome to our school!", "Thank you!", "Let's be friends.", "Sure!"],
     "0,1,2,3", "先表示欢迎，再道谢，然后提议做朋友，最后答应。", 1),
    ("Expressing yourself", UB, "将下列单词排列成正确的句子。",
     ["long", "She", "has", "hair"],
     "1,2,0,3", "正确句子：She has long hair.（她有长头发。）", 2),
    ("Expressing yourself", UB, "将下列对话按正确顺序排列。",
     ["Look at me!", "Wow, you are so tall!", "Yes, I'm tall.", "You are tall."],
     "0,1,3,2", "先说看我，再夸高，然后确认。", 1),
    ("Learning better", UC, "将下列单词排列成正确的句子。",
     ["together", "study", "Let's"],
     "2,1,0", "正确句子：Let's study together.（让我们一起学习。）", 1),
    ("Learning better", UC, "将下列对话按正确顺序排列。",
     ["I like reading books.", "What do you like?", "I like study.", "Let's study together."],
     "1,0,2,3", "先问喜欢什么，再回答喜欢读书，然后说喜欢学习，最后提议一起学习。", 2),
    ("Healthy food", UD, "将下列对话按正确顺序排列。",
     ["I'd like some apples.", "Here you are.", "Thank you!", "You're welcome."],
     "0,1,2,3", "先说想要苹果，再递过去，再道谢，最后回应。", 1),
    ("Healthy food", UD, "将下列单词排列成正确的句子。",
     ["like", "I", "healthy", "food"],
     "1,0,3,2", "正确句子：I like healthy food.（我喜欢健康食物。）", 2),
    ("Old toys", UE, "将下列对话按正确顺序排列。",
     ["Look at my old toys.", "Wow! A blue car!", "Yes, I like it.", "It's so cool!"],
     "0,1,3,2", "先说看我的旧玩具，再夸车，然后确认喜欢。", 1),
    ("Numbers in life", UF, "将下列单词排列成正确的句子。",
     ["eleven", "I", "am"],
     "1,2,0", "正确句子：I am eleven.（我十一岁了。）", 1),
]
for tname, unit, content, opts, ans, expl, diff in sort_qs:
    questions.append({
        "type": "sort", "topic_name": tname, "unit": unit,
        "content": content, "options": opts,
        "answer": ans, "explanation": expl, "difficulty": diff,
    })

# ============ 题型 -> 线上课时名 映射（避免新建重复课时）============
# 词汇/判断/填空/连线 -> Part A 词汇；排序 -> Part B 句型；应用 -> Part C 对话
TYPE_TO_TOPIC = {
    "choice": PART_A,
    "judge": PART_A,
    "fill": PART_A,
    "match": PART_A,
    "sort": PART_B,
    "essay": PART_C,
}
for q in questions:
    q["topic_name"] = TYPE_TO_TOPIC[q["type"]]

# ============ 输出 ============
out_path = r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_grade3_lower_new60.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print(f"已生成 {len(questions)} 题 -> {out_path}")
from collections import Counter
print("题型分布:", dict(Counter(q["type"] for q in questions)))
print("课时分布:", dict(Counter(q["topic_name"] for q in questions)))
