"""SEC-01 as fixed, part 3: the keyboard path, two dialogs back to back, the `pendingDelete` note.

E1  Enter on the trash button, 650 ms, Tab to Delete habit, Enter: must delete at once (no guard past the window),
    then an Enter right after must not be swallowed (a keyboard delete starts no page guard)
E1b keyboard delete of row 1, then an immediate second Enter (the close event may not have run yet)
E2  Enter on trash, Tab and Enter within 100 ms: held (R13 note: the window covers the keyboard too), then 600 ms later Enter deletes
E3  Enter on trash, a mouse click on Delete habit at +100 ms (held) and at +650 ms (deletes)
E4  Space on trash, 650 ms, Tab, Space on Delete habit
E5  mouse click opens, Tab and Enter within 100 ms (held), 600 ms later Enter (deletes)
E6  Enter held down (auto repeat, 10 keydowns) on Delete habit after the window, and on a trash button
E7  Enter on Cancel (keyboard close), then a click on a bead at once: must tick
F1  two dialogs back to back with the mouse (open A, Esc, open B, Delete inside B's window, then after it)
F2  Cancel A with the mouse, then trash B at +200 ms (lost, documented) and +650 ms (opens)
F3  the solver's note: confirm A and open B in one task, so B opens before A's close event runs
F4  keyboard rapid: Delete habit, then an immediate Enter, 12 trials
Real input except F3 (one JS task, which no person can produce). Real-time installed clock. A snapshot is taken 150 ms
after a gesture (the dialog's `close` event runs as its own task, after the key press has returned).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from chars import FSI, PDI
from lib import Run, box, centre, events, fmt_clicks, open_app, press, reseed, snap, verdict

DESK = ("1440x900 mouse", (1440, 900), False)

FOCUS_DESC = "() => { const e = document.activeElement; return e ? (e.tagName.toLowerCase() + '|' + (e.getAttribute('aria-label') || e.textContent || e.id || '').trim().slice(0, 30)) : null; }"


def trash(page, row):
    return page.locator(f"li.habit:nth-child({row}) .icon-btn")


def active(page):
    return page.evaluate(FOCUS_DESC)


def title(page):
    return page.locator("#del-title").text_content().replace(FSI, "<FSI>").replace(PDI, "<PDI>")


def key_open(page, row, key="Enter"):
    trash(page, row).focus()
    page.keyboard.press(key)
    page.wait_for_selector("dialog[open]")


def settle(page, ms=150):
    page.wait_for_timeout(ms)
    return snap(page)


def fresh(page):
    reseed(page)
    s = snap(page)
    assert len(s["names"]) == 3, s["names"]
    return s


def main():
    with Run() as run:
        say = run.say
        ctx, page = open_app(run.browser, run.base, DESK[1], False)
        try:
            say("== E1: keyboard Enter, window passed, delete at once ==")
            before = fresh(page)
            key_open(page, 3)
            say(f"  after Enter on trash: focus={active(page)!r}, title={title(page)}")
            page.wait_for_timeout(650)
            page.keyboard.press("Tab")
            say(f"  after Tab: focus={active(page)!r}")
            page.keyboard.press("Enter")
            after = settle(page)
            say(f"  Enter on Delete habit: {verdict(before, after)}; focus={after['active']!r}")
            page.keyboard.press("Enter")
            page.wait_for_timeout(200)
            say(f"  immediate Enter in the New habit field (not swallowed, empty submit shows the error): message={page.locator('#new-habit-msg').text_content()!r}")
            say(f"  clicks: {fmt_clicks(events(page))}")

            say("== E1b: keyboard delete of row 1, then an immediate second Enter ==")
            before = fresh(page)
            key_open(page, 1)
            page.wait_for_timeout(650)
            page.keyboard.press("Tab")
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            after = settle(page)
            say(f"  after Enter, Enter: names={after['names']}, dialog open={after['open']}, title={title(page)}; clicks: {fmt_clicks(events(page))}")

            say("== E2: Enter on trash, Tab+Enter inside the window, then after it ==")
            before = fresh(page)
            key_open(page, 3)
            page.wait_for_timeout(100)
            page.keyboard.press("Tab")
            page.keyboard.press("Enter")
            held = settle(page, 100)
            say(f"  Tab+Enter ~250 ms after opening: {verdict(before, held)}; focus={held['active']!r}")
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            after = settle(page)
            say(f"  Enter again ~850 ms after opening: {verdict(before, after)}; clicks: {fmt_clicks(events(page))}")

            say("== E3: Enter on trash, then a mouse click on Delete habit ==")
            for gap in (100, 650):
                before = fresh(page)
                key_open(page, 3)
                page.wait_for_timeout(gap)
                page.mouse.click(*centre(box(page, "dialog .btn-danger")))
                say(f"  mouse click on Delete habit {gap} ms after a keyboard open: {verdict(before, settle(page))}; clicks: {fmt_clicks(events(page))}")

            say("== E4: Space ==")
            before = fresh(page)
            key_open(page, 3, "Space")
            say(f"  Space opened the dialog on key up: focus={active(page)!r}")
            page.wait_for_timeout(650)
            page.keyboard.press("Tab")
            page.keyboard.press("Space")
            say(f"  Space on Delete habit after the window: {verdict(before, settle(page))}")

            say("== E5: mouse click opens, Tab+Enter at once ==")
            before = fresh(page)
            press(page, *centre(trash(page, 3).bounding_box()), False)
            page.wait_for_selector("dialog[open]")
            page.keyboard.press("Tab")
            page.keyboard.press("Enter")
            say(f"  Tab+Enter right after a mouse open: {verdict(before, settle(page, 100))}")
            page.wait_for_timeout(600)
            page.keyboard.press("Enter")
            say(f"  Enter 800 ms later: {verdict(before, settle(page))}")

            say("== E6: Enter held down (auto repeat) ==")
            before = fresh(page)
            key_open(page, 1)
            page.wait_for_timeout(650)
            page.keyboard.press("Tab")
            for _ in range(10):
                page.keyboard.down("Enter")
            page.keyboard.up("Enter")
            after = settle(page, 400)
            say(f"  10 keydowns of Enter on Delete habit (row 1): habits {before['names']} -> {after['names']}; dialog open={after['open']}; focus={after['active']!r}")
            before = fresh(page)
            trash(page, 1).focus()
            for _ in range(10):
                page.keyboard.down("Enter")
            page.keyboard.up("Enter")
            after = settle(page, 400)
            say(f"  10 keydowns of Enter held on a trash button: habits {before['names']} -> {after['names']}; dialog open={after['open']}; ticks unchanged={after['pressed'] == before['pressed']}")

            say("== E7: keyboard close, then a bead at once ==")
            before = fresh(page)
            key_open(page, 3)
            page.keyboard.press("Enter")  # focus is on Cancel
            bead = page.locator("li.habit:nth-child(1) button.day").nth(6)
            press(page, *centre(bead.bounding_box()), False)
            say(f"  Enter on Cancel, bead click at once: {verdict(before, settle(page))}; clicks: {fmt_clicks(events(page))}")

            say("== F1: two dialogs back to back, mouse ==")
            before = fresh(page)
            press(page, *centre(trash(page, 1).bounding_box()), False)
            page.wait_for_selector("dialog[open]")
            page.wait_for_timeout(50)
            page.keyboard.press("Escape")
            press(page, *centre(trash(page, 2).bounding_box()), False)
            page.wait_for_timeout(300)
            x, y = centre(box(page, "dialog .btn-danger"))
            say(f"  B open ({title(page)}); Delete habit click ~350 ms after B opened:")
            press(page, x, y, False)
            say(f"    -> {verdict(before, settle(page, 100))}")
            page.wait_for_timeout(450)
            press(page, x, y, False)
            after = settle(page)
            say(f"  Delete habit ~950 ms after B opened: {verdict(before, after)}; names now {after['names']} (A 'Read 20 pages' must remain)")
            say(f"  clicks: {fmt_clicks(events(page))}")

            say("== F2: Cancel A with the mouse, then trash B ==")
            for gap in (200, 650):
                fresh(page)
                press(page, *centre(trash(page, 1).bounding_box()), False)
                page.wait_for_selector("dialog[open]")
                page.wait_for_timeout(100)
                press(page, *centre(box(page, "dialog .btn-secondary")), False)
                page.wait_for_timeout(gap)
                press(page, *centre(trash(page, 2).bounding_box()), False)
                after = settle(page)
                say(f"  trash B pressed {gap} ms after Cancel: dialog open={after['open']}; clicks: {fmt_clicks(events(page)[-2:])}")

            say("== F3: confirm A and open B in one task (B opens before A's close event runs) ==")
            for mode in ("confirm A, open B", "Esc-style close A, open B"):
                before = fresh(page)
                press(page, *centre(trash(page, 1).bounding_box()), False)
                page.wait_for_selector("dialog[open]")
                page.wait_for_timeout(650)
                result = page.evaluate(
                    """(mode) => {
                      const dlg = document.querySelector('dialog');
                      const trashB = document.querySelectorAll('.habit-head .icon-btn')[1];
                      if (mode.startsWith('confirm')) dlg.querySelector('.btn-danger').click(); else dlg.close('cancel');
                      const openAfterA = dlg.open;
                      trashB.click();
                      return { openAfterA, openAfterB: dlg.open };
                    }""", mode)
                mid = settle(page, 300)
                say(f"  {mode}: dialog open after A's close step={result['openAfterA']}, after B's click={result['openAfterB']}; after A's close event: {verdict(before, mid)}; title={title(page)}")
                page.wait_for_timeout(650)
                page.mouse.click(*centre(box(page, "dialog .btn-danger")))
                end = settle(page)
                say(f"    then a real click on B's Delete habit after the window: {verdict(before, end)}; names={end['names']}; focus={end['active']!r}")

            say("== F4: keyboard, Delete habit then an immediate Enter (12 trials, row 1) ==")
            tally = {}
            for trial in range(12):
                fresh(page)
                key_open(page, 1)
                page.wait_for_timeout(650)
                page.keyboard.press("Tab")
                page.keyboard.press("Enter")
                page.keyboard.press("Enter")
                after = settle(page, 250)
                key = f"habits={after['names']} dialog open={after['open']} title={title(page) if after['open'] else '-'}"
                tally[key] = tally.get(key, 0) + 1
            for key, n in tally.items():
                say(f"  {n} of 12: {key}")
            say(f"  page errors over the whole probe: {page.errors}")
        finally:
            ctx.close()
    run.finish("probe_03")


if __name__ == "__main__":
    main()
