# PushPlus 推送说明

> 安全约定：**token 不入库**。真实 token 保存在本机
> `%LOCALAPPDATA%\PCMonitor\config.json` 的 `pushplus_token` 字段（该文件不在 git 仓库中）。
> 备份目录的 `config.example.json` 为模板，token 留空。

## 获取 token（首次配置或更换时）

1. 访问 http://www.pushplus.plus/ ，微信扫码登录
2. 进入「一对一推送」页面复制 token（32 位字符）
3. 微信关注公众号「pushplus推送加」（不关注收不到消息）
4. 填入 `%LOCALAPPDATA%\PCMonitor\config.json`：
   ```json
   "pushplus_token": "你的32位token",
   ```
   无需重启服务，每次推送实时读取配置。

## 调用方式

```python
import requests
requests.post("http://www.pushplus.plus/send", json={
    "token": "<token>",
    "title": "标题",
    "content": "内容",
    "template": "txt"   # txt | markdown | html
}, timeout=10)
```

注意：用 Python requests 推送（UTF-8）。PowerShell 5.1 默认 GBK 编码会导致中文乱码，
若必须用 PS，需将 body 转 UTF8 字节并设 ContentType 为 `application/json; charset=utf-8`。
