"""The v1.1.0 cold-boot live-e2e gate (app spec R27 and R30, qa.md "Cold-boot live-e2e gate").

Not a pytest file, so pytest never collects it. It proves the shipped page works from nothing, on the real clock, driven only by real gestures in the engine asked for,
and keeps the evidence the Definition of done asks for. Run it on an app somebody else serves (this script starts
nothing) with
    python tests/browser/live_e2e.py --engine <engine> --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/
Its control adds --control seeded and writes to a folder ending in -<engine>-control. It seeds the sample through the
same-origin __seed__ page before the app loads, so a gate that can tell a seeded start from a cold one stops red at the
first-visit step. The control can only make a run fail.
Input is the engine (default the first of the conftest's ENGINES), the app's URL and --out, a new or empty folder inside
the project. Output is one full-page screenshot per step, steps.json, console.json, network.json and summary.json in
that folder. The run stops at the first failing step and exits 0 only when every step and every run check passed, which
a control run never does.
"""
import argparse
import datetime
import json
import pathlib
import sys
import time
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright

# The calendar names, guard window, title, locators, clipboard stand-in and browser launch the pytest suite uses.
from conftest import (
    CLIPBOARD_STANDIN,
    ENGINES,
    GUARD_WINDOW_MS,
    add_habit,
    band_day,
    bead,
    bin_btn,
    confirm_delete,
    dialog_title,
    done_btn,
    launch,
    long_date,
    p3_day,
    sample_state,
    short_date,
    tick,
    with_engine,
    year_btn,
    year_date,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
READ, STRETCH = "Read 20 pages", "Stretch 10 minutes"
PHONE, DESKTOP = (390, 844), (1280, 800)
STEP_SECONDS = 5  # qa.md, 5 seconds per expectation
POLL_MS = 100
# A check that holds is read once more after this pause. The close event is a queued task, so in Chromium the browser's
# own focus restore can show the opener focused before the app's close handler has run, and that must not pass a step.
SETTLE_MS = 150
PAUSE_MS = GUARD_WINDOW_MS + 100  # qa.md's 600 ms after a click inside a popup, for the page guard of R14
CONTROLS = ("seeded",)
FIRST_VISIT = "first visit"
# The two properties the control must fail on (spec R27). Problem lines start with them, so the summary can find them.
STORED_IS_NULL = "stored(page) is null"
EMPTY_LIST = 'ul.rows holds li.empty with "No habits yet."'
CLIPBOARD_MARK = "test:clipboard:"
NO_STREAK = ["Current", "No streak yet"]
LOCAL_DATE_JS = "() => { const d = new Date(); return [d.getFullYear(), d.getMonth() + 1, d.getDate()]; }"

# Read-only, everything a step's check looks at, in one round trip. `t` and `y` are the date keys of T and Y.
# A stats block reads as its words in order, ["Current", "2", "days"], ["Current", "No streak yet"] or ["Best", "2"].
# Focus reads as where it is (a popup's class, "band", "page" or "body") and what it is.
SNAPSHOT_JS = """([t, y]) => {
  const one = (selector) => document.querySelector(selector);
  const text = (node) => (node ? node.textContent : null);
  const attr = (node, name) => (node ? node.getAttribute(name) : null);
  const classes = (node) => Array.from(node.classList).filter((name) => name !== 'pop' && name !== 'bump');
  const words = (node) => node && [text(node.querySelector('.lbl')), ...Array.from(node.querySelectorAll('.num, .unit, .none'), text)];
  const stats = (node) => node && { current: words(node.querySelector('.stat.cur')), best: words(node.querySelector('.stat.best')) };
  const day = (selector) => {
    const button = one(selector);
    return button && { label: attr(button, 'aria-label'), current: attr(button, 'aria-current'), classes: classes(button) };
  };
  const place = (node) => {
    const dialog = node.closest('dialog');
    if (dialog) return ['dlg-ov', 'dlg-all', 'dlg-year', 'dlg-day', 'dlg-del'].find((name) => dialog.classList.contains(name));
    return node.closest('section.band') ? 'band' : 'page';
  };
  const active = document.activeElement;
  const band = one('section.band');
  const ring = one(`section.band div.ovg-cols button.hc[data-key="${t}"] > svg`);
  const field = one('#nh');
  const message = one('#nh-msg');
  const writeText = typeof Clipboard === 'function' ? Clipboard.prototype.writeText : undefined;
  return {
    standIn: typeof writeText !== 'function' || !Function.prototype.toString.call(writeText).includes('[native code]'),
    stored: localStorage.getItem('streaks.state'),
    empty: Array.from(document.querySelectorAll('ul.rows > li.empty'), (item) => [text(item.querySelector('p.lead')), text(item.querySelector('p.line'))]),
    rows: Array.from(document.querySelectorAll('ul.rows > li.row'), (item) => ({
      name: text(item.querySelector('h3.r-name')),
      ...stats(item.querySelector('p.stats')),
      done: attr(item.querySelector('button.btn-done'), 'aria-pressed'),
    })),
    banners: one('div.banners').childElementCount,
    overview: attr(one('button.ov-btn'), 'aria-label'),
    composer: { value: field.value, invalid: attr(field, 'aria-invalid'), message: message.textContent, classes: message.className, hidden: message.hidden },
    open: Object.fromEntries(Array.from(document.querySelectorAll('dialog'), (dialog) => [place(dialog), dialog.open])),
    focus: !active || active === document.body ? { place: 'body' } : {
      place: place(active), tag: active.localName, classes: classes(active), label: attr(active, 'aria-label'),
      text: active.textContent.trim(), key: attr(active, 'data-key'),
    },
    band: {
      shown: getComputedStyle(band).display !== 'none' && band.getBoundingClientRect().width > 0,
      days: Array.from(band.querySelectorAll('div.ovg-cols button.hc'), (button) => [button.dataset.key, attr(button, 'aria-label'), attr(button, 'aria-current')]),
      t: day(`section.band div.ovg-cols button.hc[data-key="${t}"]`),
      y: day(`section.band div.ovg-cols button.hc[data-key="${y}"]`),
      tRing: ring && Array.from(ring.children, (node) => [[node.localName, ...classes(node)].join('.'), node.localName === 'text' ? node.textContent : null]),
    },
    p1: {
      title: text(one('#day-title')),
      sub: text(one('#day-sub')),
      ticks: Array.from(document.querySelectorAll('dialog.dlg-day ul.day-list button.tick'), (button) => ({
        name: attr(button, 'aria-label'), pressed: attr(button, 'aria-pressed'), stat: Array.from(button.querySelectorAll(':scope > span.tstat > span'), text),
      })),
    },
    p2: { title: text(one('#yr-title')), stats: stats(one('dialog.dlg-year p.yr-stats')), y: attr(one(`dialog.dlg-year div.months button.yc[data-key="${y}"]`), 'aria-pressed') },
    p3: { y: day(`dialog.dlg-ov div.ovg-rows button.hc[data-key="${y}"]`) },
    p4: { t: day(`dialog.dlg-all div.months button.hc[data-key="${t}"]`) },
    m1: { title: text(one('#del-title')) },
  };
}"""

STILL_JS = """(name) => {
  const dialog = document.querySelector(`dialog.${name}`);
  return dialog.open && dialog.querySelector(':scope > div.dlg-box').getAnimations().length === 0;
}"""


def shorten(value, limit=160):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else f"{text[:limit]}... ({len(text)} characters)"


def mismatches(*checks):
    """One line per (property, found, wanted) whose found value is not the wanted one. No line means the step holds."""
    return [f"{what}, found {shorten(found)}, expected {shorten(wanted)}" for what, found, wanted in checks if found != wanted]


def focus_view(found, wanted):
    """The properties of the focused element that `wanted` names, to compare with it. "class" holds when the element
    carries that class."""
    view = {}
    for name, value in wanted.items():
        if name == "class":
            view[name] = value if value in found.get("classes", []) else found.get("classes")
        else:
            view[name] = found.get(name)
    return view


def focus_on(found, what, **wanted):
    return (f"focus is on {what}", focus_view(found, wanted), wanted)


def current(days):
    return ["Current", str(days), "day" if days == 1 else "days"]


def best(days):
    return ["Best", str(days)]


def shown_row(name, current_words, best_words, done):
    return {"name": name, "current": current_words, "best": best_words, "done": done}


def band_difference(found, wanted):
    """The first band day button that differs from the one wanted, as one line, so a band of 84 days stays readable."""
    if found == wanted:
        return []
    index = next((i for i, (a, b) in enumerate(zip(found, wanted)) if a != b), min(len(found), len(wanted)))
    return [
        f"every band day button up to T is named '<shortDate>, 0 of 0 habits' and only T's has aria-current 'date', "
        f"found {len(found)} buttons, expected {len(wanted)}, first difference at index {index}, found "
        f"{shorten(found[index:index + 1])}, expected {shorten(wanted[index:index + 1])}"
    ]


def wait_until_still(page, name):
    """Wait until the popup `name` is open and its box has ended its rise, so a click inside it lands where it rests, as
    a person's would. A click sent during the rise made Playwright scroll P2's body 144 px first (measured at task 27).
    Polled from here with a deadline."""
    deadline = time.monotonic() + STEP_SECONDS
    while not page.evaluate(STILL_JS, name):
        if time.monotonic() > deadline:
            raise TimeoutError(f"dialog.{name} was not open and still within {STEP_SECONDS} s")
        page.wait_for_timeout(POLL_MS)


class Gate:
    """Runs the steps in order and keeps the evidence of each.

    The run stops at the first failing step, because every later step builds on the state the earlier ones left, and
    the control must stop at the first visit (qa.md).
    """

    def __init__(self, page, out, keys):
        self.page, self.out, self.keys, self.steps = page, out, keys, []

    def read(self, check):
        try:
            observed = self.page.evaluate(SNAPSHOT_JS, self.keys)
            return observed, check(observed)
        except Exception as exc:
            return {"error": repr(exc)}, [f"the page could not be read or checked, {exc!r}"]

    def settle(self, check):
        """Read the page until `check` finds no problem and still finds none SETTLE_MS later, or until STEP_SECONDS pass."""
        deadline = time.monotonic() + STEP_SECONDS
        while True:
            observed, problems = self.read(check)
            if not problems:
                self.page.wait_for_timeout(SETTLE_MS)
                observed, problems = self.read(check)
                if not problems:
                    return observed, problems
            if time.monotonic() > deadline:
                return observed, problems
            self.page.wait_for_timeout(POLL_MS)

    def step(self, name, gesture, expected, do, check, keep_band_days=False):
        """Do the gesture, check the page, save a full-page screenshot and the record, and return whether it passed."""
        number = len(self.steps) + 1
        shot = f"{number:02d}-{name.replace(' ', '-')}.png"
        started = time.monotonic()
        error = None
        try:
            do()
        except (Exception, pytest.fail.Exception) as exc:  # point_beside reports a missing box through pytest.fail
            error = f"{type(exc).__name__}: {exc}"
        observed, problems = self.read(check) if error else self.settle(check)
        if error:
            problems = [f"the gesture failed, {error}"] + problems
        try:
            self.page.screenshot(path=str(self.out / shot), full_page=True)
        except Exception as exc:
            problems.append(f"no screenshot, {exc!r}")
            shot = None
        if not keep_band_days and isinstance(observed.get("band"), dict):
            observed["band"].pop("days", None)
        self.steps.append({
            "step": number, "name": name, "gesture": gesture, "expected": expected, "observed": observed,
            "problems": problems, "pass": not problems, "at": datetime.datetime.now().isoformat(timespec="milliseconds"),
            "seconds": round(time.monotonic() - started, 2), "screenshot": shot,
        })
        print(f"{'PASS' if not problems else 'FAIL'} {number:02d} {name}", flush=True)
        for problem in problems:
            print(f"    {problem}", flush=True)
        return not problems


class Scenario:
    """The @R27 scenario of qa.md as named steps over one page, done in order by `run` until one fails.

    T is the browser's local date when the run started and Y the day before. Gestures are clicks, typing, key presses,
    reloads and one viewport change. Each pause waits out the page guard of R14 after a click inside a popup.
    """

    def __init__(self, page, gate, base_url, t_key, y_key):
        self.page, self.gate, self.base_url = page, gate, base_url
        self.t, self.y = t_key, y_key
        self.rows_before_reload = None

    def steps(self):
        return [
            self.open_the_app, self.add_the_first_habit, self.add_a_second_habit, self.mark_both_done_today,
            self.open_yesterday_from_the_overview, self.tick_yesterday_in_the_day_editor, self.close_the_day_editor,
            self.close_the_overview, self.tick_yesterday_in_the_year_view, self.close_the_year_view,
            self.reload_keeps_everything, self.ask_to_delete, self.keep_the_habit, self.delete_the_habit,
            self.add_a_duplicate, self.reload_keeps_one_habit, self.widen_to_the_desktop,
            self.open_yesterday_from_the_band, self.close_the_day_editor_over_the_band, self.open_the_year_of_all_habits,
            self.close_the_year_of_all_habits,
        ]

    def run(self):
        for step in self.steps():
            if not step():
                return

    # -- gestures
    def pause(self):
        self.page.wait_for_timeout(PAUSE_MS)

    def close_button(self, name):
        return self.page.locator(f"dialog.{name}").get_by_role("button", name="Close", exact=True)

    def empty_band(self):
        """The band's day buttons of a first visit, oldest first. Twelve weeks end with T's week, and every day up to T
        is a button (spec R3, R35)."""
        today = datetime.date.fromisoformat(self.t)
        first = today - datetime.timedelta(days=today.weekday() + 77)
        keys = [(first + datetime.timedelta(days=i)).isoformat() for i in range((today - first).days + 1)]
        return [[key, f"{short_date(key)}, 0 of 0 habits", "date" if key == self.t else None] for key in keys]

    # -- the steps, each a When and its Then lines
    def open_the_app(self):
        return self.gate.step(
            FIRST_VISIT, "page.goto(BASE_URL)",
            "S1, li.empty with its two lines, no li.row, no banner, Overview 0 of 0, every band day up to T at 0 of 0 with T "
            "current, nothing stored, and the clipboard stand-in in place before any gesture",
            do=lambda: self.page.goto(self.base_url),
            check=lambda s: mismatches(
                ("Clipboard.prototype.writeText is absent or is not the browser's native function", s["standIn"], True),
                (STORED_IS_NULL, s["stored"], None),
                (EMPTY_LIST, s["empty"], [["No habits yet.", "Add one you want to do every day."]]),
                ("there is no li.row", len(s["rows"]), 0),
                ("there is no banner", s["banners"], 0),
                ("the Overview button's name", s["overview"], "Overview, today 0 of 0 habits done"),
            ) + band_difference(s["band"]["days"], self.empty_band()),
            keep_band_days=True,
        )

    def add_the_first_habit(self):
        return self.gate.step(
            "added", "click #nh, keyboard.type, click Add",
            "one row Read 20 pages, Current with No streak yet and no Best, Done today not pressed, the field empty",
            do=lambda: add_habit(self.page, READ),
            check=lambda s: mismatches(
                ("the rows", s["rows"], [shown_row(READ, NO_STREAK, None, "false")]),
                ("the field's text", s["composer"]["value"], ""),
            ),
        )

    def add_a_second_habit(self):
        return self.gate.step(
            "second habit", "click #nh, keyboard.type, Enter", "a second row Stretch 10 minutes under the first",
            do=lambda: add_habit(self.page, STRETCH, enter=True),
            check=lambda s: mismatches(("the row names in order", [r["name"] for r in s["rows"]], [READ, STRETCH])),
        )

    def mark_both_done_today(self):
        def do():
            done_btn(self.page, READ).click()
            done_btn(self.page, STRETCH).click()

        return self.gate.step(
            "done today", "click Done today of Read, click Done today of Stretch",
            "both rows Current 1 day and Best 1, the Overview button 2 of 2 done",
            do=do,
            check=lambda s: mismatches(
                ("the rows", s["rows"], [shown_row(READ, current(1), best(1), "true"), shown_row(STRETCH, current(1), best(1), "true")]),
                ("the Overview button's name", s["overview"], "Overview, today 2 of 2 habits done"),
            ),
        )

    def open_yesterday_from_the_overview(self):
        def do():
            self.page.locator("button.ov-btn").click()
            wait_until_still(self.page, "dlg-ov")
            p3_day(self.page, self.y).click()

        return self.gate.step(
            "day editor from the overview", "click Overview, wait until P3 rests, click P3's button for Y",
            "P1 open for Y with 0 of 2 habits, its first tick focused",
            do=do,
            check=lambda s: mismatches(
                ("P1 is open", s["open"]["dlg-day"], True),
                ("P1's title", s["p1"]["title"], long_date(self.y)),
                ("P1's subtitle", s["p1"]["sub"], "0 of 2 habits"),
                ("P1's first tick", [t["name"] for t in s["p1"]["ticks"]][:1], [READ]),
                focus_on(s["focus"], "P1's first tick", place="dlg-day", label=READ),
            ),
        )

    def tick_yesterday_in_the_day_editor(self):
        return self.gate.step(
            "ticked in the day editor", "click the tick Read 20 pages",
            "the tick pressed, P1 1 of 2 habits, the tick Current 2 days and Best 2",
            do=lambda: tick(self.page, READ).click(),
            check=lambda s: mismatches(
                ("the tick Read 20 pages", s["p1"]["ticks"][:1], [{"name": READ, "pressed": "true", "stat": ["Current 2 days", "Best 2"]}]),
                ("P1's subtitle", s["p1"]["sub"], "1 of 2 habits"),
            ),
        )

    def close_the_day_editor(self):
        return self.gate.step(
            "day editor closed", "click P1's Close", "P1 closed, focus on P3's button for Y, now 1 of 2 habits",
            do=lambda: self.close_button("dlg-day").click(),
            check=lambda s: mismatches(
                ("P1 is closed", s["open"]["dlg-day"], False),
                focus_on(s["focus"], "P3's button for Y", place="dlg-ov", key=self.y, **{"class": "hc"}),
                ("P3's button for Y", (s["p3"]["y"] or {}).get("label"), f"{short_date(self.y)}, 1 of 2 habits"),
            ),
        )

    def close_the_overview(self):
        def do():
            self.pause()
            self.close_button("dlg-ov").click()

        return self.gate.step(
            "overview closed", "pause 600 ms, click P3's Close", "P3 closed, focus on Overview, Read Current 2 days and Best 2",
            do=do,
            check=lambda s: mismatches(
                ("P3 is closed", s["open"]["dlg-ov"], False),
                focus_on(s["focus"], "the Overview button", place="page", **{"class": "ov-btn"}),
                ("Read's numbers", [s["rows"][0]["current"], s["rows"][0]["best"]], [current(2), best(2)]),
            ),
        )

    def tick_yesterday_in_the_year_view(self):
        def do():
            self.pause()
            year_btn(self.page, STRETCH).click()
            wait_until_still(self.page, "dlg-year")
            bead(self.page, self.y).click()

        return self.gate.step(
            "ticked in the year view", "pause 600 ms, click Year view of Stretch, wait until P2 rests, click the bead for Y",
            "the bead pressed, P2's stats Current 2 days and Best 2",
            do=do,
            check=lambda s: mismatches(
                ("P2 is open for Stretch 10 minutes", [s["open"]["dlg-year"], s["p2"]["title"]], [True, STRETCH]),
                ("the bead for Y is pressed", s["p2"]["y"], "true"),
                ("P2's stats", s["p2"]["stats"], {"current": current(2), "best": best(2)}),
            ),
        )

    def close_the_year_view(self):
        return self.gate.step(
            "year view closed", "click P2's Close", "P2 closed, focus on Year view of Stretch, Stretch Current 2 days and Best 2",
            do=lambda: self.close_button("dlg-year").click(),
            check=lambda s: mismatches(
                ("P2 is closed", s["open"]["dlg-year"], False),
                focus_on(s["focus"], "Year view, Stretch 10 minutes", place="page", label=f"Year view, {STRETCH}"),
                ("Stretch's numbers", [s["rows"][1]["current"], s["rows"][1]["best"]], [current(2), best(2)]),
            ),
        )

    def reload_keeps_everything(self):
        def do():
            self.rows_before_reload = self.page.evaluate(SNAPSHOT_JS, self.gate.keys)["rows"]
            self.page.reload()

        return self.gate.step(
            "reloaded", "page.reload()", "both rows, their Done today states and their numbers unchanged",
            do=do,
            check=lambda s: mismatches(
                ("two rows before the reload", len(self.rows_before_reload), 2),
                ("the rows after the reload", s["rows"], self.rows_before_reload),
            ),
        )

    def ask_to_delete(self):
        return self.gate.step(
            "delete asked", "click Delete \"Stretch 10 minutes\"", "M1 open with its title, Cancel focused",
            do=lambda: bin_btn(self.page, STRETCH).click(),
            check=lambda s: mismatches(
                ("M1 is open", s["open"]["dlg-del"], True),
                ("#del-title", s["m1"]["title"], dialog_title(STRETCH)),
                focus_on(s["focus"], "Cancel", place="dlg-del", text="Cancel"),
            ),
        )

    def keep_the_habit(self):
        return self.gate.step(
            "delete kept", "click Cancel", "M1 closed, 2 rows, focus on Delete \"Stretch 10 minutes\"",
            do=lambda: self.page.locator("dialog.dlg-del").get_by_role("button", name="Cancel", exact=True).click(),
            check=lambda s: mismatches(
                ("M1 is closed", s["open"]["dlg-del"], False),
                ("rows remaining", len(s["rows"]), 2),
                focus_on(s["focus"], 'Delete "Stretch 10 minutes"', place="page", label=f'Delete "{STRETCH}"'),
            ),
        )

    def delete_the_habit(self):
        def do():
            self.pause()
            bin_btn(self.page, STRETCH).click()
            wait_until_still(self.page, "dlg-del")
            confirm_delete(self.page, bin_btn(self.page, STRETCH))

        return self.gate.step(
            "deleted",
            "pause 600 ms, click Delete \"Stretch 10 minutes\", wait until M1 rests, click Delete habit at the centre of the "
            "largest part of it outside the bin's box",
            "1 row, focus on Delete \"Read 20 pages\", the Overview button 1 of 1 done",
            do=do,
            check=lambda s: mismatches(
                ("M1 is closed", s["open"]["dlg-del"], False),
                ("the row names", [r["name"] for r in s["rows"]], [READ]),
                focus_on(s["focus"], 'Delete "Read 20 pages"', place="page", label=f'Delete "{READ}"'),
                ("the Overview button's name", s["overview"], "Overview, today 1 of 1 habits done"),
            ),
        )

    def add_a_duplicate(self):
        def do():
            self.pause()
            add_habit(self.page, "read 20 pages", enter=True)

        return self.gate.step(
            "name error", "pause 600 ms, click #nh, keyboard.type, Enter",
            "#nh-msg You already track this habit. with field-msg err, the field keeps its text with aria-invalid true",
            do=do,
            check=lambda s: mismatches(
                ("#nh-msg", [s["composer"]["message"], s["composer"]["classes"], s["composer"]["hidden"]],
                 ["You already track this habit.", "field-msg err", False]),
                ("the field", [s["composer"]["value"], s["composer"]["invalid"]], ["read 20 pages", "true"]),
            ),
        )

    def reload_keeps_one_habit(self):
        return self.gate.step(
            "reloaded again", "page.reload()", "exactly one row Read 20 pages, Current 2 days, Best 2, Done today pressed",
            do=self.page.reload,
            check=lambda s: mismatches(("the rows", s["rows"], [shown_row(READ, current(2), best(2), "true")])),
        )

    def widen_to_the_desktop(self):
        day_number = str(datetime.date.fromisoformat(self.t).day)
        return self.gate.step(
            "desktop band", "page.set_viewport_size(1280 x 800)",
            "the band shown, T's button 1 of 1 with the today circle, one seg on, the core and the number on",
            do=lambda: self.page.set_viewport_size({"width": DESKTOP[0], "height": DESKTOP[1]}),
            check=lambda s: mismatches(
                ("the band is shown", s["band"]["shown"], True),
                ("T's band button's name", (s["band"]["t"] or {}).get("label"), f"{short_date(self.t)}, 1 of 1 habits"),
                ("T's band ring", s["band"]["tRing"],
                 [["circle.c-today", None], ["circle.seg.on", None], ["circle.c-core", None], ["text.c-num.on", day_number]]),
            ),
        )

    def open_yesterday_from_the_band(self):
        return self.gate.step(
            "day editor from the band", "click Y's band button", "P1 open for Y with 1 of 1 habits, the tick Read 20 pages pressed",
            do=lambda: band_day(self.page, self.y).click(),
            check=lambda s: mismatches(
                ("P1 is open", s["open"]["dlg-day"], True),
                ("P1's title", s["p1"]["title"], long_date(self.y)),
                ("P1's subtitle", s["p1"]["sub"], "1 of 1 habits"),
                ("the tick Read 20 pages is pressed", [[t["name"], t["pressed"]] for t in s["p1"]["ticks"]], [[READ, "true"]]),
            ),
        )

    def close_the_day_editor_over_the_band(self):
        return self.gate.step(
            "day editor closed on the band", "click P1's Close", "P1 closed, focus on Y's band button",
            do=lambda: self.close_button("dlg-day").click(),
            check=lambda s: mismatches(
                ("P1 is closed", s["open"]["dlg-day"], False),
                focus_on(s["focus"], "Y's band button", place="band", key=self.y, **{"class": "hc"}),
            ),
        )

    def open_the_year_of_all_habits(self):
        def do():
            self.pause()
            self.page.locator("section.band button.btn-all").click()

        return self.gate.step(
            "year of all habits", "pause 600 ms, click the band's Year", "P4 open, Close focused, T's P4 button 1 of 1",
            do=do,
            check=lambda s: mismatches(
                ("P4 is open", s["open"]["dlg-all"], True),
                focus_on(s["focus"], "P4's Close", place="dlg-all", label="Close"),
                ("T's P4 button's name", (s["p4"]["t"] or {}).get("label"), f"{year_date(self.t)}, 1 of 1 habits"),
            ),
        )

    def close_the_year_of_all_habits(self):
        return self.gate.step(
            "year of all habits closed", "keyboard.press(Escape)", "P4 closed, focus on the band's Year",
            do=lambda: self.page.keyboard.press("Escape"),
            check=lambda s: mismatches(
                ("P4 is closed", s["open"]["dlg-all"], False),
                focus_on(s["focus"], "the band's Year", place="band", **{"class": "btn-all"}),
            ),
        )


def seed(page, base_url):
    """The control's one write. The sample goes into storage through the same-origin __seed__ page (a 404 page of
    http.server, so no app code runs), before the app loads."""
    page.goto(base_url + "__seed__")
    page.evaluate("(text) => localStorage.setItem('streaks.state', text)", sample_state())


def request_is_allowed(request, origin, allowed_paths):
    parts = urlsplit(request["url"])
    return (
        request["method"] == "GET" and f"{parts.scheme}://{parts.netloc}" == origin
        and parts.query == "" and parts.path in allowed_paths
    )


def read_local_date(page):
    return datetime.date(*page.evaluate(LOCAL_DATE_JS))


def run(engine, base_url, out, control):
    out.mkdir(parents=True, exist_ok=True)
    requests, console, errors = [], [], []
    with sync_playwright() as playwright:
        browser = launch(playwright, engine)
        try:
            context = browser.new_context(viewport={"width": PHONE[0], "height": PHONE[1]})
            context.add_init_script(CLIPBOARD_STANDIN)
            context.set_default_timeout(STEP_SECONDS * 1000)
            context.set_default_navigation_timeout(2 * STEP_SECONDS * 1000)
            page = context.new_page()
            page.goto("about:blank")
            start = read_local_date(page)
            if control == "seeded":
                seed(page, base_url)
            page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))
            page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
            page.on("pageerror", lambda e: errors.append(str(e)))

            t_key, y_key = start.isoformat(), (start - datetime.timedelta(days=1)).isoformat()
            gate = Gate(page, out, [t_key, y_key])
            scenario = Scenario(page, gate, base_url, t_key, y_key)
            planned = len(scenario.steps())
            scenario.run()
            try:
                end = read_local_date(page)
            except Exception:
                end = None
            browser_version = browser.version
        finally:
            browser.close()

    parts = urlsplit(base_url)
    allowed = {"/", "/index.html", "/favicon.ico", "/src/styles.css", "/src/icon.svg"} | {
        f"/src/{p.name}" for p in (ROOT / "src").glob("*.js")
    }
    outside = [r for r in requests if not request_is_allowed(r, f"{parts.scheme}://{parts.netloc}", allowed)]
    console_errors = [m for m in console if m["type"] == "error"]
    clipboard_marks = [m for m in console if m["text"].startswith(CLIPBOARD_MARK)]
    failing = next((s for s in gate.steps if not s["pass"]), None)
    every_step_passed = failing is None and len(gate.steps) == planned
    passed = (
        control is None and every_step_passed and not outside and not console_errors and not errors
        and not clipboard_marks and end == start
    )
    summary = {
        "control": control, "engine": engine, "browser_version": browser_version, "base_url": base_url,
        "start_date": start.isoformat(), "end_date": end and end.isoformat(), "date_unchanged": end == start,
        "steps_planned": planned, "steps_run": len(gate.steps), "steps_passed": sum(s["pass"] for s in gate.steps),
        "first_failing_step": failing and failing["name"],
        "requests": len(requests), "requests_outside_the_rule": len(outside), "console_errors": len(console_errors),
        "page_errors": len(errors), "clipboard_marks": len(clipboard_marks), "pass": passed,
    }
    if control:
        problems = failing["problems"] if failing else []
        summary["control_red_on_its_property"] = bool(
            failing and failing["name"] == FIRST_VISIT
            and any(p.startswith(STORED_IS_NULL) for p in problems) and any(p.startswith(EMPTY_LIST) for p in problems)
        )

    def save(name, data):
        (out / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    save("steps.json", gate.steps)
    save("console.json", {"console": console, "page_errors": errors})
    save("network.json", {"requests": requests, "outside_the_rule": outside})
    save("summary.json", summary)
    if control:
        verdict = "RED at the first-visit step on its property" if summary["control_red_on_its_property"] else (
            "NOT RED at the first-visit step on its property, so the gate cannot tell a seeded start from a cold one")
        print(f"CONTROL {control} {verdict} ->", out)
    else:
        print("GATE " + ("PASS" if passed else "FAIL"), "->", out)
    return 0 if passed else 1


def evidence_folder(out, engine, control):
    """--out with its last part ending in -<engine>, or in -<engine>-control for a control run (spec R27, R30)."""
    if control is None:
        return with_engine(out, engine)
    ending = f"-{engine}-control"
    if pathlib.PurePath(out).name.endswith(ending):
        return out
    folder = pathlib.PurePath(with_engine(out, engine))
    return str(folder.with_name(folder.name + "-control"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--engine", choices=ENGINES, default=ENGINES[0])
    parser.add_argument("--base-url", required=True, help="the app's address, ending with /")
    parser.add_argument("--out", required=True, help="a new or empty folder inside the project, normally docs/modules/app/qa/live-e2e/<datetimestamp>-<engine>/")
    parser.add_argument("--control", choices=CONTROLS, default=None, help="seeded, the gate's control run, which must fail at the first visit")
    arguments = parser.parse_args()
    if not arguments.base_url.endswith("/"):
        sys.exit(f"--base-url must end with /, got {arguments.base_url}")
    destination = (ROOT / evidence_folder(arguments.out, arguments.engine, arguments.control)).resolve()
    if ROOT not in destination.parents:
        sys.exit(f"--out must be inside the project, got {destination}")
    if destination.exists() and any(destination.iterdir()):
        sys.exit(f"--out already holds files, and a run never writes over another run, {destination}")
    sys.exit(run(arguments.engine, arguments.base_url, destination, arguments.control))
