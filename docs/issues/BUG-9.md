# BUG-9 阅读理解 4 小题过去 10S 计时未到 + admin 调试免计时

| 项 | 值 |
|---|---|
| 状态 | 🟢已关闭（2026-09-04 ECS 部署完成） |
| 类型 | 体验问题 |
| 录入时间 | 2026-09-04 |
| 关联需求 | — |

## 1. 问题描述

阿垚在 ECS 环境做阅读理解题，4 小题答完，**10s 计时仍未到**。此外 admin 调试做题时受 10s 限制太慢。

## 2. 根因

`src/static/quiz.html` 计时器设计缺陷：

1. `renderQuestion()` 第 442-443 行 **每次调用都** `resetQuestionTimer()`
2. 阅读理解是**一个 curIdx 对应 4 个子题**（reading_items 数组）
3. 用户每选一个子题 → `pickReading()` → `renderQuestion()` → 计时器被重置
4. 4 个子题来回切 → 计时器永远从 0 重新开始 → 永远计不到 10s

## 3. 修复（2026-09-04）

### 修复 1：仅在 curIdx 真正切换时重置计时
- 新增 `_prevCurIdx` 变量追踪上次渲染的 curIdx
- `renderQuestion()` 内增加判断：`curIdx !== _prevCurIdx` 才 reset
- 阅读理解子题切选 → curIdx 不变 → 不重置 ✅
- goNext/goPrev/jumpTo → curIdx 变化 → 仍正常重置 ✅

### 修复 2：admin 账号跳过 10s 限制
- 新增 `isAdminUser()` 判断 `user.role === 'admin'`
- 新增 `checkAnswerTime()` 统一入口：admin 直接返回 true
- goNext / jumpTo / doSubmit 三处时间检查统一改用 `checkAnswerTime()`

## 4. 改动文件

- `src/static/quiz.html`（仅此一文件）
  - 第 390-405 行：新增 `isAdminUser()` + `checkAnswerTime()` 工具
  - 第 437-449 行：新增 `_prevCurIdx` + 条件 reset
  - 第 660-672 行：`pickReading` 注释说明（实际依赖 renderQuestion 内部修复）
  - goNext / jumpTo / doSubmit 三处改用 `checkAnswerTime()`

## 5. 验证

- 阅读理解 4 子题连续选择 → 计时器不重置，10s 后可正常切下一题
- admin 账号：点击下一题 / 提交都不再触发"答题少于 10s"弹窗
- 普通学生：行为不变（同一题内重渲染不重置；换题仍正常重置）

## 6. 部署

- commit 单独提交
- 镜像 push ECS + docker compose up -d --force-recreate
- ECS 数据未动（仅改前端 JS）
