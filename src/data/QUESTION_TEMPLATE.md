# 题库 JSON 标准格式规范

> 本文件定义了题库系统的标准题目 JSON 格式。后续出题、批量导入均遵循此格式。

## 一、整体结构

批量导入时，JSON 是一个**题目数组**，每道题是一个对象：

```json
[
  { "type": "choice", "topic_name": "章节名", "content": "题干", "options": ["A","B","C","D"], "answer": "1", "explanation": "讲解", "difficulty": 1 },
  { "type": "judge", "topic_name": "章节名", "content": "题干", "options": ["对","错"], "answer": "0", "explanation": "讲解", "difficulty": 1 },
  { "type": "calc", "topic_name": "章节名", "content": "题干", "options": null, "answer": "834", "explanation": "讲解", "difficulty": 2 }
]
```

## 二、字段说明

| 字段 | 必填 | 类型 | 说明 |
|---|---|---|---|
| `type` | ✅ | string | 题型：`choice`(选择) / `judge`(判断) / `calc`(计算) |
| `topic_name` | ✅ | string | 章节名称。导入时如不存在会**自动创建** |
| `unit` | 可选 | string | 所属单元（仅文化类科目用，如 `"三年级上册"`）。创建章节时一并写入；编程类科目留空 |
| `content` | ✅ | string | 题干内容。可用 `\n` 换行 |
| `options` | 选择/判断必填 | array\|null | 选项数组。选择题通常4个，判断题固定 `["对","错"]`，计算题填 `null` |
| `answer` | ✅ | string | 答案（字符串）。选择题/判断题填选项序号（从0开始），计算题填具体答案 |
| `explanation` | 可选 | string | 错题讲解。支持 HTML 标签如 `<b>`、`<code>`、`<br>` |
| `difficulty` | 可选 | int | 难度 1-5，默认 1。1最简单，5最难 |

## 三、三种题型示例

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
- `answer` 是 `"0"` 表示"对"，`"1"` 表示"错"

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
- [ ] 答案与讲解语义一致（判断题尤其注意"对/错"不要搞反）
- [ ] 讲解用小朋友能懂的语言，无超纲术语
- [ ] 计算题答案已验算
- [ ] 难度标注合理（1=口算，2=需列竖式，3=两步以上）
