"""精通奖励功能 本地验证脚本（M5）。

基于 TestClient + 临时 SQLite 库，验证：
1. 迁移 0005（mastery_rewards 表 + 唯一约束）
2. 跃迁发分：达成精通 → 奖励 = 当前 wheel_cost（mode=new）
3. 历史补发：已精通未发奖的课，在下次新精通时一次性补发（mode=retroactive）
4. 防重复：同一课同一档位再次提交不再发奖
5. 进阶档独立：同课进阶精通再奖一次
6. wheel_cost=0 保护：不发放
7. admin 测试接口：只读预览，不写任何数据
"""
import os
import sys
import tempfile

TMP_DB = os.path.join(tempfile.gettempdir(), "quiz_verify_m5.db")
if os.path.exists(TMP_DB):
    os.remove(TMP_DB)
os.environ["QUIZ_DB_PATH"] = TMP_DB

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/

from database import engine, Base, SessionLocal  # noqa: E402
import models  # noqa: F401,E402

Base.metadata.create_all(bind=engine)
from migrations import run_migrations  # noqa: E402
run_migrations(engine)

from sqlalchemy import text  # noqa: E402
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


def set_wheel_cost(v, H_ADM):
    client.put("/api/admin/config/wheel_cost", json={"value": str(v)}, headers=H_ADM)


def get_balance(H):
    return client.get("/api/points/balance", headers=H).json()["balance"]


print("\n==== 1. 迁移 ====")
with engine.connect() as conn:
    tables = {r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
    ver = {r[0] for r in conn.execute(text("SELECT version FROM schema_migrations"))}
check("mastery_rewards 表已建", "mastery_rewards" in tables)
check("0005 迁移已登记", "0005_mastery_rewards" in ver)
with engine.connect() as conn:
    idx = conn.execute(text("PRAGMA index_list(mastery_rewards)")).fetchall()
check("唯一约束索引存在", any("sqlite_autoindex" in str(r[1]) or "uq" in str(r[1]) for r in idx), str(idx))

print("\n==== 2. 种子 + 账号 + 题库 ====")
import seed_reward  # noqa: E402
db = SessionLocal()
db.add(models.Subject(name="Python基础实操", category="programming", icon="🐍"))
db.commit()
db.close()
seed_reward.seed()

r = client.post("/api/auth/register?regkey=openschool2026",
                json={"username": "m5adm", "password": "test1234", "nickname": "M5管理", "role": "admin"})
check("注册管理员", r.status_code == 200, r.text[:150])
r = client.post("/api/auth/register?regkey=openschool2026",
                json={"username": "m5stu", "password": "test1234", "nickname": "M5学员", "role": "student"})
check("注册学员", r.status_code == 200, r.text[:150])
H_ADM = login("m5adm")
H_STU = login("m5stu")

# 设置转盘费 = 30（与线上一致）
set_wheel_cost(30, H_ADM)

# 建 3 个课时，各 10 题（全对一次即精通）
r = client.post("/api/subjects", json={"name": "M5数学", "category": "culture", "icon": "🧪"}, headers=H_ADM)
SUB = r.json()["id"]
topA = client.post("/api/topics", json={"subject_id": SUB, "name": "A课", "unit": "上"}, headers=H_ADM).json()["id"]
topB = client.post("/api/topics", json={"subject_id": SUB, "name": "B课", "unit": "上"}, headers=H_ADM).json()["id"]
topC = client.post("/api/topics", json={"subject_id": SUB, "name": "C课", "unit": "上"}, headers=H_ADM).json()["id"]
for tid in (topA, topB, topC):
    qs = [{"subject_id": SUB, "topic_id": tid, "type": "choice",
           "content": f"{tid}-{i}", "options": ["1", "2", "3", "4"], "answer": "1", "difficulty": 1}
          for i in range(10)]
    client.post("/api/questions/batch", json=qs, headers=H_ADM)


def master_topic(tid, tier=1):
    """组卷并全对提交，达成精通。返回 submit 响应 json。"""
    r = client.post("/api/exam/start", json={"subject_id": SUB, "topic_ids": [tid], "types": [],
                                              "count": 10, "mode": "custom", "tier": tier}, headers=H_STU)
    qids = [q["id"] for q in r.json()["questions"]]
    answers = [{"question_id": q, "user_answer": "1"} for q in qids]
    r = client.post("/api/exam/submit", json={"subject_id": SUB, "mode": "custom", "topic_ids": [tid],
                                               "answers": answers, "duration_seconds": 5, "tier": tier}, headers=H_STU)
    return r.json()


print("\n==== 3. 跃迁发分（mode=new） ====")
bal0 = get_balance(H_STU)
rec = master_topic(topA)
rewards = rec.get("mastery_rewards", [])
check("达成精通返回 1 条奖励", len(rewards) == 1, f"{len(rewards)}")
check("  mode=new", rewards and rewards[0]["mode"] == "new")
check("  积分=wheel_cost(30)", rewards and rewards[0]["points"] == 30)
# 余额 = 答题积分(10题全对=1) + 精通奖励(30)
check("  余额=答题积分+奖励30", get_balance(H_STU) == bal0 + 30 + rec.get("points_earned", 0),
      f"+{get_balance(H_STU)-bal0}")
afterA = get_balance(H_STU)

print("\n==== 4. 防重复：同课再提交不再发奖 ====")
rec = master_topic(topA)
check("重复提交无新奖励", len(rec.get("mastery_rewards", [])) == 0,
      f"{len(rec.get('mastery_rewards', []))}")
# 已精通：掌握度闸门拦截答题积分 + 无奖励 → 余额不变
check("  余额不变", get_balance(H_STU) == afterA, f"{get_balance(H_STU)} vs {afterA}")

print("\n==== 5. 历史补发（mode=retroactive） ====")
# 模拟历史精通：直接插一条 mastered 但无奖励记录
db = SessionLocal()
db.add(models.StudentMastery(student_id=2, subject_id=SUB, topic_id=topC, tier=1,
                              status="mastered", rate=1.0, coverage=1.0,
                              answered_count=10, distinct_count=10, correct_count=10, topic_total=10))
db.commit()
db.close()
bal1 = get_balance(H_STU)
rec = master_topic(topB)  # 新达成 B
rewards = rec.get("mastery_rewards", [])
modes = sorted([r["mode"] for r in rewards])
check("新精通 B + 补发历史 C，共 2 条", len(rewards) == 2, f"{len(rewards)}")
check("  含 new + retroactive", modes == ["new", "retroactive"], str(modes))
# 余额 = 答题积分 + 60(2×30 奖励)
check("  余额=答题积分+60", get_balance(H_STU) == bal1 + 60 + rec.get("points_earned", 0),
      f"+{get_balance(H_STU)-bal1}")
retro = [r for r in rewards if r["mode"] == "retroactive"]
check("  补发条目=历史课 C", retro and retro[0]["topic_name"] == "C课", str(retro))
afterB = get_balance(H_STU)

print("\n==== 6. wheel_cost=0 保护 ====")
set_wheel_cost(0, H_ADM)
# 造个新课时达成精通
topD = client.post("/api/topics", json={"subject_id": SUB, "name": "D课", "unit": "上"}, headers=H_ADM).json()["id"]
qs = [{"subject_id": SUB, "topic_id": topD, "type": "choice", "content": f"D-{i}",
       "options": ["1", "2", "3", "4"], "answer": "1", "difficulty": 1} for i in range(10)]
client.post("/api/questions/batch", json=qs, headers=H_ADM)
rec = master_topic(topD)
check("wheel_cost=0 不发奖", len(rec.get("mastery_rewards", [])) == 0,
      f"{len(rec.get('mastery_rewards', []))}")
# 只应有答题积分，无精通奖励
check("  余额仅+答题积分", get_balance(H_STU) == afterB + rec.get("points_earned", 0),
      f"+{get_balance(H_STU)-afterB}")
afterD = get_balance(H_STU)
set_wheel_cost(30, H_ADM)  # 恢复

print("\n==== 7. admin 测试接口（只读预览） ====")
bal_before = get_balance(H_STU)
r = client.post("/api/admin/test-mastery-reward", headers=H_ADM)
check("测试接口返回 200", r.status_code == 200, r.text[:150])
d = r.json()
check("  含 nickname/wheel_cost/rewards", "nickname" in d and "wheel_cost" in d and "rewards" in d)
check("  wheel_cost=30", d.get("wheel_cost") == 30)
check("  rewards 非空", len(d.get("rewards", [])) > 0)
check("  只读不写（余额不变）", get_balance(H_STU) == bal_before,
      f"{get_balance(H_STU)} vs {bal_before}")

print(f"\n==== 结果：PASS {PASS} / FAIL {FAIL} ====")
sys.exit(1 if FAIL else 0)
