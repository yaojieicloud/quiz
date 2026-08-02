"""Generate English Grade 3 Vol 1 - Units 2-6, append to existing file"""
import json

# Load existing Unit 1
with open("C:/Users/Yaojie/Documents/GitHub/quiz/src/data/english_grade3_vol1.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def q(type, topic, unit, content, answer, explanation, difficulty=1, options=None, match_options=None, blank_count=1, blank_answers=None, tolerance=0.01):
    item = {"type": type, "topic_name": topic, "unit": unit, "content": content, "answer": str(answer), "explanation": explanation, "difficulty": difficulty}
    if options is not None: item["options"] = options
    if match_options is not None: item["match_options"] = match_options
    if type == "fill":
        item["blank_count"] = blank_count
        if blank_answers: item["blank_answers"] = blank_answers
        item["tolerance"] = tolerance
    questions.append(item)

# ============================================================
# Unit 2: Colours! (red, yellow, green, blue, white, black, orange, brown)
# ============================================================
U2 = "Unit 2"
T2 = "Colours!"

u2_choice = [
    ("'red' 是什么颜色？", ["蓝色", "红色", "绿色", "黄色"], "1", "red是红色。", 1),
    ("'blue' 是什么颜色？", ["红色", "绿色", "蓝色", "白色"], "2", "blue是蓝色。", 1),
    ("'green' 是什么颜色？", ["黄色", "绿色", "黑色", "橙色"], "1", "green是绿色。", 1),
    ("'yellow' 是什么颜色？", ["红色", "蓝色", "黄色", "绿色"], "2", "yellow是黄色。", 1),
    ("'white' 是什么颜色？", ["黑色", "白色", "棕色", "橙色"], "1", "white是白色。", 1),
    ("'black' 是什么颜色？", ["白色", "黑色", "灰色", "棕色"], "1", "black是黑色。", 1),
    ("'orange' 是什么颜色？", ["红色", "橙色", "黄色", "棕色"], "1", "orange是橙色。", 1),
    ("'brown' 是什么颜色？", ["橙色", "棕色", "黑色", "红色"], "1", "brown是棕色。", 1),
    ("天空是什么颜色？", ["red", "green", "blue", "yellow"], "2", "天空是蓝色的，blue。", 1),
    ("草地是什么颜色？", ["blue", "green", "red", "white"], "1", "草地是绿色的，green。", 1),
    ("太阳是什么颜色？", ["blue", "green", "yellow", "black"], "2", "太阳是黄色的，yellow。", 1),
    ("雪是什么颜色？", ["black", "white", "green", "red"], "1", "雪是白色的，white。", 1),
    ("'I see red.' 是什么意思？", ["我是红色的。", "我看到红色。", "我喜欢红色。", "红色在哪里？"], "1", "I see是我看到。", 1),
    ("'Show me green.' 是什么意思？", ["给我看看绿色。", "我是绿色。", "绿色在哪里？", "我喜欢绿色。"], "0", "Show me是给我看看。", 1),
    ("'The flower is red.' 是什么意思？", ["花是红色的。", "花是绿色的。", "红色的花在哪里？", "我喜欢花。"], "0", "flower是花，red是红色。", 1),
    ("'What colour is it?' 是在问什么？", ["它在哪里？", "它是什么颜色？", "它是什么？", "它是谁的？"], "1", "What colour问颜色。", 2),
    ("'It's blue and white.' 是什么意思？", ["它是蓝色的。", "它是蓝白相间的。", "它是白色的。", "它是蓝色的或白色的。"], "1", "and是和，blue and white是蓝白相间。", 2),
    ("'Colour the apple red.' 是什么意思？", ["把苹果涂成红色。", "苹果是红色的。", "红色的苹果在哪里？", "我喜欢红苹果。"], "0", "Colour作动词是涂色。", 2),
    ("'I like blue.' 是什么意思？", ["我是蓝色的。", "蓝色在哪里？", "我喜欢蓝色。", "这是蓝色的。"], "2", "I like是我喜欢。", 1),
    ("'The cat is black.' 是什么意思？", ["猫是白色的。", "猫是黑色的。", "黑色的猫在哪里？", "我喜欢猫。"], "1", "cat是猫，black是黑色。", 1),
]
for content, opts, ans, exp, diff in u2_choice:
    q("choice", T2, U2, content, ans, exp, diff, options=opts)

u2_judge = [
    ("'red' 的意思是蓝色。", "1", "red是红色，blue才是蓝色。", 1),
    ("'green' 的意思是绿色。", "0", "对的，green就是绿色。", 1),
    ("'yellow' 的意思是黄色。", "0", "对的，yellow就是黄色。", 1),
    ("'white' 的意思是黑色。", "1", "white是白色，black才是黑色。", 1),
    ("'black' 的意思是白色。", "1", "black是黑色，white才是白色。", 1),
    ("'orange' 的意思是橙色。", "0", "对的，orange就是橙色。", 1),
    ("'brown' 的意思是棕色。", "0", "对的，brown就是棕色。", 1),
    ("'blue' 的意思是红色。", "1", "blue是蓝色，red才是红色。", 1),
    ("天空通常是green色的。", "1", "天空是blue蓝色的，不是green绿色。", 1),
    ("'I see red' 意思是我看到红色。", "0", "对的，I see是我看到。", 1),
    ("'Show me' 是给我看看的意思。", "0", "对的，Show me就是给我看看。", 1),
    ("'colour' 只能做名词，不能做动词。", "1", "colour也可以做动词，表示涂色。", 2),
    ("'The sky is blue.' 意思是天空是蓝色的。", "0", "对的，sky天空，blue蓝色。", 1),
    ("'What colour' 是问什么东西。", "1", "What colour是问什么颜色，What才是问什么。", 1),
    ("'I like green.' 意思是我喜欢绿色。", "0", "对的，I like是我喜欢。", 1),
    ("'and' 是但是的意思。", "1", "and是和、并且，but才是但是。", 2),
    ("'The grass is green.' 意思是草是绿色的。", "0", "对的，grass草，green绿色。", 1),
    ("'orange' 只能表示颜色，不能表示水果。", "1", "orange既可以表示橙色，也可以表示橙子。", 2),
    ("'It's red and yellow.' 意思是它是红黄相间的。", "0", "对的，and表示和、并且。", 1),
    ("'Colour it blue.' 意思是把它涂成蓝色。", "0", "对的，Colour作动词是涂色。", 2),
]
for content, ans, exp, diff in u2_judge:
    q("judge", T2, U2, content, ans, exp, diff, options=["对", "错"])

u2_fill = [
    ("'红色'的英文是____。", "red", "red是红色。", 1),
    ("'蓝色'的英文是____。", "blue", "blue是蓝色。", 1),
    ("'绿色'的英文是____。", "green", "green是绿色。", 1),
    ("'黄色'的英文是____。", "yellow", "yellow是黄色。", 1),
    ("'白色'的英文是____。", "white", "white是白色。", 1),
    ("'黑色'的英文是____。", "black", "black是黑色。", 1),
    ("'橙色'的英文是____。", "orange", "orange是橙色。", 1),
    ("'棕色'的英文是____。", "brown", "brown是棕色。", 1),
    ("天空是蓝色的：The sky is ____。", "blue", "blue是蓝色。", 1),
    ("草是绿色的：The grass is ____。", "green", "green是绿色。", 1),
    ("'给我看看红色'：Show me ____。", "red", "red是红色。", 1),
    ("'我看到黄色'：I see ____。", "yellow", "yellow是黄色。", 1),
    ("'我喜欢蓝色'：I like ____。", "blue", "blue是蓝色。", 1),
    ("'它是什么颜色？'：What ____ is it?", "colour", "colour是颜色。", 2),
    ("'把它涂成绿色'：Colour it ____。", "green", "green是绿色。", 2),
    ("'花是红色的'：The flower is ____。", "red", "red是红色。", 1),
    ("'雪是白色的'：The snow is ____。", "white", "white是白色。", 1),
    ("'猫是黑色的'：The cat is ____。", "black", "black是黑色。", 1),
    ("'它是蓝白相间的'：It's blue ____ white。", "and", "and是和、并且。", 2),
    ("'太阳是黄色的'：The sun is ____。", "yellow", "yellow是黄色。", 1),
]
for content, ans, exp, diff in u2_fill:
    q("fill", T2, U2, content, ans, exp, diff)

u2_essay = [
    ("用英文描述你最喜欢的颜色，说说为什么喜欢它。（3-5句话）", "参考：My favourite colour is blue. I like blue. The sky is blue. The sea is blue. Blue is beautiful.", 1),
    ("用英文描述你看到的彩虹有哪些颜色。（3-5句话）", "参考：I see a rainbow. It's red and orange. It's yellow and green. It's blue and purple. It's beautiful!", 2),
    ("用英文描述你的书包是什么颜色的，里面有什么颜色的东西。（3-5句话）", "参考：My bag is blue. My pen is red. My pencil is yellow. My ruler is green. I like my bag.", 1),
    ("写一段你和朋友讨论颜色的对话。（至少4句）", "参考：What colour do you like? I like blue. What about you? I like green.", 1),
    ("用英文描述你画的一幅画用了哪些颜色。（3-5句话）", "参考：I draw a picture. The sun is yellow. The sky is blue. The grass is green. The flower is red.", 2),
    ("用英文描述你的房间有哪些颜色的东西。（3-5句话）", "参考：My room is white. My bed is blue. My desk is brown. My chair is black. I like my room.", 2),
    ("写一段你教弟弟妹妹认识颜色的对话。（至少5句）", "参考：What colour is this? It's red. What colour is that? It's blue. Good job!", 2),
    ("用英文描述你最喜欢的水果是什么颜色的。（3-5句话）", "参考：I like apples. Apples are red. I like bananas. Bananas are yellow. They are yummy!", 1),
    ("用英文描述四季的颜色。（3-5句话）", "参考：Spring is green. Summer is blue. Autumn is yellow. Winter is white. I love all seasons.", 3),
    ("写一段你在美术课上涂色的对话。（至少4句）", "参考：Colour the sky blue. OK! Colour the grass green. Done! It's beautiful!", 2),
    ("用英文描述你的衣服今天是什么颜色的。（3-5句话）", "参考：My shirt is white. My pants are blue. My shoes are black. I look nice today.", 1),
    ("用英文描述你看到的国旗有哪些颜色。（3-5句话）", "参考：The flag is red. It has yellow stars. Red and yellow are beautiful. I love my country.", 2),
    ("写一段你和妈妈买衣服时讨论颜色的对话。（至少4句）", "参考：Mum, I like the red one. The blue one is nice too. Let's get the red one. OK!", 2),
    ("用英文描述你画的动物用了哪些颜色。（3-5句话）", "参考：I draw a cat. The cat is black. The eyes are green. The nose is pink. It's cute!", 2),
    ("用英文描述交通灯有哪些颜色，各代表什么。（3-5句话）", "参考：The traffic light has three colours. Red means stop. Yellow means wait. Green means go.", 3),
    ("写一段你看到彩虹后和朋友的对话。（至少4句）", "参考：Look! A rainbow! What colours can you see? I see red, yellow and blue. It's so beautiful!", 2),
    ("用英文描述你的铅笔盒里有哪些颜色的笔。（3-5句话）", "参考：I have many pens. The red pen is for drawing. The blue pen is for writing. The green pen is for marking.", 2),
    ("用英文描述你最喜欢的花是什么颜色的。（3-5句话）", "参考：I like roses. Roses are red. I also like sunflowers. They are yellow. Flowers are beautiful.", 1),
    ("写一段你在公园里看到各种颜色的对话。（至少4句）", "参考：The grass is green. The sky is blue. The flowers are red and yellow. What a beautiful park!", 2),
    ("用英文描述你梦想中的房间是什么颜色的。（3-5句话）", "参考：I want a blue room. The walls are blue. The bed is white. The curtains are yellow. It's my dream room.", 2),
]
for content, exp, diff in u2_essay:
    q("essay", T2, U2, content, "待老师点评", exp, diff)

u2_match = [
    ("将颜色英文与中文连线。", ["red", "blue", "green", "yellow"], ["蓝色", "红色", "黄色", "绿色"], "0:1,1:0,2:3,3:2", "red红，blue蓝，green绿，yellow黄。", 1),
    ("将颜色英文与中文连线。", ["white", "black", "orange", "brown"], ["黑色", "白色", "棕色", "橙色"], "0:1,1:0,2:3,3:2", "white白，black黑，orange橙，brown棕。", 1),
    ("将颜色与对应事物连线。", ["blue", "green", "yellow", "white"], ["草地", "天空", "雪", "太阳"], "0:1,1:0,2:3,3:2", "blue天空，green草地，yellow太阳，white雪。", 1),
    ("将颜色与对应事物连线。", ["red", "black", "brown", "orange"], ["橙子", "苹果", "熊", "猫"], "0:1,1:3,2:2,3:0", "red苹果，black猫，brown熊，orange橙子。", 2),
    ("将英文与中文连线。", ["I see", "Show me", "I like", "Colour it"], ["给我看看", "涂色", "我看到", "我喜欢"], "0:2,1:0,2:3,3:1", "I see我看到，Show me给我看，I like我喜欢，Colour it涂色。", 2),
    ("将英文与中文连线。", ["The sky is blue.", "The grass is green.", "The sun is yellow.", "The snow is white."], ["草是绿色的。", "雪是白色的。", "天空是蓝色的。", "太阳是黄色的。"], "0:2,1:0,2:3,3:1", "根据句意匹配。", 1),
    ("将颜色英文与中文连线。", ["red", "green", "blue", "white"], ["绿色", "白色", "红色", "蓝色"], "0:2,1:0,2:3,3:1", "red红，green绿，blue蓝，white白。", 1),
    ("将颜色英文与中文连线。", ["yellow", "black", "orange", "brown"], ["橙色", "黄色", "棕色", "黑色"], "0:1,1:3,2:0,3:2", "yellow黄，black黑，orange橙，brown棕。", 1),
    ("将英文与中文连线。", ["What colour?", "I like red.", "Show me blue.", "It's green."], ["给我看看蓝色。", "它是什么颜色？", "它是绿色的。", "我喜欢红色。"], "0:1,1:3,2:0,3:2", "根据句意匹配。", 2),
    ("将颜色与对应事物连线。", ["blue", "red", "green", "yellow"], ["苹果", "天空", "香蕉", "树叶"], "0:1,1:0,2:3,3:2", "blue天空，red苹果，green树叶，yellow香蕉。", 1),
    ("将英文与中文连线。", ["red", "blue", "green", "yellow"], ["黄色", "绿色", "蓝色", "红色"], "0:3,1:2,2:1,3:0", "red红，blue蓝，green绿，yellow黄。", 1),
    ("将英文与中文连线。", ["white", "black", "orange", "brown"], ["棕色", "橙色", "黑色", "白色"], "0:3,1:2,2:1,3:0", "white白，black黑，orange橙，brown棕。", 1),
    ("将颜色与对应事物连线。", ["white", "black", "green", "blue"], ["大海", "雪", "树叶", "夜晚"], "0:1,1:3,2:2,3:0", "white雪，black夜晚，green树叶，blue大海。", 2),
    ("将英文与中文连线。", ["Colour the apple.", "I see red.", "The sky is blue.", "Show me green."], ["我看到红色。", "给我看看绿色。", "把苹果涂色。", "天空是蓝色的。"], "0:2,1:0,2:3,3:1", "根据句意匹配。", 2),
    ("将颜色英文与中文连线。", ["red", "yellow", "blue", "green"], ["蓝色", "绿色", "红色", "黄色"], "0:2,1:3,2:0,3:1", "red红，yellow黄，blue蓝，green绿。", 1),
    ("将颜色与对应事物连线。", ["orange", "brown", "white", "black"], ["熊", "橙子", "猫", "兔子"], "0:1,1:0,2:3,3:2", "orange橙子，brown熊，white兔子，black猫。", 2),
    ("将英文与中文连线。", ["I like blue.", "It's red.", "What colour?", "Show me yellow."], ["它是什么颜色？", "给我看看黄色。", "我喜欢蓝色。", "它是红色的。"], "0:2,1:3,2:0,3:1", "根据句意匹配。", 2),
    ("将颜色英文与中文连线。", ["green", "red", "black", "white"], ["白色", "黑色", "绿色", "红色"], "0:2,1:3,2:1,3:0", "green绿，red红，black黑，white白。", 1),
    ("将颜色与对应事物连线。", ["yellow", "blue", "red", "green"], ["太阳", "草地", "大海", "苹果"], "0:0,1:2,2:3,3:1", "yellow太阳，blue大海，red苹果，green草地。", 1),
    ("将英文与中文连线。", ["The flower is red.", "The sky is blue.", "The grass is green.", "The snow is white."], ["天空是蓝色的。", "雪是白色的。", "花是红色的。", "草是绿色的。"], "0:2,1:0,2:3,3:1", "根据句意匹配。", 1),
]
for content, opts, mopts, ans, exp, diff in u2_match:
    q("match", T2, U2, content, ans, exp, diff, options=opts, match_options=mopts)

u2_sort = [
    ("将下列颜色按彩虹顺序排列（红橙黄绿蓝）。", ["green", "red", "blue", "yellow"], "1,3,0,2", "彩虹顺序：red, orange, yellow, green, blue。这里取红黄绿蓝。", 2),
    ("将下列颜色按字母表顺序排列。", ["red", "blue", "green", "black"], "3,1,2,0", "字母表顺序：black, blue, green, red。", 2),
    ("将下列颜色按字母表顺序排列。", ["white", "yellow", "orange", "brown"], "3,2,0,1", "字母表顺序：brown, orange, white, yellow。", 2),
    ("将下列对话按正确顺序排列。", ["It's red.", "What colour is it?", "Show me your crayon.", "OK! Here you are."], "2,3,1,0", "先要求展示，再给，再问颜色，最后回答。", 2),
    ("将下列对话按正确顺序排列。", ["I like blue.", "What colour do you like?", "Me too!", "I like blue too."], "1,0,3,2", "先问喜欢什么颜色，再回答，再说我也喜欢蓝色，最后说我也是。", 2),
    ("将下列句子按正确顺序排列成对话。", ["The sky is blue.", "What colour is the sky?", "Yes, it is.", "Is it blue?"], "1,0,3,2", "先问颜色，再回答，再确认，最后肯定。", 2),
    ("将下列颜色按字母表顺序排列。", ["green", "red", "blue", "yellow"], "2,0,1,3", "字母表顺序：blue, green, red, yellow。", 2),
    ("将下列颜色按字母表顺序排列。", ["orange", "white", "black", "brown"], "2,3,0,1", "字母表顺序：black, brown, orange, white。", 2),
    ("将下列对话按正确顺序排列。", ["Colour it red.", "OK! It's red now.", "Show me your picture.", "Here you are. It's beautiful!"], "2,3,0,1", "先要求展示，再给并夸赞，再要求涂色，最后完成。", 2),
    ("将下列句子按正确顺序排列。", ["I see green.", "Look at the grass!", "Yes, the grass is green.", "What colour is it?"], "1,3,0,2", "先看草，再问颜色，再说看到绿色，最后确认。", 2),
    ("将下列颜色按字母表顺序排列。", ["purple", "pink", "red", "white"], "1,0,2,3", "字母表顺序：pink, purple, red, white。", 2),
    ("将下列对话按正确顺序排列。", ["It's yellow.", "What colour is the banana?", "Yes, bananas are yellow.", "Do you like bananas?"], "1,0,3,2", "先问颜色，再回答，再问喜不喜欢，最后确认。", 2),
    ("将下列颜色按字母表顺序排列。", ["blue", "green", "red", "black"], "3,0,1,2", "字母表顺序：black, blue, green, red。", 2),
    ("将下列句子按正确顺序排列。", ["The apple is red.", "I like apples.", "What colour is the apple?", "It's red and sweet."], "2,0,3,1", "先问颜色，再说苹果是红色，再说又红又甜，最后说喜欢。", 2),
    ("将下列颜色按字母表顺序排列。", ["yellow", "white", "orange", "green"], "3,2,1,0", "字母表顺序：green, orange, white, yellow。", 2),
    ("将下列对话按正确顺序排列。", ["Show me blue.", "Here is the blue crayon.", "Thank you!", "You're welcome."], "0,1,2,3", "先要求，再给，再谢谢，最后不客气。", 1),
    ("将下列颜色按字母表顺序排列。", ["brown", "black", "blue", "green"], "1,0,2,3", "字母表顺序：black, brown, blue, green。", 2),
    ("将下列句子按正确顺序排列。", ["I see a rainbow.", "What colours can you see?", "Red, yellow, green and blue.", "How beautiful!"], "0,1,2,3", "先看到彩虹，再问颜色，再回答，最后感叹。", 2),
    ("将下列颜色按字母表顺序排列。", ["red", "orange", "yellow", "green"], "3,1,0,2", "字母表顺序：green, orange, red, yellow。", 2),
    ("将下列对话按正确顺序排列。", ["What colour is your bag?", "It's blue.", "I like blue too!", "Me too! Blue is nice."], "0,1,3,2", "先问颜色，再回答，再说我也喜欢蓝色，最后回应。", 2),
]
for content, opts, ans, exp, diff in u2_sort:
    q("sort", T2, U2, content, ans, exp, diff, options=opts)

print(f"After Unit 2: {len(questions)} questions")

# Save
with open("C:/Users/Yaojie/Documents/GitHub/quiz/src/data/english_grade3_vol1.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print(f"Saved {len(questions)} questions")
