using System;
using System.Diagnostics;
using System.IO;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.TaskScheduler;

class Program
{
    static int Main(string[] args)
    {
        string localAppData = Environment.GetEnvironmentVariable("LOCALAPPDATA");
        string baseDir = Path.Combine(localAppData, "PCMonitor");
        string reportPath = Path.Combine(baseDir, "logs", "setup_report.txt");
        var rep = new StringBuilder();

        // --restart 模式: 杀掉所有 pythonw 监控进程并重启计划任务
        if (Array.IndexOf(args, "--restart") >= 0)
        {
            reportPath = Path.Combine(baseDir, "logs", "restart_report.txt");
            try
            {
                foreach (var p in Process.GetProcessesByName("pythonw"))
                {
                    try { p.Kill(); rep.AppendLine("killed pythonw pid=" + p.Id); }
                    catch (Exception ex) { rep.AppendLine("kill_failed pid=" + p.Id + " err=" + ex.Message); }
                }
                System.Threading.Thread.Sleep(2000);
                using (var ts = new TaskService())
                {
                    var t = ts.GetTask("PCMonitor_Main");
                    if (t != null) { t.Run(); rep.AppendLine("task_started=true"); }
                }
                System.Threading.Thread.Sleep(5000);
                var alive = Process.GetProcessesByName("pythonw");
                rep.AppendLine("pythonw_after=" + alive.Length);
                foreach (var ap in alive)
                {
                    string parent = "?";
                    try
                    {
                        using (var mo = new System.Management.ManagementObject(
                            "Win32_Process.Handle='" + ap.Id + "'"))
                        {
                            parent = mo["ParentProcessId"]?.ToString();
                        }
                    }
                    catch { }
                    rep.AppendLine("  pid=" + ap.Id + " parent=" + parent +
                        " mem_mb=" + (ap.WorkingSet64 / 1048576));
                }
                File.WriteAllText(reportPath, rep.ToString());
                return 0;
            }
            catch (Exception ex)
            {
                rep.AppendLine("ERROR: " + ex);
                try { File.WriteAllText(reportPath, rep.ToString()); } catch { }
                return 1;
            }
        }

        try
        {
            bool admin = new WindowsPrincipal(WindowsIdentity.GetCurrent())
                .IsInRole(WindowsBuiltInRole.Administrator);
            rep.AppendLine("admin=" + admin);

            // 1. 在当前(提权)权限下读取温度, 验证 CPU 温度链路
            string tempReader = Path.Combine(baseDir, "tools", "TempReader", "publish", "TempReader.exe");
            var psi = new ProcessStartInfo(tempReader)
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            using (var p = Process.Start(psi))
            {
                string output = p.StandardOutput.ReadToEnd();
                string err = p.StandardError.ReadToEnd();
                p.WaitForExit(15000);
                rep.AppendLine("temps=" + output);
                if (!string.IsNullOrWhiteSpace(err)) rep.AppendLine("temp_err=" + err);
            }

            // 2. 注册开机自启任务 (登录时启动, 最高权限, 失败自动重启)
            string pythonw = Path.Combine(baseDir, "venv", "Scripts", "pythonw.exe");
            string monitor = Path.Combine(baseDir, "monitor.py");
            using (var ts = new TaskService())
            {
                try { ts.RootFolder.DeleteTask("PCMonitor_Main", false); } catch { }
                var td = ts.NewTask();
                td.RegistrationInfo.Description = "PC Monitor service - system metrics monitoring";
                td.RegistrationInfo.Author = "PCMonitor";
                td.Principal.RunLevel = TaskRunLevel.Highest;
                td.Principal.LogonType = TaskLogonType.InteractiveToken;
                td.Triggers.Add(new LogonTrigger());
                td.Actions.Add(new ExecAction(pythonw, "\"" + monitor + "\"", baseDir));
                td.Settings.ExecutionTimeLimit = TimeSpan.Zero;
                td.Settings.DisallowStartIfOnBatteries = false;
                td.Settings.StopIfGoingOnBatteries = false;
                td.Settings.StartWhenAvailable = true;
                td.Settings.RestartInterval = TimeSpan.FromMinutes(1);
                td.Settings.RestartCount = 3;
                td.Settings.MultipleInstances = TaskInstancesPolicy.IgnoreNew;
                ts.RootFolder.RegisterTaskDefinition("PCMonitor_Main", td);
                rep.AppendLine("task_registered=true");
            }

            // 3. 立即启动任务 (IgnoreNew 策略: 已在运行则忽略)
            using (var ts = new TaskService())
            {
                var t = ts.GetTask("PCMonitor_Main");
                if (t != null)
                {
                    t.Run();
                    rep.AppendLine("task_started=true");
                }
            }

            File.WriteAllText(reportPath, rep.ToString());
            return 0;
        }
        catch (Exception ex)
        {
            rep.AppendLine("ERROR: " + ex);
            try { File.WriteAllText(reportPath, rep.ToString()); } catch { }
            return 1;
        }
    }
}
