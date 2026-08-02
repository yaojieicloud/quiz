# -*- coding: utf-8 -*-
"""英语课时整理：删空课时骨架 + 按课时名确定上下册加前缀"""
import urllib.request, urllib.error, json, sys

BASE = "http://106.14.99.100:8000"

# 人教版 PEP 三年级英语标准单元主题 → 册次
VOL1_NAMES = {"Hello!", "Colours!", "Look at me!", "We love animals", "Let's eat!", "Happy birthday!"}
VOL2_NAMES = {"Welcome back to school!", "My family", "At the zoo",
              "Where is my car?", "Do you like pears?", "How many?"}


def http(method, url, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
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


def main():
    st, res = http("POST", f"{BASE}/api/auth/login", data={"username": "admin", "password": "admin123"})
    tok = res["access_token"]
    print("[登录] 成功")

    st, topics = http("GET", f"{BASE}/api/subjects/5/topics", token=tok)

    # 1) 删空课时骨架（unit=三年级上册 且 0 题）
    skeletons = [t for t in topics if t.get("unit") == "三年级上册" and t.get("question_count", 0) == 0]
    deleted = 0
    for t in skeletons:
        st2, r2 = http("DELETE", f"{BASE}/api/topics/{t['id']}", token=tok)
        if st2 == 200:
            deleted += 1
    print(f"[清理] 删除空课时骨架 {deleted}/{len(skeletons)}")

    # 2) 给真实课时加上下册前缀
    up, down, unknown = 0, 0, []
    for t in topics:
        unit = t.get("unit") or ""
        if not unit.startswith("Unit"):
            continue
        name = t["name"]
        if name in VOL1_NAMES:
            new_unit = f"上册-{unit}"
        elif name in VOL2_NAMES:
            new_unit = f"下册-{unit}"
        else:
            unknown.append(name)
            continue
        st2, r2 = http("PUT", f"{BASE}/api/topics/{t['id']}", token=tok, data={"unit": new_unit})
        if st2 == 200:
            if name in VOL1_NAMES:
                up += 1
            else:
                down += 1
            print(f"  「{name}」: {unit} -> {new_unit}")
        else:
            print(f"  [警告] 改「{name}」失败 HTTP {st2}: {r2}")
    print(f"[改名] 上册 {up} 个, 下册 {down} 个")
    if unknown:
        print(f"[警告] 未识别课时: {unknown}")

    # 3) 验证
    st, topics2 = http("GET", f"{BASE}/api/subjects/5/topics", token=tok)
    by_unit = {}
    for t in topics2:
        by_unit.setdefault(t.get("unit"), []).append((t["name"], t.get("question_count", 0)))
    total_q = 0
    print("\n[最终结构] 英语学科:")
    for unit in sorted(by_unit.keys(), key=lambda x: str(x)):
        lst = by_unit[unit]
        qsum = sum(c for _, c in lst)
        total_q += qsum
        print(f"  [{unit}] {len(lst)} 课时 / {qsum} 题: {[n for n, _ in lst]}")
    print(f"  课时总数: {len(topics2)} | 题目总数: {total_q}")


if __name__ == "__main__":
    main()
