# -*- coding: utf-8 -*-
"""备份数据库 + docker compose 重建容器"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

# 1) 重建前先备份数据库（VACUUM INTO 原子备份）
cmd = ("cd /opt/quiz-system/quiz-data && "
       "sqlite3 quiz.db \"VACUUM INTO 'backups/pre_rebuild_$(date +%Y%m%d_%H%M%S).db'\" 2>/dev/null || "
       "cp quiz.db backups/pre_rebuild_$(date +%Y%m%d_%H%M%S).db; "
       "echo '备份完成'; ls -la backups/ | tail -3")
stdin, stdout, stderr = client.exec_command(cmd)
print("===== 重建前备份 =====")
print(stdout.read().decode("utf-8", "ignore"))

# 2) docker compose 重建容器（用新镜像）
cmd = "cd /opt/quiz-system && docker compose up -d 2>&1"
stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
print("===== docker compose up -d =====")
print(stdout.read().decode("utf-8", "ignore"))
err = stderr.read().decode().strip()
if err:
    print("stderr:", err[:500])

client.close()
