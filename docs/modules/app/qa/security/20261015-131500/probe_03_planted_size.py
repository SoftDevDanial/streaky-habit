"""T8 (v1.1.0 changed) and habit-logic "Responsiveness of the year views". How slow does a planted value make
boot, a tick, P4, P1 over P4 and P2? Each step is timed from the key press to the state it causes, wall clock,
with a bounded wait ("gave up after N s"). Printed unbuffered step by step (run with python -u -B).

Shapes (all keys valid, so the decoder accepts them, all built inside the throwaway context):
  real               12 habits x 1,826 days from 2021-10-11 (five years of daily use, the realistic heavy user)
  <habits> <perHabit> habits with perHabit consecutive days each from 1000-01-01 onwards, none inside the year,
                     so every doneFlags lookup scans the whole list. The quota is 5,242,880 UTF-16 units in both
                     engines (probe_03a), about 395,000 keys of 13 characters.
A tick step waits for aria-pressed to flip from the value it had before the key press.
Usage: python -u -B probe_03_planted_size.py <engine> <cap seconds> real
       python -u -B probe_03_planted_size.py <engine> <cap seconds> <habits> <perHabit>
"""
import sys
import time

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"

BUILD_JS = """([habitCount, perHabit, startYear, startMonth, startDay]) => {
  const pad = (n, w) => String(n).padStart(w, '0');
  const habits = [];
  let t = Date.UTC(startYear, startMonth, startDay);
  for (let h = 0; h < habitCount; h++) {
    const done = [];
    if (startYear === 2021) t = Date.UTC(startYear, startMonth, startDay);
    for (let i = 0; i < perHabit; i++) {
      const d = new Date(t); t += 86400000;
      done.push(pad(d.getUTCFullYear(), 4) + '-' + pad(d.getUTCMonth() + 1, 2) + '-' + pad(d.getUTCDate(), 2));
    }
    habits.push({ name: 'Habit ' + (h + 1), done });
  }
  const text = JSON.stringify({ version: 1, habits });
  localStorage.setItem('streaks.state', text);
  return text.length;
}"""

CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"
PRESSED_JS = "(sel) => document.querySelector(sel).getAttribute('aria-pressed')"
FLIPPED_JS = "([sel, before]) => document.querySelector(sel).getAttribute('aria-pressed') !== before"


def main():
    engine, cap = sys.argv[1], int(sys.argv[2])
    if sys.argv[3] == "real":
        arg, label = [12, 1826, 2021, 9, 11], "real 12 x 1826 from 2021-10-11"
    else:
        habits, per = int(sys.argv[3]), int(sys.argv[4])
        arg, label = [habits, per, 1000, 0, 1], f"{habits} x {per} from 1000-01-01"
    proc, port, _ = lib.start_server()
    started = time.time()
    try:
        base = f"http://127.0.0.1:{port}/"
        with sync_playwright() as p:
            browser = lib.launch(p, engine)
            print("engine", engine, browser.version, "shape", label, "cap", cap, flush=True)
            try:
                s = lib.Session(browser, base, viewport=(1280, 800), clock=NOON, route_log=False, path="__seed__",
                                timeout_ms=cap * 1000, nav_timeout_ms=cap * 1000, init=[CLOSE_LOGGER])
                page = s.page
                print("stored_chars", page.evaluate(BUILD_JS, arg), flush=True)

                def step(name, action, done_js, arg=None):
                    t0 = time.time()
                    action()
                    try:
                        page.wait_for_function(done_js, arg=arg, timeout=cap * 1000, polling=50)
                        print(f"{name}: {time.time() - t0:.2f} s", flush=True)
                        return True
                    except Exception as exc:
                        print(f"{name}: gave up after {cap} s ({type(exc).__name__})", flush=True)
                        return False

                def key(selector):
                    page.locator(selector).first.focus()
                    page.keyboard.press("Enter")

                def tick(name, selector):
                    before = page.evaluate(PRESSED_JS, selector)
                    return step(f"{name} (was {before})", lambda: key(selector), FLIPPED_JS, [selector, before])

                ok = step("boot (goto to first row)", lambda: page.goto(base, wait_until="commit"),
                          "() => document.querySelector('ul.rows > li.row, ul.rows > li.empty') !== null")
                if ok:
                    print("rows", page.evaluate("() => document.querySelectorAll('ul.rows > li.row').length"),
                          "note", page.evaluate("() => document.querySelectorAll('div.banner.note').length"), flush=True)
                ok = ok and tick("Done today tick, no popup", "ul.rows > li.row button.btn-done")
                ok = ok and step("open P4 from the band", lambda: key("section.band button.btn-all"),
                                 "() => document.querySelector('dialog.dlg-all').open")
                ok = ok and step("open P1 over P4 for 2026-01-15", lambda: key("dialog.dlg-all button.hc[data-key='2026-01-15']"),
                                 "() => document.querySelector('dialog.dlg-day').open")
                ok = ok and tick("tick in P1 over P4", "dialog.dlg-day button.tick")
                ok = ok and step("Esc P1", lambda: page.keyboard.press("Escape"), "() => !document.querySelector('dialog.dlg-day').open")
                ok = ok and step("Esc P4", lambda: page.keyboard.press("Escape"), "() => !document.querySelector('dialog.dlg-all').open")
                if ok:
                    deadline = time.time() + cap
                    while sum(1 for c in s.console if c.startswith("log: closed:")) < 2 and time.time() < deadline:
                        page.wait_for_timeout(50)
                ok = ok and step("open P2", lambda: key("ul.rows > li.row button.btn-year"), "() => document.querySelector('dialog.dlg-year').open")
                ok = ok and tick("bead tick in P2 for 2026-01-15", "dialog.dlg-year button.yc[data-key='2026-01-15']")
                print("page errors", s.errors, flush=True)
                s.close()
            finally:
                browser.close()
    finally:
        lib.stop_server(proc, port)
        print(f"total {time.time() - started:.1f} s", flush=True)


if __name__ == "__main__":
    main()
