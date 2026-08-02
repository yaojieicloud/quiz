# -*- coding: utf-8 -*-
"""SSH 连接 ECS 测试"""
import paramiko, socket, sys

HOST = "106.14.99.100"
USER = "root"
PASS = "QWEasd23!@#"  # 直接写在源码里，避免 shell 转义干扰

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(HOST, port=22, username=USER, password=PASS,
                   timeout=10, allow_agent=False, look_for_keys=False)
    print("SSH 连接成功!")
    stdin, stdout, stderr = client.exec_command(
        'whoami; hostname; uptime; echo "---docker---"; '
        'docker ps --format "{{.Names}} {{.Status}}" 2>/dev/null | head -5')
    print("--- 命令输出 ---")
    print(stdout.read().decode("utf-8", "ignore"))
    err = stderr.read().decode("utf-8", "ignore")
    if err.strip():
        print("stderr:", err)
    client.close()
except paramiko.AuthenticationException:
    print("X 认证失败：账号或密码错误")
except paramiko.SSHException as e:
    print(f"X SSH 错误: {e}")
except socket.timeout:
    print("X 连接超时（22端口可能未开放或被防火墙拦截）")
except Exception as e:
    print(f"X 其他错误: {type(e).__name__}: {e}")
