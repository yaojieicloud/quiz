"""认证路由：注册 / 登录 / 当前用户 / 绑定孩子"""
import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, ParentChild
from schemas import UserCreate, LoginRequest, Token, UserOut, BindChildRequest
from core.security import hash_password, verify_password, create_access_token
from core.deps import get_current_user, generate_bind_code

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 注册功能默认隐藏：需通过 ?regkey=<密钥> 调出。密钥可用环境变量 QUIZ_REGKEY 覆盖。
REGKEY = os.getenv("QUIZ_REGKEY", "openschool2026")


@router.post("/register", response_model=Token)
def register(data: UserCreate, regkey: str = Query(None), db: Session = Depends(get_db)):
    # 默认关闭公开注册；只有携带正确 regkey 才放行（客户端隐藏 UI + 服务端二次校验）
    if not regkey or not secrets.compare_digest(regkey, REGKEY):
        raise HTTPException(status_code=403, detail="注册功能已关闭，如需开通请联系管理员")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        nickname=data.nickname,
        password_hash=hash_password(data.password),
        role=data.role,
        bind_code=generate_bind_code() if data.role == "student" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/bind-child", response_model=UserOut)
def bind_child(data: BindChildRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """家长通过绑定码绑定孩子"""
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="仅家长角色可绑定孩子")
    child = db.query(User).filter(User.bind_code == data.bind_code, User.role == "student").first()
    if not child:
        raise HTTPException(status_code=404, detail="绑定码无效")
    if child.id == user.id:
        raise HTTPException(status_code=400, detail="不能绑定自己")
    existing = db.query(ParentChild).filter(ParentChild.parent_id == user.id, ParentChild.child_id == child.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已绑定该孩子")
    link = ParentChild(parent_id=user.id, child_id=child.id)
    db.add(link)
    db.commit()
    return UserOut.model_validate(child)


@router.get("/children", response_model=list[UserOut])
def my_children(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """家长查看已绑定的孩子列表"""
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="仅家长可查看")
    links = db.query(ParentChild).filter(ParentChild.parent_id == user.id).all()
    return [UserOut.model_validate(link.child) for link in links]
