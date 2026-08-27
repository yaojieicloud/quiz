# Python 基础实操题库格式（code 题专用）

> 适用科目：Python基础实操(id=3)，category=programming
> 导入脚本：`src/data/import_via_api.py`
> 文件格式：**嵌套对象** `{ "subject": {...}, "questions": [...] }`
> 支持题型：**仅 `code`**（编程题，后台沙箱实跑判分 + LLM 评星）

---

## 一、文件整体结构

```json
{
  "subject": {
    "name": "Python基础实操",
    "icon": "💻",
    "grade": "L1-L20 递进",
    "desc": "Python 实操编程题，递进式综合运用"
  },
  "questions": [
    {
      "type": "code",
      "topic_name": "变量与标识符",
      "content": "定义一个变量 name，赋值为字符串 小明，然后用 print 打印这个变量。",
      "options": null,
      "answer": "name = \"小明\"\nprint(name)",
      "explanation": "先写 name = '小明'，注意变量名不加引号、字符串的值要加引号；再用 print(name) 打印。",
      "difficulty": 1,
      "sample_input": "",
      "expected_output": "小明\r\n"
    }
  ]
}
```

**关键点**：
- 顶层是**对象**，包含 `subject` 和 `questions`
- 每题 `type` 固定 `"code"`
- `answer` 是**参考代码**（学生端隐藏，仅 admin 可见）
- `expected_output` 和 `sample_input` 是 code 题**判分关键字段**

---

## 二、code 题专用字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `type` | ✅ | 固定 `"code"` |
| `content` | ✅ | 题干，描述要编写的程序功能 |
| `answer` | ✅ | **参考代码**（Python 源码字符串，学生端隐藏） |
| `expected_output` | ✅ | 参考代码运行后的**预期 stdout**（判分比对依据） |
| `sample_input` | 可选 | 参考代码 `input()` 需要的 stdin 样例（无 input 则填空字符串） |
| `explanation` | 建议填 | 指导思路（学生答题时可见，**不要泄露参考代码**） |
| `difficulty` | 建议填 | 难度 1-5 |

---

## 三、expected_output 生成规则（关键）

`expected_output` 必须是**实际运行参考代码**得到的 stdout，不能凭空写。

### 生成方法

用 `src/data/gen_expected.py` 自动生成：

```bash
python src/data/gen_expected.py
```

该脚本会：
1. 读取 `python_coding200.json`
2. 对含 `input()` 的题，从题干"参考(…)"解析 `sample_input`
3. 实际运行参考代码，获取 stdout 写入 `expected_output`
4. 写回 JSON

### 格式细节

- stdout 末尾通常带 `\r\n`（Windows 换行），保持原样即可
- 多行输出用 `\n` 分隔
- 中文输出正常写入（判分时用 `-X utf8` 运行，不会乱码）

---

## 四、sample_input 说明

- 参考代码**没有 `input()`**：`sample_input` 填 `""`（空字符串）
- 参考代码**有 `input()`**：`sample_input` 填测试输入（如 `"5"`），判分时通过 stdin 注入

**示例（含 input）：**
```json
{
  "type": "code",
  "topic_name": "数值类型与字符串",
  "content": "输入一个整数，输出它的两倍。",
  "answer": "n = int(input())\nprint(n * 2)",
  "expected_output": "10",
  "sample_input": "5",
  "explanation": "先用 input() 获取输入，转成整数，再乘以2输出。",
  "difficulty": 2
}
```

---

## 五、判分机制（了解即可）

code 题判分流程：
1. **沙箱实跑**学生代码（`core/code_runner.py`，超时 6s，禁止危险模块）
2. **LLM 评星**：对比参考代码与学生代码，给 0-5 星 + 鼓励性反馈
3. **LLM 不可用时降级**：stdout 与 `expected_output` 精确匹配（匹配成功=100）
4. `is_correct = (llm_score >= 60)`，3 星及以上算通过

---

## 六、递进式设计原则

Python 实操题是**递进式**的：第 N 课的题综合运用第 1~N 课学过的知识点。

- `topic_name` 对应 20 个知识点章节（与理论科目相同的章节名）
- 线上 topic id 为 45~64（名称固定，重灌题需保持名称一致以复用）
- `explanation` 里可标注"结合第X课"，提示综合运用了哪些知识点

**20 个章节名**：
```
变量与标识符 / 注释与输出函数 / 数值类型与字符串 / 算术赋值与输入转义
if判断与比较逻辑运算 / if-else与嵌套if / while循环与嵌套循环 / 字符串查找判断修改
列表与列表推导式 / 元组与字典 / 类型转换 / 赋值与深浅拷贝
函数与返回值 / 函数参数与嵌套 / 作用域与匿名函数 / lambda与内置函数
内置函数与拆包 / 异常模块与包 / 闭包与装饰器 / 标准装饰器与语法糖
```

---

## 七、导入命令

```bash
python src/data/import_via_api.py --json src/data/python_coding200.json
```

- 自动按 `content` 去重（重跑不翻倍）
- 发送 `expected_output` 和 `sample_input` 字段
- `subject.name` 必须与线上已有科目名匹配

---

## 八、注意事项

1. **`expected_output` 必须实跑验证**：不能凭空写，用 `gen_expected.py` 生成
2. **`explanation` 不要泄露参考代码**：只写思路，不写完整代码
3. **参考代码要能在沙箱跑通**：不能用 os/subprocess/socket 等被禁模块
4. **中文输出**：参考代码的 print 中文正常，沙箱用 `-X utf8` 运行
5. **`answer` 是字符串**：参考代码用 `\n` 表示换行
6. **不超纲**：面向 3-4 年级（8-10 岁），只用当前章节教过的知识点；不串课、不碰 CPython 底层机制（对象缓存/`is`/双下划线等）、不碰超纲数学/类型（复数/二八十六进制/浮点误差等）、不混真实工程概念；存疑即废弃。细则见 [python_theory.md §〇](python_theory.md)
