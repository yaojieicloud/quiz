"""Generate English Grade 3 Vol 1 (PEP) questions - 6 Units x 6 types x 20 = 720 questions"""
import json

questions = []

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
# Unit 1: Hello! (greetings, stationery: pen, pencil, ruler, eraser, crayon, bag)
# ============================================================
U1 = "Unit 1"
T1 = "Hello!"

# --- Choice (20) ---
u1_choice = [
    ("'Hello' 是什么意思？", ["再见", "你好", "谢谢", "对不起"], "1", "Hello是你好，用于打招呼。", 1),
    ("'Goodbye' 是什么意思？", ["你好", "早上好", "再见", "晚安"], "2", "Goodbye是再见，用于告别。", 1),
    ("'pen' 是什么意思？", ["铅笔", "钢笔", "尺子", "橡皮"], "1", "pen是钢笔，pencil才是铅笔。", 1),
    ("'pencil' 是什么意思？", ["钢笔", "铅笔", "蜡笔", "书包"], "1", "pencil是铅笔。", 1),
    ("'ruler' 是什么意思？", ["橡皮", "尺子", "蜡笔", "书包"], "1", "ruler是尺子。", 1),
    ("'eraser' 是什么意思？", ["尺子", "蜡笔", "橡皮", "钢笔"], "2", "eraser是橡皮。", 1),
    ("'crayon' 是什么意思？", ["蜡笔", "铅笔", "钢笔", "尺子"], "0", "crayon是蜡笔。", 1),
    ("'bag' 是什么意思？", ["书", "书包", "铅笔盒", "橡皮"], "1", "bag是书包。", 1),
    ("早上见到老师，应该说：", ["Good night!", "Good morning!", "Goodbye!", "Sorry!"], "1", "早上见面说Good morning（早上好）。", 1),
    ("放学回家时，跟老师说：", ["Hello!", "Good morning!", "Goodbye!", "Thank you!"], "2", "离开时说Goodbye（再见）。", 1),
    ("'I'm Sarah.' 是什么意思？", ["我是Sarah。", "你好Sarah。", "再见Sarah。", "谢谢Sarah。"], "0", "I'm = I am，意思是我是。", 1),
    ("'What's your name?' 是在问什么？", ["你几岁？", "你叫什么名字？", "你好吗？", "你在哪里？"], "1", "What's your name? 问你叫什么名字。", 1),
    ("别人问你叫什么名字，你应该回答：", ["I'm fine.", "My name is Tom.", "Goodbye.", "Thank you."], "1", "回答名字用My name is...或I'm...", 1),
    ("'Show me your pencil.' 是什么意思？", ["给我看看你的铅笔。", "给我一支铅笔。", "你的铅笔在哪里？", "这是你的铅笔。"], "0", "Show me是给我看看的意思。", 2),
    ("下列哪个是'橡皮'的英文？", ["ruler", "eraser", "crayon", "pen"], "1", "eraser是橡皮。", 1),
    ("'Open your bag.' 是什么意思？", ["关上你的书包。", "打开你的书包。", "看看你的书包。", "这是你的书包。"], "1", "Open是打开的意思。", 2),
    ("'Close your book.' 是什么意思？", ["打开你的书。", "关上你的书。", "看看你的书。", "给我你的书。"], "1", "Close是关上的意思。", 2),
    ("'I have a ruler.' 是什么意思？", ["我有一把尺子。", "这是一把尺子。", "我喜欢尺子。", "尺子在哪里？"], "0", "I have是我也有的意思。", 1),
    ("'Good afternoon' 是什么意思？", ["早上好", "下午好", "晚上好", "晚安"], "1", "afternoon是下午，Good afternoon是下午好。", 1),
    ("'Me too!' 是什么意思？", ["我也是！", "谢谢你！", "对不起！", "再见！"], "0", "Me too表示我也是，用于附和别人。", 1),
]
for content, opts, ans, exp, diff in u1_choice:
    q("choice", T1, U1, content, ans, exp, diff, options=opts)

# --- Judge (20) ---
u1_judge = [
    ("'pen' 的意思是铅笔。", "1", "pen是钢笔，pencil才是铅笔。", 1),
    ("'Hello' 和 'Hi' 都是打招呼用的。", "0", "对的，Hello和Hi都表示你好。", 1),
    ("'Goodbye' 是早上好的意思。", "1", "Goodbye是再见，Good morning才是早上好。", 1),
    ("'eraser' 的意思是橡皮。", "0", "对的，eraser就是橡皮。", 1),
    ("'ruler' 的意思是蜡笔。", "1", "ruler是尺子，crayon才是蜡笔。", 1),
    ("'bag' 的意思是书包。", "0", "对的，bag就是书包。", 1),
    ("'crayon' 的意思是钢笔。", "1", "crayon是蜡笔，pen才是钢笔。", 1),
    ("'Good night' 是睡觉前说的。", "0", "对的，Good night是晚安，睡觉前说。", 1),
    ("'pencil' 的意思是尺子。", "1", "pencil是铅笔，ruler才是尺子。", 1),
    ("'I'm Tom.' 和 'My name is Tom.' 意思一样。", "0", "对的，两种说法都表示我叫Tom。", 1),
    ("'Good morning' 是晚上说的。", "1", "Good morning是早上好，早上说的。", 1),
    ("'Show me' 是给我看看的意思。", "0", "对的，Show me就是给我看看。", 1),
    ("'Open' 是关上的意思。", "1", "Open是打开，Close才是关上。", 1),
    ("'I have a pen.' 意思是我有一支钢笔。", "0", "对的，I have是我有。", 1),
    ("'What's your name?' 是问你几岁了。", "1", "What's your name是问名字，How old are you才是问年龄。", 1),
    ("'Good afternoon' 是下午好。", "0", "对的，afternoon是下午。", 1),
    ("'Me too' 是对不起的意思。", "1", "Me too是我也是，Sorry才是对不起。", 1),
    ("'Thank you' 是谢谢的意思。", "0", "对的，Thank you就是谢谢。", 1),
    ("'Close your book' 是打开你的书。", "1", "Close是关上，Open才是打开。", 1),
    ("'Hi' 只能对老师说，不能对同学说。", "1", "Hi可以对任何人说，同学、老师、朋友都可以。", 1),
]
for content, ans, exp, diff in u1_judge:
    q("judge", T1, U1, content, ans, exp, diff, options=["对", "错"])

# --- Fill (20) ---
u1_fill = [
    ("'钢笔'的英文是____。", "pen", "pen是钢笔。", 1),
    ("'铅笔'的英文是____。", "pencil", "pencil是铅笔。", 1),
    ("'尺子'的英文是____。", "ruler", "ruler是尺子。", 1),
    ("'橡皮'的英文是____。", "eraser", "eraser是橡皮。", 1),
    ("'蜡笔'的英文是____。", "crayon", "crayon是蜡笔。", 1),
    ("'书包'的英文是____。", "bag", "bag是书包。", 1),
    ("早上见面说Good ____。", "morning", "Good morning是早上好。", 1),
    ("告别时说____。", "Goodbye", "Goodbye是再见。", 1),
    ("自我介绍：My ____ is Tom.", "name", "My name is...是自我介绍的常用句型。", 1),
    ("问别人名字：What's your ____?", "name", "What's your name? 问你叫什么名字。", 1),
    ("'给我看看'的英文是____ me。", "Show", "Show me是给我看看。", 2),
    ("'打开'的英文是____。", "Open", "Open是打开。", 1),
    ("'关上'的英文是____。", "Close", "Close是关上。", 1),
    ("'我也是'的英文是Me ____。", "too", "Me too是我也是。", 1),
    ("'谢谢'的英文是____ you。", "Thank", "Thank you是谢谢。", 1),
    ("'下午好'是Good ____。", "afternoon", "afternoon是下午。", 2),
    ("'晚安'是Good ____。", "night", "Good night是晚安。", 1),
    ("'我有一支铅笔'：I have a ____。", "pencil", "pencil是铅笔。", 1),
    ("'你好'的英文是____。", "Hello", "Hello是你好。", 1),
    ("'对不起'的英文是____。", "Sorry", "Sorry是对不起。", 1),
]
for content, ans, exp, diff in u1_fill:
    q("fill", T1, U1, content, ans, exp, diff)

# --- Essay (20) ---
u1_essay = [
    ("用英文写一段自我介绍，包括你的名字和年龄。（3-5句话）", "参考：Hello! My name is... I'm... years old. I'm a boy/girl. Nice to meet you!", 1),
    ("用英文介绍你的书包里有什么。（3-5句话）", "参考：This is my bag. I have a pen. I have a pencil. I have a ruler. I have an eraser.", 1),
    ("写一段你和朋友的对话，包括打气和问名字。（至少4句）", "参考：A: Hello! B: Hi! A: What's your name? B: My name is...", 1),
    ("用英文描述你的铅笔盒里有什么文具。（3-5句话）", "参考：I have a pencil box. There is a pen. There is a pencil. There is a ruler. There is an eraser.", 2),
    ("写一段早上到学校后和老师同学的对话。（至少4句）", "参考：Good morning, Miss Li! Good morning, Tom! Hello! Hi!", 1),
    ("用英文写一写你今天带了哪些文具上学。（3-5句话）", "参考：Today I have a pen. I have a pencil. I have a ruler. I have a crayon.", 1),
    ("写一段放学时和同学告别的对话。（至少4句）", "参考：Goodbye, Tom! Bye! See you tomorrow! See you!", 1),
    ("用英文介绍你最喜欢的一种文具，说说为什么喜欢它。（3-5句话）", "参考：I like my crayon. It's red. I can draw pictures with it. I like it very much.", 2),
    ("写一段你和新同学第一次见面的对话。（至少5句）", "参考：Hello! Hi! What's your name? My name is... Nice to meet you! Nice to meet you, too!", 1),
    ("用英文写一写你的书包是什么颜色的，里面有什么。（3-5句话）", "参考：My bag is blue. I have a pen in my bag. I have a book. I have a ruler.", 2),
    ("写一段课堂上老师说Show me your pencil后你的回答。（至少3句）", "参考：OK! This is my pencil. Here you are.", 1),
    ("用英文写一写你文具盒里有几支铅笔、几块橡皮。（3-5句话）", "参考：I have three pencils. I have two erasers. I have one ruler. I have many crayons.", 2),
    ("写一段你教新同学认识文具的对话。（至少5句）", "参考：This is a pen. This is a pencil. This is a ruler. What's this? It's an eraser.", 2),
    ("用英文写一写你最喜欢上什么课，为什么。（3-5句话）", "参考：I like English class. I can learn new words. I like my teacher. English is fun.", 2),
    ("写一段你借文具给同学的对话。（至少4句）", "参考：Can I have a pencil? Sure, here you are. Thank you! You're welcome.", 2),
    ("用英文描述你的一天中什么时候说Hello、Goodbye。（3-5句话）", "参考：In the morning, I say Hello to my teacher. At school, I say Hi to my friends. After school, I say Goodbye.", 2),
    ("写一段你向妈妈介绍新同学的对话。（至少4句）", "参考：Mum, this is my friend. Her name is Lily. Hello, Lily! Nice to meet you!", 2),
    ("用英文写一写你的文具都有什么颜色。（3-5句话）", "参考：My pen is black. My pencil is yellow. My ruler is blue. My eraser is white.", 2),
    ("写一段你丢失文具后寻找的对话。（至少4句）", "参考：Where is my pencil? Is it in your bag? No, it's not. Oh, here it is! Thank you!", 2),
    ("用英文写一写开学第一天你的心情。（3-5句话）", "参考：Today is the first day of school. I'm happy. I have a new bag. I have new pencils. I like school.", 2),
]
for content, exp, diff in u1_essay:
    q("essay", T1, U1, content, "待老师点评", exp, diff)

# --- Match (20) ---
u1_match = [
    ("将英文单词与中文意思连线。", ["pen", "pencil", "ruler", "eraser"], ["铅笔", "钢笔", "橡皮", "尺子"], "0:1,1:0,2:3,3:2", "pen钢笔，pencil铅笔，ruler尺子，eraser橡皮。", 1),
    ("将英文单词与中文意思连线。", ["crayon", "bag", "book", "hello"], ["书包", "蜡笔", "你好", "书"], "0:1,1:0,2:3,3:2", "crayon蜡笔，bag书包，book书，hello你好。", 1),
    ("将问候语与使用场景连线。", ["Good morning", "Good afternoon", "Good night", "Goodbye"], ["下午见面", "睡觉前", "早上见面", "离开时"], "0:2,1:0,2:1,3:3", "Good morning早上，Good afternoon下午，Good night睡前，Goodbye离开。", 1),
    ("将英文与中文连线。", ["Open", "Close", "Show", "Have"], ["关上", "打开", "有", "展示"], "0:1,1:0,2:3,3:2", "Open打开，Close关上，Show展示，Have有。", 2),
    ("将文具与用途连线。", ["pen", "ruler", "eraser", "crayon"], ["画直线", "写字", "擦错字", "画画"], "0:1,1:0,2:2,3:3", "pen写字，ruler画直线，eraser擦错字，crayon画画。", 2),
    ("将英文与中文连线。", ["I'm", "My name is", "Thank you", "Me too"], ["谢谢", "我也是", "我是", "我的名字是"], "0:2,1:3,2:0,3:1", "I'm我是，My name is我的名字是，Thank you谢谢，Me too我也是。", 1),
    ("将英文与中文连线。", ["What's your name?", "How are you?", "Nice to meet you.", "See you."], ["再见。", "你叫什么名字？", "很高兴认识你。", "你好吗？"], "0:1,1:3,2:2,3:0", "What's your name问名字，How are you问好，Nice to meet you初次见面，See you再见。", 2),
    ("将英文与中文连线。", ["red pen", "blue ruler", "green bag", "yellow pencil"], ["黄色铅笔", "红色钢笔", "绿色书包", "蓝色尺子"], "0:1,1:3,2:2,3:0", "red红，blue蓝，green绿，yellow黄。", 2),
    ("将英文与中文连线。", ["I have a pen.", "Show me your book.", "Open your bag.", "Close your pencil box."], ["打开你的书包。", "我有一支钢笔。", "关上你的铅笔盒。", "给我看看你的书。"], "0:1,1:3,2:0,3:2", "I have我有，Show me给我看，Open打开，Close关上。", 2),
    ("将英文与中文连线。", ["Good morning, Miss Li.", "Hello, I'm Sarah.", "Goodbye, Tom.", "Thank you, Mum."], ["再见，Tom。", "早上好，李老师。", "谢谢，妈妈。", "你好，我是Sarah。"], "0:1,1:3,2:0,3:2", "根据句意匹配。", 1),
    ("将英文与中文连线。", ["pencil", "eraser", "crayon", "bag"], ["橡皮", "蜡笔", "铅笔", "书包"], "0:2,1:0,2:1,3:3", "pencil铅笔，eraser橡皮，crayon蜡笔，bag书包。", 1),
    ("将英文与中文连线。", ["pen", "ruler", "book", "hello"], ["你好", "书", "钢笔", "尺子"], "0:2,1:3,2:1,3:0", "pen钢笔，ruler尺子，book书，hello你好。", 1),
    ("将英文与中文连线。", ["Good night", "Good afternoon", "Good morning", "Goodbye"], ["再见", "晚安", "下午好", "早上好"], "0:1,1:2,2:3,3:0", "Good night晚安，Good afternoon下午好，Good morning早上好，Goodbye再见。", 1),
    ("将英文与中文连线。", ["I'm fine.", "Me too.", "Here you are.", "You're welcome."], ["给你。", "我也是。", "不客气。", "我很好。"], "0:3,1:1,2:0,3:2", "I'm fine我很好，Me too我也是，Here you are给你，You're welcome不客气。", 2),
    ("将英文与中文连线。", ["What's this?", "It's a pen.", "I like it.", "Thank you."], ["谢谢。", "这是什么？", "我喜欢它。", "它是一支钢笔。"], "0:1,1:3,2:2,3:0", "What's this这是什么，It's a pen它是钢笔，I like it我喜欢，Thank you谢谢。", 1),
    ("将英文与中文连线。", ["Show me your ruler.", "I have a crayon.", "Open your book.", "Good morning."], ["早上好。", "给我看看你的尺子。", "打开你的书。", "我有一支蜡笔。"], "0:1,1:3,2:2,3:0", "Show me给我看，I have我有，Open打开，Good morning早上好。", 2),
    ("将英文与中文连线。", ["pencil", "pen", "bag", "eraser"], ["书包", "橡皮", "铅笔", "钢笔"], "0:2,1:3,2:0,3:1", "pencil铅笔，pen钢笔，bag书包，eraser橡皮。", 1),
    ("将英文与中文连线。", ["Hello", "Goodbye", "Sorry", "Please"], ["请", "你好", "对不起", "再见"], "0:1,1:3,2:2,3:0", "Hello你好，Goodbye再见，Sorry对不起，Please请。", 1),
    ("将英文与中文连线。", ["ruler", "crayon", "pen", "pencil"], ["蜡笔", "铅笔", "尺子", "钢笔"], "0:2,1:0,2:3,3:1", "ruler尺子，crayon蜡笔，pen钢笔，pencil铅笔。", 1),
    ("将英文与中文连线。", ["I'm Tom.", "Nice to meet you.", "See you.", "Good night."], ["晚安。", "我是Tom。", "很高兴认识你。", "再见。"], "0:1,1:2,2:3,3:0", "I'm Tom我是Tom，Nice to meet you很高兴认识你，See you再见，Good night晚安。", 1),
]
for content, opts, mopts, ans, exp, diff in u1_match:
    q("match", T1, U1, content, ans, exp, diff, options=opts, match_options=mopts)

# --- Sort (20) ---
u1_sort = [
    ("将下列字母按字母表顺序排列。", ["C", "A", "D", "B"], "1,3,0,2", "字母表顺序：A, B, C, D。", 1),
    ("将下列字母按字母表顺序排列。", ["E", "G", "F", "H"], "0,2,1,3", "字母表顺序：E, F, G, H。", 1),
    ("将下列字母按字母表顺序排列。", ["J", "I", "L", "K"], "1,0,3,2", "字母表顺序：I, J, K, L。", 1),
    ("将下列字母按字母表顺序排列。", ["N", "M", "P", "O"], "1,0,3,2", "字母表顺序：M, N, O, P。", 1),
    ("将下列字母按字母表顺序排列。", ["R", "Q", "T", "S"], "1,0,3,2", "字母表顺序：Q, R, S, T。", 1),
    ("将下列对话按正确顺序排列。", ["My name is Tom.", "Hello!", "What's your name?", "Nice to meet you!"], "1,2,0,3", "先打招呼，再问名字，然后回答，最后说很高兴认识你。", 1),
    ("将下列对话按正确顺序排列。", ["Goodbye!", "Good morning!", "See you tomorrow!", "Hello!"], "1,3,0,2", "先早上好，再你好，然后再见，最后明天见。", 1),
    ("将下列对话按正确顺序排列。", ["Thank you!", "Here you are.", "Can I have a pen?", "You're welcome."], "2,1,0,3", "先请求，再给，然后谢谢，最后不客气。", 2),
    ("将下列对话按正确顺序排列。", ["I'm fine, thank you.", "Good morning!", "How are you?", "Good morning!"], "1,3,2,0", "先早上好，再回早上好，然后问好，最后回答。", 2),
    ("将下列对话按正确顺序排列。", ["Nice to meet you, too.", "Hello, I'm Sarah.", "What's your name?", "My name is Mike. Nice to meet you!"], "1,2,3,0", "先自我介绍，再问名字，再回答并说高兴认识你，最后回应。", 2),
    ("将下列单词按字母个数从少到多排列。", ["pencil", "pen", "eraser", "bag"], "1,3,0,2", "pen(3), bag(3), pencil(6), eraser(6)。按字母数：pen, bag, pencil, eraser。", 2),
    ("将下列单词按字母表顺序排列。", ["ruler", "pen", "bag", "eraser"], "2,3,1,0", "字母表顺序：bag, eraser, pen, ruler。", 2),
    ("将下列单词按字母表顺序排列。", ["crayon", "book", "pencil", "desk"], "1,0,3,2", "字母表顺序：book, crayon, desk, pencil。", 2),
    ("将下列数字按从小到大排列。", ["three", "one", "five", "two"], "1,3,0,2", "one(1), two(2), three(3), five(5)。", 1),
    ("将下列数字按从小到大排列。", ["ten", "seven", "eight", "nine"], "1,2,3,0", "seven(7), eight(8), nine(9), ten(10)。", 1),
    ("将下列对话按正确顺序排列。", ["Show me your pencil.", "OK! Here you are.", "Thank you!", "Good morning, class!"], "3,0,1,2", "先早上好，再要求展示，再给，最后谢谢。", 2),
    ("将下列对话按正确顺序排列。", ["Goodbye, Miss Li!", "Good morning, Miss Li!", "Good morning, class!", "See you tomorrow!"], "1,2,0,3", "先早上好，再回早上好，放学再见，明天见。", 1),
    ("将下列句子按正确顺序排列成对话。", ["I'm Tom.", "Hello!", "What's your name?", "Hi!"], "1,3,2,0", "先Hello，再Hi，再问名字，最后回答。", 1),
    ("将下列字母按字母表顺序排列。", ["U", "W", "V", "X"], "0,2,1,3", "字母表顺序：U, V, W, X。", 1),
    ("将下列字母按字母表顺序排列。", ["Z", "Y", "X", "W"], "3,2,1,0", "字母表顺序：W, X, Y, Z。", 1),
]
for content, opts, ans, exp, diff in u1_sort:
    q("sort", T1, U1, content, ans, exp, diff, options=opts)

print(f"Unit 1 done: {len(questions)} questions")

# Save partial result
with open("C:/Users/Yaojie/Documents/GitHub/quiz/src/data/english_grade3_vol1.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print(f"Saved {len(questions)} questions to english_grade3_vol1.json")
