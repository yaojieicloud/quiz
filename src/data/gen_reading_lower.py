# -*- coding: utf-8 -*-
"""英语三年级下册阅读理解题：6单元 x 4课时 x 5篇 = 120篇
每篇含 2 个 choice 子题。主题贴合人教PEP 2024 下册单元。
输出 english_reading_lower.json"""
import json

Q = []

def r(topic, unit, content, pairs, diff=1):
    items = [{"type": "choice", "q": q, "options": opts, "answer": str(ans), "explanation": expl}
             for q, opts, ans, expl in pairs]
    Q.append({
        "type": "reading", "topic_name": topic, "unit": unit,
        "content": content, "options": None, "reading_items": items,
        "answer": ",".join(it["answer"] for it in items),
        "explanation": "", "difficulty": diff,
    })

U1 = "下册-Unit 1 Meeting new people"
U2 = "下册-Unit 2 Expressing yourself"
U3 = "下册-Unit 3 Learning better"
U4 = "下册-Unit 4 Healthy food"
U5 = "下册-Unit 5 Old toys"
U6 = "下册-Unit 6 Numbers in life"
PA, PB, PC, PD = "Part A 词汇", "Part B 句型", "Part C 对话", "拼读与语音"

# ===== Unit 1 Meeting new people =====
r(PA, U1, "Hello, everyone! My name is Li Ming. I am nine years old. I am from China. Nice to meet you all!", [
    ("What is the boy's name?", ["Li Ming", "Wang Lei", "Chen Jie", "Zhang Peng"], "0", "文中说 My name is Li Ming。"),
    ("Where is he from?", ["China", "USA", "UK", "Canada"], "0", "文中说 I am from China。"),
])
r(PA, U1, "This is my new classmate. Her name is Amy. She is from the USA. She is friendly and kind.", [
    ("What is the girl's name?", ["Amy", "Lily", "Emma", "Lucy"], "0", "文中说 Her name is Amy。"),
    ("Where is Amy from?", ["USA", "China", "Canada", "UK"], "0", "文中说 She is from the USA。"),
])
r(PA, U1, "I have a new friend. He is tall. He has big eyes. His name is Sam. We sit together in class.", [
    ("What is Sam like?", ["Tall", "Short", "Small", "Old"], "0", "文中说 He is tall。"),
    ("Where do they sit?", ["Together in class", "Far away", "At home", "In the park"], "0", "文中说 We sit together in class。"),
])
r(PA, U1, "Our teacher is Miss White. She is from Canada. She is very nice. We all like her very much.", [
    ("Who is Miss White?", ["A teacher", "A student", "A doctor", "A cook"], "0", "文中说 Our teacher is Miss White。"),
    ("Where is she from?", ["Canada", "China", "USA", "UK"], "0", "文中说 She is from Canada。"),
])
r(PA, U1, "There are three new students in our class. One is from the UK. One is from the USA. One is from China.", [
    ("How many new students are there?", ["Three", "Two", "Four", "Five"], "0", "文中说 three new students。"),
    ("Is one from the UK?", ["Yes", "No", "Maybe", "Never"], "0", "文中说 One is from the UK。"),
])
r(PB, U1, "A: Where are you from? B: I'm from Beijing. A: Welcome! B: Thank you very much.", [
    ("Where is B from?", ["Beijing", "Shanghai", "London", "New York"], "0", "B 说 I'm from Beijing。"),
    ("What does B say at last?", ["Thank you very much", "Goodbye", "Sorry", "No thanks"], "0", "B 说 Thank you very much。"),
])
r(PB, U1, "A: Is she your new friend? B: Yes, she is. A: What's her name? B: Her name is Lily.", [
    ("Is she B's new friend?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, she is。"),
    ("What is her name?", ["Lily", "Amy", "Lucy", "Lisa"], "0", "B 说 Her name is Lily。"),
])
r(PB, U1, "A: How old are you? B: I'm nine. A: I'm nine, too. Let's be good friends. B: Great!", [
    ("How old is B?", ["Nine", "Eight", "Ten", "Seven"], "0", "B 说 I'm nine。"),
    ("What do they want to be?", ["Good friends", "Brothers", "Classmates only", "Strangers"], "0", "A 说 Let's be good friends。"),
])
r(PB, U1, "A: Who is that girl? B: She is my new classmate. A: She looks kind. B: Yes, she helps me a lot.", [
    ("Who is that girl?", ["B's new classmate", "B's sister", "A teacher", "A doctor"], "0", "B 说 She is my new classmate。"),
    ("What does she do for B?", ["Helps a lot", "Nothing", "Cries", "Sleeps"], "0", "B 说 she helps me a lot。"),
])
r(PB, U1, "A: Are you from Shanghai? B: No, I'm not. I'm from Hangzhou. A: Hangzhou is a beautiful city.", [
    ("Is B from Shanghai?", ["No", "Yes", "Maybe", "Never"], "0", "B 说 No, I'm not。"),
    ("Where is B from?", ["Hangzhou", "Shanghai", "Beijing", "Nanjing"], "0", "B 说 I'm from Hangzhou。"),
])
r(PC, U1, "On the first day, Mike feels shy. Then Amy says hello to him. They talk about their hobbies. Now Mike has a new friend.", [
    ("How does Mike feel at first?", ["Shy", "Happy", "Angry", "Loud"], "0", "文中说 Mike feels shy。"),
    ("Who says hello to him?", ["Amy", "Teacher", "Sam", "Lily"], "0", "文中说 Amy says hello to him。"),
])
r(PC, U1, "A new boy joins our class. He speaks English and Chinese. We teach him our games. He teaches us new words. We learn from each other.", [
    ("What languages does the boy speak?", ["English and Chinese", "Only English", "Only Chinese", "French"], "0", "文中说 English and Chinese。"),
    ("What do they do together?", ["Learn from each other", "Fight", "Sleep", "Cry"], "0", "文中说 We learn from each other。"),
])
r(PC, U1, "Lily meets a girl at the park. The girl is drawing pictures. Lily asks her name. They draw together and become friends.", [
    ("What is the girl doing?", ["Drawing pictures", "Swimming", "Running", "Singing"], "0", "文中说 The girl is drawing pictures。"),
    ("What do they do together?", ["Draw", "Eat", "Sleep", "Fight"], "0", "文中说 They draw together。"),
])
r(PC, U1, "Tom moves to a new school. He is worried at first. But his classmates are kind. They play with him every day. Tom loves his new school.", [
    ("How does Tom feel at first?", ["Worried", "Happy", "Angry", "Excited"], "0", "文中说 He is worried at first。"),
    ("How are his classmates?", ["Kind", "Mean", "Quiet", "Lazy"], "0", "文中说 his classmates are kind。"),
])
r(PC, U1, "At the party, we meet many new friends. We say our names and shake hands. We sing songs together. Everyone is happy.", [
    ("What do they do at the party?", ["Meet new friends", "Sleep", "Study only", "Cry"], "0", "文中说 we meet many new friends。"),
    ("How is everyone?", ["Happy", "Sad", "Angry", "Tired"], "0", "文中说 Everyone is happy。"),
])
r(PD, U1, "Letter A a says /æ/. Apple starts with A. Letter B b says /b/. Ball starts with B. We sing the ABC song.", [
    ("What starts with A?", ["Apple", "Ball", "Cat", "Dog"], "0", "文中说 Apple starts with A。"),
    ("What starts with B?", ["Apple", "Ball", "Ant", "Egg"], "1", "文中说 Ball starts with B。"),
])
r(PD, U1, "Letter C c says /k/. Cat starts with C. Letter D d says /d/. Dog starts with D. Letters are fun.", [
    ("What starts with C?", ["Cat", "Dog", "Cow", "Cup"], "0", "文中说 Cat starts with C。"),
    ("What starts with D?", ["Cat", "Dog", "Door", "Desk"], "1", "文中说 Dog starts with D。"),
])
r(PD, U1, "Look at the letter M m. Man starts with M. Look at the letter N n. Nose starts with N.", [
    ("What starts with M?", ["Man", "Nose", "Moon", "Mat"], "0", "文中说 Man starts with M。"),
    ("What starts with N?", ["Man", "Nose", "Net", "Nut"], "1", "文中说 Nose starts with N。"),
])
r(PD, U1, "The letter P p says /p/. Pig starts with P. The letter Q q says /kw/. Queen starts with Q.", [
    ("What starts with P?", ["Pig", "Queen", "Pen", "Pot"], "0", "文中说 Pig starts with P。"),
    ("What starts with Q?", ["Pig", "Queen", "Quiet", "Quick"], "1", "文中说 Queen starts with Q。"),
])
r(PD, U1, "We practise letters every day. Big letters and small letters. We write them neatly. Our teacher says well done.", [
    ("When do they practise letters?", ["Every day", "Never", "Once a year", "Only Sunday"], "0", "文中说 every day。"),
    ("What does the teacher say?", ["Well done", "Bad", "Stop", "Go away"], "0", "文中说 well done。"),
])

# ===== Unit 2 Expressing yourself =====
r(PA, U2, "I am a happy boy. I have short hair and big eyes. I like sports. I can run very fast.", [
    ("What is the boy like?", ["Happy", "Sad", "Angry", "Shy"], "0", "文中说 I am a happy boy。"),
    ("What can he do?", ["Run fast", "Fly", "Swim deep", "Sing well"], "0", "文中说 I can run very fast。"),
])
r(PA, U2, "This is me. I have long hair. I like drawing pictures. I draw flowers and birds every day.", [
    ("What does the girl have?", ["Long hair", "Short hair", "No hair", "A hat"], "0", "文中说 I have long hair。"),
    ("What does she like?", ["Drawing pictures", "Playing ball", "Swimming", "Cooking"], "0", "文中说 I like drawing pictures。"),
])
r(PA, U2, "My name is Tom. I am tall and thin. I like reading books. Books are my good friends.", [
    ("What is Tom like?", ["Tall and thin", "Short and fat", "Small and round", "Old and slow"], "0", "文中说 I am tall and thin。"),
    ("What does Tom like?", ["Reading books", "Playing games", "Eating candy", "Watching TV"], "0", "文中说 I like reading books。"),
])
r(PA, U2, "She is my friend Lily. She has curly hair and a round face. She sings very well. We all like her songs.", [
    ("What kind of hair does Lily have?", ["Curly", "Straight", "Long", "No"], "0", "文中说 She has curly hair。"),
    ("What does she do well?", ["Sings", "Runs", "Jumps", "Cooks"], "0", "文中说 She sings very well。"),
])
r(PA, U2, "I have two good friends. One is tall, one is short. The tall one likes basketball. The short one likes football.", [
    ("How many good friends?", ["Two", "One", "Three", "Four"], "0", "文中说 two good friends。"),
    ("What does the tall one like?", ["Basketball", "Football", "Tennis", "Swimming"], "0", "文中说 The tall one likes basketball。"),
])
r(PB, U2, "A: What do you look like? B: I have big eyes and small ears. A: You are cute. B: Thank you.", [
    ("What does B look like?", ["Big eyes and small ears", "Small eyes and big ears", "Long hair", "Short hair"], "0", "B 说 I have big eyes and small ears。"),
    ("What does A think of B?", ["Cute", "Ugly", "Tall", "Old"], "0", "A 说 You are cute。"),
])
r(PB, U2, "A: What do you like doing? B: I like swimming. A: Can you swim well? B: Yes, I can.", [
    ("What does B like?", ["Swimming", "Running", "Reading", "Cooking"], "0", "B 说 I like swimming。"),
    ("Can B swim well?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, I can。"),
])
r(PB, U2, "A: Are you good at singing? B: No, I'm not. I'm good at dancing. A: Can you show me? B: Sure!", [
    ("Is B good at singing?", ["No", "Yes", "Maybe", "Always"], "0", "B 说 No, I'm not。"),
    ("What is B good at?", ["Dancing", "Singing", "Cooking", "Reading"], "0", "B 说 I'm good at dancing。"),
])
r(PB, U2, "A: Who is your best friend? B: She is Lucy. A: What does she look like? B: She has long hair and a kind smile.", [
    ("Who is B's best friend?", ["Lucy", "Lily", "Amy", "Emma"], "0", "B 说 She is Lucy。"),
    ("What does Lucy have?", ["Long hair and a kind smile", "Short hair", "Big ears", "Small eyes"], "0", "B 说 long hair and a kind smile。"),
])
r(PB, U2, "A: Can you tell me about yourself? B: I'm nine. I like drawing. I want to be a painter.", [
    ("How old is B?", ["Nine", "Eight", "Ten", "Seven"], "0", "B 说 I'm nine。"),
    ("What does B want to be?", ["A painter", "A doctor", "A teacher", "A cook"], "0", "B 说 I want to be a painter。"),
])
r(PC, U2, "At the talent show, Lily sings a song. Everyone claps hands. Tom tells a joke. Everyone laughs. They are all stars today.", [
    ("What does Lily do?", ["Sings a song", "Dances", "Draws", "Runs"], "0", "文中说 Lily sings a song。"),
    ("What does Tom do?", ["Tells a joke", "Sings", "Sleeps", "Cries"], "0", "文中说 Tom tells a joke。"),
])
r(PC, U2, "Sam draws a self-portrait. He draws his big smile. His friends say it looks like him. Sam is proud of his work.", [
    ("What does Sam draw?", ["A self-portrait", "A tree", "A car", "A house"], "0", "文中说 Sam draws a self-portrait。"),
    ("How does Sam feel?", ["Proud", "Sad", "Angry", "Shy"], "0", "文中说 Sam is proud。"),
])
r(PC, U2, "Amy introduces herself to the class. She says her name, age and hobbies. She likes reading and swimming. Her classmates clap for her.", [
    ("What does Amy introduce?", ["Herself", "Her dog", "Her house", "Her food"], "0", "文中说 Amy introduces herself。"),
    ("What are her hobbies?", ["Reading and swimming", "Cooking and singing", "Running and jumping", "Eating and sleeping"], "0", "文中说 reading and swimming。"),
])
r(PC, U2, "Mike is good at sports. Lily is good at art. They help each other. Mike teaches Lily to run. Lily teaches Mike to draw.", [
    ("What is Mike good at?", ["Sports", "Art", "Music", "Cooking"], "0", "文中说 Mike is good at sports。"),
    ("What does Lily teach Mike?", ["To draw", "To run", "To swim", "To sing"], "0", "文中说 Lily teaches Mike to draw。"),
])
r(PC, U2, "We are all different. Some are tall, some are short. Some like sports, some like books. Different makes us special.", [
    ("Are we all the same?", ["No", "Yes", "Maybe", "Always"], "0", "文中说 We are all different。"),
    ("What makes us special?", ["Different", "Same", "Tall", "Short"], "0", "文中说 Different makes us special。"),
])
r(PD, U2, "Letter E e says /e/. Egg starts with E. Letter F f says /f/. Fish starts with F.", [
    ("What starts with E?", ["Egg", "Fish", "Ear", "Elk"], "0", "文中说 Egg starts with E。"),
    ("What starts with F?", ["Egg", "Fish", "Fox", "Fan"], "1", "文中说 Fish starts with F。"),
])
r(PD, U2, "Letter G g says /g/. Goat starts with G. Letter H h says /h/. Hat starts with H.", [
    ("What starts with G?", ["Goat", "Hat", "Gate", "Game"], "0", "文中说 Goat starts with G。"),
    ("What starts with H?", ["Goat", "Hat", "Hot", "Hop"], "1", "文中说 Hat starts with H。"),
])
r(PD, U2, "Letter I i says /ɪ/. Igloo starts with I. Letter J j says /dʒ/. Jet starts with J.", [
    ("What starts with I?", ["Igloo", "Jet", "Ink", "It"], "0", "文中说 Igloo starts with I。"),
    ("What starts with J?", ["Igloo", "Jet", "Jam", "Jar"], "1", "文中说 Jet starts with J。"),
])
r(PD, U2, "Letter K k says /k/. Kite starts with K. Letter L l says /l/. Lamp starts with L.", [
    ("What starts with K?", ["Kite", "Lamp", "Key", "Kid"], "0", "文中说 Kite starts with K。"),
    ("What starts with L?", ["Kite", "Lamp", "Leg", "Log"], "1", "文中说 Lamp starts with L。"),
])
r(PD, U2, "We read letters out loud. A B C D E F G. Each letter has a sound. Sounds make words.", [
    ("What do they read out loud?", ["Letters", "Pictures", "Numbers", "Toys"], "0", "文中说 We read letters out loud。"),
    ("What do sounds make?", ["Words", "Pictures", "Toys", "Games"], "0", "文中说 Sounds make words。"),
])

# ===== Unit 3 Learning better =====
r(PA, U3, "I go to school every day. I have Chinese, maths and English. My favourite subject is English. I learn new words every day.", [
    ("What is the favourite subject?", ["English", "Chinese", "Maths", "Art"], "0", "文中说 My favourite subject is English。"),
    ("What does the writer learn every day?", ["New words", "New songs", "New games", "New toys"], "0", "文中说 I learn new words every day。"),
])
r(PA, U3, "My classroom is big. There are desks and chairs. There is a blackboard, too. We study in the classroom.", [
    ("What is in the classroom?", ["Desks and chairs", "Beds and sofas", "Trees and flowers", "Cars and bikes"], "0", "文中说 desks and chairs。"),
    ("What do they do there?", ["Study", "Sleep", "Swim", "Cook"], "0", "文中说 We study in the classroom。"),
])
r(PA, U3, "I have a pencil case. There are pens, pencils and a ruler in it. I use them to write and draw.", [
    ("What is in the pencil case?", ["Pens, pencils and a ruler", "Books and bags", "Toys and balls", "Food and drinks"], "0", "文中说 pens, pencils and a ruler。"),
    ("What does the writer use them for?", ["Write and draw", "Eat and drink", "Play and run", "Sing and dance"], "0", "文中说 to write and draw。"),
])
r(PA, U3, "Our library has many books. Story books, picture books and science books. I borrow a book every week.", [
    ("What does the library have?", ["Many books", "Many toys", "Many foods", "Many cars"], "0", "文中说 many books。"),
    ("How often does the writer borrow a book?", ["Every week", "Every year", "Never", "Once"], "0", "文中说 every week。"),
])
r(PA, U3, "I do my homework after school. I write carefully. Then I check my answers. My teacher says I am a good learner.", [
    ("When does the writer do homework?", ["After school", "Before school", "In class only", "Never"], "0", "文中说 after school。"),
    ("What does the teacher say?", ["A good learner", "A bad student", "Too slow", "Too noisy"], "0", "文中说 I am a good learner。"),
])
r(PB, U3, "A: What subject do you like? B: I like maths. A: Why? B: Numbers are interesting.", [
    ("What subject does B like?", ["Maths", "English", "Art", "Music"], "0", "B 说 I like maths。"),
    ("Why does B like it?", ["Numbers are interesting", "It's easy", "It's short", "No homework"], "0", "B 说 Numbers are interesting。"),
])
r(PB, U3, "A: Can you read this word? B: Yes, it's 'apple'. A: Good job! B: Thank you, teacher.", [
    ("What is the word?", ["Apple", "Orange", "Banana", "Pear"], "0", "B 说 it's apple。"),
    ("What does the teacher say?", ["Good job", "Bad", "Try again", "Sit down"], "0", "老师说 Good job。"),
])
r(PB, U3, "A: How do you learn English? B: I read books and listen to tapes. A: Do you practise every day? B: Yes, I do.", [
    ("How does B learn English?", ["Read books and listen to tapes", "Only play games", "Only sleep", "Only eat"], "0", "B 说 read books and listen to tapes。"),
    ("Does B practise every day?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, I do。"),
])
r(PB, U3, "A: Is this your notebook? B: Yes, it is. A: Your handwriting is neat. B: I write slowly and carefully.", [
    ("Is it B's notebook?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, it is。"),
    ("How does B write?", ["Slowly and carefully", "Fast and messy", "Never", "Loudly"], "0", "B 说 slowly and carefully。"),
])
r(PB, U3, "A: What's your favourite class? B: It's art class. A: Why? B: I can draw beautiful pictures.", [
    ("What is B's favourite class?", ["Art class", "Maths class", "PE class", "Music class"], "0", "B 说 It's art class。"),
    ("What can B do in it?", ["Draw pictures", "Run fast", "Sing songs", "Cook food"], "0", "B 说 draw beautiful pictures。"),
])
r(PC, U3, "Sam has a problem with maths. His friend Lily helps him. They study together after class. Now Sam understands it well.", [
    ("What problem does Sam have?", ["Maths", "English", "Art", "Music"], "0", "文中说 a problem with maths。"),
    ("Who helps him?", ["Lily", "Teacher only", "No one", "His dog"], "0", "文中说 His friend Lily helps him。"),
])
r(PC, U3, "Amy wants to read faster. She reads every night before bed. Her mum listens to her. Now Amy reads much faster.", [
    ("What does Amy want?", ["To read faster", "To sleep more", "To eat more", "To play more"], "0", "文中说 wants to read faster。"),
    ("When does she read?", ["Every night before bed", "Every morning", "Never", "Only Sunday"], "0", "文中说 every night before bed。"),
])
r(PC, U3, "Tom forgets his homework. He feels sorry. His teacher says it's OK, but don't do it again. Tom makes a checklist now.", [
    ("What does Tom forget?", ["Homework", "Lunch", "Shoes", "Bag"], "0", "文中说 forgets his homework。"),
    ("What does Tom make now?", ["A checklist", "A cake", "A toy", "A song"], "0", "文中说 makes a checklist。"),
])
r(PC, U3, "We learn better together. I help you with English. You help me with maths. We both get better grades.", [
    ("How do they learn better?", ["Together", "Alone", "Never", "Slowly"], "0", "文中说 We learn better together。"),
    ("What happens at last?", ["Both get better grades", "Both fail", "Both sleep", "Both cry"], "0", "文中说 We both get better grades。"),
])
r(PC, U3, "Lily sets a study plan. She reads in the morning. She writes in the afternoon. She reviews at night. She learns a lot every day.", [
    ("What does Lily set?", ["A study plan", "A party plan", "A trip plan", "A game plan"], "0", "文中说 Lily sets a study plan。"),
    ("What does she do at night?", ["Reviews", "Plays", "Sleeps all night", "Eats"], "0", "文中说 She reviews at night。"),
])
r(PD, U3, "Letter O o says /ɒ/. Octopus starts with O. Letter P p says /p/. Pencil starts with P.", [
    ("What starts with O?", ["Octopus", "Pencil", "Owl", "Ox"], "0", "文中说 Octopus starts with O。"),
    ("What starts with P?", ["Octopus", "Pencil", "Pen", "Pig"], "1", "文中说 Pencil starts with P。"),
])
r(PD, U3, "Letter R r says /r/. Ruler starts with R. Letter S s says /s/. School starts with S.", [
    ("What starts with R?", ["Ruler", "School", "Red", "Run"], "0", "文中说 Ruler starts with R。"),
    ("What starts with S?", ["Ruler", "School", "Sun", "Sit"], "1", "文中说 School starts with S。"),
])
r(PD, U3, "Letter T t says /t/. Teacher starts with T. Letter U u says /ʌ/. Umbrella starts with U.", [
    ("What starts with T?", ["Teacher", "Umbrella", "Top", "Ten"], "0", "文中说 Teacher starts with T。"),
    ("What starts with U?", ["Teacher", "Umbrella", "Up", "Us"], "1", "文中说 Umbrella starts with U。"),
])
r(PD, U3, "Letter V v says /v/. Violin starts with V. Letter W w says /w/. Window starts with W.", [
    ("What starts with V?", ["Violin", "Window", "Van", "Vet"], "0", "文中说 Violin starts with V。"),
    ("What starts with W?", ["Violin", "Window", "Wet", "Win"], "1", "文中说 Window starts with W。"),
])
r(PD, U3, "We blend sounds to make words. C-a-t makes cat. D-o-g makes dog. Blending is a magic trick.", [
    ("What does C-a-t make?", ["Cat", "Dog", "Car", "Cup"], "0", "文中说 C-a-t makes cat。"),
    ("What does D-o-g make?", ["Cat", "Dog", "Dot", "Dig"], "1", "文中说 D-o-g makes dog。"),
])

# ===== Unit 4 Healthy food =====
r(PA, U4, "I like healthy food. I eat fruit and vegetables every day. Apples, bananas and carrots are good for me.", [
    ("What does the writer eat every day?", ["Fruit and vegetables", "Candy", "Ice cream", "Only meat"], "0", "文中说 fruit and vegetables every day。"),
    ("What is good for the writer?", ["Apples, bananas and carrots", "Chips", "Cola", "Cake"], "0", "文中说 Apples, bananas and carrots。"),
])
r(PA, U4, "Breakfast is important. I have bread, milk and an egg. It gives me energy for school. I feel strong.", [
    ("What does the writer have for breakfast?", ["Bread, milk and an egg", "Nothing", "Only candy", "Only water"], "0", "文中说 bread, milk and an egg。"),
    ("How does the writer feel?", ["Strong", "Weak", "Sleepy", "Sad"], "0", "文中说 I feel strong。"),
])
r(PA, U4, "Milk is good for our bones. Water is the best drink. We should drink water every day. It keeps us healthy.", [
    ("What is good for bones?", ["Milk", "Cola", "Juice only", "Candy"], "0", "文中说 Milk is good for our bones。"),
    ("What is the best drink?", ["Water", "Cola", "Milk shake", "Soda"], "0", "文中说 Water is the best drink。"),
])
r(PA, U4, "Vegetables have many colours. Carrots are orange. Tomatoes are red. Cucumbers are green. We should eat rainbow food.", [
    ("What colour are carrots?", ["Orange", "Red", "Green", "White"], "0", "文中说 Carrots are orange。"),
    ("What should we eat?", ["Rainbow food", "Only candy", "Only chips", "Nothing"], "0", "文中说 eat rainbow food。"),
])
r(PA, U4, "Fish is healthy food. It helps our brain. We eat fish twice a week. My mother cooks it very well.", [
    ("What helps our brain?", ["Fish", "Candy", "Cake", "Cola"], "0", "文中说 Fish helps our brain。"),
    ("How often do they eat fish?", ["Twice a week", "Never", "Once a year", "Every hour"], "0", "文中说 twice a week。"),
])
r(PB, U4, "A: Do you like vegetables? B: Yes, I do. A: Which one? B: I like carrots. They are sweet.", [
    ("Does B like vegetables?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, I do。"),
    ("Which one does B like?", ["Carrots", "Onions", "Potatoes", "Peppers"], "0", "B 说 I like carrots。"),
])
r(PB, U4, "A: What do you have for lunch? B: I have rice, chicken and soup. A: It sounds healthy. B: Yes, it is.", [
    ("What does B have for lunch?", ["Rice, chicken and soup", "Only candy", "Nothing", "Only cola"], "0", "B 说 rice, chicken and soup。"),
    ("Is it healthy?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, it is。"),
])
r(PB, U4, "A: Is candy healthy food? B: No, it isn't. A: What should we eat instead? B: We should eat fruit.", [
    ("Is candy healthy?", ["No", "Yes", "Maybe", "Always"], "0", "B 说 No, it isn't。"),
    ("What should we eat instead?", ["Fruit", "More candy", "Chips", "Ice cream"], "0", "B 说 We should eat fruit。"),
])
r(PB, U4, "A: How many apples do you eat a day? B: I eat one apple a day. A: An apple a day keeps the doctor away.", [
    ("How many apples does B eat a day?", ["One", "Two", "Five", "Zero"], "0", "B 说 one apple a day。"),
    ("What does an apple a day do?", ["Keeps the doctor away", "Makes you sick", "Nothing", "Makes you tired"], "0", "A 说 keeps the doctor away。"),
])
r(PB, U4, "A: Would you like some milk? B: Yes, please. A: Milk is good for you. B: Thank you. It's delicious.", [
    ("What does A offer?", ["Milk", "Cola", "Candy", "Cake"], "0", "A 说 some milk。"),
    ("How is it?", ["Delicious", "Bad", "Cold", "Sour"], "0", "B 说 It's delicious。"),
])
r(PC, U4, "Lily wants to be healthy. She eats breakfast every day. She drinks water, not cola. She feels much better now.", [
    ("What does Lily drink?", ["Water", "Cola", "Juice", "Soda"], "0", "文中说 She drinks water, not cola。"),
    ("How does she feel now?", ["Much better", "Worse", "Sleepy", "Sad"], "0", "文中说 much better now。"),
])
r(PC, U4, "Tom eats too much candy. His teeth hurt. The dentist says eat less candy. Tom eats fruit instead now.", [
    ("What does Tom eat too much?", ["Candy", "Fruit", "Rice", "Fish"], "0", "文中说 too much candy。"),
    ("What does he eat now?", ["Fruit", "More candy", "Chips", "Cake"], "0", "文中说 eats fruit instead。"),
])
r(PC, U4, "Our class has a food day. We bring healthy food. Amy brings apples. Sam brings milk. We share and eat together happily.", [
    ("What do they bring?", ["Healthy food", "Toys", "Books", "Balls"], "0", "文中说 We bring healthy food。"),
    ("What does Amy bring?", ["Apples", "Milk", "Candy", "Cake"], "0", "文中说 Amy brings apples。"),
])
r(PC, U4, "Mum makes a salad. She puts in tomatoes, cucumbers and carrots. It is colourful and yummy. We eat it for dinner.", [
    ("What does Mum make?", ["A salad", "A cake", "Candy", "Ice cream"], "0", "文中说 Mum makes a salad。"),
    ("When do they eat it?", ["Dinner", "Breakfast", "Midnight", "Never"], "0", "文中说 for dinner。"),
])
r(PC, U4, "We learn about food groups. Grains, fruit, vegetables, meat and milk. We need them all. A balanced diet keeps us strong.", [
    ("What do we need?", ["All food groups", "Only candy", "Only meat", "Nothing"], "0", "文中说 We need them all。"),
    ("What keeps us strong?", ["A balanced diet", "Only sleep", "Only play", "Nothing"], "0", "文中说 A balanced diet keeps us strong。"),
])
r(PD, U4, "Letter X x says /ks/. Fox starts with X. Letter Y y says /j/. Yogurt starts with Y.", [
    ("What starts with X?", ["Fox", "Yogurt", "Box", "Axe"], "0", "文中说 Fox starts with X。"),
    ("What starts with Y?", ["Fox", "Yogurt", "Yes", "You"], "1", "文中说 Yogurt starts with Y。"),
])
r(PD, U4, "Letter Z z says /z/. Zebra starts with Z. We finish the alphabet. From A to Z, well done!", [
    ("What starts with Z?", ["Zebra", "Zoo", "Zip", "Zen"], "0", "文中说 Zebra starts with Z。"),
    ("What do they finish?", ["The alphabet", "Lunch", "Homework", "A game"], "0", "文中说 We finish the alphabet。"),
])
r(PD, U4, "We read food words. Milk, egg, rice, fish. We sound them out slowly. Reading food words is fun.", [
    ("What words do they read?", ["Food words", "Animal words", "Colour words", "Number words"], "0", "文中说 We read food words。"),
    ("How do they sound them out?", ["Slowly", "Fast", "Never", "Loudly only"], "0", "文中说 slowly。"),
])
r(PD, U4, "The short sound /æ/ is in apple and cat. The short sound /e/ is in egg and bed. We practise the sounds.", [
    ("Which word has /æ/?", ["Apple", "Egg", "Bed", "Pen"], "0", "文中说 /æ/ is in apple and cat。"),
    ("Which word has /e/?", ["Apple", "Egg", "Cat", "Hat"], "1", "文中说 /e/ is in egg and bed。"),
])
r(PD, U4, "We play a letter game. Find food starting with B. Banana, bread, beans! We win the game and laugh.", [
    ("What letter do they look for?", ["B", "A", "C", "D"], "0", "文中说 starting with B。"),
    ("What food do they find?", ["Banana, bread, beans", "Apple, egg, rice", "Fish, milk, cake", "Candy, cola, chips"], "0", "文中说 Banana, bread, beans。"),
])

# ===== Unit 5 Old toys =====
r(PA, U5, "I have many toys. A car, a ball and a doll. My favourite toy is the doll. Her name is Kitty.", [
    ("What is the favourite toy?", ["The doll", "The car", "The ball", "A kite"], "0", "文中说 My favourite toy is the doll。"),
    ("What is the doll's name?", ["Kitty", "Lily", "Amy", "Lucy"], "0", "文中说 Her name is Kitty。"),
])
r(PA, U5, "This is my old toy car. It is red. It can run fast. I have had it for three years. I still like it.", [
    ("What colour is the toy car?", ["Red", "Blue", "Green", "Black"], "0", "文中说 It is red。"),
    ("How long has the writer had it?", ["Three years", "One year", "Ten years", "One day"], "0", "文中说 three years。"),
])
r(PA, U5, "My teddy bear is soft. It is brown. I sleep with it every night. It is my best friend.", [
    ("What is the teddy bear like?", ["Soft", "Hard", "Cold", "Wet"], "0", "文中说 My teddy bear is soft。"),
    ("When does the writer sleep with it?", ["Every night", "Never", "Once a year", "Only Sunday"], "0", "文中说 every night。"),
])
r(PA, U5, "There is a toy box in my room. It has many old toys. Robots, blocks and puzzles. I open it every day.", [
    ("What is in the room?", ["A toy box", "A big bed", "A TV", "A fridge"], "0", "文中说 There is a toy box。"),
    ("What is in the box?", ["Old toys", "Food", "Books", "Clothes"], "0", "文中说 many old toys。"),
])
r(PA, U5, "Old toys have stories. My kite flew high in the sky. My boat played in the water. I remember them all.", [
    ("Where did the kite fly?", ["High in the sky", "In the water", "Under the bed", "In the box"], "0", "文中说 flew high in the sky。"),
    ("Where did the boat play?", ["In the water", "In the sky", "On the road", "In the room"], "0", "文中说 played in the water。"),
])
r(PB, U5, "A: Is this your toy? B: Yes, it's my old robot. A: How old is it? B: It's five years old.", [
    ("What is the toy?", ["An old robot", "A new car", "A ball", "A doll"], "0", "B 说 my old robot。"),
    ("How old is it?", ["Five years", "One year", "Ten years", "Two days"], "0", "B 说 five years old。"),
])
r(PB, U5, "A: What can your toy car do? B: It can run and turn. A: Wow, it's cool. B: Yes, I love it.", [
    ("What can the toy car do?", ["Run and turn", "Fly and swim", "Sing and dance", "Eat and drink"], "0", "B 说 run and turn。"),
    ("What does A think?", ["It's cool", "It's bad", "It's boring", "It's ugly"], "0", "A 说 it's cool。"),
])
r(PB, U5, "A: Do you still play with old toys? B: Yes, I do. A: Why? B: They are my friends with memories.", [
    ("Does B play with old toys?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 Yes, I do。"),
    ("Why?", ["They are friends with memories", "They are new", "They are expensive", "No reason"], "0", "B 说 friends with memories。"),
])
r(PB, U5, "A: Where is your ball? B: It's under the bed. A: Let's get it. B: OK, here it is.", [
    ("Where is the ball?", ["Under the bed", "On the table", "In the box", "In the sky"], "0", "B 说 under the bed。"),
    ("What do they do?", ["Get it", "Buy a new one", "Forget it", "Cry"], "0", "A 说 Let's get it。"),
])
r(PB, U5, "A: Whose doll is this? B: It's mine. A: Can I play with it? B: Sure, let's play together.", [
    ("Whose doll is it?", ["B's", "A's", "Teacher's", "Nobody's"], "0", "B 说 It's mine。"),
    ("What do they do?", ["Play together", "Fight", "Sleep", "Leave"], "0", "B 说 let's play together。"),
])
r(PC, U5, "Amy's teddy bear is old. One ear is loose. Her mum sews it for her. The bear is as good as new. Amy hugs it tightly.", [
    ("What is wrong with the bear?", ["One ear is loose", "It is lost", "It is dirty", "It is broken in half"], "0", "文中说 One ear is loose。"),
    ("Who fixes it?", ["Her mum", "Amy", "Teacher", "Nobody"], "0", "文中说 Her mum sews it。"),
])
r(PC, U5, "Sam has a toy sale. He sells his old cars. His friends buy them. The toys find new homes. Sam is happy to share.", [
    ("What does Sam have?", ["A toy sale", "A birthday party", "A picnic", "A class"], "0", "文中说 Sam has a toy sale。"),
    ("What happens to the toys?", ["Find new homes", "Get lost", "Break", "Stay old"], "0", "文中说 The toys find new homes。"),
])
r(PC, U5, "Lily makes a new toy. She uses an old box and some paint. It becomes a robot. Old things can be new toys.", [
    ("What does Lily use?", ["An old box and paint", "New toys", "Food", "Books"], "0", "文中说 an old box and some paint。"),
    ("What does it become?", ["A robot", "A car", "A doll", "A ball"], "0", "文中说 It becomes a robot。"),
])
r(PC, U5, "We visit a toy museum. There are toys from long ago. Wooden horses and cloth dolls. Toys tell us stories of the past.", [
    ("Where do they visit?", ["A toy museum", "A zoo", "A park", "A school"], "0", "文中说 a toy museum。"),
    ("What toys are there?", ["Wooden horses and cloth dolls", "Robots only", "Cars only", "Nothing"], "0", "文中说 Wooden horses and cloth dolls。"),
])
r(PC, U5, "Grandpa shows me his old toys. A spinning top and marbles. He played with them as a boy. Now we play together.", [
    ("What are Grandpa's old toys?", ["Spinning top and marbles", "Robots", "Video games", "Phones"], "0", "文中说 A spinning top and marbles。"),
    ("What do they do now?", ["Play together", "Sleep", "Eat", "Watch TV"], "0", "文中说 Now we play together。"),
])
r(PD, U5, "Letter B b says /b/. Ball starts with B. Letter T t says /t/. Toy starts with T.", [
    ("What starts with B?", ["Ball", "Toy", "Bat", "Bed"], "0", "文中说 Ball starts with B。"),
    ("What starts with T?", ["Ball", "Toy", "Top", "Ten"], "1", "文中说 Toy starts with T。"),
])
r(PD, U5, "Letter D d says /d/. Doll starts with D. Letter R r says /r/. Robot starts with R.", [
    ("What starts with D?", ["Doll", "Robot", "Dog", "Door"], "0", "文中说 Doll starts with D。"),
    ("What starts with R?", ["Doll", "Robot", "Red", "Run"], "1", "文中说 Robot starts with R。"),
])
r(PD, U5, "We read toy words. Ball, doll, car, kite. We sound them out. Then we read them fast.", [
    ("What words do they read?", ["Toy words", "Food words", "Animal words", "Number words"], "0", "文中说 We read toy words。"),
    ("How do they read at last?", ["Fast", "Slow", "Never", "Quietly"], "0", "文中说 read them fast。"),
])
r(PD, U5, "The /ɒ/ sound is in doll and top. The /eɪ/ sound is in kite and plane. We listen and repeat.", [
    ("Which word has /ɒ/?", ["Doll", "Kite", "Plane", "Cake"], "0", "文中说 /ɒ/ is in doll and top。"),
    ("Which word has /eɪ/?", ["Doll", "Kite", "Top", "Hot"], "1", "文中说 /eɪ/ is in kite and plane。"),
])
r(PD, U5, "We sing a toy song. Ball and doll, car and kite. We play with toys every day. Toys make us happy.", [
    ("What do they sing?", ["A toy song", "A food song", "A number song", "A colour song"], "0", "文中说 We sing a toy song。"),
    ("What do toys do?", ["Make us happy", "Make us sad", "Make us sleep", "Make us cry"], "0", "文中说 Toys make us happy。"),
])

# ===== Unit 6 Numbers in life =====
r(PA, U6, "Numbers are everywhere. There are twelve months in a year. There are seven days in a week. We count every day.", [
    ("How many months in a year?", ["Twelve", "Seven", "Ten", "Five"], "0", "文中说 twelve months。"),
    ("How many days in a week?", ["Seven", "Twelve", "Thirty", "One"], "0", "文中说 seven days。"),
])
r(PA, U6, "I have twenty crayons. Ten are warm colours. Ten are cool colours. I use them to draw rainbows.", [
    ("How many crayons?", ["Twenty", "Ten", "Twelve", "Fifteen"], "0", "文中说 twenty crayons。"),
    ("What does the writer draw?", ["Rainbows", "Cars", "Food", "Numbers"], "0", "文中说 draw rainbows。"),
])
r(PA, U6, "There are four seasons. Spring, summer, autumn and winter. Each season has three months. I count them all.", [
    ("How many seasons are there?", ["Four", "Three", "Twelve", "Six"], "0", "文中说 four seasons。"),
    ("How many months in each season?", ["Three", "Four", "Two", "Five"], "0", "文中说 three months。"),
])
r(PA, U6, "My family lives on the fifth floor. There are six rooms in our home. I climb the stairs to count them.", [
    ("Which floor do they live on?", ["Fifth", "Sixth", "First", "Tenth"], "0", "文中说 fifth floor。"),
    ("How many rooms?", ["Six", "Five", "Four", "Seven"], "0", "文中说 six rooms。"),
])
r(PA, U6, "A clock has twelve numbers. It tells us the time. It is eight o'clock now. Time to go to school.", [
    ("How many numbers on a clock?", ["Twelve", "Ten", "Six", "Eight"], "0", "文中说 twelve numbers。"),
    ("What time is it?", ["Eight o'clock", "Nine o'clock", "Six o'clock", "Twelve o'clock"], "0", "文中说 eight o'clock。"),
])
r(PB, U6, "A: How many students are in your class? B: There are forty students. A: How many boys? B: Twenty boys and twenty girls.", [
    ("How many students in the class?", ["Forty", "Twenty", "Thirty", "Fifty"], "0", "B 说 forty students。"),
    ("How many boys?", ["Twenty", "Forty", "Ten", "Thirty"], "0", "B 说 twenty boys。"),
])
r(PB, U6, "A: What's your phone number? B: It's 5-5-3-2. A: I'll call you. B: Great, talk soon.", [
    ("What is B's phone number?", ["5-5-3-2", "1-2-3-4", "9-9-9-9", "5-3-5-3"], "0", "B 说 It's 5-5-3-2。"),
    ("What will A do?", ["Call B", "Visit B", "Write a letter", "Nothing"], "0", "A 说 I'll call you。"),
])
r(PB, U6, "A: How old is your sister? B: She is six. A: When is her birthday? B: It's on June first.", [
    ("How old is the sister?", ["Six", "Seven", "Eight", "Five"], "0", "B 说 She is six。"),
    ("When is her birthday?", ["June first", "July first", "May first", "June second"], "0", "B 说 June first。"),
])
r(PB, U6, "A: What time do you get up? B: At seven o'clock. A: What time do you go to school? B: At eight o'clock.", [
    ("When does B get up?", ["Seven o'clock", "Eight o'clock", "Nine o'clock", "Six o'clock"], "0", "B 说 seven o'clock。"),
    ("When does B go to school?", ["Eight o'clock", "Seven o'clock", "Ten o'clock", "Five o'clock"], "0", "B 说 eight o'clock。"),
])
r(PB, U6, "A: How much is the book? B: It's ten yuan. A: I have twelve yuan. B: Then you can buy it.", [
    ("How much is the book?", ["Ten yuan", "Twelve yuan", "Five yuan", "Twenty yuan"], "0", "B 说 ten yuan。"),
    ("Can A buy it?", ["Yes", "No", "Maybe", "Never"], "0", "B 说 you can buy it。"),
])
r(PC, U6, "Lily counts the stars at night. One, two, three... She counts twenty stars. The sky is full of lights.", [
    ("What does Lily count?", ["Stars", "Birds", "Clouds", "Planes"], "0", "文中说 Lily counts the stars。"),
    ("How many stars?", ["Twenty", "Ten", "Five", "Twelve"], "0", "文中说 twenty stars。"),
])
r(PC, U6, "Sam buys fruit at the shop. Five apples and three oranges. That is eight fruits in all. He counts them on the way home.", [
    ("How many fruits in all?", ["Eight", "Five", "Three", "Ten"], "0", "5+3=8，文中说 eight fruits。"),
    ("When does he count them?", ["On the way home", "At school", "In bed", "Never"], "0", "文中说 on the way home。"),
])
r(PC, U6, "There are ten candles on the cake. It is Amy's birthday. We sing the birthday song. Amy blows out all ten candles.", [
    ("How many candles?", ["Ten", "Five", "Eight", "Twelve"], "0", "文中说 ten candles。"),
    ("Whose birthday is it?", ["Amy's", "Sam's", "Lily's", "Tom's"], "0", "文中说 Amy's birthday。"),
])
r(PC, U6, "We measure the classroom. The room is eight metres long. The blackboard is three metres wide. Numbers help us measure things.", [
    ("How long is the room?", ["Eight metres", "Three metres", "Ten metres", "Five metres"], "0", "文中说 eight metres long。"),
    ("What do numbers help us do?", ["Measure things", "Sing songs", "Draw pictures", "Eat food"], "0", "文中说 Numbers help us measure things。"),
])
r(PC, U6, "Mum gives me some coins. Five one-yuan coins and one five-yuan coin. That is ten yuan. I save it in my piggy bank.", [
    ("How much money in all?", ["Ten yuan", "Five yuan", "Six yuan", "Eight yuan"], "0", "5+5=10，文中说 ten yuan。"),
    ("Where does the writer save it?", ["Piggy bank", "Toy box", "School bag", "Pocket"], "0", "文中说 in my piggy bank。"),
])
r(PD, U6, "Number 1 and 2. One is a stick. Two is a duck. We trace the numbers in the air.", [
    ("What does 1 look like?", ["A stick", "A duck", "A ball", "A hook"], "0", "文中说 One is a stick。"),
    ("What does 2 look like?", ["A duck", "A stick", "A cup", "A ring"], "0", "文中说 Two is a duck。"),
])
r(PD, U6, "Number 3 and 4. Three has two curves. Four has straight lines. We write them on paper.", [
    ("How many curves does 3 have?", ["Two", "One", "Three", "Four"], "0", "文中说 Three has two curves。"),
    ("What does 4 have?", ["Straight lines", "Curves", "Circles", "Dots"], "0", "文中说 straight lines。"),
])
r(PD, U6, "Number 5 and 6. Five is a hook. Six is a whistle. We count from one to six.", [
    ("What does 5 look like?", ["A hook", "A whistle", "A ball", "A flag"], "0", "文中说 Five is a hook。"),
    ("What does 6 look like?", ["A whistle", "A hook", "A stick", "A cup"], "0", "文中说 Six is a whistle。"),
])
r(PD, U6, "Number 9 and 10. Nine is a balloon on a string. Ten is a stick and a ball. Numbers are our friends.", [
    ("What does 9 look like?", ["A balloon on a string", "A stick", "A duck", "A hook"], "0", "文中说 Nine is a balloon on a string。"),
    ("What does 10 look like?", ["A stick and a ball", "A duck", "A whistle", "A hook"], "0", "文中说 Ten is a stick and a ball。"),
])
r(PD, U6, "We count and clap. One two three four five. We jump at six seven eight. Numbers make games fun.", [
    ("What do they do with numbers?", ["Count and clap", "Eat", "Sleep", "Cry"], "0", "文中说 We count and clap。"),
    ("What do numbers make fun?", ["Games", "Food", "Books", "Clothes"], "0", "文中说 Numbers make games fun。"),
])

with open(r"C:\Users\Yaojie\Documents\GitHub\quiz\data\english_reading_lower.json", "w", encoding="utf-8") as f:
    json.dump(Q, f, ensure_ascii=False, indent=2)
from collections import Counter, defaultdict
print(f"下册共 {len(Q)} 篇")
d = defaultdict(Counter)
for q in Q:
    d[q['unit']][q['topic_name']] += 1
units = sorted(d.keys())
parts = ['Part A 词汇','Part B 句型','Part C 对话','拼读与语音']
for u in units:
    line = ' | '.join(f'{p}:{d[u].get(p,0)}' for p in parts)
    print(f'{u}: {line}')
