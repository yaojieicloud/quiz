# REQ-1-1 掌握度/最近动态柱状图横向响应式改造

## 1. 所属需求
- 需求编号：REQ-1
- 需求标题：统一掌握度/最近动态柱状图样式为横向响应式
- 需求文档：docs/requirements/REQ-1.md

## 2. 设计目标
把两个 ECharts 纵向 bar（掌握度·各课覆盖度、最近动态·各课答题量）改写为**纯 HTML/CSS 横向进度条**，每课一行（标签 + 横向条 + 数值），彻底消除窄屏/手机上课程多时的横向挤压与标签重叠问题。其余图表（矩阵表、成绩趋势折线、场次明细表）**保持 ECharts 不动**。

## 3. 技术方案

### 3.1 技术选型
- 纯 HTML/CSS 实现横向柱（`div` + `flex` + 百分比宽度），**不引入新依赖**，这两个柱状图不再依赖 ECharts
- 保留 ECharts 供其余图表（矩阵/曲线）使用，不删除 `vendor/echarts.min.js` 引用
- 前端无构建步骤，直接改 JS/CSS 文件，`docker cp` 或热更新即生效

### 3.2 架构设计
- 核心改动集中在共享组件 `src/static/js/analytics-shared.js` 的 2 个函数：
  - `renderMasteryCoverageChart(domId, d)` → 输出 `<div class="hbar-list">` 横向柱 HTML
  - `renderRecentTopicChart(domId, d)` → 输出同样式横向柱 HTML
- 两函数不再调 `echarts.init`/`chart.setOption`，改 `el.innerHTML = ...`；移除对 `_sharedCharts` 缓存（这两图）的依赖，但该缓存对象保留供其他 ECharts 图使用
- **数据聚合逻辑保持不变**：掌握度保留「所选学员平均覆盖度」，最近动态保留 `answers + rate`

### 3.3 数据模型
无后端/接口/表结构变更。入参结构沿用现有：
- 掌握度：`d = { tier, topics:[{name, subject_name, topic_total, cells:{sid:{tier:{status, coverage}}}}], students:[{id,name}] }`
- 最近动态：`d = { by_topic:[{student, subject, topic, answers, rate}], sessions:[...] }`

### 3.4 接口定义
无接口变更。继续使用现有接口：
- 掌握度：`GET /api/admin/mastery?tier=&subject_ids=`、`GET /api/mastery/me`
- 最近动态：`GET /api/exam/recent-activity`、`GET /api/admin/analytics/recent-activity`

### 3.5 关键流程
1. 页面加载 → 拉取数据结构（不变）→ 调用渲染函数
2. `renderMasteryCoverageChart`：遍历 `d.topics`，每课计算所选学员平均覆盖度 → 按覆盖度定色 → 生成一行 `label + track(fill + masterline) + val`
3. `renderRecentTopicChart`：遍历 `d.by_topic`（前 20），生成 `label + track(fill) + val(题数 正确率%)`
4. `.chart-box` 容器改为自适应高度 + 最大高度滚动，课多不挤压

### 3.5 横向柱 DOM 结构（两行结构，复刻 qyn_mastery_chart.html）
```html
<div class="hbar-list">
  <div class="hbar-row">
    <div class="hbar-head">                            <!-- 标签行：单独一行，在柱上方 -->
      <span class="hbar-label">科目·课名</span>
      <span class="hbar-meta">题库 69 题</span>          <!-- 次要元数据 -->
    </div>
    <div class="hbar-track">                            <!-- 柱行：占满整行宽 -->
      <span class="hbar-fill" style="width:72.5%;background:#e67700;"></span>
      <span class="hbar-masterline"></span>             <!-- 仅掌握度图，80% 精通门槛 -->
      <span class="hbar-val">72.5%</span>               <!-- 数值，跟随柱末端 -->
    </div>
  </div>
</div>
```

### 3.6 CSS 样式要点（common.css 新增）
- `.hbar-list`：宽度 100%，`padding:4px 0`
- `.hbar-row`：`margin-bottom:16px`（课间距）；`:last-child` 收窄
- `.hbar-head`：`display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px`
- `.hbar-label`：`font-size:14px; font-weight:600; color:#0f172a; word-break:break-all`（标签单独一行，不占用柱宽）
- `.hbar-meta`：`font-size:12px; color:#94a3b8; white-space:nowrap`
- `.hbar-track`：`position:relative; height:20px; background:#eef2f7; border-radius:6px; width:100%`（柱占满整行宽）
- `.hbar-fill`：`position:absolute; left:0; top:0; height:100%; border-radius:6px; min-width:2px; transition:width .4s`
- `.hbar-masterline`：`position:absolute; left:80%; top:-3px; bottom:-3px; width:2px; background:#f97316; opacity:.55`
- `.hbar-val`：`position:absolute; top:0; transform:translateX(6px); font-size:12px; font-weight:700; line-height:20px; white-space:nowrap`（跟随柱末端）
- 颜色规则沿用：覆盖度 ≥80 `#e67700`、≥50 `#69db7c`、≥20 `#74c0fc`、<20 `#dee2e6`；最近动态统一 `#74c0fc`
- `.chart-box.hbar-box`：`width:100%; height:auto !important; min-height:40px;`（**用双类+!important 覆盖页面内联 `.chart-box{height:320px}`**，高度跟随柱状图内容，无滚动条、背景方框随之撑高）

## 4. 涉及文件
- 新增文件：无
- 修改文件：
  - `src/static/js/analytics-shared.js`（2 函数重写，核心）
  - `src/static/css/common.css`（新增横向柱样式 + 响应式）
  - `src/static/admin.html`（`#chartMasteryDist`/`#chartRecentTopic` 容器适配）
  - `src/static/mastery.html`（`#chartMasteryDist` 容器适配）
  - `src/static/stats.html`（`#chartRecentTopic` 容器适配）
  - `docs/design/管理后台与学情分析.md`（前端清单同步）
  - `docs/design/掌握度与学情联动设计.md`（§5 前端清单同步）
- 依赖变更：无（不增删第三方依赖）

## 5. 风险评估
- 低。纯前端渲染层重构，不改后端/接口/结构。主要风险：
  - `analytics-shared.js` 被 3 页面复用，改写须保证入参兼容 → 保留原聚合逻辑、逐一页验
  - 移动端隐藏 ECharts tooltip 后须保证数值可读 → 保留 `.hbar-val` 数值标签
- 回滚：改前可 `git stash`/备份 `analytics-shared.js`

## 6. 关联任务预估
- 预计拆分为 3 个任务：
  - REQ-1-1-1：CSS 横向柱样式 + 响应式（common.css）
  - REQ-1-1-2：改写 analytics-shared.js 两个渲染函数
  - REQ-1-1-3：3 页面容器适配 + 文档同步 + 联调验证

## 7. 状态
- 设计状态：✅已确认（用户 2026-08-25 确认方案）
