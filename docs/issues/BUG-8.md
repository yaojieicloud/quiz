# BUG-8 提交报错一闪而过 + 422 错误信息丢失

| 项 | 值 |
|---|---|
| 状态 | 🔄修复中 |
| 类型 | 体验问题 + 后端校验不友好 |
| 录入时间 | 2026-09-04 |
| 关联需求 | — |

## 1. 问题描述

ECS 上学员端做语文题，提交时浏览器弹出错误提示，但**提示一秒钟就消失**（用户原话"这个报错一下就消失了，我无法截图 复制"）。用户无法看到具体错误内容、无法截图发给管理员。

## 2. 复现证据（ECS 真实日志）

```
INFO:     61.170.224.87:3730 - "POST /api/exam/submit HTTP/1.1" 422 Unprocessable Content
```

该 422 是 FastAPI Pydantic 校验错误，响应体格式：

```json
{
  "detail": [
    {
      "type": "missing|int_type|int_parsing|...",
      "loc": ["body", "field_name"],
      "msg": "Field required | Input should be a valid integer | ...",
      "input": <触发错误的原始值>
    }
  ]
}
```

## 3. 根因分析

定位到两处代码缺陷（**双重叠加**）：

### 缺陷 A：toast 自动消失（`src/static/js/common.js:50`）

```js
function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);  // ← 2.5 秒自动消失
}
```

→ **所有 toast（成功/错误/普通提示）2.5s 自动消失**，用户根本来不及看。

### 缺陷 B：API 错误信息被破坏（`src/static/js/common.js:16-17`）

```js
const data = await res.json();
if (!res.ok) throw new Error(data.detail || '请求失败');  // ← data.detail 是数组
```

→ 后端 422 的 `data.detail` 是**数组**（Pydantic 标准格式），前端却当字符串塞进 `Error()`。`new Error([...])` 会把数组 toString 成 `"[object Object],[object Object]..."`，**用户看到的错误就是这种乱码**。

复现验证（见 `/tmp/r3.py`）：

```text
NaN duration          → 500 (Pydantic NaN 崩了)
null duration         → 422 "Input should be a valid integer"  
超大 duration         → 500 Internal Server Error
answers 含 null qid   → 422 "Input should be a valid integer, got None"
```

## 4. 422 根因定位（待定）

本次用户报错的**具体 422 字段**还没 100% 定位，但**改造点 A+B 一旦落地，错误信息就能完整显示**。当前最可能触发 422 的两个路径：

1. **旧版 `quiz_exam` localStorage 中 `questions[].id` 缺失**（schema 升级后老数据残留）→ `answers[].question_id` 序列化时为 null
2. **前端某题型（match/sort）答案转换失败** → 仍可触发字段异常

需要**先做改造**让用户能看到 422，再让用户截图发回才能精确定位。

## 5. 改造方案（待阿垚确认）

### 方案 1：通用错误弹窗（推荐）✅

- 在 `common.js` 新增 `showError(title, body)`，渲染**手动确认弹窗**（类比 `showMasteryRewardPopup`）：
  - 标题 + 错误详情（`data.detail` 数组时智能格式化）
  - 「📋 复制」按钮（一键复制到剪贴板）
  - 「关闭」按钮（手动确认）
- 把所有 `catch (e) { toast(e.message, 'error') }` 改为 `showError('请求失败', e.message)`
- 成功 toast 保留 2.5s 自动消失（成功提示不需要确认）

### 方案 2：后端友好化 422 错误信息

- 在 `src/main.py` 加 FastAPI `exception_handler(RequestValidationError)`，把 422 响应改写为：
  ```json
  {"detail": "answers[0].question_id 不能为空（实际值: null）"}
  ```
- 字符串 detail，前端不用改也能显示

### 方案 3：定位并修复 422 根因

- 在前端 submit 前对 `duration_seconds`、`answers[].question_id` 做兜底校验
- 清理老版 `localStorage.quiz_exam` 兼容性
- 这是治本，但要先能复现

## 6. 建议组合：方案 1 + 方案 3

- **方案 1 必做**：错误弹窗手动关 + 复制，**保证后续任何错误都能被用户主动反馈**（含 422/500/网络错误等）
- **方案 3 选做**：找到 422 根因后修复，避免下次再 422
- 方案 2 可选（如果方案 1 的格式化做得够好就不需要）

## 8. 修复内容（2026-09-04）

### 任务1：showError 弹窗（仅错误时）+ 普通toast延长
- **common.js**：
  - 新增 `showError(title, body)`：手动确认弹窗 + 复制按钮 + `console.error` 控制台记录
  - 新增 `formatApiError(data, status, url)`：把 Pydantic 422 detail 数组格式化成 `answers[0].question_id: Input should be a valid integer (实际值: null)` 的多行文本
  - `toast()` 默认时长从 2.5s → **5s**；`durationMs` 第三个参数保留可自定义
  - API 网络错误单独捕获并记录
  - 替换全部 `toast(e.message, 'error')` → `showError('请求失败', e.message)`（9处）
- **admin.html**：所有 catch 块改 showError
- **quiz.html**：submit 报错改 showError（精确 title='提交失败'）

### 任务2：后端 + 前端全链路错误日志
- **models.py**：新增 `ErrorLog` 模型（error_logs 表）
- **migrations/0012_error_logs.py**：建表 + 3索引
- **routers/log.py**（新）：`POST /api/log/error`（前端 JS 报错上报）、`GET /api/log/errors`（admin 分页查看）、`DELETE /api/log/errors`（按天数清理）
- **main.py**：新增 3 个全局 exception_handler
  - `RequestValidationError` → kind=validation_422，记录原始 request body（含触发 422 的 input 值）
  - `StarletteHTTPException` → >=500 打 error_logs；<500 仅记 info
  - `Exception` → 500 + traceback 完整入库
  - 写库失败兜底到文件 + stdout，绝不递归抛异常

### 任务3：422 根因定位 + 前端防御修复
- **quiz.html submit**：answers 构造改用 for 循环，跳过 `q.id` 缺失的题（console.warn 记录）
- match/sort 题答案解析失败时显式设 `answer = null`（不再静默保留原值）
- `duration_seconds` 加 NaN 兜底 + 上限 3h（`Math.min(10800, ...)`）
- answers 全空时前端拦截 + showError 提示刷新

## 9. 验证（本地 docker）

```
触发 422 (subject_id=abc) → 自动入库
GET /api/log/errors       → total=3, 含 kind=validation_422, status=422, input="abc"
JS 报错 POST              → kind=js_error, username=qinyunuo
容器启动                  → 正常（[migrate] schema up to date）
```

## 10. ECS 部署

| 文件 | 操作 |
|---|---|
| src/static/js/common.js | build |
| src/static/admin.html | build |
| src/static/quiz.html | build |
| src/static/js/admin-reward.js | build |
| src/static/js/lottery.js | build |
| src/static/js/redeem.js | build |
| src/models.py | build |
| src/main.py | build |
| src/routers/log.py | build (新文件) |
| src/migrations/0012_error_logs.py | build (新文件) |

```
cd quiz && docker build -t quiz-system:local -f src/Dockerfile . && docker save quiz-system:local | ssh ecs "docker load" && ssh ecs "cd /opt/quiz-system && docker compose up -d --force-recreate"
```
