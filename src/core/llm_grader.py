"""LLM 代码评分模块：调用 DeepSeek API 对编程题做星级评分与个性化反馈。

降级策略：若 openai 库不可用 / API Key 未配置 / API 超时 / 返回格式异常，
自动返回 fallback 标记，由调用方（exam.py）回退到 stdout 精确匹配的二元判分。
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# ── API Key：优先环境变量，其次数据卷文件 ──
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
if not DEEPSEEK_API_KEY:
    _key_file = "/app/data/deepseek_key.txt"
    try:
        if os.path.exists(_key_file):
            with open(_key_file, "r", encoding="utf-8") as f:
                DEEPSEEK_API_KEY = f.read().strip()
    except Exception:
        pass

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"

# ── 系统提示词 ──
SYSTEM_PROMPT = """你是一位 Python 编程老师，正在批改一位 10 岁小学生的 Python 练习题。
你的职责是：根据题目要求和学员提交的代码，给出星级评价和鼓励性反馈。

## 评分标准（五级阶梯制）

★★★★★ 5星：代码正确执行，输出完全符合预期，且写法清晰易懂（缩进规范、变量命名有意义）。
★★★★☆ 4星：代码能正确执行，输出符合预期，但写法有改进空间（如变量名无意义、有重复代码未简化）。
★★★☆☆ 3星：代码思路大体正确，但存在小错误导致部分输出不符预期，或漏了某个边界情况。
★★☆☆☆ 2星：代码涉及了正确方向（用到了要考查的知识点），但核心逻辑有误，无法正确运行。
★☆☆☆☆ 1星：代码与题目要求基本无关，或语法错误严重到无法判断思路。
☆ 0星：未提交任何有效代码。

## 反馈要求
- 用温和、鼓励的语气，像老师跟学生谈心一样
- 先肯定做得好的地方，再指出可以改进的地方
- 不要使用"你错了""不对"等否定表达，改用"可以试试""还有一个地方需要注意"
- 控制在 3-5 句话以内
- 必须用中文
- 如果代码能运行但输出不符预期，要在反馈里对比"运行结果"和"期望结果"

## 输出格式（严格遵守，不要输出任何其他内容）
请只返回一个 JSON 对象，格式如下：
{"stars": 数字, "score": 数字, "feedback": "评语"}

注意：
- stars 的值必须是 0 到 5 的整数
- score 对应关系：5星=100, 4星=80, 3星=60, 2星=30, 1星=10, 0星=0
- feedback 不要包含双引号，不要换行，用中文逗号句号即可"""


def grade_code(
    question_content: str,
    expected_output: str,
    user_code: str,
    run_result: str,
) -> dict:
    """调用 DeepSeek API 对编程题作答进行评分。

    Args:
        question_content: 题目要求（题干）
        expected_output: 期望输出（预设正确答案）
        user_code: 学员提交的代码
        run_result: 后台实跑结果（stdout + stderr）

    Returns:
        {"stars": int, "score": int, "feedback": str}
        若 LLM 不可用，返回 {"stars": -1, "score": -1, "feedback": ""} 表示需降级
    """
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY 未配置，跳过 LLM 评分")
        return _fallback()

    try:
        from openai import OpenAI  # noqa: PLC0415
    except ImportError:
        logger.warning("openai 库未安装，跳过 LLM 评分")
        return _fallback()

    user_prompt = f"""题目要求：
{question_content}

期望输出：
{expected_output or '(无预设期望输出)'}

学员提交的代码：
```
{user_code or '(未提交代码)'}
```

代码运行结果：
{run_result or '(无运行结果)'}

请根据以上信息给出评分。"""

    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=300,
            timeout=15,
        )
        raw = response.choices[0].message.content.strip()

        # 提取 JSON（处理可能的 markdown 代码块包裹）
        if raw.startswith("```"):
            lines = raw.split("\n")
            # 去掉第一行 ```json 或 ```
            raw = "\n".join(lines[1:])
            if raw.rstrip().endswith("```"):
                raw = raw.rstrip()[:-3]
        raw = raw.strip()

        result = json.loads(raw)
        stars = int(result.get("stars", -1))
        score = int(result.get("score", -1))
        feedback = str(result.get("feedback", ""))

        # 合法性校验
        if stars < 0 or stars > 5 or score < 0 or score > 100:
            logger.warning(
                "LLM 返回的评分不合法: stars=%d score=%d raw=%s", stars, score, raw[:200]
            )
            return _fallback()

        logger.info("LLM 评分完成: stars=%d score=%d", stars, score)
        return {"stars": stars, "score": score, "feedback": feedback}

    except json.JSONDecodeError:
        logger.warning("LLM 返回格式无法解析: %s", raw[:200] if "raw" in dir() else "(无输出)")
        return _fallback()
    except Exception:
        logger.exception("LLM 评分异常")
        return _fallback()


def _fallback() -> dict:
    """降级标记，由调用方回退到原有判分逻辑。"""
    return {"stars": -1, "score": -1, "feedback": ""}
