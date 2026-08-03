# 题库 JSON 标准格式规范

> 本文件定义了题库系统的标准题目 JSON 格式。后续出题、批量导入均遵循此格式。
> 关联文档：[README.md](../README.md) §4 数据模型

## 一、整体结构

批量导入时，JSON 是一个**题目数组**，每道题是一个对象：

```json
[
  { "type": "choice", "topic_name": "章节名", "content": "题干", "options": ["A","B","C","D"], "answer": "1", "explanation": "讲解", "difficulty": 1 },
  { "type": "judge", "topic_name": "章节名", "content": "题干", "options": ["对","错"], "answer": "0", "explanation": "讲解", "difficulty": 1 },
  { "type": "calc", "topic_name": "章节名", "content": "题干", "options": null, "answer": "834", "explanation": "讲解", "difficulty": 2 },
  { "type": "fill", "topic_name": "章节名", "content": "题干____", "answer": "答案", "explanation": "讲解", "difficulty": 1 },
  { "type": "essay", "topic_name": "章节名", "content": "题干", "answer": "待老师点评", "explanation": "参考思路", "difficulty": 1 },
  { "type": "match", "topic_name": "章节名", "content": "将左侧与右侧连线匹配", "options": ["左1","左2"], "match_options": ["右A","右B"], "answer": "0:1,1:0", "explanation": "讲解", "difficulty": 1 },
  { "type": "sort", "topic_name": "章节名", "content": "将下列步骤排序", "options": ["步骤B","步骤A","步骤C"], "answer": "1,0,2", "explanation": "讲解", "difficulty": 1 }
]
```

## 二、字段说明

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `type` | ✅ | string | 题型：`choice` / `judge` / `calc` / `fill` / `essay` / `match` / `sort` / `code` / `reading` |
| `topic_name` | ✅ | string | 章节名称。导入时如不存在会**自动创建** |
| `unit` | 可选 | string | 所属单元（仅文化类科目用，如 `"三年级上册"`）。创建章节时一并写入；编程类科目留空 |
| `content` | ✅ | string | 题干内容。可用 `\n` 换行 |
| `options` | 选择/判断/连线/排序必填 | array\|null | 选项数组。选择题通常4个，判断题固定 `["对","错"]`，计算/应用题填 `null`，连线题填左侧项目，排序题填打乱的项目 |
| `match_options` | 连线题必填 | array\|null | 连线题右侧选项数组（打乱顺序），其他题型不填 |
| `reading_items` | reading 题必填 | array\|null | 阅读理解子题数组（仅语文/英语），见题型 9 |
| `answer` | ✅ | string | 答案（字符串）。各题型格式不同，见下方详细说明 |
| `blank_count` | 填空题可选 | int | 填空数量，默认 1 |
| `blank_answers` | 多空填空必填 | array\|null | 多空填空题各空答案数组 |
| `tolerance` | 填空题可选 | float | 数字容差，默认 0.01 |
| `explanation` | 可选 | string | 错题讲解。支持 HTML 标签如 `<b>`、`<code>`、`<br>` |
| `difficulty` | 可选 | int | 难度 1-5，默认 1。1最简单，5最难 |

## 三、各题型详细说明与示例

> 说明：`unit` 字段仅文化类科目（语文/数学/英语...）使用，用于按单元分组；编程类科目（Python）不填。

### 1. 选择题（choice）

```json
{
  "type": "choice",
  "topic_name": "变量与标识符",
  "content": "下面哪个是合法的变量名？",
  "options": ["2name", "name_2", "class", "my-name"],
  "answer": "1",
  "explanation": "变量名只能用字母、数字、下划线组成。<b>2name</b>数字开头不行，<b>my-name</b>有减号不行，<b>class</b>是关键字。选<b>name_2</b>。",
  "difficulty": 1
}
```

- `options` 有4个选项
- `answer` 是 `"1"`，表示第2个选项（序号从0开始）
- `explanation` 用 `<b>` 加粗关键内容

### 2. 判断题（judge）

```json
{
  "type": "judge",
  "topic_name": "注释",
  "content": "# 是 Python 的注释符号。",
  "options": ["对", "错"],
  "answer": "0",
  "explanation": "对的！Python 单行注释用 # 开头。",
  "difficulty": 1
}
```

- `options` 固定 `["对", "错"]`
- `answer` 是 `"0"` 表示“对”，`"1"` 表示“错”

### 3. 计算题（calc）—— 文化类科目带 unit 示例

```json
{
  "type": "calc",
  "topic_name": "万以内加减法",
  "unit": "三年级上册",
  "content": "458 + 376 = ?",
  "options": null,
  "answer": "834",
  "explanation": "列竖式计算：个位8+6=14写4进1，十位5+7+1=13写3进1，百位4+3+1=8，答案是834。",
  "difficulty": 2
}
```

- `options` 填 `null`
- `answer` 是具体答案字符串（如 `"834"`、`"3时20分"`）
- 判分时自动去空格、全角转半角

### 4. 填空题（fill）

**单空填空题：**

```json
{
  "type": "fill",
  "topic_name": "万以内加减法",
  "unit": "三年级上册",
  "content": "小明有12个苹果，给了小红5个，还剩____个。",
  "options": null,
  "answer": "7",
  "blank_count": 1,
  "tolerance": 0,
  "explanation": "12-5=7，还剩7个。",
  "difficulty": 1
}
```

**多空填空题：**

```json
{
  "type": "fill",
  "topic_name": "应用题",
  "unit": "三年级上册",
  "content": "先列算式再求结果：36+36=____，结果是____",
  "options": null,
  "answer": "36+36",
  "blank_count": 2,
  "blank_answers": ["36+36", "72"],
  "tolerance": 0.01,
  "explanation": "36+36=72。",
  "difficulty": 2
}
```

- `blank_count`：填空数量，默认 1
- `blank_answers`：多空题各空答案数组
- `tolerance`：数字容差，0 表示严格匹配，0.01 表示允许小数误差
- 判分时逐空比对，全对才算对

### 5. 应用题（essay）

```json
{
  "type": "essay",
  "topic_name": "看图写话",
  "unit": "三年级上册",
  "content": "请用3-5句话描述这幅图。",
  "options": null,
  "answer": "待老师点评",
  "explanation": "参考：春天来了，小草从地里探出头来...",
  "difficulty": 1
}
```

- 无标准答案，学生自由作答
- `answer` 填 `"待老师点评"` 或参考思路
- 降级策略：作答≥10字即算通过（60分/3星）

### 6. 连线题（match）

```json
{
  "type": "match",
  "topic_name": "词语释义",
  "unit": "三年级上册",
  "content": "将下列词语与其正确的释义连线。",
  "options": ["苹果", "香蕉", "橘子"],
  "match_options": ["黄色水果", "红色水果", "橙色水果"],
  "answer": "0:1,1:0,2:2",
  "explanation": "苹果是红色水果，香蕉是黄色水果，橘子是橙色水果。",
  "difficulty": 1
}
```

- `options`：左侧项目数组（固定顺序）
- `match_options`：右侧选项数组（建议打乱顺序）
- `answer`：匹配关系，格式 `"左索引:右索引,左索引:右索引"`
  - 示例 `"0:1,1:0,2:2"` 表示：左0→右1，左1→右0，左2→右2
- 前端交互：点击左侧项目，再点击右侧选项完成连线

### 7. 排序题（sort）

```json
{
  "type": "sort",
  "topic_name": "洗手步骤",
  "content": "将下列洗手步骤按正确顺序排列。",
  "options": ["先洗手", "打开水龙头", "抹肥皂", "冲干净"],
  "answer": "1,0,2,3",
  "explanation": "正确顺序：打开水龙头→先洗手→抹肥皂→冲干净。",
  "difficulty": 1
}
```

- `options`：打乱顺序的项目数组
- `answer`：正确顺序，格式 `"索引1,索引2,索引3,..."`
  - 示例 `"1,0,2,3"` 表示：第1位是options[1]，第2位是options[0]，第3位是options[2]，第4位是options[3]
- 前端交互：使用 ↑↓ 按钮上下移动项目

### 8. 编程题（code）

```json
{
  "type": "code",
  "topic_name": "变量与标识符",
  "content": "写一个程序，输入一个整数，输出它的两倍。",
  "options": null,
  "answer": "n = int(input())\nprint(n * 2)",
  "expected_output": "10",
  "sample_input": "5",
  "explanation": "先用 input() 获取输入，转成整数，再乘以2输出。",
  "difficulty": 2
}
```

- `answer`：参考代码（学生端隐藏）
- `expected_output`：参考代码运行的预期 stdout
- `sample_input`：参考代码 input() 需要的 stdin 样例
- 判分：沙箱实跑 + LLM 评星反馈

### 9. 阅读理解题（reading）—— 仅语文/英语

```json
{
  "type": "reading",
  "topic_name": "阅读理解",
  "unit": "上册-第一单元",
  "content": "春天来了，小明和小红去公园放风筝。\n风筝飞得很高，他们非常开心。",
  "options": null,
  "reading_items": [
    { "type": "choice", "q": "他们去公园做什么？", "options": ["放风筝", "游泳", "爬山", "钓鱼"], "answer": "0", "explanation": "文中说去公园放风筝。" },
    { "type": "choice", "q": "风筝飞得怎么样？", "options": ["很低", "很高", "飞走了", "掉下来了"], "answer": "1", "explanation": "文中说风筝飞得很高。" }
  ],
  "answer": "0,1",
  "explanation": "",
  "difficulty": 2
}
```

- `content`：文章正文（可用 `\n` 分段）；一篇文章 = 一道题，不要拆散
- `reading_items`：子题数组。当前版本子题**只支持选择题**（`type: "choice"`）；
  `type` 字段预留，后续可扩展 judge（英语 T/F）、fill、essay 子题
- 子题字段：`q`（问题）、`options`（选项）、`answer`（正确选项索引字符串）、`explanation`（讲解）
- `answer`：各子题正确索引的逗号串，如 `"0,1"`（管理后台/导入脚本可自动从子题生成）
- 判分：按子题正确比例给分（对 2/3 ≈ 67 分），≥60 分算通过；整篇进错题本
- 出题要求：文章长度匹配学段（三年级语文 100~200 字、英语 60~100 词），每篇配 2~4 道子题，
  内容以人教版教材话题为准（见根目录 README 出题铁律）

## 四、讲解编写规范（针对 10 岁小朋友）

1. **用小朋友能懂的语言**：浮点数→小数，取模→取余数，布尔→真/假类型
2. **用 emoji 增加趣味**：但不要过度
3. **关键内容加粗**：用 `<b>` 标签
4. **代码用 `<code>` 标签**：如 `<code>print()</code>`
5. **解释为什么**：不只说答案，要说明原因
6. **避免超纲**：只涉及已学知识点，不引入循环/函数/列表等

## 五、导入方式

### 方式一：管理后台网页导入（推荐）

1. 用 admin 账号登录 → 管理后台 → 批量导入 tab
2. 选择科目
3. 粘贴 JSON 到文本框
4. 点击「校验并导入」

### 方式二：脚本导入

1. 将 JSON 保存为 `quiz_system/data/xxx_questions.json`，格式：
```json
{
  "subject": { "name": "科目名", "icon": "📚", "grade": "三年级", "desc": "简介" },
  "questions": [ ...题目数组... ]
}
```
2. 在 `import_questions.py` 的 `SOURCES` 列表中添加该文件路径
3. 运行：`python data/import_questions.py`（自动去重，已存在的题干会跳过）

## 六、出题检查清单

每批题出完后，逐项确认：

- [ ] 每题都有 `type`、`topic_name`、`content`、`answer` 四个必填字段
- [ ] 选择题 `options` 有4个选项，`answer` 是 0-3 的序号
- [ ] 判断题 `options` 是 `["对","错"]`，`answer` 是 `"0"` 或 `"1"`
- [ ] 计算题 `options` 是 `null`，`answer` 是具体答案
- [ ] 答案与讲解语义一致（判断题尤其注意“对/错”不要搞反）
- [ ] reading 题：文章与子题完整（子题均为 choice），answer 与子题索引一致，文章长度匹配学段
- [ ] 讲解用小朋友能懂的语言，无超纲术语
- [ ] 计算题答案已验算
- [ ] 难度标注合理（1=口算，2=需列竖式，3=两步以上）
