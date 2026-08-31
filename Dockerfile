# quiz-system 业务层镜像
# 依赖：FROM quiz-base:deps（已固化所有 Python 依赖，pip install 不再每次重跑）
# 何时重新 build：只改 src/、static/、migrations/、Dockerfile 时（秒级）
# 何时不需要 build：只改配置/数据（用 docker cp + restart 即可）
#
# 部署流程：
#   1. cd /opt/quiz-system && git pull
#   2. docker build -t quiz-system:latest -f Dockerfile .
#   3. docker tag quiz-system:latest quiz-system:local
#   4. docker compose up -d --force-recreate

FROM quiz-base:deps

WORKDIR /app

# 复制项目代码（依赖已在上层镜像里，无需 pip install）
COPY . .

# 创建数据目录（数据库文件挂载到这里）
RUN mkdir -p /app/data

# 环境变量默认值（密钥在 docker-compose.yml 中设置）
ENV QUIZ_DB_PATH=/app/data/quiz.db
ENV QUIZ_HOST=0.0.0.0
ENV QUIZ_PORT=8000

# 启动入口
RUN chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["/app/entrypoint.sh"]