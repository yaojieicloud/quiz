# ECS 部署标准流程

> **唯一合法部署方式**：所有代码变更必须通过标准流程推送到 ECS，不得绕过。
> 
> **历史遗留方式已废弃**：`POST /api/admin/update-file` 接口（逐个文件推送）**已废弃**，仅保留作为紧急回滚手段。
> 
> **部署前必读**：部署与运维设计文档 `docs/design/部署与运维.md`

---

## 1. ECS 基本信息

| 项目 | 值 |
|------|-----|
| IP 地址 | `106.14.99.100` |
| SSH 端口 | `22` |
| 用户名 | `root` |
| 认证方式 | 公钥认证 |
| 私钥路径 | `C:/Users/Yaojie/Documents/openclaw.pem` |
| 部署目录 | `/opt/quiz-system/build/` |
| 数据目录 | `/opt/quiz-system/data/` |
| 容器名 | `quiz-system` |
| 镜像名 | `quiz-system:latest` |

---

## 2. ECS 目录结构

```
/opt/quiz-system/
├── docker-compose.yml    # 仅 image: quiz-system:latest 引用（无 build 段）
├── build/                # 实际运行源码（与本地 src/ 对应）
│   ├── Dockerfile
│   └── main.py / models.py / schemas.py / routers/ / core/ / static/ ...
└── data/            # DB 数据卷（quiz.db + backups/ + 密钥）
```

> ⚠️ **本地 `src/` 即对应 ECS 的 `build/`；本地改代码后需 scp 到 `build/` 再重建镜像才生效。**
> ⚠️ **历史坑**：ECS `build/core/` 曾缺失 `tier.py`、`schemas.py` 也曾与本地不同步，导致重建后 import 失败、容器重启循环。**每次部署前务必确认 `build/` 与本地 `src/` 完整一致**（缺文件/旧文件都会致启动失败）。

---

## 3. 标准部署流程（推荐）

```bash
# 1. 确认本地代码完整（git status 无未提交文件）
cd /c/Users/Yaojie/Documents/GitHub/quiz
git status

# 2. 打包 src/（**仅打包源码，不打包 data/docs/tests/docker**）
# ⚠️ ECS 部署文档原版含 docs/ 是历史错误，2026-08-31 修正
tar -czf /tmp/quiz-src.tar.gz \
  --exclude=.git \
  --exclude=__pycache__ \
  -C src .

# 3. 推送文件到 ECS 根目录
scp -i C:/Users/Yaojie/Documents/openclaw.pem \
  /tmp/quiz-src.tar.gz \
  root@106.14.99.100:/opt/quiz-system/

# 4. 登录 ECS 解压、重建镜像、重启容器
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 << 'EOF'
  cd /opt/quiz-system
  # 备份旧 Dockerfile（防止覆盖后无法回滚）
  cp Dockerfile Dockerfile.ecs-predeploy-$(date +%s).bak
  tar -xzf quiz-src.tar.gz
  rm quiz-src.tar.gz
  docker build -t quiz-system:latest -f Dockerfile .
  docker compose up -d
EOF

# 5. 健康检查
curl -o /dev/null -w '%{http_code}\n' http://106.14.99.100:8000/
```

> **关于自定义基础镜像 `quiz-base:3.13`**：
> 本地构建使用 `docker/base/Dockerfile` + `FROM quiz-base:3.13`（内嵌阿里云 pip 源，
> 避免每次构建重复配置）。ECS 上首次部署需要先 build 一次：
> ```bash
> scp docker/base/Dockerfile ... /opt/quiz-system/docker/base/Dockerfile
> ssh ... "cd /opt/quiz-system && docker build -t quiz-base:3.13 -f docker/base/Dockerfile docker/base"
> ```
> 之后 ECS 的 quiz-system:latest 可基于 quiz-base:3.13 构建。

## 3.1 ⚠️ ECS 部署关键陷阱（2026-08-31 事故记录）

**事故**：本次部署错误用 `src/docker-compose.yml` 覆盖了 ECS 原 compose 文件，导致
数据卷挂载路径错乱，容器读到空数据库。

### 真相
- ECS 真实数据卷挂载在 `/opt/data`（不是 `/opt/quiz-system/data`）
- ECS 通过环境变量 `QUIZ_DATA_DIR=/opt/data` 把 `src/docker-compose.yml` 默认的 `../data` 重定向
- 但**新解压的 compose 文件可能不包含该环境变量**，导致默认 `../data` 解析为 `/opt/data`（**容器里是空目录**）

### 应对
- **永远不要把 src/docker-compose.yml 覆盖到 ECS 的 `/opt/quiz-system/docker-compose.yml`**
- ECS 的 docker-compose.yml 应**单独维护**（不打包进 tar），或者改成挂载绝对路径：
  ```yaml
  volumes:
    - /opt/data:/app/data    # 绝对路径，避免解析问题
  ```
- **部署后必须验证**：`docker exec quiz-system python3 -c "import sqlite3; print(sqlite3.connect('/app/data/quiz.db').execute('SELECT COUNT(*) FROM users').fetchone())"`
  - 若 users 数 = 0 → 数据库被覆盖了，立即从 `/opt/quiz-system/data/quiz.db`（宿主机旧库）恢复

### 数据库恢复命令（事故后回滚）
```bash
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 "
  docker stop quiz-system
  cp /opt/data/quiz.db /opt/data/quiz.db.empty    # 备份空库（万一）
  cp /opt/quiz-system/data/quiz.db /opt/data/quiz.db    # 用宿主机旧库覆盖
  docker start quiz-system
"
```

---

## 4. 应急热更新（docker cp）

> 仅用于紧急修复，**不作为常规部署方式**。

```bash
# 1. 本地打包（排除数据库和缓存）
cd /c/Users/Yaojie/Documents/GitHub/quiz
tar --exclude='*.db' --exclude='__pycache__' --exclude='data' \
  -czf quiz-src.tar.gz -C src .

# 2. 上传到 ECS
scp -i C:/Users/Yaojie/Documents/openclaw.pem \
  quiz-src.tar.gz root@106.14.99.100:/opt/quiz-system/

# 3. 解压并 cp 到容器
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 << 'EOF'
  cd /opt/quiz-system
  tar -xzf quiz-src.tar.gz -C /tmp/quiz-build
  docker cp /tmp/quiz-build/. quiz-system:/app/
  rm -rf /tmp/quiz-build
EOF

# 4. 如需更新密钥
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 \
  "printf '%s\n' '<KEY>' > /opt/quiz-system/data/deepseek_key.txt"

# 5. 重启容器（改 .py 才需 restart）
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 \
  "docker restart quiz-system"
```

---

## 5. 回滚流程

```bash
# 打回滚标签
docker tag quiz-system:latest quiz-system:rollback-$(date +%s)

# 回滚到指定版本
docker tag quiz-system:rollback-<ts> quiz-system:latest
docker compose up -d
```

> DB 在数据卷 `data`，重建镜像不丢数据。

---

## 6. 运维 API（仅用于紧急操作）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/exec-sql` | 执行 SQL（先自动备份再执行） |
| POST | `/api/admin/backup-db` | 数据库备份 |
| GET | `/api/admin/backup-db` | 列出备份文件 |
| GET | `/api/admin/backup-db/download?name=` | 下载备份 |
| POST | `/api/admin/restart` | 重启服务 |

> ⚠️ **这些接口仅用于紧急操作，不得作为常规部署手段。**

---

## 7. 安全红线（**最高纪律**）

- **🔴 ECS 数据是唯一权威**：本地 `data/quiz.db` 永远只是 ECS 的运行时工作区，**绝对不允许本地数据库覆盖 ECS 数据库**。
  - 数据流方向：**ECS → 本地**（拉库验证用），**不允许 反向**（本地 → ECS）
  - 打包命令必须 `tar --exclude=data` 强制排除本地数据库
  - scp 命令**绝对不能**把本地 `data/quiz.db` 推到 `/opt/data/` 或 `/opt/quiz-system/data/`
  - ECS 的 docker-compose.yml 应**单独维护**（不打包进 tar），用绝对路径挂载 `/opt/data`

- **🔴 部署前快照**：任何 ECS 写操作前必须 `POST /api/admin/backup-db`（这是 ECS 自带的原子备份门）
- **🔴 ECS docker-compose.yml 不动**：只动 `src/*.py` 和 `migrations/` 目录下的文件
- **🔴 部署前后必查 users COUNT(*)**：部署前 `N` 部署后必须仍是 `N`，变了就是事故

- **密钥安全**：`openclaw.pem` 等密钥文件**禁止提交到 git**（已入 `.gitignore`）
- **数据库安全**：任何写操作前必须备份（`POST /api/admin/backup-db`）
- **版本一致**：ECS `build/` 目录必须与本地 `src/` 完全一致
- **健康检查**：部署后必须验证 HTTP 200 响应

---

## 8. 常见问题

### Q: 容器启动失败怎么办？
A: 查看日志 `docker logs quiz-system`，检查 import 错误和数据库连接。

### Q: 镜像构建慢怎么办？
A: pip 层有缓存，通常只需 1-2 分钟。

### Q: 数据库损坏怎么办？
A: 从 `/opt/quiz-system/data/backups/` 恢复最近备份。

---

> **文档版本**：v1.0（2026-08-26）
> **维护者**：阿垤（姚杰）
> **最后更新**：2026-08-26 18:00