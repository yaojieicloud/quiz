# Docker 部署指南（ECS）

## 一、项目结构说明

```
quiz_system/
├── main.py              # FastAPI 入口
├── config.py            # 配置（数据库路径、JWT密钥等，支持环境变量）
├── database.py          # 数据库引擎
├── models.py            # 数据模型
├── schemas.py           # Pydantic 校验
├── requirements.txt     # Python 依赖
├── quiz.db              # ⬅️ 数据库文件（SQLite，这就是你要找的文件）
├── routers/             # API 路由
├── core/                # 安全模块（JWT、密码哈希）
├── static/              # 前端页面（HTML/CSS/JS）
├── data/                # 题目数据 + 导入脚本
├── Dockerfile           # Docker 构建文件
├── docker-compose.yml   # Docker Compose 编排
└── .dockerignore
```

## 二、数据库文件

数据库文件就是 **`quiz.db`**（SQLite），位于 `quiz_system/` 根目录。

- 当前包含：Python 1000题 + 数学 50题 = 1050题
- 文件大小：约几MB
- **不打包进 Docker 镜像**，通过卷映射挂载，这样升级镜像不丢数据

## 三、本地构建镜像

```bash
cd quiz_system

# 构建镜像
docker build -t quiz-system:latest .

# 验证镜像
docker images | grep quiz-system
```

## 四、上传到 ECS（两种方式）

### 方式 A：导出镜像文件上传（推荐，无需镜像仓库）

```bash
# 1. 本地导出镜像为 tar 文件
docker save quiz-system:latest -o quiz-system.tar

# 2. 上传到 ECS（用 scp 或其他工具）
scp quiz-system.tar root@你的ECS公网IP:/opt/

# 3. 在 ECS 上加载镜像
ssh root@你的ECS公网IP
docker load -i /opt/quiz-system.tar

# 4. 上传数据库文件到 ECS
scp quiz.db root@你的ECS公网IP:/opt/quiz-system/quiz-data/

# 5. 上传 docker-compose.yml 到 ECS
scp docker-compose.yml root@你的ECS公网IP:/opt/quiz-system/
```

### 方式 B：推送到镜像仓库（适合频繁更新）

```bash
# 1. 登录镜像仓库（阿里云ACR / DockerHub 等）
docker login --username=你的用户名 registry.cn-hangzhou.aliyuncs.com

# 2. 给镜像打标签
docker tag quiz-system:latest registry.cn-hangzhou.aliyuncs.com/你的命名空间/quiz-system:latest

# 3. 推送
docker push registry.cn-hangzhou.aliyuncs.com/你的命名空间/quiz-system:latest

# 4. 在 ECS 上拉取
docker pull registry.cn-hangzhou.aliyuncs.com/你的命名空间/quiz-system:latest
```

## 五、ECS 上部署运行

### 1. 准备目录结构

在 ECS 上创建目录：

```bash
mkdir -p /opt/quiz-system/quiz-data
cd /opt/quiz-system
```

### 2. 放置文件

将以下文件放到 ECS 的 `/opt/quiz-system/` 目录：

```
/opt/quiz-system/
├── docker-compose.yml    # 编排文件
└── quiz-data/
    └── quiz.db           # 数据库文件（从本地上传过来）
```

### 3. 修改 docker-compose.yml（如果用方式A导出镜像）

编辑 `docker-compose.yml`，注释掉 `build`，启用 `image`：

```yaml
services:
  quiz-app:
    # build: .          # 注释掉
    image: quiz-system:latest   # 用这个
    container_name: quiz-system
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./quiz-data:/app/data
    environment:
      - QUIZ_DB_PATH=/app/data/quiz.db
      - QUIZ_SECRET_KEY=你的自定义密钥   # 改成你自己的密钥
      - TZ=Asia/Shanghai
```

### 4. 启动

```bash
cd /opt/quiz-system
docker compose up -d

# 查看运行状态
docker compose ps
docker logs quiz-system

# 测试
curl http://localhost:8000/api/health
# 应返回 {"status":"ok"}
```

### 5. 访问

浏览器打开：`http://你的ECS公网IP:8000`

> 确保 ECS 安全组放通了 **8000 端口**（TCP 入方向）

## 六、数据库说明

### 为什么用卷映射？

```
容器内: /app/data/quiz.db  ←──映射──→  宿主机: /opt/quiz-system/quiz-data/quiz.db
```

- **数据持久化**：容器删除/重建，数据不丢失
- **方便备份**：直接在宿主机复制 `quiz.db` 即可备份
- **方便升级**：重新构建镜像后，`docker compose up -d` 即可升级，数据保留

### 如果是全新部署（没有现成数据库）

不传 `quiz.db`，容器启动时会自动创建空数据库（表结构自动建好）。
然后通过管理后台导入题目，或把题目 JSON 传上去执行导入脚本：

```bash
# 进入容器执行导入脚本
docker exec -it quiz-system python data/import_questions.py
docker exec -it quiz-system python data/import_py500.py
```

### 备份数据库

```bash
# 在 ECS 上备份
cp /opt/quiz-system/quiz-data/quiz.db /opt/quiz-system/quiz-data/quiz-backup-$(date +%Y%m%d).db
```

## 七、常用运维命令

```bash
# 查看日志
docker logs -f quiz-system

# 重启
docker compose restart

# 停止
docker compose down

# 升级（重新构建镜像后）
docker compose up -d

# 进入容器调试
docker exec -it quiz-system bash
```

## 八、安全组配置

在 ECS 控制台 → 安全组 → 添加入方向规则：

| 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|
| TCP | 8000 | 0.0.0.0/0 | 题库系统访问 |
| TCP | 22 | 你的IP | SSH 管理（已有则跳过） |

## 九、环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `QUIZ_DB_PATH` | `/app/data/quiz.db` | 数据库文件路径 |
| `QUIZ_SECRET_KEY` | 内置默认值 | JWT 加密密钥，**生产环境务必修改** |
| `QUIZ_HOST` | `0.0.0.0` | 监听地址 |
| `QUIZ_PORT` | `8000` | 监听端口 |
| `TZ` | `Asia/Shanghai` | 时区 |
