# REQ-7 学习模块集成（教程+练习一体化）

## 1. 原始描述

> 学员端目前只有刷题功能。希望加入教程学习能力：
> - 文化课（英语/语文/数学）：嵌入人教版电子课本（`https://book.pep.com.cn/...`）
> - 编程课（Python 等）：嵌入 B 站视频教程（`https://www.bilibili.com/video/...`）
> - 目标：学员在 quiz 内完成"看教程→做题"闭环，不再跳站
> - 用途：自家两个孩子使用，无任何商业分发
> - 流程方向：首页科目点击 → 课程详情页（学习/练习两 Tab）→ 学习 Tab 内嵌 iframe 教程，练习 Tab 走现有组卷流程
> - 学员端首页：标题/卡片文案改 2 处，结构不动

## 2. 需求目标

- 在 quiz 内集成外部教程内容（在线课本 + B站视频），学员不离开系统即可学+练
- 学习体验符合业界"学-练-测"一体化产品的成熟模式（步步高/学而思/讯飞）
- 现有刷题流程、题库、积分等核心功能不受影响

## 3. 功能范围

### 3.1 要做（In Scope）

- 学员端首页标题/卡片文案微调（"选择题库"→"课程中心"等）
- 学员端科目卡片点击行为分流：
  - **当前**：点科目卡 → 直接打开组卷配置
  - **变更后**：点科目卡 → 进入课程详情页（学习+练习两 Tab）
  - **例外保留**：实操科目的"选课闯关"流程（现有 openCoursePick）—— 仍走原逻辑，不进入新详情页
- 新增学员端课程详情页 `study.html`：
  - 顶部：科目名 + 当前课程名（如"4年级英语 - Unit 1 Making friends"）
  - 课程序列展示：当前课的 Part/子课（按 topic 顺序）
  - 主体：两个 Tab
    - **📺 学习 Tab**：嵌入外部教程 iframe（B站视频/在线课本），下方"开始做题"按钮
    - **📝 练习 Tab**：复用现有 openConfig/openCoursePick 流程，弹出原有组卷配置弹层
  - 底部：上一课/下一课切换按钮
- 后端：topics 模型加 `tutorial_video_url` + `tutorial_book_url` 字段
  - `tutorial_video_url`：B站视频嵌入 URL（`player.bilibili.com/player.html?bvid=xxx`，所有科目通用）
  - `tutorial_book_url`：在线课本 URL（人教版，仅文化课科目有值，Python 等无）
  - 两字段独立，均可空（某课只有视频，或只有课本，或两者都有，或两者都无）
- 管理端 `admin.html`：复用现有课程编辑弹窗，加两个 URL 输入框（"视频教程 URL（B站）" + "在线课本 URL"）
  - **增**：新建课程弹窗也带这两个字段，填了保存即生效
  - **删**：清空字段 = 删除教程配置（不做独立删除按钮）
  - **改**：编辑课程弹窗里改 URL，保存即生效
  - **接口**：复用 `POST /api/topics`（新建）和 `PUT /api/topics/{id}`（改），body 加 `tutorial_video_url` + `tutorial_book_url` 两个字段即可，**不新增接口**
- iframe 嵌入规则：
  - B站视频：用 `https://player.bilibili.com/player.html?bvid=xxx&autoplay=0` 格式（学员点播放才开始）
  - 人教版课本：用 `https://book.pep.com.cn/.../mobile/index.html` 原 URL
  - 两套 iframe 并列展示（上下排列，各占一区），字段为空则该区隐藏
  - 兜底：两个 URL 都为空时学习 Tab 显示"该课暂未配置教程"提示，并保留"开始做题"按钮

### 3.2 不做（Out of Scope）

- 不实现学习进度跟踪（"看完了"状态记录）—— 学员看自己点"开始做题"
- 不实现视频时间戳 ↔ 题目锚定（边看边练）
- 不实现教程内容本地缓存/下载
- 不实现学员笔记功能
- 不动现有组卷流程的弹层逻辑（openConfig/openCoursePick 复用）
- 不动积分/掌握度/错题本核心模块
- 不动 ECS 部署（仅本地 docker 验证）

## 4. 非功能约束

- **兼容性**：
  - 保留现有 `home.html` 的科目卡片点击行为对实操科目的兼容（仍走 openCoursePick）
  - iframe 加载失败时显示降级提示（"教程加载失败，请直接点击下方按钮开始练习"），不阻塞练习入口
- **性能**：
  - iframe 按需加载（点学习 Tab 时才注入 src，初始不预加载避免首屏慢）
  - 课程切换时不刷新整页，仅切换 iframe src
- **安全**：
  - iframe 沙箱：`sandbox="allow-scripts allow-same-origin allow-popups allow-forms"`，不外跳主站
  - tutorial_url 仅允许 http/https，不接受 javascript: / data: 等危险协议
- **内容版权**：
  - 本系统仅供家庭自用，无任何分发/商业用途
  - iframe 嵌入的是原始网页，不下载/缓存/再分发
  - 不向学员提供"保存到本地"等可能涉及下载的按钮

## 5. 影响范围

- 涉及模块：
  - 学员端首页（home.html）
  - 学员端课程详情页（study.html 新建）
  - 学员端 API（subjects.py GET /topics）
  - 数据模型（Topic 模型 + 迁移）
  - 管理端（admin.html 课程编辑表单）
  - 静态资源（新增 study.html）
- 涉及现有文件/接口：
  - `src/static/home.html`（点击逻辑分流）
  - `src/routers/subjects.py`（GET topics 返回字段扩展）
  - `src/models.py`（Topic 模型加字段）
  - `src/migrations/`（新建 0009）
  - `src/static/admin.html`（课程编辑表单）
- 上下游影响：
  - 学员端首页点击行为变化 —— 实操科目保持原样，理论科目从"直接组卷"改为"进详情页"
  - 家长端、管理端不受影响

## 6. 风险与约束

- **iframe 跨域限制**：人教版/B站页面内有跨域资源，部分浏览器可能拒绝加载 —— 接受现状，加降级提示
- **B 站嵌入 URL 格式**：必须用 `player.bilibili.com/player.html?bvid=` 形式，原始 `bilibili.com/video/` 页面 iframe 嵌入会被 X-Frame-Options 拒 —— 需在管理端说明或后端自动转换
- **移动端体验**：iframe 在小屏体验一般 —— 接受现状（学员目前主要平板/电脑用）
- **管理端表单改动**：admin.html 已有课程编辑表单，加两个字段是低风险

## 7. 验收标准

- [ ] 首页标题改为"课程中心"或类似（不要"题库闯关"等旧词）
- [ ] 理论科目（如英语4年级）点击卡片进入 study.html
- [ ] 实操科目（如 Python基础实操）点击卡片仍走原有选课弹层
- [ ] study.html 顶部显示"科目名 - 当前课程名"
- [ ] 课程序列展示该科目所有 topic，按 sort_order 排序
- [ ] 学习 Tab 内嵌 B站视频能正常播放（用一个测试 BV 号验证）
- [ ] 学习 Tab 内嵌人教版课本能正常显示（用 https://book.pep.com.cn/1212001401255/mobile/index.html 验证）
- [ ] 文化课的某课同时配了视频和课本 URL 时，两套 iframe 都正常显示（上下排列）
- [ ] Python 课的某课只配了视频 URL 时，课本 iframe 区域隐藏，仅显示视频
- [ ] 学习 Tab 两个 URL 都为空时显示降级提示，"开始做题"按钮仍可用
- [ ] 练习 Tab 复用现有 openConfig 弹层，组卷流程不变
- [ ] 上一课/下一课按钮能切换 iframe src
- [ ] 管理端 admin.html 课程编辑弹窗有"视频教程 URL（B站）"和"在线课本 URL"两个输入框
- [ ] 管理端新建课程弹窗也有这两个字段，填完保存成功
- [ ] 管理端编辑已有课程，清空两个 URL 后保存即清除教程配置
- [ ] 上述增/改/删操作均走现有 `POST/PUT /api/topics`，不新增接口
- [ ] 本地 docker 跑通，回归现有刷题流程无破损

## 8. 状态

- 梳理状态：✅已确认
- 设计状态：0/0
- 任务状态：0/0
