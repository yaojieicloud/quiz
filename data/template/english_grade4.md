# 英语四年级出题模板

> 适用年级：四年级（上册/下册）
> 教材版本：**人教版 PEP 2024 秋季沿用版**
> 科目信息：name=英语，grade=四年级
> 最后更新：2026-09-01

---

## 课程结构规范

- **无单元概念**：`name = unit`（参考 Python 理论科目样式）
- ECS 已建 11 个课程（6 Units + 1 Revision + 4 Appendix）

---

## 科目基本信息

| 字段 | 值 |
|------|-----|
| name | 英语 |
| grade | 四年级 |
| category | culture |
| icon | 🦜 |
| allowed_types | `["choice", "judge", "fill", "essay", "match", "sort", "reading"]` |

> 注：英语支持 reading ✅，可用于英语阅读理解。

---

## 四年级上册目录结构（人教 PEP 2024 秋季沿用版）

> ECS 现状（2026-09-01 已录 11 课时）：

| topic_name（= unit） | 页码 | 主题 | 核心知识点 |
|---------------------|------|------|-----------|
| Unit 1 Helping at home | 22 | 家务与职业 | 字母组合 ch(/tʃ/)：teach, chair, lunch, peach, China, child, teacher, kitchen；职业词汇：farmer, nurse, doctor, office worker, factory worker, PE teacher, cook；家务：sweep, clean, look after；句型：What's sb.'s job? Can you help at home? |
| Unit 2 My friends | 14 | 朋友 | 字母组合 sh(/ʃ/)：share, shell, fish, shop, ship, English；性格外貌：kind, quiet, funny, tall, strong, short, thin；句型：What's he/she like? He/She has...；主谓一致：has/have |
| Unit 3 Places we live in | 26 | 社区场所 | 字母组合 ck(/k/)：duck, black, sock, back, tick；场所：park, hospital, playground, shop, bus stop, toilets, library, museum；句型：There is/are...；Is there...? 一般疑问句；就近原则 |
| Unit 4 Helping in the community | 38 | 社区工作 | 字母组合 ph(/f/)：phone, photo, elephant, Philip；社区职业：cleaner, police officer, delivery worker, bus driver, firefighter, volunteer |
| Unit 5 The weather and us | 50 | 天气 | 字母组合（待补：wh-）；天气：sunny, rainy, cloudy, windy, hot, cold；句型：What's the weather like? |
| Unit 6 Changing for the seasons | 62 | 季节变化 | 字母组合（待补：ing）；四季：spring, summer, autumn, winter；活动：fly kites, swim, pick apples, make a snowman |
| Revision Let's help! | 74 | 复习 | Let's help 综合复习 |
| Appendix 1 Songs | 78 | 歌曲 | - |
| Appendix 2 Words in each unit | 80 | 词汇表 | - |
| Appendix 3 Vocabulary | 83 | 词汇总表 | - |
| Appendix 4 Useful expressions | 86 | 常用表达 | - |

> **详细音标/词汇/句型/语法** 参见搜索的"考点知识汇编"和教师用书。
> **已完成的课本摘录笔记**（按 Unit 整理，可直接用于出题）：
>
> | 课时 | 笔记路径 | 状态 |
> |------|---------|------|
> | Unit 1 Helping at home | `docs/textbook/english_grade4/Unit1_HelpingAtHome.md` | ✅ 已完成（6 张截图完整摘录：导入 + Section A/B/C + Reading time） |
> | Unit 2 My friends | `docs/textbook/english_grade4/Unit2_MyFriends.md` | ✅ 已完成（6 张截图完整摘录：导入 + Section A/B/C + Let's spell + Reading time） |
>
> **未来 Unit 笔记产出 SOP**：课本截图 → 子代理 vision_analyze 逐张识别 → 汇总到 `docs/textbook/english_grade4/unit{N}_{name}_notes.md`（追加不覆盖）→ 与 `data/english_grade4/` 下的出题 JSON 配套保存。

---

## 出题前知识点清单模板

```markdown
## 出题课时：Unit 2 My friends
- 来源：人教版 PEP 四年级 上册 Unit 2
- 核心知识点（3-7 条）：
  1. 字母组合 sh 读 /ʃ/（share, shell, fish, ship, English）
  2. 性格外貌词汇：kind, quiet, funny, tall, strong, short, thin, long hair, short hair
  3. 询问外貌性格句型：What's he/she like?
  4. has/have 区别：主语第三人称单数用 has
  5. 物主代词 his/her 区分
- 拟用题型：choice + match（英汉）+ fill（单词拼写）
- 拟出题数：choice 5 道 + match 2 道 + fill 3 道 = 10 道
- 检查项：
  - [ ] 不超纲（不出 has/ have 三单以外的高级语法）
  - [ ] 不串课（不出后续单元的 there be 句型）
  - [ ] 拼写答案大小写不敏感
```

---

## 出题铁律

1. **不超纲**：4 年级 PEP 水平；不出现后续年级/单元的语法
2. **不出字母大写错误**：`His name is Zhang Peng.`（专有名词首字母大写）
3. **拼写答案大小写不敏感**：系统判分自动 lowercase
4. **match 用英汉连线**（单词↔中文/图意）
5. **fill 可出单词拼写题**：单词填入 `____` 形式的句子
6. **不出 reading 短文的复杂语法**：时态限于一般现在时和一般过去时
7. **连接题/连线题去重约束**：左右两侧各自唯一（见 `question_types.md`）

---

## 题型支持情况

| 题型 | 支持 | 常见用法 |
|------|------|----------|
| choice | ✅ | 4 选 1：单词/句型/语法/听力理解 |
| judge | ✅ | 对/错：语法/文化常识 |
| fill | ✅ | 单词拼写/句子填空 |
| match | ✅ | 英汉连线、单词↔图片意 |
| sort | ✅ | 按字母顺序、按时间顺序 |
| reading | ✅ | 英语阅读理解（一般现在时/一般过去时） |
| essay | ✅ | 短文写作（如 My friend） |
| code | ❌ | 不支持 |
| calc | ❌ | 不支持 |

---

## 导入命令

```bash
# 英语四上
python src/data/import_array.py --subject-id 8 --json data/english_grade4_vol1.json --label 英语四上
```

> 注：英语无单元，topic_name 直接是 Unit 标题，与 unit 相同。
