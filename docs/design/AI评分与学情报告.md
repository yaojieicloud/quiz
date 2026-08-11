# AI 评分与学情报告 设计文档

> 模块：`core/code_runner.py`（沙箱）、`core/llm_client.py`（LLM 通道）、`core/llm_grader.py`（code 评分）、`routers/admin.py`(analytics_report)
> 关联：[题型与出题规范](题型与出题规范.md)（code 题判法）、[管理后台与学情分析](管理后台与学情分析.md)（AI 周报）

---

## 1. 沙箱执行 `core/code_runner.py`

- `run_python(code, sample_input, timeout=6.0)`（`:56`）；rc 约定 `0=正常 / -1=超时 / -2=运行异常`。
- 执行：临时目录 + `[sys.executable, "-I", "-X", "utf8", fpath]`，`capture_output`。
- **安全黑名单** `_FORBIDDEN`：os / subprocess / socket / shutil / pathlib / importlib / ctypes / multiprocessing / signal / requests / urllib / pty / popen 等（`:20-38`）；守卫先存 `_real_import` 防递归。
- 环境白名单 `_ENV_ALLOW = ("PATH","LANG","LC_","TEMP","TMP")`；注入 `PYTHONHASHSEED=0`、`PYTHONUTF8=1`、`LANG=C.UTF-8`。
- `normalize_output` 归一化（小写、去空白）用于 expected_output 比对。`expected_output` 为空时视为不校验（降级判 100 分，见下）。

---

## 2. LLM 通道 `core/llm_client.py`

- aliyun 主：`qwen3.7-plus`（`LLM_ALIYUN_MODEL` 可覆盖），`DEFAULT_TIMEOUT=90`。
- deepseek 兜底：`deepseek-v4-flash`（`LLM_DEEPSEEK_MODEL` 可覆盖）。
- Key：aliyun 读 `LLM_API_KEY` 或 `/app/data/llm_key.txt`；deepseek 读 `DEEPSEEK_API_KEY` 或 `/app/data/deepseek_key.txt`。
- 无 key 的 provider 跳过；全部无 key 抛 `RuntimeError`；有尝试但全失败抛 `last_exc`。
- **每次调用无论成败都写 `llm_calls`**（独立 Session，失败静默）——用于审计。

---

## 3. code 题评分 `core/llm_grader.py` + `exam.py`

1. `run_python(code, sample_input)` 沙箱实跑（`exam.py:220-270`）。
2. rc≠0 仍调 LLM 求诊断（`exam.py:241-248`）。
3. LLM 可用 → `is_ok = llm_info["score"] >= 60`（三星及以上通过，`exam.py:246,258`）。
4. LLM 全失败降级 → stdout `normalize_output` 精确匹配；`expected_output` 为空直接判 5 星 100 分（`exam.py:262-265`）。
5. 调用参数：`scenario="code_grade", temperature=0, max_tokens=300, timeout=90`（`llm_grader.py:85-93`）。
6. 星级↔分数映射写在提示词：`5星=100 / 4星=80 / 3星=60 / 2星=30 / 1星=10 / 0星=0`（`llm_grader.py:44`）。
7. 合法性校验 `stars 0-5` / `score 0-100`，越界或 JSON 解析失败 → `_fallback()` 返回 `{-1,-1}`（`exam.py:281` 以 `stars<0` 识别降级）。

> ⚠️ 已知落差：`llm_grader.py` 顶部 `LLM_API_KEY` 模块导入时求值，与 `llm_client` 运行时读取不同步。

---

## 4. AI 学情周报 `POST /api/admin/analytics/report`

- 入参 `{student_id, force}`；`force=False` 命中 **7 天缓存** `datetime('now','-7 days')` 直接返回 `cached:True`（`admin.py:896-909`）。
- 聚合 4 组 SQL：按科目正确率、按知识点（HAVING≥2，正确率升序 LIMIT 8）、全部考试分数、未掌握错题数（`admin.py:911-936`）。
- 无答题记录 → 400；取 early_scores 前 5 / recent_scores 后 5（`admin.py:950-951`）。
- 通道：`llm_chat(scenario="weekly_report", temperature=0.7, max_tokens=800, timeout=90)`（`admin.py:972-981`）。
- **全部 provider 失败抛 502，不造假**（`admin.py:982-983`）。
- 落 `AIReport`，`data_summary` 含 score_trend / by_subject / weak_topics。
- 提示词要求 200-350 字、三段式【学习概况】【进步与亮点】【薄弱点与建议】（`admin.py:963-969`）。

### AI 报告管理
`GET /api/admin/ai-reports`（列表）、`GET /api/admin/ai-reports/{id}`、`DELETE /api/admin/ai-reports/{id}`。

---

## 5. 相关前端

- `admin.html` 内「AI周报」子面板（`analytics/report`）。
- `admin-llm.html` + `js/admin-llm.js`：LLM 调用日志审计（`GET /api/admin/llm-calls`，按场景/provider/状态筛选）。
