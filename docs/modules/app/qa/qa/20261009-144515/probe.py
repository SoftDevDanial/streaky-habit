"""QA finder cross-check probe for the Streaks app (module app).

Independent of tests/browser/conftest.py: its own helpers, its own oracle (a Python model of the
habit-logic rules written from docs/modules/habit-logic/spec.md), real gestures only (click, keyboard,
mouse), time only through Playwright's clock. Read-only on the project; writes only into its own folder.

Usage: python probe.py <base_url_with_trailing_slash>
Output: results.json and shots/*.png next to this file.
"""
import datetime
import json
import pathlib
import random
import re
import sys
import traceback

from playwright.sync_api import expect, sync_playwright

BASE = sys.argv[1]
OUT = pathlib.Path(__file__).resolve().parent
SHOTS = OUT / "shots"
SHOTS.mkdir(exist_ok=True)
ROOT = OUT.parents[5]  # .../streaks
KL = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"

WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WDL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MOL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
       "November", "December"]


def short(d):
    return f"{WD[d.weekday()]} {d.day} {MO[d.month - 1]}"


def longd(d):
    return f"{WDL[d.weekday()]} {d.day} {MOL[d.month - 1]}"


def D(text):
    return datetime.date.fromisoformat(text)


def add_days(d, n):
    return d + datetime.timedelta(days=n)


# ------------------------------------------------------------------ results
RESULTS = []


def rec(pid, req, what, ok, observed=""):
    RESULTS.append({"id": pid, "r": req, "what": what, "verdict": "PASS" if ok else "FAIL", "observed": str(observed)[:700]})
    line = ("PASS " if ok else "FAIL ") + pid + " [" + req + "] " + what
    if not ok:
        line += " :: " + str(observed)[:400]
    print(line, flush=True)


def err(pid, req, what, exc):
    RESULTS.append({"id": pid, "r": req, "what": what, "verdict": "ERROR", "observed": traceback.format_exc()[-900:]})
    print("ERROR " + pid + " [" + req + "] " + what + " :: " + repr(exc)[:300], flush=True)


# ------------------------------------------------------------------ oracle (habit-logic spec)
def heat_level(count, total):
    if count == 0 or total == 0:
        return 0
    if count == total:
        return 4
    if 3 * count <= total:
        return 1
    if 3 * count <= 2 * total:
        return 2
    return 3


def current_streak(done, today):
    start = today if today in done else add_days(today, -1)
    n = 0
    d = start
    while d in done:
        n += 1
        d = add_days(d, -1)
    return n


def best_streak(done):
    best = 0
    for d in done:
        if add_days(d, -1) in done:
            continue
        n = 0
        e = d
        while e in done:
            n += 1
            e = add_days(e, 1)
        best = max(best, n)
    return best


class Model:
    def __init__(self, today):
        self.today = today
        self.habits = []  # [name, set(date)]

    def window(self):
        return [add_days(self.today, i - 6) for i in range(7)]

    def grid(self):
        monday = add_days(self.today, -self.today.weekday())
        first = add_days(monday, -77)
        return [add_days(first, i) for i in range(84)]

    def stored(self):
        return json.dumps({"version": 1, "habits": [{"name": n, "done": sorted(x.isoformat() for x in s)} for n, s in self.habits]},
                          separators=(",", ":"), ensure_ascii=False)

    def expected_rows(self):
        rows = []
        for i, (name, done) in enumerate(self.habits):
            cur = current_streak(done, self.today)
            best = best_streak(done)
            win = self.window()
            rows.append({
                "id": f"h{i + 1}-name", "name": name, "trash": f"Delete {name}",
                "cur": "No streak yet" if cur == 0 else ("1 day" if cur == 1 else f"{cur} days"),
                "curClass": "cur none" if cur == 0 else "cur",
                "best": None if best == 0 else f"Best {best}",
                "run": (add_days(self.today, -6) in done and add_days(self.today, -7) in done),
                "labelledby": f"h{i + 1}-name",
                "days": [[d.isoformat(), "true" if d in done else "false", f"Mark {short(d)} as done",
                          "date" if d == self.today else None] for d in win],
            })
        return rows

    def expected_cells(self):
        total = len(self.habits)
        out = []
        for d in self.grid():
            if d > self.today:
                out.append(["hc future", d.isoformat(), None, "true", None, None])
                continue
            count = sum(1 for _, s in self.habits if d in s)
            cls = f"hc l{heat_level(count, total)}" + (" today" if d == self.today else "")
            out.append([cls, d.isoformat(), "img", None, f"{short(d)}, {count} of {total} habits",
                        "date" if d == self.today else None])
        return out

    def expected_months(self):
        # habit-logic R12: column 1 is labelled with its Monday's month; a later column is labelled when its
        # Monday is in a different month from the previous column's Monday.
        g = self.grid()
        cols = []
        prev = None
        for idx in range(0, 84, 7):
            monday = g[idx]
            if prev is None or monday.month != prev:
                cols.append((MO[monday.month - 1], idx // 7 + 1))
            prev = monday.month
        return cols


SNAP_JS = """() => {
  const q = (s, r = document) => r.querySelector(s);
  const time = q('p.date time');
  const input = q('#new-habit');
  const msg = q('#new-habit-msg');
  return {
    date: [time.getAttribute('datetime'), time.textContent],
    brand: q('h1.brand').textContent,
    empty: q('p.empty') ? q('p.empty').textContent : null,
    hasList: !!q('ul.habits'),
    note: q('.col-main > .note') ? q('.col-main > .note').textContent : null,
    rows: Array.from(document.querySelectorAll('ul.habits > li.habit')).map((li) => {
      const cur = li.querySelector('.cur');
      const best = li.querySelector('.best');
      return {
        id: li.querySelector('h3.habit-name').id, name: li.querySelector('h3.habit-name').textContent,
        trash: li.querySelector('.habit-head .icon-btn').getAttribute('aria-label'),
        cur: cur.textContent, curClass: cur.className, best: best ? best.textContent : null,
        run: li.querySelector('.strip').hasAttribute('data-run-continues'),
        labelledby: li.querySelector('.strip').getAttribute('aria-labelledby'),
        days: Array.from(li.querySelectorAll('button.day')).map((b) => [b.getAttribute('data-date'),
          b.getAttribute('aria-pressed'), b.getAttribute('aria-label'), b.getAttribute('aria-current')]),
      };
    }),
    cells: Array.from(document.querySelectorAll('.cells > span')).map((e) => [e.className, e.getAttribute('data-date'),
      e.getAttribute('role'), e.getAttribute('aria-hidden'), e.getAttribute('aria-label'), e.getAttribute('aria-current')]),
    months: Array.from(document.querySelectorAll('.months > span')).map((e) => [e.textContent, e.style.gridColumn]),
    stored: localStorage.getItem('streaks.state'),
    input: { disabled: input.disabled, value: input.value, invalid: input.getAttribute('aria-invalid'),
             describedby: input.getAttribute('aria-describedby') },
    addDisabled: q('.add .btn').disabled,
    msg: [msg.textContent, msg.className],
    dialogOpen: q('dialog.dialog').open,
    active: document.activeElement ? (document.activeElement.getAttribute('aria-label') || document.activeElement.id ||
      document.activeElement.textContent.trim().slice(0, 30) || document.activeElement.tagName) : null,
    activeTag: document.activeElement ? document.activeElement.tagName : null,
  };
}"""


def diff_model(snap, model):
    problems = []
    if snap["date"] != [model.today.isoformat(), longd(model.today)]:
        problems.append(f"date {snap['date']} vs {model.today.isoformat()} {longd(model.today)}")
    if snap["brand"] != "Streaks":
        problems.append("brand")
    if model.habits:
        if snap["empty"] is not None or not snap["hasList"]:
            problems.append("list/empty state wrong with habits")
    else:
        if snap["empty"] != "No habits yet. Add one you want to do every day." or snap["hasList"]:
            problems.append(f"empty state wrong: {snap['empty']!r} hasList={snap['hasList']}")
    exp = model.expected_rows()
    if len(snap["rows"]) != len(exp):
        problems.append(f"row count {len(snap['rows'])} vs {len(exp)}")
    else:
        for i, (a, b) in enumerate(zip(snap["rows"], exp)):
            for k in b:
                if a[k] != b[k]:
                    problems.append(f"row {i} {k}: {a[k]!r} vs {b[k]!r}")
    cells = model.expected_cells()
    if snap["cells"] != cells:
        bad = [(x, y) for x, y in zip(snap["cells"], cells) if x != y][:3]
        problems.append(f"cells differ ({len(snap['cells'])} vs {len(cells)}): {bad}")
    months = [[m, str(c)] for m, c in model.expected_months()]
    if snap["months"] != months:
        problems.append(f"months {snap['months']} vs {months}")
    if snap["stored"] is not None and snap["stored"] != model.stored():
        problems.append(f"stored {snap['stored']!r} vs {model.stored()!r}")
    full = len(model.habits) >= 12
    if snap["input"]["disabled"] != full or snap["addDisabled"] != full:
        problems.append(f"disabled state {snap['input']['disabled']}/{snap['addDisabled']} for {len(model.habits)} habits")
    return problems


# ------------------------------------------------------------------ session
COUNTER = ("(() => { const o = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) {"
           " console.log('__SET__' + v); return o.call(this, k, v); }; })();")


class Sess:
    def __init__(self, browser, viewport=(390, 844), tz=KL, locale="en-US", reduced="no-preference", fixed=NOON,
                 install=None, storage=None, init=None, counter=True, path="", base=None):
        base = base or BASE
        self.ctx = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1,
                                       color_scheme="light", timezone_id=tz, locale=locale, reduced_motion=reduced)
        self.ctx.set_default_timeout(5000)
        self.ctx.set_default_navigation_timeout(10000)
        if install:
            self.ctx.clock.install(time=install)
        elif fixed:
            self.ctx.clock.set_fixed_time(fixed)
        self.page = self.ctx.new_page()
        if storage is not None:
            self.page.goto(base + "__seed__")
            self.page.evaluate("(t) => localStorage.setItem('streaks.state', t)", storage)
        if counter:
            self.ctx.add_init_script(COUNTER)
        if init:
            self.ctx.add_init_script(init)
        self.console = []
        self.errors = []
        self.requests = []
        self.dialogs = []
        self.page.on("console", lambda m: self.console.append((m.type, m.text)))
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("request", lambda r: self.requests.append((r.method, r.url)))
        self.page.on("dialog", lambda d: (self.dialogs.append(d.message), d.dismiss()))
        self.page.goto(base + path)

    def writes(self):
        return [t[len("__SET__"):] for _, t in self.console if t.startswith("__SET__")]

    def console_errors(self):
        return [(k, t) for k, t in self.console if k == "error"]

    def snap(self):
        return self.page.evaluate(SNAP_JS)

    def shot(self, name):
        self.page.screenshot(path=str(SHOTS / (name + ".png")), full_page=True)

    def close(self):
        try:
            self.ctx.close()
        except Exception:
            pass

    # gestures
    def type_name(self, text):
        self.page.locator("#new-habit").click()
        self.page.keyboard.type(text)

    def add(self, text, enter=False):
        self.type_name(text)
        if enter:
            self.page.keyboard.press("Enter")
        else:
            self.page.get_by_role("button", name="Add", exact=True).click()

    def rows(self):
        return self.page.locator("li.habit")

    def names(self):
        return self.page.locator("h3.habit-name").all_inner_texts()

    def trash(self, name):
        return self.page.get_by_role("button", name=f"Delete {name}", exact=True)

    def day(self, idx, date):
        return self.rows().nth(idx).locator(f'button.day[data-date="{date}"]')

    def dialog(self):
        return self.page.locator("dialog.dialog")

    def open_delete(self, name):
        self.trash(name).click()
        expect(self.dialog()).to_have_attribute("open", "")

    def closed(self):
        """Wait (bounded) until the dialog is closed, then let the queued close event run."""
        expect(self.dialog()).not_to_have_attribute("open", "")
        self.page.wait_for_timeout(60)

    def confirm_delete(self):
        self.page.get_by_role("button", name="Delete habit", exact=True).click()
        self.closed()

    def active_label(self):
        return self.page.evaluate("() => document.activeElement && (document.activeElement.getAttribute('aria-label')"
                                  " || document.activeElement.id || document.activeElement.textContent.trim())")


def seed_text(habits):
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"))


SAMPLE = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))["habits"]


def sample_model(today="2026-10-08"):
    m = Model(D(today))
    for h in SAMPLE:
        m.habits.append([h["name"], {D(x) for x in h["done"]}])
    return m


# ================================================================== FLOWS
def flow_first_visit(browser):
    S = Sess(browser)
    try:
        s = S.snap()
        S.shot("F1-first-visit-390")
        m = Model(D("2026-10-08"))
        probs = diff_model(s, m)
        rec("F1.model", "R3", "first visit equals the empty model (date, empty message, 84 cells, months)", not probs, probs)
        rec("F1.nowrite", "R3/R16", "no storage key and no write on first visit", s["stored"] is None and S.writes() == [], (s["stored"], S.writes()))
        rec("F1.form", "R3", "input enabled, empty, no aria-invalid; message empty with field-msg field-error; no note",
            s["input"] == {"disabled": False, "value": "", "invalid": None, "describedby": "new-habit-msg"} and s["msg"] == ["", "field-msg field-error"] and s["note"] is None, s["input"])
        rec("F1.clean", "R25", "no console error, no page error, requests same-origin GET only",
            S.console_errors() == [] and S.errors == [] and all(me == "GET" and u.startswith(BASE) for me, u in S.requests), (S.console_errors(), S.errors, S.requests))
        S.page.keyboard.press("Tab")
        a1 = S.active_label()
        S.page.keyboard.press("Tab")
        a2 = S.active_label()
        rec("F1.tab", "R22", "fresh page: Tab visits input then Add", (a1, a2) == ("new-habit", "Add"), (a1, a2))
    except Exception as e:
        err("F1", "R3", "first visit", e)
    finally:
        S.close()


def flow_add_tick_reload(browser):
    S = Sess(browser)
    try:
        m = Model(D("2026-10-08"))
        t = D("2026-10-08")
        y = D("2026-10-07")
        S.add("Read 20 pages")
        m.habits.append(["Read 20 pages", set()])
        s = S.snap()
        rec("F2.add1", "R10", "add by clicking Add: model equal, field cleared, no message", not diff_model(s, m) and s["input"]["value"] == "" and s["msg"][0] == "", diff_model(s, m))
        rec("F2.add1.focus", "R10", "app does not move focus after a successful add by click (focus stays on Add button)", s["active"] == "Add", s["active"])
        rec("F2.add1.write", "R16", "exactly one save, exact compact text", S.writes() == ['{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'], S.writes())
        S.add("Stretch 10 minutes", enter=True)
        m.habits.append(["Stretch 10 minutes", set()])
        s = S.snap()
        rec("F2.add2", "R10", "add by Enter: bottom, model equal, focus stays in the input", not diff_model(s, m) and s["active"] == "new-habit", (diff_model(s, m), s["active"]))
        # in place: handle to today's heat cell before the tick is the same element after
        cell_handle = S.page.locator('.cells .hc[data-date="2026-10-08"]').element_handle()
        S.day(0, t).click(); m.habits[0][1].add(t)
        rec("F2.cell-inplace", "R8", "the heatmap cell for the date is updated in place (same element, still connected)",
            cell_handle.evaluate("(e) => e.isConnected && e.getAttribute('aria-label')") == "Thu 8 Oct, 1 of 2 habits", "")
        S.day(1, t).click(); m.habits[1][1].add(t)
        S.day(0, y).click(); m.habits[0][1].add(y)
        s = S.snap()
        probs = diff_model(s, m)
        rec("F2.tick", "R8", "tick today and yesterday: streaks, strips, heat cells equal the model", not probs, probs)
        rec("F2.tick.vals", "R8", "Read shows '2 days'/'Best 2'; Stretch '1 day'/'Best 1'; today cell l4 '2 of 2'; yesterday cell l2 '1 of 2'",
            s["rows"][0]["cur"] == "2 days" and s["rows"][0]["best"] == "Best 2" and s["rows"][1]["cur"] == "1 day" and s["rows"][1]["best"] == "Best 1"
            and any(c[1] == "2026-10-08" and c[0] == "hc l4 today" and c[4] == "Thu 8 Oct, 2 of 2 habits" for c in s["cells"])
            and any(c[1] == "2026-10-07" and c[0] == "hc l2" and c[4] == "Wed 7 Oct, 1 of 2 habits" for c in s["cells"]),
            (s["rows"][0]["cur"], s["rows"][0]["best"]))
        rec("F2.tick.focus", "R8", "focus stays on the ticked button", s["active"] == "Mark Wed 7 Oct as done", s["active"])
        rec("F2.writes", "R16", "one save per change (2 adds + 3 ticks = 5 writes)", len(S.writes()) == 5, len(S.writes()))
        S.shot("F2-ticked-390")
        before = S.snap()["stored"]
        n = len(S.writes())
        S.page.reload()
        s2 = S.snap()
        rec("F2.reload", "R16", "reload shows the same state (model equal) and stored text unchanged", not diff_model(s2, m) and s2["stored"] == before, diff_model(s2, m))
        rec("F2.reload.nowrite", "R16", "reload performs no write", len(S.writes()) == n, len(S.writes()) - n)
        S.page.close()
        p2 = S.ctx.new_page()
        p2.goto(BASE)
        s3 = p2.evaluate(SNAP_JS)
        rec("F2.newtab", "R16", "closing the tab and opening again shows the same state", not diff_model(s3, m), diff_model(s3, m))
        p2.close()
    except Exception as e:
        err("F2", "R8/R10/R16", "add, tick, reload", e)
    finally:
        S.close()


def flow_delete(browser):
    S = Sess(browser, storage=seed_text(SAMPLE))
    try:
        m = sample_model()
        rec("F3.boot", "R5-R9", "sample day equals the model", not diff_model(S.snap(), m), diff_model(S.snap(), m))
        base_writes = len(S.writes())
        S.open_delete("Stretch 10 minutes")
        d = S.snap()
        rec("F3.open", "R13", "dialog open, title/body, Cancel focused",
            d["dialogOpen"] and S.page.locator("#del-title").text_content() == 'Delete "Stretch 10 minutes"?' and d["active"] == "Cancel", d["active"])
        S.shot("F3-dialog-390")
        S.page.get_by_role("button", name="Cancel", exact=True).click()
        S.closed()
        s = S.snap()
        rec("F3.cancel", "R14", "Cancel keeps all, focus on same trash, no save", not diff_model(s, m) and s["active"] == "Delete Stretch 10 minutes" and len(S.writes()) == base_writes, (s["active"], len(S.writes())))
        S.open_delete("Stretch 10 minutes")
        S.page.keyboard.press("Escape")
        S.closed()
        s = S.snap()
        rec("F3.esc", "R14", "Esc keeps all, focus on same trash, no save", not diff_model(s, m) and s["active"] == "Delete Stretch 10 minutes" and len(S.writes()) == base_writes, (s["active"], len(S.writes())))
        S.open_delete("Stretch 10 minutes")
        S.page.mouse.click(5, 5)
        S.closed()
        s = S.snap()
        rec("F3.backdrop", "R14", "backdrop click keeps all, focus on same trash, no save", not diff_model(s, m) and s["active"] == "Delete Stretch 10 minutes" and len(S.writes()) == base_writes, (s["active"], len(S.writes())))
        S.open_delete("Read 20 pages")
        box = S.dialog().bounding_box()
        S.page.mouse.click(box["x"] + box["width"] + 3, box["y"] + box["height"] + 3)
        S.closed()
        rec("F3.backdrop2", "R14", "click 3px outside the box corner closes as Cancel", S.snap()["active"] == "Delete Read 20 pages" and len(S.writes()) == base_writes, S.snap()["active"])
        S.open_delete("Read 20 pages")
        S.page.locator("#del-title").click()
        S.page.locator("#del-body").click()
        rec("F3.inside", "R14", "clicks on title and body keep the dialog open", S.snap()["dialogOpen"], "")
        S.page.keyboard.press("Escape")
        S.closed()
        # open for A, cancel, open for B, delete B: B removed (not A)
        S.open_delete("Read 20 pages")
        S.page.get_by_role("button", name="Cancel", exact=True).click()
        S.closed()
        S.open_delete("Stretch 10 minutes")
        S.confirm_delete()
        m.habits.pop(1)
        s = S.snap()
        rec("F3.confirm-middle", "R15", "open A, Cancel, open B, delete: B removed; model equal (ids renumbered, heatmap recounted), one save",
            not diff_model(s, m) and len(S.writes()) == base_writes + 1, (diff_model(s, m), len(S.writes()) - base_writes))
        rec("F3.confirm-focus", "R15", "focus on the trash of the habit that was below ('Delete No phone after 11pm')", s["active"] == "Delete No phone after 11pm", s["active"])
        S.open_delete("No phone after 11pm")
        S.confirm_delete()
        m.habits.pop(1)
        s = S.snap()
        rec("F3.confirm-last", "R15", "delete the bottom habit: focus on the New habit input", not diff_model(s, m) and s["active"] == "new-habit", (diff_model(s, m), s["active"]))
        S.open_delete("Read 20 pages")
        S.confirm_delete()
        m.habits.pop(0)
        s = S.snap()
        rec("F3.confirm-only", "R15", "delete the only habit: empty message, stored empty state, focus on input",
            not diff_model(s, m) and s["stored"] == '{"version":1,"habits":[]}' and s["active"] == "new-habit", (diff_model(s, m), s["stored"], s["active"]))
        S.add("Stretch 10 minutes")
        m.habits.append(["Stretch 10 minutes", set()])
        s = S.snap()
        rec("F3.readd", "R15", "re-adding a deleted name starts with no history", not diff_model(s, m) and s["rows"][0]["cur"] == "No streak yet" and s["rows"][0]["best"] is None, diff_model(s, m))
        rec("F3.clean", "R25", "no console error and no page error across the delete flows", S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
    except Exception as e:
        err("F3", "R13-R15", "delete flows", e)
    finally:
        S.close()


def flow_stray_enter_keyboard(browser):
    S = Sess(browser)
    try:
        pg = S.page
        pg.keyboard.press("Tab")
        pg.keyboard.type("Walk dog")
        pg.keyboard.press("Enter")
        s = S.snap()
        rec("F4.add", "R10/R22", "keyboard-only add: Tab, type, Enter", bool(s["rows"]) and s["rows"][0]["name"] == "Walk dog" and s["active"] == "new-habit", s["active"])
        pg.keyboard.press("Shift+Tab")
        rec("F4.back", "R22", "Shift+Tab from the input reaches today's bead", S.active_label() == "Mark Thu 8 Oct as done", S.active_label())
        S.shot("F4-focus-ring-390")
        pg.keyboard.press("Space")
        s = S.snap()
        rec("F4.space", "R8", "Space ticks today, focus kept", s["rows"][0]["days"][6][1] == "true" and s["rows"][0]["cur"] == "1 day" and s["active"] == "Mark Thu 8 Oct as done", (s["rows"][0]["cur"], s["active"]))
        pg.keyboard.press("Shift+Tab")
        pg.keyboard.press("Enter")
        s = S.snap()
        rec("F4.enter", "R8", "Enter ticks yesterday, streak 2 days Best 2", s["rows"][0]["cur"] == "2 days" and s["rows"][0]["best"] == "Best 2" and s["active"] == "Mark Wed 7 Oct as done", (s["rows"][0]["cur"], s["active"]))
        for _ in range(6):
            pg.keyboard.press("Shift+Tab")
        rec("F4.trash", "R22", "six more Shift+Tab reach the trash button", S.active_label() == "Delete Walk dog", S.active_label())
        pg.keyboard.press("Enter")
        s = S.snap()
        rec("F4.dialog", "R13", "Enter on trash opens the dialog with Cancel focused", s["dialogOpen"] and s["active"] == "Cancel", s["active"])
        pg.keyboard.press("Enter")
        S.closed()
        s = S.snap()
        rec("F4.stray", "R14/T7", "a stray Enter on Cancel keeps the habit and returns focus to the trash", len(s["rows"]) == 1 and s["active"] == "Delete Walk dog", (len(s["rows"]), s["active"]))
        pg.keyboard.press("Enter")
        expect(S.dialog()).to_have_attribute("open", "")
        inside = []
        reached = False
        for _ in range(6):
            pg.keyboard.press("Tab")
            inside.append(pg.evaluate("() => !document.querySelector('.page').contains(document.activeElement)"))
            if S.active_label() == "Delete habit":
                reached = True
                break
        rec("F4.tab-dialog", "R13/R22", "Tab inside the dialog reaches 'Delete habit' and never lands on the page behind", reached and all(inside), (reached, inside))
        pg.keyboard.press("Tab")
        pg.keyboard.press("Tab")
        pg.keyboard.press("Tab")
        rec("F4.tab-wrap", "R13", "further Tab presses still never reach the page behind", pg.evaluate("() => !document.querySelector('.page').contains(document.activeElement)"), S.active_label())
        for _ in range(4):
            if S.active_label() == "Delete habit":
                break
            pg.keyboard.press("Tab")
        pg.keyboard.press("Enter")
        S.closed()
        s = S.snap()
        rec("F4.delete", "R15", "keyboard delete: gone, focus on input, empty message, empty state saved", s["rows"] == [] and s["active"] == "new-habit" and s["stored"] == '{"version":1,"habits":[]}', (s["active"], s["stored"]))
        rec("F4.clean", "R25", "no console or page errors", S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
    except Exception as e:
        err("F4", "R22", "keyboard-only flow", e)
    finally:
        S.close()


def flow_name_errors(browser):
    S = Sess(browser, storage=seed_text(SAMPLE))
    try:
        base = len(S.writes())
        cases = [("", "Name the habit first."), ("   ", "Name the habit first."),
                 ("Walk to the end of the street and back after dinner", "Keep it to 40 characters or fewer."),
                 ("X" * 41, "Keep it to 40 characters or fewer."),
                 ("read 20 pages", "You already track this habit."), (" STRETCH 10 MINUTES ", "You already track this habit."),
                 ("NO PHONE AFTER 11PM", "You already track this habit.")]
        ok = True
        details = []
        for typed, message in cases:
            S.page.locator("#new-habit").fill(typed)
            S.page.get_by_role("button", name="Add", exact=True).click()
            s = S.snap()
            good = (s["msg"] == [message, "field-msg field-error"] and s["input"]["invalid"] == "true" and s["input"]["value"] == typed
                    and s["active"] == "new-habit" and len(s["rows"]) == 3)
            if not good:
                ok = False
                details.append((typed, s["msg"], s["input"], s["active"]))
        rec("F5.errors", "R11", "7 rejected names: one message, red classes, aria-invalid, text kept untrimmed, focus in the input, 3 rows", ok, details)
        rec("F5.nowrite", "R11/R16", "rejected names write nothing", len(S.writes()) == base, len(S.writes()) - base)
        S.shot("F5-error-390")
        S.page.locator("#new-habit").fill("")
        S.page.keyboard.press("Enter")
        s = S.snap()
        rec("F5.enter-empty", "R11", "Enter in the empty field shows the empty message", s["msg"][0] == "Name the habit first." and s["input"]["invalid"] == "true", s["msg"])
        S.page.locator("#new-habit").fill("Drink water")
        s = S.snap()
        rec("F5.typing", "R11", "typing a valid name does not clear the message until submit", s["msg"][0] == "Name the habit first.", s["msg"])
        S.page.keyboard.press("Enter")
        s = S.snap()
        rec("F5.success", "R11/R10", "success clears message and aria-invalid, adds row", s["msg"] == ["", "field-msg field-error"] and s["input"]["invalid"] is None and len(s["rows"]) == 4, (s["msg"], s["input"]))
        S.add("a" * 40)
        s = S.snap()
        rec("F5.40", "R11", "40 characters accepted", len(s["rows"]) == 5, len(s["rows"]))
        rec("F5.clean", "R25", "no console or page errors", S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
    except Exception as e:
        err("F5", "R11", "name errors", e)
    finally:
        S.close()


def flow_unreadable(browser):
    variants = ["{", "null", "[]", '{"version":2,"habits":[]}', '{"version":1,"habits":[{"name":" Read","done":[]}]}',
                '{"version":1,"habits":[{"name":"Read","done":["2026-02-30"]}]}',
                '{"version":1,"habits":[{"name":"Read","done":"x"}]}', "\u0000",
                '{"version":1,"habits":[{"name":"Read","done":[]},{"name":"READ","done":[]}]}',
                '"just a string"', "42", '{"version":1}', '{"habits":[]}', "", "true"]
    allok = True
    bad = []
    for raw in variants:
        S = Sess(browser, storage=raw)
        try:
            s = S.snap()
            good = (s["note"] == "Your saved habits could not be read, so the list was reset." and s["empty"] is not None
                    and s["stored"] == '{"version":1,"habits":[]}' and len(S.writes()) == 1 and S.console_errors() == [] and S.errors == [])
            if not good:
                allok = False
                bad.append((raw, s["note"], s["stored"], len(S.writes()), S.console_errors(), S.errors))
        except Exception as e:
            allok = False
            bad.append((raw, repr(e)))
        finally:
            S.close()
    rec("F6.variants", "R17", f"{len(variants)} unreadable variants (incl. empty string, NUL, bare true): note shown, empty state saved with exactly one write, no errors", allok, bad)
    S = Sess(browser, storage="{")
    try:
        S.shot("F6-note-390")
        S.page.get_by_role("button", name="Dismiss note", exact=True).click()
        s = S.snap()
        rec("F6.dismiss", "R17", "Dismiss: note gone, empty message stays, focus on the input, no extra write", s["note"] is None and bool(s["empty"]) and s["active"] == "new-habit" and len(S.writes()) == 1, (s["active"], len(S.writes())))
        S.page.reload()
        s = S.snap()
        rec("F6.reload", "R17", "after reload no note and no new write", s["note"] is None and len(S.writes()) == 1, len(S.writes()))
    except Exception as e:
        err("F6b", "R17", "dismiss", e)
    finally:
        S.close()
    S = Sess(browser, storage="{", viewport=(1280, 800))
    try:
        S.shot("F6-note-1280")
        S.add("After reset")
        s = S.snap()
        rec("F6.add-after", "R17", "adding after a reset works; note stays until dismissed", len(s["rows"]) == 1 and s["note"] is not None, (len(s["rows"]), s["note"]))
    except Exception as e:
        err("F6c", "R17", "add after reset", e)
    finally:
        S.close()


def overflow_check(S, label, limit=360):
    sw = S.page.evaluate("() => document.documentElement.scrollWidth")
    culprits = S.page.evaluate("""(limit) => Array.from(document.querySelectorAll('body *')).filter((e) => {
        if (e.closest('svg') && !e.matches('svg')) return false;
        if (e.closest('.sr-only')) return false;
        const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > limit + 0.5 || r.left < -0.5);
      }).slice(0, 5).map((e) => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().left) + '..' + Math.round(e.getBoundingClientRect().right))""", limit)
    rec(f"F7.{label}", "R21", f"{limit}px wide: no horizontal scroll and nothing past the right edge: {label}", sw <= limit and culprits == [], (sw, culprits))


def flow_width_360(browser):
    long_a = "W" * 40
    long_b = "M" * 39 + "x"
    habits = [{"name": long_a, "done": []}, {"name": long_b, "done": ["2026-10-08"]}] + [{"name": f"Habit {n}", "done": []} for n in range(3, 13)]
    S = Sess(browser, viewport=(360, 780), storage=seed_text(habits))
    try:
        overflow_check(S, "12 habits with 40-char unbroken names (12-note visible)")
        S.shot("F7-12habits-360")
        S.open_delete(long_a)
        overflow_check(S, "delete dialog with a 40-char unbroken name")
        S.shot("F7-dialog-long-360")
        box = S.dialog().bounding_box()
        rec("F7.dialog-box", "R13", "dialog box stays inside the viewport at 360", box["x"] >= 0 and box["x"] + box["width"] <= 360, box)
        S.page.keyboard.press("Escape")
        S.closed()
        rows = S.page.evaluate("() => Array.from(document.querySelectorAll('button.day')).map((b) => Math.round(b.getBoundingClientRect().width * 10) / 10)")
        rec("F7.day-width", "R21", "every day button >= 44px wide at 360 with 12 habits", min(rows) >= 44, min(rows))
        msg = S.page.locator("#new-habit-msg").bounding_box()
        rec("F7.note-wrap", "R12", "12-habit note wraps inside the form at 360", msg["x"] + msg["width"] <= 360 and msg["height"] >= 40, msg)
    except Exception as e:
        err("F7", "R21", "12 habits at 360", e)
    finally:
        S.close()
    S = Sess(browser, viewport=(360, 780), storage="{")
    try:
        overflow_check(S, "unreadable-data note")
        S.shot("F7-note-360")
        ib = S.page.locator("button.icon-btn").bounding_box()
        rec("F7.dismiss-44", "R21", "Dismiss button is 44x44", (ib["width"], ib["height"]) == (44, 44), ib)
        S.add("X" * 41)
        overflow_check(S, "name error message")
        S.shot("F7-error-360")
        for sel in ("#new-habit", ".add .btn"):
            h = S.page.locator(sel).bounding_box()["height"]
            rec(f"F7.h{sel}", "R21", f"{sel} is 48px tall", h == 48, h)
    except Exception as e:
        err("F7b", "R21", "note at 360", e)
    finally:
        S.close()
    S = Sess(browser, viewport=(360, 780), storage=seed_text(SAMPLE))
    try:
        overflow_check(S, "sample day")
        S.shot("F7-sample-360")
    except Exception as e:
        err("F7c", "R21", "sample at 360", e)
    finally:
        S.close()
    S = Sess(browser, viewport=(320, 640), storage=seed_text(SAMPLE))
    try:
        sw = S.page.evaluate("() => document.documentElement.scrollWidth")
        rec("F7.320", "R21", "(extra, below the 360 floor) 320x640 sample day scrollWidth <= 320", sw <= 320, sw)
    except Exception as e:
        err("F7d", "R21", "320", e)
    finally:
        S.close()


def flow_desktop(browser):
    S = Sess(browser, viewport=(1280, 800), storage=seed_text(SAMPLE))
    try:
        sw = S.page.evaluate("() => document.documentElement.scrollWidth")
        col = S.page.locator("div.col-main").bounding_box()
        heat = S.page.locator("section.heat").bounding_box()
        rec("F8.layout", "R28/S1-07", "1280x800: main column x168 w500, heatmap x732 w380, no horizontal scroll", (col["x"], col["width"], heat["x"], heat["width"]) == (168, 500, 732, 380) and sw <= 1280, (col, heat, sw))
        S.shot("F8-sample-1280")
        S.open_delete("Read 20 pages")
        box = S.dialog().bounding_box()
        rec("F8.dialog", "R28/M1-03", "1280x800 dialog 400 wide at x440", (box["x"], box["width"]) == (440, 400), box)
        S.shot("F8-dialog-1280")
    except Exception as e:
        err("F8", "R28", "desktop", e)
    finally:
        S.close()


def flow_rollover_extras(browser):
    for action in ("cancel", "delete", "escape"):
        S = Sess(browser, storage=seed_text(SAMPLE), install="2026-10-08T23:59:30+08:00")
        try:
            base = len(S.writes())
            S.open_delete("Stretch 10 minutes")
            S.page.clock.run_for(90000)
            s = S.snap()
            rec(f"F9.{action}.open", "R19", "dialog stays open across the rollover with the same title", s["dialogOpen"] and S.page.locator("#del-title").text_content() == 'Delete "Stretch 10 minutes"?', s["dialogOpen"])
            rec(f"F9.{action}.nowrite", "R16/R19", "rollover itself writes nothing", len(S.writes()) == base, len(S.writes()) - base)
            m = sample_model("2026-10-09")
            if action == "cancel":
                S.page.get_by_role("button", name="Cancel", exact=True).click()
            elif action == "escape":
                S.page.keyboard.press("Escape")
            else:
                S.page.get_by_role("button", name="Delete habit", exact=True).click()
                m.habits.pop(1)
            S.closed()
            s = S.snap()
            probs = diff_model(s, m)
            if action in ("cancel", "escape"):
                rec(f"F9.{action}.focus", "R14", "after a rollover while open, focus returns to the same habit's trash and the Friday view equals the model", s["active"] == "Delete Stretch 10 minutes" and not probs, (s["active"], probs))
            else:
                rec(f"F9.{action}.focus", "R15", "delete after a rollover removes the right habit, focus on the next trash, Friday model equal", s["active"] == "Delete No phone after 11pm" and not probs, (s["active"], probs))
        except Exception as e:
            err(f"F9.{action}", "R14/R19", "rollover with dialog open", e)
        finally:
            S.close()
    S = Sess(browser, storage=seed_text(SAMPLE), install="2026-10-08T23:59:00+08:00")
    try:
        S.page.clock.pause_at("2026-10-08T23:59:30+08:00")
        S.page.clock.run_for(29900)
        rec("F9.early", "R19", "at 23:59:59.9 the view still shows Thursday", S.snap()["date"][1] == "Thursday 8 October", S.snap()["date"])
        S.page.clock.run_for(30000)
        rec("F9.late", "R19", "30 s after midnight the view shows Friday", S.snap()["date"][1] == "Friday 9 October", S.snap()["date"])
    except Exception as e:
        err("F9b", "R19", "boundary", e)
    finally:
        S.close()
    S = Sess(browser, storage=seed_text(SAMPLE), install="2026-10-08T12:00:00+08:00")
    try:
        before = S.snap()
        S.page.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
        after = S.snap()
        rec("F9.vis-same", "R20", "visibilitychange on the same day changes nothing", before == after, "")
    except Exception as e:
        err("F9c", "R20", "visibility", e)
    finally:
        S.close()
    S = Sess(browser, storage=seed_text(SAMPLE), install="2026-10-08T23:59:30+08:00")
    try:
        S.page.clock.run_for(90000)
        m = sample_model("2026-10-09")
        S.day(0, "2026-10-09").click()
        m.habits[0][1].add(D("2026-10-09"))
        S.add("Drink water")
        m.habits.append(["Drink water", set()])
        s = S.snap()
        probs = diff_model(s, m)
        rec("F9.after", "R19/R8", "tick and add after a rollover equal the Friday model; stored text equal", not probs, probs)
    except Exception as e:
        err("F9d", "R19", "tick after rollover", e)
    finally:
        S.close()


TZ_CASES = [
    ("America/Los_Angeles", "2026-10-08T23:30:00-07:00", "2026-10-08"),
    ("Pacific/Auckland", "2026-10-09T00:30:00+13:00", "2026-10-09"),
    ("Europe/London", "2026-10-25T01:30:00+00:00", "2026-10-25"),
    ("Europe/London", "2026-10-26T00:10:00+00:00", "2026-10-26"),
    ("Europe/London", "2026-03-29T00:30:00+00:00", "2026-03-29"),
    ("Europe/London", "2026-03-30T00:10:00+01:00", "2026-03-30"),
    ("America/Los_Angeles", "2026-11-02T00:10:00-08:00", "2026-11-02"),
    ("Pacific/Kiritimati", "2026-12-31T23:59:00+14:00", "2026-12-31"),
    (KL, "2028-02-29T00:00:00+08:00", "2028-02-29"),
    (KL, "2027-03-01T00:00:00+08:00", "2027-03-01"),
    (KL, "2026-12-31T23:59:59+08:00", "2026-12-31"),
    (KL, "2027-01-01T00:00:00+08:00", "2027-01-01"),
    (KL, "2027-01-07T12:00:00+08:00", "2027-01-07"),
    (KL, "2026-03-31T12:00:00+08:00", "2026-03-31"),
    (KL, "2026-01-01T00:00:00+08:00", "2026-01-01"),
    (KL, "2026-10-05T00:00:00+08:00", "2026-10-05"),
    (KL, "2026-10-11T23:59:00+08:00", "2026-10-11"),
]


def flow_timezones(browser):
    bad = []
    for tz, instant, local in TZ_CASES:
        today = D(local)
        m = Model(today)
        m.habits.append(["Ten days", {add_days(today, -n) for n in range(0, 10)}])
        m.habits.append(["Gap", {add_days(today, -1), add_days(today, -2), add_days(today, -5)}])
        S = Sess(browser, tz=tz, fixed=instant, storage=m.stored())
        try:
            probs = diff_model(S.snap(), m)
            if probs:
                bad.append((tz, instant, probs[:3]))
        except Exception as e:
            bad.append((tz, instant, repr(e)))
        finally:
            S.close()
    rec("F10.tz", "R4/R7/R9", f"{len(TZ_CASES)} time zone / DST / leap / year-boundary days: header, strips, streaks, 84 cells, month labels (incl. habit-logic R12 worked examples 2027-01-07 and 2026-03-31) equal the oracle", not bad, bad)


def flow_names_as_text(browser):
    S = Sess(browser)
    try:
        names = ["__proto__", "constructor", "toString", "hasOwnProperty", "<b>bold</b>", 'Say "hi"', "a&amp;b", "<script>window.x=1</script>", "' onmouseover='x", "emoji \U0001F600 ok"]
        for n in names:
            S.add(n)
        got = S.names()
        rec("F11.literal", "R24", "10 hostile/odd names render literally and in order", got == names, got)
        rec("F11.noelems", "R24", "no b/script/img element was created inside the list", S.page.evaluate("() => document.querySelectorAll('ul.habits b, ul.habits script, ul.habits img, ul.habits *[onmouseover]').length") == 0, "")
        labels = S.page.locator("li.habit .icon-btn").evaluate_all("(els) => els.map((e) => e.getAttribute('aria-label'))")
        rec("F11.labels", "R24", "trash names are 'Delete <name>'", labels == [f"Delete {n}" for n in names], labels)
        rec("F11.noxss", "R24", "no JS dialog, no page error, window.x undefined", S.dialogs == [] and S.errors == [] and S.page.evaluate("() => window.x") is None, (S.dialogs, S.errors))
        proto = S.page.evaluate("() => Object.getOwnPropertyNames(Object.prototype).sort().join(',')")
        S.page.reload()
        got2 = S.names()
        rec("F11.reload", "R24/R17", "hostile names survive a reload (readable) with no note", got2 == names and S.snap()["note"] is None, (got2, S.snap()["note"]))
        proto2 = S.page.evaluate("() => Object.getOwnPropertyNames(Object.prototype).sort().join(',')")
        rec("F11.proto", "T2", "Object.prototype has the same own properties after loading '__proto__' as a name", proto == proto2 and S.page.evaluate("() => ({}).polluted") is None, proto == proto2)
        S.open_delete('Say "hi"')
        title = S.page.locator("#del-title").text_content()
        rec("F11.title", "R13/R24", "dialog title shows quotes literally", title == 'Delete "Say "hi""?', title)
        S.page.keyboard.press("Escape")
        S.closed()
        S.open_delete("<b>bold</b>")
        title = S.page.locator("#del-title").text_content()
        rec("F11.title2", "R24", "dialog title with markup name is text", title == 'Delete "<b>bold</b>"?' and S.page.evaluate("() => document.querySelector('#del-title').children.length") == 0, title)
        S.page.keyboard.press("Escape")
        S.closed()
        S.page.locator("#new-habit").fill("TOSTRING")
        S.page.get_by_role("button", name="Add", exact=True).click()
        rec("F11.dup", "R11", "'TOSTRING' duplicates 'toString' ignoring case", S.snap()["msg"][0] == "You already track this habit.", S.snap()["msg"])
        S.shot("F11-odd-names-390")
    except Exception as e:
        err("F11", "R24", "names as text", e)
    finally:
        S.close()


def flow_storage_failures(browser):
    S = Sess(browser, init="Storage.prototype.getItem = function () { throw new DOMException('denied', 'SecurityError'); };", counter=False)
    try:
        pg = S.page
        rec("F12.getitem", "R18", "getItem throws: starts empty with no note", pg.locator("p.empty").count() == 1 and pg.locator("div.note").count() == 0, "")
        S.add("Read")
        S.day(0, "2026-10-08").click()
        line = pg.locator("p.streak").text_content()
        rec("F12.getitem.keep", "R18", "app keeps working in memory ('1 day' 'Best 1')", "1 day" in line and "Best 1" in line, line)
        rec("F12.getitem.clean", "R18", "no console error, no page error", S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
    except Exception as e:
        err("F12a", "R18", "getItem throws", e)
    finally:
        S.close()
    S = Sess(browser, storage="{", init="Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); };", counter=False)
    try:
        rec("F12.reset-save-fails", "R17/R18", "unreadable data with a failing reset save: note shown, empty list, no errors",
            S.page.locator("div.note").count() == 1 and S.page.locator("p.empty").count() == 1 and S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
        S.page.get_by_role("button", name="Dismiss note", exact=True).click()
        S.add("Read")
        rec("F12.reset-save-fails2", "R18", "add still works after the failing reset", S.names() == ["Read"] and S.errors == [], S.errors)
    except Exception as e:
        err("F12b", "R17/R18", "reset save fails", e)
    finally:
        S.close()
    S = Sess(browser, storage=seed_text(SAMPLE), init="Storage.prototype.setItem = function () { throw new Error('boom'); };", counter=False)
    try:
        S.day(0, "2026-10-05").click()
        rec("F12.plain-error", "R18", "setItem throws a plain Error: tick still shown, no page error", S.errors == [] and S.day(0, "2026-10-05").get_attribute("aria-pressed") == "false", S.errors)
    except Exception as e:
        err("F12c", "R18", "plain error", e)
    finally:
        S.close()


def flow_twelve(browser):
    S = Sess(browser, storage=seed_text([{"name": f"Habit {n}", "done": []} for n in range(1, 12)]))
    try:
        S.add("Habit 12")
        s = S.snap()
        rec("F13.12th", "R12", "12th add disables input and Add, shows the note with field-note", s["input"]["disabled"] and s["addDisabled"] and s["msg"] == ["You track 12 habits, the most this app holds. Delete one to add another.", "field-msg field-note"], s["msg"])
        order = []
        for _ in range(12 * 8 + 1):
            S.page.keyboard.press("Tab")
            order.append(S.active_label())
        rec("F13.skip-disabled", "R12/R22", "disabled input and Add are skipped by Tab across the whole page", "new-habit" not in order and "Add" not in order, "")
        S.page.keyboard.press("Escape")
        S.open_delete("Habit 12")
        S.confirm_delete()
        s = S.snap()
        rec("F13.delete12", "R12/R15", "deleting the last of 12: input enabled, message cleared (field-error), focus on the input", not s["input"]["disabled"] and s["msg"] == ["", "field-msg field-error"] and s["active"] == "new-habit", (s["msg"], s["active"]))
        S.add("Habit 12 again", enter=True)
        s = S.snap()
        rec("F13.readd", "R12", "adding back to 12 disables again", s["input"]["disabled"] and len(s["rows"]) == 12, "")
        rec("F13.clean", "R25", "no console or page errors", S.console_errors() == [] and S.errors == [], (S.console_errors(), S.errors))
    except Exception as e:
        err("F13", "R12", "twelve habits", e)
    finally:
        S.close()


def flow_model_random(browser, seed, ops):
    rng = random.Random(seed)
    S = Sess(browser)
    m = Model(D("2026-10-08"))
    window = m.window()
    pool = ["Read", "Walk", "Water", "Sleep", "Stretch", "Journal", "Code", "Run", "Yoga", "Piano", "Cook", "Floss", "Plan", "Swim"]
    failures = []
    counts = {"tick": 0, "add": 0, "add-bad": 0, "delete": 0, "keep": 0, "reload": 0, "dbl": 0}
    expected_writes = 0
    try:
        for i in range(ops):
            roll = rng.random()
            note = ""
            try:
                if roll < 0.40 and m.habits:
                    hi = rng.randrange(len(m.habits))
                    d = rng.choice(window)
                    S.day(hi, d.isoformat()).click()
                    if d in m.habits[hi][1]:
                        m.habits[hi][1].remove(d)
                    else:
                        m.habits[hi][1].add(d)
                    expected_writes += 1
                    counts["tick"] += 1
                    note = f"tick {m.habits[hi][0]} {d}"
                elif roll < 0.45 and m.habits:
                    hi = rng.randrange(len(m.habits))
                    d = rng.choice(window)
                    S.day(hi, d.isoformat()).dblclick()
                    expected_writes += 2
                    counts["dbl"] += 1
                    note = f"dblclick {m.habits[hi][0]} {d}"
                elif roll < 0.65:
                    if len(m.habits) >= 12:
                        continue
                    name = rng.choice(pool)
                    typed = rng.choice(["", name, "  " + name + "  ", name.upper(), name.lower()]) if rng.random() < 0.6 else name
                    clean = typed.strip()
                    enter = rng.random() < 0.5
                    S.page.locator("#new-habit").fill("")
                    S.add(typed, enter=enter)
                    dup = any(n.lower() == clean.lower() for n, _ in m.habits)
                    if clean == "" or dup:
                        counts["add-bad"] += 1
                        want = "Name the habit first." if clean == "" else "You already track this habit."
                        got = S.snap()["msg"]
                        if got[0] != want:
                            failures.append((i, f"error message {got} wanted {want}", typed))
                        note = f"add-bad {typed!r}"
                    else:
                        m.habits.append([clean, set()])
                        expected_writes += 1
                        counts["add"] += 1
                        note = f"add {clean!r}"
                elif roll < 0.80 and m.habits:
                    hi = rng.randrange(len(m.habits))
                    name = m.habits[hi][0]
                    S.open_delete(name)
                    if S.page.locator("#del-title").text_content() != f'Delete "{name}"?':
                        failures.append((i, "dialog title wrong", name))
                    S.confirm_delete()
                    m.habits.pop(hi)
                    expected_writes += 1
                    counts["delete"] += 1
                    note = f"delete {name!r}"
                    s = S.snap()
                    want_focus = f"Delete {m.habits[hi][0]}" if hi < len(m.habits) else "new-habit"
                    if s["active"] != want_focus:
                        failures.append((i, f"focus after delete {s['active']!r} wanted {want_focus!r}", name))
                elif roll < 0.90 and m.habits:
                    hi = rng.randrange(len(m.habits))
                    name = m.habits[hi][0]
                    how = rng.choice(["cancel", "esc", "backdrop"])
                    S.open_delete(name)
                    if how == "cancel":
                        S.page.get_by_role("button", name="Cancel", exact=True).click()
                    elif how == "esc":
                        S.page.keyboard.press("Escape")
                    else:
                        S.page.mouse.click(5, 5)
                    S.closed()
                    counts["keep"] += 1
                    note = f"keep via {how} {name!r}"
                    if S.active_label() != f"Delete {name}":
                        failures.append((i, f"focus after {how} {S.active_label()!r}", name))
                elif roll < 0.95:
                    S.page.reload()
                    counts["reload"] += 1
                    note = "reload"
                else:
                    continue
            except Exception as e:
                failures.append((i, "exception " + repr(e)[:200], note))
                break
            snap = S.snap()
            probs = diff_model(snap, m)
            if len(S.writes()) != expected_writes:
                probs.append(f"writes {len(S.writes())} vs expected {expected_writes}")
            if probs:
                failures.append((i, note, probs[:4]))
                if len(failures) > 4:
                    break
        rec(f"F14.model.seed{seed}", "R5-R16", f"model-based run of {ops} operations {counts}: DOM, storage text and write count equal the oracle after every operation; focus rules hold", not failures, failures[:5])
        rec(f"F14.model.seed{seed}.clean", "R25", "no console error or page error in the random run", S.console_errors() == [] and S.errors == [], (S.console_errors()[:3], S.errors[:3]))
        S.shot(f"F14-model-end-seed{seed}")
    except Exception as e:
        err(f"F14.seed{seed}", "R5-R16", "model run", e)
    finally:
        S.close()


def flow_backdrop_colour(browser):
    S = Sess(browser, storage=seed_text(SAMPLE), reduced="reduce")
    try:
        S.day(0, "2026-10-05").click()
        S.open_delete("Read 20 pages")
        bd = S.page.evaluate("() => getComputedStyle(document.querySelector('dialog.dialog'), '::backdrop').backgroundColor")
        rec("F15.backdrop-colour", "R2/R23", "native ::backdrop shows the scrim colour under reduced motion", "28, 37, 35" in bd, bd)
        S.page.keyboard.press("Escape")
        S.closed()
    except Exception as e:
        err("F15", "R23", "reduced motion", e)
    finally:
        S.close()
    S = Sess(browser, storage=seed_text(SAMPLE))
    try:
        S.open_delete("Read 20 pages")
        bd = S.page.evaluate("() => getComputedStyle(document.querySelector('dialog.dialog'), '::backdrop').backgroundColor")
        rec("F15.backdrop-colour2", "R2", "native ::backdrop colour without reduced motion", "28, 37, 35" in bd, bd)
        box = S.page.locator("button.icon-btn[aria-label='Delete Stretch 10 minutes']").bounding_box()
        S.page.mouse.click(box["x"] + 5, box["y"] + 5)
        S.closed()
        s_after = S.snap()
        rec("F15.inert", "R13", "a click on the backdrop over another habit's trash only closes the dialog (no second dialog, nothing deleted)", not s_after["dialogOpen"] and len(s_after["rows"]) == 3, "")
    except Exception as e:
        err("F15b", "R13", "backdrop over trash", e)
    finally:
        S.close()


def flow_german_locale(browser):
    S = Sess(browser, locale="de-DE", storage=seed_text(SAMPLE))
    try:
        m = sample_model()
        rec("F16.de", "R4", "de-DE browser: whole page equals the English oracle", not diff_model(S.snap(), m), diff_model(S.snap(), m))
    except Exception as e:
        err("F16", "R4", "de-DE", e)
    finally:
        S.close()


def static_scans():
    src = ROOT / "src"
    files = sorted(p for p in src.iterdir() if p.is_file())
    texts = {p.name: p.read_text(encoding="utf-8") for p in files}
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    sinks = ["innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"]
    hits = [(n, s) for n, t in texts.items() for s in sinks if s in t]
    rec("S1.sinks", "R24", f"no HTML sink in any file under src/ ({', '.join(texts)}), styles.css included", not hits, hits)
    names = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm", "sample-history"]
    hits = [(n, s) for n, t in {**texts, "index.html": index}.items() for s in names if s in t]
    rec("S1.sample", "R26", "no sample name or sample-history reference in index.html or any file under src/ (styles.css included)", not hits, hits)
    net = ["fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource", "importScripts", "serviceWorker", "http://", "https://"]
    hits = [(n, s) for n, t in texts.items() for s in net if s in t.replace("http://www.w3.org/2000/svg", "")]
    rec("S1.net", "R25", "no network API and no absolute URL anywhere in src/ (the SVG namespace string excepted)", not hits, hits)
    asyncs = ["setTimeout", "requestAnimationFrame", "queueMicrotask", "Promise", "async ", "await ", ".then("]
    hits = [(n, s) for n, t in texts.items() if n.endswith(".js") for s in asyncs if s in t]
    rec("S1.sync", "Invariants", "no setTimeout/rAF/queueMicrotask/Promise/async in src/*.js (renders are synchronous)", not hits, hits)
    date_use = [(n, m.group(0)) for n, t in texts.items() if n.endswith(".js") for m in re.finditer(r"new Date\(|Date\.now", t)]
    rec("S1.clock", "Invariants", "the clock is read in one place: 'new Date(' / 'Date.now' occurs only in src/app.js", all(n == "app.js" for n, _ in date_use) and len(date_use) >= 1, date_use)
    imports = []
    for n, t in texts.items():
        if n.endswith(".js"):
            for mm in re.finditer(r"""(?:import|from)\s*\(?\s*["']([^"']+)["']""", t):
                imports.append((n, mm.group(1)))
    rec("S1.imports", "R1", "every import specifier starts with ./", bool(imports) and all(s.startswith("./") for _, s in imports), imports)
    windows = [(n, m.group(0)) for n, t in texts.items() if n.endswith(".js") for m in re.finditer(r"window\.\w+\s*=|globalThis\.\w+\s*=|self\.\w+\s*=", t)]
    rec("S1.globals", "R26", "no assignment to window/globalThis/self in src/", not windows, windows)
    rec("S1.template", "R1", "index.html has no <template>, no inline script, no inline event handler",
        "<template" not in index and not re.search(r"<script(?![^>]*src=)", index) and not re.search(r"\son\w+\s*=", index), "")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        try:
            for fn in (flow_first_visit, flow_add_tick_reload, flow_delete, flow_stray_enter_keyboard, flow_name_errors,
                       flow_unreadable, flow_width_360, flow_desktop, flow_rollover_extras, flow_timezones,
                       flow_names_as_text, flow_storage_failures, flow_twelve, flow_backdrop_colour,
                       flow_german_locale):
                try:
                    fn(browser)
                except Exception as e:
                    err(fn.__name__, "?", "flow crashed", e)
            for seed in (20261009, 7, 1234):
                flow_model_random(browser, seed, 90)
        finally:
            browser.close()
    static_scans()
    (OUT / "results.json").write_text(json.dumps(RESULTS, indent=1, ensure_ascii=False), encoding="utf-8")
    p = sum(1 for r in RESULTS if r["verdict"] == "PASS")
    f = sum(1 for r in RESULTS if r["verdict"] == "FAIL")
    e = sum(1 for r in RESULTS if r["verdict"] == "ERROR")
    print(f"\nPROBE TOTAL pass={p} fail={f} error={e}", flush=True)


if __name__ == "__main__":
    main()
