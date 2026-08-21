"""
批量导入题目到线上库（只读/写操作：会真实写入生产库）。

用法：
    .venv/Scripts/python.exe scripts/quiz_import_batch.py <json_path> [--dry]

- json_path：包含 list[QuestionCreate] 的 JSON 文件
- --dry：只做本地校验与统计，不调用 API

QuestionCreate 必填：subject_id, topic_id, type, content, answer
可选：options, match_options, reading_items, explanation, difficulty(默认1),
      tier(默认1), is_multiple(默认False), blank_count(默认1),
      blank_answers, tolerance, expected_output, sample_input
type ∈ {choice, judge, fill, essay, code, match, sort, reading}
"""
import sys
import json
import argparse
import requests

BASE = "http://106.14.99.100:8000"
ADMIN = {"username": "admin", "password": "admin123"}

VALID_TYPES = {"choice", "judge", "fill", "essay", "code", "match", "sort", "reading"}


def login():
    r = requests.post(BASE + "/api/auth/login", json=ADMIN, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def normalize(items):
    """填空题多空题若漏写顶层 answer，则从 blank_answers 逗号拼接补全
    （与前端 admin.html:1153 约定一致：answer = 各空答案拼接）。"""
    for it in items:
        if not isinstance(it, dict):
            continue
        if it.get("type") == "fill" and it.get("blank_answers") and not it.get("answer"):
            it["answer"] = ",".join(str(x) for x in it["blank_answers"])


def validate(items):
    errors = []
    types_count = {}
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            errors.append(f"[{i}] 不是对象")
            continue
        for f in ("subject_id", "topic_id", "type", "content", "answer"):
            if f not in it or it[f] in (None, ""):
                errors.append(f"[{i}] 缺少必填字段 {f}")
        t = it.get("type")
        if t and t not in VALID_TYPES:
            errors.append(f"[{i}] 非法 type={t!r}")
        if t:
            types_count[t] = types_count.get(t, 0) + 1
    return errors, types_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    with open(args.json_path, encoding="utf-8") as f:
        items = json.load(f)
    assert isinstance(items, list), "JSON 顶层必须是数组"

    normalize(items)  # 多空填空自动补全 answer
    errors, types_count = validate(items)
    print(f"共 {len(items)} 题，题型分布: {types_count}")
    if errors:
        print("校验错误:")
        for e in errors[:50]:
            print("  -", e)
        if not args.dry:
            sys.exit(1)
    if args.dry:
        print("[dry] 仅校验，未写入。")
        return

    tok = login()
    h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    r = requests.post(BASE + "/api/questions/batch", json=items, headers=h, timeout=120)
    print("HTTP", r.status_code, r.text[:300])
    r.raise_for_status()
    print("已创建:", r.json().get("created"))


if __name__ == "__main__":
    main()
