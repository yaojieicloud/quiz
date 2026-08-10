"""连线题治理脚本（可重复执行 / 幂等）。

针对"左右选项不得重复"规则：
1. 未做过的连线题（answer_records 中无记录）：合并右侧重复选项（保留首次出现），
   并重排 answer 索引，使 match_options 内文本唯一、语义无损。
2. 已做过的连线题（answer_records 中有记录）：仅标记 deprecated=1，
   不改动 options/answer，以保证历史答题记录展示与现在完全一致。

用法：python3 apply_match_cleanup.py <db_path>
"""
import sqlite3
import json
import sys


def collapse_right(L, R, answer):
    """合并右侧重复文本（保留首次出现顺序），返回 (new_R, new_answer)。"""
    seen = {}
    new_R = []
    for i, txt in enumerate(R):
        if txt not in seen:
            seen[txt] = len(new_R)
            new_R.append(txt)
    # 旧右索引 -> 新右索引
    remap = {i: seen[txt] for i, txt in enumerate(R)}
    new_pairs = []
    for part in answer.split(","):
        if ":" not in part:
            continue
        li, ri = part.split(":", 1)
        try:
            li_i, ri_i = int(li), int(ri)
        except ValueError:
            continue
        new_pairs.append(f"{li_i}:{remap[ri_i]}")
    return new_R, ",".join(new_pairs)


def collapse_left(L, R, answer):
    """合并左侧重复文本（保留首次出现顺序），返回 (new_L, new_answer)。"""
    seen = {}
    new_L = []
    for i, txt in enumerate(L):
        if txt not in seen:
            seen[txt] = len(new_L)
            new_L.append(txt)
    remap = {i: seen[txt] for i, txt in enumerate(L)}
    new_pairs = []
    for part in answer.split(","):
        if ":" not in part:
            continue
        li, ri = part.split(":", 1)
        try:
            li_i, ri_i = int(li), int(ri)
        except ValueError:
            continue
        new_pairs.append(f"{remap[li_i]}:{ri_i}")
    return new_L, ",".join(new_pairs)


def main(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # 1) 加 deprecated 列（幂等）
    cols = [r[1] for r in cur.execute("PRAGMA table_info(questions)")]
    if "deprecated" not in cols:
        cur.execute("ALTER TABLE questions ADD COLUMN deprecated INTEGER NOT NULL DEFAULT 0")
        con.commit()
        print("[schema] 已新增 deprecated 列")
    else:
        print("[schema] deprecated 列已存在，跳过")

    # 取所有连线题 + 是否做过
    cur.execute(
        """SELECT q.id, q.options, q.match_options, q.answer,
                  (SELECT 1 FROM answer_records ar WHERE ar.question_id=q.id LIMIT 1) AS is_done
           FROM questions q WHERE q.type='match'"""
    )
    rows = cur.fetchall()

    reprocessed, deprecated, skipped = 0, 0, 0
    for r in rows:
        qid = r["id"]
        L = json.loads(r["options"]) if r["options"] else []
        R = json.loads(r["match_options"]) if r["match_options"] else []
        answer = r["answer"] or ""
        dupL = len(L) != len(set(L))
        dupR = len(R) != len(set(R))
        if not (dupL or dupR):
            continue

        if r["is_done"]:
            # 已做过：仅标记弃用，不改选项/答案
            cur.execute("UPDATE questions SET deprecated=1 WHERE id=?", (qid,))
            deprecated += 1
            print(f"[deprecate] Q{qid} (已做过，标记弃用；保留选项与答案)")
        else:
            # 未做过：合并重复项并修正答案索引
            new_L, new_R, new_answer = L, R, answer
            if dupR:
                new_R, new_answer = collapse_right(L, R, answer)
            if dupL:
                # 当前数据左侧无重复；保留通用处理以防万一
                new_L, new_answer = collapse_left(L, R, answer)
                # 若同时发生两侧合并，需二次重排右索引（此处数据不会发生，简单告警）
                if dupR:
                    print(f"[warn] Q{qid} 左右同时重复，请人工复核")
                    skipped += 1
                    continue
            cur.execute(
                "UPDATE questions SET options=?, match_options=?, answer=? WHERE id=?",
                (json.dumps(new_L, ensure_ascii=False),
                 json.dumps(new_R, ensure_ascii=False),
                 new_answer, qid),
            )
            reprocessed += 1
            print(f"[reprocess] Q{qid} | R {len(R)}->{len(new_R)} | answer={new_answer}")

    con.commit()

    # 校验：治理后不应再有重复选项的"未做过"连线题
    cur.execute(
        """SELECT q.id FROM questions q
           WHERE q.type='match'
             AND (SELECT 1 FROM answer_records ar WHERE ar.question_id=q.id LIMIT 1) IS NULL"""
    )
    undone_ids = [row["id"] for row in cur.fetchall()]
    still_dup = 0
    for qid in undone_ids:
        cur.execute("SELECT options, match_options FROM questions WHERE id=?", (qid,))
        rr = cur.fetchone()
        L = json.loads(rr["options"]) if rr["options"] else []
        R = json.loads(rr["match_options"]) if rr["match_options"] else []
        if len(L) != len(set(L)) or len(R) != len(set(R)):
            still_dup += 1
            print(f"[CHECK FAIL] Q{qid} 治理后仍有重复")
    con.close()
    print(f"\n=== 完成 === reprocessed={reprocessed} deprecated={deprecated} skipped={skipped} 未做重复残留={still_dup}")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "quiz.db"
    main(db)
