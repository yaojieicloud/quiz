# Quiz 题库系统

小朋友刷题系统（FastAPI + SQLite + Docker，部署于 ECS）。

## ⚠️ 出题铁律（永远遵守）

**小朋友的英语、语文、数学课本全部是人教版新课标课本。**

- 英语：人教 PEP 新课标（**2024 年秋季改版**，三年级上册单元为
  U1 Making friends / U2 Different families / U3 Amazing animals /
  U4 Plants around us / U5 The colourful world / U6 Useful numbers）
- 语文：部编版（统编版）
- 数学：人教版

后续为这三个科目生成/补充题目时，**单元、课时、知识点必须与课本保持一致**：
1. 单元名和顺序照课本目录
2. 课时按课本 Part / 课文拆分（英语按 Part A/B/C，语文按课文+语文园地）
3. 单词表、句型、课文内容以教材为准，出题前必须核对教材清单
4. 不得凭旧版教材或记忆杜撰单元内容

## 结构约定

- 文化类科目（语文/数学/英语）：Topic 表用 `unit`（单元）+ `name`（课时）两级组织
- 编程类科目（Python）：按“课”扁平组织，`unit` 留空

## 题型体系（9 种）

| 题型 | type | 适用科目 | 说明 |
|---|---|---|---|
| 选择题 | `choice` | 全部 | 单选/多选 |
| 判断题 | `judge` | 全部 | 固定选项 `["对","错"]` |
| 计算题 | `calc` | 数学/Python理论 | 文本答案，支持数字容差 |
| 填空题 | `fill` | 文化类 | 单空/多空，支持数字容差 |
| 应用题 | `essay` | 数学 | 无标准答案，≥10字即通过（可经科目配置关闭） |
| 连线题 | `match` | 文化类 | 左右项目连线 |
| 排序题 | `sort` | 文化类 | 拖拽/按钮排序 |
| 阅读理解 | `reading` | **仅语文/英语** | 一篇文章 + 多道子题（当前子题均为选择题） |
| 编程题 | `code` | Python实操 | 沙箱实跑 + LLM 评星 |

### 阅读理解（reading，2026-08 新增）

- `content` = 文章正文，`reading_items` = 子题数组，一篇文章就是一道题
- 子题结构：`{"type":"choice", "q":"问题", "options":[...], "answer":"索引", "explanation":"讲解"}`；
  子题 `type` 预留 judge（英语 T/F）/fill/essay 扩展，当前只实现 choice
- 顶层 `answer` 为子题正确索引逗号串（如 `"0,1"`），后台可从子题自动生成
- 判分：按子题正确比例给分（≥60 分算通过），整篇进错题本
- 出题格式详见 `data/template/culture_subject.md` §7 与 `data/template/question_types.md`

### 科目题型配置（allowed_types，2026-08 新增）

- 每个科目可配置允许参与组卷/显示的题型：管理后台 → 编辑科目 → “参与组卷的题型”勾选
- 全勾 = 不限制（`allowed_types` 存 NULL）；未勾选的题型不在学生端显示，也不参与组卷（服务端强制拦截）
- 典型用法：应用题（essay）只在数学科目启用；阅读理解（reading）只在语文/英语启用

## 📊 学情分析（2026-08-04 新增）

管理后台新增「📊 学情分析」tab（admin.html），4 个子面板，帮助全面掌握学员学习情况：

| 面板 | 内容 | 接口 |
|---|---|---|
| 📈 学习总览 | KPI 卡（总答题/正确率/考试次数/活跃学员/今日/近7天）+ 近14天趋势图 + 科目/题型正确率图 + 活跃学员榜 | `GET /api/admin/analytics/overview` |
| 🎒 学员档案 | 选学员看：成绩趋势曲线、各科/知识点正确率、高频错题、最近动态 | `GET /api/admin/analytics/student/{id}` |
| 🎯 薄弱分析 | 薄弱知识点 TOP10（作答≥5次）、反复错题榜（错≥2次未掌握）、低正确率题目（作答≥3次） | `GET /api/admin/analytics/weakness` |
| 🤖 AI 周报 | 一键生成 LLM 学情报告（学习概况/进步亮点/薄弱建议），约10-20秒 | `POST /api/admin/analytics/report` |

技术要点：
- 图表用 ECharts 5.5 CDN（加载失败自动降级提示）
- AI 周报复用 code 题评分的 LLM 通道（qwen3.7-plus），失败返回 502 明确报错、不造假
- 后端 `routers/admin.py` 的 `_fetch_all` 用 SQLAlchemy `.mappings()` 转 dict（勿用 `row.keys()`，2.x 会报 NoSuchColumnError）

## 🐍 Python 实操题库（2026-08-04 扩充至 400 题）

- 20 课 × 20 题（原 10 题/课，新增 10 题/课），三年级趣味生活场景（小明/小猫花花/玩具等）
- 难度 1 为主、每课穿插少量难度 2；`expected_output` 全部由沙箱实跑参考代码生成
- 生成脚本：`src/data/gen_coding_p1.py`（第1-10课）+ `gen_coding_p2.py`（第11-20课）；实跑补 expected_output：`fill_expected_new200.py`
- 导入方式：纯数组 JSON 需包装成 `{subject, questions}` 嵌套格式后用 `import_via_api.py`
