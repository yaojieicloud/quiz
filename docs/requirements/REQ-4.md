# REQ-4 新建4年级科目支持

## 1. 原始描述
> 我要新建 4 年级的科目（数学/语文/英语），但目前「数学」已经存在，数据库唯一约束报错。

## 2. 需求目标
- 支持同名校科目跨年级并存（数学/三年级 + 数学/四年级合法共存）
- 新建 4 年级科目时不触发 IntegrityError
- 修复后端校验逻辑与数据库约束对齐

## 3. 功能范围

### 3.1 要做（In Scope）
1. **数据模型层**：`models.py` 去掉 `Subject.name` 单列 `unique=True`，改为 `UniqueConstraint("name", "grade")` 复合唯一
2. **数据迁移层**：`migrations/0006_subject_grade_unique.py` — 幂等迁移：重建 subjects 表、加复合唯一约束、把已有 Python 类科目的 grade 置占位串「通用」
3. **后端校验层**：`routers/subjects.py` 的 `create_subject` 改为检查 `(name, grade)` 组合不存在后再创建
4. **schemas 补注释**：`schemas.py` 的 `grade` 字段补说明（文化课填年级字符串，编程类填「通用」）
5. **设计文档同步**：`docs/design/科目与知识点体系.md` 已在 working tree 更新字段说明
6. **本地验证**：迁移幂等验证 + POST `/subjects` 新建"数学/四年级"端到端通
7. **ECS 验证**：ECS 拉库 + 本地跑迁移 + ECS 重启 + POST 新建验证（生产库拉回本地测）

### 3.2 不做（Out of Scope）
- 新建 4 年级的题库/课程/题目（题库导入工作，独立任务）
- 语文/英语 sort_order 全 0 遗留问题（BUG-4 已关闭）
- 编程类 grade=None/「通用」导致的 sort_order 排序异常（需单独评估）

## 4. 非功能约束
- 性能要求：无特殊要求，轻量迁移
- 安全要求：写运维操作前先备份数据库（`POST /api/admin/backup-db`）
- 兼容性要求：迁移幂等，重复执行不报错；旧数据库（含 grade=None）迁移后数据不丢失

## 5. 影响范围
- **涉及模块**：`models.py`、`schemas.py`、`routers/subjects.py`、`migrations/`
- **涉及现有文件/接口**：
  - `POST /subjects`（校验逻辑变更，同名同年级 400，同名跨年级 200）
  - `GET /subjects`（无影响）
  - `docs/design/科目与知识点体系.md`（字段说明已更新）
- **上下游影响**：
  - 管理端创建科目 UI 无需改（前端传 grade 字段，后端接住即可）
  - 已有科目"数学/三年级"不受影响

## 6. 风险与约束
- **风险1**：SQLite `ALTER TABLE` 限制导致迁移用 RENAME TABLE 重建表；依赖 SQLite FK 按父表名解析特性（子表外键引用 `subjects.id` 不变），实测 6 张子表无影响
- **风险2**：0006 迁移如在已有 `(name, grade)` 复合约束的库上重复跑，幂等检查会跳过；但 ECS 当前库的 grade 全为 None，迁移必须跑才能解锁新建 4 年级
- **约束**：迁移执行时机：必须在 ECS 拉库→本地验证→确认无误后再在 ECS 执行，防止生产库数据损坏

## 7. 验收标准
- [ ] `models.py` 有 `UniqueConstraint("name", "grade")`，无单列 `name unique=True`
- [ ] `migrations/0006_subject_grade_unique.py` 幂等检查存在，执行一次后再次执行不报错
- [ ] `routers/subjects.py` 新建"数学/三年级"→ 400 同名同年级；新建"数学/四年级"→ 200 成功
- [ ] 本地开发环境：POST `/subjects` 新建"数学/四年级"成功，数据库 grade 字段为"四年级"
- [ ] ECS 生产库：迁移执行后，Python 类科目 grade 已置"通用"，不影响已有数据
- [ ] 设计文档 `科目与知识点体系.md` 已更新（已在 working tree）

## 8. 状态
- 梳理状态：✅已确认（2026-08-31）
- 设计状态：0/0
- 任务状态：0/0
