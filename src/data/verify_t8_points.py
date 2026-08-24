"""积分档位化改造 本地验证脚本（T8）。

基于 TestClient + 临时 SQLite 库（不影响真实数据），验证：
1. 迁移 0004 应用（subject_id 列、旧种子清理）
2. seed 幂等（空库播种 18 条；二次执行不重复不覆盖）
3. 组卷白名单 1/10/20/30/40/50；自动降档逻辑
4. 积分发放：各档位×分数段查表、科目专属、兜底、掌握度闸门不受影响
5. 管理端接口：积分矩阵含 subject_id；旧 subject-points 接口已移除
"""
import os
import sys
import tempfile

# 临时库：必须在 import 应用前设置
TMP_DB = os.path.join(tempfile.gettempdir(), "quiz_verify_t8.db")
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ["QUIZ_DB_PATH"] = TMP_DB

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/

from database import engine, Base, SessionLocal  # noqa: E402
import models  # noqa: F401,E402

Base.metadata.create_all(bind=engine)
from migrations import run_migrations  # noqa: E402
run_migrations(engine)

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)
PASS, FAIL = 0, 0


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name} {extra}")


def login(username, password="test1234"):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"登录失败 {username}: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


print("\n==== 1. 迁移与种子 ====")
from sqlalchemy import text  # noqa: E402
with engine.connect() as conn:
    cols = [r[1] for r in conn.execute(text("PRAGMA table_info(scoring_rules)"))]
check("scoring_rules 含 subject_id 列", "subject_id" in cols)
with engine.connect() as conn:
    ver = {r[0] for r in conn.execute(text("SELECT version FROM schema_migrations"))}
check("0004 迁移已登记", "0004_scoring_subject" in ver, str(ver))

# 种子（临时库无科目，先建"Python基础实操"科目再播种，覆盖科目专属规则）
db = SessionLocal()
db.add(models.Subject(name="Python基础实操", category="programming", icon="🐍"))
db.commit()
db.close()

import seed_reward  # noqa: E402
seed_reward.seed()
db = SessionLocal()
n1 = db.query(models.ScoringRule).count()
check("种子后规则数=18（全局16+实操2）", n1 == 18, f"实际 {n1}")
seed_reward.seed()
n2 = db.query(models.ScoringRule).count()
check("二次 seed 幂等（不重复不覆盖）", n2 == n1, f"{n1}→{n2}")

# 手动改一条，再 seed，确认不重置
r1 = db.query(models.ScoringRule).filter(models.ScoringRule.question_count == 50,
                                          models.ScoringRule.score_band == 100).first()
orig = r1.points
r1.points = 99
db.commit()
seed_reward.seed()
db.expire_all()
r1b = db.query(models.ScoringRule).filter(models.ScoringRule.question_count == 50,
                                           models.ScoringRule.score_band == 100).first()
check("后台修改不被 seed 重置", r1b.points == 99, f"{r1b.points}")
r1b.points = orig
db.commit()
db.close()

print("\n==== 2. 账号与题库准备 ====")
r = client.post("/api/auth/register?regkey=openschool2026",
                json={"username": "t8admin", "password": "test1234", "nickname": "T8管理员", "role": "admin"})
check("注册管理员", r.status_code == 200, r.text[:200])
r = client.post("/api/auth/register?regkey=openschool2026",
                json={"username": "t8stu", "password": "test1234", "nickname": "T8学员", "role": "student"})
check("注册学员", r.status_code == 200, r.text[:200])
H_ADM = login("t8admin")
H_STU = login("t8stu")

# 建科目+课时+30 道单选题（模拟"该课只有 30 题"的漏洞场景）
r = client.post("/api/subjects", json={"name": "T8测试数学", "category": "culture", "icon": "🧪"}, headers=H_ADM)
check("建科目", r.status_code == 200, r.text[:200])
SUB = r.json()["id"]
r = client.post("/api/topics", json={"subject_id": SUB, "name": "T8第一课", "unit": "上册"}, headers=H_ADM)
check("建课时", r.status_code == 200, r.text[:200])
TOP = r.json()["id"]

qs = [{"subject_id": SUB, "topic_id": TOP, "type": "choice",
       "content": f"T8第{i}题：1+1=?", "options": ["1", "2", "3", "4"],
       "answer": "1", "difficulty": 1} for i in range(30)]
r = client.post("/api/questions/batch", json=qs, headers=H_ADM)
check("批量导入 30 题", r.status_code == 200, r.text[:200])

print("\n==== 3. 组卷降档 ====")
def start(count):
    return client.post("/api/exam/start",
                       json={"subject_id": SUB, "topic_ids": [TOP], "types": [], "count": count,
                             "mode": "custom", "tier": 1}, headers=H_STU)

r = start(50)
check("选50题(池30)→降档40题档仍不足→30题", r.status_code == 200, r.text[:200])
d = r.json()
check("  实际发题=30", len(d["questions"]) == 30 and d["actual_count"] == 30, f"{len(d['questions'])}")
check("  downgraded=true", d["downgraded"] is True)
check("  requested=50", d["requested_count"] == 50)

r = start(10)
d = r.json()
check("选10题(池30)→不降档", r.status_code == 200 and len(d["questions"]) == 10 and d["downgraded"] is False)

r = start(15)
check("选15题→400 白名单拦截", r.status_code == 400, r.text[:120])

print("\n==== 4. 积分发放 ====")
# 每个用例用独立课时，避免掌握度闸门干扰（同课精通后不再发分，属设计预期）
_case_no = [0]

def fresh_topic(sub, n_questions, tier=1):
    _case_no[0] += 1
    r = client.post("/api/topics", json={"subject_id": sub, "name": f"T8课{_case_no[0]}", "unit": "上册"}, headers=H_ADM)
    tid = r.json()["id"]
    qs = [{"subject_id": sub, "topic_id": tid, "type": "choice",
           "content": f"T8课{_case_no[0]}第{i}题", "options": ["1", "2", "3", "4"],
           "answer": "1", "difficulty": 1, "tier": tier} for i in range(n_questions)]
    client.post("/api/questions/batch", json=qs, headers=H_ADM)
    return tid

def do_case(sub, pool_size, request_count, correct_count, expect_pts, tier=1):
    """造 pool_size 题课时 → 请求 request_count 档 → 答对 correct_count 题 → 断言积分"""
    tid = fresh_topic(sub, pool_size, tier)
    r = client.post("/api/exam/start", json={"subject_id": sub, "topic_ids": [tid], "types": [],
                                              "count": request_count, "mode": "custom", "tier": tier}, headers=H_STU)
    d = r.json()
    qids = [q["id"] for q in d["questions"]]
    answers = [{"question_id": q, "user_answer": "1" if i < correct_count else "0"}
               for i, q in enumerate(qids)]
    r = client.post("/api/exam/submit", json={"subject_id": sub, "mode": "custom", "topic_ids": [tid],
                                               "answers": answers, "duration_seconds": 10, "tier": tier}, headers=H_STU)
    return r.json(), d

# 主漏洞场景：该课仅 30 题，选 50 题 → 降档到 30 题，全对 100 分 → 3 积分（不再是 50 题档的 5 分）
rec, d = do_case(SUB, pool_size=30, request_count=50, correct_count=30, expect_pts=3)
check("漏洞封堵：30题课选50档→降档30题全对 → 3积分(非5)",
      rec["score"] == 100 and rec["points_earned"] == 3 and d["downgraded"],
      f"score={rec['score']} pts={rec['points_earned']} down={d['downgraded']}")

rec, _ = do_case(SUB, 30, 30, 29, 2)
check("30题错1(96分) → 积分2", rec["score"] == 96 and rec["points_earned"] == 2,
      f"score={rec['score']} pts={rec['points_earned']}")

rec, _ = do_case(SUB, 10, 10, 10, 1)
check("10题全对 → 积分1", rec["score"] == 100 and rec["points_earned"] == 1,
      f"score={rec['score']} pts={rec['points_earned']}")

rec, _ = do_case(SUB, 20, 20, 20, 2)
check("20题全对 → 积分2", rec["score"] == 100 and rec["points_earned"] == 2,
      f"score={rec['score']} pts={rec['points_earned']}")

rec, _ = do_case(SUB, 40, 40, 40, 4)
check("40题全对 → 积分4", rec["score"] == 100 and rec["points_earned"] == 4,
      f"score={rec['score']} pts={rec['points_earned']}")

# 50 题档各分数段（50 题课）
SUB2 = client.post("/api/subjects", json={"name": "T8测试语文", "category": "culture", "icon": "🧪"}, headers=H_ADM).json()["id"]
rec, _ = do_case(SUB2, 50, 50, 50, 5)
check("50题全对 → 积分5", rec["score"] == 100 and rec["points_earned"] == 5,
      f"score={rec['score']} pts={rec['points_earned']}")

rec, _ = do_case(SUB2, 50, 50, 30, 1)
check("50题对30(60分) → 积分1", rec["score"] == 60 and rec["points_earned"] == 1,
      f"score={rec['score']} pts={rec['points_earned']}")

# <60 分 → 0 分（用 25/50=50 精确值，避开 int(correct/total*100) 浮点截断边界）
rec, _ = do_case(SUB2, 50, 50, 25, 0)
check("50题对25(50分) → 积分0", rec["score"] == 50 and rec["points_earned"] == 0,
      f"score={rec['score']} pts={rec['points_earned']}")

# tier 倍率：30 题全对进阶档 → 3×2 = 6（造题用进阶档）
rec, _ = do_case(SUB, 30, 30, 30, 6, tier=2)
check("30题全对进阶档 → 积分6(3×2)", rec["score"] == 100 and rec["points_earned"] == 6,
      f"score={rec['score']} pts={rec['points_earned']}")

# 掌握度闸门：同课再刷（已精通）→ 0 分
tid_gate = fresh_topic(SUB, 30)
for _ in range(2):
    r = client.post("/api/exam/start", json={"subject_id": SUB, "topic_ids": [tid_gate], "types": [],
                                              "count": 30, "mode": "custom", "tier": 1}, headers=H_STU)
    qids = [q["id"] for q in r.json()["questions"]]
    answers = [{"question_id": q, "user_answer": "1"} for q in qids]
    r = client.post("/api/exam/submit", json={"subject_id": SUB, "mode": "custom", "topic_ids": [tid_gate],
                                               "answers": answers, "duration_seconds": 10, "tier": 1}, headers=H_STU)
rec = r.json()
check("掌握度闸门：精通课再刷 → 0积分", rec["points_earned"] == 0, f"pts={rec['points_earned']}")

print("\n==== 5. 管理端接口 ====")
r = client.get("/api/admin/scoring-rules", headers=H_ADM)
rows = r.json()
check("积分矩阵含 subject_id 字段", all("subject_id" in x for x in rows))
subj_rows = [x for x in rows if x["subject_id"] is not None]
check("Python实操专属规则存在(≥1条)", len(subj_rows) >= 1, f"{len(subj_rows)}")

r = client.get("/api/admin/subject-points", headers=H_ADM)
check("旧 subject-points 接口已移除(404)", r.status_code == 404, f"{r.status_code}")

# 新增一条 60 题档规则，验证后台可配
r = client.post("/api/admin/scoring-rules",
                json={"question_count": 60, "score_band": 100, "points": 6, "subject_id": None}, headers=H_ADM)
check("后台新增 60 题档规则", r.status_code == 200, r.text[:120])

print(f"\n==== 结果：PASS {PASS} / FAIL {FAIL} ====")
sys.exit(1 if FAIL else 0)
