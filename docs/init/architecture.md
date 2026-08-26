# 架构设计

> it-workflow 初始化生成（2026-08-24）。从代码逆向梳理（main.py / config.py / models.py / core/ / routers/ / static/），并与存量设计文档交叉核对；如两者有出入，以代码为准（已知入参见 BUG-1）。

## 1. 架构模式
- **单体后端 + 多页前端 + 单文件数据库**：一个 FastAPI 进程同时提供 API 与静态页面；SQLite 单文件作为唯一状态源；无消息队列、无缓存层
- **双环境部署**：本地 `quiz-local`（测试）+ ECS `quiz-system`（生产，106.14.99.100），Docker 镜像统一，数据卷持久化
- **无状态鉴权**：JWT（HS256，7 天），token 仅携带用户 id，服务端不落会话
- **前端无构建**：原生 HTML/JS + fetch 直连 API；ECharts 经 CDN 引入并降级

## 2. 核心模块
### 2.1 组件层（src/core/，不依赖 HTTP）
| 模块 | 职责 |
|------|------|
| security.py | 密码哈希（passlib/pbkdf2_sha256）、JWT 签发与校验 |
| deps.py | `get_current_user`（Bearer → 按 sub 查库）、`require_role(*roles)` 角色网关 |
| tier.py | 组卷题数档位（1/10/20/30/40/50）与降档逻辑 |
| mastery.py | 掌握度算法（三硬门槛）、掌握度闸门（已掌握课程停发积分）、精通奖励判定 |
| code_runner.py | code 题沙箱实跑 |
| llm_client.py | LLM 双通道：aliyun 主 / deepseek 兜底 |
| llm_grader.py | code 题 LLM 评星（写 answer_records.llm_score / llm_stars） |
| times.py | 时间口径统一：库内 UTC 存储，对外输出 +00:00 / 北京日期 |

### 2.2 路由层（src/routers/，11 个模块）
| 路由模块 | 职责 |
|----------|------|
| auth | 注册/登录/当前用户/绑定孩子/孩子列表 |
| subjects | 科目与课（topic）/单元 CRUD、题型闸门（allowed_types） |
| questions | 题目 CRUD + 批量导入（/api/questions/batch） |
| exam | 组卷/开考/交卷判分/记录/错题本/run-code |
| stats | 总览统计 |
| parent | 家长查看孩子记录/错题/统计 |
| reward | 学员积分余额/流水/大转盘/直兑 |
| reward_admin | 管理端积分调整/核销/矩阵/转盘/直兑配置/LLM 日志/精通奖励测试 |
| mastery | 学员本人掌握度 / 管理端掌握度矩阵 |
| system | 运维：exec-sql / update-file / pip-install / re-grade（重评）/ restart / backup-db |
| analytics | 学情分析：学员/记录/总览/学员维度/薄弱分析/AI 周报/最近动态 |

### 2.3 数据层
- ORM 表共 **22 张**：users / parent_child / subjects / topics / tier_config / questions / exam_records / answer_records / wrong_questions / ai_reports / student_mastery / mastery_rewards / scoring_rules / subject_points / student_points / points_ledger / wheel_prizes / plays / direct_redemptions / redeem_items / config / llm_calls
- 迁移机制：启动时 `create_all`（全新库）+ `run_migrations()`（老库增量补齐）；迁移文件 `MIGRATION_ID` + 幂等 `up(engine)`，当前已有 0003_tier / 0004_scoring_subject / 0005_mastery_rewards
- 种子数据：`seed_reward.py`（积分规则/转盘/直兑，幂等）+ entrypoint.sh 启动时执行

## 3. 模块依赖
```
main.py ──> routers/*（11 个）──> core/{deps,tier,mastery,code_runner,llm_grader,llm_client,times}
   │                              │
   ├─ config.py（DB/JWT/静态目录）  └─ schemas.py（Pydantic）
   ├─ database.py（engine/Session）
   ├─ models.py（22 表）<── core/{security,llm_client,mastery}
   └─ migrations（启动时 run_migrations）

浏览器 ──> static/*.html ──> js/common.js（API 封装/顶栏）──> /api/*
```
- core 组件为跨模块共享业务逻辑的唯一载体；router 只负责 HTTP 边界
- llm_grader 依赖 llm_client；判分链路调用 code_runner

## 4. 数据流向
### 4.1 组卷与答题主链路（核心）
```
POST /api/exam/available-count   题池计数 + 档位可满足性
  → POST /api/exam/start          白名单/allowed_types 闸门；题池不足自动降档并提示
  → 逐题作答（9 种题型；code 题 POST /api/exam/run-code 沙箱实跑）
  → POST /api/exam/submit         判分（code 题结合 llm_grader 评星；通过线 60 分）
      ① exam_records + answer_records 落库
      ② 未通过题 → wrong_questions（错题本）
      ③ 积分：查 scoring_rules 矩阵（题数档位×分数段，科目专属覆盖）→ points_ledger
         ★ 掌握度闸门：该课已达精通则本次不发分
      ④ 掌握度：student_mastery 增量 upsert（三硬门槛算法）
         ★ 非精通→精通跃迁：一次性精通奖励（mastery_rewards 唯一约束防重发；历史精通在下次新精通时补发）
```
### 4.2 LLM 链路
- code 题评分：submit → code_runner 实跑 → llm_grader 评星 → llm_calls 审计（管理端 LLM 日志）
- AI 周报：POST 学情分析 report → llm_client 双通道 → ai_reports
### 4.3 家长端 / 管理端
- 家长：按 bind_code 绑定后只读聚合（records / wrong / stats）
- 管理端：学情分析（总览/学员/薄弱/最近动态）；★ 薄弱分析仅列「练习中/需复习」课程，已掌握不进榜

## 5. 设计模式
| 模式 | 落点 |
|------|------|
| 依赖注入 | FastAPI Depends（get_current_user / require_role） |
| 工厂（角色网关） | `require_role(*roles)` 按路由声明角色集合 |
| 幂等迁移 | MIGRATION_ID + up(engine) + 列存在检查 |
| 幂等种子 | seed_reward.py / entrypoint.sh 可重复执行 |
| 无状态 token + DB 取角色 | 改角色即时生效，无需重新登录 |
| 闸门式业务规则 | 掌握度闸门（精通停发积分）、allowed_types（科目题型闸门）、题数白名单 |
| 双通道兜底 | LLM aliyun → deepseek |

## 6. 接口契约（主要 API）
> Base：`http://<host>:8000`；鉴权：`Authorization: Bearer <jwt>`；角色经 require_role 网关。完整清单见 Swagger `/docs`。

| 领域 | 主要接口 |
|------|----------|
| 认证 | POST /api/auth/register（需 regkey）· POST /api/auth/login · GET /api/auth/me · POST /api/auth/bind-child · GET /api/auth/children |
| 科目/课 | GET·POST /api/subjects · GET /api/subjects/{id}/topics · GET /api/subjects/{id}/units · POST /api/topics · PUT/DELETE 科目与课 |
| 题目 | POST /api/questions/batch · GET·PUT·DELETE /api/questions/{id} |
| 组卷/答题 | POST /api/exam/available-count · POST /api/exam/start · POST /api/exam/submit · GET /api/exam/records(/ {id}) · GET /api/exam/recent-activity · 错题本 GET·master·DELETE · POST /api/exam/run-code |
| 学员积分/奖励 | GET /api/meta · GET /api/points/balance · GET /api/points/ledger · GET /api/wheel/prizes · POST /api/wheel/spin · GET /api/redeem/items · POST /api/redeem/direct · GET /api/redeem/mine |
| 掌握度 | GET /api/mastery/me · GET /api/admin/mastery · GET /api/admin/mastery/student/{id} |
| 家长端 | GET /api/parent/children/{id}/records · /wrong · /stats |
| 管理·统计/运维 | GET /api/stats/overview · POST /api/admin/exec-sql · POST /api/admin/update-file · POST /api/admin/pip-install · POST /api/admin/re-grade · POST /api/admin/restart · POST·GET /api/admin/backup-db · GET /api/admin/backup-db/download |
| 管理·奖励配置 | POST /api/admin/points/adjust · GET /api/admin/redeem/pending · POST /api/admin/redeem/approve · GET /api/admin/points/ledger · scoring-rules / wheel-prizes / redeem-items 全套 CRUD · GET·PUT /api/admin/config · GET /api/admin/llm-calls · POST /api/admin/test-mastery-reward |
| 学情分析 | GET /api/admin/students · GET /api/admin/students/{id}/records · PUT /api/admin/answer-records/{id} · GET·DELETE /api/admin/records/{id} · GET /api/admin/analytics/overview · GET /api/admin/analytics/student/{id} · GET /api/admin/analytics/weakness · POST /api/admin/analytics/report · GET·DELETE /api/admin/ai-reports(/ {id}) · GET /api/admin/analytics/recent-activity |

> ⚠️ 各路由器的最终挂载前缀以代码与 Swagger 为准。
> ✅ 存量《系统架构总览》等文档曾提到的 `routers/admin.py` 在代码中不存在（对应功能在 analytics.py + system.py），2026-08-25 已全部修正（BUG-1 关闭，见 `docs/issues/BUG-1.md`）。

## 7. 状态管理
- 后端无状态：全部状态在 SQLite 单文件（账号/题库/答题记录/积分/掌握度/LLM 审计）
- 前端：token 存 `localStorage.quiz_token`、用户存 `quiz_user`、组卷上下文存 `quiz_exam`；页面刷新即重新 fetch，无前端状态框架
- LLM 调用不做持久化缓存，仅审计（llm_calls 表）

## 8. 认证机制
- JWT：HS256，7 天有效，payload `sub` = 用户 id
- `get_current_user` 仅按 sub 查库，**role 取自数据库**（改角色即时生效，无需重新登录）
- 注册需 regkey（默认 `openschool2026`），当前未开放自由注册
- 家长绑定：parent 以孩子的 `bind_code` POST bind-child
- 运维接口（system.py：exec-sql / update-file / restart 等）高风险，限 admin，且写前必须备份

## 9. 部署架构
- 镜像：`src/Dockerfile`；`entrypoint.sh` 启动时 seed + 起服务
- 本地：`docker run --name quiz-local -p 8000:8000 -v data:/app/data`
- ECS：106.14.99.100:8000；热更新路径 = POST /api/admin/update-file 写文件 + POST /api/admin/restart（省去 ssh）
- 数据备份：/api/admin/backup-db（POST 备份 / GET 列表 / GET 下载）；拉线上库：`scripts/fetch_db.py`（纯 API 通道）

## 10. 关键常量速查
| 项 | 值 | 位置 |
|----|----|----|
| Token 有效期 | 7 天 | config.py |
| 默认 regkey | openschool2026 | routers/auth.py |
| 组卷题数白名单 | 1 / 10 / 20 / 30 / 40 / 50 | routers/exam.py |
| 通过线 | 60 分 | routers/exam.py |
| DB 路径 | 环境变量 `QUIZ_DB_PATH`；本地裸跑默认 `../../data/quiz.db`（★ 唯一合法路径），容器内 `/app/data/quiz.db` | config.py |
| 管理后台入口 | /static/admin.html | static/ |
| ECS 地址 | 106.14.99.100:8000 | scripts/fetch_db.py |
