# 文化类科目题库格式（语文 / 数学 / 英语）

> 适用科目：语文、数学、英语（category=culture）
> 导入方式：`POST /api/questions/batch`（需 admin token；见步骤 4️⃣）
> 文件格式：**纯数组** `[...]`，顶层直接是题目数组（无 subject 包装）
> 最后更新：2026-09-01（v2 完整流水线：搜索→题型对齐→出题→复核→导入；搜不到/网络不通时**先停下来反馈，不自行降级**）

---

## 〇、完整出题流水线 v2（2026-09-01）

> **适用范围**：所有 culture 科目（语文/数学/英语）出题**必须**走完这 4 步，缺一步视同未完成。
> **事故注**：2026-08-26 Python 理论 8 个入门课（topic 25-32）发现 116 道超纲题（串课、超纲、混入进阶题）；2026-09-01《1 观潮》出题时联网搜不到、稳定后才意识到应该先反馈不直接降级。两次教训都指向"流程不闭环"。

### 总览

**出题前必读（缺一不可）**：
1. 读 `culture_subject.md` 本节步骤 1-4（尤其是"搜不到先停下来反馈"铁律）
2. 读 `question_types.md` 字段表（含 `tier` 字段：1初级/2进阶/3挑战）
3. 读科目模板（如 `chinese_grade4.md`）
4. 读 `docs/qa/manual-review.md` 5 判点
5. 读上轮出题的复核结论（避免同类错误重复）

**出题后必审（5 判点逐题过，结论表必出）**：

| 判点 | 内容 | 处置 |
|------|------|------|
| ① 题目正确性 | 题干通顺、答案对、选项无恒对恒错 | 修 |
| ② 题型专项 | choice 歧义选项、match 左右唯一性、judge 陈述无歧义 | 修 |
| ③ 课程范围 | 紧跟年级课本，不超纲不串课 | 废 |
| ④ 认知范围 | 9-10岁凭已学知识能做，不模棱两可 | 废 |
| ⑤ 答案-讲解一致性 | answer 标对、讲解与 answer 逻辑吻合 | 修 |

> **事故教训**：2026-09-01 繁星 Q6 修辞判断题，讲解与 answer 自相矛盾（A 对但讲解说 B）；秋晚 Q19 match 四改三仍含错误答案。说明复核时必须逐题对照 answer 和 explanation 文字，不能只靠印象判断。

| 步骤 | 动作 | 产出 | 卡控点 |
|------|------|------|--------|
| 1️⃣ 联网搜资料 | 通过 searxng 搜课文原文 + 教案 + 知识点 | 搜索结果清单（含引擎/URL/标题） | 搜不到/网络不通时**必须停下来反馈**，禁止自行降级 |
| 2️⃣ 对齐题型配比 | 列出该课时的核心知识点 + 题型矩阵 + 总题数，报用户确认 | 知识点清单 + 拟出题数 + 占比 | 用户点头前**不写 JSON** |
| 3️⃣ 出题 + 5 判点复核 | 写 JSON 后立即按 `docs/qa/manual-review.md` 的 5 个检查点逐题过堂 | 每题结论（✅/🔧/❌） | 答案错/选项错 → 修；超纲/超认知 → 废 |
| 4️⃣ 导入（仅数据） | 走 `POST /api/questions/batch`，本地/ECS 各调一次，回读一致 | 双端活跃题数与 JSON 一致 | 写入 ECS 前必备份；不写代码、不 scp .db |

---

### 步骤 1️⃣ 联网搜资料（必走，禁止跳过）

**搜索引擎**：优先使用本地自托管的 SearXNG（`http://127.0.0.1:8080`），默认 Bing 引擎；如未部署/不可用，再考虑 `ddgs` 内置 provider。

**SearXNG 调用模板**（Python 3）：

```python
import urllib.request, urllib.parse, json

def searxng_search(query: str, engines: str = "bing", limit: int = 8) -> list[dict]:
    q = urllib.parse.quote(query)
    url = f"http://127.0.0.1:8080/search?q={q}&format=json&engines={engines}"
    try:
        r = urllib.request.urlopen(url, timeout=20)
        d = json.loads(r.read().decode())
        return d.get("results", [])[:limit]
    except Exception as e:
        return [{"error": str(e)}]

# 用法：搜《观潮》四年级
results = searxng_search("观潮 人教版 四年级上册 课文原文")
for x in results:
    print(f"[{x.get('engine')}] {x.get('title','')[:60]} | {x.get('url','')[:80]}")
```

**搜索词模板**（按课时类型）：

| 课时类型 | 搜索词模板 |
|----------|-----------|
| 语文写景/叙事 | `<课名> 人教版 <年级>上/下册 课文原文 教案 知识点` |
| 语文古诗 | `<古诗名> 默写 注释 翻译 中心思想` |
| 数学 | `<章节名> 人教版 <年级> 知识点 考点 易错题` |
| 英语 | `<Unit名> 人教PEP <年级> 单词表 句型 语法点` |

**🚨 搜索失败处置（强制）**：

| 状况 | 处置 |
|------|------|
| SearXNG 返回 0 条结果 | **先停下来反馈**："searxng 搜 `<query>` 返回 0 条，建议：① 换关键词重搜 ② 降级为模板默认知识点硬出题 ③ 取消本次出题" |
| SearXNG 不可达（Connection refused/timeout） | **先停下来反馈**："searxng:8080 不可达（错误信息），建议：① 检查容器 ② 改用内置 ddgs ③ 取消本次出题" |
| 搜到了但内容质量差（如广告站/百科站堆砌） | 用人话汇报：列出找到的 2-3 条最相关结果，问用户是否继续用 |

> **铁律**：以上 3 种情况**绝不自行降级出题**。用户的明确指令（A 继续/B 取消/C 改用 X）才能进入步骤 2️⃣。
> 历史教训：2026-09-01 我擅自决定"搜不到就靠常识硬出《观潮》"，虽然结果碰巧没翻车，但流程是错的。

---

### 步骤 2️⃣ 对齐题型配比（用户未确认前不写 JSON）

根据搜索结果 + 模板 `题型选择参考`，产出三件东西**一句话**汇报给用户，等他点头：

```
课时：<年级> <上/下册> <单元> <课时名>
来源：<出版社> <教材版本> <作者>
核心知识点（3-7 条）：1) ... 2) ... 3) ...
拟用题型：reading(1 含X子题) + choice(N) + judge(N) + fill(N) + match(N) = 共 N 道大题
覆盖维度：时间顺序/修辞/字音/词语理解/成语/中心思想 ...
等你点头再写 JSON
```

**用户回 "确认" 才进入步骤 3️⃣**。临时改题数/题型配比属于设计决策，不擅自动手。

---

### 步骤 3️⃣ 出题 + 5 判点复核（写完 JSON 立即过堂）

按 `data/template/question_types.md` 出题，每题按 `docs/qa/manual-review.md` 的 **5 个检查点** 逐题过堂：

| 判点 | 内容 | 出错处置 |
|------|------|---------|
| ① 题目正确性 | 题干通顺、答案正确、选项无重复/无恒对恒错 | 修 |
| ② 连线题专项 | 左右两列各自文本唯一、一一对应无歧义 | 修 |
| ③ 判断题专项 | 陈述本身事实正确、无歧义 | 修（错题）或 废（超纲） |
| ④ 课程范围 | 紧跟课本年级，不超纲/不串课 | 废（deprecated=1） |
| ⑤ 认知范围 | "9-10 岁没学过这些概念的孩子能不能凭已学知识做对？" 不能/模棱两可 → 废 | 废 |

**复核结论表格式**（每张表必出）：

```
| # | 题型 | 题干 | ① | ②/③ | ④ | ⑤ | 结论 |
| # | reading | ... | ✅ | ✅ | ✅ | ✅ | ✅保留 |
| # | choice | ... | ✅ | ✅ | ✅ | ✅ | ✅保留 |
| # | choice | ... | ✅ | ⚠ 选项不纯净 | ✅ | ⚠ 9岁可误选 | 🔧修复 |
```

**修复后必须重审**（不能再放过）；全表打 ✅ 才算通过本步。

---

### 步骤 4️⃣ 导入（仅数据，不写代码）

**导入方式**：`POST /api/questions/batch`（HTTP 接口，需 admin token），不走任何 .db 替换 / scp / SSH 写盘。

```python
import requests, json

BASE = "http://106.14.99.100:8000"  # ECS
# BASE = "http://127.0.0.1:8000"    # 本地
token = requests.post(f"{BASE}/api/auth/login",
    json={"username":"admin","password":"admin123"}).json()["access_token"]
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

with open("data/<file>.json", encoding="utf-8") as f:
    items = json.load(f)
for it in items:
    it["subject_id"] = <S>; it["topic_id"] = <T>  # 来自本地/ECS 只读核对
r = requests.post(f"{BASE}/api/questions/batch", headers=H, json=items, timeout=30)
print(r.status_code, r.text)  # 期望 200 {"created": N}
```

**回读验证**：

```python
r = requests.get(f"{BASE}/api/questions?topic_id={T}", headers=H)
print(len(r.json()))  # 应等于 N
from collections import Counter
print(Counter(x["type"] for x in r.json()))  # 题型分布应与拟出题数一致
```

**红线**（来自事故 ECSDB-2026-09-01-01）：
1. ECS 写操作前必 `POST /api/admin/backup-db`
2. 本地/ECS `topic_id` 可能不一致（曾误伤 #3758）—— 写前先 GET 只读核对
3. 绝不 `scp data/quiz.db root@ecs:/opt/data/` 替换库
4. 不写代码、不重启服务（纯数据变更）

---

## 〇（旧版，v1）出题前准备工作 SOP ⚠️（已被 v2 取代，仅作参考保留）

> **事故注**：2026-08-26 Python 理论 8 个入门课（topic 25-32）发现 116 道超纲题（串课、超纲、混入进阶题）。v1 的 4 步走没有联网搜索和题型配比对齐两环，导致出题时只能靠模板默认 + 知识库存量。v2 已补齐这两步。

### v1 4 步走（旧版）

| 步骤 | 动作 | 产出 |
|------|------|------|
| 1️⃣ 列出知识点 | 参考课本目录 + 联网搜索该课时核心知识点（人教社官网/教案） | 该课时的 3-7 条核心知识点清单 |
| 2️⃣ 列出题型 | 决定该课时用哪几种题型（choice/judge/fill/match/sort/reading/essay） | 该课时的题型矩阵 |
| 3️⃣ 不超纲检查 | 检查每题（含选项/连线两列）是否在 3-4 年级认知范围内；不出超纲题 | 清单 |
| 4️⃣ 不串课检查 | 检查每题是否只用本课时教过的内容，不引用后续课时 | 清单 |

### 知识点清单模板（出题前先填）

```markdown
## 出题课时：xxx
- 来源：人教版 xx 年级 xx 册 xx 单元 第 X 课《xxxx》
- 核心知识点（3-7 条）：
  1. ...
  2. ...
- 拟用题型：choice / judge / fill / match / sort / reading / essay
- 拟出题数：每种题型 X 道，共 X 道
- 检查项：
  - [ ] 不超纲
  - [ ] 不串课
  - [ ] 答案与讲解语义一致
```

### 题型选择参考

| 课时类型 | 推荐题型 | 不推荐 |
|----------|---------|--------|
| 古诗/韵文 | fill（背默）+ judge + choice | essay |
| 写景/叙事课文 | reading + choice + judge + essay | sort |
| 单词/词组 | match（汉英/拼音）+ choice + fill | essay |
| 算理/公式 | choice + judge + calc + fill | essay |
| 图形/几何 | choice + judge + calc | essay |
| 口语交际 | essay | - |
| 习作 | essay | - |
| 单元整理（园地） | 综合（choice+judge+fill+match） | - |

---

## 一、文件整体结构

```json
[
  { "type": "choice", "topic_name": "校园生活", "unit": "上册-第一单元", "content": "...", "options": [...], "answer": "0", "explanation": "...", "difficulty": 1 },
  { "type": "judge", "topic_name": "校园生活", "unit": "上册-第一单元", "content": "...", "options": ["对","错"], "answer": "0", "explanation": "...", "difficulty": 1 }
]
```

**关键点**：
- 顶层是**数组**，不是对象
- 每题必须有 `topic_name`（课时名）和 `unit`（单元名）两个字段
- 导入时按 `topic_name` 自动建/复用课时，`unit` 一并写入
- 按 `content` 去重，相同题干不会重复导入

---

## 二、unit 命名规范（重要）

上下册单元名**必须加册次前缀**，避免重名混淆：

| 册次 | 语文/数学格式 | 英语格式 |
|---|---|---|
| 上册 | `上册-第一单元` ~ `上册-第八单元` | `上册-Unit 1` ~ `上册-Unit 6` |
| 下册 | `下册-第一单元` ~ `下册-第八单元` | `下册-Unit 1` ~ `下册-Unit 6` |

> ⚠️ 不要只写 `"第一单元"` / `"Unit 1"`，否则上下册会混在同一分组。

---

## 三、各题型完整示例（真实线上数据）

### 1. 选择题（choice）

```json
{
  "type": "choice",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'早晨'的'晨'读音是什么？",
  "options": ["chén", "chéng", "chénɡ", "cén"],
  "answer": "0",
  "explanation": "晨读chén，第二声。",
  "difficulty": 1,
  "tier": 1
}
```

- `options`：4 个选项
- `answer`：正确选项索引（字符串，从 0 开始）

### 2. 判断题（judge）

```json
{
  "type": "judge",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'鲜艳'的近义词是'暗淡'。",
  "options": ["对", "错"],
  "answer": "1",
  "explanation": "'鲜艳'的近义词是'艳丽'，'暗淡'是反义词。",
  "difficulty": 1,
  "tier": 1
}
```

- `options` 固定 `["对","错"]`
- `answer`：`"0"`=对，`"1"`=错

### 3. 填空题（fill）

**单空：**
```json
{
  "type": "fill",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "'早晨'的拼音是 zǎo ____。",
  "answer": "chén",
  "explanation": "晨读chén。",
  "difficulty": 1,
  "tier": 1,
  "blank_count": 1,
  "tolerance": 0.01
}
```

**多空：**
```json
{
  "type": "fill",
  "topic_name": "万以内加减法",
  "unit": "上册-第三单元",
  "content": "36+36=____，结果是____",
  "answer": "36+36",
  "blank_count": 2,
  "blank_answers": ["36+36", "72"],
  "tolerance": 0.01,
  "explanation": "36+36=72。",
  "difficulty": 2,
  "tier": 1
}
```

- `blank_count`：空的数量（默认 1）
- `blank_answers`：多空时各空答案数组
- `tolerance`：数字容差（0=严格，0.01=允许小数误差）

### 4. 应用题（essay）

```json
{
  "type": "essay",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "用'鲜艳'造一个句子。",
  "answer": "待老师点评",
  "explanation": "参考：同学们穿着鲜艳的民族服装，真好看。",
  "difficulty": 1,
  "tier": 1
}
```

- `answer` 固定 `"待老师点评"`（无标准答案）
- 判分降级：作答≥10字即通过（60分/3星）

### 5. 连线题（match）

```json
{
  "type": "match",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "将词语与拼音连线。",
  "options": ["早晨", "坪坝", "鲜艳", "安静"],
  "match_options": ["ān jìng", "zǎo chén", "xiān yàn", "píng bà"],
  "answer": "0:1,1:3,2:2,3:0",
  "explanation": "早晨zǎo chén，坪坝píng bà，鲜艳xiān yàn，安静ān jìng。",
  "difficulty": 1,
  "tier": 1
}
```

- `options`：左侧项目（固定顺序，**内部文本必须唯一，不得重复**）
- `match_options`：右侧选项（**建议打乱顺序**；**内部文本必须唯一，不得重复**）
- `answer`：`"左索引:右索引,..."`，如 `"0:1"` 表示左0→右1
- ⚠️ **去重约束**：左右两侧选项文本各自唯一。重复文本会让判分产生歧义（见 `question_types.md` 连线题去重约束）

### 6. 排序题（sort）

```json
{
  "type": "sort",
  "topic_name": "校园生活",
  "unit": "上册-第一单元",
  "content": "将下列词语按拼音首字母顺序排列。",
  "options": ["安静", "早晨", "坪坝", "鲜艳"],
  "answer": "0,2,3,1",
  "explanation": "按拼音首字母 a、p、x、z 排列：安静、坪坝、鲜艳、早晨。",
  "difficulty": 2,
  "tier": 1
}
```

- `options`：打乱顺序的项目
- `answer`：正确顺序的索引串，`"0,2,3,1"` 表示第1位=options[0]，第2位=options[2]...
- 判分：全对=100，否则=0

### 7. 阅读理解题（reading）—— 语文/英语专用

```json
{
  "type": "reading",
  "topic_name": "阅读理解",
  "unit": "上册-第一单元",
  "content": "春天来了，小明和小红去公园放风筝。\n风筝飞得很高，他们非常开心。",
  "options": null,
  "reading_items": [
    { "type": "choice", "q": "他们去公园做什么？", "options": ["放风筝", "游泳", "爬山", "钓鱼"], "answer": "0", "explanation": "文中说去公园放风筝。" },
    { "type": "choice", "q": "风筝飞得怎么样？", "options": ["很低", "很高", "飞走了", "掉下来了"], "answer": "1", "explanation": "文中说风筝飞得很高。" }
  ],
  "answer": "0,1",
  "explanation": "",
  "difficulty": 2,
  "tier": 1
}
```

- `content`：文章正文（可用 `\n` 分段）
- `reading_items`：子题数组，当前版本子题**只支持选择题**（`type:"choice"`）；
  `type` 字段预留，后续可扩展 judge（英语T/F）、fill、essay 子题
- 子题字段：`q`（问题）、`options`（选项）、`answer`（正确选项索引字符串）、`explanation`（讲解）
- `answer`：各子题正确索引的逗号串，如 `"0,1"`（可用管理后台/导入脚本自动从子题生成）
- 判分：按子题正确比例给分（对2/3≈67分），≥60分算通过；整篇进错题本

---

## 四、导入命令

走 `POST /api/questions/batch`（HTTP 接口），不走 .db 替换 / scp / SSH 写盘。完整 Python 调用模板见**步骤 4️⃣**。

> ⚠️ **历史命令已废弃**：`python src/data/import_array.py --subject-id ... --json ... --label ...`（src/data/ 下已无此脚本，2026-09-01 起统一走 batch API）。
