"""管理端运维 / 系统接口（admin 专用）
- POST /api/admin/exec-sql      先备份数据库文件，再执行 SQL（SELECT 返回结果 / DML 返回影响行数 / 多语句脚本）
- POST /api/admin/update-file   在 /app 目录内写入文件（供后续纯 API 更新源码/前端）
- POST /api/admin/pip-install   容器内安装 Python 包
- POST /api/admin/re-grade      批量重评历史 code 答题记录
- POST /api/admin/restart       退出当前进程，依赖容器 restart:always 自动重启以加载新代码
- POST /api/admin/backup-db     本地 VACUUM 备份
- GET  /api/admin/backup-db     列出已有备份
- GET  /api/admin/backup-db/download?name=  下载备份文件
说明：所有接口均 require_role("admin")，且数据库文件通过卷映射持久化，备份也落在同一卷，安全可回滚。
"""
import os
import threading
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import text, func, case
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, get_db
from core.deps import require_role

router = APIRouter(prefix="/api/admin", tags=["管理端运维"])

DB_PATH = os.getenv("QUIZ_DB_PATH", "/app/data/quiz.db")
# 备份目录与数据库同处数据卷（./data -> /app/data），随卷持久化、随容器重启不丢
BACKUP_DIR = os.path.join(os.path.dirname(DB_PATH), "backups")
# 容器内应用根目录；写文件接口只允许写入该目录内，避免越权
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 兜底：若上面推导异常，使用常见容器路径
if not os.path.isdir(APP_ROOT) or APP_ROOT == "/":
    APP_ROOT = "/app"


# ============ 请求模型 ============
class SQLRequest(BaseModel):
    sql: str
    script: bool = False  # True 时按多条语句脚本执行（executescript）


class FileRequest(BaseModel):
    path: str       # 目标路径，必须落在 /app 内
    content: str    # 文件内容


# ============ 工具 ============
def _safe_backup() -> "str | None":
    """用 SQLite 的原生 VACUUM INTO 做原子备份（比文件拷贝更安全），落在数据库同目录（卷上持久化）。"""
    if not os.path.exists(DB_PATH):
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # 精确到微秒，避免同秒连续调用撞名
    backup_path = f"{DB_PATH}.bak.{ts}"
    # 兜底：极端情况下仍存在则追加序号（VACUUM INTO 要求目标文件不存在）
    _i = 0
    while os.path.exists(backup_path):
        _i += 1
        backup_path = f"{DB_PATH}.bak.{ts}_{_i}"
    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"PRAGMA busy_timeout=5000")
        cur.execute(f"VACUUM INTO '{backup_path}'")
        conn.commit()
    finally:
        conn.close()
    return backup_path


def _is_select(sql: str) -> bool:
    s = sql.strip().upper()
    return s.startswith("SELECT") or s.startswith("PRAGMA") or s.startswith("WITH") or s.startswith("EXPLAIN")


# ============ 执行 SQL ============
@router.post("/exec-sql")
def exec_sql(data: SQLRequest, _=Depends(require_role("admin"))):
    sql = (data.sql or "").strip()
    if not sql:
        raise HTTPException(status_code=400, detail="SQL 不能为空")

    backup_path = _safe_backup()

    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA busy_timeout=5000")
        if data.script:
            cur.executescript(sql)
            conn.commit()
            return {
                "ok": True,
                "backup": backup_path,
                "script": True,
                "rowcount": cur.rowcount,
            }
        if _is_select(sql):
            cur.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            return {
                "ok": True,
                "backup": backup_path,
                "columns": cols,
                "count": len(rows),
                "rows": [dict(zip(cols, r)) for r in rows],
            }
        cur.execute(sql)
        conn.commit()
        return {
            "ok": True,
            "backup": backup_path,
            "rowcount": cur.rowcount,
        }
    finally:
        conn.close()


# ============ 写文件（供后续纯 API 更新源码/前端） ============
@router.post("/update-file")
def update_file(data: FileRequest, _=Depends(require_role("admin"))):
    norm = os.path.normpath(data.path)
    if norm != APP_ROOT and not norm.startswith(APP_ROOT + os.sep):
        raise HTTPException(status_code=400, detail="只允许写入 /app 目录内")
    parent = os.path.dirname(norm)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(norm, "w", encoding="utf-8") as f:
        f.write(data.content)
    return {"ok": True, "path": norm, "bytes": len(data.content.encode("utf-8"))}


# ============ 安装 Python 包（admin only） ============
class PipRequest(BaseModel):
    package: str


@router.post("/pip-install")
def pip_install(data: PipRequest, _=Depends(require_role("admin"))):
    """在容器内安装 Python 包。"""
    import subprocess
    import sys as _sys

    pkg = (data.package or "").strip()
    if not pkg or " " in pkg or ";" in pkg or "&" in pkg or "|" in pkg:
        raise HTTPException(status_code=400, detail="非法包名")
    try:
        result = subprocess.run(
            [_sys.executable, "-m", "pip", "install", pkg],
            capture_output=True, text=True, timeout=120,
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
        }
    except Exception as e:
        return {"ok": False, "stderr": str(e)}


# ============ 批量重评历史 code 答题记录 ============
@router.post("/re-grade")
def re_grade_code_records(_=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """对所有历史 code 类答题记录调用 LLM 重新评分，并同步更新对应 exam_record 的
    correct/wrong/score。

    仅处理有代码提交的 code 题（user_answer 非空），理论题不动。
    """
    from core.code_runner import run_python
    from core.llm_grader import grade_code

    # 1. 查询所有待重评记录
    rows = db.execute(text("""
        SELECT ar.id, ar.question_id, ar.user_answer, ar.exam_record_id
        FROM answer_records ar
        JOIN questions q ON q.id = ar.question_id
        WHERE q.type = 'code'
          AND ar.user_answer IS NOT NULL
          AND trim(ar.user_answer) != ''
    """)).fetchall()

    results = {"total": len(rows), "success": 0, "fallback": 0, "error": 0, "details": []}
    # 收集需要重算总分的 exam_record_id
    affected_exam_ids = set()

    for row in rows:
        ar_id, q_id, user_code, er_id = row
        detail = {"ar_id": ar_id, "q_id": q_id}
        affected_exam_ids.add(er_id)

        # 2. 获取题目信息
        qr = db.execute(
            text("SELECT content, expected_output, sample_input FROM questions WHERE id = :qid"),
            {"qid": q_id}
        ).fetchone()
        if not qr:
            detail["error"] = "question not found"
            results["details"].append(detail)
            results["error"] += 1
            continue

        # 3. 沙箱执行
        out, err, rc = run_python(str(user_code), qr.sample_input or "")
        if rc != 0:
            run_result = f"运行出错：{err.strip()[:300]}" if err else "运行超时"
        else:
            run_result = out.strip() or "(代码执行成功，无输出)"

        # 4. LLM 评分
        llm = grade_code(
            question_content=qr.content or "",
            expected_output=qr.expected_output or "",
            user_code=str(user_code),
            run_result=run_result,
        )

        if llm["stars"] >= 0:
            # 更新这条 answer_record
            db.execute(text("""
                UPDATE answer_records
                SET llm_score = :score, llm_stars = :stars, llm_feedback = :feedback,
                    is_correct = :is_correct
                WHERE id = :aid
            """), {
                "score": llm["score"], "stars": llm["stars"],
                "feedback": llm.get("feedback", ""),
                "is_correct": 1 if llm["score"] >= 60 else 0,
                "aid": ar_id,
            })
            detail["llm_score"] = llm["score"]
            detail["llm_stars"] = llm["stars"]
            results["success"] += 1
        else:
            # 降级：stdout 匹配
            from core.code_runner import normalize_output
            expected = normalize_output(qr.expected_output or "")
            actual = normalize_output(out)
            ok = bool(expected and actual == expected) or (not expected and rc == 0)
            s = 100 if ok else 0
            db.execute(text("""
                UPDATE answer_records
                SET llm_score = :score, llm_stars = :stars, is_correct = :is_correct
                WHERE id = :aid
            """), {"score": s, "stars": 5 if ok else 0, "is_correct": 1 if ok else 0, "aid": ar_id})
            detail["llm_score"] = s
            detail["fallback"] = True
            results["fallback"] += 1

        results["details"].append(detail)
        time.sleep(0.3)  # API 限速间隔

    db.commit()

    # 5. 重算所有受影响的 exam_records 的 correct/wrong/score
    for er_id in affected_exam_ids:
        rows2 = db.execute(text("""
            SELECT llm_score FROM answer_records WHERE exam_record_id = :eid
        """), {"eid": er_id}).fetchall()
        scores = [r.llm_score for r in rows2 if r.llm_score is not None]
        correct = sum(1 for s in scores if s >= 60)
        wrong = len(scores) - correct
        total_score = sum(scores)
        db.execute(text("""
            UPDATE exam_records
            SET correct = :correct, wrong = :wrong, score = :score
            WHERE id = :eid
        """), {"correct": correct, "wrong": wrong, "score": total_score, "eid": er_id})

    db.commit()
    results["affected_exams"] = len(affected_exam_ids)
    return results


# ============ 重启容器加载新代码 ============
@router.post("/restart")
def restart_app(_=Depends(require_role("admin"))):
    # 依赖 docker-compose 的 restart: always，进程退出后由 docker 自动重启，
    # 重启时重新 import /app 下最新源码与静态文件。先返回响应再退出。
    def _do():
        time.sleep(1)
        os._exit(0)

    threading.Thread(target=_do, daemon=True).start()
    return {"ok": True, "msg": "容器将在约 1 秒后重启以加载新代码（依赖 restart:always）"}


# ============ 数据库备份（本地备份 + 下载） ============
def _ensure_backup_dir() -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR


@router.post("/backup-db")
def backup_db(_=Depends(require_role("admin"))):
    """在 ECS 服务器本地（数据卷）做一次数据库备份，返回备份文件名。

    步骤①：先 VACUUM INTO 到备份目录（原子、比文件拷贝更安全）。
    每日自动任务即调用此接口完成「服务器本地备份」。
    """
    _ensure_backup_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # 精确到微秒，避免同秒连续调用撞名
    backup_path = os.path.join(BACKUP_DIR, f"quiz_{ts}.db")
    _i = 0
    while os.path.exists(backup_path):
        _i += 1
        backup_path = os.path.join(BACKUP_DIR, f"quiz_{ts}_{_i}.db")
    conn = engine.raw_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA busy_timeout=5000")
        cur.execute(f"VACUUM INTO '{backup_path}'")
        conn.commit()
    finally:
        conn.close()
    return {
        "ok": True,
        "name": os.path.basename(backup_path),
        "path": backup_path,
        "size": os.path.getsize(backup_path),
    }


@router.get("/backup-db")
def list_backups(_=Depends(require_role("admin"))):
    """列出服务器上已有的备份文件。"""
    _ensure_backup_dir()
    files = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith(".db"):
            p = os.path.join(BACKUP_DIR, f)
            files.append({
                "name": f,
                "size": os.path.getsize(p),
                "mtime": os.path.getmtime(p),
            })
    return {"ok": True, "count": len(files), "files": files}


@router.get("/backup-db/download")
def download_backup(name: str, _=Depends(require_role("admin"))):
    """步骤②：将服务器上的备份文件下载到本机。

    防目录穿越：只允许 BACKUP_DIR 下的纯文件名，禁止 / \\ .. 等。
    """
    if not name or "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="非法文件名")
    _ensure_backup_dir()
    path = os.path.join(BACKUP_DIR, name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="备份文件不存在")
    # 直接读取字节返回，避免 Starlette FileResponse 在 Docker 卷上
    # 使用 sendfile 导致 body 为 0 字节的问题（overlay/virtio 文件系统已知坑）。
    with open(path, "rb") as f:
        data = f.read()
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )
