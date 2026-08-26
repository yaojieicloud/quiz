# -*- coding: utf-8 -*-
import paramiko

LOCAL_TAR = r"C:\Users\Yaojie\AppData\Local\Temp\quiz-src-window.tar.gz"
ECS_HOST = "106.14.99.100"
ECS_USER = "root"
ECS_KEY = r"C:\Users\Yaojie\Documents\openclaw.pem"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ECS_HOST, 22, username=ECS_USER, key_filename=ECS_KEY, timeout=15, allow_agent=False, look_for_keys=False)

# 1) SFTP 上传
sftp = client.open_sftp()
sftp.put(LOCAL_TAR, "/opt/quiz-system/quiz-src-window.tar.gz")
st = sftp.stat("/opt/quiz-system/quiz-src-window.tar.gz")
print(f"[1] 上传完成: {st.st_size} bytes")
sftp.close()

# 2) 解压（ECS 目录扁平，无 src/ 子目录）
cmd = "cd /opt/quiz-system && tar -xzf quiz-src-window.tar.gz && ls core/mastery.py"
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print("[2] 解压:", stdout.read().decode("utf-8", "ignore")[:300])
err = stderr.read().decode("utf-8", "ignore").strip()
if err:
    print("    stderr:", err[:200])

# 3) 重建镜像（Dockerfile 在当前目录）
cmd = "cd /opt/quiz-system && docker build -t quiz-system:latest -f Dockerfile . 2>&1 | tail -10"
stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
print("[3] 构建镜像:", stdout.read().decode("utf-8", "ignore")[-500:])

# 4) 重启容器（docker compose v2）
cmd = "cd /opt/quiz-system && docker compose up -d 2>&1"
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print("[4] 重启容器:", stdout.read().decode("utf-8", "ignore"))

client.close()
print("\n部署完成！")
