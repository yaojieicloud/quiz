# -*- coding: utf-8 -*-
"""上册阅读补充：每单元补 7 篇到 5 篇/课时（PA+1 PB+2 PC+2 语音+2），共42篇。
读入 english_reading_upper.json 合并后写回。"""
import json
from collections import Counter, defaultdict

Q = []

def items_from(pairs):
    out = []
    for q, opts, ans, expl in pairs:
        out.append({"type": "choice", "q": q, "options": opts, "answer": str(ans), "explanation": expl})
    return out

def r(topic, unit, content, pairs, diff=1):
    items = items_from(pairs)
    Q.append({
        "type": "reading", "topic_name": topic, "unit": unit,
        "content": content, "options": None,
        "reading_items": items,
        "answer": ",".join(it["answer"] for it in items),
        "explanation": "", "difficulty": diff,
    })

U1 = "上册-Unit 1 Making friends"
U2 = "上册-Unit 2 Different families"
U3 = "上册-Unit 3 Amazing animals"
U4 = "上册-Unit 4 Plants around us"
U5 = "上册-Unit 5 The colourful world"
U6 = "上册-Unit 6 Useful numbers"
PA, PB, PC, PD = "Part A 词汇", "Part B 句型", "Part C 对话", "字母与语音"

# ===== Unit 1 补: PA1 PB2 PC2 语音2 =====
r(PA, U1, "My friend has a red bag. He has a blue pen. We go to school together every morning.", [
    ("What colour is the bag?", ["Red", "Blue", "Green", "Black"], "0", "文中说 a red bag。"),
    ("When do they go to school?", ["Every morning", "At night", "Never", "Only Friday"], "0", "文中说 every morning。"),
])
r(PB, U1, "A: How are you? B: I'm fine, thank you. A: Let's play together. B: OK, great!", [
    ("How is B?", ["Fine", "Sad", "Sick", "Tired"], "0", "B 说 I'm fine。"),
    ("What do they want to do?", ["Play together", "Sleep", "Eat", "Read"], "0", "A 说 Let's play together。"),
])
r(PB, U1, "Is he your friend? Yes, he is. His name is Jack. We often play ball after school.", [
    ("Is he the writer's friend?", ["Yes", "No", "Maybe", "Never"], "0", "文中说 Yes, he is。"),
    ("When do they play ball?", ["After school", "Before school", "At night", "In class"], "0", "文中说 after school。"),
])
r(PC, U1, "A new student comes to our class. We say welcome to her. She smiles and says thank you. Soon we become friends.", [
    ("Who comes to the class?", ["A new student", "A teacher", "A doctor", "A cook"], "0", "文中说 A new student comes。"),
    ("What does she say?", ["Thank you", "Goodbye", "Sorry", "No"], "0", "文中说 she says thank you。"),
])
r(PC, U1, "Mike and Lily sit together. They read books together. They help each other. They are best friends.", [
    ("What do they do together?", ["Read books", "Play ball", "Swim", "Sing"], "0", "文中说 They read books together。"),
    ("What are they?", ["Best friends", "Brothers", "Strangers", "Enemies"], "0", "文中说 They are best friends。"),
])
r(PD, U1, "Letter O o says /ɒ/. Octopus starts with O. Letter P p says /p/. Panda starts with P.", [
    ("What starts with O?", ["Octopus", "Panda", "Pig", "Pen"], "0", "文中说 Octopus starts with O。"),
    ("What starts with P?", ["Octopus", "Panda", "Owl", "Orange"], "1", "文中说 Panda starts with P。"),
])
r(PD, U1, "We sing the alphabet song. A B C D E F G. Letters are our friends. We love learning letters.", [
    ("What do they sing?", ["Alphabet song", "Birthday song", "Sleep song", "Rain song"], "0", "文中说 the alphabet song。"),
    ("What are letters to them?", ["Friends", "Enemies", "Food", "Toys"], "0", "文中说 Letters are our friends。"),
])

# ===== Unit 2 补: PA1 PB2 PC2 语音2 =====
r(PA, U2, "This is my family photo. My father is reading. My mother is cooking. I am playing with my brother.", [
    ("What is father doing?", ["Reading", "Cooking", "Sleeping", "Running"], "0", "文中说 My father is reading。"),
    ("What is mother doing?", ["Cooking", "Reading", "Swimming", "Singing"], "0", "文中说 My mother is cooking。"),
])
r(PB, U2, "A: Is this your brother? B: Yes, it is. A: How old is he? B: He is eight.", [
    ("Is it B's brother?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, it is。"),
    ("How old is the brother?", ["Eight", "Six", "Ten", "Nine"], "0", "B 说 He is eight。"),
])
r(PB, U2, "Who is the man in the photo? He is my grandpa. He is old but strong. He often plays with me.", [
    ("Who is the man?", ["Grandpa", "Father", "Uncle", "Brother"], "0", "文中说 He is my grandpa。"),
    ("What does grandpa often do?", ["Plays with me", "Sleeps all day", "Goes away", "Reads only"], "0", "文中说 He often plays with me。"),
])
r(PC, U2, "On Mother's Day, Lily makes a card. She draws a heart on it. She says, I love you, Mum. Her mother is very happy.", [
    ("What does Lily make?", ["A card", "A cake", "A toy", "A dress"], "0", "文中说 Lily makes a card。"),
    ("How does her mother feel?", ["Very happy", "Sad", "Angry", "Tired"], "0", "文中说 very happy。"),
])
r(PC, U2, "Sam's family eats dinner together. They talk and laugh. After dinner, they watch TV. Family time is warm.", [
    ("What do they do after dinner?", ["Watch TV", "Go to school", "Swim", "Work"], "0", "文中说 they watch TV。"),
    ("How is family time?", ["Warm", "Cold", "Sad", "Boring"], "0", "文中说 Family time is warm。"),
])
r(PD, U2, "Letter I i says /ɪ/. It starts with I. Letter J j says /dʒ/. Jam starts with J.", [
    ("What starts with I?", ["It", "Jam", "Jet", "Jam"], "0", "文中说 It starts with I。"),
    ("What starts with J?", ["It", "Jam", "In", "Ice"], "1", "文中说 Jam starts with J。"),
])
r(PD, U2, "Look at the letter K k. Kite starts with K. Look at the letter L l. Lion starts with L.", [
    ("What starts with K?", ["Kite", "Lion", "Leg", "Lamp"], "0", "文中说 Kite starts with K。"),
    ("What starts with L?", ["Kite", "Lion", "Key", "Kid"], "1", "文中说 Lion starts with L。"),
])

# ===== Unit 3 补: PA1 PB2 PC2 语音2 =====
r(PA, U3, "The tiger is strong. The bear is big. The fox is clever. The animals in the forest are amazing.", [
    ("What is strong?", ["Tiger", "Fox", "Rabbit", "Bird"], "0", "文中说 The tiger is strong。"),
    ("What is clever?", ["Fox", "Bear", "Cow", "Pig"], "0", "文中说 The fox is clever。"),
])
r(PB, U3, "A: Can birds fly? B: Yes, they can. A: Can fish fly? B: No, they can't. They swim.", [
    ("Can birds fly?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, they can。"),
    ("What do fish do?", ["Swim", "Fly", "Run", "Climb"], "0", "B 说 They swim。"),
])
r(PB, U3, "Does the cat like fish? Yes, it does. Does the rabbit like carrots? Yes, it does. Animals like their food.", [
    ("Does the cat like fish?", ["Yes", "No", "Maybe", "Never"], "0", "文中说 Yes, it does。"),
    ("What does the rabbit like?", ["Carrots", "Fish", "Meat", "Grass only"], "0", "文中说 carrots。"),
])
r(PC, U3, "Amy feeds the fish in the pond. The fish are red and gold. They swim to her quickly. Amy laughs happily.", [
    ("What does Amy feed?", ["Fish", "Birds", "Cats", "Dogs"], "0", "文中说 Amy feeds the fish。"),
    ("How does Amy feel?", ["Happily", "Sadly", "Angrily", "Sleepily"], "0", "文中说 Amy laughs happily。"),
])
r(PC, U3, "Tom draws his favourite animal. It is a panda. It eats bamboo and climbs trees. Tom likes pandas very much.", [
    ("What is Tom's favourite animal?", ["Panda", "Tiger", "Monkey", "Dog"], "0", "文中说 It is a panda。"),
    ("What does the panda eat?", ["Bamboo", "Fish", "Meat", "Grass"], "0", "文中说 It eats bamboo。"),
])
r(PD, U3, "Letter Q q says /kw/. Queen starts with Q. Letter R r says /r/. Rabbit starts with R.", [
    ("What starts with Q?", ["Queen", "Rabbit", "Quilt", "Quick"], "0", "文中说 Queen starts with Q。"),
    ("What starts with R?", ["Queen", "Rabbit", "Queen", "Quiet"], "1", "文中说 Rabbit starts with R。"),
])
r(PD, U3, "We write letters in the sand. Big C and small c. Big D and small d. Writing letters is fun.", [
    ("Where do they write letters?", ["Sand", "Water", "Sky", "Book"], "0", "文中说 in the sand。"),
    ("How is writing letters?", ["Fun", "Boring", "Sad", "Hard only"], "0", "文中说 Writing letters is fun。"),
])

# ===== Unit 4 补: PA1 PB2 PC2 语音2 =====
r(PA, U4, "The garden has many flowers. Some are red. Some are yellow. Bees fly to the flowers. They are busy.", [
    ("What flies to the flowers?", ["Bees", "Fish", "Cats", "Dogs"], "0", "文中说 Bees fly to the flowers。"),
    ("How are the bees?", ["Busy", "Lazy", "Sad", "Slow"], "0", "文中说 They are busy。"),
])
r(PB, U4, "A: Is this a leaf? B: Yes, it is. A: What colour is it? B: It's green.", [
    ("Is it a leaf?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, it is。"),
    ("What colour is it?", ["Green", "Red", "Blue", "Black"], "0", "B 说 It's green。"),
])
r(PB, U4, "Do plants need water? Yes, they do. Do plants need sun? Yes, they do. Water and sun help plants grow.", [
    ("Do plants need water?", ["Yes", "No", "Maybe", "Never"], "0", "文中说 Yes, they do。"),
    ("What helps plants grow?", ["Water and sun", "Candy", "Toys", "Books"], "0", "文中说 Water and sun。"),
])
r(PC, U4, "In autumn, the leaves turn yellow. They fall from the trees. Lily picks up the leaves. She makes a leaf picture.", [
    ("What colour do leaves turn in autumn?", ["Yellow", "Green", "Blue", "Pink"], "0", "文中说 the leaves turn yellow。"),
    ("What does Lily make?", ["A leaf picture", "A flower", "A tree", "A song"], "0", "文中说 She makes a leaf picture。"),
])
r(PC, U4, "Mike waters the flowers in the morning. The flowers drink the water. They open their petals. Mike says good morning to them.", [
    ("When does Mike water the flowers?", ["Morning", "Night", "Noon", "Evening"], "0", "文中说 in the morning。"),
    ("What do the flowers open?", ["Petals", "Doors", "Books", "Bags"], "0", "文中说 They open their petals。"),
])
r(PD, U4, "Letter U u says /ʌ/. Umbrella starts with U. Letter V v says /v/. Van starts with V.", [
    ("What starts with U?", ["Umbrella", "Van", "Up", "Us"], "0", "文中说 Umbrella starts with U。"),
    ("What starts with V?", ["Umbrella", "Van", "Vet", "Very"], "1", "文中说 Van starts with V。"),
])
r(PD, U4, "Look at letter W w. It says /w/. Water starts with W. Look at letter X x. It says /ks/. Box starts with X.", [
    ("What starts with W?", ["Water", "Box", "Wet", "Win"], "0", "文中说 Water starts with W。"),
    ("What starts with X?", ["Water", "Box", "Wet", "Wall"], "1", "文中说 Box starts with X。"),
])

# ===== Unit 5 补: PA1 PB2 PC2 语音2 =====
r(PA, U5, "My schoolbag is blue. My pencil case is white. My ruler is yellow. I like my colourful things.", [
    ("What colour is the schoolbag?", ["Blue", "Red", "Green", "Black"], "0", "文中说 My schoolbag is blue。"),
    ("What colour is the ruler?", ["Yellow", "Blue", "White", "Purple"], "0", "文中说 My ruler is yellow。"),
])
r(PB, U5, "A: Is the flower pink? B: No, it isn't. It's purple. A: Oh, purple is nice.", [
    ("Is the flower pink?", ["No", "Yes", "Maybe", "Never"], "0", "B 说 No, it isn't。"),
    ("What colour is it?", ["Purple", "Pink", "Red", "Blue"], "0", "B 说 It's purple。"),
])
r(PB, U5, "What colour is the night sky? It is dark blue. What colour are the stars? They are bright yellow.", [
    ("What colour is the night sky?", ["Dark blue", "Red", "Green", "White"], "0", "文中说 It is dark blue。"),
    ("What colour are the stars?", ["Bright yellow", "Blue", "Black", "Green"], "0", "文中说 bright yellow。"),
])
r(PC, U5, "Lily has a red dress. She wears it to the party. Everyone says she looks nice. Lily is so happy.", [
    ("What colour is Lily's dress?", ["Red", "Blue", "Green", "Yellow"], "0", "文中说 a red dress。"),
    ("Where does she wear it?", ["Party", "School", "Farm", "Zoo"], "0", "文中说 to the party。"),
])
r(PC, U5, "Tom and Sam paint a wall. Tom uses blue. Sam uses green. The wall looks like a forest. They are proud.", [
    ("What colour does Tom use?", ["Blue", "Green", "Red", "Black"], "0", "文中说 Tom uses blue。"),
    ("What does the wall look like?", ["A forest", "A sea", "A sky", "A house"], "0", "文中说 like a forest。"),
])
r(PD, U5, "Letter Y y says /j/. Yellow starts with Y. Letter Z z says /z/. Zoo starts with Z.", [
    ("What starts with Y?", ["Yellow", "Zoo", "Yes", "You"], "0", "文中说 Yellow starts with Y。"),
    ("What starts with Z?", ["Yellow", "Zoo", "Yam", "Yak"], "1", "文中说 Zoo starts with Z。"),
])
r(PD, U5, "We learn all the letters now. From A to Z. We can read simple words. Letters are magic keys.", [
    ("What can they do now?", ["Read simple words", "Fly", "Swim fast", "Cook"], "0", "文中说 We can read simple words。"),
    ("What are letters like?", ["Magic keys", "Heavy stones", "Cold ice", "Old shoes"], "0", "文中说 Letters are magic keys。"),
])

# ===== Unit 6 补: PA1 PB2 PC2 语音2 =====
r(PA, U6, "There are seven days in a week. I go to school for five days. I rest for two days. I love weekends.", [
    ("How many days in a week?", ["Seven", "Five", "Two", "Ten"], "0", "文中说 seven days。"),
    ("How many days does the writer rest?", ["Two", "Five", "Seven", "One"], "0", "文中说 rest for two days。"),
])
r(PB, U6, "A: How many legs does a dog have? B: It has four legs. A: How many legs does a bird have? B: It has two legs.", [
    ("How many legs does a dog have?", ["Four", "Two", "Six", "Eight"], "0", "B 说 four legs。"),
    ("How many legs does a bird have?", ["Two", "Four", "Three", "One"], "0", "B 说 two legs。"),
])
r(PB, U6, "A: What's five and five? B: It's ten. A: What's ten and zero? B: It's still ten.", [
    ("What is five and five?", ["Ten", "Eight", "Nine", "Eleven"], "0", "B 说 It's ten。"),
    ("What is ten and zero?", ["Ten", "Zero", "One", "Eleven"], "0", "B 说 It's still ten。"),
])
r(PC, U6, "Mum buys six eggs. Lily helps count them. One, two, three, four, five, six. They make a cake with the eggs.", [
    ("How many eggs does Mum buy?", ["Six", "Four", "Eight", "Ten"], "0", "文中说 six eggs。"),
    ("What do they make?", ["A cake", "Bread", "Soup", "Rice"], "0", "文中说 make a cake。"),
])
r(PC, U6, "There are nine players on the team. Three are girls. Six are boys. They play together and win the game.", [
    ("How many players in the team?", ["Nine", "Six", "Three", "Twelve"], "0", "文中说 nine players。"),
    ("What do they do at last?", ["Win the game", "Lose the game", "Go home", "Sleep"], "0", "文中说 win the game。"),
])
r(PD, U6, "Number 5 looks like a hook. Number 6 looks like a whistle. We draw numbers in the air.", [
    ("What does 5 look like?", ["A hook", "A whistle", "A ball", "A cup"], "0", "文中说 5 looks like a hook。"),
    ("What does 6 look like?", ["A whistle", "A hook", "A stick", "A ring"], "0", "文中说 6 looks like a whistle。"),
])
r(PD, U6, "We count with our fingers. One to ten. Then we clap our hands. Counting and clapping is fun.", [
    ("What do they count with?", ["Fingers", "Toes", "Books", "Pens"], "0", "文中说 with our fingers。"),
    ("What do they do then?", ["Clap hands", "Sleep", "Eat", "Cry"], "0", "文中说 we clap our hands。"),
])

# 合并写回
main = json.load(open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_upper.json", encoding="utf-8"))
main.extend(Q)
with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_upper.json", "w", encoding="utf-8") as f:
    json.dump(main, f, ensure_ascii=False, indent=2)
print(f"补充 {len(Q)} 篇，上册合计 {len(main)} 篇")

d = defaultdict(Counter)
for q in main:
    d[q['unit']][q['topic_name']] += 1
units = sorted(d.keys())
parts = ['Part A 词汇','Part B 句型','Part C 对话','字母与语音']
for u in units:
    line = ' | '.join(f'{p}:{d[u].get(p,0)}' for p in parts)
    print(f'{u}: {line}')
