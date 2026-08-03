# -*- coding: utf-8 -*-
"""SSH 容器化部署：SFTP 上传 -> ECS 解压 -> docker build"""
import paramiko

LOCAL_TAR = r"C:\Users\Yaojie\AppData\Local\Temp\quiz-src.tar.gz"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

# 1) SFTP 上传
sftp = client.open_sftp()
sftp.put(LOCAL_TAR, "/opt/quiz-system/quiz-src.tar.gz")
st = sftp.stat("/opt/quiz-system/quiz-src.tar.gz")
print(f"[1] 上传完成: {st.st_size} bytes")
sftp.close()

# 2) 解压（清旧 build 目录）
cmd = "cd /opt/quiz-system && rm -rf build && mkdir -p build && tar -xzf quiz-src.tar.gz -C build && ls build/ | head -15"
stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
print("[2] 解压:", stdout.read().decode("utf-8", "ignore")[:300])
err = stderr.read().decode("utf-8", "ignore").strip()
if err:
    print("    stderr:", err[:200])

client.close()
