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
| REQ-4-1-1 | subjects.py 校验改为 (name, grade) 组合 | REQ-4 | P0 | ✅已完成 | - |
| REQ-4-1-2 | schemas.py grade 字段补注释 | REQ-4 | P0 | ✅已完成 | - |
| REQ-4-1-3 | 本地迁移验证 + 端到端测试 | REQ-4 | P1 | ✅已完成 | REQ-4-1-1, REQ-4-1-2 |
| REQ-4-1-4 | ECS 拉库验证 + 设计文档归档 | REQ-4 | P1 | ✅已完成 | REQ-4-1-3 |
| REQ-6-1-1 | 后端：sort_order 改 REAL + reorder 接口 + 软/硬删除分流 | REQ-6 | P0 | ✅已完成（本地验证，待 ECS 部署） | - |
| REQ-6-1-2 | 前端：科目行新建按钮 + 课程行拖动 + 删除弹窗 | REQ-6 | P0 | ✅已完成（本地 docker 验证） | REQ-6-1-1 |
| REQ-7-1-1 | 后端：迁移 + 模型 + schema 加字段 | REQ-7 | P0 | ✅已完成 | - |
| REQ-7-1-2 | 管理端：admin.html 课程编辑弹窗加两 URL 字段 | REQ-7 | P0 | ✅已完成（已弃用，被 v2 方案取代） | REQ-7-1-1 |
| REQ-7-1-3 | 学员端：home.html 点击分流 + 文案改动 | REQ-7 | P0 | ✅已完成 | REQ-7-1-1 |
| REQ-7-1-4 | 学员端：新建 study.html 课程详情页 | REQ-7 | P0 | ✅已完成 | REQ-7-1-1, REQ-7-1-3 |
| REQ-7-1-5 | 本地 docker 验证 + 拉 ECS 数据到本地 + 回归测试 | REQ-7 | P1 | ✅已完成 | REQ-7-1-2, REQ-7-1-4 |
| BUG-7-1 | v2 智能渲染：Admin 录入只粘裸 URL 自动包 iframe | REQ-7 | P0 | ✅已完成 | - |

进度跟踪（多任务并行）见 `docs/PROGRESS.md`；恢复中断任务用 `/继续`。
