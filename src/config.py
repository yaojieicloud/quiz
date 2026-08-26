"""全局配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ★ 数据库唯一合法路径 = <项目根>/data/quiz.db（本地开发 + Docker 卷挂载统一用这一个）
# 规则：容器内由环境变量 QUIZ_DB_PATH=/app/data/quiz.db 指向数据卷；
#      本地裸跑（不设环境变量）回落到 <项目根>/data/quiz.db，严禁再落到 src/quiz.db。
# 安装说明：删除 src/quiz.db（旧默认库），唯一合法路径见 docs/init/dependencies.md 说明。
PROJECT_ROOT = BASE_DIR.parent
DB_PATH = Path(os.getenv("QUIZ_DB_PATH", str(PROJECT_ROOT / "data" / "quiz.db")))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# JWT
SECRET_KEY = os.getenv("QUIZ_SECRET_KEY", "quiz-system-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 静态文件
STATIC_DIR = BASE_DIR / "static"
