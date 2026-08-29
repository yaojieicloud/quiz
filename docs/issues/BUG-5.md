# BUG-5: 精通度页/管理端精通度矩阵 每课精通度恒显示 0%（与组卷界面不一致）

> 状态: 🟢已关闭（2026-08-29 修复，commit `6556915`）
> 关联: REQ-1 精通度展示 / REQ-2 精通度联动
> 现象来源: 学员覃禹诺「Python 基础实操」所有课程精通度全 0，与组卷界面数值不符

## 现象

学员端精通度页（`mastery.html`）与个人/矩阵展示里，**每一课的「精通度」都显示 0%**（仅已精通显示"精通"），即使该课有真实答题记录（如 覃禹诺 实操科 topic45 正确率 62.5%、覆盖 35%、8 题，本应≈44%）。组卷界面（`home.html`）同一真实数据却显示正常百分比，两边口径不一致。

## 根因

精通度综合算法 = 覆盖度、正确率、做题数三者取**短板**（最小值）。组卷界面把后端每课完整信息（status/rate/coverage/total/topic_total）原样存入 `masteryDetailMap`，故算法正常。但两处拼装 cell 时**漏传了字段**，导致短板恒为 0：

1. **学员端 `mastery.html` 的 `adaptMeData()`**（src/static/mastery.html:91）：拼 `cells` 时只挑了 `status` 和 `coverage`，**漏掉 `rate` 和 `total`** → `calcMasteryPctShared` 里 `rateRatio=(0)/100/0.90=0`、`nRatio=(0)/thrN=0`，`Math.min(...)=0` → 每课恒 0%。
2. **管理端 `routers/mastery.py` 的 `class_mastery()`**（src/routers/mastery.py:196）：拼 `cells` 时只放了 `status/status_label/rate/coverage`，**漏掉 `total`** → 管理端精通度矩阵同样每课恒 0%。

该缺陷由 `0a7c612`（掌握度系统重构 + 学情分析重构）引入；`d4ff6ea`（统一精通度显示规范）仅改动文案，未修复字段遗漏。

## 修复

补全 cell 字段（算法与门槛完全不变，仅恢复数据完整）：

1. `src/static/mastery.html` `adaptMeData()`：cells 补 `rate`、`total`。
2. `src/routers/mastery.py` `class_mastery()`：cells 补 `total`。

修复后（覃禹诺 实操科 tier1）：45→44%、46→85%、47→19%、48→81%，与组卷界面一致；未开做/仅做 1-2 题课程显示 0% 属正确语义。

## 验证

- 学员端 `/api/mastery/me` 走 `adaptMeData` + `calcMasteryPctShared` 回放，8 课数值全部正常。
- 管理端 `/api/admin/mastery?subject_ids=3&tier=1` 矩阵：覃禹诺 44/85/19/81%，另一学员"瑶瑶"(id=2) 均 mastered/94-100%，无回归。
- 改动仅补字段，未触碰算法或其它分支。

## 备注

- 受影响链路仅 `mastery.html`（学员端精通度页）与 `admin.html`（管理端精通度矩阵）；`stats.html` 仅引用公共函数但未走该 cells 结构；`js/mastery.js` 无任何页面引用（废弃）。
