"""Cold-boot live-e2e gate (app spec R27, qa.md "@R27"). Not a pytest file, so pytest never collects it.

Why: it proves the shipped page works from nothing, on the real clock, driven only by real gestures
(click, keyboard.type, keyboard.press, reload), and leaves the evidence the Definition of done asks for.
Run: python tests/browser/live_e2e.py --base-url http://127.0.0.1:<port>/ --out docs/modules/app/qa/live-e2e/<datetimestamp>/
Input: the URL of the app, already served (this script starts nothing). Output: one full-page screenshot
per step, steps.json, console.json, network.json and summary.json in --out; exit 0 only when every step passed.
"""
import argparse
import datetime
import json
import pathlib
import sys
import time
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

from conftest import short_date  # the same calendar-table helper the pytest suite uses

ROOT = pathlib.Path(__file__).resolve().parents[2]
READ, STRETCH = "Read 20 pages", "Stretch 10 minutes"
STEP_TIMEOUT_SECONDS = 5
LOCAL_DATE_JS = "() => { const d = new Date(); return [d.getFullYear(), d.getMonth() + 1, d.getDate()]; }"

# Read-only: what is on the page right now.
SNAPSHOT_JS = """() => {
  const text = (node) => (node ? node.textContent : null);
  const rows = Array.from(document.querySelectorAll('li.habit')).map((li) => ({
    name: text(li.querySelector('h3')),
    cur: text(li.querySelector('.streak .cur')),
    best: text(li.querySelector('.streak .best')),
    dates: Array.from(li.querySelectorAll('button.day')).map((b) => b.dataset.date),
    pressed: Array.from(li.querySelectorAll('button.day')).map((b) => b.getAttribute('aria-pressed') === 'true'),
  }));
  const active = document.activeElement;
  return {
    rows,
    empty: text(document.querySelector('p.empty')),
    field: document.querySelector('#new-habit').value,
    message: text(document.querySelector('#new-habit-msg')),
    stored: localStorage.getItem('streaks.state'),
    cells: Array.from(document.querySelectorAll('.cells .hc')).map((c) => ({
      date: c.dataset.date, cls: c.className, label: c.getAttribute('aria-label'),
    })),
    active: { label: active.getAttribute('aria-label'), id: active.id, text: active.textContent.trim() },
    dialogOpen: document.querySelector('dialog.dialog').open,
    dialogTitle: text(document.querySelector('#del-title')),
  };
}"""


class Gate:
    """Runs the steps in order and keeps their evidence. A failed step is recorded and the run goes on."""

    def __init__(self, page, out):
        self.page, self.out, self.steps = page, out, []

    def step(self, shot, name, gesture, expected, do, check):
        """Do the gesture, then poll `check(snapshot)` for up to 5 seconds, then save a screenshot and the record."""
        started = time.monotonic()
        error = None
        try:
            do()
        except Exception as exc:
            error = repr(exc)
        deadline = time.monotonic() + STEP_TIMEOUT_SECONDS
        while True:
            try:
                observed = self.page.evaluate(SNAPSHOT_JS)
                passed = bool(check(observed)) and error is None
            except Exception as exc:
                observed, passed = {"error": repr(exc)}, False
            if passed or time.monotonic() > deadline:
                break
            self.page.wait_for_timeout(100)
        self.page.screenshot(path=str(self.out / f"{shot}.png"), full_page=True)
        observed.pop("cells", None)
        self.steps.append({
            "name": name, "gesture": gesture, "expected": expected, "observed": observed, "pass": passed,
            "error": error, "seconds": round(time.monotonic() - started, 2), "screenshot": f"{shot}.png",
        })
        print(("PASS " if passed else "FAIL ") + name, flush=True)


def request_is_allowed(request, origin, allowed_paths):
    parts = urlsplit(request["url"])
    return (
        request["method"] == "GET" and f"{parts.scheme}://{parts.netloc}" == origin
        and parts.query == "" and parts.path in allowed_paths
    )


def row_of(snapshot, name):
    return next((r for r in snapshot["rows"] if r["name"] == name), None)


def streak_of(snapshot, name):
    row = row_of(snapshot, name)
    return row["cur"], row["best"]


def cell_of(snapshot, key):
    found = next(c for c in snapshot["cells"] if c["date"] == key)
    return found["label"], found["cls"].split()


class Scenario:
    """The @R27 scenario as 11 named steps over one page; `run` does them in order.

    T is the browser's local date when the run started and Y the day before. Each step makes its
    gestures through `Gate.step`, which polls the step's check and saves the evidence.
    """

    def __init__(self, page, gate, base_url, t_key, y_key):
        self.page, self.gate, self.base_url = page, gate, base_url
        self.t_key, self.y_key = t_key, y_key
        self.t_short, self.y_short = short_date(t_key), short_date(y_key)
        self.field = page.locator("#new-habit")
        self.add = page.get_by_role("button", name="Add", exact=True)

    def run(self):
        for step in (
            self.open_the_app, self.add_the_first_habit, self.add_a_second_habit, self.tick_today,
            self.tick_yesterday, self.reload_keeps_everything, self.ask_to_delete, self.cancel_the_delete,
            self.delete_a_habit, self.add_a_duplicate, self.reload_keeps_one_habit,
        ):
            step()

    # -- the page, by real gestures
    def bead(self, name, key):
        row = self.page.locator("li.habit").filter(has=self.page.get_by_text(name, exact=True))
        return row.locator(f'button.day[data-date="{key}"]')

    def trash(self, name):
        return self.page.get_by_role("button", name=f"Delete {name}", exact=True)

    def type_name_and_press_enter(self, text):
        self.field.click()
        self.page.keyboard.type(text)
        self.page.keyboard.press("Enter")

    # -- the steps
    def open_the_app(self):
        def first_visit(s):
            past = [c for c in s["cells"] if c["date"] <= self.t_key]
            return (
                s["empty"] == "No habits yet. Add one you want to do every day." and not s["rows"] and s["stored"] is None
                and all(c["cls"].split()[:2] == ["hc", "l0"] and c["label"].endswith(", 0 of 0 habits") for c in past)
                and cell_of(s, self.t_key)[1] == ["hc", "l0", "today"]
            )

        self.gate.step(
            "01-first-visit", "open the app", gesture="page.goto(base_url)",
            expected="the empty first screen, T ringed, nothing stored",
            do=lambda: self.page.goto(self.base_url), check=first_visit,
        )

    def add_the_first_habit(self):
        def first_row_added(s):
            row = row_of(s, READ)
            return (
                len(s["rows"]) == 1 and row["pressed"] == [False] * 7 and row["dates"][-1] == self.t_key
                and streak_of(s, READ) == ("No streak yet", None) and s["field"] == ""
            )

        self.gate.step(
            "02-added", "click the field, type a name, click Add", gesture="click #new-habit; keyboard.type; click Add",
            expected="one row with 7 open beads ending with T",
            do=lambda: (self.field.click(), self.page.keyboard.type(READ), self.add.click()), check=first_row_added,
        )

    def add_a_second_habit(self):
        self.gate.step(
            "03-second-habit", "type a name, press Enter", gesture="click #new-habit; keyboard.type; Enter",
            expected="a second row under the first",
            do=lambda: self.type_name_and_press_enter(STRETCH),
            check=lambda s: [r["name"] for r in s["rows"]] == [READ, STRETCH],
        )

    def tick_today(self):
        def both_ticked_today(s):
            return (
                all(streak_of(s, name) == ("1 day", "Best 1") for name in (READ, STRETCH))
                and cell_of(s, self.t_key) == (f"{self.t_short}, 2 of 2 habits", ["hc", "l4", "today"])
            )

        self.gate.step(
            "04-ticked-today", "click T's bead of both rows", gesture="click T bead twice",
            expected="1 day and Best 1 on both rows, T's cell at level 4",
            do=lambda: (self.bead(READ, self.t_key).click(), self.bead(STRETCH, self.t_key).click()),
            check=both_ticked_today,
        )

    def tick_yesterday(self):
        def yesterday_ticked(s):
            return (
                streak_of(s, READ) == ("2 days", "Best 2")
                and cell_of(s, self.y_key) == (f"{self.y_short}, 1 of 2 habits", ["hc", "l2"])
            )

        self.gate.step(
            "05-ticked-yesterday", "click Y's bead of Read", gesture="click Y bead",
            expected="2 days and Best 2, Y's cell at level 2",
            do=lambda: self.bead(READ, self.y_key).click(), check=yesterday_ticked,
        )

    def reload_keeps_everything(self):
        rows_before_reload = self.page.evaluate(SNAPSHOT_JS)["rows"]
        self.gate.step(
            "06-reloaded", "reload", gesture="page.reload()",
            expected="both rows, their beads and streak lines unchanged",
            do=self.page.reload, check=lambda s: s["rows"] == rows_before_reload,
        )

    def ask_to_delete(self):
        self.gate.step(
            "07-dialog", "click Delete Stretch 10 minutes", gesture="click the trash button",
            expected="the dialog asks, Cancel has focus",
            do=self.trash(STRETCH).click,
            check=lambda s: s["dialogOpen"] and s["dialogTitle"] == f'Delete "{STRETCH}"?' and s["active"]["text"] == "Cancel",
        )

    def cancel_the_delete(self):
        self.gate.step(
            "08-cancelled", "click Cancel", gesture="click Cancel",
            expected="2 rows remain, focus on the trash button",
            do=self.page.get_by_role("button", name="Cancel", exact=True).click,
            check=lambda s: not s["dialogOpen"] and len(s["rows"]) == 2 and s["active"]["label"] == f"Delete {STRETCH}",
        )

    def delete_a_habit(self):
        self.gate.step(
            "09-deleted", "click the trash button, then Delete habit", gesture="click the trash button; click Delete habit",
            expected="1 row, focus on the field, T's cell counts 1 habit",
            do=lambda: (self.trash(STRETCH).click(), self.page.get_by_role("button", name="Delete habit", exact=True).click()),
            check=lambda s: (
                len(s["rows"]) == 1 and s["active"]["id"] == "new-habit"
                and cell_of(s, self.t_key) == (f"{self.t_short}, 1 of 1 habits", ["hc", "l4", "today"])
            ),
        )

    def add_a_duplicate(self):
        self.gate.step(
            "10-duplicate", "type a duplicate name, press Enter", gesture="click #new-habit; keyboard.type; Enter",
            expected="the duplicate message shows and the text stays",
            do=lambda: self.type_name_and_press_enter("read 20 pages"),
            check=lambda s: s["message"] == "You already track this habit." and s["field"] == "read 20 pages",
        )

    def reload_keeps_one_habit(self):
        self.gate.step(
            "11-reloaded-again", "reload", gesture="page.reload()", expected="exactly one row, 2 days and Best 2",
            do=self.page.reload, check=lambda s: len(s["rows"]) == 1 and streak_of(s, READ) == ("2 days", "Best 2"),
        )


def run(base_url, out):
    out.mkdir(parents=True, exist_ok=True)
    requests, console, errors = [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="light")
        context.set_default_timeout(STEP_TIMEOUT_SECONDS * 1000)
        page = context.new_page()
        page.goto("about:blank")
        start = datetime.date(*page.evaluate(LOCAL_DATE_JS))
        page.on("request", lambda r: requests.append({"method": r.method, "url": r.url}))
        page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: errors.append(str(e)))

        gate = Gate(page, out)
        Scenario(page, gate, base_url, start.isoformat(), (start - datetime.timedelta(days=1)).isoformat()).run()

        end = datetime.date(*page.evaluate(LOCAL_DATE_JS))
        browser_version = browser.version
        context.close()
        browser.close()

    parts = urlsplit(base_url)
    allowed = {"/", "/index.html", "/favicon.ico", "/src/styles.css"} | {f"/src/{p.name}" for p in (ROOT / "src").glob("*.js")}
    outside = [r for r in requests if not request_is_allowed(r, f"{parts.scheme}://{parts.netloc}", allowed)]
    console_errors = [m for m in console if m["type"] == "error"]
    passed = all(s["pass"] for s in gate.steps) and not outside and not console_errors and not errors and end == start

    def save(name, data):
        (out / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

    save("steps.json", gate.steps)
    save("console.json", {"console": console, "page_errors": errors})
    save("network.json", {"requests": requests, "outside_the_rule": outside})
    save("summary.json", {
        "base_url": base_url, "start_date": start.isoformat(), "end_date": end.isoformat(), "browser": f"Chromium {browser_version}",
        "steps": len(gate.steps), "steps_passed": sum(s["pass"] for s in gate.steps),
        "requests": len(requests), "requests_outside_the_rule": len(outside),
        "console_errors": len(console_errors), "page_errors": len(errors),
        "pass": passed, "void_if_the_date_changed": end != start,
    })
    print("GATE " + ("PASS" if passed else "FAIL"), "->", out)
    return 0 if passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True, help="a folder inside the project, normally docs/modules/app/qa/live-e2e/<datetimestamp>/")
    arguments = parser.parse_args()
    destination = (ROOT / arguments.out).resolve()
    if ROOT not in destination.parents:
        sys.exit(f"--out must be inside the project: {destination}")
    sys.exit(run(arguments.base_url, destination))
