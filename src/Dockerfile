FROM quiz-base:3.13

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录（数据库文件挂载到这里）
RUN mkdir -p /app/data

# 环境变量默认值（密钥在 docker-compose.yml 中设置）
ENV QUIZ_DB_PATH=/app/data/quiz.db
ENV QUIZ_HOST=0.0.0.0
ENV QUIZ_PORT=8000

# 启动入口（先幂等播种积分系统种子数据，再启动服务）
RUN chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["/app/entrypoint.sh"]
