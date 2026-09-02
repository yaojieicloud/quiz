"""课本 URL 代理：反向代理整站，绕开 CDN Referer ACL（REQ-7）

前端 iframe 的 Referer 是自己的域（localhost），被 PEP CDN 防盗链拦。
本端点支持两种调用：
  1. /api/proxy/book?url=https://book.pep.com.cn/.../mobile/index.html
     → 抓 HTML，里面 <link>/<script> 资源被前端的拦截器改写成 ?url=...
  2. /api/proxy/book?url=https%3A%2F%2Fbook.pep.com.cn%2Fstyle%2Fplayer.css
     → 直接抓静态资源

后端带正确 Referer 重新请求，再把内容透传。
"""
import re
import httpx
from fastapi import APIRouter, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api/proxy", tags=["课本代理"])

PEP_BOOK_HOST = "book.pep.com.cn"
ALLOWED_ORIGIN = "https://book.pep.com.cn"


def _validate_url(url: str) -> str | None:
    """只允许代理 book.pep.com.cn 域名，返回合法 url 或 None。"""
    if not url.startswith(f"{ALLOWED_ORIGIN}/") and url != ALLOWED_ORIGIN:
        return None
    return url


@router.get("/book")
async def proxy_book(url: str = Query(..., description="book.pep.com.cn 下的完整 URL")):
    """
    反向代理：支持整站所有资源（HTML/css/js/png 等）。
    每个请求的 Referer 设为请求目标本身，绕过 CDN 的 Referer ACL。
    HTML 资源：把子资源路径改写成走本代理。
    """
    target = _validate_url(url)
    if not target:
        return Response(content="只允许代理 book.pep.com.cn 域名", status_code=403)

    # CDN 要求 Referer 是被请求页面本身，不是根域名
    headers = {"Referer": target}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(target, headers=headers)

    content_type = resp.headers.get("content-type", "application/octet-stream")

    # 仅 HTML 处理：把子资源路径改写成走代理
    if "text/html" in content_type:
        html = resp.text

        def replace_relative(match):
            tag_full = match.group(0)
            attr = match.group(1)
            quote = match.group(2)
            val = match.group(3)
            if val.startswith(("http://", "https://", "data:", "#", "javascript:")):
                return tag_full
            # 解析为完整 URL
            if val.startswith("//"):
                full = "https:" + val
            elif val.startswith("/"):
                full = ALLOWED_ORIGIN + val
            else:
                from urllib.parse import urljoin
                full = urljoin(target, val)
            if not full.startswith(ALLOWED_ORIGIN):
                return tag_full
            # URL 编码：& → %26
            new_val = "/api/proxy/book?url=" + full.replace("&", "%26")
            return tag_full.replace(f'{attr}={quote}{val}{quote}',
                                   f'{attr}={quote}{new_val}{quote}')

        pattern = re.compile(r'(href|src)=(["\'])([^"\']*?)\2')
        html = pattern.sub(replace_relative, html)

        return Response(content=html, media_type=content_type)

    return Response(
        content=resp.content,
        media_type=content_type.split(";")[0].strip(),
    )

