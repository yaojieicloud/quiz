# -*- coding: utf-8 -*-
"""SSH 容器化部署：检查 compose 配置 -> 重建容器"""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

# 1) 确认 compose 含 QUIZ_REGKEY
stdin, stdout, stderr = client.exec_command("grep -c QUIZ_REGKEY /opt/quiz-system/docker-compose.yml", timeout=10)
cnt = stdout.read().decode().strip()
print(f"[1] compose 中 QUIZ_REGKEY 出现 {cnt} 次", "✓" if cnt != "0" else "✗ 缺失!")

if cnt == "0":
    cmd = "cd /opt/quiz-system && cp docker-compose.yml docker-compose.yml.bak.$(date +%s) && sed -i '/QUIZ_SECRET_KEY/a\\      - QUIZ_REGKEY=openschool2026' docker-compose.yml"
    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
    stdout.read()
    print("    已补充 QUIZ_REGKEY")

# 2) 重建容器
stdin, stdout, stderr = client.exec_command("cd /opt/quiz-system && docker compose up -d 2>&1", timeout=120)
print("[2] compose up -d:")
print(stdout.read().decode("utf-8", "ignore"))

# 3) 等容器起来
time.sleep(6)
stdin, stdout, stderr = client.exec_command("docker ps --format '{{.Names}} | {{.Status}} | {{.Image}}'", timeout=10)
print("[3] 容器状态:")
print(stdout.read().decode("utf-8", "ignore"))

# 4) 容器内确认新代码（学情分析接口已含）
stdin, stdout, stderr = client.exec_command("docker exec quiz-system grep -c 'analytics/overview' /app/routers/admin.py", timeout=15)
print(f"[4] 容器内 admin.py 含学情分析接口: {stdout.read().decode().strip()} 处")

client.close()
