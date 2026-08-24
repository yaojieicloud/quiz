# AGENTS.md — Quiz 题库系统快速入门指南

> **it-workflow 流程入口**。项目已有成熟文档体系：
> - `README.md` — 系统总入口（功能/架构/部署/运维导航），**优先阅读**
> - `CODEBUDDY.md` — 历史协作规则文件（workbuddy 生成）：其铁律（教材/文档先行/安全红线）仍作项目约定，**流程与文档体系以 it-workflow 为准**
> - `docs/design/` — 11 份分模块设计文档（存量）
> 本文件与 it-workflow 文档骨架（`docs/init/`、`docs/overview.md` 等）并存互链，不覆盖任何现有文件。

## 1. 项目简介
- **项目名称**：Quiz 题库闯关系统
- **定位**：面向小学小朋友的刷题系统——做题赚积分 → 大转盘/直兑激励；学员/家长/管理员三角色
- **核心功能**：
  - 学员端：组卷答题（9 种题型，1/10/20/30/40/50 题数档位）、错题本、掌握度全景、积分奖励（大转盘/直兑）、最近动态
  - 家长端：bind_code 绑定孩子，查看记录/错题/统计
  - 管理端：科目题目管理、学情分析（5 子页）、学员掌握度矩阵、奖励配置、LLM 日志、运维（SQL/备份/热更新）
- **出题铁律**：内容必须以人教版新课标课本（2024 秋季改版）为准，详见 README 与 CODEBUDDY.md §3.1

## 2. 技术栈
- 后端：Python 3.13 + FastAPI + SQLAlchemy（SQLite 单文件库）
- 前端：原生多页 HTML/JS（无构建步骤）+ ECharts（CDN，失败降级）
- AI：OpenAI 兼容 SDK（aliyun 主 / deepseek 兜底），代码题沙箱实跑
- 鉴权：JWT（HS256，7 天）+ `require_role` 角色网关
- 部署：Docker 双环境（本地 `quiz-local:8000` / ECS `106.14.99.100:8000`）
- 详见 `docs/init/dependencies.md`

## 3. 项目结构
```
quiz/
├── AGENTS.md / README.md / CODEBUDDY.md   # 三个入口
├── docs/    # 文档：design(11 份存量) + plan/qa + it-workflow 骨架(overview/init/requirements/tasks/issues/PROGRESS)
├── src/     # 后端（main.py / models / core / 11 routers / migrations / static / Docker）
├── scripts/ # 出题/推送/验证一次性脚本 + pc_monitor 硬件监控子系统
├── data/    # 题库源数据（JSON）
├── quiz-data/ # 本地运行时数据（库/密钥/备份，不进 git）
└── .venv/   # 虚拟环境（不进 git）
```
- 详见 `docs/init/project-structure.md`

## 4. 依赖说明
fastapi==0.141.1、uvicorn[standard]==0.52.1、sqlalchemy==2.0.51、pydantic==2.13.4、python-jose[cryptography]==3.5.0、passlib==1.7.4、python-multipart==0.0.32、openai==2.53.0（2026-08-25 锁定）+ 前端 ECharts CDN。详见 `docs/init/dependencies.md`。

## 5. 架构设计
- 单体后端：11 个业务路由器 + core/* 组件（security/deps/tier/mastery/code_runner/llm_client/llm_grader/times）
- 数据：SQLite 22 表（questions、exam_records、student_mastery、points_ledger、scoring_rules 等）
- 核心业务机制：掌握度闸门（已掌握课程不再发分）、精通奖励（唯一约束防重发）、积分矩阵（题数档位×分数段，支持科目专属覆盖）
- 数据流：组卷→答题→交卷判分→积分/掌握度/错题本同事务落库，详见 `docs/init/architecture.md` §4
- 迁移：`create_all` + `run_migrations()`（幂等），加字段必须走 `src/migrations/`
- 各模块设计细节在 `docs/design/`（11 份存量文档，见 `docs/design/INDEX.md`）

## 6. 需求总览
- 存量功能：见 README 功能特性（9 大模块，详见 `docs/overview.md`）
- it-workflow 需求：0（REQ-{N} 体系自本初始化起算，首个新需求为 REQ-1）
- 索引：`docs/requirements/INDEX.md`

## 7. 开发规范（it-workflow 流程）
- 流程：需求(①确认) → 方案设计(②确认) → 任务拆解(③确认) → 逐任务开发 → 文档同步(④确认) → 验收；Bug 流程同样两次确认门
- 指令：`/需求` `/设计` `/任务` `/问题` `/测试` `/讨论` `/继续` `/暂停` `/帮助`
- 编号：需求 REQ-{N} / 设计 REQ-{N}-{M} / 任务 REQ-{N}-{M}-{K} / 问题单 BUG-{N}
- 进度：`docs/PROGRESS.md`（多任务并行，`/继续` 恢复）
- 项目铁律（承自 CODEBUDDY.md）：
  - 文档先行：先写文档后改代码；主文档同步：功能变更必须同步 README.md 对应章节
  - 安全红线：禁止硬编码密钥；批量数据库操作前确认备份；推 ECS 前本地完整测试
  - 运维写接口（exec-sql / update-file / restart）前务必备份数据库
- Python 规范：import 置顶、PEP8（4 空格/行宽 120）、中文注释、项目内相对导入优先、返回类型标注且一致、FastAPI 路由带 summary/description/response_model/tags

## 8. 注意事项
- ✅ 3 份设计文档残留的 `routers/admin.py` 引用已修正为 `analytics.py` + `system.py`（2026-08-25，`BUG-1` 已关闭，见 `docs/issues/BUG-1.md`）
- ✅ 依赖版本已锁定（2026-08-25，见 `src/requirements.txt` 与 `docs/init/dependencies.md`）
- `quiz-data/`、`*.db`、`.venv/` 已入 .gitignore，严禁提交（含密钥）
- 时间口径：库内统一 UTC 存储，对外输出 +00:00（`core/times.py`），前端负责换算
- 管理后台：`/static/admin.html`（README 记载账号 admin/admin123）
