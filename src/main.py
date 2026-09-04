"""FastAPI 入口 —— 题库闯关系统"""
import os
import json
import logging
import traceback
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import Base, engine, SessionLocal
import models  # noqa: E402
from config import STATIC_DIR

logger = logging.getLogger("quiz")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
    logger.addHandler(_h)

# 启动时建表（依赖上面的 models 导入，确保 metadata 已包含全部表）
Base.metadata.create_all(bind=engine)

# 轻量迁移：为已存在的库补齐增量字段/索引（见 src/migrations/）
from migrations import run_migrations

run_migrations()

app = FastAPI(title="题库闯关系统", version="1.0.0")


# ============ BUG-8：全链路错误日志 ============
def _log_error_to_db(kind, message, status_code=None, http_method=None, request_url=None,
                    response=None, stack=None, source=None, page_url=None,
                    user_id=None, username=None, role=None):
    """统一写 error_logs 表。失败兜底到文件 + stdout（绝不让日志自己抛异常）。"""
    try:
        from models import ErrorLog
        with SessionLocal() as db:
            log = ErrorLog(
                kind=kind, status_code=status_code, http_method=http_method,
                request_url=request_url, message=(message or "(空)")[:2000],
                stack=(stack or "")[:4000] if stack else None,
                content_json=json.dumps(response, ensure_ascii=False)[:5000] if response else None,
                source=source, page_url=page_url, user_id=user_id, username=username, role=role,
                created_at=datetime.utcnow(),
            )
            db.add(log); db.commit()
    except Exception as e:
        # 兜底：写文件 + logger（绝不递归）
        try:
            import os as _os
            LOG_FILE = _os.path.join(_os.getenv("QUIZ_DB_PATH", "/app/data/quiz.db").rsplit("/", 1)[0], "error_log_fallback.txt")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().isoformat()}] [{kind}] {message} | err={e}\n")
        except Exception:
            pass
        logger.exception("[error_log_fallback] 写库失败: %s", e)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """422 Pydantic 校验错误：记录原始值（这是阿垚 422 排查的命根子）。"""
    body_bytes = await request.body()
    body_text = ""
    try: body_text = body_bytes.decode("utf-8", errors="replace")[:1500]
    except Exception: pass
    # 截断：422 原始错误数组是 [ {type, loc, msg, input, url, ctx}, ... ]
    err_summary = json.dumps(exc.errors(), ensure_ascii=False)[:1500]
    user_id = getattr(request.state, "user_id", None)
    _log_error_to_db(
        kind="validation_422", message=f"422 {err_summary}",
        status_code=422, http_method=request.method, request_url=str(request.url.path),
        response={"errors": exc.errors(), "body": body_text},
        source=f"{request.client.host if request.client else '?'}",
        page_url=str(request.url),
        user_id=user_id,
    )
    logger.warning("[422] %s %s | %s", request.method, request.url.path, err_summary)
    # 保持与 FastAPI 默认 422 响应体兼容
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """业务主动 raise 的 HTTPException：>=500 的打日志（5xx 是事故），<500 仅记 warn。"""
    if exc.status_code >= 500:
        _log_error_to_db(
            kind="server_error", message=f"{exc.status_code} {exc.detail}",
            status_code=exc.status_code, http_method=request.method, request_url=str(request.url.path),
            response={"detail": exc.detail},
        )
        logger.error("[%d] %s %s | %s", exc.status_code, request.method, request.url.path, exc.detail)
    else:
        logger.info("[%d] %s %s | %s", exc.status_code, request.method, request.url.path, exc.detail)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """所有未捕获异常：500 + 完整 traceback 入库 + 友好响应。"""
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_text = "".join(tb)
    _log_error_to_db(
        kind="server_error", message=f"500 {type(exc).__name__}: {exc}",
        status_code=500, http_method=request.method, request_url=str(request.url.path),
        stack=tb_text, source=f"{request.client.host if request.client else '?'}",
        page_url=str(request.url),
    )
    logger.error("[500] %s %s | %s\n%s", request.method, request.url.path, exc, tb_text)
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": f"服务器内部错误：{type(exc).__name__}: {str(exc)[:200]}"})


# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 注册路由
from routers import auth, subjects, questions, exam, stats, parent, reward, reward_admin, mastery, system, analytics, proxy, log  # noqa: E402

app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(questions.router)
app.include_router(exam.router)
app.include_router(stats.router)
app.include_router(parent.router)
app.include_router(reward.router)
app.include_router(reward_admin.router)
app.include_router(mastery.router)
app.include_router(system.router)
app.include_router(analytics.router)
app.include_router(proxy.router)
app.include_router(log.router)


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
