"""管理端运维接口（admin 专用）
- POST /api/admin/exec-sql  先备份数据库文件，再执行 SQL（支持 SELECT 返回结果 / DML 返回影响行数 / 多语句脚本）
- POST /api/admin/update-file  在 /app 目录内写入文件（供后续纯 API 更新源码/前端）
- POST /api/admin/restart      退出当前进程，依赖容器 restart:always 自动重启以加载新代码
说明：所有接口均 require_role("admin")，且数据库文件通过卷映射持久化，备份也落在同一卷，安全可回滚。
"""
import os
import threading
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, get_db
from models import User, ExamRecord, AnswerRecord
from schemas import ExamRecordOut, AnswerRecordOut, QuestionOut
from core.deps import require_role

router = APIRouter(prefix="/api/admin", tags=["管理端运维"])

DB_PATH = os.getenv("QUIZ_DB_PATH", "/app/data/quiz.db")
# 备份目录与数据库同处数据卷（./quiz-data -> /app/data），随卷持久化、随容器重启不丢
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
    import time
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


# ============ 学员答题记录（管理员查看） ============
def _admin_record_out(record: ExamRecord, db: Session, with_answers: bool = True) -> ExamRecordOut:
    """管理员视角的记录序列化：不隐藏任何信息。

    与学生端 exam._record_to_out 的区别：
    - code 题的参考代码（question.answer）不置空，管理员可对照批阅；
    - answer_records 里的 user_answer 即学生提交的代码/答案，run_output 为后台实跑结果。
    """
    out = ExamRecordOut.model_validate(record)
    if with_answers:
        ars = db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record.id).all()
        out.answer_records = []
        for ar in ars:
            aro = AnswerRecordOut.model_validate(ar)
            if ar.question:
                qo = QuestionOut.model_validate(ar.question)
                if ar.question.topic:
                    qo.topic_name = ar.question.topic.name
                aro.question = qo  # 管理员可见参考代码，不做隐藏
            out.answer_records.append(aro)
    return out


@router.get("/students")
def list_students(_=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """学员列表（含答题次数、最近一次答题时间），供管理端下拉选择。"""
    students = db.query(User).filter(User.role == "student").order_by(User.created_at.asc()).all()
    result = []
    for s in students:
        exam_count = db.query(ExamRecord).filter(ExamRecord.user_id == s.id).count()
        last = (
            db.query(ExamRecord)
            .filter(ExamRecord.user_id == s.id)
            .order_by(ExamRecord.started_at.desc())
            .first()
        )
        result.append({
            "id": s.id,
            "username": s.username,
            "nickname": s.nickname,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "exam_count": exam_count,
            "last_exam_at": last.started_at.isoformat() if last and last.started_at else None,
        })
    return result


@router.get("/students/{student_id}/records", response_model=list[ExamRecordOut])
def student_records(student_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """某学员的全部答题记录列表（不含每题明细，点详情再查）。"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    records = (
        db.query(ExamRecord)
        .filter(ExamRecord.user_id == student_id)
        .order_by(ExamRecord.started_at.desc())
        .all()
    )
    return [_admin_record_out(r, db, with_answers=False) for r in records]


@router.get("/records/{record_id}", response_model=ExamRecordOut)
def admin_record_detail(record_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """某次答题记录的完整明细：每题的题干、学生答案/提交代码、运行结果、正确答案、讲解。"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _admin_record_out(record, db, with_answers=True)


class AnswerRecordUpdate(BaseModel):
    """管理员修改某题评分/评语"""
    llm_score: int  # 0-100
    llm_feedback: Optional[str] = None


@router.put("/answer-records/{ar_id}")
def admin_update_answer_record(ar_id: int, data: AnswerRecordUpdate, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """管理员修改某道题的评分和评语，修改后自动重算所属答题记录的 score/correct/wrong。"""
    ar = db.query(AnswerRecord).filter(AnswerRecord.id == ar_id).first()
    if not ar:
        raise HTTPException(status_code=404, detail="答题明细不存在")
    if data.llm_score < 0 or data.llm_score > 100:
        raise HTTPException(status_code=400, detail="评分必须在 0-100 之间")
    ar.llm_score = data.llm_score
    ar.llm_stars = min(5, max(0, data.llm_score // 20))  # 按分数折算星级
    ar.is_correct = data.llm_score >= 60
    if data.llm_feedback is not None:
        ar.llm_feedback = data.llm_feedback.strip() or None
    # 重算所属 exam_record 的 correct/wrong/score
    record = db.query(ExamRecord).filter(ExamRecord.id == ar.exam_record_id).first()
    if record:
        all_ars = db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record.id).all()
        record.correct = sum(1 for a in all_ars if (a.llm_score or 0) >= 60)
        record.wrong = record.total - record.correct
        record.score = int(record.correct / record.total * 100) if record.total else 0
    db.commit()
    return {"ok": True, "llm_score": ar.llm_score, "is_correct": ar.is_correct,
            "record_score": record.score if record else None,
            "record_correct": record.correct if record else None,
            "record_wrong": record.wrong if record else None}


@router.delete("/records/{record_id}")
def admin_delete_record(record_id: int, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """删除某次答题记录（含关联的答题明细），用于清理 0 分/无效记录。"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    # 先删关联答题明细（虽然 cascade=all,delete-orphan 会自动删，显式删更稳妥）
    db.query(AnswerRecord).filter(AnswerRecord.exam_record_id == record_id).delete()
    db.delete(record)
    db.commit()
    return {"ok": True}


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


# ============ 学情分析（4 个接口） ============

def _fetch_all(db: Session, sql: str, params: dict = None) -> list:
    """执行查询返回 list[dict]（SQLAlchemy 2.x 用 RowMapping，勿用 row.keys()）"""
    rows = db.execute(text(sql), params or {}).mappings().all()
    return [dict(r) for r in rows]


@router.get("/analytics/overview")
def analytics_overview(grade: Optional[str] = None, subject_id: Optional[int] = None,
                       _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """总览仪表盘：核心指标 + 近14天趋势(按科目) + 科目/题型正确率 + 活跃榜

    可选过滤: grade(年级, 精确匹配 subjects.grade) / subject_id(科目)。
    顶部 KPI 始终为全局总量；趋势/正确率/活跃榜受过滤影响。
    """
    # 过滤条件（基于 exam_records.subject_id -> subjects）
    conds, params = [], {}
    if subject_id is not None:
        conds.append("er.subject_id = :sid")
        params["sid"] = subject_id
    if grade:
        conds.append("s.grade = :grade")
        params["grade"] = grade
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    total_ar = db.execute(text(
        "SELECT COUNT(*) c, SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END) ok FROM answer_records")).fetchone()
    total_exams = db.execute(text("SELECT COUNT(*) c FROM exam_records")).fetchone().c
    active_students = db.execute(text(
        "SELECT COUNT(DISTINCT user_id) c FROM exam_records")).fetchone().c
    today = datetime.now().strftime("%Y-%m-%d")
    today_ar = db.execute(text(
        "SELECT COUNT(*) c FROM answer_records ar JOIN exam_records er ON er.id=ar.exam_record_id "
        "WHERE date(er.started_at)=:d"), {"d": today}).fetchone().c
    week_ar = db.execute(text(
        "SELECT COUNT(*) c FROM answer_records ar JOIN exam_records er ON er.id=ar.exam_record_id "
        "WHERE julianday('now') - julianday(er.started_at) <= 7")).fetchone().c

    # 全局聚合趋势（向后兼容）
    _trend_where = ("WHERE julianday('now') - julianday(er.started_at) <= 14"
                    + ((" AND " + " AND ".join(conds)) if conds else ""))
    trend = _fetch_all(db, f"""
        SELECT date(er.started_at) d,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {_trend_where}
        GROUP BY date(er.started_at) ORDER BY d
    """, params)

    # 按科目分组趋势（前端画多线用）
    trend_by_subject = _fetch_all(db, f"""
        SELECT date(er.started_at) d, er.subject_id, s.name subject,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {_trend_where}
        GROUP BY date(er.started_at), er.subject_id ORDER BY d, er.subject_id
    """, params)

    by_subject = _fetch_all(db, f"""
        SELECT s.id subject_id, s.name subject, s.grade, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY s.id ORDER BY total DESC
    """, params)

    by_type = _fetch_all(db, f"""
        SELECT q.type, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY q.type ORDER BY total DESC
    """, params)

    top_students = _fetch_all(db, f"""
        SELECT u.nickname, u.username, COUNT(er.id) exams,
               MAX(er.started_at) last_at
        FROM exam_records er
        JOIN users u ON u.id=er.user_id
        JOIN subjects s ON s.id=er.subject_id
        {where}
        GROUP BY er.user_id ORDER BY exams DESC LIMIT 10
    """, params)

    total_cnt = total_ar.c or 0
    ok_cnt = total_ar.ok or 0
    return {
        "totals": {
            "answers": total_cnt,
            "correct_rate": round(ok_cnt / total_cnt * 100, 1) if total_cnt else 0,
            "exams": total_exams,
            "active_students": active_students,
            "today_answers": today_ar,
            "week_answers": week_ar,
        },
        "trend": trend,
        "trend_by_subject": trend_by_subject,
        "by_subject": by_subject,
        "by_type": by_type,
        "top_students": top_students,
    }


@router.get("/analytics/student/{student_id}")
def analytics_student(student_id: int, subject_id: Optional[int] = None,
                      _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """学员深度档案：成绩趋势 + 科目/知识点正确率 + 高频错题 + 最近动态

    可选 subject_id 过滤 by_topic / top_wrong（知识点正确率与高频错题）。
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    score_trend = _fetch_all(db, """
        SELECT er.id, er.started_at, er.score, er.total, er.correct, s.name subject
        FROM exam_records er JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid ORDER BY er.started_at
    """, {"uid": student_id})

    by_subject = _fetch_all(db, """
        SELECT s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid GROUP BY s.id ORDER BY total DESC
    """, {"uid": student_id})

    # 各知识点正确率（作答>=2次才统计；SQLite 的 ok/total 是整数除法，需 *1.0）
    _subj_cond = "AND er.subject_id = :sid" if subject_id else ""
    _subj_params = {"uid": student_id, **({"sid": subject_id} if subject_id else {})}
    by_topic = _fetch_all(db, f"""
        SELECT t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid {_subj_cond} GROUP BY q.topic_id HAVING COUNT(*)>=2
        ORDER BY (ok*1.0/total) ASC LIMIT 20
    """, _subj_params)

    top_wrong = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.name topic, s.name subject,
               COUNT(*) wrong_times
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid AND ar.is_correct=0 {_subj_cond}
        GROUP BY q.id ORDER BY wrong_times DESC LIMIT 10
    """, _subj_params)

    recent = _fetch_all(db, """
        SELECT er.id, er.started_at, er.score, er.total, er.correct, s.name subject
        FROM exam_records er JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid ORDER BY er.started_at DESC LIMIT 10
    """, {"uid": student_id})

    return {
        "student": {"id": student.id, "nickname": student.nickname, "username": student.username},
        "score_trend": score_trend,
        "by_subject": by_subject,
        "by_topic": by_topic,
        "top_wrong": top_wrong,
        "recent": recent,
    }


@router.get("/analytics/weakness")
def analytics_weakness(subject_id: Optional[int] = None, grade: Optional[str] = None,
                      _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """知识点薄弱分析：薄弱知识点TOP10 + 反复错题榜 + 低正确率题目

    可选过滤: subject_id(科目) / grade(年级, 精确匹配 subjects.grade)。
    """
    conds, params = [], {}
    if subject_id is not None:
        conds.append("q.subject_id = :sid")
        params["sid"] = subject_id
    if grade:
        conds.append("s.grade = :grade")
        params["grade"] = grade
    where = ("WHERE " + " AND ".join(conds)) if conds else ""

    weak_topics = _fetch_all(db, f"""
        SELECT t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok,
               ROUND(SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) rate
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        {where}
        GROUP BY q.topic_id HAVING COUNT(*)>=5
        ORDER BY rate ASC LIMIT 10
    """, params)

    # wrong_questions 无直连 subjects，需经 questions 关联
    weak_conds = ["w.mastered=0"]
    if subject_id is not None:
        weak_conds.append("q.subject_id = :sid")
    if grade:
        weak_conds.append("s.grade = :grade")
    repeat_wrong = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.name topic, s.name subject,
               COUNT(DISTINCT w.user_id) students, SUM(w.wrong_count) times
        FROM wrong_questions w
        JOIN questions q ON q.id=w.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        WHERE {' AND '.join(weak_conds)}
        GROUP BY q.id HAVING SUM(w.wrong_count)>=2
        ORDER BY times DESC LIMIT 15
    """, params)

    hard_questions = _fetch_all(db, f"""
        SELECT q.id qid, q.content, q.type, t.name topic, s.name subject,
               COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok,
               ROUND(SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) rate
        FROM answer_records ar
        JOIN questions q ON q.id=ar.question_id
        LEFT JOIN topics t ON t.id=q.topic_id
        LEFT JOIN subjects s ON s.id=q.subject_id
        {where}
        GROUP BY q.id HAVING COUNT(*)>=3
        ORDER BY rate ASC LIMIT 15
    """, params)

    return {
        "weak_topics": weak_topics,
        "repeat_wrong": repeat_wrong,
        "hard_questions": hard_questions,
    }


class ReportRequest(BaseModel):
    student_id: int


@router.post("/analytics/report")
def analytics_report(data: ReportRequest, _=Depends(require_role("admin")), db: Session = Depends(get_db)):
    """AI 学情周报：聚合学员数据 → LLM 生成自然语言评语（失败返回 502，不造假）"""
    from core import llm_grader
    from openai import OpenAI

    student = db.query(User).filter(User.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    if not llm_grader.LLM_API_KEY:
        raise HTTPException(status_code=502, detail="LLM_API_KEY 未配置，无法生成 AI 报告")

    by_subject = _fetch_all(db, """
        SELECT s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN subjects s ON s.id=er.subject_id
        WHERE er.user_id=:uid GROUP BY s.id
    """, {"uid": data.student_id})
    by_topic = _fetch_all(db, """
        SELECT t.name topic, s.name subject, COUNT(*) total,
               SUM(CASE WHEN ar.is_correct=1 THEN 1 ELSE 0 END) ok
        FROM answer_records ar
        JOIN exam_records er ON er.id=ar.exam_record_id
        JOIN questions q ON q.id=ar.question_id
        JOIN topics t ON t.id=q.topic_id
        JOIN subjects s ON s.id=q.subject_id
        WHERE er.user_id=:uid GROUP BY q.topic_id HAVING COUNT(*)>=2
        ORDER BY (ok*1.0/total) ASC LIMIT 8
    """, {"uid": data.student_id})
    exams = _fetch_all(db, """
        SELECT er.score, er.started_at FROM exam_records er
        WHERE er.user_id=:uid ORDER BY er.started_at
    """, {"uid": data.student_id})
    wrong_cnt = db.execute(text(
        "SELECT COUNT(*) c FROM wrong_questions WHERE user_id=:uid AND mastered=0"),
        {"uid": data.student_id}).fetchone().c

    if not exams:
        raise HTTPException(status_code=400, detail="该学员还没有答题记录，无法生成报告")

    subj_lines = []
    for r in by_subject:
        rate = round((r["ok"] or 0) / r["total"] * 100, 1) if r["total"] else 0
        subj_lines.append(f"- {r['subject']}：作答{r['total']}次，正确率{rate}%")
    topic_lines = []
    for r in by_topic:
        rate = round((r["ok"] or 0) / r["total"] * 100, 1) if r["total"] else 0
        topic_lines.append(f"- {r['subject']}/{r['topic']}：作答{r['total']}次，正确率{rate}%")
    scores = [e["score"] for e in exams]
    recent_scores = scores[-5:]
    early_scores = scores[:5] if len(scores) >= 5 else scores

    prompt_data = f"""学员：{student.nickname}
总考试次数：{len(exams)}
未掌握错题数：{wrong_cnt}
各科正确率：
{chr(10).join(subj_lines)}
正确率最低的知识点（最薄弱）：
{chr(10).join(topic_lines) if topic_lines else '（数据不足）'}
最早5次考试分数：{early_scores}
最近5次考试分数：{recent_scores}"""

    system_prompt = """你是一位温暖专业的少儿学习顾问，请根据数据为一位小学生家长写一份学习周报。
要求：
1. 用中文，语气温和鼓励，200-350字
2. 分三段：【学习概况】【进步与亮点】【薄弱点与建议】
3. 基于数据客观分析，不要编造数据里没有的信息
4. 建议要具体可操作（如"建议多练习XX知识点"）
5. 直接输出周报内容，不要额外说明"""

    try:
        client = OpenAI(api_key=llm_grader.LLM_API_KEY, base_url=llm_grader.LLM_BASE_URL)
        resp = client.chat.completions.create(
            model=llm_grader.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_data},
            ],
            temperature=0.7,
            max_tokens=800,
            timeout=90,
        )
        report_text = resp.choices[0].message.content.strip()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"AI 报告生成失败：{e}")

    return {
        "student": {"id": student.id, "nickname": student.nickname},
        "report": report_text,
        "data_summary": {
            "exams": len(exams),
            "unmastered_wrong": wrong_cnt,
            "avg_score": round(sum(scores) / len(scores), 1),
            "best_score": max(scores),
        },
    }
