# REQ-7-1 学习模块集成 — 方案设计

## 1. 所属需求

- 需求编号：REQ-7
- 需求标题：学习模块集成（教程+练习一体化：在线课本/B站视频 iframe）
- 需求文档：`docs/requirements/REQ-7.md`

## 2. 设计目标

在 quiz 内实现"学习 + 练习"一体化闭环，学员不跳站完成：看教程 → 做题。学员端新增课程详情页（`study.html`），管理端复用现有课程编辑弹窗加教程 URL 字段，后端加两个 topic 字段。

## 3. 技术方案

### 3.1 技术选型

- **前端**：新增 `src/static/study.html`（纯 HTML/JS/CSS，与现有 `home.html` 一致风格），修改 `home.html` 和 `admin.html`
- **后端**：`models.py` 的 `Topic` 加两列、`schemas.py` 的 `TopicCreate`/`TopicUpdate`/`TopicOut` 加字段、新建 `src/migrations/0010_topic_tutorial_urls.py`
- **路由**：`subjects.py` 的 POST/PUT topics 接口自然透传新字段，无需改动

### 3.2 数据库变更

**迁移文件** `src/migrations/0010_topic_tutorial_urls.py`：

```python
MIGRATION_ID = "0010_topic_tutorial_urls"

def up(engine):
    from migrations import add_column
    add_column(engine, "topics", "tutorial_video_url", "TEXT", default=None)
    add_column(engine, "topics", "tutorial_book_url", "TEXT", default=None)
```

两列均为 `TEXT`，可空，默认 `NULL`。

**模型** `src/models.py` 的 `Topic` 类加两行：
```python
tutorial_video_url = Column(Text, nullable=True)  # B站视频嵌入 URL
tutorial_book_url  = Column(Text, nullable=True)  # 人教版课本 URL
```

### 3.3 Schema 变更

**`src/schemas.py`**：

`TopicCreate`（新建时可选）：
```python
tutorial_video_url: Optional[str] = None
tutorial_book_url:  Optional[str] = None
```

`TopicUpdate`（编辑时可选）：
```python
tutorial_video_url: Optional[str] = None
tutorial_book_url:  Optional[str] = None
```

`TopicOut`（查询返回）：
```python
tutorial_video_url: Optional[str] = None
tutorial_book_url:  Optional[str] = None
```

路由 `PUT /api/topics/{id}` 的 for 循环天然透传新字段（`model_dump(exclude_unset=True)` 自动处理），无需改动。

### 3.4 学员端路由

无需新增后端路由。`study.html` 通过 `location.href` 跳转，传参：
```
study.html?subject_id=8&topic_id=123
```

### 3.5 页面设计

#### 3.5.1 `study.html` 整体布局

```
┌──────────────────────────────────────────────────────────┐
│  ← 返回   [科目名] - [课程名]                            │
├──────────────────────────────────────────────────────────┤
│  [📺 学习]              [📝 练习]      ← Tab 切换       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  左侧课节目录（220px）  │  右侧内容区（flex:1）        │
│  · 第1课 Part A         │  ┌───────────────────────┐  │
│  · 第2课 Part B         │  │  📺 B站视频            │  │
│  · 第3课 ← 当前        │  │  iframe (16:9)         │  │
│  · 第4课               │  └───────────────────────┘  │
│                        │  ┌───────────────────────┐  │
│                        │  │  📖 在线课本            │  │
│                        │  │  iframe (70vh)         │  │
│                        │  └───────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ [← 上一课]     [本课已学N次]  [→ 下一课]        │   │
│  │           [✅ 开始做题！]                         │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Tab 逻辑**：
- 学习 Tab：iframe 加载在 `iframe#tutorialFrame`（按需注入 src，空 URL 不加载，显示降级提示）
- 练习 Tab：调用父窗口 `window.parent.openConfig(subjectId)`（利用 admin 用法：父窗口是 `home.html`，所以 study.html 用 `window.parent` 调用 home.html 函数），`subjectId` 从 URL 参数取

**iframe 嵌入规则**：
- 视频：`src = tutorial_video_url`，`width=100% height=calc(100vw*9/16)`（16:9 比例），空则隐藏
- 课本：`src = tutorial_book_url`，`width=100% height=70vh`，空则隐藏
- 两者都空：显示"该课暂未配置教程"提示文字 + "开始做题"按钮
- `sandbox="allow-scripts allow-same-origin allow-popups allow-forms"`，防外跳主站

**课程切换**：点击左侧目录 → 切换当前课 → 更新 iframe src + 顶部标题 + 上一课/下一课按钮状态

**返回按钮**：`history.back()` 或 `location.href = 'home.html'`

#### 3.5.2 `home.html` 改动

**点击行为分流**（`startOrConfig` 函数）：
```javascript
async function startOrConfig(subjectId) {
  const sub = subjects.find(s => s.id === subjectId);
  if (isPractical(sub)) {
    openCoursePick(subjectId);   // 实操 → 现有选课弹层
  } else {
    location.href = `study.html?subject_id=${subjectId}`;  // 理论 → 新详情页
  }
}
```

**文案改动**（两处，grep "选择题库"/"题库闯关"/"开始今天的闯关"）：
- 标题 `<h1>`：「选择题库」→「课程中心」
- 副标题 `.subtitle`：「开始今天的闯关」→「开始今天的学习」

### 3.6 管理端改动

**`src/static/admin.html`**

`openTopicModal` 函数（新建/编辑课程弹窗），在排序字段后追加两个 URL 输入框：

```javascript
// 新增两个字段
<div class="form-group"><label>📺 B站视频嵌入 URL</label>
  <input type="url" class="form-input" id="fTopicVideoUrl"
    value="${t ? esc(t.tutorial_video_url || '') : ''}"
    placeholder="https://player.bilibili.com/player.html?bvid=..."></div>
<div class="form-group"><label>📖 在线课本 URL</label>
  <input type="url" class="form-input" id="fTopicBookUrl"
    value="${t ? esc(t.tutorial_book_url || '') : ''}"
    placeholder="https://book.pep.com.cn/..."></div>
```

`saveTopic` 函数，POST/PUT body 加两个字段：
```javascript
const videoUrl = document.getElementById('fTopicVideoUrl').value.trim() || null;
const bookUrl  = document.getElementById('fTopicBookUrl').value.trim() || null;
// PUT body:
{ name, unit, sort_order: order, tutorial_video_url: videoUrl, tutorial_book_url: bookUrl }
// POST body:
{ subject_id, name, unit, tutorial_video_url: videoUrl, tutorial_book_url: bookUrl }
```

编辑成功后同步更新 DOM 行的 `data-video-url` / `data-book-url` 属性（可选，便于后续扩展）。

## 4. 涉及文件

### 新增文件
| 文件 | 用途 |
|------|------|
| `src/static/study.html` | 学员端课程详情页（学习+练习双 Tab） |
| `src/migrations/0010_topic_tutorial_urls.py` | 迁移：topics 表加两列 |

### 修改文件
| 文件 | 改动 |
|------|------|
| `src/models.py` | `Topic` 类加两列 |
| `src/schemas.py` | `TopicCreate`/`TopicUpdate`/`TopicOut` 各加两字段 |
| `src/static/home.html` | `startOrConfig` 分流 + 文案改两处 |
| `src/static/admin.html` | `openTopicModal` 加两 URL 输入框 + `saveTopic` 加两字段 |

## 5. 风险评估

| 风险 | 等级 | 缓解 |
|------|------|------|
| B站 `X-Frame-Options` 拒绝 iframe 嵌入 | 低 | 用 `player.bilibili.com` 而非主站页面；该域名支持嵌入 |
| 人教版 iframe 跨域资源被浏览器拦截 | 低 | 接受现状，加降级提示兜底 |
| `window.parent.openConfig` 跨窗口调用失败（study.html 非 home.html 子窗口） | 低 | study.html 直接另开窗口承载练习 Tab（即关闭 home.html 的模拟；改用按钮点开 `home.html?pick=subjectId` 的 hash 弹层），或练习 Tab 直接 `location.href = 'home.html?pick=' + subjectId + '&autoStart=1'` 让 home.html 进页面自动弹组卷 |
| 迁移重复执行 | 低 | `migrations/__init__.py` 有幂等设计，列已存在自动跳过 |
| 管理端课程列表缓存 topicsCache 同步 | 低 | 编辑后 `topicsCache[subjectId]` 已做覆盖（line 786），无需额外处理 |

> **练习 Tab 跨窗口问题**（方案 5.3.6 注）：`study.html` 打开后不是 `home.html` 的 iframe 子窗口，`window.parent.openConfig` 会失败。稳妥方案：练习 Tab 的"开始做题"按钮 `location.href = 'home.html?pick=' + subjectId`，回到 home.html 后由 URL 参数自动触发 `openConfig`（现有逻辑已有 `?pick=` 支持）。

## 6. 关联任务预估

| 任务编号 | 任务标题 | 依赖 |
|----------|----------|------|
| REQ-7-1-1 | 后端：迁移 + 模型 + schema 加字段 | — |
| REQ-7-1-2 | 管理端：admin.html 课程编辑弹窗加两 URL 字段 | REQ-7-1-1 |
| REQ-7-1-3 | 学员端：home.html 点击分流 + 文案改动 | REQ-7-1-1 |
| REQ-7-1-4 | 学员端：新建 study.html 课程详情页 | REQ-7-1-1, REQ-7-1-3 |
| REQ-7-1-5 | 本地 docker 验证 + 回归测试 | REQ-7-1-2, REQ-7-1-4 |

## 7. 状态

- 设计状态：✅已确认

---

## 8. v2 补充（2026-09-02 BUG-7）

### 8.1 触发

实际使用中发现：admin 录入时经常只粘 URL（懒得手写 `<iframe>`），但 v1 的渲染逻辑 `embedContainer.innerHTML = raw` 对裸 URL 只会当作文本显示，学员端看不到视频。

### 8.2 改动

在 `study.html` 的 selectTopic 函数中增加**智能识别**：

| 输入格式 | 识别方式 | 渲染行为 |
|---------|---------|---------|
| 裸 URL（`^https?://` 开头，无 HTML 标签）| 正则 `/<(iframe|video|embed|object|script)/i` 排除 | 自动包成 `<iframe src="..." allowfullscreen>` |
| 完整 HTML 标签 | 含 `<iframe>`/`<video>`/`<embed>` 等 | 直接 `innerHTML = raw`（保留原属性） |

### 8.3 URL 包装的差异化属性

按 URL 后缀/域名自动选择不同的 iframe 属性：

| URL 特征 | iframe 属性 |
|---------|-----------|
| `.pdf` 结尾 | `style="width:100%;height:600px"` |
| 其他 | `allowfullscreen style="width:100%;aspect-ratio:16/9;border:none;border-radius:10px;"` |

### 8.4 XSS 防护

新增 `escAttr` 函数，转义 URL 中的 `&` 和 `"`，防止 attribute 注入。

### 8.5 Admin 端 UX

`admin.html` 的 placeholder 改写为**两种格式都展示**，并增加智能识别提示文字，降低 admin 学习成本。

### 8.6 验证

- ECS 端（106.14.99.100:8000）真实数据验证：topic 287（裸 URL）和 topic 288（完整 iframe）均渲染正常
- B站视频可正常播放

### 8.7 关联

- BUG-7.md
- commit `e1e01b6`

