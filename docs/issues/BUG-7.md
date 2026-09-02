# BUG-7 Admin 录入体验改进：智能识别 URL 与 iframe

## 1. 问题描述

- 现象：Admin 在 `admin.html` 课题编辑表单的"教程内容"文本框中录入内容时，**只支持完整 iframe 标签**。
  - 如果只粘贴裸 URL（如 `https://www.bilibili.com/video/BVxxx`），学员端 `study.html` 渲染该 URL 时会**直接被浏览器当作文本显示**（因为 `embedContainer.innerHTML = raw` 把纯文本注入 DOM，浏览器不会把 URL 文本自动转成 `<iframe>`）
  - 阿垚实际录入时，更倾向于只粘 URL（更快），但当前系统需要他手写 `<iframe>` 标签，对 admin 录入体验不友好
- 复现步骤：
  1. 打开 admin 编辑课题表单
  2. 文本框粘入 `https://www.bilibili.com/video/BV1c9Mk61EBU`
  3. 保存
  4. 学员端打开对应 topic → 看到的是 URL 文字，不是视频
- 关联需求：REQ-7
- 关联设计：REQ-7-1
- 严重程度：体验问题（非功能性 bug，但影响实际使用）

## 2. 根因分析

- 根因：`study.html` 的渲染逻辑固定为 `embedContainer.innerHTML = raw`，未做格式识别
- 影响范围：所有 admin 录入裸 URL 的场景
- 不是代码 bug，是设计遗漏——REQ-7-1 §3.5.1 当时只考虑了 iframe 标签的 case

## 3. 修复方案

- 策略：前端在渲染时做格式识别，两种输入都正常显示
- 涉及文件：
  - `src/static/study.html`（学员端渲染逻辑）
  - `src/static/admin.html`（placeholder 提示更新）
- 改动范围：~30 行代码，无 schema 变更，无迁移
- 风险评估：低（纯前端渲染，XSS 风险已用 `escAttr` 控制）

### 3.1 识别规则

```javascript
// 智能识别：
//   ① 裸 URL（以 http/https 开头，无 HTML 标签）→ 自动包 iframe
//   ② 已有 <iframe>/<video>/<embed>/<object>/<script> → 直接 innerHTML
const raw = t.tutorial_embed_html.trim();
const isUrl = !/<(iframe|video|embed|object|script)/i.test(raw) && /^https?:\/\//.test(raw);
```

### 3.2 URL 自动包装策略

```javascript
if (isUrl) {
  // B站 / YouTube / 普通 URL：根据平台生成不同的 iframe 属性
  const u = raw.split('?')[0].toLowerCase();
  let attrs = 'allowfullscreen style="width:100%;aspect-ratio:16/9;border:none;border-radius:10px;"';
  if (u.includes('.pdf')) {
    attrs = 'style="width:100%;height:600px;border:none;border-radius:10px;"';
  }
  eContainer.innerHTML = `<iframe src="${escAttr(raw)}" ${attrs}></iframe>`;
} else {
  // 已有 HTML 标签：直接渲染
  eContainer.innerHTML = raw;
}
```

## 4. 修复记录

- 2026-09-02 commit `e1e01b6`：
  - `study.html` 新增 URL 识别 + 智能包装（~20 行）
  - `study.html` 新增 `escAttr` 属性转义工具函数（~6 行）
  - `admin.html` placeholder 改写，明示两种录入格式
- 部署：本地 docker + ECS（106.14.99.100:8000）均验证通过

## 5. 回归测试结果

- 裸 URL `https://player.bilibili.com/player.html?bvid=BV1GJ411x7h7` → 自动包成 iframe + allowfullscreen ✅
- 裸 URL `https://www.bilibili.com/video/BV1c9Mk61EBU?spm_id_from=...` → 自动包成 iframe + B站视频可正常播放 ✅
- 完整 iframe 标签 `<iframe src="..." allowfullscreen></iframe>` → 直接渲染（保留原属性）✅
- HTML 注入风险：`escAttr` 转义 `"` 和 `&` ✅

## 6. 状态

- 🟢已关闭（2026-09-02，commit `e1e01b6`）
