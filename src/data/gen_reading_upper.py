# -*- coding: utf-8 -*-
"""英语三年级上册阅读理解题：6单元 x 4课时 x 5篇 = 120篇
每篇含 2 个 choice 子题。主题贴合人教PEP 2024 单元。
输出 english_reading_upper.json"""
import json

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

# ===== Unit 1 Making friends =====
r(PA, U1, "Hello! My name is Mike. I am a boy. I am nine. I like to make friends. Nice to meet you!", [
    ("What is the boy's name?", ["Tom", "Mike", "John", "Sam"], "1", "文中说 My name is Mike。"),
    ("How old is Mike?", ["Eight", "Ten", "Nine", "Seven"], "2", "文中说 I am nine。"),
])
r(PA, U1, "This is my new friend. Her name is Lily. She is a girl. She is nice. We play together.", [
    ("What is the girl's name?", ["Lily", "Lucy", "Amy", "Ann"], "0", "文中说 Her name is Lily。"),
    ("Is Lily nice?", ["Yes", "No", "I don't know", "Maybe"], "0", "文中说 She is nice。"),
])
r(PA, U1, "Good morning! I am Zhang Peng. This is my friend Li Ming. We are in Class One.", [
    ("Who is Zhang Peng's friend?", ["Li Ming", "Wang Lei", "Chen Jie", "Mike"], "0", "文中说 This is my friend Li Ming。"),
    ("When does the story happen?", ["Evening", "Morning", "Night", "Noon"], "1", "开头说 Good morning。"),
])
r(PB, U1, "A: What's your name? B: My name is Sarah. A: Nice to meet you. B: Nice to meet you, too.", [
    ("What is B's name?", ["Sarah", "Emma", "Lisa", "Kate"], "0", "B 说 My name is Sarah。"),
    ("What do they say to each other?", ["Goodbye", "Nice to meet you", "See you", "Good night"], "1", "他们都说了 Nice to meet you。"),
])
r(PB, U1, "Are you a boy or a girl? I am a girl. My friend is a boy. We are good friends.", [
    ("What is the speaker?", ["A boy", "A girl", "A teacher", "A baby"], "1", "文中说 I am a girl。"),
    ("What is the speaker's friend?", ["A girl", "A dog", "A boy", "A cat"], "2", "文中说 My friend is a boy。"),
])
r(PC, U1, "Mike: Hello, I'm Mike. What's your name? Lily: I'm Lily. Mike: Let's be friends! Lily: Great!", [
    ("What does Mike want?", ["Food", "To be friends", "A toy", "Water"], "1", "Mike 说 Let's be friends。"),
    ("How does Lily feel?", ["Great", "Sad", "Angry", "Tired"], "0", "Lily 说 Great。"),
])
r(PC, U1, "Tom: Hi! My name is Tom. Sam: Hi, I'm Sam. Tom: How are you? Sam: I'm fine, thank you.", [
    ("What are the two boys?", ["Brothers", "Friends meeting", "Teacher and student", "Father and son"], "1", "两个男孩在互相问好、交朋友。"),
    ("How is Sam?", ["Fine", "Sad", "Sick", "Hungry"], "0", "Sam 说 I'm fine。"),
])
r(PD, U1, "M m is for make. N n is for name. We say hello. We say hi. We make new friends.", [
    ("What letter is for 'make'?", ["M m", "N n", "A a", "B b"], "0", "文中说 M m is for make。"),
    ("What letter is for 'name'?", ["M m", "N n", "O o", "P p"], "1", "文中说 N n is for name。"),
])
r(PD, U1, "Look at the big letter M m. Now look at the small letter n. M is big, n is small. We learn letters.", [
    ("Which letter is big?", ["M", "n", "o", "p"], "0", "文中说 M is big。"),
    ("Which letter is small?", ["M", "n", "m", "N"], "1", "文中说 n is small。"),
])
r(PA, U1, "I have two friends. One is a boy. One is a girl. The boy is tall. The girl is short. We are happy.", [
    ("How many friends does the writer have?", ["One", "Two", "Three", "Four"], "1", "文中说 I have two friends。"),
    ("What is the girl like?", ["Tall", "Short", "Big", "Fat"], "1", "文中说 The girl is short。"),
])
r(PB, U1, "This is my friend. He is from China. His name is Chen Jie. I am from China, too.", [
    ("Where is Chen Jie from?", ["China", "USA", "UK", "Canada"], "0", "文中说 He is from China。"),
    ("What is the boy's name?", ["Chen Jie", "Mike", "Tom", "Jack"], "0", "文中说 His name is Chen Jie。"),
])
r(PC, U1, "At school, I meet a new girl. She says hi to me. I say hi back. Now we talk and laugh together.", [
    ("Where does the writer meet the girl?", ["At school", "At home", "In the park", "In the zoo"], "0", "文中说 At school。"),
    ("What do they do together?", ["Talk and laugh", "Sleep", "Cry", "Fight"], "0", "文中说 we talk and laugh together。"),
])
r(PD, U1, "The letter A a says /a/. Apple starts with A. The letter B b says /b/. Boy starts with B.", [
    ("What starts with A?", ["Apple", "Banana", "Cat", "Dog"], "0", "文中说 Apple starts with A。"),
    ("What starts with B?", ["Apple", "Boy", "Ant", "Egg"], "1", "文中说 Boy starts with B。"),
])

# ===== Unit 2 Different families =====
r(PA, U2, "This is my family. I have a father and a mother. My father is tall. My mother is kind. I love my family.", [
    ("How many parents does the writer have?", ["One", "Two", "Three", "Four"], "1", "文中说有 father 和 mother 两位。"),
    ("What is the mother like?", ["Kind", "Angry", "Sad", "Small"], "0", "文中说 My mother is kind。"),
])
r(PA, U2, "This is my brother. He is ten. This is my sister. She is six. We are a happy family.", [
    ("How old is the brother?", ["Six", "Ten", "Eight", "Nine"], "1", "文中说 He is ten。"),
    ("How old is the sister?", ["Ten", "Seven", "Six", "Five"], "2", "文中说 She is six。"),
])
r(PA, U2, "I have a big family. There is my grandpa, my grandma, my father, my mother and me.", [
    ("Is the family big or small?", ["Big", "Small", "One", "Empty"], "0", "文中说 I have a big family。"),
    ("Who is NOT in the family?", ["Grandpa", "Grandma", "Uncle", "Mother"], "2", "文中没有提到 uncle。"),
])
r(PB, U2, "A: Who is he? B: He is my father. A: Who is she? B: She is my mother.", [
    ("Who is 'he'?", ["Mother", "Father", "Sister", "Friend"], "1", "B 说 He is my father。"),
    ("Who is 'she'?", ["Father", "Brother", "Mother", "Aunt"], "2", "B 说 She is my mother。"),
])
r(PB, U2, "Is this your sister? No, it is not. This is my cousin. My sister is over there.", [
    ("Is it the writer's sister?", ["Yes", "No", "Maybe", "I don't know"], "1", "文中说 No, it is not。"),
    ("Who is it?", ["Cousin", "Sister", "Mother", "Aunt"], "0", "文中说 This is my cousin。"),
])
r(PC, U2, "Amy: Look, this is my family photo. Mike: Who is the man? Amy: He is my grandpa.", [
    ("What does Amy show?", ["A photo", "A book", "A toy", "A bag"], "0", "Amy 说 this is my family photo。"),
    ("Who is the man?", ["Grandpa", "Father", "Brother", "Uncle"], "0", "Amy 说 He is my grandpa。"),
])
r(PC, U2, "Sam shows his family to Lily. The woman is his mother. The girl is his sister. Lily says they are nice.", [
    ("Who is the woman?", ["Sister", "Mother", "Aunt", "Grandma"], "1", "文中说 The woman is his mother。"),
    ("What does Lily say?", ["They are nice", "They are sad", "They are tall", "They are old"], "0", "Lily 说 they are nice。"),
])
r(PD, U2, "F f is for father. M m is for mother. Father, mother, I love you. Family is happy.", [
    ("What letter is for father?", ["F f", "M m", "D d", "S s"], "0", "文中说 F f is for father。"),
    ("What letter is for mother?", ["F f", "M m", "B b", "G g"], "1", "文中说 M m is for mother。"),
])
r(PD, U2, "Look at letter G g. It says /g/. Girl starts with G. Look at letter H h. It says /h/. Home starts with H.", [
    ("What starts with G?", ["Girl", "Home", "Hat", "Hand"], "0", "文中说 Girl starts with G。"),
    ("What starts with H?", ["Girl", "Goat", "Home", "Game"], "2", "文中说 Home starts with H。"),
])
r(PA, U2, "My family has five people. Father, mother, brother, sister and me. We eat dinner together.", [
    ("How many people are in the family?", ["Three", "Four", "Five", "Six"], "2", "文中说 five people。"),
    ("What do they do together?", ["Eat dinner", "Play ball", "Swim", "Sing"], "0", "文中说 We eat dinner together。"),
])
r(PB, U2, "This is my mother. She is a teacher. This is my father. He is a doctor. I love them.", [
    ("What is the mother's job?", ["Doctor", "Teacher", "Nurse", "Farmer"], "1", "文中说 She is a teacher。"),
    ("What is the father's job?", ["Teacher", "Doctor", "Driver", "Cook"], "1", "文中说 He is a doctor。"),
])
r(PC, U2, "On Sunday, my family goes to the park. Father plays ball. Mother reads a book. I run and jump.", [
    ("When do they go to the park?", ["Sunday", "Monday", "Friday", "Night"], "0", "文中说 On Sunday。"),
    ("What does mother do?", ["Plays ball", "Reads a book", "Runs", "Swims"], "1", "文中说 Mother reads a book。"),
])

# ===== Unit 3 Amazing animals =====
r(PA, U3, "I like animals. This is a dog. It is friendly. This is a cat. It is cute. They are my pets.", [
    ("What is friendly?", ["Cat", "Dog", "Bird", "Fish"], "1", "文中说 dog is friendly。"),
    ("What is cute?", ["Dog", "Cat", "Pig", "Cow"], "1", "文中说 cat is cute。"),
])
r(PA, U3, "Look at the panda. It is black and white. It eats bamboo. Look at the monkey. It likes bananas.", [
    ("What colour is the panda?", ["Black and white", "Red", "Blue", "Green"], "0", "文中说 It is black and white。"),
    ("What does the monkey like?", ["Bamboo", "Bananas", "Grass", "Fish"], "1", "文中说 It likes bananas。"),
])
r(PA, U3, "The bird can fly. The fish can swim. The rabbit can jump. Animals are amazing.", [
    ("What can the bird do?", ["Swim", "Fly", "Jump", "Run"], "1", "文中说 The bird can fly。"),
    ("What can the fish do?", ["Fly", "Jump", "Swim", "Climb"], "2", "文中说 The fish can swim。"),
])
r(PB, U3, "A: What's this? B: It's an elephant. A: Wow, it's so big! B: Yes, it has a long nose.", [
    ("What animal is it?", ["Elephant", "Tiger", "Horse", "Bear"], "0", "B 说 It's an elephant。"),
    ("What does the elephant have?", ["Long nose", "Short tail", "Small eyes", "Big ears only"], "0", "文中说 it has a long nose。"),
])
r(PB, U3, "Do you like ducks? Yes, I do. They can swim. Do you like pigs? No, I don't.", [
    ("Does the writer like ducks?", ["Yes", "No", "Maybe", "I don't know"], "0", "文中说 Yes, I do。"),
    ("What can ducks do?", ["Fly high", "Swim", "Climb", "Sing"], "1", "文中说 They can swim。"),
])
r(PC, U3, "Tom goes to the zoo. He sees a tiger. The tiger is strong. He sees a giraffe. It is very tall.", [
    ("Where does Tom go?", ["Zoo", "School", "Home", "Shop"], "0", "文中说 Tom goes to the zoo。"),
    ("What is the giraffe like?", ["Very tall", "Small", "Short", "Fat"], "0", "文中说 It is very tall。"),
])
r(PC, U3, "Lily has a little dog. It is white. It can run fast. Lily plays with it every day. They are good friends.", [
    ("What colour is the dog?", ["White", "Black", "Brown", "Red"], "0", "文中说 It is white。"),
    ("When does Lily play with it?", ["Every day", "Never", "Once a year", "Only Sunday"], "0", "文中说 every day。"),
])
r(PD, U3, "D d is for dog. C c is for cat. The letter D says /d/. The letter C says /k/.", [
    ("What letter is for dog?", ["D d", "C c", "B b", "P p"], "0", "文中说 D d is for dog。"),
    ("What letter is for cat?", ["D d", "C c", "T t", "K k"], "1", "文中说 C c is for cat。"),
])
r(PD, U3, "Look at letter I i. It says /i/. Pig starts with I. Look at letter J j. It says /dʒ/. Juice starts with J.", [
    ("What starts with I?", ["Pig", "Juice", "Jam", "Jet"], "0", "文中说 Pig starts with I。"),
    ("What starts with J?", ["Pig", "Ice", "Juice", "Ink"], "2", "文中说 Juice starts with J。"),
])
r(PA, U3, "At the farm, I see many animals. There are cows, sheep and horses. The horses can run very fast.", [
    ("Where is the writer?", ["Zoo", "Farm", "Park", "School"], "1", "文中说 At the farm。"),
    ("What can the horses do?", ["Swim", "Fly", "Run fast", "Climb"], "2", "文中说 The horses can run very fast。"),
])
r(PB, U3, "A bird is in the tree. A fish is in the water. A rabbit is on the grass. Where is the cat? It is on the sofa.", [
    ("Where is the bird?", ["Water", "Tree", "Grass", "Sofa"], "1", "文中说 A bird is in the tree。"),
    ("Where is the cat?", ["Sofa", "Tree", "Water", "Grass"], "0", "文中说 It is on the sofa。"),
])
r(PC, U3, "Mike wants a pet. He likes dogs. Dogs are friendly and smart. His mother says yes. Mike is very happy.", [
    ("What pet does Mike want?", ["Cat", "Dog", "Bird", "Fish"], "1", "文中说 He likes dogs。"),
    ("How does Mike feel?", ["Very happy", "Sad", "Angry", "Tired"], "0", "文中说 Mike is very happy。"),
])

# ===== Unit 4 Plants around us =====
r(PA, U4, "I like plants. This is a tree. It is tall. This is a flower. It is beautiful. Plants make our world green.", [
    ("What is tall?", ["Flower", "Tree", "Grass", "Leaf"], "1", "文中说 tree is tall。"),
    ("What is beautiful?", ["Tree", "Flower", "Stone", "Rock"], "1", "文中说 flower is beautiful。"),
])
r(PA, U4, "Look at the apple tree. It has many apples. Look at the leaf. It is green. The plants are nice.", [
    ("What does the tree have?", ["Apples", "Birds", "Cats", "Books"], "0", "文中说 It has many apples。"),
    ("What colour is the leaf?", ["Red", "Green", "Blue", "Yellow"], "1", "文中说 It is green。"),
])
r(PA, U4, "The seed grows into a plant. The plant needs water and sun. Then it has leaves and flowers.", [
    ("What does the plant need?", ["Water and sun", "Meat", "Milk", "Candy"], "0", "文中说 The plant needs water and sun。"),
    ("What does the seed become?", ["A plant", "A stone", "A toy", "A ball"], "0", "文中说 The seed grows into a plant。"),
])
r(PB, U4, "A: What's this? B: It's a flower. A: What colour is it? B: It's red.", [
    ("What is it?", ["A flower", "A tree", "A leaf", "A fruit"], "0", "B 说 It's a flower。"),
    ("What colour is it?", ["Red", "Blue", "Green", "Black"], "0", "B 说 It's red。"),
])
r(PB, U4, "Do you like plants? Yes, I do. I water the flowers every day. They grow very well.", [
    ("Does the writer like plants?", ["Yes", "No", "Maybe", "Never"], "0", "文中说 Yes, I do。"),
    ("What does the writer do every day?", ["Waters the flowers", "Cuts the tree", "Eats fruit", "Plays ball"], "0", "文中说 I water the flowers every day。"),
])
r(PC, U4, "In spring, the trees turn green. The flowers start to open. The birds sing in the trees. Spring is beautiful.", [
    ("What colour do trees turn in spring?", ["Green", "White", "Black", "Brown"], "0", "文中说 the trees turn green。"),
    ("What do the birds do?", ["Sing", "Sleep", "Swim", "Cry"], "0", "文中说 The birds sing。"),
])
r(PC, U4, "Lily plants a seed in the garden. She waters it every day. Soon a small plant grows. Lily is so happy.", [
    ("Where does Lily plant the seed?", ["Garden", "Room", "Kitchen", "Zoo"], "0", "文中说 in the garden。"),
    ("What grows soon?", ["A small plant", "A big tree", "A dog", "A rock"], "0", "文中说 a small plant grows。"),
])
r(PD, U4, "K k is for kite. L l is for leaf. The letter K says /k/. The letter L says /l/.", [
    ("What letter is for kite?", ["K k", "L l", "M m", "N n"], "0", "文中说 K k is for kite。"),
    ("What letter is for leaf?", ["K k", "L l", "P p", "Q q"], "1", "文中说 L l is for leaf。"),
])
r(PD, U4, "Look at letter O o. It says /ɒ/. Orange starts with O. Look at letter P p. It says /p/. Pen starts with P.", [
    ("What starts with O?", ["Orange", "Pen", "Pig", "Pot"], "0", "文中说 Orange starts with O。"),
    ("What starts with P?", ["Orange", "Pen", "Octopus", "Owl"], "1", "文中说 Pen starts with P。"),
])
r(PA, U4, "There are many plants in the park. Trees, flowers and grass. The grass is soft. The flowers smell nice.", [
    ("What is soft?", ["Tree", "Grass", "Stone", "Flower"], "1", "文中说 The grass is soft。"),
    ("How do the flowers smell?", ["Nice", "Bad", "Cold", "Hot"], "0", "文中说 The flowers smell nice。"),
])
r(PB, U4, "This is a big tree. It has green leaves. This is a small flower. It has red petals. I like them both.", [
    ("What does the tree have?", ["Green leaves", "Red petals", "Blue fruit", "Yellow flowers"], "0", "文中说 It has green leaves。"),
    ("What does the flower have?", ["Red petals", "Green leaves", "Long roots", "Big seeds"], "0", "文中说 It has red petals。"),
])
r(PC, U4, "Tom and his father go to the garden. They plant flowers together. Tom learns to water them. He loves plants now.", [
    ("Who goes to the garden with Tom?", ["Mother", "Father", "Sister", "Friend"], "1", "文中说 Tom and his father。"),
    ("What does Tom learn to do?", ["Water them", "Cut them", "Eat them", "Sell them"], "0", "文中说 Tom learns to water them。"),
])

# ===== Unit 5 The colourful world =====
r(PA, U5, "The world is colourful. The sky is blue. The grass is green. The sun is yellow. I love colours.", [
    ("What colour is the sky?", ["Blue", "Red", "Green", "Black"], "0", "文中说 The sky is blue。"),
    ("What colour is the sun?", ["Yellow", "Blue", "Purple", "White"], "0", "文中说 The sun is yellow。"),
])
r(PA, U5, "I see many colours. Red, blue, green, yellow, orange and purple. The rainbow has all these colours.", [
    ("What has all these colours?", ["Rainbow", "Book", "Car", "House"], "0", "文中说 The rainbow has all these colours。"),
    ("Is blue one of the colours?", ["Yes", "No", "Maybe", "Never"], "0", "文中列出了 blue。"),
])
r(PA, U5, "My favourite colour is red. My bag is red. My pen is red, too. Red is a warm colour.", [
    ("What is the favourite colour?", ["Red", "Blue", "Green", "Black"], "0", "文中说 My favourite colour is red。"),
    ("What is red too?", ["Bag and pen", "Shoe and hat", "Book and desk", "Chair and door"], "0", "文中说 bag 和 pen 都是红色。"),
])
r(PB, U5, "A: What colour is the apple? B: It's red. A: What colour is the banana? B: It's yellow.", [
    ("What colour is the apple?", ["Red", "Blue", "Green", "Purple"], "0", "B 说 It's red。"),
    ("What colour is the banana?", ["Yellow", "Red", "Black", "White"], "0", "B 说 It's yellow。"),
])
r(PB, U5, "Do you like blue? Yes, I do. The sea is blue. Do you like green? Yes, the trees are green.", [
    ("What is blue?", ["Sea", "Tree", "Sun", "Apple"], "0", "文中说 The sea is blue。"),
    ("What colour are the trees?", ["Green", "Red", "Blue", "Yellow"], "0", "文中说 the trees are green。"),
])
r(PC, U5, "Lily draws a picture. She uses red, blue and yellow. Her picture is a garden. It is very beautiful.", [
    ("What does Lily draw?", ["A garden", "A dog", "A car", "A house"], "0", "文中说 Her picture is a garden。"),
    ("How is her picture?", ["Beautiful", "Ugly", "Small", "Dark"], "0", "文中说 It is very beautiful。"),
])
r(PC, U5, "After the rain, Mike sees a rainbow. It has many colours. Red, orange, yellow, green, blue and purple. He is so happy.", [
    ("What does Mike see after the rain?", ["Rainbow", "Cloud", "Storm", "Snow"], "0", "文中说 Mike sees a rainbow。"),
    ("How does Mike feel?", ["So happy", "Sad", "Angry", "Scared"], "0", "文中说 He is so happy。"),
])
r(PD, U5, "R r is for red. G g is for green. The letter R says /r/. The letter G says /g/.", [
    ("What letter is for red?", ["R r", "G g", "B b", "Y y"], "0", "文中说 R r is for red。"),
    ("What letter is for green?", ["R r", "G g", "P p", "O o"], "1", "文中说 G g is for green。"),
])
r(PD, U5, "Look at letter S s. It says /s/. Sun starts with S. Look at letter T t. It says /t/. Tree starts with T.", [
    ("What starts with S?", ["Sun", "Tree", "Top", "Ten"], "0", "文中说 Sun starts with S。"),
    ("What starts with T?", ["Sun", "Tree", "See", "Sit"], "1", "文中说 Tree starts with T。"),
])
r(PA, U5, "I have a box of crayons. There are twelve colours. I draw a blue sea and a yellow sun. My picture is nice.", [
    ("How many colours are there?", ["Ten", "Twelve", "Five", "Eight"], "1", "文中说 twelve colours。"),
    ("What colour is the sea in the picture?", ["Blue", "Red", "Green", "Black"], "0", "文中说 a blue sea。"),
])
r(PB, U5, "The traffic light has three colours. Red means stop. Green means go. Yellow means wait. We must follow it.", [
    ("What does red mean?", ["Go", "Stop", "Wait", "Run"], "1", "文中说 Red means stop。"),
    ("What does green mean?", ["Stop", "Go", "Wait", "Sleep"], "1", "文中说 Green means go。"),
])
r(PC, U5, "Amy and Lily colour a picture together. Amy uses pink. Lily uses blue. They show it to their teacher. The teacher says well done.", [
    ("What colour does Amy use?", ["Pink", "Blue", "Green", "Red"], "0", "文中说 Amy uses pink。"),
    ("What does the teacher say?", ["Well done", "Bad", "Stop", "Go away"], "0", "文中说 The teacher says well done。"),
])

# ===== Unit 6 Useful numbers =====
r(PA, U6, "I can count. One, two, three, four, five. Numbers are useful. We use numbers every day.", [
    ("What can the writer do?", ["Count", "Swim", "Fly", "Cook"], "0", "文中说 I can count。"),
    ("When do we use numbers?", ["Every day", "Never", "Once a year", "Only Sunday"], "0", "文中说 We use numbers every day。"),
])
r(PA, U6, "There are six apples on the tree. I pick two. Now there are four apples left. Numbers help me count them.", [
    ("How many apples are left?", ["Two", "Four", "Six", "Eight"], "1", "文中说 there are four apples left。"),
    ("How many apples does the writer pick?", ["Two", "Four", "Three", "One"], "0", "文中说 I pick two。"),
])
r(PA, U6, "I have ten fingers. I have two hands. Each hand has five fingers. I use my fingers to count.", [
    ("How many fingers does the writer have?", ["Five", "Ten", "Two", "Eight"], "1", "文中说 I have ten fingers。"),
    ("How many fingers does each hand have?", ["Five", "Ten", "Three", "Four"], "0", "文中说 Each hand has five fingers。"),
])
r(PB, U6, "A: How many books? B: I have three books. A: How many pens? B: I have two pens.", [
    ("How many books does B have?", ["Three", "Two", "Four", "One"], "0", "B 说 I have three books。"),
    ("How many pens does B have?", ["Two", "Three", "Five", "Six"], "0", "B 说 I have two pens。"),
])
r(PB, U6, "A: What's this number? B: It's seven. A: What's one and two? B: It's three.", [
    ("What is the number?", ["Seven", "Five", "Nine", "Four"], "0", "B 说 It's seven。"),
    ("What is one and two?", ["Three", "Four", "Two", "Five"], "0", "B 说 It's three。"),
])
r(PC, U6, "Mike has five toy cars. Tom gives him two more. Now Mike has seven cars. He is very happy.", [
    ("How many cars does Mike have at last?", ["Five", "Seven", "Two", "Three"], "1", "5+2=7，文中说 seven cars。"),
    ("Who gives Mike more cars?", ["Tom", "Lily", "Amy", "Sam"], "0", "文中说 Tom gives him two more。"),
])
r(PC, U6, "There are eight birds in the tree. Three fly away. Now there are five birds left. We count them together.", [
    ("How many birds are left?", ["Five", "Eight", "Three", "Two"], "0", "8-3=5，文中说 five birds left。"),
    ("How many birds fly away?", ["Three", "Five", "Eight", "One"], "0", "文中说 Three fly away。"),
])
r(PD, U6, "The number 1 looks like a stick. The number 2 looks like a duck. We learn to write numbers.", [
    ("What does 1 look like?", ["A stick", "A duck", "A ball", "A cat"], "0", "文中说 1 looks like a stick。"),
    ("What does 2 look like?", ["A stick", "A duck", "A tree", "A sun"], "1", "文中说 2 looks like a duck。"),
])
r(PD, U6, "Let's write number 3 and 4. Number 3 has two curves. Number 4 has straight lines. Writing numbers is fun.", [
    ("How many curves does 3 have?", ["Two", "One", "Three", "Four"], "0", "文中说 Number 3 has two curves。"),
    ("What does number 4 have?", ["Straight lines", "Circles", "Curves only", "Dots"], "0", "文中说 Number 4 has straight lines。"),
])
r(PA, U6, "I see four birds and two cats. That is six animals in all. I can add them up. Numbers are fun.", [
    ("How many animals in all?", ["Four", "Six", "Two", "Eight"], "1", "4+2=6，文中说 six animals。"),
    ("How many cats are there?", ["Two", "Four", "Six", "Three"], "0", "文中说 two cats。"),
])
r(PB, U6, "A: How old are you? B: I'm nine. A: How many candles? B: There are nine candles on my cake.", [
    ("How old is B?", ["Nine", "Eight", "Ten", "Seven"], "0", "B 说 I'm nine。"),
    ("How many candles are on the cake?", ["Nine", "Eight", "Six", "Five"], "0", "B 说 nine candles。"),
])
r(PC, U6, "Sam buys three apples and four oranges. He puts them in his bag. He has seven fruits now. He shares them with friends.", [
    ("How many fruits does Sam have?", ["Three", "Four", "Seven", "Ten"], "2", "3+4=7，文中说 seven fruits。"),
    ("What does Sam do with the fruits?", ["Shares with friends", "Throws away", "Sells them", "Hides them"], "0", "文中说 He shares them with friends。"),
])

with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_upper.json", "w", encoding="utf-8") as f:
    json.dump(Q, f, ensure_ascii=False, indent=2)
from collections import Counter
print(f"上册共 {len(Q)} 篇")
print("单元分布:", dict(Counter(q['unit'] for q in Q)))
print("课时分布:", dict(Counter(q['topic_name'] for q in Q)))
