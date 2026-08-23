# Python基础理论 1900题 核对修正计划

> 创建时间：2026-08-24
> 状态：📝 Draft（待阿尧最终确认）

---

## 一、基本信息

| 项 | 值 |
|---|---|
| 科目 | Python基础理论 |
| 总题量 | 1929 题（实际以 ECS db 为准） |
| 题型分布 | choice 741 / judge 346 / calc 271 / match 489 / sort 71 / fill 5 |
| 定时任务 | 每晚 00:00 启动 |
| 批次大小 | 100 题/批 |
| 预计批次数 | ~20 批 |
| 数据源 | **ECS 为唯一权威数据源** |

---

## 二、铁律

1. **每次执行前，先从 ECS 备份完整 quiz.db，替换本地开发环境和 Docker 环境**
2. **所有数据以 ECS 为准**
3. **FIX 直接写库（修正后同步回 ECS）**
4. **DROP 只标记 deprecated=1，不物理删除**
5. **每 10 题更新一次进度文件，防中断丢数据**
6. **中断后下次启动自动从断点续跑**
7. **新题目自动纳入核对范围（按 ID 排序，未核对即纳入）**

---

## 三、执行流程

```
定时任务启动 (00:00)
  │
  ├─ Step 1: 从 ECS 拉取 quiz.db → 替换本地
  │
  ├─ Step 2: 读取进度文件 progress.json
  │
  ├─ Step 3: 查询未核对题目 (checked 之后的 ID)
  │
  ├─ Step 4: 无剩余题 → 输出汇总 → 结束
  │
  ├─ Step 5: 有题 → 按 100 题/批处理
  │     ├─ 逐题核对（题干/选项/答案/解析/结构）
  │     ├─ PASS → 记录
  │     ├─ FIX → 修正写库 + 记录 fix_log
  │     └─ DROP → deprecated=1 + 记录 drop_log
  │     ├─ 每 10 题更新 progress.json
  │     └─ 批次完成 → 同步修正回 ECS
  │
  └─ Step 6: 全部完成 → 输出汇总报告
```

---

## 四、判定标准

| 判定 | 条件 | 动作 |
|---|---|---|
| **PASS** | 题干通顺、选项无歧义、答案正确、解析准确、结构完整 | 不改动 |
| **FIX** | 答案错误 / 解析错误 / 选项错误 / 题干错字 | 直接修正写库 |
| **DROP** | 结构损坏 / match缺右列 / 无法验证 / 内容不可用 | 标记 deprecated=1 |

### FIX 修正范围
- `answer`：答案值
- `explanation`：解析文本
- `options`：选项内容/顺序
- `content`：题干文本（仅限错字/明显歧义）

### DROP 触发条件（严格限制，不要轻易废弃）
**必须同时满足：确实无法修正 + 没有修正的必要**

- 数据结构彻底损坏，无法解析出题干/选项/答案
- 题目内容与 Python 基础理论完全无关（录错科目）
- 题干和答案均缺失，无任何可修正基础

**以下情况应 FIX 而非 DROP：**
- match 缺右列 → 根据解析/答案反推右列内容，补全选项
- 解析错误 → 重写解析
- 选项顺序乱 → 调整顺序并修正答案索引
- 题干有歧义 → 改写题干使其无歧义

---

## 五、进度文件

路径：`quiz-data/check_progress.json`

```json
{
  "subject": "Python基础理论",
  "total": 1929,
  "checked": 0,
  "last_question_id": 0,
  "started_at": null,
  "updated_at": null,
  "batches": [],
  "fix_log": [],
  "drop_log": [],
  "status": "pending"
}
```

### batch 结构
```json
{
  "batch_id": 1,
  "range_start": 1,
  "range_end": 100,
  "status": "pending|in_progress|done",
  "result": { "pass": 0, "fix": 0, "drop": 0 },
  "started_at": null,
  "finished_at": null
}
```

### fix_log 结构
```json
{
  "question_id": 303,
  "type": "choice",
  "field": "answer",
  "original": "1",
  "corrected": "2",
  "reason": "a[-1]=30 对应选项索引2",
  "time": "2026-08-24 00:15:23"
}
```

### drop_log 结构
```json
{
  "question_id": 3837,
  "type": "match",
  "reason": "match题型缺少右列选项，无法验证答案映射",
  "time": "2026-08-24 00:16:01"
}
```

---

## 六、ECS 同步规则

### 拉取（执行前）
```bash
scp -i /tmp/.k -P 2222 root@localhost:/opt/quiz-system/quiz-data/quiz.db ./quiz-data/quiz.db
```

### 推送（每批完成后）
```bash
scp -i /tmp/.k -P 2222 ./quiz-data/quiz.db root@localhost:/opt/quiz-system/quiz-data/quiz.db
ssh root@localhost "cd /opt/quiz-system && docker compose restart"
```

> ⚠ 推送前需确认 ECS 上 quiz 服务的实际 db 路径，首次执行时探测。

---

## 七、阿尧早间汇报格式

每天早上阿尧问"哪些题有问题"时，我读取 `fix_log` 和 `drop_log`，按以下格式汇报：

```
## 昨晚核对结果（08-24 00:00 ~ 03:30）

### 修正 (FIX) 共 X 题
| ID | 题型 | 问题 | 原值 | 修正为 |
|---|---|---|---|---|
| 303 | choice | 答案错误 | 1 | 2 |
| ... | | | | |

### 废弃 (DROP) 共 Y 题
| ID | 题型 | 原因 |
|---|---|---|
| 3837 | match | 缺少右列选项 |
| ... | | |

### 统计
- 本批核对: 100 题
- PASS: 95 | FIX: 3 | DROP: 2
- 累计已核对: 500 / 1929
- 预计剩余: ~15 小时
```

---

## 八、已确认决策

- [x] 同步节奏：**每批推回 ECS**（安全优先）
- [x] DROP 的题：**不自动补题**，只废弃+记录，由阿尧决定补不补
- [x] 废弃原则：**不要轻易废弃**，除非确实无法修正或没修正必要
- [x] 跑完后输出废弃题知识点分布，供阿尧判断 coverage 缺口

---

*文档版本：v1.0 · 2026-08-24*
