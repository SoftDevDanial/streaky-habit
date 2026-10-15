"""Re-check of task 9a (the bound on yearMonths), what P2 and P4 show at far clocks, and whether the page answers.

Security finder (read-only), re-check 2026-10-15. Run: timeout 900 python -u -B rs9a_views.py <chromium|webkit>
Each date is its own headless browser and context (lib.Session, the clipboard stand-in first, Asia/Kuala_Lumpur, UTC+8),
the clock fixed with Playwright's clock API at 12:00 local. Steps per date at 1280 x 800:
  add "Read", Done today, the row's Year (P2) and what it holds, every open bead pressed, close, the band's Year (P4)
  and what it holds, its first open day and P1's tick, close, the band's Year a second time, close.
Phone dates at 390 x 844: Overview (P3), P3's Year (P4).
Every read of the page goes through wait_for_function with a 3 s timeout, so a frozen page shows as answers=false and
no read blocks. Every press has a 3 s timeout. The browser is closed in finally. Prints JSON lines, writes no file.
"""
import json
import re
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeout  # noqa: E402
from probe_11_year10000 import epoch_s  # noqa: E402

DESKTOP = (1280, 800)
PHONE = (390, 844)
KEY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DIM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_date_key(k):
    """A copy of src/dates.js isDateKey, for reading the captures."""
    if not isinstance(k, str) or not KEY.match(k):
        return False
    y, m, d = (int(x) for x in k.split("-"))
    leap = (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
    return y >= 1 and 1 <= m <= 12 and 1 <= d <= (29 if m == 2 and leap else DIM[m - 1])


BASE = """() => ({
  header: document.querySelector('header.top > time.date')?.getAttribute('datetime'),
  headerText: document.querySelector('header.top > time.date')?.textContent,
  stored: localStorage.getItem('streaks.state'),
  doneToday: Array.from(document.querySelectorAll('ul.rows > li.row button.btn-done')).map((b) => b.getAttribute('aria-pressed')).join(','),
  band: document.querySelectorAll('section.band div.ovg-cols button.hc').length,
  open: Array.from(document.querySelectorAll('dialog[open]')).map((d) => d.className).join(','),
  banners: Array.from(document.querySelectorAll('div.banners > div.banner')).map((b) => b.className).join(','),
})"""

YEAR = """(sel) => {
  const d = document.querySelector(sel);
  const cls = sel.includes('dlg-year') ? 'yc' : 'hc';
  if (!d) return { found: false };
  const months = Array.from(d.querySelectorAll('div.months section.month'));
  const ctl = Array.from(d.querySelectorAll('div.months button.' + cls));
  return {
    isOpen: d.open,
    months: months.length,
    titles: months.map((m) => m.querySelector('h3')?.textContent),
    headingIds: months.map((m) => m.querySelector('h3')?.id),
    daysPerMonth: months.map((m) => m.querySelectorAll('div.mgrid > .' + cls + ':not(.lead):not(.blank)').length),
    openControls: ctl.length,
    openKeys: ctl.map((b) => b.getAttribute('data-key')),
    firstLabels: ctl.slice(0, 2).map((b) => b.getAttribute('aria-label')),
    closed: d.querySelectorAll('div.months .' + cls + '.closed').length,
    blank: d.querySelectorAll('div.months .' + cls + '.blank').length,
    lead: d.querySelectorAll('div.months .' + cls + '.lead').length,
    duplicateIds: (() => { const ids = Array.from(document.querySelectorAll('[id]')).map((e) => e.id); return ids.length - new Set(ids).size; })(),
  };
}"""


def read(s, expr, arg=None):
    try:
        return True, s.page.wait_for_function(expr, arg=arg, timeout=3000).json_value()
    except PlaywrightTimeout:
        return False, None


def press(s, selector, nth=None):
    t0 = time.time()
    try:
        loc = s.page.locator(selector)
        loc = loc.nth(nth) if nth is not None else loc.first
        loc.click(timeout=3000, no_wait_after=True)
        result = "returned"
    except PlaywrightTimeout:
        result = "timed out after 3 s"
    except PlaywrightError as error:
        result = "error " + str(error).splitlines()[0][:100]
    return result, round(time.time() - t0, 2)


def emit(engine, case, step, s, extra=None):
    ok, base = read(s, BASE)
    row = {"engine": engine, "case": case, "step": step, "answers": ok, **(base or {}), "pageErrors": len(s.errors)}
    if s.errors:
        row["lastError"] = s.errors[-1][:100]
    if s.csp():
        row["csp"] = s.csp()
    if extra:
        row.update(extra)
    print(json.dumps(row, ensure_ascii=True), flush=True)
    return ok, base


def year(engine, case, step, s, sel):
    ok, snap = read(s, YEAR, sel)
    if snap and snap.get("openKeys") is not None:
        keys = snap["openKeys"]
        snap["openKeysPassingIsDateKey"] = sum(1 for k in keys if is_date_key(k))
        snap["openKeys"] = keys if len(keys) <= 12 else keys[:4] + ["..."] + keys[-2:]
    row = {"engine": engine, "case": case, "step": step, "answers": ok, **(snap or {}), "pageErrors": len(s.errors)}
    if s.errors:
        row["lastError"] = s.errors[-1][:100]
    print(json.dumps(row, ensure_ascii=True), flush=True)
    return ok, snap


def escape_all(s):
    for _ in range(4):
        ok, base = read(s, BASE)
        if not ok or not base["open"]:
            return ok
        s.page.keyboard.press("Escape")
    return True


def desktop_case(p, engine, base_url, case, clock_s):
    browser = lib.launch(p, engine)
    started = time.time()
    try:
        s = lib.Session(browser, base_url, viewport=DESKTOP, clock=clock_s)
        s.page.fill("#nh", "Read", timeout=3000)
        s.page.press("#nh", "Enter", timeout=3000)
        ok, b = emit(engine, case, "added Read", s, {"standIn": s.page.evaluate(lib.conftest.STANDIN_IN_PLACE_JS)})
        if not ok:
            return
        before = b["stored"]
        r = press(s, "ul.rows > li.row button.btn-done")
        ok, b = emit(engine, case, "pressed Done today", s, {"press": r[0], "storedChanged": None})
        if not ok:
            return
        print(json.dumps({"engine": engine, "case": case, "step": "Done today changed storage", "value": b["stored"] != before}), flush=True)
        r = press(s, "ul.rows > li.row button.btn-year")
        ok, _ = year(engine, case, f"pressed the row's Year (P2), press {r[0]} in {r[1]} s", s, "dialog.dlg-year")
        if not ok:
            return
        ok, snap = read(s, YEAR, "dialog.dlg-year")
        if snap and snap.get("isOpen") and snap["openControls"]:
            n = min(snap["openControls"], 12)
            for i in range(n):
                press(s, "dialog.dlg-year div.months button.yc", i)
            ok, b = emit(engine, case, f"pressed {n} open bead(s) in P2", s)
            if not ok:
                return
            print(json.dumps({"engine": engine, "case": case, "step": "P2 bead presses changed storage", "value": b["stored"] != before}), flush=True)
        if not escape_all(s):
            return
        s.page.wait_for_timeout(600)
        r = press(s, "section.band button.btn-all")
        ok, _ = year(engine, case, f"pressed the band's Year (P4), first time, press {r[0]} in {r[1]} s", s, "dialog.dlg-all")
        if not ok:
            return
        ok, snap = read(s, YEAR, "dialog.dlg-all")
        if snap and snap.get("isOpen") and snap["openControls"]:
            press(s, "dialog.dlg-all div.months button.hc", 0)
            ok, b = read(s, "() => ({ p1: document.querySelector('dialog.dlg-day[open] #day-title')?.textContent ?? null,"
                            " ticks: document.querySelectorAll('dialog.dlg-day[open] ul.day-list button.tick').length })")
            if b and b["ticks"]:
                press(s, "dialog.dlg-day[open] ul.day-list button.tick")
            ok, b2 = emit(engine, case, "pressed P4's first open day, then P1's tick", s, {"p1": b})
            if not ok:
                return
            print(json.dumps({"engine": engine, "case": case, "step": "P4 day and P1 tick changed storage", "value": b2["stored"] != before}), flush=True)
        if not escape_all(s):
            return
        s.page.wait_for_timeout(600)
        r = press(s, "section.band button.btn-all")
        year(engine, case, f"pressed the band's Year (P4), second time, press {r[0]} in {r[1]} s", s, "dialog.dlg-all")
        escape_all(s)
        emit(engine, case, "end", s)
    finally:
        t = time.time()
        browser.close()
        print(json.dumps({"engine": engine, "case": case, "step": "browser closed", "closeSeconds": round(time.time() - t, 2),
                          "caseSeconds": round(time.time() - started, 2)}), flush=True)


def phone_case(p, engine, base_url, case, clock_s):
    browser = lib.launch(p, engine)
    try:
        s = lib.Session(browser, base_url, viewport=PHONE, clock=clock_s)
        s.page.fill("#nh", "Read", timeout=3000)
        s.page.press("#nh", "Enter", timeout=3000)
        r = press(s, "button.ov-btn")
        ok, _ = emit(engine, case, f"pressed Overview (P3), press {r[0]}", s)
        if not ok:
            return
        r = press(s, "dialog.dlg-ov button.btn-all")
        year(engine, case, f"pressed P3's Year (P4), press {r[0]} in {r[1]} s", s, "dialog.dlg-all")
        emit(engine, case, "end", s)
    finally:
        browser.close()
        print(json.dumps({"engine": engine, "case": case, "step": "browser closed"}), flush=True)


DESKTOP_DATES = [
    ("control 9999-10-15", (9999, 10, 15)),
    ("Q4 10000-10-01", (10000, 10, 1)),
    ("Q4 10000-10-15", (10000, 10, 15)),
    ("Q4 10000-11-30", (10000, 11, 30)),
    ("Q4 10000-12-31", (10000, 12, 31)),
    ("Q4 10003-11-15", (10003, 11, 15)),
    ("Q4 10005-11-20", (10005, 11, 20)),
    ("Q4 10007-12-01", (10007, 12, 1)),
    ("Q4 10009-10-01", (10009, 10, 1)),
    ("Q4 10009-12-31", (10009, 12, 31)),
    ("Jan-Sep 10000-01-05", (10000, 1, 5)),
    ("Jan-Sep 10000-05-20", (10000, 5, 20)),
    ("Jan-Sep 10000-09-30", (10000, 9, 30)),
    ("Jan-Sep 10010-03-10", (10010, 3, 10)),
    ("Q4 10010-10-15", (10010, 10, 15)),
    ("Q4 10010-12-31", (10010, 12, 31)),
    ("Q4 10123-11-11", (10123, 11, 11)),
    ("six digits 100000-10-15", (100000, 10, 15)),
    ("six digits 100000-03-03", (100000, 3, 3)),
]
PHONE_DATES = [
    ("phone 10000-10-15", (10000, 10, 15)),
    ("phone 10005-11-20", (10005, 11, 20)),
    ("phone 10010-10-15", (10010, 10, 15)),
]


def main():
    engine = sys.argv[1]
    only = set(sys.argv[2:])
    proc, port, _ = lib.start_server()
    base_url = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            b = lib.launch(p, engine)
            print(json.dumps({"engine": engine, "version": b.version}), flush=True)
            b.close()
            for case, ymd in DESKTOP_DATES:
                if only and case not in only:
                    continue
                desktop_case(p, engine, base_url, case, epoch_s(*ymd))
            for case, ymd in PHONE_DATES:
                if only and case not in only:
                    continue
                phone_case(p, engine, base_url, case, epoch_s(*ymd))
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
