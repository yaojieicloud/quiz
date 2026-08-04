# -*- coding: utf-8 -*-
"""
PC Monitor 数据查询工具
用法:
  python query_monitor.py --from "2026-08-03 13:00" --to "2026-08-03 14:00"
  python query_monitor.py --from "2026-08-03 13:00"            # to 默认当前时间
  python query_monitor.py --alerts                              # 列出所有告警
  python query_monitor.py --snapshot alert_20260803_131235.json # 查看指定快照
  python query_monitor.py --status                              # 服务与磁盘状态
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(os.environ.get("PCMONITOR_HOME", str(Path(os.environ["LOCALAPPDATA"]) / "PCMonitor")))
METRICS = BASE / "logs" / "metrics.csv"
ALERTS = BASE / "logs" / "alerts.log"
SNAP_DIR = BASE / "snapshots"
SERVICE_LOG = BASE / "logs" / "service.log"

COLS = ["cpu_pct", "cpu_temp", "mem_pct", "mem_used_mb", "disk_pct",
        "gpu_temp", "gpu_pct", "gpu_mem_used_mb", "net_sent_mb", "net_recv_mb", "proc_count"]


def parse_ts(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m-%d %H:%M", "%H:%M"):
        try:
            d = datetime.strptime(s, fmt)
            if d.year == 1900:
                now = datetime.now()
                d = d.replace(year=now.year, month=now.month, day=now.day)
            return d
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {s}")


def load_metrics(start=None, end=None):
    rows = []
    if not METRICS.exists():
        return rows
    with open(METRICS, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                ts = datetime.strptime(row["ts"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, KeyError):
                continue
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            rows.append((ts, row))
    return rows


def summarize(rows):
    if not rows:
        print("该时间段无数据。")
        return
    n = len(rows)
    span = (rows[-1][0] - rows[0][0]).total_seconds()
    print(f"时间段: {rows[0][0]} ~ {rows[-1][0]}  样本数: {n}  覆盖: {span/60:.1f} 分钟")
    print()
    header = f"{'指标':<14}{'最小':>10}{'平均':>10}{'最大':>10}"
    print(header)
    print("-" * len(header))
    for col in COLS:
        vals = []
        for _, r in rows:
            try:
                v = r.get(col)
                if v not in (None, "", "None"):
                    vals.append(float(v))
            except (ValueError, TypeError):
                pass
        if vals:
            print(f"{col:<14}{min(vals):>10.1f}{sum(vals)/len(vals):>10.1f}{max(vals):>10.1f}")
        else:
            print(f"{col:<14}{'无数据':>10}")
    # 采样间隔检测(断电/服务中断线索)
    gaps = []
    for i in range(1, len(rows)):
        delta = (rows[i][0] - rows[i-1][0]).total_seconds()
        if delta > 60:
            gaps.append((rows[i-1][0], rows[i][0], delta))
    if gaps:
        print()
        print("检测到采样中断(可能关机/休眠/服务停止):")
        for a, b, d in gaps[:10]:
            print(f"  {a} -> {b}  中断 {d/60:.1f} 分钟")


def show_samples(rows, limit=20):
    if not rows:
        return
    step = max(1, len(rows) // limit)
    print()
    print(f"抽样明细(每 {step} 条取 1):")
    print(f"{'时间':<20}{'CPU%':>7}{'内存%':>7}{'磁盘%':>7}{'GPU温':>7}{'GPU%':>7}{'进程数':>7}")
    for i in range(0, len(rows), step):
        ts, r = rows[i]
        print(f"{str(ts):<20}{r['cpu_pct']:>7}{r['mem_pct']:>7}{r['disk_pct']:>7}"
              f"{(r['gpu_temp'] or '-'):>7}{r['gpu_pct']:>7}{r['proc_count']:>7}")


def list_alerts():
    if not ALERTS.exists():
        print("无告警日志文件。")
        return
    lines = ALERTS.read_text(encoding="utf-8").splitlines()
    alerts = [l for l in lines if "ALERT" in l]
    if not alerts:
        print("无告警记录。")
        return
    print(f"共 {len(alerts)} 条告警:")
    for l in alerts:
        print(l)


def show_snapshot(name):
    path = SNAP_DIR / name if not name.endswith(".json") else SNAP_DIR / name
    if not path.exists():
        candidates = sorted(SNAP_DIR.glob("*.json"))
        print(f"未找到 {path.name}。可用快照:")
        for c in candidates[-20:]:
            print(f"  {c.name}")
        return
    snap = json.loads(path.read_text(encoding="utf-8"))
    print(f"触发时间: {snap.get('trigger_time')}")
    print(f"告警项: {'; '.join(snap.get('alerts', []))}")
    cur = snap.get("current", {})
    print(f"当前指标: CPU {cur.get('cpu_pct')}% | 内存 {cur.get('mem_pct')}% | "
          f"磁盘 {cur.get('disk_pct')}% | GPU温 {cur.get('gpu_temp')}")
    procs = snap.get("processes", {})
    print("\nCPU Top10:")
    for p in procs.get("by_cpu", [])[:10]:
        print(f"  {p['name']:<30} CPU {p['cpu_pct']:>6}%  MEM {p['mem_mb']:>8}MB")
    print("\n内存 Top10:")
    for p in procs.get("by_mem", [])[:10]:
        print(f"  {p['name']:<30} MEM {p['mem_mb']:>8}MB  CPU {p['cpu_pct']:>6}%")
    hist = snap.get("history", [])
    print(f"\n前置历史样本数: {len(hist)}")


def status():
    print(f"部署目录: {BASE}")
    for name, p in [("metrics.csv", METRICS), ("alerts.log", ALERTS), ("service.log", SERVICE_LOG)]:
        if p.exists():
            size_mb = p.stat().st_size / 1048576
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            print(f"{name}: {size_mb:.2f} MB, 最后写入 {mtime}")
        else:
            print(f"{name}: 不存在")
    snaps = sorted(SNAP_DIR.glob("*.json")) if SNAP_DIR.exists() else []
    print(f"快照数量: {len(snaps)}")
    # 服务进程检查
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq pythonw.exe"],
                             capture_output=True, text=True, timeout=5)
        running = "pythonw.exe" in out.stdout
        print(f"监控进程(pythonw): {'运行中' if running else '未检测到!'}")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", help="起始时间")
    ap.add_argument("--to", help="结束时间")
    ap.add_argument("--alerts", action="store_true", help="列出所有告警")
    ap.add_argument("--snapshot", help="查看指定快照文件")
    ap.add_argument("--status", action="store_true", help="服务与数据状态")
    ap.add_argument("--detail", action="store_true", help="附带抽样明细")
    args = ap.parse_args()

    if args.status:
        status()
        return
    if args.alerts:
        list_alerts()
        return
    if args.snapshot:
        show_snapshot(args.snapshot)
        return

    start = parse_ts(args.frm) if args.frm else None
    end = parse_ts(args.to) if args.to else datetime.now()
    if start is None:
        print("请指定 --from 时间, 或使用 --alerts / --status / --snapshot")
        sys.exit(1)
    rows = load_metrics(start, end)
    summarize(rows)
    if args.detail:
        show_samples(rows)


if __name__ == "__main__":
    main()
