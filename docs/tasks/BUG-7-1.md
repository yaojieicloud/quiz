# BUG-7-1 v2 智能渲染：Admin 录入只粘裸 URL 自动包 iframe

## 1. 任务描述

修复 BUG-7：admin 录入只粘裸 URL 时，学员端 study.html 无法正确渲染成 iframe。改为前端智能识别输入格式：
- 裸 URL（`^https?://` 开头）→ 自动包成 `<iframe>`
- 已有 `<iframe>`/`<video>`/`<embed>` 标签 → 直接渲染

## 2. 涉及文件

- `src/static/study.html`（学员端渲染逻辑）
- `src/static/admin.html`（placeholder 提示优化）

## 3. 实施步骤

### 3.1 study.html 智能识别

在 `selectTopic` 函数里把原来的：
```js
eContainer.innerHTML = t.tutorial_embed_html;
```
改为：
```js
const raw = t.tutorial_embed_html ? t.tutorial_embed_html.trim() : '';
if (raw) {
  const isUrl = !/<(iframe|video|embed|object|script)/i.test(raw) && /^https?:\/\//.test(raw);
  if (isUrl) {
    // 裸 URL：自动包装
    const u = raw.split('?')[0].toLowerCase();
    let attrs = 'allowfullscreen style="width:100%;aspect-ratio:16/9;border:none;border-radius:10px;"';
    if (u.endsWith('.pdf')) attrs = 'style="width:100%;height:600px;border:none;border-radius:10px;"';
    eContainer.innerHTML = `<iframe src="${escAttr(raw)}" ${attrs}></iframe>`;
  } else {
    eContainer.innerHTML = raw;
  }
}
```

### 3.2 escAttr 工具函数

新增属性值转义：
```js
function escAttr(s) {
  if (s == null) return '';
  return String(s).replace(/[&"]/g, c => ({'&':'&amp;','"':'&quot;'}[c]));
}
```

### 3.3 admin.html placeholder

把单行"直接粘贴 iframe"提示改为展示两种格式：
```
1. 直接粘贴完整 iframe 标签（自动渲染）
2. 只粘贴 https URL（自动包成 iframe）
```

## 4. 验证

- [x] 裸 URL `https://player.bilibili.com/player.html?bvid=BV1xxxxx` → 自动包成 iframe ✅
- [x] 裸 URL `https://www.bilibili.com/video/BV1xxxxx?spm_id_from=...` → 自动包成 iframe ✅
- [x] 完整 iframe 标签 → 直接渲染保留原属性 ✅
- [x] XSS 防护：`escAttr` 转义 `&` 和 `"` ✅
- [x] ECS 端 106.14.99.100:8000 真实数据验证通过

## 5. 状态

✅已完成
- commit: `e1e01b6`
- 部署：本地 docker + ECS（已上线）
