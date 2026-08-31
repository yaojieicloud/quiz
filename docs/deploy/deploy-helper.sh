#!/bin/bash
# ECS 一键部署脚本 - 从 src/ 解压到 /opt/quiz-system/ 并重建镜像
# 用法: ./deploy-helper.sh (在本机运行)

set -e
BASE="/c/Users/Yaojie/Documents/GitHub/quiz"
SSH="C:/Program Files/Git/usr/bin/ssh.exe"
SCP="C:/Program Files/Git/usr/bin/scp.exe"
KEY="C:/Users/Yaojie/Documents/openclaw.pem"
HOST="root@106.14.99.100"

echo "=== 1. 检查本地代码 ==="
cd "$BASE"
git status --porcelain | grep -q . && echo "⚠️ 未提交文件:" && git status --porcelain && exit 1 || echo "✅ 干净的 git 工作区"

echo "=== 2. 打包 src/ (仅源码) ==="
cd "$BASE"
tar -czf /tmp/quiz-src.tar.gz \
  --exclude=.git \
  --exclude=__pycache__ \
  --exclude=*.pyc \
  -C src .

echo "=== 3. 推送到 ECS ==="
scp -i $KEY -o StrictHostKeyChecking=no /tmp/quiz-src.tar.gz $HOST:/opt/quiz-system/

echo "=== 4. ECS 解压 + 构建 + 启动 ==="
ssh -i $KEY -o StrictHostKeyChecking=no $HOST \
  "cd /opt/quiz-system && \
   tar -xzf quiz-src.tar.gz && rm quiz-src.tar.gz && \
   docker build -t quiz-system:latest -f Dockerfile . && \
   docker compose up -d && \
   docker ps -f name=quiz-system --format \"{{.Status}} {{.Image}}\""

echo "=== 5. 健康检查 ==="
echo "HTTP: $(curl -s -o /dev/null -w \"%{http_code}\" http://106.14.99.100:8000/)"

echo "=== ✅ 部署完成 ==="
