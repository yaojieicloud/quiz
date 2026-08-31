# REQ-5：科目完成状态标识 + 首页历史科目隔离

## 需求描述

当前首页展示的所有科目（包括三年级、四年级、编程类等）都平铺显示。当年份更替时，过去的科目仍占据主视觉位置，给用户造成"年级错乱"的感觉。

## 目标

为每个科目增加 `status` 状态字段：
- `active`（活跃）：首页显示于"当前年级"区域，卡片常亮
- `completed`（已完成）：首页显示于"历史科目"区域，卡片置灰（opacity:0.6 + 轮廓灰边），点击后仍可选

## 目标范围

### 功能要点
1. **Sc-1**：数据库 `subjects` 表新增 `status` 列，默认值 `'active'`
2. **Sc-2**：管理后台为每个科目添加"已完成"按钮
3. **Sc-3**：点击"完成"弹二次确认，确认后调用 `PATCH /api/admin/subjects/{id}/status`
4. **Sc-4**：学生首页按 `status` 分区渲染：active 在上，completed 在下
5. **Sc-5**：完成状态不影响做题、题目出卷、精通度等后端逻辑

### 验收标准
- ✅ 新增科目默认显示在 active 区
- ✅ 管理员点击"完成"→二次确认→点击确定→状态变为 completed
- ✅ active 区科目卡片默认亮色
- ✅ completed 区科目卡片置灰（边框#e9ecef，文字#9c8bb5，背景#f8f9fc）
- ✅ 点击 completed 科目卡片→可正常进入组卷流程
- ✅ 完成后仍可在管理后台看到该科目、题目、章节

### 非目标（不做）
- ❌ 禁止"删除科目"功能（已由后台删除接口支持）
- ❌ 禁止"恢复"功能（如需恢复，由后台直接改回 active）
- ❌ 完成科目自动隐藏题目（题目仍在数据库，组卷时可被选）

## 影响范围

### 前端
- `home.html`：科目渲染逻辑从 `subjects.map(card)` → 按 status 分组渲染
- `admin.html`：科目列表每行添加 "已完成" 按钮，弹二次确认

### 后端
- `models.py`：Subject 模型加 `status: str` 列
- `schemas.py`：SubjectOut/SubjectUpdate 加 `status` 字段
- `routers/subjects.py`：新增 `PATCH /subjects/{id}/status` 路由

### 数据库
- 迁移 0007：给 subjects 表加 status 列（默认 active）
- 旧数据：已有科目默认设为 active

## 风险评估

| 风险 | 概率 | 影响 | 规避 |
|------|------|------|------|
| 迁移字段冲突 | 低 | 破坏现有功能 | 迁移默认 active，保留旧数据 |
| 前端渲染卡顿 | 低 | 用户体验差 | 用 CSS 隐藏而非删除 DOM |
| 边界情况：无 active 科目 | 低 | 页面空白 | 仍显示头部区域标题"当前科目" |

## 验收指令

```bash
# 1. 本地数据库：运行迁移 0007，验证 subjects 表多了 status 列
# 2. 后端 API：POST /api/subjects/{id}/status {"status":"completed"}
# 3. 前端 home.html：渲染 active+completed 区域，验证卡片样式
# 4. 管理后台 admin.html：点击完成按钮，验证二次弹层
# 5. 健康检查：curl home.html → 200；登录后台 → 科目列表正常
```

## 状态

- 梳理完成：✅
- 设计完成：✅（见 docs/design/REQ-5-1.md）
- 开发完成：✅（2026-08-31）
  - ✅ 迁移 0007：subjects 加 status 列
  - ✅ models.py：Subject 加 status 列
  - ✅ schemas.py：SubjectOut/SubjectUpdate 加字段
  - ✅ routers/subjects.py：PATCH /subjects/{id}/status 路由
  - ✅ home.html：按 status 分区渲染
  - ✅ admin.html：完成/恢复按钮 + 二次确认
  - ✅ common.js：加 API.patch 方法
  - ✅ 验收：ECS 已部署验证通过（2026-08-31）

> 文档编号：REQ-5  
> 创建时间：2026-08-31  
> 作者：阿垣