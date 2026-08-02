# -*- coding: utf-8 -*-
"""移除旧的 docker run 容器 + compose 重建"""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

# 1) 停止并移除旧容器（数据在卷 quiz-data 里，不受影响，且已备份）
cmd = "docker stop quiz-system && docker rm quiz-system && echo '旧容器已移除'"
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print("===== 移除旧容器 =====")
print(stdout.read().decode("utf-8", "ignore"))
err = stderr.read().decode().strip()
if err:
    print("stderr:", err[:300])

# 2) compose 重建（新镜像 + 含 QUIZ_REGKEY 的配置）
cmd = "cd /opt/quiz-system && docker compose up -d 2>&1"
stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
print("===== docker compose up -d =====")
print(stdout.read().decode("utf-8", "ignore"))

# 3) 等容器起来
time.sleep(5)
cmd = "docker ps --format '{{.Names}} | {{.Status}} | {{.Image}}'"
stdin, stdout, stderr = client.exec_command(cmd)
print("===== 容器状态 =====")
print(stdout.read().decode("utf-8", "ignore"))

client.close()
