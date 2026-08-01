"""受限 Python 代码执行器（用于编程题判分）。

安全策略：
- 用独立临时目录 + `python -I`（隔离模式，忽略用户 site-packages / 环境变量）。
- 仅保留最小环境变量（PATH / LANG / LC_* / TEMP），其余剥离。
- 前置一段「导入守卫」：禁止导入 os / subprocess / socket / sys / shutil 等
  危险模块，避免孩子代码（或误粘贴）对宿主造成破坏。
- 超时保护（默认 6 秒），防止死循环卡死。
- 捕获 stdout / stderr，供判分比对。
"""
import os
import sys
import textwrap
import tempfile
import subprocess

# 禁止导入的模块（首段名匹配即拦截）
# 注意：不要拦截 sys / builtins —— 它们是众多标准库（functools/collections…）
# 内部依赖的基础模块，拦截会连累正常代码跑不起来。
_FORBIDDEN = {
    "os", "subprocess", "socket", "shutil", "pathlib",
    "importlib", "ctypes", "multiprocessing", "signal", "requests",
    "urllib", "pty", "popen",
}

# 注入到用户代码顶部的守卫：覆盖 __import__ 拦截危险模块
_GUARD = textwrap.dedent('''
import builtins as _b
_block = {"os","subprocess","socket","shutil","pathlib",
           "importlib","ctypes","multiprocessing","signal","requests",
           "urllib","pty","popen"}
_real_import = _b.__import__  # 先保存真正的 __import__，否则递归死循环
def _g(name, *a, **k):
    if name.split(".")[0] in _block:
        raise ImportError("该模块被禁止导入：" + name)
    return _real_import(name, *a, **k)
_b.__import__ = _g
''')

# 允许透传的最小环境变量前缀
_ENV_ALLOW = ("PATH", "LANG", "LC_", "TEMP", "TMP")


def _safe_env() -> dict:
    env = {}
    for k, v in os.environ.items():
        if any(k.startswith(p) for p in _ENV_ALLOW):
            env[k] = v
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"  # 保证中文输出不乱码/被吞
    env["LANG"] = "C.UTF-8"
    return env


def run_python(code: str, stdin: str = "", timeout: float = 6.0):
    """运行一段 Python 代码，返回 (stdout, stderr, returncode)。

    - code:    孩子提交的源码字符串
    - stdin:   参考代码里 input() 需要的输入（多行用 \\n 分隔）
    - returncode: 0=正常；-1=超时；-2=运行异常
    """
    guarded = _GUARD + "\n" + (code or "")
    with tempfile.TemporaryDirectory() as td:
        fpath = os.path.join(td, "user_code.py")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(guarded)
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-X", "utf8", fpath],
                input=(stdin or "").encode("utf-8"),
                capture_output=True,
                timeout=timeout,
                cwd=td,
                env=_safe_env(),
            )
            out = proc.stdout.decode("utf-8", "ignore")
            err = proc.stderr.decode("utf-8", "ignore")
            return out, err, proc.returncode
        except subprocess.TimeoutExpired:
            return "", "运行超时（超过 %d 秒），请检查是否有死循环。" % int(timeout), -1
        except Exception as e:  # noqa: BLE001
            return "", "运行出错：%s" % e, -2


def normalize_output(s: str) -> str:
    """把运行输出归一化，便于判分比对：

    - 统一换行符
    - 逐行去除首尾空白
    - 去掉末尾空白行
    - 不区分大小写（Python 输出多为数字/英文，大小写差异通常是笔误）
    """
    if not s:
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in s.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).lower()
