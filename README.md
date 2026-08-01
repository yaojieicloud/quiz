# 题库闯关系统 — 项目手册（Project Handbook）

> **用途**：本手册供开发者（AI / 人）快速接手本项目。重读即可进入状态，无需回溯历史对话。
> **最后更新**：2026-08-02
> **范围**：`quiz_system/` 为线上运行系统；工作区根目录的 `python_quiz0506*.html`、`math_grade3*.html` 是早期**独立原型**，与线上系统无关，勿混淆。

---

## 0. 协作约定（军规）

用户明确的工作方式，务必遵守：

1. 用户提想法 → 我梳理分析 → 我提问澄清 → **用户最终确认后才执行**。
2. **严禁**超出已沟通范围自作主张（如未确认就部署、改库、重构）。
3. 文档类需求同样遵循：先给结构/补充建议，确认后再落笔。

---

## 1. 项目概览

**定位**：为 10 岁小朋友（覃禹诺）设计的**题库闯关学习系统**。

**核心能力**：
- 多用户 / 多科目 / 多章节
- 组卷答题（按科目+章节随机抽题）
- 错题本、学习统计、家长视角
- code 题型（Python 实操）**后台沙箱实跑判分** + LLM 评星反馈
- 浏览器内代码编辑器（语法高亮 + 智能提示 + Pyodide 本地运行）

**题目规模**（约 1250 题）：
| 科目 | id | 题量 | 章节 | category | 题型 |
|---|---|---|---|---|---|
| Python 基础理论（原名 Python 入门） | 1 | 1000 | 20 章 × 50 | programming | choice/judge/calc |
| Python 基础实操（原名 Python 实操） | 3 | 200 | 20 章 × 10（线上 topic id 45~64） | programming | **code** |
| 数学（三年级） | — | 50 | 13 章 | culture | choice/judge/calc |

> 线上章节 topic id 为 45~64（名称固定），重灌题需保持名称一致以复用。

---

## 2. 技术栈与运行环境

**后端**：FastAPI + SQLAlchemy 2.0（async）+ SQLite + JWT 认证。

**关键依赖决策（坑）**：
- **密码哈希用 `pbkdf2_sha256`**（纯 Python），不引 bcrypt —— Windows 沙箱编译会失败。
- **pydantic 用宽松版 `2.13.4`**，不锁 `2.7.1` —— pydantic-core 无 Python 3.13 的 wheel。

**前端**：原生 HTML/JS + CodeMirror 5（UMD 同步加载）+ Pyodide v0.26.4（浏览器内 Python）。

**本地运行环境**（managed Python）：
```
Python venv : C:\Users\Yaojie\.workbuddy\binaries\python\envs\default
启动命令   : python -m uvicorn main:app --host 127.0.0.1 --port 8000   # 不带 --reload
杀进程     : Stop-Process -Id <pid> -Force   (PowerShell)
```
**数据库**：SQLite，本地 `quiz_system/quiz.db`；线上 `/app/quiz.db`（挂载同卷持久化）。

---

## 3. 系统架构与文件结构

```
quiz_system/
├── main.py                 # FastAPI 入口、JWT、CORS、路由挂载
├── models.py               # SQLAlchemy 模型（8 张表）
├── schemas.py              # Pydantic 出入参（含 *Out 必须含 is_correct）
├── database.py             # 引擎 / Session
├── auth.py                 # 密码哈希(pbkdf2) / JWT 签发校验
├── core/
│   ├── code_runner.py      # Python 沙箱实跑（见 §9 三个坑）
│   └── llm_grader.py       # code 题 LLM 评星反馈（不可用时降级）
├── routers/
│   ├── exam.py             # 组卷/提交/判分/run-code/错题
│   ├── questions.py        # 题目 CRUD / 列表（非 admin 隐藏 code 答案）
│   └── admin.py            # 管理后台 API（update-file/exec-sql/restart/学员记录）
├── static/
│   ├── login.html home.html quiz.html records.html wrong.html
│   ├── stats.html parent.html admin.html   # 7 学员页 + 家长 + 后台
│   ├── js/common.js        # renderAnswerCard 等共用渲染
│   └── css/common.css
└── data/
    ├── push_ecs.py         # 热部署推送 14 文件
    ├── import_via_api.py   # 灌题（content 去重）
    ├── import_py500.py     # 早期批量导入
    ├── gen_expected.py     # 生成 code 题 expected_output
    ├── verify_ecs.py       # 端到端验证
    ├── qa_full_test*.py    # 后端测试
    └── python_coding200.json  # 实操题源数据
```

**热部署 14 文件清单**（push_ecs.py 的 `FILES`）：
`models.py schemas.py routers/exam.py routers/questions.py routers/admin.py core/code_runner.py core/llm_grader.py static/admin.html static/js/common.js static/quiz.html static/home.html static/records.html static/wrong.html static/css/common.css`

---

## 4. 数据模型

**8 张表**：`user` / `subject` / `topic` / `question` / `exam_record` / `answer_record` / `wrong_question` / `parent_child`。

**Subject.category**：
- `culture`：文化类，按 `unit` 分组（如数学按"三年级上/下册"）
- `programming`：编程类，扁平选题（`topic.unit` 留 NULL）

**Question.type**（题型）：`choice`(选择) / `judge`(判断) / `calc`(计算/代码结果填空) / **`code`**(代码题，后台实跑判分)。

**code 题型新增列**：
- `questions` 表：`expected_output(Text)`、`sample_input(Text, default="")`
- `answer_records` 表：`run_output(Text)`、`llm_score(Integer)`、`llm_stars(Integer)`、`llm_feedback(Text)`

**关键业务规则**：
- code 题参考代码对学生隐藏：`exam.py _build_question_out` 与 `questions.py list_questions`（非 admin）把 code 题 `answer` 置 `None`。
- `AnswerRecordOut` schema **必须含 `is_correct` 字段**（老数据 `llm_score=NULL` 时前端靠它判断对错）。
- 注册暗号是 **query 参数**：`POST /api/auth/register?regkey=openschool2026`（不是 body 字段）。

---

## 5. 功能清单（当前）

**学员端 7 页**：登录 / 首页组卷 / 答题 / 答题记录 / 错题本 / 学习统计 / 家长视角。

**管理后台 `admin.html`**：
- 科目 / 章节 / 题目 CRUD + JSON 批量导入
- **学员答题 tab**：选学员 → 记录列表 → 每题详情（实操题显示学生代码 / 运行结果 / 参考代码；admin 视角不隐藏 code 答案）
- 弹层 CSS：`max-height:85vh + overflow-y:auto`，防内容截断

**实操题（code）答题区**（`quiz.html`）：
- CodeMirror 5 语法高亮 + **智能提示**（自动按前缀补全关键字，Ctrl/Cmd-Space 手动触发）
- 「▶ 运行代码（服务端）」→ `POST /api/exam/run-code`（沙箱实跑，不判分不落库）
- 「🧠 浏览器内运行」→ Pyodide v0.26.4 本地跑（lazy 加载 + `requestIdleCallback` 预加载）

**判分逻辑**（`routers/exam.py _judge / _judge_code`）：
- choice/judge/calc：对=100(5星)，错=0(0星)，**不调 LLM**
- code：先沙箱实跑 → 调 LLM 评星反馈；LLM 不可用时降级为 stdout 匹配（匹配成功=100）
- `is_correct = (llm_score >= 60)`（3 星及以上算通过）
- **score 公式**：`record.score = int(correct / total * 100)` —— **严禁 `sum(answer_scores)`**（会出 1400/5000 这类错误）

**答题记录详情**：学员端 `records.html` 与管理端 `admin.html` 共用 `js/common.js` 的 `renderAnswerCard(q, ar, opts)`，差异仅 `opts.showRefCode`（学员 false / 管理员 true）。`records.html` 每题始终展开便于复盘。

---

## 6. API 速查

> 完整请求/响应字段见 `routers/*.py` 与 `schemas.py`。

**认证**
- `POST /api/auth/register?regkey=openschool2026`
- `POST /api/auth/login` → `{access_token}`

**科目 / 题目**
- `GET /api/subjects`
- `GET /api/questions`（列表；非 admin 隐藏 code 答案）
- 题目 CRUD（admin）

**组卷 / 答题**（`routers/exam.py`）
- 组卷 start、提交 submit（具体签名见 `exam.py`）
- `POST /api/exam/run-code` `{code, sample_input}` → `{output, error, rc}`（需登录，不判分不落库）
- `GET /api/exam/records`（答题记录）
- `GET /api/wrong`（错题本；填充 `user_answer/run_output/llm_feedback/subject_name`）
- 学习统计接口（stats 页）

**管理后台**（`routers/admin.py`）
- `GET /api/admin/students`、`GET /api/admin/students/{id}/records`、`GET /api/admin/records/{id}`
- `POST /api/admin/update-file` `{path, content}`（热部署写 `/app`）
- `POST /api/admin/exec-sql` `{script:true, sql}`（多语句；**先 VACUUM 备份同卷**）
- `POST /api/admin/restart`（`os._exit(0)` → docker `restart:always` 自动重启）
- `GET /api/health` → `{"status":"ok"}`

---

## 7. 维护与部署流程（ECS 热部署）

**线上环境**：`http://106.14.99.100:8000`，admin/admin123，注册暗号 `openschool2026`（线上环境变量 `QUIZ_REGKEY=openschool2026`）。

**改前端 / 后端 Python**：
1. 本地改完 → `python data/push_ecs.py`（POST `/api/admin/update-file` 写 `/app`）
2. **前端改动无需 restart**；**后端 Python 改动需** `POST /api/admin/restart`
3. 重启后 `GET /api/health` 应返回 `{"status":"ok"}`

**改 DB schema**：
- `POST /api/admin/exec-sql`，`script:true` 跑多语句（接口先 VACUUM 备份）
- 加列用 `ALTER TABLE ... ADD COLUMN`（脚本会先备份）

**灌题**：`python data/import_via_api.py`（默认 `python_coding200.json`，已加 content 去重，发送 `expected_output/sample_input`）。

**端到端验证**：`python data/verify_ecs.py`（注册测试生 → 单题闯关 → 正确/改坏/语法错三提交 → 断言 → 清理）。

> ⚠️ **重复导入坑**：早期 batch 导入无去重，同一 JSON 跑两次会翻倍；`import_via_api.py` 已加 content 去重。

---

## 8. 扩展方式（加科目 / 题目）

- **加语文/英语等科目**：管理后台或 import 脚本添加，**不改代码**（`Subject.category` 决定分组方式）。
- **出题规范（踩坑）**：
  - JSON 转义：`\'` 非法，要显示 `\'` 需写 `\\'`；`\d` 非法转义
  - 换行：题干用 `\n` 换行；要显示字面 `\n` 需写 `\\n`
  - `field` 格式 `"explanation":"` 缺冒号会报错
  - `answer` 类型必须是**字符串**，不能是 int
  - 大批量 JSON 错误用 Python `replace/re.sub` 修复，不逐个手改
  - 生成脚本用 Write 写独立 `.py`，用 `json.dump` 输出确保格式
- **导入流程**：题目 JSON 存 `data/py500/batch*.json` → `import_py500.py` 用 glob 读取，按 `topic_name` 建章节、按 `content` 去重 → 不足则 `batch_supplement.json` 补题。
- 出题规范文档：`data/QUESTION_TEMPLATE.md`。

**20 个 Python 知识点（章节名）**：
变量与标识符 / 注释与输出函数 / 数值类型与字符串 / 算术赋值与输入转义 / if判断与比较逻辑运算 / if-else与嵌套if / while循环与嵌套循环 / 字符串查找判断修改 / 列表与列表推导式 / 元组与字典 / 类型转换 / 赋值与深浅拷贝 / 函数与返回值 / 函数参数与嵌套 / 作用域与匿名函数 / lambda与内置函数 / 内置函数与拆包 / 异常模块与包 / 闭包与装饰器 / 标准装饰器与语法糖

---

## 9. 决策日志（防重蹈覆辙 — 最重要）

**已踩坑及结论，未来禁止重犯 / 重改：**

1. **密码哈希用 `pbkdf2_sha256`**，别引 bcrypt（Windows 沙箱编译失败）。
2. **pydantic 用宽松版 `2.13.4`**，别锁 `2.7.1`（pydantic-core 无 3.13 wheel）。
3. **`core/code_runner.py` 三个坑（已修）**：
   - 导入守卫不能用 `builtins.__import__=_g` 后又在 `_g` 内调 `_b.__import__`（死递归）→ 必须先 `_real_import=_b.__import__` 再覆盖。
   - **禁止列表不要含 `sys`/`builtins`**：`functools`/`collections` 等标准库内部 `import sys`，拦了会连累正常代码。危险的是 `os/subprocess/socket/shutil/ctypes/importlib/multiprocessing` 等。
   - `python -I` 隔离模式下 `PYTHONUTF8=1` 环境变量**不生效**，中文 stdout 被吞 → 必须用命令行参数 `-X utf8`。
   - 运行命令：`[sys.executable, "-I", "-X", "utf8", fpath]` + 临时目录 + 导入守卫 + 环境变量剥离（仅 PATH/LANG/LC_*/TEMP）+ 超时 6s。
4. **score 公式用 `int(correct/total*100)`**，严禁 `sum(answer_scores)`（每题 100 累加会出 1400/5000）。
5. **`AnswerRecordOut` 必须含 `is_correct` 字段**，前端优先用它判断对错（降级 `llm_score>=60`）。
6. **submit 校验**：空 `answers` → 400；所有 `question_id` 必须存在否则 400。
7. **code 题参考代码对学生隐藏**（`_build_question_out` / `list_questions` 非 admin 置 None）。
8. **注册暗号是 query 参数 `regkey`**，不是 body 字段。
9. **代码编辑器演进结论（重要）**：
   - ❌ 绝不用 `contenteditable` 做代码编辑器（换行/IME/光标行为不可控）。
   - ❌ 不用 CodeMirror 6（ESM 只支持异步链 esm.sh，国内网络不稳，编辑器不显示）。
   - ✅ 用 **CodeMirror 5（UMD 同步加载）**，10+ 年成熟，中文 IME 安全。
   - ⚠️ **`anyword-hint` 忽略 `words` 参数**——它只补全文档内已出现的词。空白文件输入 `pri` 弹不出 `print`。已改为自定义 `pythonHint(cm)`（按光标前词前缀过滤 `PY_HINT_WORDS`）+ `CodeMirror.registerHelper('hint','python',pythonHint)`。
10. **前端改动 push 后无需 restart；后端 Python 改动必须 `POST /api/admin/restart`**。
11. **改 DB schema 用 exec-sql + `ALTER TABLE ADD COLUMN`**，接口先 VACUUM 备份。
12. **Pyodide 按钮曾因 `display:none` 未切换而隐藏** —— 已移除并加 `requestIdleCallback` 预加载，加载完文案变「（已就绪）」。

---

## 10. 环境与密钥清单 + 应急手册

**环境 / 密钥**（散落各处，集中于此）：
| 项 | 值 |
|---|---|
| 线上地址 | `http://106.14.99.100:8000` |
| admin 账号 | `admin` / `admin123` |
| 注册暗号 | `openschool2026`（线上 env `QUIZ_REGKEY`；本地注册 `?regkey=openschool2026`） |
| Pyodide CDN | `https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js` |
| CodeMirror 5 CDN | `https://cdn.jsdelivr.net/npm/codemirror@5.65.18/...` |
| 本地 DB | `quiz_system/quiz.db`；线上 `/app/quiz.db`（同卷） |

**应急手册**：
- **站点打不开**：先 `GET /api/health`；若超时，可能容器挂了 → 检查 ECS / docker；若 500，看后端日志，必要时 `POST /api/admin/restart`。
- **改 DB schema 安全步骤**：`POST /api/admin/exec-sql`（`script:true`）→ 接口自动 VACUUM 备份到同卷 → 只用 `ALTER TABLE ADD COLUMN` 加列（别 DROP/改类型）。
- **改后端后不生效**：确认 push 了 14 文件 **且** 调了 `POST /api/admin/restart`（前端改动不用）。
- **重复导入翻倍**：用 `import_via_api.py`（已 content 去重），别直接跑早期 batch 导入。
- **CDN 不可达**：CodeMirror 5 加载失败自动降级纯 textarea（仍可编辑）；Pyodide 不可用则只能用「服务端运行」按钮。

---

## 11. 历史脏数据清单（看似 BUG 实为遗留）

以下问题**不是代码 bug**，是早期校验缺失时的遗留数据，新提交已加校验不会再产生：
- `exam_record` #11、#12 为空记录（无答案）。
- 51 条 `answer_record` 为空答案（历史提交缺失）。
- 5 条 `record.score` 与 `correct/total` 计算有舍入差异（旧逻辑遗留）。

> 排查时遇到上述特征，直接判定为历史脏数据，不要在代码层"修"。

---

## 12. 测试 / 验证脚本索引

| 脚本 | 用途 |
|---|---|
| `data/qa_full_test.py` / `qa_full_test2.py` | 后端测试：auth / run-code 安全 / 数据一致性 / subjects / exam / submit / grading / records / admin |
| `data/verify_ecs.py` | 端到端：注册测试生 → 单题闯关 → 正确/改坏/语法错三提交 → 断言 → 清理 |
| `data/import_via_api.py` | 灌题（默认 `python_coding200.json`，content 去重，发 `expected_output/sample_input`） |
| `data/gen_expected.py` | 读 `python_coding200.json`，对含 `input()` 的题从题干"参考(…)"解析 `sample_input`，实跑算 `expected_output` 写回 |
| `data/push_ecs.py` | 热部署推送 14 文件到 ECS |
| `data/import_py500.py` | 早期批量导入 `py500/batch*.json`（按 topic_name 建章节、content 去重） |

---

## 13. Day-one 上手清单

新会话接手，按序执行：

1. **读本手册 §1–§9** 建立全局认知（重点看 §9 决策日志，避免重踩）。
2. **扫一遍 `quiz_system/` 结构**，重点：`routers/exam.py`、`core/code_runner.py`、`static/quiz.html`、`schemas.py`。
3. **本地起服务**：venv 激活 → `python -m uvicorn main:app --host 127.0.0.1 --port 8000`。
4. **改前端验证**：改 `static/quiz.html` → `python data/push_ecs.py` → 浏览器硬刷新（Ctrl+Shift+R）。
5. **改后端验证**：改 Python → push → `POST /api/admin/restart` → `GET /api/health` 确认 `{"status":"ok"}`。
6. **加题**：`python data/import_via_api.py` 或 admin 后台；遵守 §8 出题规范。
7. **任何改动后跑** `data/verify_ecs.py` 做端到端回归。

---

*本手册由项目沉淀整理，覆盖技术栈、架构、功能、API、维护、决策日志与应急手册。重读即进入状态。*
