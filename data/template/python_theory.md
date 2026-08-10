# Python 基础理论题库格式

> 适用科目：Python基础理论(id=1)，category=programming
> 导入脚本：`src/data/import_via_api.py`
> 文件格式：**嵌套对象** `{ "subject": {...}, "questions": [...] }`
> 支持题型：choice / judge / calc / **match**（**无** fill/essay/sort/code）

---

## 一、文件整体结构

```json
{
  "subject": {
    "name": "Python基础理论",
    "icon": "🐍",
    "grade": "入门",
    "desc": "Python 基础理论知识"
  },
  "questions": [
    { "type": "choice", "topic_name": "变量与标识符", "content": "...", "options": [...], "answer": "1", "explanation": "...", "difficulty": 1 },
    { "type": "judge", "topic_name": "变量与标识符", "content": "...", "options": ["对","错"], "answer": "0", "explanation": "...", "difficulty": 1 }
  ]
}
```

**关键点**：
- 顶层是**对象**，包含 `subject` 和 `questions` 两个键
- `questions` 是题目数组
- **不填 `unit` 字段**（编程类科目无单元概念，`topic_name` 即 20 个知识点章节）
- 导入时按 `topic_name` 自动建/复用章节

---

## 二、subject 字段说明

| 字段 | 说明 | 示例 |
|---|---|---|
| `name` | 科目名称（必须与线上已有科目名匹配） | `"Python基础理论"` |
| `icon` | emoji 图标 | `"🐍"` |
| `grade` | 学段/级别 | `"入门"` |
| `desc` | 科目简介 | `"Python 基础理论知识"` |

---

## 三、20 个知识点章节（topic_name 取值）

Python 理论科目共 20 个章节，出题时 `topic_name` 必须使用以下名称之一：

```
变量与标识符 / 注释与输出函数 / 数值类型与字符串 / 算术赋值与输入转义
if判断与比较逻辑运算 / if-else与嵌套if / while循环与嵌套循环 / 字符串查找判断修改
列表与列表推导式 / 元组与字典 / 类型转换 / 赋值与深浅拷贝
函数与返回值 / 函数参数与嵌套 / 作用域与匿名函数 / lambda与内置函数
内置函数与拆包 / 异常模块与包 / 闭包与装饰器 / 标准装饰器与语法糖
```

---

## 四、各题型完整示例

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

- `options`：4 个选项
- `answer`：正确选项索引（字符串，从 0 开始）
- 不填 `unit`

### 2. 判断题（judge）

```json
{
  "type": "judge",
  "topic_name": "注释与输出函数",
  "content": "# 是 Python 的注释符号。",
  "options": ["对", "错"],
  "answer": "0",
  "explanation": "对的！Python 单行注释用 # 开头。",
  "difficulty": 1
}
```

- `options` 固定 `["对","错"]`
- `answer`：`"0"`=对，`"1"`=错

### 3. 计算题（calc）

```json
{
  "type": "calc",
  "topic_name": "算术赋值与输入转义",
  "content": "Python 中 7 // 2 的结果是？",
  "options": null,
  "answer": "3",
  "explanation": "// 是整除运算符，7÷2=3余1，整除取整数部分 <b>3</b>。",
  "difficulty": 1
}
```

- `options` 填 `null`
- `answer` 是具体答案字符串
- 判分时自动去空格、全角转半角

### 3b. 连线题（match，Python 理论科目已支持）

```json
{
  "type": "match",
  "topic_name": "数值类型与字符串",
  "content": "将数值字面量与类型连线。",
  "options": ["10", "3.14", "0b101", "0x1A"],
  "match_options": ["int", "float", "int（二进制）", "int（十六进制）"],
  "answer": "0:0,1:1,2:2,3:3",
  "explanation": "10 是整数 int；3.14 是 float；0b 开头是二进制整数；0x 开头是十六进制整数。",
  "difficulty": 1
}
```

- `options`：左侧项目数组（**内部文本必须唯一，不得重复**）
- `match_options`：右侧选项数组（**不可留 `null`**；**内部文本必须唯一，不得重复**）
- `answer`：`"左索引:右索引,左索引:右索引"`，索引从 0 开始，逗号分隔
- 判分按「(左索引, 右项文本) 集合」比对，**忽略连线顺序**
- ⚠️ **去重约束**：左右两侧选项文本各自唯一，重复文本会让判分产生歧义（见 `question_types.md` 连线题去重约束）。本例 `int / float / int（二进制） / int（十六进制）` 即为唯一文本的规范写法——`int（二进制）` 与 `int（十六进制）` 必须分开写，不可都写 `int`

---

## 五、导入命令

```bash
python src/data/import_via_api.py --json src/data/py500/batch1.json
```

- 自动按 `content` 去重（重跑不翻倍）
- `subject.name` 必须与线上已有科目名匹配，否则会尝试创建新科目

---

## 六、注意事项

1. **不填 `unit`**：编程类科目无单元概念
2. **`topic_name` 必须用 20 个知识点章节名之一**：否则会自动创建新章节
3. **answer 必须是字符串**：`"1"` 不是 `1`
4. **讲解用小朋友能懂的语言**：避免超纲术语
