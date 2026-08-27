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

# 2. 打包整个项目（排除不需要的文件）
tar -czf /tmp/quiz-project.tar.gz \
  --exclude=.git \
  --exclude=.venv \
  --exclude=data \
  --exclude=__pycache__ \
  --exclude=node_modules \
  src/ data/ docs/ README.md CODEBUDDY.md

# 3. 推送文件到 ECS build/ 目录
scp -i C:/Users/Yaojure/Documents/openclaw.pem \
  /tmp/quiz-project.tar.gz \
  root@106.14.99.100:/opt/quiz-system/

# 4. 登录 ECS 解压、重建镜像、重启容器
ssh -i C:/Users/Yaojie/Documents/openclaw.pem root@106.14.99.100 << 'EOF'
  cd /opt/quiz-system
  tar -xzf quiz-project.tar.gz
  cd build
  docker build -t quiz-system:latest -f Dockerfile .
  cd /opt/quiz-system
  docker compose up -d
EOF

# 5. 健康检查
curl -o /dev/null -w '%{http_code}\n' http://106.14.99.100:8000/
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

## 7. 安全红线

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