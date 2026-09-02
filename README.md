# Quiz 题库系统

> 面向小朋友的刷题系统：做题赚积分 → 大转盘 / 直兑激励。技术栈 **FastAPI + SQLite + Docker**，原生多页 HTML/JS，部署于阿里云 ECS。
>
> **这份 README 是系统总入口**：想知道「有什么功能、怎么设计、怎么编码、怎么部署、怎么维护」，按下面的链接点进 `docs/design/` 对应文档即可。

---

## 📚 文档导航（先读这里）

所有设计与运维细节都在 `docs/` 下，README 只做索引与概览。

**设计文档 `docs/design/`（按模块拆分，每个功能一份）**

| 文档 | 讲什么 |
|---|---|
| [系统架构总览](docs/design/系统架构总览.md) | 技术栈、角色权限、模块路由、请求流向、数据模型、目录布局、常量速查 |
| [用户与权限](docs/design/用户与权限.md) | 学生/家长/管理员三角色、JWT 鉴权、注册 regkey、家长绑娃 |
| [科目与知识点体系](docs/design/科目与知识点体系.md) | 科目→课→题三级结构、allowed_types 题型闸门、题目 CRUD/批量导入 |
| [题型与出题规范](docs/design/题型与出题规范.md) | 9 种题型判分逻辑、归一化、阅读理解、应用题降级 |
| [组卷与答题流程](docs/design/组卷与答题流程.md) | 组卷白名单、交卷判分、积分发放、记录与错题本 |
| [积分与奖励体系](docs/design/积分与奖励体系.md) | 积分流水、积分矩阵、转盘权重、直兑核销、种子数据 |
| [AI 评分与学情报告](docs/design/AI评分与学情报告.md) | 代码沙箱、LLM 双通道、code 题评星、AI 周报 |
| [掌握度与学情联动](docs/design/掌握度与学情联动设计.md) | 掌握度持久化表、三硬门槛算法、积分闸门、学员×课程矩阵、与薄弱分析联动 |
| [管理后台与学情分析](docs/design/管理后台与学情分析.md) | 9 tab 总台（2026-08-24 起移除「科目积分」）、学情分析 5 子页、最近动态接口、记录管理、掌握度矩阵 |
| [数据库迁移机制](docs/design/数据库迁移机制.md) | 轻量迁移器原理、迁移文件格式、加字段标准流程、幂等要点 |
| [部署与运维](docs/design/部署与运维.md) | 本地/ECS 部署、热更新、拉库脚本、运维 API（exec-sql/backup/restart） |

**方案与规划 `docs/plan/`（提案类，非当前实现）**

- [积分系统 + 大转盘设计方案](docs/plan/积分系统与大转盘方案.md)
- [实时出题改造方案](docs/plan/实时出题改造方案.md)
- [未来规划](docs/plan/未来规划.md)

**开发规范与协作流程（it-workflow）**

本仓库遵循 **it-workflow** 流程（需求 → 方案设计 → 任务拆解 → 开发 → 文档同步 → 验收，Bug 流程同样两次确认门）；指令：`/需求` `/设计` `/任务` `/问题` `/测试` `/讨论` `/继续` `/暂停` `/帮助`；编号：需求 `REQ-{N}` / 设计 `REQ-{N}-{M}` / 任务 `REQ-{N}-{M}-{K}` / 问题单 `BUG-{N}`。骨架见 `docs/init/`、`docs/overview.md`、进度 `docs/PROGRESS.md`；历史协作铁律（教材/文档先行/安全红线）承自 `CODEBUDDY.md`，仍作项目约定。

- [Git 协作规范 `docs/init/git-workflow.md`](docs/init/git-workflow.md) — AI 代推送前提、标准流程、禁止行为（credential helper 走 GitHub Desktop）

- [习题人工复核规范](docs/qa/manual-review.md) — 全科目题目正确性/选项合理性/超纲判定（5 检查点 + 正材清单 + 废弃正路流程）
- [自动核对计划 check-plan](docs/qa/python-theory-check-plan.md) — 结构/答案判定 PASS/FIX/DROP
- 需求索引 `docs/requirements/INDEX.md`；问题单 `docs/issues/INDEX.md`

---

## ⚠️ 出题铁律（永远遵守）

**小朋友的英语、语文、数学课本全部是人教版新课标课本。**

- 英语：人教 PEP 新课标（**2024 年秋季改版**，三年级上册单元为 U1 Making friends / U2 Different families / U3 Amazing animals / U4 Plants around us / U5 The colourful world / U6 Useful numbers）
- 语文：部编版（统编版）
- 数学：人教版

后续生成/补充题目时，**单元、课时、知识点必须与课本一致**：单元名顺序照课本目录；课时按课本 Part/课文拆分（英语 Part A/B/C，语文 课文+语文园地）；单词表/句型/课文以教材为准；不得凭旧版教材或记忆杜撰。详见 [科目与知识点体系](docs/design/科目与知识点体系.md)。

### 认知铁律：不超纲、不超出小朋友认知（适用 Python 两科，2026-08-26 增补）

面向 **小学 3-4 年级（8-10 岁）**。出题/审核每题（含选项、连线两列）必须过一句：「一个没学过这些概念的 9 岁孩子，能不能凭已学知识做对？」不能 → 换掉或删掉，不得入库。

- ❌ **不串课**：只用当前章节教过的知识点，后文章节（函数、字符串方法、列表/字典/元组、lambda 等）禁止提前出现
- ❌ 不碰 CPython 内部机制与底层概念（对象缓存/`is` 同一性、`id/dir/help`、双下划线、类型检查器、docstring 等）
- ❌ 不碰超纲数学/类型（复数、二/八/十六进制、科学计数、`inf`、浮点误差、步长切片、字符串字典序比较、高级格式化 spec、`round` 舍入规则等）
- ❌ 不混真实工程概念（文件/缓冲区、日志、`import` 第三方模块、调试工具等）
- 存疑一律废弃，不纠结

> **事故注**：2026-08-26 人工复核前 8 个入门课（变量与标识符 → 字符串查找判断修改，topic 25-32）发现 **116 道超纲题**（多为批量生成批次混入入门课，属进阶题漏过滤），已全部 `deprecated`，库内 564 道活跃达标。**人工复核机制（5 检查点 + 正材清单 + 废弃正路流程）详见 [习题人工复核规范](docs/qa/manual-review.md)；出题铁律细则见 [Python 理论模板](data/template/python_theory.md#〇出题铁律不超纲不超出小朋友认知-每题必过)。**

---

## ✨ 功能特性

### 学员端（小朋友）
- **刷题组卷**：选科目→章节/题型/题数（1/10/20/50）→ 答题（9 种题型，code 题在线实跑）。见 [组卷与答题流程](docs/design/组卷与答题流程.md)
- **答题记录 & 错题本**：历史记录含「获得积分」，错题可标记掌握/删除。见 [组卷与答题流程](docs/design/组卷与答题流程.md)
- **掌握度全景**：每课覆盖度%（=精通度）柱状图 + 掌握度矩阵，科目多选 + 档位筛选。见 [掌握度与学情联动](docs/design/掌握度与学情联动设计.md)
- **积分 & 奖励**：余额/流水、🎡 大转盘抽奖、🎁 直兑商城、我的奖品。见 [积分与奖励体系](docs/design/积分与奖励体系.md)
- **最新动态**：本人最近刷题动态（各课答题量 + 场次明细）。

### 家长端
- 用孩子的 `bind_code` 绑定，查看孩子记录/错题/掌握度/统计。见 [用户与权限](docs/design/用户与权限.md)

### 管理端（管理员）
- **科目/题目管理**：科目章节 CRUD、题目 CRUD、批量导入（`/api/questions/batch`）。
- **学情分析**：掌握度全景（覆盖度柱状图 + 矩阵 + 成绩趋势）、最近动态（各课答题量 + 场次明细）、学员答题、薄弱分析（选学员后只列"练习中/需复习"的课，已掌握不进榜）、AI 周报。见 [管理后台与学情分析](docs/design/管理后台与学情分析.md)
- **学员掌握度矩阵**：行=课程、列=学员，每格状态色块，点格看详情。见 [掌握度与学情联动](docs/design/掌握度与学情联动设计.md)
- **奖励配置**：积分调整（学员卡片选择，移动端友好）、待核销（学员/转盘直兑来源筛选）、积分矩阵/转盘权重/直兑价格编辑、精通奖励测试按钮（烟花弹窗预览）。见 [积分与奖励体系](docs/design/积分与奖励体系.md)
- ~~**科目积分**~~：已废弃（2026-08-24），并入积分矩阵的科目专属维度（`scoring_rules.subject_id`）。
- **LLM 日志**：code 评分 / 周报的模型调用审计。见 [AI 评分与学情报告](docs/design/AI评分与学情报告.md)
- **运维**：SQL 运维、数据备份（封装运维 API）。见 [部署与运维](docs/design/部署与运维.md)

> **掌握度与学情联动**：掌握度结果持久化到 `student_mastery` 表（submit 后增量 upsert），薄弱分析 / 掌握度全景 / 积分闸门共用同一张表，**已掌握的课不会出现在薄弱榜**；某课达「精通」后该课不再发放积分（防刷分）。

---

## 📝 出题入口

收到 `/出题` 指令时，按以下顺序读文档并出题：
- 流程：`data/template/culture_subject.md`（v2 完整流水线：搜→对齐→出题→复核→导入；搜不到/网络不通时**先停下来反馈，不自行降级**）
- 题型字段：`data/template/question_types.md`（含 `tier` 字段：1初级/2进阶/3挑战）
- 人工复核：`docs/qa/manual-review.md`（5 检查点）
- 科目专属模板：`data/template/chinese_grade4.md` / `math_grade4.md` / `english_grade4.md`（按需）
- 联网搜资料：本地 SearXNG `http://127.0.0.1:8080`（默认 Bing；`data/template/culture_subject.md` 步骤 1️⃣ 有 Python 调用模板）

调用方式（任选其一）：
- 结构化：`/出题 语文四年级上册 观潮 20道`
- 自然语言：`/出题 给我出 2 繁星 20 题`

**用户未给题数时先询问，再走流程**。题型配比同理，**用户点头前不写 JSON**。

- **后端** FastAPI + SQLAlchemy + SQLite；JWT Bearer 鉴权，`require_role` 做角色网关。
- **前端** 原生多页 HTML + JS，`common.js` 提供 API 封装 / 顶栏 / embed 模式；ECharts 画图。
- **AI** OpenAI 兼容 SDK（aliyun 主 / deepseek 兜底），代码沙箱实跑。
- **部署** Docker，本地 `quiz-local`(localhost:8000) 与 ECS `quiz-system`(106.14.99.100:8000) 双环境，数据卷持久化。

完整技术栈、模块路由表、数据模型、请求流向见 [系统架构总览](docs/design/系统架构总览.md)。

### 依赖版本（2026-08-25 锁定）
`fastapi==0.141.1`、`uvicorn[standard]==0.52.1`、`sqlalchemy==2.0.51`、`pydantic==2.13.4`、`python-jose[cryptography]==3.5.0`、`passlib==1.7.4`、`python-multipart==0.0.32`、`openai==2.53.0` + 前端 ECharts CDN。详见 `docs/init/dependencies.md`。

### Python 编码规范
import 置顶、PEP8（4 空格 / 行宽 120）、中文注释、项目内相对导入优先、返回类型标注且一致、FastAPI 路由带 `summary/description/response_model/tags`。

### 角色与权限

| 角色 | 用途 |
|---|---|
| `student` | 学员（小朋友）：刷题/错题/掌握度/积分/抽奖/直兑 |
| `parent` | 家长：绑定孩子、查看孩子数据 |
| `admin` | 管理员：全部管理接口 |

注册需 `regkey`（默认 `openschool2026`），当前未开放自由注册。详见 [用户与权限](docs/design/用户与权限.md)。

---

## 🚀 快速开始 / 部署

### 本地 Docker（推荐测试方式）
```bash
docker build -t quiz-system:local -f src/Dockerfile src
mkdir -p data   # ★ 数据库唯一合法路径 = data/quiz.db；文件不存在时容器启动自动建库（不复制 src/ 下旧库）
docker run -d --name quiz-local -p 8000:8000 \
  -v "$(pwd)/data:/app/data" --restart unless-stopped quiz-system:local
# 访问 http://localhost:8000  ，管理后台 admin.html 账号 admin/admin123
```
`entrypoint.sh` 自动 seed（积分/转盘/直兑）+ 起服务；静态文件改完 `docker cp` 即生效，改 `.py` 需 `docker restart quiz-local`。

### 线上 ECS
ECS 已配置阿里云 pip 源、恢复 `docker build` 标准部署；`docker cp` 仅作应急热更新。完整步骤、拉库脚本、运维接口、Schema 迁移见 [部署与运维](docs/design/部署与运维.md) 与 [数据库迁移机制](docs/design/数据库迁移机制.md)。

### 本地直接运行（开发调试）
```bash
cd src && .venv/Scripts/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8010
```

### ⚠️ 部署红线（唯一合法部署方式）
所有代码变更必须走**标准流程**推送到 ECS，不得绕过（详细见 [部署与运维](docs/design/部署与运维.md) 与 `docs/deploy/ecs-deploy.md`）：
> **禁止**用 `POST /api/admin/update-file` 逐个文件推送——该接口**已废弃**，仅保留作紧急回滚手段。

**部署前检查清单**：
- [ ] 本地代码完整（`git status` 无未提交文件）
- [ ] 确认 `src/` 与 ECS `build/` 目录结构一致
- [ ] 确认 ECS 数据卷 `/opt/quiz-system/data/` 存在且可写
- [ ] 确认 ECS SSH 正常（`openclaw.pem` 私钥可用）
- [ ] 确认 ECS 健康检查通过（`curl http://106.14.99.100:8000/` 返回 200）

> ⚠️ 改代码后一律走标准流程（打包→scp→docker build→docker compose up -d→健康检查），禁止逐文件 update-file 推算部署。推 ECS 前本地完整测试、批量数据库操作前确认备份。

---

## 🔧 维护者须知

- **改完代码热更新**：`POST /api/admin/update-file` 写文件 + `POST /api/admin/restart` 重启（ECS 省去 ssh）。
- **拉取线上库到本地**：`python scripts/fetch_db.py`（走 exec-sql API，纯接口）。
- **备份/下载数据库**：`POST /api/admin/backup-db` 备份、`GET` 列表、`GET /api/admin/backup-db/download?name=` 下载。
- **应急 SQL**：`POST /api/admin/exec-sql`（先自动备份再执行）。
- **加字段（正确姿势）**：在 `src/migrations/` 新建 `00xx_xxx.py`，定义 `MIGRATION_ID` 和幂等的 `up(engine)`（用 `add_column` 等辅助函数），应用在 `main.py` 启动时自动执行；同时记得在 `models.py` 补列声明。**禁止再手写散落 `ALTER` 或直调 `exec-sql` 加列**（`exec-sql` 仅应急）。
- **密钥安全**：DeepSeek / aliyun key 走环境变量或 `data/*.txt`，**禁止写入代码或提交仓库**；`data/`、`*.db`、`.venv` 已加入 `.gitignore`。

> 所有写操作类运维接口（exec-sql / update-file / restart）**务必先备份数据库**。

**注意事项 / 已确认事项**：
- ✅ `routers/admin.py` 引用残留已修正为 `analytics.py` + `system.py`（2026-08-25，`BUG-1` 已关闭，见 `docs/issues/BUG-1.md`）
- ✅ 依赖版本已锁定（2026-08-25，见 `docs/init/dependencies.md` 与上方依赖清单）
- `data/`、`*.db`、`.venv/` 已入 `.gitignore`，严禁提交（含密钥）
- 时间口径：库内统一 UTC 存储，对外输出 +00:00（`core/times.py`），前端负责换算
- 管理后台：`/static/admin.html`（账号 `admin/admin123`）

完整运维 API 清单、热更新流程、安全提醒见 [部署与运维](docs/design/部署与运维.md)。

---

## 📁 目录结构

```
quiz/
├── README.md              # 本文件（系统总入口）
├── docs/
│   ├── design/            # 各功能设计文档（10 份，见上方导航）
│   └── plan/              # 方案/规划类提案
├── src/
│   ├── main.py            # 应用入口、路由挂载、静态目录
│   ├── models.py          # ORM 模型
│   ├── schemas.py         # Pydantic 模型
│   ├── config.py          # 配置
│   ├── core/              # security / deps / llm_client / llm_grader / code_runner / tier / mastery
│   ├── routers/           # 业务路由（auth/parent/subjects/questions/exam/stats/mastery/reward/reward_admin/system/analytics）
│   ├── migrations/        # 轻量数据库迁移（增量 schema，启动时自动执行）
│   ├── static/            # 前端页面 + js + css
│   ├── data/              # 题库 JSON（权威题库源）
│   ├── seed_reward.py     # 积分/转盘/直兑种子
│   └── Dockerfile / entrypoint.sh / docker-compose.yml
├── modules/pc_monitor/   # 独立功能模块：PC 硬件监控
├── scripts/              # 运维脚本（fetch_db 拉库 / mastery_backfill 重算）
└── data/ (本地，不进 git)  # 数据库 + 密钥 + 备份
```

---

## 🛠️ 技术要点备忘

- 题型体系与判分见 [题型与出题规范](docs/design/题型与出题规范.md)；阅读理解（reading）为「一篇文章+多子题」，按子题正确比例给分。
- 组卷题数白名单固定为 **1/10/20/30/40/50**（1 题档仅实操单题）；科目 `allowed_types` 是组卷题型闸门。**题池不足所选档位时自动降档**到最大可满足档位并提醒学员。
- 积分按「题数档位 × 分数段」查 `scoring_rules` 表（10题 1/1、20题 2/1、30题 3/2/1、40题 4/3/2/1、50题 5/4/3/2/1），支持 `subject_id` 科目专属覆盖（如 Python基础实操 1 题档 100→2 / 90→1）；与成绩同事务落 `points_ledger`；**课程达「精通」则该次不再发分**（掌握度闸门）。改造见 [积分档位化改造任务清单](docs/plan/积分档位化改造_任务清单.md)。
- **精通奖励**（2026-08-24）：达成精通（非精通→精通跃迁）奖励一次「玩转大转盘」等额积分（动态读 `wheel_cost`），烟花弹窗；历史精通在下次新精通时一次性补发；`mastery_rewards` 表唯一约束防重复；详见 [积分与奖励体系](docs/design/积分与奖励体系.md) §4.5。
- **轻量迁移**：`main.py` 启动 `create_all` 后跑 `run_migrations()`，增量字段走 `src/migrations/` 迁移文件（幂等、跨环境一致），不再手写散落 `ALTER`；新增字段流程见上方「维护者须知 · 加字段正确姿势」。
