# 项目结构

> it-workflow 初始化生成（2026-08-24）：目录树 + 各部分职责。

## 目录树
```
quiz/
├── AGENTS.md                  # it-workflow 快速入门总入口
├── README.md                  # 系统总入口（存量）：功能/架构/部署/运维导航
├── CODEBUDDY.md               # LLM 协作军规（存量）
├── .gitignore
├── docs/
│   ├── overview.md            # 需求总览（it-workflow）
│   ├── PROGRESS.md            # 进度文件（多任务并行恢复）
│   ├── init/                  # 初始化文档
│   │   ├── project-structure.md
│   │   ├── dependencies.md
│   │   └── architecture.md
│   ├── requirements/          # 需求梳理文档 + INDEX.md（REQ-{N}）
│   ├── design/                # 设计文档：11 份中文存量 + INDEX.md + 新增 REQ-{N}-{M}
│   ├── tasks/                 # 任务拆解文档 + INDEX.md（REQ-{N}-{M}-{K}）
│   ├── issues/                # 问题单 + INDEX.md（BUG-{N}）
│   ├── plan/                  # 方案/规划（存量）：积分大转盘/实时出题/未来规划等
│   └── qa/                    # QA 计划（存量）
├── src/                       # ★ 后端应用代码（FastAPI 根目录，部署为容器 /app）
│   ├── main.py                # 入口：建表 + 迁移 + 路由挂载 + 静态文件
│   ├── models.py              # 全部 22 张 ORM 表
│   ├── schemas.py             # Pydantic 请求/响应模型
│   ├── config.py              # 配置：DB 路径 / JWT / 静态目录（环境变量驱动）
│   ├── database.py            # 引擎 / Session
│   ├── core/                  # 核心组件（见 architecture.md §2.1）
│   ├── routers/               # 11 个业务路由模块
│   ├── migrations/            # 轻量迁移（0003~0005 + _template，幂等）
│   ├── static/                # 前端 14 个页面 + js/common.js + css
│   ├── data/                  # 题库 JSON + 导入/清理脚本
│   ├── seed_reward.py         # 积分/转盘/直兑种子（幂等）
│   ├── fetch_db.py            # 拉线上库到本地（走 exec-sql API）
│   ├── 一次性脚本              # reconstruct_58 / evaluate_match / import_chinese_english / push_questions / verify_window
│   ├── requirements.txt
│   └── Dockerfile / entrypoint.sh / docker-compose.yml
├── scripts/                   # 一次性运维脚本：出题生成(gen_*) / 推送(push_*) / 校验(verify_*) / 评审 JSON 等
│   └── pc_monitor/            # ★ 独立子系统：PC 硬件监控（Python + LibreHardwareMonitor .NET vendor + C# 工具 + PushPlus 推送）
├── data/                      # 题库源数据：JSON、子目录（reading_chinese / py500 / theory3 / template 等）
├── quiz-data/                 # 本地运行时数据：数据库 + 密钥（deepseek_key.txt）+ 备份（不进 git）
└── .venv/                     # 虚拟环境（不进 git）
```

## 目录职责速查
| 目录 | 职责 | 备注 |
|------|------|------|
| src/ | 唯一应用代码 | 容器内 /app；前端改完 docker cp 即生效，.py 需重启 |
| src/core/ | 业务核心组件 | 不依赖 HTTP，可被所有 router 复用 |
| src/routers/ | HTTP 接口 | 按模块拆分（CODEBUDDY.md 3.5） |
| src/migrations/ | 增量 schema | 加字段唯一合法途径，禁止手写散落 ALTER |
| src/static/ | 前端页面 | 原生 HTML/JS，common.js 统一 API 封装 |
| docs/design | 设计文档（存量 11 份） | 见 docs/design/INDEX.md |
| docs/requirements | 需求 | 新 REQ-{N} 体系 |
| docs/tasks | 任务 | 新 REQ-{N}-{M}-{K} 体系 |
| docs/issues | 问题单 | 新 BUG-{N} 体系 |
| scripts/ | 运维一次性脚本 | 非应用代码，不进容器 |
| data/ | 题库源数据 | 供导入脚本使用 |
| quiz-data/ | 本地运行时数据 | 含密钥，严禁入仓库 |

## 命名约定
- Python：文件/函数 snake_case，类 PascalCase
- 前端页面：`xxx.html`；公共能力沉淀 `js/common.js`
- 迁移文件：`00NN_短名.py`，含 MIGRATION_ID + 幂等 up(engine)
- 一次性脚本：动词前缀 gen_/push_/verify_/check_/inspect_ + 批次号
- 文档：it-workflow 按编号命名；存量设计文档保持中文命名不动
