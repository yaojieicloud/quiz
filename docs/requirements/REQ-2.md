# REQ-2: 答题后精通度变化展示

> 状态: ✅已完成 | 优先级: P1 | 提出日期: 2026-08-28

## 需求背景

学员提交答卷后，结果页只显示分数、对错、积分，没有显示本次答题对精通度的影响。学员无法直观感受到自己的进步或不足。

用户原话："学员答题后我记得是有弹窗，还是有界面，这个界面上显示精通度提升了几点，如果没提升，则说明原因，注意，用户是小朋友，要让他们看得懂"

## 需求范围

在答题结果页（分数+积分下方）新增"精通度变化"区域，逐课展示本次答题带来的精通度变化：

| 状态 | 展示内容 |
|------|---------|
| 精通度提升 | "精通度 +X%！继续加油！" |
| 新达到精通 | "🎉 恭喜！已精通！" |
| 未提升 | 简化说明原因 |

### 未提升原因（简化版）

| 瓶颈项 | 文案 |
|--------|------|
| 正确率 < 90% | "正确率还不够，争取答对更多！" |
| 覆盖度 < 80% | "做过的题型还不够多样，试试更多不同的题！" |
| 做题数不够 | "做得还太少，再多练几次！" |

## 确认记录

- 展示位置：固定在结果页（积分横幅下方），不是弹窗 ✅
- 涉及课程范围：只展示本次答题涉及的课程 ✅
- 后端接口：delta 数据跟在 submit 响应的 `mastery_deltas` 字段里 ✅

## 设计文档

`docs/design/答题后精通度变化展示.md`

## 任务拆解

| 任务编号 | 任务标题 | 状态 |
|----------|----------|------|
| REQ-2-1-1 | `core/mastery.py` 新增 `calc_mastery_pct` + `diagnose_bottleneck` | ✅已完成 |
| REQ-2-1-2 | `schemas.py` 新增 `MasteryDeltaOut` + `ExamRecordOut` 新增字段 | ✅已完成 |
| REQ-2-1-3 | `exam.py` `submit_exam` 快照旧精通度 + 计算 delta + 传入响应 | ✅已完成 |
| REQ-2-1-4 | `quiz.html` 前端渲染精通度变化区域（含样式+JS） | ✅已完成 |

## 改动文件

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `src/core/mastery.py` | 新增 | `calc_mastery_pct()` + `diagnose_bottleneck()` |
| `src/schemas.py` | 新增 | `MasteryDeltaOut` schema + `ExamRecordOut.mastery_deltas` |
| `src/routers/exam.py` | 修改 | submit_exam 快照 + delta 计算 + _record_to_out 传参 |
| `src/static/quiz.html` | 修改 | CSS样式 + `renderMasteryDelta()` + showResult 调用 |

## ECS 功能验证

- 后端 `mastery_deltas` 字段正确返回 ✅
- 瓶颈诊断 `bottleneck=rate` 正确 ✅
- 前端样式和渲染待用户在浏览器中验证
