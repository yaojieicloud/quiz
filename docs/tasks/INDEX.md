# 任务索引

> 编号规则：REQ-{N}-{M}-{K}；任务文档存放 `docs/tasks/REQ-{N}-{M}-{K}.md`。
> 任务状态值：⏳待开发 / 🔵进行中 / ✅已完成 / ⏸️暂停

| 任务编号 | 任务标题 | 所属需求 | 优先级 | 状态 | 依赖 |
|----------|----------|----------|--------|------|------|
| REQ-1-1-1 | 新增横向柱 CSS 样式（common.css） | REQ-1 | P0 | ✅已完成 | - |
| REQ-1-1-2 | 改写 analytics-shared.js 两个渲染函数 | REQ-1 | P0 | ✅已完成 | REQ-1-1-1 |
| REQ-1-1-3 | 三页面容器适配 + 文档同步 + 联调验证 | REQ-1 | P1 | ✅已完成 | REQ-1-1-2 |
| REQ-2-1-1 | mastery.py 新增 calc_mastery_pct + diagnose_bottleneck | REQ-2 | P0 | ✅已完成 | - |
| REQ-2-1-2 | schemas.py 新增 MasteryDeltaOut + ExamRecordOut 字段 | REQ-2 | P0 | ✅已完成 | - |
| REQ-2-1-3 | exam.py 快照旧精通度 + 计算 delta + 传入响应 | REQ-2 | P0 | ✅已完成 | REQ-2-1-1, REQ-2-1-2 |
| REQ-2-1-4 | quiz.html 前端渲染精通度变化区域（CSS + JS） | REQ-2 | P0 | ✅已完成 | REQ-2-1-3 |
| REQ-3-1-1 | 课程递进解锁全栈实现（前端锁定+默认选中+后端校验+题数默认值） | REQ-3 | P0 | ✅已完成 | - |

进度跟踪（多任务并行）见 `docs/PROGRESS.md`；恢复中断任务用 `/继续`。
