"""CS-01, the year 10000 residual (1.0 SEC-05) as v1.1.0 has it, driven through the running app at HEAD.

Security finder (read-only), regression 2026-10-15. Run 2 (run 1's faults are in probe_11_run1_note.txt).
Run: timeout 600 python -u -B probe_11_year10000.py <chromium|webkit> [group ...]
Groups (default all): basic, phone, far, rollover, bcontrol, hang. Each case is a fresh headless context with the
clipboard stand-in first (lib.Session), Asia/Kuala_Lumpur (UTC+8).
  basic     control 2026-10-10 and A 10000-01-05 (CS-01's date) at 1280 x 800. Boot, add, Done today, the band's last
            day and P1's tick, the row's Year (P2), the band's Year (P4) twice, reload
  phone     A2 10000-01-05 at 390 x 844. Overview (P3), P3's newest day and P1's tick, P3's Year (P4)
  far       E 10015-11-20, P2 opens on keys that fail isDateKey, a bead press, the band's Year
  rollover  C and C2. Done today on 9999-12-31, P2 (C) or P4 (C2) open, the clock runs 90 s into 10000-01-01
  bcontrol  9999-10-15, the row's Year and the band's Year open
  hang      B-P2 and B-P4 at 10000-10-15, each in its own browser. A second page of the same context, opened before
            the press, reads storage and boots the app during the hang. The browser is closed after
The probe waits 600 ms after any mouse click inside a popup before it clicks the page, so the R14 guard holds nothing.
Prints one JSON line per step. Never writes a file. The server and every browser are stopped in finally blocks.
"""
import json
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeout  # noqa: E402

DESKTOP = (1280, 800)
PHONE = (390, 844)
GUARD_CLEAR_MS = 600  # R14 holds page clicks for 500 ms after a mouse click inside a popup


def days_from_civil(y, m, d):
    y -= m <= 2
    era = y // 400  # Python floors, so no C-style adjustment
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def epoch_s(y, mo, d, hh=12, mi=0, ss=0, offset_h=8):
    """Seconds since the epoch for a local time at UTC+offset_h, valid past the year 9999 (datetime stops there)."""
    return days_from_civil(y, mo, d) * 86400 + hh * 3600 + mi * 60 + ss - offset_h * 3600


SNAP = """(withKeys) => {
  const q = (s) => document.querySelector(s);
  const all = (s) => Array.from(document.querySelectorAll(s));
  const band = all('section.band div.ovg-cols button.hc');
  const snap = {
    header: q('header.top > time.date')?.getAttribute('datetime'),
    stored: localStorage.getItem('streaks.state'),
    rows: all('ul.rows > li.row').length,
    doneToday: all('ul.rows > li.row button.btn-done').map((b) => b.getAttribute('aria-pressed')).join(','),
    banners: all('div.banners > div.banner').map((b) => b.className).join(','),
    band: band.length,
    open: all('dialog[open]').map((d) => d.className).join(','),
    p2Beads: all('dialog.dlg-year div.months button.yc').length,
    p4Days: all('dialog.dlg-all div.months button.hc').length,
    p1: q('dialog.dlg-day[open] #day-title')?.textContent ?? null,
    p1Ticks: all('dialog.dlg-day[open] ul.day-list button.tick').map((b) => b.getAttribute('aria-pressed')).join(','),
    focus: document.activeElement ? document.activeElement.localName + '.' + document.activeElement.className : null,
  };
  if (withKeys) {
    snap.headerText = q('header.top > time.date')?.textContent;
    snap.bandKeys = band.length <= 8 ? band.map((b) => b.getAttribute('data-key')) : [band[0]?.getAttribute('data-key'), '...', band.at(-1)?.getAttribute('data-key')];
  }
  return snap;
}"""


def out(engine, case, step, s, extra=None, keys=False):
    snap = s.page.evaluate(SNAP, keys)
    row = {"engine": engine, "case": case, "step": step, **snap, "pageErrors": len(s.errors)}
    if s.errors:
        row["lastError"] = s.errors[-1][:100]
    if extra:
        row.update(extra)
    if s.csp():
        row["csp"] = s.csp()
    if s.clipboard_marks():
        row["clipboard"] = s.clipboard_marks()
    print(json.dumps(row, ensure_ascii=True), flush=True)
    return snap


def add(s, name):
    s.page.fill("#nh", name)
    s.page.press("#nh", "Enter")


def settle(s):
    s.page.wait_for_timeout(GUARD_CLEAR_MS)


def close_all(s):
    for _ in range(4):
        if not s.page.locator("dialog[open]").count():
            return
        s.page.keyboard.press("Escape")


def standin(s):
    return s.page.evaluate(lib.conftest.STANDIN_IN_PLACE_JS)


def case_basic(browser, engine, base, case, clock_s):
    s = lib.Session(browser, base, viewport=DESKTOP, clock=clock_s)
    try:
        out(engine, case, "boot, empty storage", s, {"standIn": standin(s)}, keys=True)
        add(s, "Read")
        out(engine, case, "added Read with Enter", s)
        s.page.click("ul.rows > li.row button.btn-done")
        out(engine, case, "clicked Done today", s)
        s.page.locator("section.band div.ovg-cols button.hc").last.click()
        out(engine, case, "clicked the band's last day button (today)", s)
        if s.page.locator("dialog.dlg-day[open] ul.day-list button.tick").count():
            s.page.click("dialog.dlg-day[open] ul.day-list button.tick")
            out(engine, case, "clicked P1's tick", s)
        close_all(s)
        settle(s)
        s.page.click("ul.rows > li.row button.btn-year")
        out(engine, case, "clicked the row's Year (P2)", s)
        close_all(s)
        s.page.click("section.band button.btn-all")
        out(engine, case, "clicked the band's Year (P4), first time", s)
        close_all(s)
        s.page.click("section.band button.btn-all")
        out(engine, case, "clicked the band's Year (P4), second time", s)
        close_all(s)
        s.page.reload()
        out(engine, case, "reloaded", s)
    finally:
        s.close()


def case_phone(browser, engine, base, case, clock_s):
    s = lib.Session(browser, base, viewport=PHONE, clock=clock_s)
    try:
        add(s, "Read")
        s.page.click("button.ov-btn")
        out(engine, case, "added Read, clicked Overview (P3)", s, {"p3Days": s.page.locator("dialog.dlg-ov div.ovg-rows button.hc").count()})
        s.page.locator("dialog.dlg-ov div.ovg-rows button.hc").first.click()
        out(engine, case, "clicked P3's first day (P1)", s)
        s.page.click("dialog.dlg-day[open] ul.day-list button.tick")
        out(engine, case, "clicked P1's tick", s)
        s.page.keyboard.press("Escape")
        settle(s)
        s.page.click("dialog.dlg-ov button.btn-all")
        out(engine, case, "clicked P3's Year (P4)", s)
    finally:
        s.close()


def case_far_open(browser, engine, base, case, clock_s):
    s = lib.Session(browser, base, viewport=DESKTOP, clock=clock_s)
    try:
        add(s, "Read")
        out(engine, case, "added Read", s, keys=True)
        s.page.click("ul.rows > li.row button.btn-year")
        keys = s.page.evaluate("() => Array.from(document.querySelectorAll('dialog.dlg-year div.months button.yc')).map((b) => b.getAttribute('data-key'))")
        out(engine, case, "clicked the row's Year (P2)", s, {"beadKeys": keys[:3] + (["...", keys[-1]] if len(keys) > 3 else [])})
        if keys:
            s.page.locator("dialog.dlg-year div.months button.yc").first.click()
            out(engine, case, "clicked P2's first bead", s)
        close_all(s)
        settle(s)
        s.page.click("section.band button.btn-all")
        out(engine, case, "clicked the band's Year (P4)", s)
        if s.page.locator("dialog.dlg-all[open] div.months button.hc").count():
            s.page.locator("dialog.dlg-all div.months button.hc").first.click()
            if s.page.locator("dialog.dlg-day[open] ul.day-list button.tick").count():
                s.page.click("dialog.dlg-day[open] ul.day-list button.tick")
            out(engine, case, "P4's first day, then P1's tick", s)
    finally:
        s.close()


def run_clock(s, ms):
    """Playwright's fake clock rethrows a timer's exception here. A real browser reports it as an uncaught error."""
    try:
        s.page.clock.run_for(ms)
        return None
    except PlaywrightError as error:
        return str(error).splitlines()[0][:140]


def case_rollover(browser, engine, base, case, hold):
    s = lib.Session(browser, base, viewport=DESKTOP, install_clock=epoch_s(9999, 12, 31, 23, 59, 0))
    try:
        add(s, "Read")
        s.page.click("ul.rows > li.row button.btn-done")
        out(engine, case, "added Read, Done today on 9999-12-31", s)
        s.page.click("ul.rows > li.row button.btn-year" if hold == "P2" else "section.band button.btn-all")
        out(engine, case, f"opened {hold}", s)
        thrown = run_clock(s, 90000)
        out(engine, case, "clock ran 90 s from 23:59:00 (into 10000-01-01)", s, {"timerThrew": thrown}, keys=True)
        if hold == "P2":
            s.page.click("dialog.dlg-year div.months button.yc[data-key='9999-12-31']")
            out(engine, case, "clicked P2's bead 9999-12-31", s)
            s.page.click("dialog.dlg-year div.months button.yc[data-key='9999-12-30']")
            out(engine, case, "clicked P2's bead 9999-12-30", s)
            close_all(s)
            settle(s)
            s.page.click("ul.rows > li.row button.btn-done")
            out(engine, case, "closed P2, clicked Done today", s)
            s.page.click("section.band button.btn-all")
            out(engine, case, "clicked the band's Year (P4), first time", s)
            close_all(s)
            s.page.click("section.band button.btn-all")
            out(engine, case, "clicked the band's Year (P4), second time", s)
            close_all(s)
        else:
            s.page.click("dialog.dlg-all div.months button.hc[data-key='9999-12-30']")
            out(engine, case, "clicked P4's stale day 9999-12-30", s)
            if s.page.locator("dialog.dlg-day[open] ul.day-list button.tick").count():
                s.page.click("dialog.dlg-day[open] ul.day-list button.tick")
                out(engine, case, "clicked P1's tick", s)
            close_all(s)
            settle(s)
            s.page.click("section.band button.btn-all")
            out(engine, case, "closed both, clicked the band's Year (P4) again", s)
            close_all(s)
        s.page.reload()
        out(engine, case, "reloaded (clock still in 10000-01-01)", s)
    finally:
        s.close()


def case_bcontrol(browser, engine, base, case, clock_s):
    s = lib.Session(browser, base, viewport=DESKTOP, clock=clock_s)
    try:
        add(s, "Read")
        s.page.click("ul.rows > li.row button.btn-done")
        out(engine, case, "added Read, clicked Done today", s)
        s.page.click("ul.rows > li.row button.btn-year")
        out(engine, case, "clicked the row's Year (P2)", s)
        close_all(s)
        s.page.click("section.band button.btn-all")
        out(engine, case, "clicked the band's Year (P4)", s)
    finally:
        s.close()


def case_hang(playwright, engine, base, case, clock_s, opener):
    browser = lib.launch(playwright, engine)
    started = time.time()
    try:
        s = lib.Session(browser, base, viewport=DESKTOP, clock=clock_s)
        add(s, "Read")
        s.page.click("ul.rows > li.row button.btn-done")
        out(engine, case, "added Read, clicked Done today", s, {"standIn": standin(s)})
        side = s.ctx.new_page()
        side.goto(base + "__seed__")
        t0 = time.time()
        try:
            s.page.click(opener, timeout=3000, no_wait_after=True)
            press = "returned"
        except PlaywrightTimeout:
            press = "timed out after 3 s"
        press_s = round(time.time() - t0, 2)
        t1 = time.time()
        try:
            s.page.wait_for_function("() => true", timeout=3000)
            responsive = True
        except PlaywrightTimeout:
            responsive = False
        print(json.dumps({"engine": engine, "case": case, "step": f"pressed {opener}", "press": press, "pressSeconds": press_s,
                          "pageAnswersWithin3s": responsive, "waitSeconds": round(time.time() - t1, 2),
                          "pageErrors": len(s.errors), "lastError": (s.errors[-1][:100] if s.errors else None)}), flush=True)
        try:
            handle = side.wait_for_function("() => ({ stored: localStorage.getItem('streaks.state') })", timeout=5000)
            stored_side, side_ok = handle.json_value()["stored"], True
        except PlaywrightTimeout:
            stored_side, side_ok = None, False
        print(json.dumps({"engine": engine, "case": case, "step": "second page of the same context reads storage during the hang",
                          "answered": side_ok, "stored": stored_side}), flush=True)
        if side_ok:
            try:
                side.goto(base, timeout=10000)
                handle = side.wait_for_function(
                    "() => document.querySelector('ul.rows') && ({ rows: document.querySelectorAll('ul.rows > li.row').length,"
                    " banners: Array.from(document.querySelectorAll('div.banners > div.banner')).map((b) => b.className).join(','),"
                    " header: document.querySelector('header.top > time.date').getAttribute('datetime'),"
                    " stored: localStorage.getItem('streaks.state') })", timeout=5000)
                print(json.dumps({"engine": engine, "case": case, "step": "second page boots the app during the hang", **handle.json_value()}), flush=True)
            except (PlaywrightTimeout, PlaywrightError) as error:
                print(json.dumps({"engine": engine, "case": case, "step": "second page boots the app during the hang", "error": str(error)[:120]}), flush=True)
    finally:
        t2 = time.time()
        browser.close()
        print(json.dumps({"engine": engine, "case": case, "step": "browser closed", "closeSeconds": round(time.time() - t2, 2),
                          "caseSeconds": round(time.time() - started, 2)}), flush=True)


def main():
    engine = sys.argv[1]
    groups = set(sys.argv[2:]) or {"basic", "phone", "far", "rollover", "bcontrol", "hang"}
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            browser = lib.launch(p, engine)
            print(json.dumps({"engine": engine, "version": browser.version, "groups": sorted(groups)}), flush=True)
            try:
                if "basic" in groups:
                    case_basic(browser, engine, base, "control 2026-10-10", epoch_s(2026, 10, 10))
                    case_basic(browser, engine, base, "A 10000-01-05", epoch_s(10000, 1, 5))
                if "phone" in groups:
                    case_phone(browser, engine, base, "control 2026-10-10 phone", epoch_s(2026, 10, 10))
                    case_phone(browser, engine, base, "A2 10000-01-05 phone", epoch_s(10000, 1, 5))
                if "far" in groups:
                    case_far_open(browser, engine, base, "E 10015-11-20", epoch_s(10015, 11, 20))
                if "rollover" in groups:
                    case_rollover(browser, engine, base, "C rollover with P2", "P2")
                    case_rollover(browser, engine, base, "C2 rollover with P4", "P4")
                if "bcontrol" in groups:
                    case_bcontrol(browser, engine, base, "B-control 9999-10-15", epoch_s(9999, 10, 15))
            finally:
                browser.close()
            if "hang" in groups:
                case_hang(p, engine, base, "B-P2 10000-10-15", epoch_s(10000, 10, 15), "ul.rows > li.row button.btn-year")
                case_hang(p, engine, base, "B-P4 10000-10-15", epoch_s(10000, 10, 15), "section.band button.btn-all")
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
