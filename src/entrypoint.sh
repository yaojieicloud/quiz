#!/bin/sh
# 容器启动入口：先跑数据库迁移（保证 scoring_rules.subject_id 等列就位），
# 再幂等播种积分系统种子数据，最后启动服务。
# 顺序关键：种子依赖迁移新增的列，必须先迁移后播种（否则旧库首次启动种子会失败）。
set -e
python -c "from database import engine, Base; import models; Base.metadata.create_all(bind=engine); from migrations import run_migrations; run_migrations(engine)" || echo "[entrypoint] 迁移跳过（可能已应用或出错）"
python seed_reward.py || echo "[entrypoint] seed_reward 跳过（可能已种植或出错）"
exec uvicorn main:app --host 0.0.0.0 --port 8000
