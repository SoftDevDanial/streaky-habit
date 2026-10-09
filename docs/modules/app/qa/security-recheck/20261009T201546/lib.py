"""Shared helpers for the security re-check probes (app module). Read-only against the app.

Every probe starts its own `python -m http.server <free port> --bind 127.0.0.1` from the project root, prints the
PID, and stops it by exact PID in a finally block. Browsers are headless Chromium through Playwright. No clipboard
permission is ever granted. A probe prints to stdout and saves one JSON file (its own transcript) in this folder.
Run with: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <probe>.py   (cwd = project root)
"""
import csv
import io
import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("{workspace}/examples/streaks")
HERE = pathlib.Path(__file__).resolve().parent
KEY = "streaks.state"
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"

SAMPLE = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))
SAMPLE_HABITS = SAMPLE["habits"]


def state_text(habits):
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


SEED = state_text(SAMPLE_HABITS)


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


def process_set():
    """Every (pid, image name) tasklist shows. Used as a before and after diff so only PIDs this run created are named."""
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=60).stdout
    found = set()
    for row in csv.reader(io.StringIO(out)):
        if len(row) >= 2 and row[1].isdigit() and row[0].lower() != "tasklist.exe":
            found.add((int(row[1]), row[0]))
    return found


class Server:
    """A static http.server on a free 127.0.0.1 port, started from the project root, stopped by exact PID."""

    def __init__(self):
        self.proc = None
        self.port = None

    def start(self):
        self.port = free_port()
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port), "--bind", "127.0.0.1"],
            cwd=str(ROOT),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        deadline = time.monotonic() + 15
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


class Run:
    """Context manager: server + playwright + headless chromium, PIDs reported, everything stopped on exit.

    `say` prints and keeps the line; `finish(name)` saves the kept lines as JSON in this folder.
    """

    def __init__(self):
        self.server = Server()
        self.before = set()
        self.lines = []

    def say(self, text=""):
        print(text, flush=True)
        self.lines.append(text)

    def __enter__(self):
        self.before = process_set()
        self.server.start()
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        new = process_set() - self.before
        print(f"[browser] headless chromium launched; new pids after launch: {sorted(f'{p}:{n}' for p, n in new)}", flush=True)
        self.started = {p for p, _ in new}
        return self

    @property
    def base(self):
        return self.server.base

    def finish(self, name):
        (HERE / f"out_{name}.json").write_text(json.dumps({"probe": name, "lines": self.lines}, indent=1), encoding="utf-8")

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
        left = sorted(f"{p}:{n}" for p, n in process_set() - self.before)
        mine = sorted(f"{p}:{n}" for p, n in process_set() if p in self.started)
        print(f"[processes] created during this run and still alive: {left}; of the ones this run started, alive: {mine}", flush=True)
        return False


# Records, from the very first capture point (window), every click-ish event with the browser's own event time, and
# whether the click reached the window's bubble phase (a click a page guard stopped does not) and whether it was
# cancelled by then. It never changes an event. This is the probe's, not the app's.
EVENT_LOG = r"""
(() => {
  window.__ev = [];
  const desc = (t) => {
    if (!t || !t.tagName) return String(t);
    const cls = typeof t.className === 'string' && t.className ? '.' + t.className.split(' ').join('.') : '';
    return t.tagName.toLowerCase() + cls + (t.id ? '#' + t.id : '');
  };
  const byEvent = new WeakMap();
  for (const type of ['pointerdown', 'pointerup', 'mousedown', 'mouseup', 'click', 'dblclick', 'keydown', 'keyup']) {
    window.addEventListener(type, (e) => {
      const rec = { type, t: Math.round(e.timeStamp * 10) / 10, d: e.detail, x: e.clientX, y: e.clientY,
        target: desc(e.target), key: e.key || '', pt: e.pointerType || '' };
      byEvent.set(e, rec);
      window.__ev.push(rec);
    }, true);
    window.addEventListener(type, (e) => {
      const rec = byEvent.get(e);
      if (rec) { rec.reached = true; rec.cancelled = e.defaultPrevented; }
    }, false);
  }
})();
"""


def make_context(browser, viewport, touch=False, clock="install", **kw):
    options = dict(viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1,
                   color_scheme="light", timezone_id=TZ, locale="en-US")
    if touch:
        options.update(has_touch=True, is_mobile=True)
    options.update(kw)
    ctx = browser.new_context(**options)  # no permissions are granted, so no clipboard access exists
    ctx.set_default_timeout(8000)
    ctx.set_default_navigation_timeout(20000)
    if clock == "install":
        ctx.clock.install(time=NOON)
    elif clock == "fixed":
        ctx.clock.set_fixed_time(NOON)
    ctx.add_init_script(EVENT_LOG)
    return ctx


def open_app(browser, base, viewport=(1440, 900), touch=False, seed=SEED, clock="install"):
    ctx = make_context(browser, viewport, touch, clock)
    page = ctx.new_page()
    if seed is not None:
        page.goto(base + "__seed__")  # a same-origin 404 page, only to reach the origin's localStorage
        page.evaluate("(t) => localStorage.setItem('streaks.state', t)", seed)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console:" + m.text) if m.type == "error" else None)
    page.goto(base)
    page.wait_for_selector("li.habit")
    page.errors = errors
    return ctx, page


def reseed(page, seed=SEED):
    """Put the stored state back and reload, so the next trial starts clean on the same context."""
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", seed)
    page.reload()
    page.wait_for_selector("li.habit")


SNAP_JS = """() => ({
  names: [...document.querySelectorAll('h3.habit-name')].map((e) => e.textContent),
  pressed: [...document.querySelectorAll('li.habit')].map((r) => [...r.querySelectorAll('button.day')].filter((b) => b.getAttribute('aria-pressed') === 'true').length),
  open: document.querySelector('dialog').open,
  stored: localStorage.getItem('streaks.state'),
  active: document.activeElement ? ((document.activeElement.tagName + '.' + (document.activeElement.className || '')) + ' ' + (document.activeElement.getAttribute('aria-label') || document.activeElement.textContent || '').slice(0, 30)) : null,
})"""


def snap(page):
    return page.evaluate(SNAP_JS)


def verdict(before, after):
    """What a gesture did to the habits, the ticks, the stored text and the dialog."""
    notes = []
    if len(after["names"]) != len(before["names"]):
        notes.append(f"HABITS {len(before['names'])}->{len(after['names'])} (deleted {sorted(set(before['names']) - set(after['names']))})")
    elif after["pressed"] != before["pressed"]:
        notes.append(f"TICKS {before['pressed']}->{after['pressed']}")
    if after["stored"] != before["stored"]:
        notes.append("STORAGE CHANGED")
    notes.append("dialog open" if after["open"] else "dialog closed")
    return "; ".join(notes)


def events(page, types=("click",)):
    return page.evaluate("(types) => (window.__ev || []).filter((e) => types.includes(e.type))", list(types))


def fmt_clicks(evs):
    parts = []
    for e in evs:
        flag = "" if e.get("reached") else " STOPPED"
        if e.get("reached") and e.get("cancelled"):
            flag = " CANCELLED"
        parts.append(f"t={e['t']} d={e['d']} {e['target']}{flag}")
    return " | ".join(parts)


def centre(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def press(page, x, y, touch, count=1):
    """One mouse press and release (with the click count `count`, so `detail` is `count`), or one tap."""
    if touch:
        page.touchscreen.tap(x, y)
        return
    page.mouse.move(x, y)
    page.mouse.down(click_count=count)
    page.mouse.up(click_count=count)


def double(page, x, y, touch, gap_ms=0):
    """A double click (the second press has click count 2) or a double tap, `gap_ms` between the two."""
    press(page, x, y, touch, 1)
    if gap_ms:
        page.wait_for_timeout(gap_ms)
    press(page, x, y, touch, 2)


def box(page, selector):
    return page.locator(selector).first.bounding_box()


def overlap_of(a, b):
    left, right = max(a["x"], b["x"]), min(a["x"] + a["width"], b["x"] + b["width"])
    top, bottom = max(a["y"], b["y"]), min(a["y"] + a["height"], b["y"] + b["height"])
    return (left, top, right, bottom) if right > left and bottom > top else None


def geometry(browser, base, viewport, touch, row=3):
    """Trash box of the `row`th habit, the dialog's boxes while it is open (after the fade), and their overlap.

    Uses a throwaway page, so the page under test is never touched.
    """
    ctx, page = open_app(browser, base, viewport, touch)
    try:
        trash = page.locator(f"li.habit:nth-child({row}) .icon-btn")
        t = trash.bounding_box()
        trash.click()
        page.wait_for_selector("dialog[open]")
        page.wait_for_timeout(450)
        danger = box(page, "dialog .btn-danger")
        cancel = box(page, "dialog .btn-secondary")
        dlg = box(page, "dialog")
        page.keyboard.press("Escape")
        return {"trash": t, "danger": danger, "cancel": cancel, "dialog": dlg, "overlap": overlap_of(t, danger)}
    finally:
        ctx.close()
