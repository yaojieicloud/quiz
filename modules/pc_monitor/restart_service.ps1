# Restart PC Monitor service (kill old pythonw, re-run scheduled task)
$ErrorActionPreference = "SilentlyContinue"
# Kill all pythonw processes that belong to PCMonitor
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
    Write-Output "killed pythonw pid $($_.ProcessId)"
}
Start-Sleep -Seconds 2
# Re-run the scheduled task
schtasks /Run /TN "PCMonitor_Main" | Out-Null
Start-Sleep -Seconds 6
# Verify
$procs = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'"
Write-Output "pythonw count after restart: $($procs.Count)"
foreach ($p in $procs) { Write-Output "  pid=$($p.ProcessId) start=$($p.CreationDate)" }
# Write report
$rep = "$env:LOCALAPPDATA\PCMonitor\logs\restart_report.txt"
"restart at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content $rep
"pythonw_count=$($procs.Count)" | Add-Content $rep
