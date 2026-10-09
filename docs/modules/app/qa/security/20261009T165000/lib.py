"""Shared helpers for the security finder's probes (app module). Read-only against the app.

Every probe starts its own `python -m http.server <free port> --bind 127.0.0.1`, prints the PID, and
stops it by PID in a finally block. Probes print to stdout and write no file, except screenshots whose
path the probe names inside this folder.
Run with: PYTHONDONTWRITEBYTECODE=1 python <probe>.py   (cwd = project root)
"""
import json
import os
import pathlib
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("{workspace}/examples/streaks")
HERE = pathlib.Path(__file__).resolve().parent
KEY = "streaks.state"
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_open(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
        return True
    except OSError:
        return False


class Server:
    """A static http.server on a free 127.0.0.1 port, owned by this probe, stopped by exact PID."""

    def __init__(self, directory=ROOT):
        self.directory = directory
        self.proc = None
        self.port = None

    def start(self):
        self.port = free_port()
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port), "--bind", "127.0.0.1", "--directory", str(self.directory)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("server did not start")
        print(f"[server] started http.server pid {self.proc.pid} on 127.0.0.1:{self.port}", flush=True)
        return self

    @property
    def base(self):
        return f"http://127.0.0.1:{self.port}/"

    def stop(self):
        if self.proc is None:
            return
        pid, port = self.proc.pid, self.port
        if self.proc.poll() is None:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=15)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        deadline = time.monotonic() + 10
        while port_open(port) and time.monotonic() < deadline:
            time.sleep(0.25)
        print(f"[server] stopped pid {pid}; 127.0.0.1:{port} accepts connections: {port_open(port)}", flush=True)
        self.proc = None


class Canary:
    """In-process HTTP listener (a thread, no extra process) that records every hit.

    If the app's CSP failed to stop an outbound request to it, the hit would show here.
    It sends CORS headers so that a positive control from a CSP-free page can read the answer.
    """

    def __init__(self):
        self.hits = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _answer(self):
                outer.hits.append(f"{self.command} {self.path}")
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "image/gif")
                self.end_headers()
                self.wfile.write(b"GIF89a")

            do_GET = do_POST = do_HEAD = do_PUT = _answer

            def do_OPTIONS(self):
                outer.hits.append(f"OPTIONS {self.path}")
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "*")
                self.send_header("Access-Control-Allow-Methods", "*")
                self.end_headers()

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}/"

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def state_text(habits):
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


SAMPLE = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))
SAMPLE_HABITS = SAMPLE["habits"]


class Log:
    def __init__(self):
        self.requests = []
        self.console = []
        self.errors = []
        self.dialogs = []
        self.websockets = []
        self.workers = []

    def console_errors(self):
        return [c for c in self.console if c["type"] == "error"]


def attach(page):
    log = Log()
    page.on("request", lambda r: log.requests.append({"method": r.method, "url": r.url}))
    page.on("console", lambda m: log.console.append({"type": m.type, "text": m.text}))
    page.on("pageerror", lambda e: log.errors.append(str(e)))
    page.on("websocket", lambda w: log.websockets.append(w.url))
    page.on("worker", lambda w: log.workers.append(w.url))

    def on_dialog(d):
        log.dialogs.append({"type": d.type, "message": d.message})
        d.dismiss()

    page.on("dialog", on_dialog)
    return log


def new_context(browser, viewport=(390, 844), fixed_time=NOON, install_time=None, **kw):
    ctx = browser.new_context(
        viewport={"width": viewport[0], "height": viewport[1]},
        device_scale_factor=1,
        color_scheme="light",
        timezone_id=TZ,
        locale="en-US",
        **kw,
    )
    ctx.set_default_timeout(8000)
    ctx.set_default_navigation_timeout(20000)
    if install_time is not None:
        ctx.clock.install(time=install_time)
    elif fixed_time is not None:
        ctx.clock.set_fixed_time(fixed_time)
    return ctx


def open_app(browser, base, storage=None, viewport=(390, 844), fixed_time=NOON, install_time=None,
             init_script=None, path="", **kw):
    """New context + page; seed through the same-origin 404 page; then open the app. Returns (ctx, page, log)."""
    ctx = new_context(browser, viewport, fixed_time, install_time, **kw)
    page = ctx.new_page()
    if storage is not None:
        page.goto(base + "__seed__")
        page.evaluate("(t) => localStorage.setItem('streaks.state', t)", storage)
    if init_script is not None:
        ctx.add_init_script(init_script)
    log = attach(page)
    page.goto(base + path)
    return ctx, page, log


def stored(page):
    return page.evaluate("() => localStorage.getItem('streaks.state')")


def row_names(page):
    return page.locator("h3.habit-name").all_text_contents()


def proto_fingerprint(page):
    """Own property names of the shared prototypes, to compare against a clean baseline."""
    return page.evaluate(
        """() => ({
          object: Object.getOwnPropertyNames(Object.prototype).sort(),
          array: Object.getOwnPropertyNames(Array.prototype).sort(),
          func: Object.getOwnPropertyNames(Function.prototype).sort(),
          string: Object.getOwnPropertyNames(String.prototype).sort(),
          polluted: [({}).polluted, ({}).name, ({}).done, ({}).evil, [].polluted].map(String),
          objectProtoOfLiteral: Object.getPrototypeOf({}) === Object.prototype,
        })"""
    )


def procs_named(*_ignored):
    """Set of (pid, name) of Playwright-style browser processes (chrome, headless shell, chromium), by CIM query.

    Not edge webview (other apps own those). Used as a before/after diff, so only PIDs this probe created are ever reported.
    """
    script = "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'chrome|headless|chromium' } | ForEach-Object { '{0} {1}' -f $_.ProcessId, $_.Name }"
    out = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60).stdout
    found = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            found.add((int(parts[0]), parts[1]))
    return found


class Run:
    """Context manager: server + playwright + browser, with PIDs reported and everything stopped on exit."""

    def __init__(self, directory=ROOT, extra_servers=()):
        self.server = Server(directory)
        self.before = set()

    def __enter__(self):
        self.before = procs_named()
        self.server.start()
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        new = procs_named() - self.before
        print(f"[browser] headless chromium launched; new browser pids: {sorted(p for p, _ in new)}", flush=True)
        self.browser_pids = {p for p, _ in new}
        return self

    @property
    def base(self):
        return self.server.base

    def __exit__(self, *exc):
        try:
            self.browser.close()
        except Exception as error:  # noqa: BLE001
            print(f"[browser] close error: {error}", flush=True)
        try:
            self.pw.stop()
        except Exception as error:  # noqa: BLE001
            print(f"[playwright] stop error: {error}", flush=True)
        self.server.stop()
        time.sleep(1.0)
        left = procs_named() - self.before
        print(f"[browser] browser pids still alive from this run: {sorted(p for p, _ in left)}", flush=True)
        return False
