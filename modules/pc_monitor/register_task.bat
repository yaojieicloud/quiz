@echo off
REM ============================================================
REM  PC Monitor startup task registration
REM  Must run as Administrator (needed for CPU temp reading)
REM ============================================================
setlocal
set BASE=%LOCALAPPDATA%\PCMonitor
set PYW=%BASE%\venv\Scripts\pythonw.exe
set MON=%BASE%\monitor.py

echo [1/2] Registering task PCMonitor_Main (at logon, highest privileges)...
schtasks /Create /TN "PCMonitor_Main" /TR "\"%PYW%\" \"%MON%\"" /SC ONLOGON /RL HIGHEST /F
if errorlevel 1 (
    echo FAILED. Please run this script as Administrator.
    pause
    exit /b 1
)

echo [2/2] Setting auto-restart on failure...
schtasks /Change /TN "PCMonitor_Main" /RI 1 /K

echo.
echo Registered. Starting now to verify...
schtasks /Run /TN "PCMonitor_Main"
timeout /t 5 /nobreak >nul
tasklist /FI "IMAGENAME eq pythonw.exe" | findstr pythonw >nul
if not errorlevel 1 (
    echo [OK] Monitor process is running in background.
) else (
    echo [WARN] pythonw not detected. Check %BASE%\logs\service.log
)

echo.
echo Done. Logs at: %BASE%\logs
REM (automated run - no pause)
