# Python 基础理论题库格式

> 适用科目：Python基础理论(id=1)，category=programming
> 导入脚本：`src/data/import_via_api.py`
> 文件格式：**嵌套对象** `{ "subject": {...}, "questions": [...] }`
> 支持题型：choice / judge / calc / **match**（**无** fill/essay/sort/code）

---

## 〇、出题铁律：不超纲、不超出小朋友认知 ⚠️（每题必过）

> 本科目面向 **小学 3-4 年级（8-10 岁）** 小朋友。每道题（含选项、连线左右两列）在出题时都要问一句：
> **「一个没学过这些概念的 9 岁孩子，能不能凭已学知识做对？」** 不能 → 必须换掉或删掉，不得入库。

**硬性红线（出现即作废）：**
- ❌ **不得串课**：只用当前 `topic_name` 章节教过的知识点。函数/返回值、字符串方法（`.upper()/.split()/.replace()/.strip()/.join()/.find()` 等属「字符串查找判断修改」）、列表/字典/元组（属各自章节）、lambda、作用域等**后文章节内容禁止提前出现在前面的课**。
- ❌ 禁止 CPython 内部机制 / 计算机底层：`is` 同一性或对象缓存（`100 is 100`）、`id()`/`dir()`/`help()`/`__dunder__` 双下划线、小整数缓存、字符串驻留、`type: ignore`、类型检查器、docstring/函数返回值等。
- ❌ 禁止超纲数学与类型：复数（`1+2j`）、二进制/八进制/十六进制字面量（`0b`/`0o`/`0x`）、科学计数（`1e3`）、float('inf')、浮点误差（`0.1+0.2!=0.3`）、带步长切片（`[::n]`）、字符串按字典序 `<`/`>` 比较、高级格式化 spec（`{:.2f}`/`{:>5}`/`03d`/`0x`）、`round` 的银行家舍入、`abs()/开平方` 等代码表达。
- ❌ 禁止真实工程概念混入入门题：文件/缓冲区（`file`/`flush`）、日志（logging）、调试工具、`import` 其他模块（`inspect`/`keyword`/`sys`）、`del` 删除变量的报错细节等。

**正确示例（合格）：**
- ✅ 变量命名规则、变量=盒子比喻、`a=b=c` 链式赋值、`x,y=x,y` 交换、中文变量名
- ✅ `#` 注释、`print()` 多内容/`sep`/`end` 基础参数
- ✅ `int/float/str/bool` 类型、`type()`、f-string `f'我{age}岁'`、`+`/`*`/`//`/`%`/`**`/`/` 运算、`len()`、索引 `[0]`/`[-1]`、基础切片 `[:3]`

**为什么这条是铁律**：2026-08-26 人工复核前 3 课（变量与标识符 / 注释与输出函数 / 数值类型与字符串）发现 **48 道超纲题**（多为批量生成的 37xx/39xx/40xx 进阶批次混入入门课，含串课、对象缓存、复数、二/八/十六进制、步长切片、`.upper()/split`、高级格式化等），已全部 `deprecated`。此类题对 9 岁孩子无意义且打击信心。**宁可少几道题，不可上一道超纲题。**

> 出题人/审核人：每题交付前逐题对照本节过一遍；存疑一律废弃，不纠结。

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
  "content": "将数据和类型连线。",
  "options": ["10", "3.14", "'hello'", "True"],
  "match_options": ["整数 int", "小数 float", "字符串 str", "布尔 bool"],
  "answer": "0:0,1:1,2:2,3:3",
  "explanation": "10 是整数；3.14 是小数；带引号的 hello 是字符串；True/False 是布尔。",
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
