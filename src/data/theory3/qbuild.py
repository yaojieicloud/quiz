"""题目生成 + 自校验框架（Python 基础理论）。

设计目标：把"人工复核"变成可执行的自动化检查，确保每题正确性。
- choice/judge：用 `_check`（正确项文本）回查 answer 索引，杜绝索引标错。
- calc：实际 exec(content) 捕获 stdout 作为答案，杜绝手算错。
- match：左右两侧文本必须唯一；用 `_pairs`（正确的 [左索引,右索引] 列表）核对 answer 映射。

导出时自动剥离 _check / _pairs 等锚点，生成符合 import_via_api 风格的干净 JSON。
"""

import io
import contextlib
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

SHORT_TYPE = {"choice": "选", "judge": "判", "calc": "算", "match": "连"}


def run_calc(content: str) -> str:
    """执行 calc 题干里的 Python 代码，返回 stdout（去掉末尾换行）。"""
    buf = io.StringIO()
    g = {}
    try:
        with contextlib.redirect_stdout(buf):
            exec(content, g, g)
    except Exception as e:  # 代码本身报错 -> 这是题干设计问题
        raise RuntimeError(f"calc 代码执行异常: {e}\n代码:\n{content}") from e
    return buf.getvalue().rstrip("\n")


def _parse_match_answer(answer: str):
    pairs = []
    if answer.strip():
        for part in answer.split(","):
            part = part.strip()
            if not part:
                continue
            l, r = part.split(":")
            pairs.append((int(l.strip()), int(r.strip())))
    return pairs


def validate(q, idx, errors):
    """校验单题，把问题追加到 errors（带题号）。返回 None。"""
    tag = f"[{SHORT_TYPE.get(q['type'], q['type'])}#{idx}]"
    t = q["type"]
    # calc 题 answer 可留空（由 run_calc 自动补全），其余题型 answer 必填
    need = ["type", "topic_name", "content"]
    if t != "calc":
        need.append("answer")
    for f in need:
        if f not in q or q[f] in (None, ""):
            errors.append(f"{tag} 缺必填字段 {f}")
    if "difficulty" not in q:
        errors.append(f"{tag} 缺 difficulty")

    if t == "choice":
        opts = q.get("options")
        if not isinstance(opts, list) or len(opts) != 4:
            errors.append(f"{tag} choice 必须 4 个选项，实际 {len(opts) if opts else 0}")
        else:
            for i, o in enumerate(opts):
                if not isinstance(o, str) or o == "":
                    errors.append(f"{tag} 选项[{i}] 为空或非字符串")
            try:
                ai = int(q["answer"])
            except Exception:
                errors.append(f"{tag} answer 不是可解析索引: {q['answer']!r}")
                return
            if not (0 <= ai < len(opts)):
                errors.append(f"{tag} answer 索引 {ai} 越界")
                return
            if "_check" in q and opts[ai] != q["_check"]:
                errors.append(
                    f"{tag} answer 指向「{opts[ai]}」，但锚定正确项应为「{q['_check']}」"
                )

    elif t == "judge":
        opts = q.get("options")
        if opts != ["对", "错"]:
            errors.append(f"{tag} judge 选项必须为 ['对','错']，实际 {opts}")
        if q["answer"] not in ("0", "1"):
            errors.append(f"{tag} judge answer 必须是 '0'/'1'，实际 {q['answer']!r}")
        else:
            picked = opts[int(q["answer"])]
            if "_check" in q and picked != q["_check"]:
                errors.append(
                    f"{tag} answer 指向「{picked}」，但锚定正确项应为「{q['_check']}」"
                )

    elif t == "calc":
        if q.get("options") is not None:
            errors.append(f"{tag} calc 的 options 必须为 null")
        try:
            out = run_calc(q["content"])
        except Exception as e:
            errors.append(f"{tag} {e}")
            return
        # calc 答案由执行结果决定；若文件已写 answer 则核对一致
        if q.get("answer") not in (None, ""):
            if out != q["answer"]:
                errors.append(
                    f"{tag} calc 答案不一致：执行得「{out}」但文件写「{q['answer']}」"
                )
        else:
            q["answer"] = out  # 自动补全答案

    elif t == "match":
        opts = q.get("options")
        mopts = q.get("match_options")
        if not isinstance(opts, list) or not opts:
            errors.append(f"{tag} match 左侧 options 非法")
        if not isinstance(mopts, list) or not mopts:
            errors.append(f"{tag} match 右侧 match_options 非法/缺失")
        if isinstance(opts, list):
            if len(set(opts)) != len(opts):
                errors.append(f"{tag} match 左侧选项文本重复: {opts}")
        if isinstance(mopts, list):
            if len(set(mopts)) != len(mopts):
                errors.append(f"{tag} match 右侧选项文本重复: {mopts}")
        if isinstance(opts, list) and isinstance(mopts, list):
            try:
                pairs = _parse_match_answer(q["answer"])
            except Exception:
                errors.append(f"{tag} match answer 格式错误: {q['answer']!r}")
                return
            n = len(opts)
            m = len(mopts)
            for (l, r) in pairs:
                if not (0 <= l < n):
                    errors.append(f"{tag} match 左索引 {l} 越界(0~{n-1})")
                if not (0 <= r < m):
                    errors.append(f"{tag} match 右索引 {r} 越界(0~{m-1})")
            # 锚定核对：_pairs 是期望的 [l,r] 列表
            if "_pairs" in q:
                exp = [tuple(p) for p in q["_pairs"]]
                if set(pairs) != set(exp):
                    errors.append(
                        f"{tag} match answer {pairs} 与锚定期望 {exp} 不一致"
                    )
    else:
        errors.append(f"{tag} 未知题型 {t}")


def validate_all(questions, topic_name):
    errors = []
    seen = {}
    for i, q in enumerate(questions, 1):
        validate(q, i, errors)
        c = (q.get("content") or "").strip()
        if c in seen:
            errors.append(f"[#{i}] 与 #{seen[c]} 题干重复: {c[:30]}")
        else:
            seen[c] = i
    return errors


def export_clean(questions, subject_name, icon, grade, desc, path: Path):
    out = {
        "subject": {"name": subject_name, "icon": icon, "grade": grade, "desc": desc},
        "questions": [],
    }
    for q in questions:
        item = {
            "type": q["type"],
            "topic_name": q["topic_name"],
            "content": q["content"],
            "options": q.get("options"),
            "answer": str(q["answer"]),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", 1),
        }
        if q["type"] == "match":
            item["match_options"] = q.get("match_options")
        # 剥离锚点
        for k in ("_check", "_pairs"):
            item.pop(k, None)
        out["questions"].append(item)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ---------------- 推送 ECS（自写，补全 match_options）----------------

def http(method, url, token=None, data=None, timeout=60):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        try:
            detail = json.loads(detail).get("detail", detail)
        except Exception:
            pass
        return e.code, detail
    except Exception as e:
        return None, str(e)


def import_to_ecs(json_path: Path, url="http://106.14.99.100:8000", user="admin", pw="admin123"):
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    subject_name = payload["subject"]["name"]
    questions = payload["questions"]
    base = url.rstrip("/")
    st, res = http("POST", f"{base}/api/auth/login", data={"username": user, "password": pw})
    if st != 200 or "access_token" not in res:
        print(f"[错误] 登录失败 HTTP {st}: {res}")
        return False
    token = res["access_token"]
    st, subs = http("GET", f"{base}/api/subjects", token=token)
    subject_id = next((s["id"] for s in subs if s["name"] == subject_name), None)
    if not subject_id:
        print(f"[错误] 找不到科目 {subject_name}")
        return False
    st, topics = http("GET", f"{base}/api/subjects/{subject_id}/topics", token=token)
    topic_map = {t["name"]: t["id"] for t in topics}
    st, exist = http("GET", f"{base}/api/questions?subject_id={subject_id}", token=token)
    existing = set((q.get("content") or "").strip() for q in exist) if st == 200 else set()

    items, skipped = [], 0
    for q in questions:
        c = (q.get("content") or "").strip()
        if c in existing:
            skipped += 1
            continue
        existing.add(c)  # 运行内去重，防止同批多文件间重复导入
        tname = q["topic_name"]
        if tname not in topic_map:
            st, t = http("POST", f"{base}/api/topics", token=token,
                         data={"subject_id": subject_id, "name": tname, "unit": None})
            if st != 200:
                print(f"[警告] 章节创建失败 {tname}: {t}")
                continue
            topic_map[tname] = t["id"]
        items.append({
            "subject_id": subject_id,
            "topic_id": topic_map[tname],
            "type": q["type"],
            "content": q["content"],
            "options": q.get("options"),
            "match_options": q.get("match_options"),
            "answer": str(q["answer"]),
            "explanation": q.get("explanation", ""),
            "difficulty": q.get("difficulty", 1),
            "expected_output": None,
            "sample_input": "",
        })
    st, res = http("POST", f"{base}/api/questions/batch", token=token, data=items)
    if st == 200:
        print(f"[完成] 新增 {res.get('created')} 题（跳过重复 {skipped}）")
        return True
    print(f"[错误] 批量导入失败 HTTP {st}: {res}")
    return False


if __name__ == "__main__":
    print("qbuild 框架：被各 gen_*.py 导入使用，不直接运行。")
