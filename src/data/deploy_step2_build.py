# -*- coding: utf-8 -*-
"""SSH 容器化部署：ECS docker build 构建新镜像"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("106.14.99.100", 22, username="root", password="Yao@123456",
               timeout=15, allow_agent=False, look_for_keys=False)

cmd = "cd /opt/quiz-system && docker build -t quiz-system:latest build/ 2>&1 | tail -12; echo BUILD_EXIT=$?"
stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
print(stdout.read().decode("utf-8", "ignore"))

stdin, stdout, stderr = client.exec_command("docker images quiz-system --format '{{.Tag}} {{.ID}} {{.Size}} {{.CreatedSince}}'", timeout=30)
print("=== 镜像列表 ===")
print(stdout.read().decode("utf-8", "ignore"))
client.close()
