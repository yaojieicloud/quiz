# BUG-1 设计文档残留引用不存在的 routers/admin.py

## 1. 问题描述
- 现象：《系统架构总览.md》《管理后台与学情分析.md》《AI评分与学情报告.md》引用不存在的 `src/routers/admin.py`（模块清单、接口章节标题、行号引用）；管理端功能实际由 `analytics.py`（学情分析/记录管理）+ `system.py`（运维）承载
- 复现步骤：全仓搜索 "admin.py" 命中上述 3 份文档；`src/routers/` 目录无 admin.py
- 关联需求：—
- 关联设计：系统架构总览 / 管理后台与学情分析 / AI评分与学情报告（存量设计文档）

## 2. 根因分析
- 问题定位：管理端路由在演进中由单模块拆分（admin.py → analytics.py + system.py），3 份设计文档未同步
- 根因：文档滞后于代码演进；行号引用（admin.py:343-464 / admin.py:896-909 等）随拆分全部失效
- 影响范围：LLM/新成员会将 AI 周报、记录管理、运维接口误定位到错误文件；行号引用完全失效

## 3. 修复方案
- 策略：修改文档，保持与代码同步（用户 2026-08-25 决策）
- 涉及文件：
  - docs/design/系统架构总览.md：模块表「管理/学情分析/运维」行拆分为「学情分析/记录管理 → analytics.py」+「运维 → system.py」；AI 评分行 admin.py → analytics.py；main.py 挂载行号 20-31 → 25-37
  - docs/design/管理后台与学情分析.md：模块行拆分 analytics/system；§2 标题；§3 标题行号改为 analytics.py:74-149
  - docs/design/AI评分与学情报告.md：模块行；§4 六处行号按 analytics.py:592-690 逐一重验替换（602-616 缓存 / 618-643 聚合SQL / 645-646 无记录400 / 656-658 取分 / 684-689 llm_chat / 690 502 / 660-683 提示词）
- 改动范围：仅文件引用与行号，不改功能描述
- 风险评估：低（纯文档修正，零代码变更）

## 4. 修复记录
- 2026-08-25：3 份设计文档修正完毕；it-workflow 文档中 BUG-1 相关记录同步更新（README.md / design/INDEX.md / init/architecture.md / issues/INDEX.md）

## 5. 回归测试结果
- 全仓 grep "admin.py"：仅剩预期残留——BUG-1 问题单记录、历史一次性部署脚本 `src/data/deploy_step3_rebuild.py`（已执行的历史产物，不在本次范围）
- 接口核对：学情分析 5 接口 + 记录管理 5 接口（analytics.py:74-149）+ 运维 7 接口（system.py）均在 main.py 挂载清单（25-37 行）确认存在
- 结果：✅ 通过

## 6. 状态
- 🟢已关闭（2026-08-25）
