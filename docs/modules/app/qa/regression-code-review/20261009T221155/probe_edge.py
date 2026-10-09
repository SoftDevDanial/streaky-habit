"""Is the 500 ms edge of the SEC-01 guards pinnable by a test, and which constant mutants would a pinned edge kill?

The suite's two window-edge tests click 400 ms and 600 ms after the opening (or closing) click, so any window length from
401 to 600 ms passes them. This probe clicks at 400, 499, 500, 501 and 600 ms under a paused Playwright clock (the same
setup as the suite: install_time at noon, pause_at 12:00:20, run_for to move on) against the pristine app.js and against
four mutants served from memory by page.route (no project file is written):
  baseline          DIALOG_GUARD_MS = 500, withinGuard uses <
  guard-450         DIALOG_GUARD_MS = 450
  guard-600         DIALOG_GUARD_MS = 600
  guard-le          withinGuard uses <=
  guard-mouse-only  "Delete habit" is held only for a mouse or touch click (event.detail > 0)
Three trials per cell:
  delete-guard      open the dialog with a mouse click, run_for(d), click "Delete habit": through = the delete happened
  page-guard        open the dialog, close it with a click on the backdrop, run_for(d), click today's bead of the 2nd habit:
                    through = the bead was ticked
  kbd-delete-guard  open the dialog with Enter on the trash button, run_for(d), Tab to "Delete habit" and press Enter:
                    through = the delete happened (spec R13: a keyboard activation inside the window is ignored too)
The server is `python -m http.server` on a free port started from the project root and stopped by exact PID. One headless
Chromium. The clipboard is never touched.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B probe_edge.py   (any cwd)
"""
import json
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
assert (ROOT / "index.html").exists() and (ROOT / "src" / "app.js").exists(), ROOT

TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"
PAUSE_AT = "2026-10-08T12:00:20+08:00"
SAMPLE = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))
SEED = json.dumps({"version": 1, "habits": SAMPLE["habits"]}, separators=(",", ":"))
APP_JS = (ROOT / "src" / "app.js").read_text(encoding="utf-8")
CONFIRM_GUARD = "if (view.confirmButtonOf(event.target) && withinGuard(event, dialogOpenedAt)) event.preventDefault();"

MUTANTS = {
    "baseline": APP_JS,
    "guard-450": APP_JS.replace("const DIALOG_GUARD_MS = 500;", "const DIALOG_GUARD_MS = 450;"),
    "guard-600": APP_JS.replace("const DIALOG_GUARD_MS = 500;", "const DIALOG_GUARD_MS = 600;"),
    "guard-le": APP_JS.replace("event.timeStamp - since < DIALOG_GUARD_MS", "event.timeStamp - since <= DIALOG_GUARD_MS"),
    "guard-mouse-only": APP_JS.replace(CONFIRM_GUARD, CONFIRM_GUARD.replace("if (view", "if (event.detail > 0 && view")),
}
for name, text in MUTANTS.items():
    assert (name == "baseline") == (text == APP_JS), f"mutant {name} did not change app.js"

OFFSETS = [400, 499, 500, 501, 600]


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


def center(locator):
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def open_page(browser, base, app_js):
    context = browser.new_context(
        viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="light", timezone_id=TZ, locale="en-US"
    )
    context.set_default_timeout(5000)
    context.clock.install(time=NOON)
    page = context.new_page()
    page.goto(base + "__seed__")
    page.evaluate("(text) => localStorage.setItem('streaks.state', text)", SEED)
    if app_js is not APP_JS:
        page.route("**/src/app.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=app_js))
    page.goto(base)
    page.wait_for_selector("li.habit")
    page.clock.pause_at(PAUSE_AT)
    return context, page


def settle_dialog(page):
    page.wait_for_selector("dialog.dialog[open]")
    page.locator("dialog.dialog").evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")


def open_dialog(page, name):
    page.mouse.click(*center(page.get_by_role("button", name=f"Delete {name}", exact=True)))
    settle_dialog(page)


def rows(page):
    return page.evaluate("() => document.querySelectorAll('li.habit').length")


def delete_guard_trial(browser, base, app_js, offset):
    context, page = open_page(browser, base, app_js)
    try:
        open_dialog(page, "Stretch 10 minutes")
        page.clock.run_for(offset)
        page.mouse.click(*center(page.locator("dialog.dialog").get_by_role("button", name="Delete habit", exact=True)))
        time.sleep(0.25)
        return rows(page) == 2
    finally:
        context.close()


def kbd_delete_guard_trial(browser, base, app_js, offset):
    context, page = open_page(browser, base, app_js)
    try:
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).focus()
        page.keyboard.press("Enter")
        settle_dialog(page)
        page.clock.run_for(offset)
        page.keyboard.press("Tab")
        focused = page.evaluate("() => document.activeElement.textContent.trim()")
        assert focused == "Delete habit", focused
        page.keyboard.press("Enter")
        time.sleep(0.25)
        return rows(page) == 2
    finally:
        context.close()


def page_guard_trial(browser, base, app_js, offset):
    context, page = open_page(browser, base, app_js)
    try:
        open_dialog(page, "Read 20 pages")
        page.mouse.click(5, 5)
        time.sleep(0.25)
        assert page.evaluate("() => !document.querySelector('dialog.dialog').open")
        bead = page.locator("li.habit").nth(1).locator('button.day[data-date="2026-10-08"]')
        before = bead.get_attribute("aria-pressed")
        page.clock.run_for(offset)
        page.mouse.click(*center(bead))
        time.sleep(0.25)
        return bead.get_attribute("aria-pressed") != before
    finally:
        context.close()


def main():
    port = free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(ROOT), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    print(f"[server] started http.server pid {server.pid} on 127.0.0.1:{port}", flush=True)
    playwright = browser = None
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1).close()
                break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("server did not start")
        base = f"http://127.0.0.1:{port}/"
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        print(f"[browser] headless chromium {browser.version}", flush=True)
        print("cell = 'through' when the second click or press got past the guard, 'held' when it was ignored.\n")
        print("mutant           trial             " + "".join(f"{d:>9}" for d in OFFSETS))
        for name, app_js in MUTANTS.items():
            for label, trial in (
                ("delete-guard", delete_guard_trial),
                ("page-guard", page_guard_trial),
                ("kbd-delete-guard", kbd_delete_guard_trial),
            ):
                cells = ["through" if trial(browser, base, app_js, offset) else "held" for offset in OFFSETS]
                print(f"{name:<16} {label:<17} " + "".join(f"{c:>9}" for c in cells), flush=True)
        print("\nexpected for the 500 ms spec (R13): held at 400 and 499, through at 500, 501 and 600.")
    finally:
        if browser is not None:
            browser.close()
        if playwright is not None:
            playwright.stop()
        if server.poll() is None:
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"], capture_output=True, timeout=15)
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        deadline = time.monotonic() + 10
        while port_open(port) and time.monotonic() < deadline:
            time.sleep(0.25)
        print(f"[server] stopped pid {server.pid}; 127.0.0.1:{port} accepts connections: {port_open(port)}", flush=True)


if __name__ == "__main__":
    main()
