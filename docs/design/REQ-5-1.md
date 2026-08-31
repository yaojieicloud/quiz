# REQ-5-1：科目完成状态标识 + 首页历史科目隔离 — 设计方案

## 1. 方案概述

在 subjects 表增加 status 字段，区分活跃/已完成科目。学生首页按 status 分区展示，管理员可在后台将科目标记为"已完成"。

## 2. 数据库设计

### 2.1 迁移脚本（migrations/0007_subject_status.py）

幂等 Python 迁移（启动时自动执行），检测 status 列已存在则跳过：
- 旧数据默认 active（已有科目保持活跃，不自动完成）
- 新建科目默认值由应用层控制（默认 'active'）

### 2.2 模型变更

**models.py — Subject 类新增字段：**
```python
status = Column(String(20), default="active", nullable=False)  # active / completed
```

### 2.3 Schema 变更

**schemas.py：**
```python
class SubjectOut(BaseModel):
    ...
    status: str = "active"

class SubjectUpdate(BaseModel):
    ...
    status: Optional[str] = Field(None, pattern="^(active|completed)$")
```

## 3. API 设计

### 3.1 新增路由

**routers/subjects.py：**
```python
@router.patch("/subjects/{subject_id}/status")
def update_subject_status(
    subject_id: int,
    status: str,  # query param: "active" | "completed"
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    s = db.query(Subject).filter(Subject.id == subject_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="科目不存在")
    if status not in ("active", "completed"):
        raise HTTPException(status_code=400, detail="status 必须是 active 或 completed")
    s.status = status
    db.commit()
    return {"id": subject_id, "status": status}
```

**现有路由无需修改**：list_subjects、create_subject 等返回 SubjectOut，已含 status 字段。

## 4. 前端设计

### 4.1 学生首页（home.html）

**渲染逻辑：**
- 分离 active 和 completed 两组科目分别渲染
- 已完成科目上方插入分隔栏「📋 历史科目（共 N 个）」
- 已完成卡片加 .completed class 灰显处理

**已完成卡片样式（CSS）：**
```css
.subject-card.completed {
  opacity: 0.58; border-color: #e9ecef; background: #f8f9fc; filter: grayscale(0.2);
}
.subject-card.completed h3 { color: #9c8bb5; }
.subject-card.completed .count { color: #adb5bd; }
.section-divider {
  grid-column: 1 / -1; text-align: center; padding: 20px 0 8px;
  font-size: 14px; color: #9c8bb5; font-weight: bold;
}
```

### 4.2 管理后台（admin.html）

**科目列表操作区按钮（需 admin 角色）：**
- completed 科目显示 🔄 恢复按钮
- active 科目显示 ✅ 完成按钮

**完成操作函数（带二次确认弹层）：**
```javascript
function markCompleted(id) {
  const s = subjects.find(x => x.id === id);
  showConfirm('标记完成', '确定将「' + s.name + '」标记为已完成？', async () => {
    await API.patch('/api/subjects/' + id + '/status?status=completed');
    toast('已标记为完成', 'success');
    loadSubjects();
  });
}
function markActive(id) {
  API.patch('/api/subjects/' + id + '/status?status=active').then(() => {
    toast('已恢复为活跃', 'success');
    loadSubjects();
  });
}
```

**common.js 新增 API.patch 方法**，供前端调用。

## 5. 不涉及变更的范围

以下功能**不受 status 字段影响**：
- /api/subjects 返回所有科目（active + completed），不做过滤
- 组卷 API 仍可对 completed 科目出题
- 精通度计算不检查 subject status
- 题目 CRUD 不检查 subject status
- 迁移不清理已完成科目的题目数据

## 6. 文件清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| migrations/0007_subject_status.py | 新增 | 幂等迁移脚本 |
| src/models.py | 修改 | Subject 类加 status 列 |
| src/schemas.py | 修改 | SubjectOut/SubjectUpdate 加 status |
| src/routers/subjects.py | 修改 | 新增 PATCH 路由 |
| src/static/home.html | 修改 | 分区渲染 + 样式 |
| src/static/admin.html | 修改 | 列表加完成/恢复按钮 |
| src/static/js/common.js | 修改 | 新增 API.patch 方法 |
| docs/requirements/REQ-5.md | 新增 | 需求文档 |
| docs/design/REQ-5-1.md | 新增 | 本文档 |

## 7. 风险与回滚

- **风险**：迁移 ALTER TABLE 在大表上可能锁表（subjects 表题量少，风险极低）
- **回滚**：前端删除 status 字段引用降级，旧数据 status='active' 不影响
- **幂等**：迁移检测 status 列已存在则跳过，支持重复执行

---

> 设计编号：REQ-5-1
> 对应需求：REQ-5
> 确认时间：2026-08-31
> 状态：✅ 已确认
> 文档修正：2026-09-01（API 改为 query param + 迁移文件命名对齐实际代码）
