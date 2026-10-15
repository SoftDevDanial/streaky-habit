"""Shared helpers for the v1.1.0 security probes (security finder, read-only, 2026-10-15).

Run every probe as `python -B <probe>.py [engine]` so nothing is compiled into tests/browser/__pycache__.
Each probe prints its result to stdout; the finder saves stdout with the Write tool as <probe>.txt.
Servers: python -m http.server on 127.0.0.1 from the project root, stopped in a finally with the port checked.
Contexts: fresh, headless, the clipboard stand-in from tests/browser/conftest.py added first.
Planted values are built inside the throwaway context and never written to disk.
"""
import json
import pathlib
import socket
import subprocess
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]  # <root>/docs/modules/app/qa/security/<stamp>
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tests" / "browser"))

import conftest  # noqa: E402  read-only use: CLIPBOARD_STANDIN, launch, encode, TWELVE, SAMPLE_HABITS

CLIPBOARD_STANDIN = conftest.CLIPBOARD_STANDIN
STORAGE_KEY = "streaks.state"

# Logs every CSP violation to the console with a marker. No property is added to window.
CSP_LOGGER = """(() => {
  document.addEventListener('securitypolicyviolation', (e) => {
    console.log('csp-violation:' + e.effectiveDirective + ':' + e.blockedURI);
  }, true);
})();"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server(directory=ROOT):
    """Start python -m http.server on a free 127.0.0.1 port. Returns (proc, port, log lines)."""
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, "-B", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(directory),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = []

    def drain():
        for line in proc.stdout:
            lines.append(line.rstrip("\n"))

    threading.Thread(target=drain, daemon=True).start()
    deadline = time.time() + 10
    while not port_open(port):
        if time.time() > deadline:
            proc.kill()
            raise RuntimeError(f"server on {port} not ready, gave up after 10 s")
        time.sleep(0.25)
    print(f"[server] started pid={proc.pid} port={port} dir={directory}")
    return proc, port, lines


def stop_server(proc, port):
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
    refused = not port_open(port)
    print(f"[server] stopped pid={proc.pid} exit={proc.returncode} port {port} refuses={refused}")
    return refused


def launch(playwright, engine):
    return conftest.launch(playwright, engine)


class Session:
    """One throwaway context and page with console, error, dialog and request logs."""

    def __init__(self, browser, base, viewport=(390, 844), seed_js=None, seed_arg=None, clock=None,
                 touch=False, path="", init=None, route_log=True, timeout_ms=5000, nav_timeout_ms=10000,
                 install_clock=None):
        self.base = base
        self.ctx = browser.new_context(
            viewport={"width": viewport[0], "height": viewport[1]},
            device_scale_factor=1,
            color_scheme="dark",
            timezone_id="Asia/Kuala_Lumpur",
            locale="en-US",
            has_touch=touch,
        )
        self.ctx.add_init_script(CLIPBOARD_STANDIN)  # first, before anything else
        self.ctx.add_init_script(CSP_LOGGER)
        self.ctx.set_default_timeout(timeout_ms)
        self.ctx.set_default_navigation_timeout(nav_timeout_ms)
        if install_clock:
            self.ctx.clock.install(time=install_clock)
        elif clock:
            self.ctx.clock.set_fixed_time(clock)
        self.console, self.errors, self.dialogs, self.requests = [], [], [], []
        self.page = self.ctx.new_page()
        self.page.on("console", lambda m: self.console.append(f"{m.type}: {m.text[:300]}"))
        self.page.on("pageerror", lambda e: self.errors.append(str(e)[:300]))
        self.page.on("dialog", self._on_dialog)
        if seed_js is not None:
            self.page.goto(base + "__seed__")
            self.page.evaluate(seed_js, seed_arg)
        for script in (init or []):
            self.ctx.add_init_script(script)
        if route_log:
            self.ctx.route("**/*", self._on_route)
        self.page.goto(base + path)

    def _on_dialog(self, dialog):
        self.dialogs.append(dialog.message[:200])
        dialog.dismiss()

    def _on_route(self, route):
        req = route.request
        self.requests.append(f"{req.method} {req.url}")
        route.continue_()

    def stored(self):
        return self.page.evaluate("() => localStorage.getItem('streaks.state')")

    def csp(self):
        return [c for c in self.console if "csp-violation:" in c]

    def clipboard_marks(self):
        return [c for c in self.console if "test:clipboard:" in c]

    def close(self):
        self.ctx.close()


SEED_TEXT = "(text) => localStorage.setItem('streaks.state', text)"


def encode(habits):
    return conftest.encode(habits)


def engines_from_argv(default=("chromium", "webkit")):
    args = [a for a in sys.argv[1:] if a in ("chromium", "webkit")]
    return tuple(args) or default


def dump(obj):
    return json.dumps(obj, ensure_ascii=True)
