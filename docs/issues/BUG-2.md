# BUG-2：组卷页面精通度显示为覆盖率，未达精通也显示 100%

- **类型**：前端显示逻辑错误
- **严重度**：高（家长误以为已精通，但实际未触发奖励）
- **状态**：✅ 已修复（2026-08-26）

## 问题描述

组卷页面（`home.html`）课时旁边显示的百分比是**覆盖率**（做过的题占总题数的比例），而非**精通度**。

例如：
- 尧奕瑶 "变量与标识符"：覆盖率 101.4%（显示 100%），但窗口正确率只有 79.5%，实际状态是 `practicing`
- 家长看到 "100%" 以为已精通，但后端未触发精通奖励

## 根因

`home.html` 的 `masteredBadge()` 函数使用 `masteryCoverageMap[key]` 直接显示覆盖率：

```javascript
// 旧代码（BUG-2）
const cov = masteryCoverageMap[key];
if (cov != null && cov > 0) {
  return '<span>' + Math.round(cov) + '%</span>';
}
```

精通判定需要三门槛同时满足：
1. 覆盖率 ≥ 80%
2. 窗口正确率 ≥ 90%
3. 做题数 ≥ max(题总数×0.8, 10)

只满足覆盖率 100% 不等于精通。

## 修复方案

改为显示**综合精通度百分比**，算法与后端 `core/mastery.py` 三门槛完全对齐：

```
精通度 = min(覆盖率÷80%, 正确率÷90%, 做题数÷门槛) × 100%
```

- 后端 `status == "mastered"` → 前端显示 100%
- 否则按公式计算，上限 99%（杜绝 "显示 100% 但不发奖励"）

## 修改文件

| 文件 | 改动 |
|------|------|
| `src/static/home.html` | `masteredBadge()` 改用 `calcMasteryPercent()`，缓存改为 `masteryDetailMap` |
| `src/static/js/mastery.js` | 新增 `calcMasteryPct()`，`topicCard()` 增加精通度进度条（主）、保留正确率和覆盖率（辅） |
| `src/static/js/analytics-shared.js` | 新增 `calcMasteryPctShared()`，`renderMasteryCoverageChart()` 改为显示精通度柱状图，`renderMasteryMatrix()` 以精通度为主、覆盖率/正确率为辅 |

## 顺手修复

### deploy_window.py

1. 认证方式：密码登录 → 公钥认证（`openclaw.pem`）
2. ECS 目录结构：`src/Dockerfile` → `Dockerfile .`（ECS 是扁平目录，无 `src/` 子目录）
3. `docker-compose` → `docker compose`（ECS 上是 v2）

## 验证

以尧奕瑶 "变量与标识符" 为例：
- 覆盖率 101.4% → 101.4÷80 = 1.27（超了）
- 正确率 79.5% → 79.5÷90 = 0.88
- 做题数 161 → 161÷55 = 2.93（超了）
- **显示：min(1.27, 0.88, 2.93) = 88%**

后端 `status = "practicing"`，前端显示 "88%"，一致。
