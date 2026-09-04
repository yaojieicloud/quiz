"""BUG-8：错误日志记录接口。
- POST /api/log/error   接收前端 JS 报错 + API 异常的原始上报（内部用，非公开）
- GET  /api/log/errors  admin 查看错误日志列表（分页）
- DELETE /api/log/errors  admin 清理历史日志（可选，按时间范围）
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from core.deps import require_role

router = APIRouter(prefix="/api/log", tags=["错误日志"])


class ErrorReport(BaseModel):
    kind: str                          # js_error / promise_rejection / api_error / network_error / server_error
    message: str                       # 已格式化的人类可读错误正文
    status: Optional[int] = None       # api_error 时 HTTP 状态码
    method: Optional[str] = None       # api_error 时请求方法
    url: Optional[str] = None          # api_error 时请求 URL
    response: Optional[dict] = None    # api_error 时响应体（原始）
    stack: Optional[str] = None        # JS 堆栈 / Python traceback
    source: Optional[str] = None        # js_error 时 filename:line:col
    page_url: Optional[str] = None     # 报错页面 URL
    path: Optional[str] = None         # 路由 path（如 /static/quiz.html）
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


@router.post("/error")
def receive_error_report(report: ErrorReport, db: Session = Depends(get_db)):
    """接收前端上报的 JS 报错 / API 异常，写入 error_logs 表。

    此接口本身不鉴权（前端在网络错误时也可能无法带 token），
    但 user_id / username / role 是可选的，前端尽力传。
    """
    from models import ErrorLog
    from datetime import datetime

    try:
        log = ErrorLog(
            kind=report.kind,
            status_code=report.status,
            http_method=report.method,
            request_url=report.url,
            message=report.message[:2000] if report.message else "(空)",
            stack=(report.stack or "")[:4000] if report.stack else None,
            content_json=json.dumps(report.response, ensure_ascii=False)[:5000]
                        if report.response else None,
            source=report.source,
            page_url=report.page_url,
            user_id=report.user_id,
            username=report.username,
            role=report.role,
            created_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        return {"ok": True}
    except Exception as e:
        # 即使写库失败也不抛给前端，避免上报死循环
        db.rollback()
        # 尝试落文件兜底
        try:
            import os, datetime
            LOG_FILE = os.path.join(os.getenv("QUIZ_DB_PATH", "/app/data/quiz.db").rsplit("/", 1)[0], "error_log_fallback.txt")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.utcnow().isoformat()}] {json.dumps(report.dict(), ensure_ascii=False)}\n")
        except Exception:
            pass
        return {"ok": False, "err": str(e)}


class ErrorLogOut(BaseModel):
    id: int
    kind: str
    status_code: Optional[int]
    http_method: Optional[str]
    request_url: Optional[str]
    message: str
    stack: Optional[str]
    content_json: Optional[str]
    source: Optional[str]
    page_url: Optional[str]
    user_id: Optional[int]
    username: Optional[str]
    role: Optional[str]
    created_at: str
    class Config:
        from_attributes = True


@router.get("/errors")
def list_error_logs(
    page: int = 1,
    page_size: int = 30,
    kind: Optional[str] = None,
    user_id: Optional[int] = None,
    _=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """admin 专用：分页查看错误日志（按时间倒序）。"""
    from models import ErrorLog
    from sqlalchemy import desc

    q = db.query(ErrorLog)
    if kind:
        q = q.filter(ErrorLog.kind == kind)
    if user_id:
        q = q.filter(ErrorLog.user_id == user_id)

    total = q.count()
    rows = (
        q.order_by(desc(ErrorLog.id))
         .offset((page - 1) * page_size)
         .limit(page_size)
         .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            ErrorLogOut(
                id=r.id,
                kind=r.kind,
                status_code=r.status_code,
                http_method=r.http_method,
                request_url=r.request_url,
                message=r.message,
                stack=r.stack,
                content_json=r.content_json,
                source=r.source,
                page_url=r.page_url,
                user_id=r.user_id,
                username=r.username,
                role=r.role,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
            for r in rows
        ],
    }


@router.delete("/errors")
def delete_error_logs(
    older_than_days: int = 30,
    _=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """admin 专用：删除 N 天前的错误日志（默认 30 天），避免表无限增长。"""
    from models import ErrorLog
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    deleted = db.query(ErrorLog).filter(ErrorLog.created_at < cutoff).delete()
    db.commit()
    return {"deleted": deleted, "older_than_days": older_than_days}
