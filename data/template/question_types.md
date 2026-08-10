# 题型字段规范（通用）

> 所有科目共用的 8+1 种题型字段定义。生成任何科目的题目时，先按此规范确认字段格式。

---

## 字段总表

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `type` | string | ✅ | 题型：`choice`/`judge`/`calc`/`fill`/`essay`/`match`/`sort`/`code`/`reading` |
| `topic_name` | string | ✅ | 课时名称。导入时如不存在会自动创建 |
| `unit` | string | 文化类必填 | 所属单元（如 `"上册-第一单元"`）。编程类科目不填或填 null |
| `content` | string | ✅ | 题干。可用 `\n` 换行。**reading 题为文章正文** |
| `options` | array\|null | 视题型 | 选项数组（见各题型说明） |
| `match_options` | array\|null | 连线题必填 | 连线题右侧选项数组。**约束：左侧 `options` 与右侧 `match_options` 各自内部选项文本必须唯一，不得重复**（详见下方「连线题去重约束」） |
| `reading_items` | array\|null | reading 必填 | 阅读理解子题数组（见下方说明） |
| `answer` | string | ✅ | 答案（**必须是字符串**）。格式因题型而异 |
| `is_multiple` | bool | 多选时填 | 仅 choice 用，true=多选题 |
| `blank_count` | int | 填空可选 | 填空数量，默认 1 |
| `blank_answers` | array\|null | 多空必填 | 多空填空各空答案数组 |
| `tolerance` | float | 填空可选 | 数字容差，默认 0.01 |
| `expected_output` | string | code 必填 | 参考代码运行的预期 stdout |
| `sample_input` | string | code 可选 | 参考代码 input() 需要的 stdin 样例 |
| `explanation` | string | 建议填 | 错题讲解，支持 HTML 标签 |
| `difficulty` | int | 建议填 | 难度 1-5，默认 1 |

### reading_items 子题结构（仅 reading 题用）

```json
[
  { "type": "choice", "q": "问题", "options": ["A","B","C","D"], "answer": "1", "explanation": "讲解" }
]
```

- `type`：子题题型，**当前版本只支持 `choice`**（预留 `judge`/`fill`/`essay` 扩展，勿提前使用）
- `q`：子题题干；`options`：选项；`answer`：正确选项索引（字符串）；`explanation`：子题讲解
- 题目顶层 `answer` 填各子题正确索引的逗号串（如 `"0,1"`）；管理后台/导入脚本可自动从子题生成

---

## 各题型 answer 格式速查

| 题型 | answer 格式 | 示例 |
|---|---|---|
| choice（单选） | 正确选项索引（字符串，从0开始） | `"1"` |
| choice（多选） | 逗号分隔的索引串 | `"0,2"` |
| judge | `"0"`=对，`"1"`=错 | `"0"` |
| calc | 具体答案文本 | `"834"`、`"1时35分"` |
| fill（单空） | 答案文本 | `"chén"` |
| fill（多空） | 第一空答案（完整答案在 blank_answers） | `"36+36"` |
| essay | 固定 `"待老师点评"` | `"待老师点评"` |
| match | `"左索引:右索引,..."` | `"0:1,1:3,2:2,3:0"` |
| sort | 正确顺序的索引串 | `"0,2,3,1"` |
| code | 参考代码（学生端隐藏） | `"print('hello')"` |
| reading | 各子题正确索引的逗号串（可与子题自动生成） | `"0,1,2"` |

---

## 连线题去重约束（强制）

连线题（`match`）的判分基于「(左索引, 右项文本)」语义集合。为杜绝"连到右侧第几个重复项"的歧义、保证判分稳定，**左侧 `options` 与右侧 `match_options` 各自内部选项文本必须唯一，不得出现重复文本**。

- ❌ 错误：`match_options: ["True","True","True","False"]`（3 个 True 重复）
- ❌ 错误：`options: ["苹果","苹果","香蕉"]`（左侧也不得重复）
- ✅ 正确：右侧用唯一文本，如 `["True","False"]`；若左侧多个项目都该连到 True，则保证 `match_options` 中 `True` 只出现一次，由多条左项共用
- ✅ 确需区分同类时，用唯一表述：`["True（第1个）","True（第2个）"]`，并在 `answer` 中连到对应索引

> 导入脚本应在写入前校验左右两侧去重，发现重复应报错而非静默入库。

---

## 判分规则（了解即可，不影响出题格式）

| 题型 | 判分方式 |
|---|---|
| choice/judge/calc | 对=100(5星)，错=0(0星)，不调 LLM |
| fill | 逐空比对，全对=100，支持数字容差 |
| essay | 降级判分：作答≥10字=60分(3星)通过 |
| match/sort | 全对=100(5星)，否则=0，不调 LLM |
| code | 沙箱实跑 + LLM 评星，LLM 不可用时降级为 stdout 匹配 |
| reading | 按子题正确比例给分（对2/3≈67分），≥60分算通过；整篇进错题本 |

---

## 讲解编写规范（针对 10 岁小朋友）

1. **用小朋友能懂的语言**：浮点数→小数，取模→取余数，布尔→真/假类型
2. **用 emoji 增加趣味**：但不要过度
3. **关键内容加粗**：用 `<b>` 标签
4. **代码用 `<code>` 标签**：如 `<code>print()</code>`
5. **解释为什么**：不只说答案，要说明原因
6. **避免超纲**：只涉及已学知识点

---

## 常见错误（务必避免）

| 错误 | 正确做法 |
|---|---|
| `"answer": 1`（数字） | `"answer": "1"`（字符串） |
| 判断题 options 写成 `["正确","错误"]` | 必须 `["对","错"]` |
| 连线题漏写 `match_options` | 右侧选项必须填 |
| 连线题左右两侧选项文本重复（如多个 `True`/`int`） | 左侧 `options` 与右侧 `match_options` 各自文本必须**唯一**；重复会让"连到哪个实例"产生歧义、判分不稳。确需同类多连时改用唯一表述（如 `True(第1个)`）或拆分为多题 |
| 排序题 answer 索引越界 | 索引必须在 0~options长度-1 范围内 |
| 上下册 unit 都写 `"第一单元"` | 加前缀：`"上册-第一单元"` / `"下册-第一单元"` |
| code 题 expected_output 未实跑验证 | 必须实际运行参考代码确认输出 |
| reading 题漏写 reading_items 或子题 answer 越界 | 每个子题必须有 q/options/answer，索引须在选项范围内 |
| reading 题文章和子题拆成多道独立题 | 一篇文章必须是一道 reading 题（子题在 reading_items 里） |
| 给数学/Python 科目出 reading 题 | reading 仅用于语文/英语（科目题型配置也会拦截） |
