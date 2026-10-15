"""The step 5 and task 27a delta (git diff 4e860ff HEAD -- src index.html), driven in each engine.

Security finder (read-only), regression 2026-10-15. Run: timeout 400 python -u -B probe_13_delta.py [chromium] [webkit]
Part 1  Done today now reads `doneFlags(habits, today)` (render, renderRows, syncRow). For readable but hostile
        stored values (duplicates of today, unsorted, keys after today, object-key names, 12 habits) every row's
        aria-pressed must equal "today is in that habit's stored done", and the Overview button's count must equal
        the number of pressed rows, at boot, after Done today on each row, after a P1 tick of today, after a P2 bead
        of today, and after a rollover. Compared inside the page against localStorage, not against the app.
Part 2  dismissNote with the field disabled (task 27a). An unreadable value resets with the note, 12 habits are
        typed in, then Dismiss is pressed by mouse and, in another context, by keyboard, at 390 and 1280. The stored
        text must not change on Dismiss, the note must go and not come back on reload, focus must not be on body,
        and no page error may occur. A control with the field enabled checks focus goes to the field.
Every context has the clipboard stand-in first (lib.Session). Prints JSON lines, writes no file.
Run 2: each Escape waits for the popup's close event (a capture listener logs it), run 1's fault is in probe_13_run1.txt.
"""
import json
import sys

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

NOON = "2026-10-10T12:00:00+08:00"
BEFORE_MIDNIGHT = "2026-10-10T23:59:30+08:00"
GUARD_CLEAR_MS = 600
CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"


def esc(s):
    """Escape, then wait for one close event, gave up after 5 s."""
    seen = sum(1 for c in s.console if c.startswith("log: closed:"))
    s.page.keyboard.press("Escape")
    for _ in range(250):
        if sum(1 for c in s.console if c.startswith("log: closed:")) > seen:
            return
        s.page.wait_for_timeout(20)
    raise RuntimeError("close event not seen, gave up after 5 s")

CHECK_JS = """() => {
  const today = document.querySelector('header.top > time.date').getAttribute('datetime');
  const stored = JSON.parse(localStorage.getItem('streaks.state'));
  const expected = stored.habits.map((h) => String(h.done.includes(today)));
  const shown = Array.from(document.querySelectorAll('ul.rows > li.row button.btn-done')).map((b) => b.getAttribute('aria-pressed'));
  const names = Array.from(document.querySelectorAll('ul.rows > li.row h3')).map((h) => h.textContent);
  const label = document.querySelector('button.ov-btn').getAttribute('aria-label');
  const pressed = shown.filter((v) => v === 'true').length;
  return { today, rowsMatchStored: JSON.stringify(shown) === JSON.stringify(expected),
           namesMatchStored: JSON.stringify(names) === JSON.stringify(stored.habits.map((h) => h.name)),
           overviewMatchesRows: label === `Overview, today ${pressed} of ${shown.length} habits done`, pressed, rows: shown.length };
}"""

STATES = {
    "today duplicated, unsorted, keys after today": [
        {"name": "Read", "done": ["2026-10-12", "2026-10-10", "2026-10-01", "2026-10-10", "2027-01-01"]},
        {"name": "Run", "done": ["2026-10-11", "2026-10-09"]},
        {"name": "__proto__", "done": ["2026-10-10"]},
    ],
    "twelve object-key names": [
        {"name": n, "done": (["2026-10-10"] if i % 2 == 0 else ["2026-10-09", "2026-10-11"])}
        for i, n in enumerate(["constructor", "toString", "hasOwnProperty", "valueOf", "prototype", "length", "then",
                               "rn-1", "nh", "del-title", "__defineGetter__", "0"])
    ],
}


def check(s, engine, label, step):
    row = {"engine": engine, "state": label, "step": step, **s.page.evaluate(CHECK_JS), "pageErrors": len(s.errors)}
    print(json.dumps(row, ensure_ascii=True), flush=True)


def part1(browser, engine, base):
    for label, habits in STATES.items():
        for width, height in ((1280, 800), (390, 844)):
            s = lib.Session(browser, base, viewport=(width, height), seed_js=lib.SEED_TEXT, seed_arg=lib.encode(habits),
                            install_clock=BEFORE_MIDNIGHT, init=[CLOSE_LOGGER])
            try:
                tag = f"{label} @{width}"
                check(s, engine, tag, "boot")
                buttons = s.page.locator("ul.rows > li.row button.btn-done")
                for i in range(buttons.count()):
                    buttons.nth(i).focus()
                    s.page.keyboard.press("Enter")
                check(s, engine, tag, "Done today on every row by keyboard")
                buttons.nth(0).click()
                check(s, engine, tag, "Done today on row 1 by mouse")
                if width >= 1024:
                    s.page.click("section.band button.hc[aria-current=date]")
                else:
                    s.page.click("button.ov-btn")
                    s.page.click("dialog.dlg-ov button.hc[aria-current=date]")
                s.page.locator("dialog.dlg-day ul.day-list button.tick").nth(1).click()
                check(s, engine, tag, "P1 tick of today on row 2")
                for _ in range(2):
                    if s.page.locator("dialog[open]").count():
                        esc(s)
                s.page.wait_for_timeout(GUARD_CLEAR_MS)
                s.page.locator("ul.rows > li.row button.btn-year").nth(0).click()
                s.page.click("dialog.dlg-year button.yc[aria-current=date]")
                check(s, engine, tag, "P2 bead of today on row 1")
                esc(s)
                s.page.clock.run_for(60000)
                check(s, engine, tag, "rollover to 2026-10-11")
            finally:
                s.close()


def part2(browser, engine, base):
    for width, height in ((390, 844), (1280, 800)):
        for how in ("mouse", "keyboard", "control field enabled"):
            s = lib.Session(browser, base, viewport=(width, height), seed_js=lib.SEED_TEXT, seed_arg="{not json", clock=NOON)
            try:
                note = s.page.locator("div.banners > div.banner.note").count()
                adds = 0 if how == "control field enabled" else 12
                for n in range(1, adds + 1):
                    s.page.fill("#nh", f"Habit {n}")
                    s.page.press("#nh", "Enter")
                disabled = s.page.evaluate("() => document.querySelector('#nh').disabled")
                before = s.stored()
                if how == "keyboard":
                    s.page.locator("div.banner.note > button.icon-btn").focus()
                    s.page.keyboard.press("Enter")
                else:
                    s.page.click("div.banner.note > button.icon-btn")
                after = s.stored()
                focus = s.page.evaluate("() => { const a = document.activeElement; return a.localName + (a.className ? '.' + a.className : '') + (a.id ? '#' + a.id : ''); }")
                notes_now = s.page.locator("div.banners > div.banner.note").count()
                s.page.reload()
                notes_reload = s.page.locator("div.banners > div.banner.note").count()
                rows_reload = s.page.locator("ul.rows > li.row").count()
                print(json.dumps({"engine": engine, "part": "Dismiss", "viewport": f"{width}x{height}", "how": how,
                                  "noteAtBoot": note, "habitsAdded": adds, "fieldDisabled": disabled,
                                  "storedUnchangedByDismiss": before == after, "noteAfterDismiss": notes_now,
                                  "focus": focus, "noteAfterReload": notes_reload, "rowsAfterReload": rows_reload,
                                  "pageErrors": s.errors, "clipboard": s.clipboard_marks()}), flush=True)
            finally:
                s.close()


def main():
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            for engine in lib.engines_from_argv():
                browser = lib.launch(p, engine)
                print(json.dumps({"engine": engine, "version": browser.version}), flush=True)
                try:
                    part1(browser, engine, base)
                    part2(browser, engine, base)
                finally:
                    browser.close()
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
