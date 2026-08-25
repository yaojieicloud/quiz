# 依赖清单

> it-workflow 初始化生成（2026-08-24），2026-08-25 版本锁定。来源：`src/requirements.txt` + 前端/工具链。

## 运行依赖（Python，2026-08-25 已锁版本）
| 依赖 | 版本 | 用途 | 备注 |
|------|------|------|------|
| fastapi | 0.141.1 | Web 框架、路由、依赖注入 | 核心框架 |
| uvicorn[standard] | 0.52.1 | ASGI 服务器 | 直跑：`python -m uvicorn main:app` |
| sqlalchemy | 2.0.51 | ORM，SQLite 单文件库 | 22 张表 |
| pydantic | 2.13.4 | 请求/响应模型 | schemas.py |
| python-jose[cryptography] | 3.5.0 | JWT 签发/校验（HS256） | core/security.py |
| passlib | 1.7.4 | 密码哈希（pbkdf2_sha256） | core/security.py |
| python-multipart | 0.0.32 | 表单/文件解析 | — |
| openai | 2.53.0 | OpenAI 兼容 SDK 调 LLM | aliyun 主 / deepseek 兜底；key 走环境变量 |
> 锁定来源：本地 .venv 实测（Python 3.13，与 Dockerfile `python:3.13-slim` 一致）；升级依赖后请重新锁定实测版本并同步本表。

## 前端依赖
| 依赖 | 用途 | 备注 |
|------|------|------|
| 原生 HTML/CSS/JS | 多页前端（14 页面） | 无构建步骤 |
| ECharts 5.5 | 图表（掌握度全景、成绩趋势、最近动态） | CDN 引入，加载失败降级 |

## 本地/运维工具链
| 工具 | 用途 |
|------|------|
| Docker + docker-compose | 本地 quiz-local 与 ECS quiz-system 双环境 |
| 阿里云 ECS（106.14.99.100:8000） | 生产环境 |
| 阿里云 pip 源 | ECS 构建加速 |

## 独立子系统依赖
| 子系统 | 位置 | 依赖 |
|--------|------|------|
| pc_monitor 硬件监控 | scripts/pc_monitor/ | Python + LibreHardwareMonitor（.NET DLL，vendor/ 内置）+ TaskRegistrar/TempReader（C#）+ PushPlus 推送 |

## 运行时环境变量
| 变量 | 用途 | 默认值 |
|------|------|--------|
| QUIZ_DB_PATH | SQLite 文件路径 | 本地裸跑默认 `quiz-data/quiz.db`（★ 数据库唯一合法路径）；容器内 `/app/data/quiz.db` |
| QUIZ_SECRET_KEY | JWT 签名密钥 | config.py 内置默认值（⚠️ 生产建议环境变量覆盖） |
| QUIZ_HOST / QUIZ_PORT | 直跑监听 | 127.0.0.1 / 8000 |
| LLM 相关 key | LLM 调用（aliyun/deepseek） | 环境变量或 quiz-data/*.txt，严禁提交仓库 |

## 依赖风险备忘
- ✅ 2026-08-25 已锁定全部运行依赖版本（见上表 / src/requirements.txt）
- ECharts 走公网 CDN：内网/弱网环境图表降级，注意可用性
- passlib 与新版 bcrypt 存在已知兼容问题（如出现告警可关注）
