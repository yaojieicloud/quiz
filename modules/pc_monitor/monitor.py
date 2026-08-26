# -*- coding: utf-8 -*-
"""
PC Monitor - 系统监控服务
采集: CPU/内存/硬盘/进程/显卡(NVIDIA)/CPU温度(LibreHardwareMonitor)
异常时抓取完整现场快照 + PushPlus 微信推送
"""
import json
import os
import sys
import csv
import time
import ctypes
import subprocess
import logging
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path

import psutil
import requests

# ---------- 路径与配置 ----------
BASE_DIR = Path(os.environ.get("PCMONITOR_HOME", str(Path(os.environ["LOCALAPPDATA"]) / "PCMonitor")))
LOG_DIR = BASE_DIR / "logs"
SNAP_DIR = BASE_DIR / "snapshots"
CONFIG_FILE = BASE_DIR / "config.json"
TEMP_READER = BASE_DIR / "tools" / "TempReader" / "publish" / "TempReader.exe"
ACK_FILE = LOG_DIR / "alerts_ack_marker"

DEFAULT_CONFIG = {
    "interval": 5,
    "thresholds": {
        "cpu_temp": 85,
        "gpu_temp": 85,
        "cpu_percent": 90,
        "mem_percent": 90,
        "disk_percent": 90
    },
    "alert_cooldown": 300,  # 已弃用(保留兼容), 事件制状态机见 alert_sustain_minutes / recover_debounce_samples
    "alert_sustain_minutes": 30,      # 异常持续期间, 每隔多少分钟推一次提醒
    "recover_debounce_samples": 6,    # 连续多少次采样正常才确认恢复(防阈值抖动刷屏)
    "log_retention_days": 30,
    "snapshot_window": 200,
    "pushplus_token": "",
    "temp_reader_timeout": 20
}


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            user_cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            for k, v in user_cfg.items():
                if isinstance(cfg.get(k), dict) and isinstance(v, dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except Exception:
            pass
    else:
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg


CFG = load_config()
LOG_DIR.mkdir(parents=True, exist_ok=True)
SNAP_DIR.mkdir(parents=True, exist_ok=True)

# Windows 下子进程静默标志: 防止 pythonw 无控制台时为子进程弹出终端窗口
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

# ---------- 日志 ----------
logger = logging.getLogger("pcmonitor")
logger.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

svc_handler = logging.FileHandler(LOG_DIR / "service.log", encoding="utf-8")
svc_handler.setFormatter(_fmt)
logger.addHandler(svc_handler)

alert_handler = logging.FileHandler(LOG_DIR / "alerts.log", encoding="utf-8")
alert_handler.setFormatter(_fmt)
alert_logger = logging.getLogger("pcmonitor.alert")
alert_logger.addHandler(alert_handler)
alert_logger.propagate = False

# ---------- 指标流水 ----------
CSV_FILE = LOG_DIR / "metrics.csv"
CSV_HEADER = ["ts", "cpu_pct", "cpu_temp", "mem_pct", "mem_used_mb", "disk_pct",
              "gpu_temp", "gpu_pct", "gpu_mem_used_mb", "net_sent_mb", "net_recv_mb", "proc_count"]
if not CSV_FILE.exists():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(CSV_HEADER)

metrics_window = deque(maxlen=CFG["snapshot_window"])


# ---------- 采集 ----------
def read_temps():
    """调用 TempReader 读取 CPU/GPU 温度。
    CPU 温度来源优先级: LHM 逐核/Package > WMI 热区 (HVCI 拦截 LHM 驱动时的回退)。
    result["cpu_source"] 标识来源: lhm / wmi_thermal / None
    """
    result = {"cpu": None, "gpu": None, "all": {}, "cpu_source": None}
    if not TEMP_READER.exists():
        return result
    try:
        out = subprocess.run([str(TEMP_READER)], capture_output=True, text=True,
                             timeout=CFG["temp_reader_timeout"], creationflags=CREATE_NO_WINDOW)
        if out.returncode == 0 and out.stdout.strip():
            data = json.loads(out.stdout.strip())
            result["all"] = data
            cpu_vals, gpu_vals, wmi_vals = [], [], []
            for key, val in data.items():
                parts = key.split("|")
                hw_type, name, sensor = parts[0], parts[1], parts[2] if len(parts) > 2 else ""
                if hw_type == "Cpu" and ("Package" in sensor or "Max" in sensor):
                    cpu_vals.append(val)
                elif hw_type.startswith("Gpu"):
                    gpu_vals.append(val)
                elif hw_type == "WmiThermalZone":
                    wmi_vals.append(val)
            if cpu_vals:
                result["cpu"] = max(cpu_vals)
                result["cpu_source"] = "lhm"
            elif wmi_vals:
                result["cpu"] = max(wmi_vals)
                result["cpu_source"] = "wmi_thermal"
            if gpu_vals:
                result["gpu"] = max(gpu_vals)
        else:
            logger.warning("TempReader rc=%s stderr=%s stdout_len=%d",
                           out.returncode, (out.stderr or "")[:300], len(out.stdout or ""))
    except subprocess.TimeoutExpired:
        logger.warning("TempReader timeout (>%ss)", CFG["temp_reader_timeout"])
    except json.JSONDecodeError as e:
        logger.warning("read_temps JSON error: %s | near=%r", e, out.stdout[max(0, e.pos - 40):e.pos + 40])
    except OSError as e:
        logger.warning("read_temps failed: %s", e)
    return result


def read_gpu_nvidia():
    """nvidia-smi 读显卡(温度/占用/显存/功耗)"""
    result = {"temp": None, "util": None, "mem_used_mb": None, "power_w": None}
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used,power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
        if out.returncode == 0 and out.stdout.strip():
            parts = [p.strip() for p in out.stdout.strip().split(",")]
            if len(parts) >= 4:
                result["temp"] = float(parts[0])
                result["util"] = float(parts[1])
                result["mem_used_mb"] = float(parts[2])
                result["power_w"] = float(parts[3])
    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass
    return result


def top_processes(n=50):
    """按 CPU/内存占用排序的进程 Top N"""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "memory_info", "username"]):
        try:
            info = p.info
            procs.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_pct": round(info.get("cpu_percent") or 0, 1),
                "mem_pct": round(info.get("memory_percent") or 0, 2),
                "mem_mb": round((info["memory_info"].rss / 1048576) if info.get("memory_info") else 0, 1),
                "user": info.get("username") or ""
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    by_cpu = sorted(procs, key=lambda x: x["cpu_pct"], reverse=True)[:n]
    by_mem = sorted(procs, key=lambda x: x["mem_mb"], reverse=True)[:n]
    return {"by_cpu": by_cpu, "by_mem": by_mem, "total": len(procs)}


def collect_sample():
    """采集一次完整样本"""
    ts = datetime.now()
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(str(Path(os.environ.get("SystemDrive", "C:")) / "."))
    net = psutil.net_io_counters()
    temps = read_temps()
    gpu = read_gpu_nvidia()
    sample = {
        "ts": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_pct": cpu_pct,
        "cpu_temp": temps["cpu"],
        "cpu_temp_source": temps.get("cpu_source"),
        "mem_pct": mem.percent,
        "mem_used_mb": round(mem.used / 1048576),
        "disk_pct": disk.percent,
        "gpu_temp": gpu["temp"] if gpu["temp"] is not None else temps["gpu"],
        "gpu_pct": gpu["util"],
        "gpu_mem_used_mb": gpu["mem_used_mb"],
        "gpu_power_w": gpu["power_w"],
        "net_sent_mb": round(net.bytes_sent / 1048576, 1),
        "net_recv_mb": round(net.bytes_recv / 1048576, 1),
        "proc_count": len(psutil.pids()),
        "temps_all": temps["all"]
    }
    metrics_window.append(sample)
    return sample


def write_csv(sample):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            sample["ts"], sample["cpu_pct"], sample["cpu_temp"], sample["mem_pct"],
            sample["mem_used_mb"], sample["disk_pct"], sample["gpu_temp"],
            sample["gpu_pct"], sample["gpu_mem_used_mb"],
            sample["net_sent_mb"], sample["net_recv_mb"], sample["proc_count"]
        ])


# ---------- 异常判定与快照 ----------
def check_alerts(sample):
    """返回 [(key, 描述文本), ...]。key 为稳定标识(用于事件状态机), 文本含当前值(用于展示)"""
    th = CFG["thresholds"]
    hits = []
    if sample["cpu_temp"] is not None and sample["cpu_temp"] >= th["cpu_temp"]:
        hits.append(("cpu_temp", f"CPU温度 {sample['cpu_temp']}C >= {th['cpu_temp']}C"))
    if sample["gpu_temp"] is not None and sample["gpu_temp"] >= th["gpu_temp"]:
        hits.append(("gpu_temp", f"GPU温度 {sample['gpu_temp']}C >= {th['gpu_temp']}C"))
    if sample["cpu_pct"] >= th["cpu_percent"]:
        hits.append(("cpu_pct", f"CPU占用 {sample['cpu_pct']}% >= {th['cpu_percent']}%"))
    if sample["mem_pct"] >= th["mem_percent"]:
        hits.append(("mem_pct", f"内存占用 {sample['mem_pct']}% >= {th['mem_percent']}%"))
    if sample["disk_pct"] >= th["disk_percent"]:
        hits.append(("disk_pct", f"磁盘占用 {sample['disk_pct']}% >= {th['disk_percent']}%"))
    return hits


def recent_event_logs(minutes=10):
    """抓最近 N 分钟的系统/应用程序错误事件(用于回溯)"""
    events = []
    since = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%S")
    for logname in ("System", "Application"):
        try:
            out = subprocess.run(
                ["wevtutil", "qe", logname, "/q:*[System[(Level<=2) and TimeCreated[@SystemTime>='" + since + "']]]",
                 "/c:50", "/f:text"],
                capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW)
            if out.returncode == 0 and out.stdout.strip():
                events.append({"log": logname, "text": out.stdout[:20000]})
        except (subprocess.TimeoutExpired, OSError):
            pass
    return events


def write_snapshot(sample, hits):
    """异常现场完整快照 - 事后可回溯的核心依据"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = {
        "trigger_time": sample["ts"],
        "alerts": hits,
        "current": sample,
        "history": list(metrics_window),
        "processes": top_processes(50),
        "event_logs": recent_event_logs(10),
        "system": {
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": getattr(psutil.cpu_freq(), "current", None),
            "load_avg": getattr(psutil, "getloadavg", lambda: None)(),
            "users": [u.name for u in psutil.users()],
            "os": sys.platform
        },
        "disks": {
            str(p.mountpoint): {
                "fstype": p.fstype,
                "total_gb": round(psutil.disk_usage(p.mountpoint).total / 1073741824, 1),
                "used_pct": psutil.disk_usage(p.mountpoint).percent
            }
            for p in psutil.disk_partitions() if p.fstype not in ("", "tmpfs")
        }
    }
    snap_file = SNAP_DIR / f"alert_{ts}.json"
    snap_file.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    return snap_file


def notify_pushplus_event(kind, payload, sample, snap_file=None, dur=None):
    """事件制推送: kind = occur(新告警) / sustain(持续提醒) / recover(恢复)"""
    token = CFG.get("pushplus_token", "")
    if not token:
        logger.warning("pushplus_token 未配置, 跳过推送")
        return False
    hhmmss = datetime.now().strftime("%H:%M:%S")
    prefix = "【测试】" if os.environ.get("PCMONITOR_TEST") else ""
    if kind == "occur":
        title = prefix + "PC监控告警 " + hhmmss
        lines = ["【新异常】首次推送，持续期间不重复轰炸："]
        lines += ["  - " + d for _, d in payload]
        lines += ["", "时间: " + sample["ts"],
                  "CPU %.1f%% / 内存 %.1f%% / CPU温度 %sC / GPU温度 %sC" % (
                      sample["cpu_pct"], sample["mem_pct"], sample["cpu_temp"], sample["gpu_temp"])]
        if snap_file:
            lines.append("现场快照: " + snap_file.name)
        lines += ["", "持续期间每 %d 分钟提醒一次，恢复正常后另行通知。" % CFG.get("alert_sustain_minutes", 30)]
    elif kind == "sustain":
        title = "PC监控持续提醒 " + hhmmss
        lines = ["【持续中】以下异常仍未恢复："]
        for key, ev in alert_events.items():
            lines.append("  - %s（已持续 %s）" % (ev["last_desc"], _fmt_dur(time.time() - ev["since"])))
        lines += ["", "当前: CPU %.1f%% / 内存 %.1f%% / CPU温度 %sC / GPU温度 %sC" % (
            sample["cpu_pct"], sample["mem_pct"], sample["cpu_temp"], sample["gpu_temp"])]
    else:  # recover
        title = "PC监控已恢复 " + hhmmss
        lines = ["【已恢复】" + payload, "持续 %s 后恢复正常，当前指标回到阈值内。" % _fmt_dur(dur)]
    try:
        r = requests.post("http://www.pushplus.plus/send", json={
            "token": token, "title": title, "content": "\n".join(lines), "template": "txt"
        }, timeout=10)
        data = r.json()
        if data.get("code") == 200:
            return True
        logger.warning("pushplus 返回异常: %s", data)
    except Exception as e:
        logger.warning("pushplus 推送失败: %s", e)
    return False


def _fmt_dur(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return "%d秒" % seconds
    if seconds < 3600:
        return "%d分%d秒" % (seconds // 60, seconds % 60)
    return "%d小时%d分" % (seconds // 3600, (seconds % 3600) // 60)


# 事件状态机: key -> {since, last_push, last_desc, recover_count}
alert_events = {}
last_sustain_push = 0


def process_alerts(sample, hits):
    """事件制告警处理:
    - 新异常出现 -> 推 occur + 写快照 + 记 alerts.log
    - 持续中    -> 每 alert_sustain_minutes 推一次 sustain
    - 恢复正常(连续 recover_debounce_samples 次采样正常) -> 推 recover
    """
    global last_sustain_push
    now = time.time()
    active = dict(hits)

    # 1) 更新防抖计数: 活跃项清零, 非活跃项累加
    for key in list(alert_events):
        if key in active:
            alert_events[key]["recover_count"] = 0
            alert_events[key]["last_desc"] = active[key]
        else:
            alert_events[key]["recover_count"] = alert_events[key].get("recover_count", 0) + 1

    # 2) 恢复确认(防抖): 连续 N 次采样正常才推恢复通知, 避免阈值附近抖动来回刷屏
    debounce = CFG.get("recover_debounce_samples", 6)
    for key in [k for k, ev in alert_events.items()
                if k not in active and ev.get("recover_count", 0) >= debounce]:
        ev = alert_events.pop(key)
        dur = now - ev["since"]
        alert_logger.info("RECOVER | %s | duration=%.0fs", key, dur)
        notify_pushplus_event("recover", ev["last_desc"], sample, dur=dur)

    # 3) 新异常出现: 推 occur + 快照 + 日志
    new_hits = [(k, d) for k, d in hits if k not in alert_events]
    if new_hits:
        for k, d in new_hits:
            alert_events[k] = {"since": now, "last_push": now, "last_desc": d, "recover_count": 0}
        snap_file = write_snapshot(sample, [d for _, d in new_hits])
        alert_logger.warning("ALERT | %s | snapshot=%s | metrics: cpu=%.1f%% mem=%.1f%% disk=%.1f%% cpuT=%s gpuT=%s",
                             "; ".join(d for _, d in new_hits), snap_file.name, sample["cpu_pct"],
                             sample["mem_pct"], sample["disk_pct"], sample["cpu_temp"], sample["gpu_temp"])
        logger.info("snapshot written: %s", snap_file.name)
        notify_pushplus_event("occur", new_hits, sample, snap_file=snap_file)
        last_sustain_push = now  # 重置持续提醒计时

    # 4) 持续提醒: 有活跃事件且距上次提醒超过阈值
    sustain = CFG.get("alert_sustain_minutes", 30) * 60
    if alert_events and now - last_sustain_push >= sustain:
        last_sustain_push = now
        notify_pushplus_event("sustain", None, sample)


# ---------- 日志清理 ----------
def cleanup_old_logs():
    cutoff = datetime.now() - timedelta(days=CFG["log_retention_days"])
    for folder in (LOG_DIR, SNAP_DIR):
        for f in folder.iterdir():
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                try:
                    f.unlink()
                except OSError:
                    pass


# ---------- 主循环 ----------
_MUTEX_HANDLE = None  # 单实例互斥锁句柄, 需保持引用防止被 GC 释放


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def ensure_single_instance():
    """互斥锁保证单实例: 第二个实例启动时自动退出"""
    global _MUTEX_HANDLE
    if sys.platform != "win32":
        return True
    ctypes.windll.kernel32.CreateMutexW.restype = ctypes.c_void_p
    _MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(None, False, "PCMonitor_SingleInstance_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        logger.warning("已有监控实例在运行, 本实例(pid=%d)自动退出", os.getpid())
        return False
    return True


def main():
    logger.info("========== PC Monitor 启动 (pid=%d, admin=%s) ==========", os.getpid(), is_admin())
    if not ensure_single_instance():
        return
    psutil.cpu_percent(interval=None)  # 预热, 首次调用返回 0
    cleanup_old_logs()
    last_cleanup = time.time()
    cycle = 0
    while True:
        try:
            sample = collect_sample()
            write_csv(sample)
            hits = check_alerts(sample)
            if hits:
                process_alerts(sample, hits)
            else:
                process_alerts(sample, [])
            cycle += 1
            if time.time() - last_cleanup > 86400:
                cleanup_old_logs()
                last_cleanup = time.time()
        except Exception as e:
            logger.exception("采样循环异常: %s", e)
        time.sleep(CFG["interval"])


if __name__ == "__main__":
    main()
