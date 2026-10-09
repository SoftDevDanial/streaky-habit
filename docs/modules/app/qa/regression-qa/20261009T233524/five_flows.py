"""Regression QA, brief item 3: the five hand-driven flows at 390 x 844.

Real gestures only: click, keyboard.type, keyboard.press and reload. Time is Playwright's clock. The clock
is installed at Thursday 8 October 2026 12:00:00 (+08:00) and paused at 12:00:20 after the first load, so
every flow sees one instant, and page.clock.run_for passes the 500 ms guard windows (the dialog's guard
on "Delete habit", and the page's guard that ignores clicks for 500 ms after a click in the dialog). The
script writes nothing to the app (the app saves on its own). Output: one full-page screenshot per observed
step and five-flows.json in --out.
--no-wait-after-delete skips the pause after "Delete habit", which reproduces the page guard: the Add click
of flow 5 then lands 0 ms after the dialog click and is ignored (spec R13 note, SEC-01).
Usage: python five_flows.py --base-url http://127.0.0.1:<port>/ --out <folder> [--no-wait-after-delete]
"""
import argparse
import json
import pathlib
import sys
import time

from playwright.sync_api import expect, sync_playwright

NOON = "2026-10-08T12:00:00+08:00"
PAUSE_AT = "2026-10-08T12:00:20+08:00"
PAST_GUARD_MS = 600  # the 500 ms guards have passed
READ = "Read 20 pages"
STRETCH = "Stretch 10 minutes"
TODAY = "2026-10-08"
YESTERDAY = "2026-10-07"
EMPTY_TEXT = "No habits yet. Add one you want to do every day."
DUPLICATE_TEXT = "You already track this habit."
# U+2068 and U+2069 wrap the name in the dialog title (spec R13 note, SEC-02). Built with chr() on purpose.
FSI, PDI = chr(0x2068), chr(0x2069)

OBSERVE_JS = """() => {
  const text = (node) => (node ? node.textContent : null);
  const rows = Array.from(document.querySelectorAll('li.habit')).map((li) => ({
    name: text(li.querySelector('h3')),
    cur: text(li.querySelector('.streak .cur')),
    best: text(li.querySelector('.streak .best')),
    strip: Array.from(li.querySelectorAll('button.day'))
      .map((b) => (b.getAttribute('aria-pressed') === 'true' ? 'D' : '.')).join(' '),
  }));
  const active = document.activeElement;
  const time = document.querySelector('p.date time');
  const field = document.querySelector('#new-habit');
  const cell = (key) => {
    const c = document.querySelector('.cells .hc[data-date="' + key + '"]');
    return c ? [c.getAttribute('aria-label'), c.className] : null;
  };
  return {
    date: time ? [time.getAttribute('datetime'), time.textContent] : null,
    empty: text(document.querySelector('p.empty')),
    rows,
    field: field.value,
    fieldAriaInvalid: field.getAttribute('aria-invalid'),
    message: text(document.querySelector('#new-habit-msg')),
    dialogOpen: document.querySelector('dialog.dialog').open,
    dialogTitle: text(document.querySelector('#del-title')),
    focus: active.id ? '#' + active.id : (active.getAttribute('aria-label') || active.textContent.trim()),
    stored: localStorage.getItem('streaks.state'),
    todayCell: cell('2026-10-08'),
    yesterdayCell: cell('2026-10-07'),
  };
}"""


class Flows:
    def __init__(self, page, out, base_url, settle_after_delete):
        self.page = page
        self.out = out
        self.base_url = base_url
        self.settle_after_delete = settle_after_delete
        self.observations = []
        self.checks = []
        self.errors = []

    def observe(self, label, shot=None):
        data = self.page.evaluate(OBSERVE_JS)
        entry = {"step": label, "screenshot": f"{shot}.png" if shot else None, "observed": data}
        if shot:
            self.page.screenshot(path=str(self.out / f"{shot}.png"), full_page=True)
        self.observations.append(entry)
        return data

    def check(self, name, passed, detail=""):
        self.checks.append({"check": name, "pass": bool(passed), "detail": detail})
        print(("PASS " if passed else "FAIL ") + name, flush=True)

    def bead(self, name, date):
        row = self.page.locator("li.habit").filter(has=self.page.get_by_text(name, exact=True))
        return row.locator(f'button.day[data-date="{date}"]')

    def add_by_click(self, text):
        self.page.locator("#new-habit").click()
        self.page.keyboard.type(text)
        self.page.get_by_role("button", name="Add", exact=True).click()

    def add_by_enter(self, text):
        self.page.locator("#new-habit").click()
        self.page.keyboard.type(text)
        self.page.keyboard.press("Enter")

    def flow_1_first_visit_and_two_habits(self):
        page = self.page
        page.goto(self.base_url)
        page.clock.pause_at(PAUSE_AT)  # after the first load: one instant for every flow from here on
        expect(page.locator("p.empty")).to_be_visible()
        first = self.observe("1.1 first visit, no storage", "f1-01-first-visit")
        self.check("1.1 empty first screen, nothing stored", first["empty"] == EMPTY_TEXT and first["stored"] is None and not first["rows"])

        self.add_by_click(READ)
        expect(page.locator("li.habit")).to_have_count(1)
        added = self.observe("1.2 typed Read 20 pages and clicked Add", "f1-02-added-read")
        self.check(
            "1.2 one row, no streak yet, field cleared",
            [r["name"] for r in added["rows"]] == [READ] and added["rows"][0]["cur"] == "No streak yet" and added["field"] == "",
        )

        self.add_by_enter(STRETCH)
        expect(page.locator("li.habit")).to_have_count(2)
        second = self.observe("1.3 typed Stretch 10 minutes and pressed Enter", "f1-03-added-stretch")
        self.check(
            "1.3 second habit at the bottom, field cleared, focus stays in the field",
            [r["name"] for r in second["rows"]] == [READ, STRETCH] and second["field"] == "" and second["focus"] == "#new-habit",
        )

    def flow_2_tick_today_and_yesterday(self):
        page = self.page
        read_streak = page.locator("li.habit").filter(has=page.get_by_text(READ, exact=True)).locator("p.streak")
        before = self.observe("2.0 before ticks")
        self.bead(READ, TODAY).click()
        expect(read_streak.locator(".cur")).to_have_text("1 day")
        today = self.observe("2.1 clicked today's bead (Thu 8 Oct) on Read", "f2-01-ticked-today")
        self.check(
            "2.1 Read shows 1 day and Best 1, today saved",
            today["rows"][0]["cur"] == "1 day" and today["rows"][0]["best"] == "Best 1" and TODAY in (today["stored"] or ""),
            f"before the tick: {before['rows'][0]['cur']} / {before['rows'][0]['best']}",
        )

        self.bead(READ, YESTERDAY).click()
        expect(read_streak.locator(".cur")).to_have_text("2 days")
        yesterday = self.observe("2.2 clicked yesterday's bead (Wed 7 Oct) on Read", "f2-02-ticked-yesterday")
        self.check(
            "2.2 Read shows 2 days and Best 2, yesterday saved too",
            yesterday["rows"][0]["cur"] == "2 days" and yesterday["rows"][0]["best"] == "Best 2"
            and YESTERDAY in (yesterday["stored"] or "") and TODAY in (yesterday["stored"] or ""),
        )

    def flow_3_reload(self):
        page = self.page
        before = self.observe("3.0 before reload")
        page.reload()
        expect(page.locator("li.habit")).to_have_count(2)
        after = self.observe("3.1 after reload", "f3-01-reloaded")
        self.check(
            "3.1 after reload the rows, beads, streak lines and stored text are unchanged",
            after["rows"] == before["rows"] and after["stored"] == before["stored"],
        )

    def flow_4_delete_through_the_dialog(self):
        page = self.page
        page.get_by_role("button", name=f"Delete {STRETCH}", exact=True).click()
        expect(page.locator("dialog.dialog")).to_have_attribute("open", "")
        opened = self.observe("4.1 clicked Delete Stretch 10 minutes, dialog open", "f4-01-dialog")
        self.check(
            "4.1 dialog asks about Stretch, Cancel has focus",
            opened["dialogTitle"] == f'Delete "{FSI}{STRETCH}{PDI}"?' and opened["focus"] == "Cancel",
            f"title read {opened['dialogTitle']!r}, focus {opened['focus']!r}",
        )
        page.clock.run_for(PAST_GUARD_MS)  # wait past the 500 ms guard on "Delete habit", as a person does
        page.get_by_role("button", name="Delete habit", exact=True).click()
        page.wait_for_function("() => !document.querySelector('dialog.dialog').open", polling=100)
        expect(page.locator("li.habit")).to_have_count(1)
        deleted = self.observe("4.2 clicked Delete habit after the guard", "f4-02-deleted")
        self.check(
            "4.2 Stretch gone, Read kept, focus on the field, stored text holds Read only",
            [r["name"] for r in deleted["rows"]] == [READ] and deleted["focus"] == "#new-habit"
            and STRETCH not in (deleted["stored"] or "") and READ in (deleted["stored"] or ""),
        )
        if self.settle_after_delete:
            page.clock.run_for(PAST_GUARD_MS)  # the page ignores clicks for 500 ms after a click in the dialog

    def flow_5_duplicate_name(self):
        page = self.page
        before = self.observe("5.0 before the duplicate")
        self.add_by_click("read 20 pages")
        error = self.observe("5.1 typed read 20 pages and clicked Add", "f5-01-duplicate")
        self.check(
            "5.1 error shows, text stays, input marked invalid, nothing saved",
            error["message"] == DUPLICATE_TEXT and error["field"] == "read 20 pages" and error["fieldAriaInvalid"] == "true"
            and [r["name"] for r in error["rows"]] == [READ] and error["stored"] == before["stored"],
            f"message read {error['message']!r}",
        )

    def run(self):
        for flow in (
            self.flow_1_first_visit_and_two_habits,
            self.flow_2_tick_today_and_yesterday,
            self.flow_3_reload,
            self.flow_4_delete_through_the_dialog,
            self.flow_5_duplicate_name,
        ):
            try:
                flow()
            except Exception as exc:  # record and stop the chain, so the failure is evidence
                self.errors.append({"flow": flow.__name__, "error": repr(exc)[:600]})
                print("FAIL flow raised", flow.__name__, repr(exc)[:300], flush=True)
                break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--no-wait-after-delete", action="store_true")
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    console, page_errors, requests = [], [], []
    started = time.monotonic()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            color_scheme="light",
            reduced_motion="no-preference",
            timezone_id="Asia/Kuala_Lumpur",
            locale="en-US",
        )
        context.set_default_timeout(5000)
        context.clock.install(time=NOON)
        page = context.new_page()
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))

        flows = Flows(page, out, args.base_url, settle_after_delete=not args.no_wait_after_delete)
        flows.run()
        version = browser.version
        context.close()
        browser.close()

    passed = all(c["pass"] for c in flows.checks) and not flows.errors and not page_errors
    result = {
        "base_url": args.base_url,
        "viewport": "390x844",
        "clock": {"installed": NOON, "paused_at": PAUSE_AT},
        "wait_after_delete": not args.no_wait_after_delete,
        "browser": f"Chromium {version}",
        "seconds": round(time.monotonic() - started, 1),
        "checks": flows.checks,
        "flow_errors": flows.errors,
        "observations": flows.observations,
        "page_errors": page_errors,
        "console": console,
        "requests": requests,
        "pass": passed,
    }
    (out / "five-flows.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    checks_passed = sum(c["pass"] for c in flows.checks)
    print(f"FIVE FLOWS {'PASS' if passed else 'FAIL'}: {checks_passed}/{len(flows.checks)} checks, "
          f"{len(page_errors)} page errors, {len(flows.errors)} flow errors, {len(requests)} requests -> {out}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
