"""Can the year 10000 October hang arrive with no press, from the midnight rollover? (CS-01 follow-up)

Security finder (read-only), regression 2026-10-15. Run: timeout 300 python -u -B probe_14_rollover_hang.py <engine>
The clock is installed at 10000-09-30 23:59:40 (UTC+8) and left to run in real time. Two contexts, each in its own
browser, closed after:
  control   no popup open. After about 35 s of real time the day check has run past midnight. The page must answer and
            show 10000-10-01.
  P4 open   the band's Year pressed twice before midnight. The first press throws (September of a five digit year),
            the second opens P4 on the layout left behind. Then the same wait, and whether the page still answers.
No Playwright call that needs the page runs during the wait (time.sleep), and every later call has a timeout.
Prints JSON lines, writes no file.
"""
import json
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout  # noqa: E402
from probe_11_year10000 import epoch_s, add  # noqa: E402

WAIT_S = 35


def answers(page):
    try:
        handle = page.wait_for_function(
            "() => ({ header: document.querySelector('header.top > time.date').getAttribute('datetime'),"
            " open: Array.from(document.querySelectorAll('dialog[open]')).map((d) => d.className).join(','),"
            " stored: localStorage.getItem('streaks.state') })", timeout=3000)
        return True, handle.json_value()
    except PlaywrightTimeout:
        return False, None


def run_case(p, engine, base, case, open_p4):
    browser = lib.launch(p, engine)
    try:
        s = lib.Session(browser, base, viewport=(1280, 800), install_clock=epoch_s(10000, 9, 30, 23, 59, 40))
        add(s, "Read")
        if open_p4:
            s.page.click("section.band button.btn-all")
            first = s.page.evaluate("() => Array.from(document.querySelectorAll('dialog[open]')).map((d) => d.className).join(',')")
            if first:
                s.page.keyboard.press("Escape")
            s.page.click("section.band button.btn-all")
        ok, snap = answers(s.page)
        print(json.dumps({"engine": engine, "case": case, "step": "before midnight", "answers": ok, **(snap or {}),
                          "pageErrors": len(s.errors), "lastError": (s.errors[-1][:90] if s.errors else None)}), flush=True)
        time.sleep(WAIT_S)
        t0 = time.time()
        ok, snap = answers(s.page)
        print(json.dumps({"engine": engine, "case": case, "step": f"after {WAIT_S} s of real time", "answers": ok,
                          "answerWaitSeconds": round(time.time() - t0, 2), **(snap or {}), "pageErrors": len(s.errors),
                          "lastError": (s.errors[-1][:90] if s.errors else None)}), flush=True)
    finally:
        t1 = time.time()
        browser.close()
        print(json.dumps({"engine": engine, "case": case, "step": "browser closed", "closeSeconds": round(time.time() - t1, 2)}), flush=True)


def main():
    engine = sys.argv[1]
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            run_case(p, engine, base, "control, nothing open", False)
            run_case(p, engine, base, "P4 open at midnight", True)
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
