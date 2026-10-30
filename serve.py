# -*- coding: utf-8 -*-
"""
本地启动器：为 site/ 目录起一个静态 HTTP 服务并自动打开浏览器。

为什么必须起服务、不能直接双击 index.html：
  1) 页面用的是 <script type="module">，浏览器在 file:// 协议下会以 CORS 为由拒绝加载模块；
  2) 游戏用 CacheStorage 缓存图片并按 sha256 校验，该 API 在 file:// 下不可用。
所以用本地 127.0.0.1 的 HTTP 服务来跑，效果与线上一致。

只用标准库，不装任何依赖。
"""
import os
import socket
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
PREFERRED_PORT = 8123

# Windows 自带的 mime 表缺项会让浏览器用错解码器（webp 当二进制、m4a 当文件下载），这里补齐
MIME = {
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
}


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, **MIME}

    def end_headers(self):
        # 本地镜像不做缓存，改了文件刷新即生效
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # 只留下错误，正常的 200 不刷屏
        if str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def pick_port():
    """优先 8123；被占用（比如已经开着一份）就换随机空闲端口。

    注意：探测时不能设 SO_REUSEADDR —— Windows 上它允许绑定到他人已在监听的端口，
    会让两份服务抢占同一端口，表现为「一半资源 404」这种难查的问题。
    """
    for port in (PREFERRED_PORT, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                continue
            return s.getsockname()[1]
    raise SystemExit("找不到可用端口")


def main():
    if not os.path.isdir(ROOT):
        raise SystemExit("找不到 site 目录：%s" % ROOT)

    # 同上：Windows 下允许复用地址会掩盖「端口已被占用」的真实错误
    ThreadingHTTPServer.allow_reuse_address = False

    port = pick_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=ROOT))
    url = "http://127.0.0.1:%d/" % port

    print("=" * 46)
    print(" 勇者奶蛙传 · 本地版")
    print(" 地址: %s" % url)
    print(" 关掉这个窗口 = 停止游戏服务")
    print("=" * 46)

    if "--no-open" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
