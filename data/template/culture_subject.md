# 文化类科目题库格式（语文 / 数学 / 英语）

> 适用科目：语文(id=4)、数学(id=2)、英语(id=5)，category=culture
> 导入脚本：`src/data/import_array.py`
> 文件格式：**纯数组** `[...]`，顶层直接是题目数组（无 subject 包装）

---

## 一、文件整体结构

```json
[
  { "type": "choice", "topic_name": "校园生活", "unit": "上册-第一单元", "content": "...", "options": [...], "answer": "0", "explanation": "...", "difficulty": 1 },
  { "type": "judge", "topic_name": "校园生活", "unit": "上册-第一单元", "content": "...", "options": ["对","错"], "answer": "0", "explanation": "...", "difficulty": 1 }
]
```

**关键点**：
- 顶层是**数组**，不是对象
- 每题必须有 `topic_name`（课时名）和 `unit`（单元名）两个字段
- 导入时按 `topic_name` 自动建/复用课时，`unit` 一并写入
- 按 `content` 去重，相同题干不会重复导入

---

## 二、unit 命名规范（重要）

上下册单元名**必须加册次前缀**，避免重名混淆：

| 册次 | 语文/数学格式 | 英语格式 |
|---|---|---|
| 上册 | `上册-第一单元` ~ `上册-第八单元` | `上册-Unit 1` ~ `上册-Unit 6` |
| 下册 | `下册-第一单元` ~ `下册-第八单元` | `下册-Unit 1` ~ `下册-Unit 6` |

> ⚠️ 不要只写 `"第一单元"` / `"Unit 1"`，否则上下册会混在同一分组。

---

## 三、各题型完整示例（真实线上数据）

### 1. 选择题（choice）

```json
{
  "type": "choice",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'早晨'的'晨'读音是什么？",
  "options": ["chén", "chéng", "chénɡ", "cén"],
  "answer": "0",
  "explanation": "晨读chén，第二声。",
  "difficulty": 1
}
```

- `options`：4 个选项
- `answer`：正确选项索引（字符串，从 0 开始）

### 2. 判断题（judge）

```json
{
  "type": "judge",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'鲜艳'的近义词是'暗淡'。",
  "options": ["对", "错"],
  "answer": "1",
  "explanation": "鲜艳的近义词是艳丽，暗淡是反义词。",
  "difficulty": 1
}
```

- `options` 固定 `["对","错"]`
- `answer`：`"0"`=对，`"1"`=错

### 3. 填空题（fill）

**单空：**
```json
{
  "type": "fill",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'早晨'的拼音是 zǎo ____。",
  "answer": "chén",
  "explanation": "晨读chén。",
  "difficulty": 1,
  "blank_count": 1,
  "tolerance": 0.01
}
```

**多空：**
```json
{
  "type": "fill",
  "topic_name": "万以内加减法",
  "unit": "上册-第三单元",
  "content": "36+36=____，结果是____",
  "answer": "36+36",
  "blank_count": 2,
  "blank_answers": ["36+36", "72"],
  "tolerance": 0.01,
  "explanation": "36+36=72。",
  "difficulty": 2
}
```

- `blank_count`：空的数量（默认 1）
- `blank_answers`：多空时各空答案数组
- `tolerance`：数字容差（0=严格，0.01=允许小数误差）

### 4. 应用题（essay）

```json
{
  "type": "essay",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "用'鲜艳'造一个句子。",
  "answer": "待老师点评",
  "explanation": "参考：同学们穿着鲜艳的民族服装，真好看。",
  "difficulty": 1
}
```

- `answer` 固定 `"待老师点评"`（无标准答案）
- 判分降级：作答≥10字即通过（60分/3星）

### 5. 连线题（match）

```json
{
  "type": "match",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "将词语与拼音连线。",
  "options": ["早晨", "坪坝", "鲜艳", "安静"],
  "match_options": ["ān jìng", "zǎo chén", "xiān yàn", "píng bà"],
  "answer": "0:1,1:3,2:2,3:0",
  "explanation": "早晨zǎo chén，坪坝píng bà，鲜艳xiān yàn，安静ān jìng。",
  "difficulty": 1
}
```

- `options`：左侧项目（固定顺序）
- `match_options`：右侧选项（**建议打乱顺序**）
- `answer`：`"左索引:右索引,..."`，如 `"0:1"` 表示左0→右1

### 6. 排序题（sort）

```json
{
  "type": "sort",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "将下列词语按拼音首字母顺序排列。",
  "options": ["安静", "早晨", "坪坝", "鲜艳"],
  "answer": "0,2,3,1",
  "explanation": "按拼音首字母 a、p、x、z 排列：安静、坪坝、鲜艳、早晨。",
  "difficulty": 2
}
```

- `options`：打乱顺序的项目
- `answer`：正确顺序的索引串，`"0,2,3,1"` 表示第1位=options[0]，第2位=options[2]...
- 判分：全对=100，否则=0

---

## 四、导入命令

```bash
# 语文三上（unit 已含"上册-"前缀，无需 --unit-prefix）
python src/data/import_array.py --subject-id 4 --json data/chinese_grade3_vol1.json --label 语文三上

# 英语三上（源文件 unit 是 "Unit 1"，用 --unit-prefix 加"上册-"）
python src/data/import_array.py --subject-id 5 --json data/english_grade3_vol1.json --label 英语三上 --unit-prefix "上册-"
```

`--unit-prefix` 会给源文件的 `unit` 值统一加前缀。如果源文件 unit 已含前缀则不传此参数。
