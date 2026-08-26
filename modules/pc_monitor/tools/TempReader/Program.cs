using System;
using System.IO;
using System.Text;
using LibreHardwareMonitor.Hardware;

class UpdateVisitor : IVisitor
{
    public void VisitComputer(IComputer computer) { computer.Traverse(this); }
    public void VisitHardware(IHardware hardware)
    {
        hardware.Update();
        foreach (var sub in hardware.SubHardware) sub.Update();
    }
    public void VisitSensor(ISensor sensor) { }
    public void VisitParameter(IParameter parameter) { }
}

class Program
{
    /// <summary>
    /// 清洗 JSON key: 移除引号、反斜杠及所有控制字符(如 \0、\r、\n)。
    /// 某些存储设备的传感器名可能包含控制字符, 会导致下游 json.loads 失败。
    /// </summary>
    static string SanitizeKey(string key)
    {
        if (key == null) return "";
        var sb = new StringBuilder(key.Length);
        foreach (char c in key)
        {
            if (char.IsControl(c)) continue;
            if (c == '"') { sb.Append('\''); continue; }
            if (c == '\\') { sb.Append('/'); continue; }
            sb.Append(c);
        }
        return sb.ToString();
    }

    /// <summary>
    /// 读取 WMI 热区温度 (MSAcpi_ThermalZoneTemperature)。
    /// 只需管理员权限、不依赖 LHM 驱动，因此在 HVCI 拦截 LHM 时仍可读 CPU 温度。
    /// 实现: 调用系统自带 Windows PowerShell 的 Get-CimInstance (避开 .NET 10 System.Management 库的 PlatformNotSupported 问题)。
    /// 返回字典: key = "WmiThermalZone|<InstanceName>|Current", value = 摄氏度。
    /// 读取失败时返回空字典。
    /// </summary>
    static System.Collections.Generic.Dictionary<string, double> ReadWmiThermalZones(System.Text.StringBuilder dbg)
    {
        var zones = new System.Collections.Generic.Dictionary<string, double>();
        try
        {
            string psCmd = "Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop " +
                "| ForEach-Object { $_.InstanceName + '=' + $_.CurrentTemperature }";
            var psi = new System.Diagnostics.ProcessStartInfo
            {
                FileName = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),
                    "WindowsPowerShell", "v1.0", "powershell.exe"),
                Arguments = "-NoProfile -NonInteractive -Command \"" + psCmd.Replace("\"", "\\\"") + "\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            string stdout, stderr;
            using (var p = System.Diagnostics.Process.Start(psi))
            {
                stdout = p.StandardOutput.ReadToEnd();
                stderr = p.StandardError.ReadToEnd();
                if (!p.WaitForExit(8000)) { try { p.Kill(); } catch { } }
            }
            if (dbg != null && !string.IsNullOrWhiteSpace(stderr)) dbg.AppendLine("WMI stderr: " + stderr.Trim());
            foreach (var raw in stdout.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                var line = raw.Trim();
                int eq = line.LastIndexOf('=');
                if (eq <= 0) continue;
                string inst = line.Substring(0, eq);
                if (!double.TryParse(line.Substring(eq + 1).Trim(), System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out double deciKelvin))
                    continue;
                double celsius = (deciKelvin - 2732.0) / 10.0;
                if (celsius >= 0 && celsius <= 200)
                    zones["WmiThermalZone|" + inst.Replace("\"", "'").Replace("\\", "/") + "|Current"] = Math.Round(celsius, 1);
            }
            if (dbg != null) dbg.AppendLine($"WMI thermal zones found: {zones.Count}");
        }
        catch (Exception ex)
        {
            if (dbg != null) dbg.AppendLine("WMI read failed: " + ex.ToString());
        }
        return zones;
    }

    static int Main(string[] args)
    {
        bool debug = Array.IndexOf(args, "--debug") >= 0;
        bool wmiOnly = Array.IndexOf(args, "--wmi") >= 0;
        string outFile = null;
        int idx = Array.IndexOf(args, "--out");
        if (idx >= 0 && idx + 1 < args.Length) outFile = args[idx + 1];

        var output = new StringBuilder();

        // --wmi 模式: 只读 WMI 热区, 用于探测/诊断 (HVCI 环境下 CPU 温度验证)
        if (wmiOnly)
        {
            var dbg = debug ? output : null;
            var zones = ReadWmiThermalZones(debug ? output : null);
            if (debug)
            {
                foreach (var kv in zones) output.AppendLine($"   {kv.Key} = {kv.Value}");
            }
            else
            {
                output.Append('{');
                bool f = true;
                foreach (var kv in zones)
                {
                    if (!f) output.Append(',');
                    f = false;
                    output.Append('"').Append(kv.Key).Append("\":").Append(kv.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
                }
                output.Append('}');
            }
            if (outFile != null) File.WriteAllText(outFile, output.ToString());
            else Console.Write(output.ToString());
            return 0;
        }

        var computer = new Computer
        {
            IsCpuEnabled = true,
            IsMotherboardEnabled = true,
            IsGpuEnabled = true,
            IsControllerEnabled = true,
            IsStorageEnabled = true
        };
        try
        {
            computer.Open();
            computer.Traverse(new UpdateVisitor());
            if (debug)
            {
                foreach (var hw in computer.Hardware)
                {
                    output.AppendLine($"HW: {hw.HardwareType} | {hw.Name}");
                    foreach (var sensor in hw.Sensors)
                        output.AppendLine($"   {sensor.SensorType} | {sensor.Name} = {sensor.Value}");
                    foreach (var sub in hw.SubHardware)
                    {
                        output.AppendLine($"  SUB: {sub.HardwareType} | {sub.Name}");
                        foreach (var sensor in sub.Sensors)
                            output.AppendLine($"     {sensor.SensorType} | {sensor.Name} = {sensor.Value}");
                    }
                }
            }
            else
            {
                output.Append('{');
                bool first = true;
                foreach (var hw in computer.Hardware)
                {
                    foreach (var sensor in hw.Sensors)
                    {
                        if (sensor.SensorType != SensorType.Temperature) continue;
                        if (sensor.Value == null) continue;
                        string key = SanitizeKey(hw.HardwareType + "|" + hw.Name + "|" + sensor.Name);
                        if (!first) output.Append(',');
                        first = false;
                        output.Append('"').Append(key).Append("\":").Append(sensor.Value.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    }
                }
                // 合并 WMI 热区温度 (HVCI 环境下 LHM 读不到 CPU 时的补充来源)
                var wmiZones = ReadWmiThermalZones(null);
                foreach (var kv in wmiZones)
                {
                    if (!first) output.Append(',');
                    first = false;
                    output.Append('"').Append(kv.Key).Append("\":").Append(kv.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
                }
                output.Append('}');
            }
        }
        catch (Exception ex) { output.Append("ERROR: ").Append(ex.Message); }
        finally { try { computer.Close(); } catch { } }

        if (outFile != null)
            File.WriteAllText(outFile, output.ToString());
        else
            Console.Write(output.ToString());
        return 0;
    }
}
