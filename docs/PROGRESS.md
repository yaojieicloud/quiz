# 项目进度

> it-workflow 多任务进度文件（2026-08-24 初始化）。
> 状态：🔵进行中 / ⏸️暂停 / ✅完成（移入本文件「已完成里程碑」段）。
> 配合 `/继续`：列出所有进行中 + 暂停任务，用户选一个继续，选中任务原样保留其余。

## 进行中

## 已完成里程碑
- 2026-08-24：it-workflow 项目初始化 ✅（README.md + docs 骨架 10 文件 + BUG-1 登记）
- 2026-08-25：BUG-1 设计文档 admin.py 残留引用修正 ✅（系统架构总览 / 管理后台与学情分析 / AI评分与学情报告）
- 2026-08-25：`src/requirements.txt` 依赖版本锁定 ✅（8 项，来源本地 .venv 实测，Python 3.13）
- 2026-08-25：**数据库唯一合法路径统一为 data/quiz.db** ✅（config.py / fetch_db.py / migrate 脚本 + 6 份文档同步；删除 src/quiz.db 并备份）
- 2026-08-25：**REQ-1 需求梳理 + 方案设计（REQ-1-1）+ 任务拆解（3 任务）落盘** ✅（需求/设计/任务三个 INDEX 已更新）
- 2026-08-25：**REQ-1 柱状图横向响应式改造完成** ✅（REQ-1-1-1 CSS、REQ-1-1-2 JS、REQ-1-1-3 页面+文档+联调；学员端 mastery/stats + 管理端 admin 4 图生效，其余 ECharts 图保留；终态样式＝标签行+粗柱两行结构、无滚动条、高度由内容撑开，已通过验收）
- 2026-08-26：**BUG-2 修复 — 组卷页面精通度显示为覆盖率** ✅（`home.html` / `mastery.js` / `analytics-shared.js` 改为显示综合精通度百分比，与 `core/mastery.py` 三门槛算法对齐；未精通状态百分比上限 99%，杜绝"显示 100% 但不发奖励"；顺带修复 `deploy_window.py` 公钥认证 + Dockerfile 路径 + docker compose v2）
- 2026-08-28：**REQ-2 答题后精通度变化展示 - 后端完成** ✅（REQ-2-1-1 mastery.py 新增工具函数、REQ-2-1-2 schemas.py 新增 MasteryDeltaOut、REQ-2-1-3 exam.py 快照+delta 计算）
- 2026-08-28：**REQ-2 答题后精通度变化展示 - 前端完成** ✅（REQ-2-1-4 quiz.html 精通度变化卡片渲染：CSS 样式 + renderMasteryDelta 函数 + showResult 调用）
- 2026-08-28：**REQ-2 全栈功能验证通过** ✅（ECS 端到端测试：mastery_deltas 字段正确返回、delta 计算准确、瓶颈诊断生效）
- 2026-08-29：**REQ-3 收尾 — 文档同步 + 验收完成** ✅（补任务文档 REQ-3-1-1 + 三个 INDEX 对齐 + 本机只读实测：数学/编程三科递进生效，语文/英语 sort_order 全 0 暂不生效已记为已知限制；需求结束）
- 2026-08-29：**BUG-5 修复 — 精通度页/管理端矩阵精通度恒显示 0%** ✅（`mastery.html` adaptMeData 补 rate/total + `mastery.py` class_mastery 补 total，算法不变；学员端 45/46/47/48→44/85/19/81% 与组卷界面一致，管理端矩阵无回归；commit `6556915`）
- 2026-08-29：BUG-4 语文/英语 sort_order 数据问题核销/修复 ✅
- 2026-08-29：**BUG-3 修复 — 实操每次 count=1 时连续抽到同一题** ✅（`routers/exam.py:_rank_pool` 增加冷却机制 + 时间打散，避免同一题反复出现；覃禹诺反馈）
- 2026-09-01：REQ-4 整体完结 ✅（ECS 拉库验证 + 设计文档归档；4/4 任务全部完成）
- 2026-09-01：临时检查脚本清理 ✅（`check_css.py` / `check_js.py` / `check_syntax.py` 根目录残留删除；按 it-workflow 纪律 git 仓库不得存临时脚本）
- 2026-09-01：**REQ-6-1-1 后端完成（本地验证）** ✅（`0008_topic_deprecated` 迁移 + `topics.sort_order` INTEGER→REAL 重建表 + `DELETE /api/topics/{id}` 软/硬分流 + `PUT /api/topics/reorder` 浮点插入；本地三场景测通：hard 删空课程 / soft 删有 67 题+1222 作答的 topic_26 / reorder 浮点 (2+12)/2=7.0；待 ECS 部署）
- 2026-09-01：**REQ-6-1-2 前端完成（本地 docker 验证）** ✅（`vendor/sortable.min.js` 本地引用 44.5KB + admin.html 改 5 处：科目行「+ 新建课程」按钮 / 课程行 `≡` 拖拽手柄 / Sortable 初始化带失败回滚 / `confirmDeleteTopic` 传 subjectId + 用缓存题数 / CSS hover+ghost 样式；三资源 HTTP 200；`TopicOut.done_count` 后端返回被做过题数；`_safeMsg` 修复 showConfirm HTML 渲染 bug；删除后局部刷新（DOM 删行 + 缓存剔除 + 计数更新，不收拢）；本地 docker 已验证，三套提示文案均可正常渲染）
- 2026-09-02：**REQ-7 整体完结** ✅（学员端 study.html 课程详情页 + Admin 端课题编辑 iframe 录入 + 部署 ECS 106.14.99.100:8000；commit `e1e01b6`；本地+ECS 真数据全链路验证通过）
- 2026-09-02：**BUG-7 修复（v2 智能渲染）** ✅（admin 录入只粘 URL 时学员端不渲染问题修复；前端智能识别裸 URL/完整 HTML；XSS 防护 `escAttr`；commit `e1e01b6`；ECS 端 B 站视频正常播放）