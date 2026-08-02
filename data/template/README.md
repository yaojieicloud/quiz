# 题库导入格式规范（总入口）

> **用途**：大模型 / 开发者生成题目时的格式参考。读此文件即可了解所有科目的题目 JSON 格式。
> **最后更新**：2026-08-03
> **关联**：[quiz README.md](../../README.md) §4 数据模型 / §8 扩展方式

---

## 一、科目分类与格式选择

| 科目 | id | category | 文件格式 | 支持题型 | 模板文件 |
|---|---|---|---|---|---|
| 语文 | 4 | culture | 纯数组 `[...]` | choice/judge/fill/essay/match/sort | [culture_subject.md](culture_subject.md) |
| 数学(三年级) | 2 | culture | 纯数组 `[...]` | choice/judge/fill/essay/match/sort | [culture_subject.md](culture_subject.md) |
| 英语 | 5 | culture | 纯数组 `[...]` | choice/judge/fill/essay/match/sort | [culture_subject.md](culture_subject.md) |
| Python基础理论 | 1 | programming | 嵌套 `{subject, questions}` | choice/judge/calc | [python_theory.md](python_theory.md) |
| Python基础实操 | 3 | programming | 嵌套 `{subject, questions}` | **code** | [python_practical.md](python_practical.md) |

**格式选择规则**：
- 文化类科目（语文/数学/英语）→ 用 `culture_subject.md` 模板（纯数组 + `unit` 字段）
- Python理论 → 用 `python_theory.md` 模板（嵌套对象 + 无 `unit`）
- Python实操 → 用 `python_practical.md` 模板（嵌套对象 + code 题专用字段）

---

## 二、题型字段规范（通用）

所有科目共用的 7 种题型字段定义，详见 [question_types.md](question_types.md)。

| 题型 | type 值 | 必填字段 | 特殊字段 |
|---|---|---|---|
| 选择题 | `choice` | options, answer(索引) | is_multiple(多选) |
| 判断题 | `judge` | options=["对","错"], answer("0"/"1") | — |
| 计算题 | `calc` | answer(文本) | — |
| 填空题 | `fill` | answer(文本) | blank_count, blank_answers, tolerance |
| 应用题 | `essay` | answer="待老师点评" | — |
| 连线题 | `match` | options(左侧), match_options(右侧), answer("左:右,...") | — |
| 排序题 | `sort` | options(打乱项), answer("索引,...") | — |
| 编程题 | `code` | answer(参考代码), expected_output, sample_input | — |

---

## 三、导入方式

### 文化类科目（语文/数学/英语）

使用 `import_array.py`：

```bash
python src/data/import_array.py --subject-id 4 --json data/chinese_grade3_vol1.json --label 语文三上
python src/data/import_array.py --subject-id 5 --json data/english_grade3_vol1.json --label 英语三上 --unit-prefix "上册-"
```

- 自动按 `topic_name` 建/复用课时（带 `unit`）
- 自动按 `content` 去重（重跑不翻倍）
- `--unit-prefix` 给单元名加前缀（如 "上册-"、"下册-"），避免上下册重名

### Python理论

使用 `import_via_api.py`：

```bash
python src/data/import_via_api.py --json src/data/py500/batch1.json
```

### Python实操

使用 `import_via_api.py`（默认读 `python_coding200.json`）：

```bash
python src/data/import_via_api.py
```

---

## 四、注意事项

1. **answer 必须是字符串**：`"1"` 不是 `1`
2. **unit 命名**：文化类科目上下册用 `"上册-第X单元"` / `"下册-Unit X"` 格式，避免重名
3. **连线题 match_options**：右侧选项建议打乱顺序，`answer` 格式为 `"左索引:右索引,..."`
4. **排序题 answer**：正确顺序的索引串，如 `"1,0,2,3"` 表示第1位是 options[1]
5. **code 题**：`expected_output` 必须实际运行参考代码验证，`sample_input` 是 input() 需要的输入
6. **去重机制**：导入脚本按 `content` 去重，相同题干不会重复导入

---

## 五、出题检查清单

每批题出完后逐项确认：

- [ ] 每题都有 `type`、`topic_name`、`content`、`answer` 四个必填字段
- [ ] 文化类科目每题都有 `unit` 字段
- [ ] 选择题 `options` 有 4 个选项，`answer` 是 0-3 的序号字符串
- [ ] 判断题 `options` 是 `["对","错"]`，`answer` 是 `"0"` 或 `"1"`
- [ ] 连线题 `match_options` 非空，`answer` 格式正确
- [ ] 排序题 `answer` 覆盖所有索引（如 4 项则为 0,1,2,3 的某种排列）
- [ ] code 题 `expected_output` 已实跑验证
- [ ] 答案与讲解语义一致（判断题"对/错"不要搞反）
- [ ] 讲解用小朋友能懂的语言，无超纲术语
