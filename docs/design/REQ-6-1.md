# REQ-6 科目下课程维护功能 — 方案设计

> 对应需求：REQ-6
> 设计者：AI + 阿垚确认（2026-09-01）
> 状态：✅ 设计确认中

---

## 一、设计决策（阿垚已确认）

| # | 决策 | 结论 |
|---|------|------|
| 1 | 软删除逻辑 | 与题目废弃机制相同：新增 `Topic.deprecated = 1` 字段 → 不可见、不参与组卷 |
| 2 | 软删条件 | 有课程+有习题+习题被学员做过 → 软删；否则 → 物理删 |
| 3 | 历史数据 | mastery 等历史数据**保留**，不清理 |
| 4 | 拖拽范围 | 单科目内拖动，不跨科目 |
| 5 | 拖拽算法 | `new_sort = (prev.sort + next.sort) / 2`，浮点存储，无需批量更新 |
| 6 | 软删效果 | 直接不可见（不展示、不参与组卷） |
| 7 | 影响预估 | 删除前展示"将软删 X 课程 X 题" |

> ⚠️ **关键修正（2026-09-01）**：`Topic` 模型**原本没有 deprecated 字段**（与 `Question.deprecated` 不同），需通过迁移新增。详见 §2.3。

---

## 二、数据库设计

### 2.1 现有字段（已支持）

```sql
-- topics 表（已有）
id          INTEGER PRIMARY KEY
subject_id  INTEGER
name        TEXT
unit        TEXT
sort_order  INTEGER
-- ⚠️ deprecated 字段：原本不存在，需通过迁移新增（§2.3）
```

### 2.2 改动点

**`topics.sort_order` 类型变更**：
- `INTEGER` → `REAL`（SQLite 支持 REAL）
- 现有 INTEGER 值（如 `1, 2, 3`）自动转为 `1.0, 2.0, 3.0`，**无需数据迁移**
- 阿垚确认用 `(A+C)/2` 浮点插入算法，无需批量更新

### 2.3 新增 `topics.deprecated` 字段（必须，迁移）

**原因**：`Topic` 模型原本**没有** `deprecated` 字段（与 `Question.deprecated` 不同）；设计需要软删除，必须先补字段。

**迁移文件**：`src/migrations/0007_topic_deprecated.py`

```python
"""为 topics 表新增 deprecated 字段，软删除课程用。"""
from sqlalchemy import text
from database import engine

MIGRATION_ID = "0007_topic_deprecated"

def up(engine):
    with engine.begin() as conn:
        # 幂等检查：列已存在则跳过
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(topics)")).fetchall()]
        if "deprecated" in cols:
            return
        conn.execute(text("ALTER TABLE topics ADD COLUMN deprecated INTEGER NOT NULL DEFAULT 0"))
```

**ORM 同步**：修改 `src/models.py` 的 `Topic` 类：

```python
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(100), nullable=True)
    sort_order = Column(Float, default=0)  # 同步改为 Float
    deprecated = Column(Integer, default=0, nullable=False)  # 新增
    # ...
```

**学员端过滤**：现有 `routers/subjects.py` 列表接口（第 22-44 行）查询 `Question.deprecated` 已过滤，软删课程下所有题目后该课程**自动不出现在题数统计**。课程列表本身**不**需改（学员端走 `Topic.deprecated=0` 过滤是**后续清理**；本期学员端走"按题过滤"已经达成"课程不可见"的效果）。

**新增接口返回值**：
```python
class DeleteTopicResult(BaseModel):
    mode: Literal["soft", "hard"]
    topic_count: int = 0          # 软删/硬删的课程数
    question_count: int = 0       # 涉及的题目数
    message: str                  # 展示给管理员的提示
```

---

## 三、接口设计

### 3.1 删除课程（改造）

```
DELETE /api/topics/{id}
```

**后端逻辑**：
```
1. 查询课程下所有题目 → count Q
2. 查询 Q 中被学员答题记录引用的题目数量 → count Q_done
   ⚠️ 必须查 answer_records.question_id（单题作答明细表），
      不要查 exam_records（聚合表，无 question_id 列），
      否则会查不到数据，错误地全部走"硬删"分支 → 数据丢失！
3. if Q > 0 and Q_done > 0:
       → 软删除：topics UPDATE deprecated=1
       → 题目 UPDATE deprecated=1（复用餐题软删逻辑）
       → return {mode:"soft", topic_count:1, question_count:Q, message:"..."}
   else:
       → 物理删除：级联删 questions + topics
       → return {mode:"hard", topic_count:1, question_count:Q, message:"..."}
```

**正确查询写法（关键！）**：

```python
# ✅ 正确：查 answer_records（单题作答明细表，存 question_id）
q_ids = [r.id for r in db.query(Question.id).filter(Question.topic_id == topic_id).all()]
done_count = db.query(AnswerRecord.id).filter(
    AnswerRecord.question_id.in_(q_ids)
).distinct().count() if q_ids else 0

# ❌ 错误：exam_records 是聚合表，无 question_id 列，查不到会返回 0，
#    导致所有课程都被当"无做题"硬删 → 历史数据丢失！
```

**为什么必须用 answer_records**：
- `exam_records`：一次完整答题（user_id, subject_id, total, correct, score, ...）—— 无 question_id
- `answer_records`：单题作答明细（exam_record_id, question_id, user_answer, is_correct, ...）—— 存了 question_id
- "某题被学员做过"只能从 `answer_records` 查

**前端接收** `DeleteTopicResult`，根据 `mode` 展示不同确认提示：
- `hard`：直接确认弹窗（"将删除课程和 X 道题目"）
- `soft`：强调提示弹窗（"课程/题目已有学员做题，删除后将不可见，保留历史记录"）

### 3.2 拖动排序（新增）

```
PUT /api/topics/reorder
Body: { "id": 123, "prev_id": 456, "next_id": 789 }
```

**后端逻辑**：
```
prev = GET /topics/{prev_id}.sort_order  (或 null = 最小)
next = GET /topics/{next_id}.sort_order  (或 null = 最大)
new_sort = (prev + next) / 2   -- 若 prev=null → new_sort = next/2
                                 -- 若 next=null → new_sort = prev + 1024
UPDATE topics SET sort_order = new_sort WHERE id = {id}
```

> `prev_id`/`next_id` 为 `null` 时表示拖到首位或末位。

### 3.3 新建课程（已有，确认无需改动）

```
POST /api/topics
Body: { "subject_id": N, "name": "...", "unit": "..." }
```

- `sort_order` 默认 `max_sort + 1024`（保证在末尾）

### 3.4 编辑课程（已有，确认无需改动）

```
PUT /api/topics/{id}
Body: { "name": "...", "unit": "..." }
```

---

## 四、前端改造

### 4.1 布局改动（科目行）

**现状**：
```
[📂 科目名]  [✏️编辑] [🗑️删除] [✅完成/🔵激活]          [📂展开按钮]
```

**改造后**：
```
[📂 科目名]  [✏️编辑] [🗑️删除] [✅完成/🔵激活] [+ 新建课程]  [📂展开]
```

- "+ 新建课程"按钮放在**科目行右侧**，展开按钮左边
- 展开区顶部不再有新建按钮（避免两个新建入口）

### 4.2 展开区布局改动（课程行）

**现状**：
```
[课程名] [题数]              [✏️编辑] [🗑️删除]
```

**改造后**：
```
[≡] [课程名] [题数]          [✏️编辑] [🗑️删除]
  ↑ 拖拽手柄
```

- 每个课程行左侧加 `≡` 拖拽手柄
- 使用 SortableJS 实现拖动，拖动时行高亮
- 拖动后立即调用 `PUT /api/topics/reorder`，完成后刷新列表

### 4.3 删除确认弹窗

**hard 模式**：
```
确认删除
删除「万以上数的认识」？
该课程下有 5 道题目，删除后不可恢复。
[取消] [确认删除]
```

**soft 模式**（强调）：
```
⚠️ 该课程有学员做题记录
「万以上数的认识」下有 5 道题目，其中 3 道已被学员做过。
删除后：课程和题目将不可见，历史学习记录（精通度等）保留。
[取消] [确认删除]
```

### 4.4 SortableJS CDN

```html
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js"></script>
```

- 放在 `admin.html` `<head>` 中引入（已有 adminlte 等 CDN，先确认不冲突）
- 使用 `new Sortable(el, { animation: 150, handle: '.drag-handle', ... })`

---

## 五、影响分析

| 影响范围 | 说明 |
|---------|------|
| `topics.sort_order` 类型 | INTEGER → REAL，现有数据自动转换，无需迁移 |
| 删除逻辑 | 新增"软/硬分流"判断 + 题目软删逻辑复用 |
| 拖拽接口 | 新增 `PUT /api/topics/reorder` |
| 前端 admin.html | 布局调整 + SortableJS 引入 |
| 学员端 | 自动跟随 `deprecated` 过滤，无需改动 |

### 软删除对学员端的影响（已验证）

现有代码已按 `deprecated=1` 过滤：
- `home.html`：只显示 `deprecated=0` 的课程
- `mastery.html`：不显示软删课程的 mastery
- 组卷：已按 `deprecated=1` 排除

**无需改动学员端代码**。

---

## 六、风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| SortableJS CDN 加载失败（106.14.99.100 网络限制） | 提前测试 CDN 可达性；如失败改用本地 copy 或 HTML5 原生 DnD |
| 拖拽时快速操作导致并发 sort_order 冲突 | `sort_order` 用 REAL 浮点，冲突概率极低；如极端情况两课程 sort 相等，取平均值 |
| 软删后学员端仍能通过 URL 访问 | API 层已统一过滤 `WHERE deprecated=0` |
| 题目软删时未级联清理外键引用 | 复用餐题软删逻辑（`questions.deprecated=1`），已有验证 |

---

## 七、验收标准

- [ ] 科目行右侧出现「+ 新建课程」按钮
- [ ] 展开区每行有拖拽手柄 `≡` 和编辑/删除按钮
- [ ] 拖动课程行后 sort_order 正确更新（相邻课程之间）
- [ ] 无题目/无做题 → hard 模式，直接物理删除
- [ ] 有题目+有做题 → soft 模式，deprecated=1，前端不再显示
- [ ] 删除弹窗显示影响预估（课程数、题目数）
- [ ] 学员端不显示软删课程/题目
