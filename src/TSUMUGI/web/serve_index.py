# serve_index.py (WSL/mac/Linux/Windows aware; English-only messages)
import contextlib
import http.server
import os
import shlex
import socket
import socketserver
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"


def is_wsl() -> bool:
    try:
        with open("/proc/sys/kernel/osrelease", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def _popen(cmdlist):
    subprocess.Popen(cmdlist, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def safe_open_url(url: str) -> None:
    """Try multiple platform-specific openers; fall back to printing the URL."""
    tried = []

    # 0) WSL FIRST (because webbrowser may mistakenly pick gio)
    if is_wsl():
        for cmd in (["wslview", url], ["explorer.exe", url], ["powershell.exe", "/c", "start", url]):
            try:
                _popen(cmd)
                return
            except Exception as e:
                tried.append(f"{' '.join(cmd)}: {e}")

    # 1) Respect $BROWSER (allow commands with args)
    browser_env = os.environ.get("BROWSER")
    if browser_env:
        try:
            cmd = shlex.split(browser_env) + [url]
            _popen(cmd)
            return
        except Exception as e:
            tried.append(f"$BROWSER({browser_env}): {e}")

    # 2) Python's webbrowser (may choose gio/xdg-open/open)
    try:
        # webbrowser may return True even if the underlying tool fails later; still worth trying.
        if webbrowser.open_new_tab(url):
            return
    except Exception as e:
        tried.append(f"webbrowser: {e}")

    # 3) macOS
    if sys.platform == "darwin":
        try:
            _popen(["open", url])
            return
        except Exception as e:
            tried.append(f"open: {e}")

    # 4) Linux/Unix (desktop)
    for cmd in (["xdg-open", url], ["gio", "open", url]):
        try:
            _popen(cmd)
            return
        except Exception as e:
            tried.append(f"{' '.join(cmd)}: {e}")

    print("Could not auto-open the browser.")
    print("Open this URL manually:", url)
    if tried:
        print("Tried:", *tried, sep="\n - ")


def find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)


def main():
    if not INDEX.exists():
        raise SystemExit("index.html not found. Place this script next to index.html.")
    port = find_free_port()
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler) as httpd:
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"Serving {ROOT} at {url}")
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        safe_open_url(url)
        try:
            threading.Event().wait()
        finally:
            httpd.shutdown()


if __name__ == "__main__":
    main()
