"""全局配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 数据库路径：优先用环境变量（Docker 卷映射用），默认放项目根目录
DB_PATH = Path(os.getenv("QUIZ_DB_PATH", str(BASE_DIR / "quiz.db")))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# JWT
SECRET_KEY = os.getenv("QUIZ_SECRET_KEY", "quiz-system-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# 静态文件
STATIC_DIR = BASE_DIR / "static"
