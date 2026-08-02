"""FastAPI 入口 —— 题库闯关系统"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine
import models  # noqa: E402
from config import STATIC_DIR

# 启动时建表（依赖上面的 models 导入，确保 metadata 已包含全部表）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="题库闯关系统", version="1.0.0")

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 注册路由
from routers import auth, subjects, questions, exam, stats, parent, admin  # noqa: E402

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(questions.router)
app.include_router(exam.router)
app.include_router(stats.router)
app.include_router(parent.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    """根路径返回首页（登录页）"""
    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("QUIZ_HOST", "127.0.0.1")
    port = int(os.getenv("QUIZ_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
