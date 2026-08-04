# -*- coding: utf-8 -*-
"""
PC 监控富文本报告生成 + PushPlus 推送
两种模式:
  daily: 全天趋势日报   python push_report.py --mode daily [--from "12:00"] [--to "20:00"]
  alert: 告警分析报告   python push_report.py --mode alert --since "2026-08-03 13:00:00" [--analysis <md文件>]
深色仪表盘风格; 微信内显示静态 SVG 趋势图 (微信屏蔽JS, 交互图无法在微信内生效)。
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "logs" / "metrics.csv"
ALERTS_LOG = BASE / "logs" / "alerts.log"
SNAP_DIR = BASE / "snapshots"
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8")) if (BASE / "config.json").exists() else {}
TOKEN = CONFIG.get("pushplus_token", "")

COLORS = {'ct': '#ff6b6b', 'gt': '#ffa940', 'cpu': '#4096ff', 'mem': '#73d13d'}
NAMES = {'ct': 'CPU温度', 'gt': 'GPU温度', 'cpu': 'CPU负载', 'mem': '内存使用'}


def load_rows(start_str, end_str):
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if start_str <= r['ts'] <= end_str:
                try:
                    rows.append({'ts': r['ts'], 'cpu': float(r['cpu_pct']),
                                 'ct': float(r['cpu_temp']) if r['cpu_temp'].strip() else None,
                                 'gt': float(r['gpu_temp']), 'mem': float(r['mem_pct']),
                                 'gpu': float(r['gpu_pct'])})
                except Exception:
                    pass
    return rows


def aggregate(rows):
    buckets = {}
    for r in rows:
        dt = datetime.strptime(r['ts'], '%Y-%m-%d %H:%M:%S')
        key = dt.replace(minute=dt.minute - dt.minute % 2, second=0)
        buckets.setdefault(key, []).append(r)
    t = {'times': [], 'cpu_p': [], 'mem_p': [], 'gpu_t': [], 'cpu_t': []}
    for k in sorted(buckets):
        rs = buckets[k]
        t['times'].append(k.strftime('%H:%M'))
        t['cpu_p'].append(round(sum(x['cpu'] for x in rs) / len(rs), 1))
        t['mem_p'].append(round(sum(x['mem'] for x in rs) / len(rs), 1))
        g = [x['gt'] for x in rs if x['gt'] is not None]
        t['gpu_t'].append(round(sum(g) / len(g), 1) if g else None)
        c = [x['ct'] for x in rs if x['ct'] is not None]
        t['cpu_t'].append(round(sum(c) / len(c), 1) if c else None)
    return t


def stat(arr):
    v = [x for x in arr if x is not None]
    return (min(v), round(sum(v) / len(v), 1), max(v)) if v else (0, 0, 0)


def static_svg(t):
    W, H, L, R, T, B = 660, 300, 38, 10, 34, 28
    n = len(t['times'])
    if n == 0:
        return ''
    X = lambda i: L + i * (W - L - R) / max(n - 1, 1)
    Y = lambda v: T + (100 - v) * (H - T - B) / 100.0
    series = {'ct': t['cpu_t'], 'gt': t['gpu_t'], 'cpu': t['cpu_p'], 'mem': t['mem_p']}

    def path_for(arr):
        segs, cur = [], []
        for i, v in enumerate(arr):
            if v is None:
                if cur: segs.append(cur); cur = []
            else:
                cur.append((X(i), Y(v)))
        if cur: segs.append(cur)
        return ' '.join('M' + ' L'.join('%.1f %.1f' % (x, y) for x, y in s) for s in segs)

    s = ['<svg viewBox="0 0 %d %d" style="width:100%%;background:#1a212c;border:1px solid #2a3444;border-radius:10px">' % (W, H)]
    for gv in (0, 20, 40, 60, 80, 100):
        s.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#242e3d"/>' % (L, Y(gv), W - R, Y(gv)))
    for gv in (0, 50, 100):
        s.append('<text x="%d" y="%.1f" fill="#8b93a1" font-size="10" text-anchor="end">%d</text>' % (L - 6, Y(gv) + 4, gv))
    for i, tm in enumerate(t['times']):
        if tm.endswith(':00'):
            s.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#242e3d"/>' % (X(i), T, X(i), H - B))
            s.append('<text x="%.1f" y="%d" fill="#8b93a1" font-size="10" text-anchor="middle">%s</text>' % (X(i), H - 8, tm))
    for key in ('ct', 'gt', 'cpu', 'mem'):
        s.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path_for(series[key]), COLORS[key]))
    lx = L
    for key in ('ct', 'gt', 'cpu', 'mem'):
        s.append('<circle cx="%d" cy="14" r="4" fill="%s"/><text x="%d" y="18" fill="#cfd3da" font-size="11">%s</text>' % (lx + 5, COLORS[key], lx + 13, NAMES[key]))
        lx += 13 + len(NAMES[key]) * 11 + 18
    s.append('</svg>')
    return ''.join(s)


DRY = False


def parse_alerts(since_str, path=None):
    alerts = []
    log_path = Path(path) if path else ALERTS_LOG
    if not log_path.exists():
        return alerts
    for line in log_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*ALERT \| (.+?) \| snapshot=(\S+) \| metrics: (.*)$', line)
        if m and m.group(1) > since_str:
            alerts.append({'time': m.group(1), 'hits': m.group(2).split('; '), 'snap': m.group(3), 'metrics': m.group(4)})
    return alerts


def severity_of(hits):
    if len(hits) >= 2:
        return ('高', '#f87171')
    for h in hits:
        mv = re.search(r'(\d+(?:\.\d+)?)', h)
        v = float(mv.group(1)) if mv else 0
        if ('温度' in h and v >= 90) or '磁盘' in h:
            return ('高', '#f87171')
    return ('中', '#fbbf24')


def md_lite(md):
    """极简 Markdown -> HTML (【段】=标题, - 列表, **加粗**)"""
    out = []
    for line in md.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'<b style="color:#e6e8eb">\1</b>', line)
        if line.startswith('【') and '】' in line:
            out.append('<h4 style="color:#e6e8eb;margin:12px 0 6px;font-size:14px">%s</h4>' % line)
        elif line.lstrip().startswith(('-', '*', '·')):
            out.append('<div style="color:#cfd3da;font-size:13px;line-height:1.7;margin:2px 0 2px 10px">• %s</div>' % line.lstrip('-*· '))
        else:
            out.append('<div style="color:#cfd3da;font-size:13px;line-height:1.7;margin:2px 0">%s</div>' % line)
    return ''.join(out)


def card(label, value, unit, sub, color):
    return ('<div style="flex:1;min-width:120px;background:#1d2430;border:1px solid #2a3444;border-radius:10px;padding:10px 12px">'
            '<div style="font-size:12px;color:#8b93a1">%s</div><div style="font-size:22px;font-weight:bold;color:%s">%s%s</div>'
            '<div style="font-size:11px;color:#8b93a1">%s</div></div>') % (label, color, value, unit, sub)


def table(t):
    cs, ms, gs, cts = stat(t['cpu_p']), stat(t['mem_p']), stat(t['gpu_t']), stat(t['cpu_t'])
    row = lambda n, a, b, c, col: ('<tr><td style="padding:7px;border-bottom:1px solid #242e3d">%s</td>'
        '<td style="padding:7px;text-align:center;border-bottom:1px solid #242e3d">%s</td>'
        '<td style="padding:7px;text-align:center;border-bottom:1px solid #242e3d">%s</td>'
        '<td style="padding:7px;text-align:center;border-bottom:1px solid #242e3d;color:%s;font-weight:bold">%s</td></tr>') % (n, a, b, col, c)
    return ('<table style="width:100%;border-collapse:collapse;font-size:13px;margin:14px 0 6px;color:#e6e8eb">'
            '<tr style="background:#1d2430"><th style="padding:8px;text-align:left;border-bottom:2px solid #2a3444;color:#cfd3da">指标</th>'
            '<th style="padding:8px;border-bottom:2px solid #2a3444;color:#cfd3da">最低</th>'
            '<th style="padding:8px;border-bottom:2px solid #2a3444;color:#cfd3da">平均</th>'
            '<th style="padding:8px;border-bottom:2px solid #2a3444;color:#cfd3da">最高</th></tr>'
            + row('CPU 负载', '%.0f%%' % cs[0], '%.1f%%' % cs[1], '%.1f%%' % cs[2], '#4096ff')
            + row('GPU 温度', '%.0f°C' % gs[0], '%.1f°C' % gs[1], '%.1f°C' % gs[2], '#ffa940')
            + row('CPU 温度', '%.0f°C' % cts[0], '%.1f°C' % cts[1], '%.1f°C' % cts[2], '#ff6b6b')
            + row('内存使用', '%.0f%%' % ms[0], '%.1f%%' % ms[1], '%.1f%%' % ms[2], '#facc15')
            + '</table>')


def push(title, html):
    if DRY:
        Path(r'C:\Users\Yaojie\AppData\Local\Temp\push_report_dry.html').write_text(html, encoding='utf-8')
        print('DRY: written to Temp/push_report_dry.html (%d bytes)' % len(html))
        return {'code': 200}
    import requests
    r = requests.post('http://www.pushplus.plus/send', json={
        'token': TOKEN, 'title': title, 'content': html, 'template': 'html'}, timeout=20)
    data = r.json()
    if data.get('code') != 200:
        raise RuntimeError('pushplus failed: %s' % data)
    return data


def build_common_body(t, title_sub):
    cs, ms, gs = stat(t['cpu_p']), stat(t['mem_p']), stat(t['gpu_t'])
    body = ['<div style="font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;background:#141821;color:#e6e8eb;max-width:680px;margin:0 auto;padding:14px;border-radius:12px">']
    body.append('<h2 style="color:#e6e8eb;border-left:5px solid #4096ff;padding-left:10px;margin:4px 0 6px;font-size:20px">%s</h2>' % title_sub)
    body.append('<div style="display:flex;gap:8px;flex-wrap:wrap">')
    body.append(card('CPU 负载峰值', '%.1f' % cs[2], '%', '平均 %.1f%%' % cs[1], '#4096ff'))
    body.append(card('GPU 温度峰值', '%.1f' % gs[2], '°C', '阈值 85°C', '#ffa940'))
    body.append(card('内存使用峰值', '%.1f' % ms[2], '%', '平均 %.1f%%' % ms[1], '#facc15'))
    body.append('</div>')
    body.append('<h3 style="color:#e6e8eb;font-size:15px;margin:18px 0 8px">趋势图（CPU温度 / GPU温度 / CPU负载 / 内存使用）</h3>')
    body.append('<p style="color:#8b93a1;font-size:11px;margin:0 0 8px">单位：% 与 °C 同轴（0-100）</p>')
    body.append(static_svg(t))
    body.append(table(t))
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['daily', 'alert'], required=True)
    ap.add_argument('--from', dest='frm', default=None)
    ap.add_argument('--to', dest='to', default=None)
    ap.add_argument('--since', default=None, help='alert 模式起点 (YYYY-MM-DD HH:MM:SS)')
    ap.add_argument('--analysis', default=None, help='AI 分析 Markdown 文件路径')
    ap.add_argument('--alerts-file', default=None, help='测试用: 覆盖默认 alerts.log 路径')
    ap.add_argument('--dry', action='store_true', help='只生成本地 HTML 不推送')
    args = ap.parse_args()

    global DRY
    DRY = args.dry
    now = datetime.now()
    if not TOKEN:
        print('ERROR: pushplus_token 未配置'); sys.exit(1)

    if args.mode == 'daily':
        day = now.strftime('%Y-%m-%d')
        start = (datetime.strptime(args.frm, '%Y-%m-%d %H:%M') if args.frm and len(args.frm) > 8
                 else datetime.strptime(args.frm or '00:00', '%H:%M').replace(year=now.year, month=now.month, day=now.day))
        end = (datetime.strptime(args.to, '%Y-%m-%d %H:%M') if args.to and len(args.to) > 8
               else datetime.strptime(args.to or '23:59', '%H:%M').replace(year=now.year, month=now.month, day=now.day))
        rows = load_rows(start.strftime('%Y-%m-%d %H:%M:%S'), end.strftime('%Y-%m-%d %H:%M:%S'))
        if not rows:
            print('NO_DATA'); sys.exit(2)
        t = aggregate(rows)
        body = build_common_body(t, 'PC 监控日报 · %s' % day)
        body.append('<h3 style="color:#e6e8eb;font-size:15px;margin:16px 0 8px">结论</h3>')
        body.append('<p style="font-size:13px;line-height:1.7;color:#cfd3da">采样 %d 条，%s ~ %s。整体指标见上表与趋势图。</p>' % (
            len(rows), t['times'][0], t['times'][-1]))
        body.append('<p style="font-size:11px;color:#8b93a1;margin-top:14px">— PCMonitor 自动生成</p></div>')
        push('PC监控日报 · %s' % day, ''.join(body))
        print('PUSHED daily')
        return

    # alert 模式
    since = args.since or (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    alerts = parse_alerts(since, args.alerts_file)
    if not alerts:
        print('NO_ALERTS'); sys.exit(2)
    rows = load_rows(since, now.strftime('%Y-%m-%d %H:%M:%S'))
    t = aggregate(rows) if rows else {'times': [], 'cpu_p': [], 'mem_p': [], 'gpu_t': [], 'cpu_t': []}

    sev_level = {'高': 0, '中': 1}
    worst = ('中', '#fbbf24')
    body = build_common_body(t, 'PC 监控告警分析 · %s' % now.strftime('%m-%d %H:%M'))

    # 告警卡片
    for a in alerts:
        sev, color = severity_of(a['hits'])
        if sev_level[sev] < sev_level[worst[0]]:
            worst = (sev, color)
        body.append('<div style="background:#1d2430;border:1px solid %s;border-left:5px solid %s;border-radius:8px;padding:10px 12px;margin:10px 0">' % (color, color))
        body.append('<div style="display:flex;justify-content:space-between"><span style="color:#e6e8eb;font-weight:bold;font-size:14px">%s</span>'
                    '<span style="color:%s;font-weight:bold;font-size:13px">风险:%s</span></div>' % (a['time'], color, sev))
        for h in a['hits']:
            body.append('<div style="color:#fca5a5;font-size:13px;margin-top:4px">⚠ %s</div>' % h)
        body.append('</div>')
        # 现场 Top 进程
        snap_file = SNAP_DIR / a['snap']
        if snap_file.exists():
            try:
                snap = json.loads(snap_file.read_text(encoding="utf-8"))
                procs = snap.get('processes', {}).get('by_cpu', [])[:5]
                if procs:
                    body.append('<div style="color:#8b93a1;font-size:12px;margin:6px 0 4px">现场 Top5 进程（CPU）</div>')
                    for p in procs:
                        body.append('<div style="color:#cfd3da;font-size:12px;line-height:1.6">%s — CPU %.1f%% / 内存 %.0fMB</div>' % (
                            p.get('name'), p.get('cpu_pct', 0), p.get('mem_mb', 0)))
            except Exception:
                pass

    # AI 深度分析
    if args.analysis and Path(args.analysis).exists():
        body.append('<h3 style="color:#e6e8eb;font-size:15px;margin:16px 0 8px">深度分析</h3>')
        body.append(md_lite(Path(args.analysis).read_text(encoding="utf-8")))

    body.append('<p style="font-size:13px;line-height:1.7;color:#cfd3da;margin-top:14px">综合风险评级：<b style="color:%s">%s</b>。趋势与指标见上方图表。</p>' % (worst[1], worst[0]))
    body.append('<p style="font-size:11px;color:#8b93a1;margin-top:14px">— PCMonitor 自动生成</p></div>')
    push('PC监控告警 %s · %s' % (worst[0], now.strftime('%H:%M')), ''.join(body))
    print('PUSHED alert count=%d worst=%s' % (len(alerts), worst[0]))


if __name__ == '__main__':
    main()
