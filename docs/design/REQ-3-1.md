# REQ-3-1: 课程递进解锁

> 需求: REQ-3 课程递进解锁与组题默认值调整
> 版本: v1.0 | 2026-08-28

## 1. 核心逻辑

### 1.1 解锁判定

```
课程 X 解锁条件：
  - X 已精通 → 永远解锁
  - X 未精通 → 同科目内 sort_order < X.sort_order 的所有课程必须全部精通
```

### 1.2 前端计算（不新增接口）

前端已有两个数据源可算出锁定状态：
- `topics`（含 `sort_order`）
- `masteryMap`（含每个 topic 的 `status`）

```javascript
function isTopicUnlocked(topic, allTopics, masteryMap, tier) {
  const st = masteryMap[`${topic.id}_${tier}`];
  if (st === 'mastered') return true;
  const prevTopics = allTopics.filter(
    t => t.sort_order < topic.sort_order && t.subject_id === topic.subject_id
  );
  return prevTopics.every(t => masteryMap[`${t.id}_${tier}`] === 'mastered');
}
```

### 1.3 后端校验（`/api/exam/start`）

```python
# 检查 topic_ids 中的课是否全部解锁
for tid in data.topic_ids:
    topic = db.query(Topic).filter(Topic.id == tid).first()
    prev_topics = db.query(Topic).filter(
        Topic.subject_id == topic.subject_id,
        Topic.sort_order < topic.sort_order
    ).all()
    for pt in prev_topics:
        m = db.query(StudentMastery).filter(
            StudentMastery.student_id == user.id,
            StudentMastery.topic_id == pt.id,
            StudentMastery.tier == data.tier
        ).first()
        if not m or m.status != 'mastered':
            raise HTTPException(400, f'请先精通「{pt.name}」再来挑战本课')
```

## 2. 前端改动点

| 位置 | 改动 |
|------|------|
| `home.html` → `openCoursePick()` | 渲染 chips 时：未解锁课程加 🔒 图标 + 灰色样式，onclick 改为弹提示 |
| `home.html` → `openConfig()` | 同上 |
| `home.html` → `pickCourse()` / `toggleChip()` | 点击锁定时拦截 + toast 提示 |
| `home.html` → `selectedCount` 初始化 | 10 → 20 |
| `home.html` → 默认选中逻辑 | 从"全选"改为"最靠前且未精通且已解锁的一课" |

## 3. 后端改动点

| 位置 | 改动 |
|------|------|
| `exam.py` → `/api/exam/start` | 新增递进解锁校验，未解锁返回 400 + 提示 |

## 4. UI 规范

**未解锁课程 chips 样式**：
```
灰色背景 + 🔒 图标 + 点击弹 toast："先把前面的课程学到精通，再来挑战这一课吧！"
```

**已解锁但未精通**：正常样式，可点击

**已精通**：显示"精通"角标，可点击

## 5. 默认选中逻辑

```
优先级：
1. 最靠前 + 未精通 + 已解锁 → 默认选中
2. 若无未精通课（全部精通）→ 选最后一课
3. 实操科目：单选模式；理论科目：单选模式（不再全选）
```

## 6. 边界场景

| 场景 | 处理 |
|------|------|
| 第一门课未精通 | 默认选中第一门课 |
| 全部课程已精通 | 默认选中最后一课 |
| 已精通课回跳 | 允许，不锁定 |
| 实操科目 | 同样适用递进解锁 |
| 后端校验绕过 | `/api/exam/start` 后端校验，返回错误 |
