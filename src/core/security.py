"""安全模块：密码哈希 + JWT 令牌"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 使用 pbkdf2_sha256（纯 Python 实现，无需编译 C 扩展）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """data 应包含 'sub'(用户ID) 和 'role'"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 token，失败抛 JWTError"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
