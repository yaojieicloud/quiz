#!/bin/sh
# 容器启动入口：先幂等播种积分系统种子数据，再启动服务
set -e
python seed_reward.py || echo "[entrypoint] seed_reward 跳过（可能已种植或出错）"
exec uvicorn main:app --host 0.0.0.0 --port 8000
