"""统一的 LLM 调用客户端：阿里云 Qwen 为主，DeepSeek 为兜底。

设计目标：
1. 先调用阿里云（qwen3.7-plus）；若调用不通（异常 / 超时 / 鉴权失败 / 额度耗尽），
   自动切换到 DeepSeek（deepseek-v4-flash）兜底，保证评分 / 周报等链路不中断。
2. 每一次实际调用（无论哪个 provider、成败）都写入 `llm_calls` 表，并记录结构化日志，
   便于事后追溯「走了哪个模型、消耗多少 token、耗时、成功还是失败、失败原因」。

Key 来源（与阿里云彻底拆开，避免历史坑：DEEPSEEK_API_KEY 被误当 aliyun key）：
- 阿里云：环境变量 LLM_API_KEY，或数据卷文件 /app/data/llm_key.txt
- DeepSeek：环境变量 DEEPSEEK_API_KEY，或数据卷文件 /app/data/deepseek_key.txt

模型名可通过 config 表覆盖（llm_deepseek_model / llm_aliyun_model）。
"""
import os
import time
import logging

logger = logging.getLogger(__name__)

# ── 阿里云（主用）──
ALIYUN_BASE_URL = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
ALIYUN_DEFAULT_MODEL = "qwen3.7-plus"

# ── DeepSeek（兜底）──
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"

DEFAULT_TIMEOUT = 90


def _read_key_from_file(path: str) -> str:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    return ""


def _aliyun_key() -> str:
    return os.getenv("LLM_API_KEY", "") or _read_key_from_file("/app/data/llm_key.txt")


def _deepseek_key() -> str:
    return os.getenv("DEEPSEEK_API_KEY", "") or _read_key_from_file("/app/data/deepseek_key.txt")


def _log_call(scenario, provider, model, usage, status, latency_ms, error=None):
    """将一次调用结果写入 llm_calls 表 + 结构化日志。失败不影响主流程。"""
    prompt_tokens = completion_tokens = total_tokens = None
    if usage is not None:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

    # 结构化日志（便于 grep / 采集）
    logger.info(
        "[LLM_CALL] scenario=%s provider=%s model=%s status=%s "
        "prompt=%s completion=%s total=%s latency_ms=%s%s",
        scenario, provider, model, status,
        prompt_tokens, completion_tokens, total_tokens, latency_ms,
        (f" error={error}" if error else ""),
    )

    # 落库（独立事务，失败静默）
    try:
        from database import SessionLocal
        import models
        db = SessionLocal()
        try:
            db.add(models.LLMCall(
                scenario=scenario,
                provider=provider,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                status=status,
                latency_ms=latency_ms,
                error=(error or "")[:2000] if error else None,
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:  # noqa: BLE001
        logger.warning("写入 llm_calls 失败（已忽略）: %s", e)


def _build_providers() -> list:
    """构造 provider 列表（阿里云优先，DeepSeek 兜底）。"""
    providers = [{
        "name": "aliyun",
        "base_url": ALIYUN_BASE_URL,
        "model": os.getenv("LLM_ALIYUN_MODEL", ALIYUN_DEFAULT_MODEL),
        "key": _aliyun_key(),
    }]
    providers.append({
        "name": "deepseek",
        "base_url": DEEPSEEK_BASE_URL,
        "model": os.getenv("LLM_DEEPSEEK_MODEL", DEEPSEEK_DEFAULT_MODEL),
        "key": _deepseek_key(),
    })
    return providers


def llm_chat(
    messages: list,
    scenario: str = "unknown",
    temperature: float = 0.7,
    max_tokens: int = 800,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """统一的对话补全调用，带兜底与审计日志。

    Args:
        messages: OpenAI 格式的消息列表
        scenario: 调用场景标识（code_grade / weekly_report / ...），用于追溯分类
        temperature / max_tokens / timeout: 透传给模型

    Returns:
        模型返回的文本内容（str）

    Raises:
        若所有 provider 均不可用 / 均失败，抛出异常（由调用方决定降级策略）
    """
    providers = _build_providers()
    last_exc = None
    attempted = False

    for p in providers:
        if not p["key"]:
            logger.info("[LLM_CALL] 跳过 provider=%s（未配置 key）", p["name"])
            continue
        attempted = True
        start = time.time()
        try:
            from openai import OpenAI  # noqa: PLC0415
            client = OpenAI(api_key=p["key"], base_url=p["base_url"], timeout=timeout)
            resp = client.chat.completions.create(
                model=p["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            latency_ms = int((time.time() - start) * 1000)
            usage = getattr(resp, "usage", None)
            _log_call(scenario, p["name"], p["model"], usage, "success", latency_ms)
            return resp.choices[0].message.content
        except Exception as e:  # noqa: BLE001
            latency_ms = int((time.time() - start) * 1000)
            err = str(e)
            logger.warning("[LLM_CALL] provider=%s 调用失败: %s", p["name"], err[:300])
            _log_call(scenario, p["name"], p["model"], None, "failed", latency_ms, error=err)
            last_exc = e
            # 继续尝试下一个 provider（兜底）

    if not attempted:
        raise RuntimeError("无任何可用的 LLM provider（未配置 aliyun / deepseek key）")
    raise last_exc
