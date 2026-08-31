# REQ-4-1 新建4年级科目支持

## 1. 所属需求
- 需求编号：REQ-4
- 需求标题：新建4年级科目支持
- 需求文档：docs/requirements/REQ-4.md

## 2. 设计目标

在「科目 name 单列唯一 → (name, grade) 复合唯一」改造下，保证新建/查询接口行为正确、迁移幂等、本地+ECS 均可验证。

## 3. 技术方案

### 3.1 数据模型

```
Subject (models.py:45-68)
  - name: String(50), nullable=False          # 去掉 unique=True
  - grade: String(20)                        # 年级/学段
  - __table_args__: UniqueConstraint("name", "grade", name="uq_subject_name_grade")
```

设计约定：
- **文化课**（数学/语文/英语）：`grade` 填年级字符串（"三年级"/"四年级"）
- **编程类**（Python基础理论/实操）：`grade` 填占位串「通用」（无年级语义，仅作复合唯一约束占位）
- 科目名**不带年级**，年级存 `grade` 字段

### 3.2 数据迁移

**文件**：`migrations/0006_subject_grade_unique.py`

- **幂等检查**：查询 `PRAGMA index_list(subjects)`，已存在 `(name, grade)` 复合唯一索引则直接跳过
- **实现**：RENAME TABLE 重建（SQLite `ALTER TABLE` 不支持 DROP CONSTRAINT）；新表仍叫 `subjects`，子表 6 张（topics/questions/exam_records/student_mastery/subject_points/mastery_rewards）外键引用 `subjects.id` 不变，无需重建子表
- **副作用**：编程类 `grade = None → "通用"`

### 3.3 后端校验

**文件**：`routers/subjects.py` 第49行

```python
# 改前（单列唯一）
if db.query(Subject).filter(Subject.name == data.name).first():
    raise HTTPException(400, "科目已存在")

# 改后（复合唯一）
if db.query(Subject).filter(
    Subject.name == data.name,
    Subject.grade == data.grade
).first():
    raise HTTPException(400, "同名同年级科目已存在")
```

### 3.4 接口行为

**POST /subjects** 请求体含 `grade` 字段：

| 场景 | 请求 | 响应 |
|---|---|---|
| 同名同年级 | `{name:"数学", grade:"三年级"}` | 400 `{"detail":"同名同年级科目已存在"}` |
| 同名跨年级 | `{name:"数学", grade:"四年级"}` | 200 新建成功 |
| 全新科目 | `{name:"数学", grade:"四年级"}` | 200 新建成功 |

### 3.5 关键流程

```
管理端 POST /subjects（带 grade）
  → 检查 (name, grade) 是否已存在
    存在 → 400 "同名同年级科目已存在"
    不存在 → INSERT → 200
```

## 4. 涉及文件

| 文件 | 动作 | 状态 |
|---|---|---|
| `src/models.py` | 去掉 `name unique=True`，加 `UniqueConstraint("name","grade")` | ✅已完成 |
| `src/migrations/0006_subject_grade_unique.py` | 幂等迁移文件 | ✅已完成 |
| `src/routers/subjects.py` | 校验改为 (name, grade) 组合 | ✅已完成 |
| `src/schemas.py` | grade 字段补注释 | ✅已完成 |
| `docs/design/科目与知识点体系.md` | 字段说明更新 | ✅已完成 |

## 5. 风险评估

| 风险 | 影响 | 应对 |
|---|---|---|
| 迁移重复跑 | 幂等检查跳过，无害 | ✅ 已有幂等逻辑 |
| ECS 生产库跑迁移 | 数据不可逆 | 先备份 `POST /api/admin/backup-db` + 本地验证后再上 |
| 编程类 grade=None 残留 | 复合唯一约束下 None 可共存多行 | 迁移把 None → "通用"，一次性解决 |

## 6. 关联任务

| 任务编号 | 任务标题 | 优先级 | 状态 |
|---|---|---|---|
| REQ-4-1-1 | subjects.py 校验改为 (name, grade) 组合 | REQ-4 | P0 | ✅已完成 | - |
| REQ-4-1-2 | schemas.py grade 字段补注释 | REQ-4 | P0 | ✅已完成 | - |
| REQ-4-1-3 | 本地迁移验证 + 端到端测试 | REQ-4 | P1 | ✅已完成 | REQ-4-1-1, REQ-4-1-2 |
| REQ-4-1-4 | ECS 拉库验证 + 设计文档归档 | REQ-4 | P1 | ⏳待开发 | REQ-4-1-3 |

## 7. 状态
- 设计状态：✅已确认（2026-08-31）
