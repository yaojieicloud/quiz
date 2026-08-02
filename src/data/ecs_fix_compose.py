# -*- coding: utf-8 -*-
"""补全 docker-compose.yml 的 QUIZ_REGKEY + 重建容器"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

# 1) 检查当前 compose 是否已有 QUIZ_REGKEY
stdin, stdout, stderr = client.exec_command("grep -c QUIZ_REGKEY /opt/quiz-system/docker-compose.yml || true")
cnt = stdout.read().decode().strip()
print(f"compose 中 QUIZ_REGKEY 出现次数: {cnt}")

if cnt == "0":
    # 补上 QUIZ_REGKEY（插在 QUIZ_SECRET_KEY 行后面）
    cmd = "cd /opt/quiz-system && cp docker-compose.yml docker-compose.yml.bak.$(date +%s) && sed -i '/QUIZ_SECRET_KEY/a\\      - QUIZ_REGKEY=openschool2026' docker-compose.yml && echo '已补 QUIZ_REGKEY'"
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode().strip()
    if err:
        print("stderr:", err)
else:
    print("已有 QUIZ_REGKEY，无需补充")

# 2) 确认最终 compose 内容
stdin, stdout, stderr = client.exec_command("cat /opt/quiz-system/docker-compose.yml")
print("=== 最终 docker-compose.yml ===")
print(stdout.read().decode("utf-8", "ignore"))

client.close()
