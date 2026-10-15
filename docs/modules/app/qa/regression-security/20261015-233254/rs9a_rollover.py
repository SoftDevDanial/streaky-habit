"""Re-check of task 9a. The midnight into a far day with a year view open, no press during the change of day.

Security finder (read-only), re-check 2026-10-15. Run: timeout 400 python -u -B rs9a_rollover.py <chromium|webkit>
Every case is its own headless browser and context (lib.Session, the clipboard stand-in first, UTC+8). The clock is
installed with Playwright's clock API at 23:59:40 of the day before and runs in real time. The app's day check runs
every 30 s from boot, so it passes midnight within the wait. All cases are set up first, then one real-time wait of
WAIT_S, then each page is read with a 3 s timeout (answers=false means frozen). Browsers closed in finally.
How a year view is opened before midnight:
  P4 x2   the band's Year twice. On a January to September clock of a five digit year the first press throws and
          the second opens P4 on the layout left behind (the path of the old no-press freeze, probe_14)
  P4      the band's Year once
  P2      the row's Year once
Prints JSON lines, writes no file.
"""
import json
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout  # noqa: E402
from probe_11_year10000 import epoch_s  # noqa: E402
from rs9a_views import YEAR, BASE  # noqa: E402

WAIT_S = 50
CASES = [
    ("control, nothing open, into 10000-10-01", (10000, 9, 30), None),
    ("P4 open (two presses), into 10000-10-01", (10000, 9, 30), "P4 x2"),
    ("P2 open (two presses), into 10000-10-01", (10000, 9, 30), "P2 x2"),
    ("P4 open, into 10000-11-01", (10000, 10, 31), "P4"),
    ("P2 open, into 10000-11-01", (10000, 10, 31), "P2"),
    ("P4 open, into 10001-01-01", (10000, 12, 31), "P4"),
    ("P4 open (two presses), into 10009-10-01", (10009, 9, 30), "P4 x2"),
    ("P4 open (two presses), into 10010-10-01", (10010, 9, 30), "P4 x2"),
    ("P4 open, into 10000-01-01 (control of the old rollover)", (9999, 12, 31), "P4"),
]
OPENERS = {"P4": "section.band button.btn-all", "P2": "ul.rows > li.row button.btn-year"}
DIALOG = {"P4": "dialog.dlg-all", "P2": "dialog.dlg-year"}


def read(page, expr, arg=None):
    try:
        return True, page.wait_for_function(expr, arg=arg, timeout=3000).json_value()
    except PlaywrightTimeout:
        return False, None


def click(page, selector):
    try:
        page.click(selector, timeout=3000, no_wait_after=True)
    except PlaywrightTimeout:
        return "timed out"
    return "returned"


def short(snap):
    if not snap:
        return None
    t = snap.get("titles") or []
    return {"isOpen": snap.get("isOpen"), "months": snap.get("months"), "first": t[0] if t else None,
            "last": t[-1] if t else None, "daysPerMonth": snap.get("daysPerMonth"), "openControls": snap.get("openControls"),
            "closed": snap.get("closed"), "blank": snap.get("blank")}


def main():
    engine = sys.argv[1]
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    live = []
    try:
        with sync_playwright() as p:
            try:
                for case, (y, m, d), how in CASES:
                    browser = lib.launch(p, engine)
                    s = lib.Session(browser, base, viewport=(1280, 800), install_clock=epoch_s(y, m, d, 23, 59, 40))
                    live.append((case, how, browser, s))
                    s.page.fill("#nh", "Read", timeout=3000)
                    s.page.press("#nh", "Enter", timeout=3000)
                    if how:
                        kind = how.split()[0]
                        click(s.page, OPENERS[kind])
                        if how.endswith("x2"):
                            ok, b = read(s.page, BASE)
                            if ok and b["open"]:
                                s.page.keyboard.press("Escape")
                            click(s.page, OPENERS[kind])
                    ok, b = read(s.page, BASE)
                    snap = read(s.page, YEAR, DIALOG[how.split()[0]])[1] if how else None
                    print(json.dumps({"engine": engine, "case": case, "step": "before midnight", "answers": ok,
                                      "header": (b or {}).get("header"), "open": (b or {}).get("open"), "view": short(snap),
                                      "pageErrors": len(s.errors), "lastError": s.errors[-1][:90] if s.errors else None}), flush=True)
                t0 = time.time()
                time.sleep(WAIT_S)
                print(json.dumps({"engine": engine, "step": f"waited {round(time.time() - t0, 1)} s of real time"}), flush=True)
                for case, how, browser, s in live:
                    t1 = time.time()
                    ok, b = read(s.page, BASE)
                    snap = read(s.page, YEAR, DIALOG[how.split()[0]])[1] if (how and ok) else None
                    print(json.dumps({"engine": engine, "case": case, "step": "after midnight", "answers": ok,
                                      "answerSeconds": round(time.time() - t1, 2), "header": (b or {}).get("header"),
                                      "open": (b or {}).get("open"), "stored": (b or {}).get("stored"), "view": short(snap),
                                      "pageErrors": len(s.errors), "lastError": s.errors[-1][:90] if s.errors else None}), flush=True)
            finally:
                for case, how, browser, s in live:
                    t2 = time.time()
                    browser.close()
                    print(json.dumps({"engine": engine, "case": case, "step": "browser closed", "closeSeconds": round(time.time() - t2, 2)}), flush=True)
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
