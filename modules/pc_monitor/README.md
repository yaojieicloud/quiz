# PC Monitor — Windows 本机常驻监控系统

一套部署在 Windows 本机（Win10/11）的轻量系统监控方案：5 秒采样、异常现场快照、
事件制告警推送（PushPlus 微信）、富文本趋势图报告、AI 巡检分析。

> 2026-08-03 首次部署于作者工作机，本目录为完整可复现备份（源码 + 依赖 + 部署脚本 + 文档）。

---

## 一、设计思路

### 1. 三层告警体系（各司其职、互不轰炸）

| 层 | 载体 | 触发 | 内容 |
|---|---|---|---|
| 实时简报 | monitor.py 内置 → PushPlus | 异常**发生**秒级推 1 条 | txt：触发项 + 当时指标 + 快照文件名 |
| 持续提醒 | monitor.py 内置 → PushPlus | 异常持续中，每 30 分钟 1 条 | txt：仍在持续的异常 + 已持续时长 |
| 恢复通知 | monitor.py 内置 → PushPlus | 恢复正常后推 1 条 | txt：已恢复 + 持续时长 |
| 深度分析 | WorkBuddy 每小时巡检（外部自动化，不在本仓库） | **仅有新告警时** | 深色富文本 HTML：告警卡片 + 现场 Top 进程 + 趋势 SVG 图 + AI 六段分析 |
| 日报 | push_report.py --mode daily（手动/可配自动化） | 手动触发 | 深色富文本 HTML：指标卡 + 趋势图 + 汇总表 |

### 2. 防轰炸：事件制状态机

不用"固定冷却间隔重复推"，而是按**事件生命周期**推送：

```
正常 ──超过阈值──> 异常发生(occur: 推1条+写快照+记日志)
        │
        ├─ 持续中: 每 alert_sustain_minutes 推 1 次提醒
        │
        └─ 连续 recover_debounce_samples 次采样正常 ──> 恢复(recover: 推1条)
```

- 一次持续 2 小时的异常 = 1(occur) + 3(sustain, 每30分钟) + 1(recover) = **5 条**，而非旧式每 5 分钟一条的 24 条轰炸。
- **恢复防抖**：指标在阈值附近抖动时不会"恢复→又告警"来回刷屏。

### 3. 温度读取：LHM + WMI 热区双源回退（HVCI 应对方案）

- 首选 **LibreHardwareMonitor (LHM)**：逐核 CPU 温度、GPU、存储温度，精度高。
- **问题**：Windows 开启 HVCI（内存完整性）后拦截 LHM 驱动，CPU 温度读不到（管理员权限也无效）。
- **回退**：读 **WMI 热区** `root\WMI\MSAcpi_ThermalZoneTemperature`（封装级温度），只需管理员权限，不受 HVCI 影响。
- monitor.py 中 `cpu_source` 标识来源：`lhm` / `wmi_thermal`。

### 4. 工程细节（踩过的坑，均已解决）

| 坑 | 表现 | 解决 |
|---|---|---|
| HVCI 拦截 LHM 驱动 | CPU 温度恒为空 | WMI 热区回退（见上） |
| .NET 10 `System.Management` 库 bug | 提权运行抛 `PlatformNotSupportedException` | TempReader 改调 Windows PowerShell 子进程 `Get-CimInstance` |
| 传感器名含控制字符/反斜杠 | 输出 JSON 非法，下游解析失败 | `SanitizeKey` 清洗所有 key（去控制字符、`\`→`/`、`"`→`'`） |
| pythonw 无控制台弹黑窗 | 子进程（TempReader/nvidia-smi/wevtutil）弹终端 | 全部 `creationflags=CREATE_NO_WINDOW (0x08000000)` |
| 双实例风险 | 重复采样/重复推送 | 单实例互斥锁 `PCMonitor_SingleInstance_Mutex` |
| PowerShell 发 PushPlus 乱码 | PS5.1 默认 GBK 编码 body | 一律用 Python `requests`（UTF-8）推送 |
| 微信内交互图失效 | 微信文章页屏蔽 JS，ECharts 画不出 | 富文本报告内嵌**静态 SVG** 趋势图；交互版部署独立网页链接 |

---

## 二、目录结构

```
pc_monitor/
├── monitor.py            # 监控主服务（采样/告警状态机/快照/PushPlus 实时推送）
├── query_monitor.py      # 查询脚本（时间段统计/告警列表/快照详情/服务状态）
├── push_report.py        # 富文本报告生成+推送（daily 日报 / alert 告警分析）
├── register_task.bat     # 注册开机自启任务（需管理员）
├── restart_service.ps1   # 重启服务脚本
├── config.example.json   # 配置模板（真实 config.json 含 token, 不入库）
├── requirements.txt      # Python 依赖: psutil, requests
├── README.md
├── PUSHPLUS.md           # PushPlus 凭据记录（私密!）
├── tools/
│   ├── TempReader/       # C# 温度读取器源码（LHM + WMI 热区）
│   │   ├── Program.cs
│   │   └── TempReader.csproj
│   └── TaskRegistrar/    # C# 任务注册/重启器源码
│       ├── Program.cs
│       └── TaskRegistrar.csproj
└── vendor/
    └── LibreHardwareMonitor/   # 编译所需 dll（LHM/HidSharp/TaskScheduler 等）
```

运行时目录（部署后）：`%LOCALAPPDATA%\PCMonitor\`，数据在 `logs/` 与 `snapshots/`（保留 30 天）。

---

## 三、部署步骤（新机器复现）

前置：Windows 10/11、Python 3.10+、.NET SDK 10、管理员权限（读 CPU 温度必需）。

```powershell
# 1. 放置目录
$BASE = "$env:LOCALAPPDATA\PCMonitor"
mkdir $BASE
#    把本备份目录内容复制到 $BASE（monitor.py 等放根目录, tools/ vendor/ 保持结构）

# 2. Python 环境
cd $BASE
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt

# 3. 编译 C# 工具
dotnet publish tools\TempReader  -c Release -r win-x64 --self-contained false -o tools\TempReader\publish
dotnet publish tools\TaskRegistrar -c Release -r win-x64 --self-contained false -o tools\TaskRegistrar\publish

# 4. 配置（填入 pushplus_token, 见 PUSHPLUS.md）
copy config.example.json config.json
notepad config.json

# 5. 注册开机自启 + 立即启动（管理员运行）
register_task.bat
```

注册效果：任务计划 `PCMonitor_Main`，登录触发、最高权限、失败自动重启、单实例策略。
重启服务：`tools\TaskRegistrar\publish\TaskRegistrar.exe --restart`（提权杀旧进程+重启任务）。

---

## 四、配置项（config.json）

| 键 | 默认 | 说明 |
|---|---|---|
| interval | 5 | 采样间隔(秒) |
| thresholds.cpu_temp / gpu_temp | 85 | 温度告警阈值(°C) |
| thresholds.cpu_percent / mem_percent / disk_percent | 90 | 占用告警阈值(%) |
| alert_sustain_minutes | 30 | 异常持续期间提醒间隔(分钟) |
| recover_debounce_samples | 6 | 连续正常采样多少次才确认恢复 |
| log_retention_days | 30 | 日志/快照保留天数 |
| snapshot_window | 200 | 快照携带的历史序列条数 |
| pushplus_token | "" | PushPlus 推送 token。**仅存本机 config.json，不入库**；获取方式见 PUSHPLUS.md |
| temp_reader_timeout | 20 | TempReader 子进程超时(秒) |

---

## 五、常用操作

```powershell
$PY = "$env:LOCALAPPDATA\PCMonitor\venv\Scripts\python.exe"
$BASE = "$env:LOCALAPPDATA\PCMonitor"

# 时间段统计
& $PY "$BASE\query_monitor.py" --from "2026-08-03 13:00" --to "2026-08-03 19:00"

# 告警列表 / 快照详情 / 服务状态
& $PY "$BASE\query_monitor.py" --alerts
& $PY "$BASE\query_monitor.py" --snapshot alert_20260803_131235.json
& $PY "$BASE\query_monitor.py" --status

# 日报推送（当天）
& $PY "$BASE\push_report.py" --mode daily

# 告警分析报告（巡检自动化调用, 或手动）
& $PY "$BASE\push_report.py" --mode alert --since "2026-08-03 19:00:00" --analysis 分析.md
```

---

## 六、富文本报告说明

- 风格：深色仪表盘（适配手机深色模式），指标卡 + 趋势 SVG 图 + 汇总表 + 结论。
- 趋势图四线：CPU温度 / GPU温度 / CPU负载 / 内存使用（2 分钟桶聚合，% 与 °C 同轴 0-100）。
- 微信屏蔽 JS，故报告内为静态 SVG；交互版（ECharts 缩放/拖选）需部署独立网页，报告顶部放链接按钮。
- 告警报告额外含：告警卡片（风险评级 高/中）、现场 Top5 进程、AI 六段分析渲染。

---

## 七、外部组件（不在本仓库）

- **WorkBuddy 每小时巡检自动化**：读 alerts.log 新告警 → 生成 AI 六段分析 → 调
  `push_report.py --mode alert` 推送。无告警保持静默。
- **PushPlus**：微信推送通道。token 仅保存在本机 `%LOCALAPPDATA%\PCMonitor\config.json`，
  **不提交到仓库**；获取与配置方法见 PUSHPLUS.md。
