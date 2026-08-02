# -*- coding: utf-8 -*-
"""语文课时整理：备份 -> 删空课时骨架 -> vol1 单元加"上册-"前缀"""
import urllib.request, urllib.error, json, sys

BASE = "http://106.14.99.100:8000"


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
    # 登录
    st, res = http("POST", f"{BASE}/api/auth/login", data={"username": "admin", "password": "admin123"})
    if st != 200:
        print(f"[错误] 登录失败 HTTP {st}: {res}")
        sys.exit(1)
    tok = res["access_token"]
    print("[登录] 成功")

    # 1) 备份数据库
    st, res = http("POST", f"{BASE}/api/admin/backup-db", token=tok, data={})
    if st == 200:
        print(f"[备份] 成功: {res.get('name')} ({res.get('size')} bytes)")
    else:
        print(f"[警告] 备份失败 HTTP {st}: {res}，但继续（exec-sql 接口本身也会备份）")

    # 2) 取语文学科(id=4)全部课时
    st, topics = http("GET", f"{BASE}/api/subjects/4/topics", token=tok)
    if st != 200:
        print(f"[错误] 取课时失败 HTTP {st}: {topics}")
        sys.exit(1)

    # 分类：空骨架(unit=三年级上册且0题) / vol1课时(unit=第X单元)
    empty_skeleton = [t for t in topics if t.get("unit") == "三年级上册" and t.get("question_count", 0) == 0]
    vol1_topics = [t for t in topics if (t.get("unit") or "").startswith("第") and (t.get("unit") or "").endswith("单元")]
    print(f"[分析] 空课时骨架 {len(empty_skeleton)} 个, vol1 课文课时 {len(vol1_topics)} 个")

    # 3) 删除空课时骨架
    deleted = 0
    for t in empty_skeleton:
        st, res = http("DELETE", f"{BASE}/api/topics/{t['id']}", token=tok)
        if st == 200:
            deleted += 1
        else:
            print(f"  [警告] 删课时「{t['name']}」(id={t['id']}) 失败 HTTP {st}: {res}")
    print(f"[清理] 删除空课时骨架 {deleted}/{len(empty_skeleton)}")

    # 4) vol1 单元改名: 第X单元 -> 上册-第X单元
    renamed = 0
    for t in vol1_topics:
        new_unit = f"上册-{t['unit']}"
        st, res = http("PUT", f"{BASE}/api/topics/{t['id']}", token=tok, data={"unit": new_unit})
        if st == 200:
            renamed += 1
            print(f"  课时「{t['name']}」: {t['unit']} -> {new_unit}")
        else:
            print(f"  [警告] 改课时「{t['name']}」单元失败 HTTP {st}: {res}")
    print(f"[改名] vol1 单元加前缀 {renamed}/{len(vol1_topics)}")

    # 5) 验证最终结构
    st, topics2 = http("GET", f"{BASE}/api/subjects/4/topics", token=tok)
    by_unit = {}
    for t in topics2:
        by_unit.setdefault(t.get("unit"), []).append(t["name"])
    print("\n[最终结构] 语文学科课时分组:")
    for unit in sorted(by_unit.keys(), key=lambda x: str(x)):
        print(f"  [{unit}] {len(by_unit[unit])} 课时: {by_unit[unit]}")


if __name__ == "__main__":
    main()
