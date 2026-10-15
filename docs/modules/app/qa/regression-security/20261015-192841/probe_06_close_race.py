"""Integrity when a popup is opened again before the previous `close` event has run (seen in probe_01 run 1).

The app clears state.year, state.day and state.remove, and moves focus to the opener, in its `close` handler,
which runs as a queued task. If the next key press is handled first, the reopened popup loses its state, or
focus jumps back to the old opener. This probe drives three sequences at automation speed (no wait between
the keys) and checks the security property: the effect of the destructive key press always matches what the
popup shows at that moment (M1's title, P1's title and tick name), or nothing happens.
  A  Enter on row 1's Year, Escape, at once Enter on row 2's Year, Enter on P2's Delete habit, read M1's title,
     Enter on M1's Delete habit.
  B  Enter on row 1's bin, Enter on M1's Delete habit, at once Enter (focus is on the next bin), read M1's title,
     Enter on M1's Delete habit.
  C  Enter on today in the band, Escape, at once Enter on yesterday, read P1's title and first tick, Enter on it.
Run 2: the name is read from M1's title as the text between U+2068 and U+2069 (run 1 kept the U+2068 and so
labelled every matching delete a mismatch).
Usage: python -B probe_06_close_race.py [chromium] [webkit]
"""
import json

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"
NAMES = [f"H{i}" for i in range(1, 7)]
STATE = lib.encode([{"name": n, "done": ["2026-10-10"]} for n in NAMES])
TRIALS = 12
TITLES = {"Saturday 10 October": "2026-10-10", "Friday 9 October": "2026-10-09"}


def enter(page, selector):
    page.locator(selector).first.focus()
    page.keyboard.press("Enter")


def habits(s):
    return json.loads(s.stored())["habits"]


def m1_name(page):
    title = page.evaluate("() => document.querySelector('dialog.dlg-del').open ? document.querySelector('#del-title').textContent : null")
    if title is None:
        return None
    return title.split("⁨", 1)[1].rsplit("⁩", 1)[0]


def run(engine, base):
    tallies = {"A": {}, "B": {}, "C": {}}
    errors = {"A": set(), "B": set(), "C": set()}
    with sync_playwright() as p:
        browser = lib.launch(p, engine)
        try:
            for case in ("A", "B", "C"):
                for _ in range(TRIALS):
                    s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=STATE, clock=NOON, route_log=False)
                    page = s.page
                    try:
                        if case in ("A", "B"):
                            if case == "A":
                                enter(page, "ul.rows > li.row:nth-child(1) button.btn-year")
                                page.keyboard.press("Escape")
                                enter(page, "ul.rows > li.row:nth-child(2) button.btn-year")
                                page.wait_for_timeout(150)
                                if page.evaluate("() => document.querySelector('dialog.dlg-year').open"):
                                    enter(page, "dialog.dlg-year button.btn-del")
                                page.wait_for_timeout(150)
                            else:
                                enter(page, "ul.rows > li.row:nth-child(1) button.btn-bin")
                                enter(page, "dialog.dlg-del button.btn-danger")
                                page.keyboard.press("Enter")
                                page.wait_for_timeout(150)
                            before = [h["name"] for h in habits(s)]
                            named = m1_name(page)
                            if named is not None:
                                enter(page, "dialog.dlg-del button.btn-danger")
                            page.wait_for_timeout(150)
                            gone = [n for n in before if n not in [h["name"] for h in habits(s)]]
                            verdict = "nothing" if not gone else ("matches title" if gone == [named] else "MISMATCH")
                            outcome = f"M1 names {named}, deleted {gone}: {verdict}"
                        else:
                            enter(page, "section.band button.hc[data-key='2026-10-10']")
                            page.keyboard.press("Escape")
                            enter(page, "section.band button.hc[data-key='2026-10-09']")
                            page.wait_for_timeout(150)
                            shown = page.evaluate("() => document.querySelector('dialog.dlg-day').open && [document.querySelector('#day-title').textContent, document.querySelector('dialog.dlg-day button.tick').getAttribute('aria-label')]")
                            if shown:
                                enter(page, "dialog.dlg-day button.tick")
                            page.wait_for_timeout(150)
                            changed = []
                            for h in habits(s):
                                diff = sorted(set(h["done"]) ^ {"2026-10-10"})
                                if diff:
                                    changed.append((h["name"], diff))
                            expect = [(shown[1], [TITLES.get(shown[0], shown[0])])] if shown else None
                            verdict = "nothing" if not changed else ("matches P1" if changed == expect else "MISMATCH")
                            outcome = f"P1 {shown}, changed {changed}: {verdict}"
                        tallies[case][outcome] = tallies[case].get(outcome, 0) + 1
                        errors[case].update(s.errors)
                    finally:
                        s.close()
        finally:
            browser.close()
    return tallies, {k: sorted(v) for k, v in errors.items()}


def main():
    proc, port, _ = lib.start_server()
    try:
        for engine in lib.engines_from_argv():
            tallies, errors = run(engine, f"http://127.0.0.1:{port}/")
            for case in ("A", "B", "C"):
                print(engine, case, json.dumps(tallies[case], ensure_ascii=True), "page errors", errors[case], flush=True)
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
