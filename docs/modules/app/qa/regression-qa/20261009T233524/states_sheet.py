"""Regression QA: the states sheet (app qa.md, R28 "Every specimen on the states sheet matches the live state",
rows ST-01 to ST-17). No pytest test covers it, so the QA finder drives it.

The live app at 360 x 780 is put into each state with real gestures (click, keyboard.type, keyboard.press,
Tab, mouse.move, mouse.down and mouse.up, hover). The sheet, docs/design/states.html, is served by the same
server and opened in a second tab of the same browser context. Each specimen element is compared with its
live element by computed style (colour, background, borders, outline, shadow, radius, font, line height,
transform, opacity, cursor, bead and button sizes, and the ::before and ::after pseudo elements of the heat
cells and thread), and the live class names and texts where the sheet gives them. Specimen-only styling
(frame sizes, the 56 px day width in .spec-day, the 24 px heat cell width in .spec-cell, the hidden thread of
the lone-bead specimens) is left out, as the Fidelity gate says.

The thread's pixel width is not compared: `.slot::before` is `right: 50%` and `.slot::after` is `left: 50%`
(styles.css), so its width is half the slot, and the slot is as wide as the frame's day cell (45.72 px live at
360, 40 px in the sheet's frame). The rule, display, height, colour and border are compared; the width is
checked as half the slot's own width on each side (a hidden thread, the last day's ::after, is checked as
display none on both sides).

Test-side steps that are not user gestures (documented, the same as the harness's own method):
- the clock is fixed at 2026-10-08 12:00 (the suite's open_app), and reduced motion is "reduce", as the
  fidelity harness renders both sides;
- before a comparison the pointer is parked at (2, 2) and a focused element is blurred, because the sheet's
  specimens are never focused or hovered (the .is-hover and .is-focus classes stand for those states).

Output: states-sheet.json in --out (one record per comparison, with the values read on both sides).
Usage: python states_sheet.py --base-url http://127.0.0.1:<port>/ --out <folder>
"""
import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tests" / "browser"))

from playwright.sync_api import expect, sync_playwright  # noqa: E402

from conftest import open_app, plain_state, row, sample_state  # noqa: E402

VIEWPORT = (360, 780)
READ, STRETCH, NO_PHONE = "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"
DRINK = "Drink water"
COLOR = [
    "color", "background-color", "border-top-color", "border-right-color", "border-bottom-color", "border-left-color",
    "border-top-width", "border-right-width", "border-bottom-width", "border-left-width", "border-top-style",
    "border-bottom-style", "box-shadow", "border-radius", "font-size", "font-weight", "line-height", "letter-spacing",
    "transform", "opacity", "cursor",
]
OUTLINE = ["outline-color", "outline-style", "outline-width", "outline-offset"]
SIZE = ["width", "height"]
BEAD_PSEUDO = ["width", "height", "background-color", "border-top-color", "border-top-width", "border-top-style", "border-radius", "box-shadow"]
THREAD_PSEUDO = ["display"] + [p for p in BEAD_PSEUDO if p != "width"]  # the width is half the slot, checked on its own

READ_JS = """(el, arg) => {
  const [pseudo, props] = arg;
  const cs = getComputedStyle(el, pseudo);
  const out = {};
  for (const p of props) {
    if (p === '@class') out[p] = el.className;
    else if (p === '@text') out[p] = el.textContent.replace(/\\s+/g, ' ').trim();
    else if (p.startsWith('@attr:')) out[p] = el.getAttribute(p.slice(6));
    else out[p] = cs.getPropertyValue(p);
  }
  return out;
}"""

# [slot width, thread width, thread display] of a .slot and one of its pseudo elements, unrounded
HALF_SLOT_JS = """(el, pseudo) => {
  const pseudoStyle = getComputedStyle(el, pseudo);
  return [parseFloat(getComputedStyle(el).width), parseFloat(pseudoStyle.width), pseudoStyle.display];
}"""


class Results:
    def __init__(self):
        self.items = []

    def compare(self, row_id, label, live, spec, props, live_pseudo=None, spec_pseudo=None):
        """Read the same properties on the live element and on the specimen and record every difference."""
        counts = (live.count(), spec.count())
        if counts != (1, 1):
            self.items.append({"row": row_id, "label": label, "pass": False, "detail": f"element count live {counts[0]} spec {counts[1]}"})
            print(f"FAIL {row_id} {label}: element count live {counts[0]} spec {counts[1]}", flush=True)
            return
        live_values = live.evaluate(READ_JS, [live_pseudo, props])
        spec_values = spec.evaluate(READ_JS, [spec_pseudo, props])
        diffs = {p: {"live": live_values[p], "spec": spec_values[p]} for p in props if live_values[p] != spec_values[p]}
        self.items.append({
            "row": row_id, "label": label, "pass": not diffs, "properties": len(props), "diffs": diffs,
            "live": live_values, "spec": spec_values,
        })
        print(("PASS " if not diffs else "FAIL ") + f"{row_id} {label} ({len(props)} properties)", flush=True)

    def check(self, row_id, label, passed, detail=""):
        self.items.append({"row": row_id, "label": label, "pass": bool(passed), "detail": detail})
        print(("PASS " if passed else "FAIL ") + f"{row_id} {label} {detail}", flush=True)

    def read_now(self, locator, props, pseudo=None):
        return locator.evaluate(READ_JS, [pseudo, props])


def settle(page):
    """Park the pointer on empty page space and blur a focused element, so no hover or focus ring is drawn."""
    page.mouse.move(2, 2)
    page.evaluate("() => { const a = document.activeElement; if (a && a !== document.body) a.blur(); }")


def tab_to(page, target, limit=60):
    for _ in range(limit):
        page.keyboard.press("Tab")
        if target.evaluate("(el) => el === document.activeElement"):
            return True
    return False


def open_pair(browser, base, sheet_url, storage):
    context, page = open_app(browser, viewport=VIEWPORT, reduced_motion="reduce", storage=storage, base_url=base)
    sheet = context.new_page()
    sheet.goto(sheet_url)
    return context, page, sheet


def st_01_to_03_and_10_error(browser, base, sheet_url, r):
    cases = [
        ("ST-01", "", "#s3a", "#s3a-msg", "Name the habit first."),
        ("ST-02", "Walk to the end of the street and back after dinner", "#s3b", "#s3b-msg", "Keep it to 40 characters or fewer."),
        ("ST-03", "read 20 pages", "#s3c", "#s3c-msg", "You already track this habit."),
    ]
    for row_id, typed, spec_input, spec_msg, message in cases:
        context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
        if typed:
            page.locator("#new-habit").click()
            page.keyboard.type(typed)
        page.get_by_role("button", name="Add", exact=True).click()
        expect(page.locator("#new-habit-msg")).to_have_text(message)
        settle(page)
        r.compare(row_id, "field (aria-invalid, danger border)", page.locator("#new-habit"), sheet.locator(spec_input), COLOR + OUTLINE)
        r.compare(row_id, "message line", page.locator("#new-habit-msg"), sheet.locator(spec_msg), COLOR + ["@class", "@text"])
        r.compare(row_id, "Add button", page.get_by_role("button", name="Add", exact=True), sheet.locator(f"form:has({spec_input}) button"), COLOR + OUTLINE)
        if row_id == "ST-01":
            # ST-10 error: the same live field against the text input's error specimen
            r.compare("ST-10", "text input error", page.locator("#new-habit"), sheet.locator('.spec-input .input[aria-label="New habit, error"]'), COLOR + OUTLINE)
        context.close()


def st_04_and_07_disabled_and_10_disabled(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, plain_state(12))
    expect(page.locator("#new-habit-msg")).to_have_text("You track 12 habits, the most this app holds. Delete one to add another.")
    settle(page)
    r.compare("ST-04", "field disabled", page.locator("#new-habit"), sheet.locator("#s4"), COLOR + OUTLINE)
    r.compare("ST-04", "label", page.locator('label[for="new-habit"]'), sheet.locator('label[for="s4"]'), COLOR)
    add = page.get_by_role("button", name="Add", exact=True)
    r.compare("ST-04", "Add disabled", add, sheet.locator("form:has(#s4) button"), COLOR + OUTLINE)
    r.compare("ST-07", "Disabled primary (Add disabled)", add, sheet.locator(".spec > .btn-primary").nth(3), COLOR + OUTLINE)
    r.compare("ST-04", "note", page.locator("#new-habit-msg"), sheet.locator("#s4-msg"), COLOR + ["@class", "@text"])
    r.compare("ST-10", "text input disabled", page.locator("#new-habit"), sheet.locator('.spec-input .input[aria-label="New habit, disabled"]'), COLOR + OUTLINE)
    before = r.read_now(add, COLOR)
    add.hover()
    after = r.read_now(add, COLOR)
    changed = {k: [before[k], after[k]] for k in before if before[k] != after[k]}
    r.check("ST-04", "Add disabled: hovering changes nothing", not changed, f"changed: {changed}" if changed else "")
    context.close()


def st_05_new_row(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, None)
    page.locator("#new-habit").click()
    page.keyboard.type(READ)
    page.get_by_role("button", name="Add", exact=True).click()
    expect(page.locator("li.habit")).to_have_count(1)
    settle(page)
    new_row = row(page, READ)
    r.compare("ST-05", "name", new_row.locator("h3"), sheet.locator("h3#new-name"), ["font-size", "font-weight", "line-height", "color", "letter-spacing"])
    r.compare("ST-05", "No streak yet", new_row.locator(".streak .cur"), sheet.locator("li.habit .streak .cur"), COLOR + ["@class", "@text"])
    r.check("ST-05", "no best element", new_row.locator(".best").count() == 0 and sheet.locator("li.habit .best").count() == 0,
            f"live {new_row.locator('.best').count()}, sheet {sheet.locator('li.habit .best').count()}")
    for index in range(7):
        live_slot = new_row.locator("button.day").nth(index).locator(".slot")
        spec_slot = sheet.locator("li.habit .strip button.day").nth(index).locator(".slot")
        r.compare("ST-05", f"bead {index}", new_row.locator("button.day").nth(index).locator(".bead"),
                  sheet.locator("li.habit .strip button.day").nth(index).locator(".bead"), COLOR + SIZE)
        for pseudo in ("::before", "::after"):
            r.compare("ST-05", f"thread {pseudo}, day {index}", live_slot, spec_slot, THREAD_PSEUDO, live_pseudo=pseudo, spec_pseudo=pseudo)
            live_slot_width, live_thread_width, live_display = live_slot.evaluate(HALF_SLOT_JS, pseudo)
            spec_slot_width, spec_thread_width, spec_display = spec_slot.evaluate(HALF_SLOT_JS, pseudo)
            if live_display == "none" or spec_display == "none":
                r.check("ST-05", f"thread {pseudo}, day {index}: hidden on both sides",
                        live_display == spec_display == "none", f"live {live_display}, sheet {spec_display}")
            else:
                ok = abs(live_thread_width - live_slot_width / 2) <= 0.05 and abs(spec_thread_width - spec_slot_width / 2) <= 0.05
                r.check("ST-05", f"thread {pseudo}, day {index}: width is half the slot on both sides", ok,
                        f"live slot {live_slot_width:.3f} thread {live_thread_width:.3f}; sheet slot {spec_slot_width:.3f} thread {spec_thread_width:.3f}")
    r.compare("ST-05", "today day button", new_row.locator('button.day[aria-current="date"]'), sheet.locator('li.habit button.day[aria-current="date"]'), COLOR + ["@attr:aria-current"])
    context.close()


def st_06_note(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, "{")
    expect(page.locator("div.note")).to_be_visible()
    r.compare("ST-06", "note banner", page.locator("div.note"), sheet.locator("div.note"), COLOR + ["@attr:role"])
    r.compare("ST-06", "note text", page.locator("div.note .note-text"), sheet.locator("div.note .note-text"), COLOR + ["@text"])
    r.compare("ST-06", "Dismiss button", page.locator("div.note button"), sheet.locator("div.note button"), COLOR + SIZE + ["@attr:aria-label"])
    r.compare("ST-06", "Dismiss glyph", page.locator("div.note button svg"), sheet.locator("div.note button svg"), ["color"] + SIZE)
    r.compare("ST-06", "empty message, 32 px below the note", page.locator("p.empty"), sheet.locator("p.empty"), ["margin-top", "font-size", "line-height", "font-weight"])
    r.compare("ST-06", "brand (h1 in the app, p on the sheet)", page.locator("h1.brand"), sheet.locator("p.brand"), ["font-size", "font-weight", "line-height", "letter-spacing", "color"])
    context.close()


def st_07_primary(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    add = page.get_by_role("button", name="Add", exact=True)
    r.compare("ST-07", "primary default", add, sheet.locator(".spec > .btn-primary").nth(0), COLOR + OUTLINE)
    add.hover()
    r.compare("ST-07", "primary hover", add, sheet.locator(".spec > .btn-primary").nth(1), COLOR + OUTLINE)
    box = add.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    pressed = add.evaluate(READ_JS, [None, ["transform"]])["transform"]
    page.mouse.move(2, 2)
    page.mouse.up()
    r.check("ST-07", "primary press scales to 0.98", pressed == "matrix(0.98, 0, 0, 0.98, 0, 0)", f"transform while pressed: {pressed}")
    settle(page)
    page.locator("#new-habit").click()
    reached = tab_to(page, add)
    r.check("ST-07", "keyboard reaches Add", reached, "Tab from the field")
    r.compare("ST-07", "primary keyboard focus", add, sheet.locator(".spec > .btn-primary").nth(2), COLOR + OUTLINE)
    context.close()


def st_08_09_dialog(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    page.get_by_role("button", name=f"Delete {READ}", exact=True).click()
    expect(page.locator("dialog.dialog")).to_have_attribute("open", "")
    cancel = page.locator("dialog.dialog").get_by_role("button", name="Cancel", exact=True)
    delete = page.locator("dialog.dialog").get_by_role("button", name="Delete habit", exact=True)
    settle(page)
    r.compare("ST-08", "secondary default (Cancel)", cancel, sheet.locator(".spec > .btn-secondary").nth(0), COLOR + OUTLINE)
    cancel.hover()
    r.compare("ST-08", "secondary hover (Cancel)", cancel, sheet.locator(".spec > .btn-secondary").nth(1), COLOR + OUTLINE)
    delete.hover()
    r.compare("ST-09", "danger hover (Delete habit)", delete, sheet.locator(".spec > .btn-danger").nth(1), COLOR + OUTLINE)
    settle(page)
    r.compare("ST-09", "danger default (Delete habit)", delete, sheet.locator(".spec > .btn-danger").nth(0), COLOR + OUTLINE)
    context.close()


def st_10_input_default_and_focus(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    r.compare("ST-10", "text input default", page.locator("#new-habit"), sheet.locator('.spec-input .input[aria-label="New habit, default"]'), COLOR + OUTLINE)
    field = page.locator("#new-habit")
    r.check("ST-10", "keyboard reaches the field", tab_to(page, field), "Tab only")
    r.compare("ST-10", "text input keyboard focus", field, sheet.locator(".spec-input .input.is-focus"), COLOR + OUTLINE)
    context.close()


def st_11_to_15_sample(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    cases = [
        ("not done", READ, 0, 0),
        ("done", READ, 1, 1),
        ("today, not done", STRETCH, 6, 2),
        ("today, done", NO_PHONE, 6, 3),
    ]
    spec_days = sheet.locator(".spec-day > .day:not(.is-hover):not(.is-focus)")
    for label, name, live_index, spec_index in cases:
        live_day = row(page, name).locator("button.day").nth(live_index)
        spec_day = spec_days.nth(spec_index)
        r.compare("ST-11", f"day {label}: button", live_day, spec_day, [p for p in COLOR + OUTLINE if p != "width"] + ["@class"])
        r.compare("ST-11", f"day {label}: bead", live_day.locator(".bead"), spec_day.locator(".bead"), COLOR + SIZE)
        r.compare("ST-11", f"day {label}: bead check glyph", live_day.locator(".bead svg"), spec_day.locator(".bead svg"), ["opacity", "color", "fill"] + SIZE)
        r.compare("ST-11", f"day {label}: weekday", live_day.locator(".wd"), spec_day.locator(".wd"), ["color", "font-size", "font-weight", "line-height"])
        r.compare("ST-11", f"day {label}: day number", live_day.locator(".dm"), spec_day.locator(".dm"), ["color", "font-size", "font-weight", "line-height"])

    # ST-12: hover on a not-done bead, then on a done bead
    hover_specs = sheet.locator(".spec-day > .day.is-hover")
    live_not_done = row(page, READ).locator("button.day").nth(0)
    live_not_done.hover()
    r.compare("ST-12", "hover, not done: bead stroke", live_not_done.locator(".bead"), hover_specs.nth(0).locator(".bead"), COLOR + SIZE)
    live_done = row(page, READ).locator("button.day").nth(1)
    live_done.hover()
    r.compare("ST-12", "hover, done: bead fill and stroke", live_done.locator(".bead"), hover_specs.nth(1).locator(".bead"), COLOR + SIZE)
    settle(page)

    # ST-13: keyboard focus on today's bead of Stretch (not done), the cell draws the capsule ring
    target = row(page, STRETCH).locator("button.day").nth(6)
    r.check("ST-13", "keyboard reaches Stretch's Thu 8 day", tab_to(page, target), "Tab only")
    focus_spec = sheet.locator(".spec-day > .day.is-focus")
    r.compare("ST-13", "keyboard focus: the day cell", target, focus_spec.nth(0), OUTLINE + ["border-radius", "box-shadow", "background-color"])
    r.compare("ST-13", "keyboard focus: the bead has no outline and keeps the today ring", target.locator(".bead"), focus_spec.nth(0).locator(".bead"), ["outline-style", "box-shadow", "width", "height"])
    settle(page)

    # ST-14: a press scales the bead to 0.94 and releasing off the cell ticks nothing
    target_box = target.bounding_box()
    page.mouse.move(target_box["x"] + target_box["width"] / 2, target_box["y"] + target_box["height"] / 2)
    page.mouse.down()
    pressed = target.locator(".bead").evaluate(READ_JS, [None, ["transform"]])["transform"]
    page.mouse.move(2, 2)
    page.mouse.up()
    r.check("ST-14", "bead scales to 0.94 while pressed", pressed == "matrix(0.94, 0, 0, 0.94, 0, 0)", f"transform while pressed: {pressed}")
    r.check("ST-14", "release off the cell ticks nothing", target.get_attribute("aria-pressed") == "false", f"aria-pressed {target.get_attribute('aria-pressed')}")
    settle(page)

    # ST-15: the trash button at rest, on hover and on keyboard focus
    trash = page.get_by_role("button", name=f"Delete {READ}", exact=True)
    icon_specs = sheet.locator(".spec > .icon-btn")
    r.compare("ST-15", "trash at rest", trash, icon_specs.nth(0), COLOR + SIZE + ["@attr:aria-label"])
    r.compare("ST-15", "trash glyph at rest", trash.locator("svg"), icon_specs.nth(0).locator("svg"), ["color"] + SIZE)
    trash.hover()
    r.compare("ST-15", "trash on hover", trash, icon_specs.nth(1), COLOR + SIZE)
    r.compare("ST-15", "trash hover glyph", trash.locator("svg"), icon_specs.nth(1).locator("svg"), ["color"] + SIZE)
    settle(page)
    r.check("ST-15", "keyboard reaches the trash button", tab_to(page, trash), "Tab only")
    r.compare("ST-15", "trash keyboard focus", trash, icon_specs.nth(2), COLOR + OUTLINE + SIZE)
    context.close()


def heat_pairs(page, sheet, r, pairs, row_id):
    """pairs: (label, date, index of the specimen in .spec-cell > .hc). The index is the sheet's own order."""
    for label, key, index in pairs:
        live = page.locator(f'.cells .hc[data-date="{key}"]')
        spec = sheet.locator(".spec-cell > .hc").nth(index)
        r.compare(row_id, f"cell {label} ({key})", live, spec, ["@class", "background-color", "border-top-color", "border-top-width", "border-top-style", "border-radius", "box-shadow", "outline-style"])
        if index != 6:  # the future specimen draws no dot
            r.compare(row_id, f"dot {label} ({key})", live, spec, BEAD_PSEUDO, live_pseudo="::before", spec_pseudo="::before")


def st_16_heat(browser, base, sheet_url, r, levels):
    picked = {}
    for key in sorted(levels):
        level = levels[key]
        if key < "2026-10-08" and level in (0, 1, 2, 4) and level not in picked:
            picked[level] = key
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    row(page, STRETCH).locator("button.day").nth(6).click()  # Stretch on Thu 8 goes 3 of 3: level 4 and today
    expect(page.locator('.cells .hc[data-date="2026-10-08"]')).to_have_attribute("aria-label", "Thu 8 Oct, 3 of 3 habits")
    settle(page)
    heat_pairs(page, sheet, r, [
        ("l0", picked[0], 0),
        ("l1", picked[1], 1),
        ("l2", picked[2], 2),
        ("l4", picked[4], 4),
        ("today, level 4", "2026-10-08", 5),
        ("future", "2026-10-09", 6),
    ], "ST-16")
    context.close()

    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    page.locator("#new-habit").click()
    page.keyboard.type(DRINK)
    page.keyboard.press("Enter")
    expect(row(page, DRINK)).to_have_count(1)
    settle(page)
    heat_pairs(page, sheet, r, [("l3, sample plus Drink water", "2026-07-20", 3)], "ST-16")
    context.close()


def st_17_chrome(browser, base, sheet_url, r):
    context, page, sheet = open_pair(browser, base, sheet_url, sample_state())
    settle(page)
    sheet_only_selectors = ".sheet, .frame, .frame-cap, .group, .frames, .spec, .specs, .is-hover, .is-focus, .spec-day, .spec-input, .spec-cell"
    count = page.locator(sheet_only_selectors).count()
    text = page.inner_text("body")
    strings = ["Streaks states", "A specimen sheet", "Habit list", "Component states", "Add field", "Level 0, none of the habits"]
    present = [s for s in strings if s in text or page.locator(f'[aria-label="{s}"]').count()]
    r.check("ST-17", "no sheet-only classes or strings in the live app", count == 0 and not present,
            f"sheet-only elements {count}, strings {present}")
    context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    sheet_url = base + "docs/design/states.html"
    sample = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))
    levels = sample["heatmapLevels"]

    r = Results()
    started = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        st_01_to_03_and_10_error(browser, base, sheet_url, r)
        st_04_and_07_disabled_and_10_disabled(browser, base, sheet_url, r)
        st_05_new_row(browser, base, sheet_url, r)
        st_06_note(browser, base, sheet_url, r)
        st_07_primary(browser, base, sheet_url, r)
        st_08_09_dialog(browser, base, sheet_url, r)
        st_10_input_default_and_focus(browser, base, sheet_url, r)
        st_11_to_15_sample(browser, base, sheet_url, r)
        st_16_heat(browser, base, sheet_url, r, levels)
        st_17_chrome(browser, base, sheet_url, r)
        version = browser.version
        browser.close()

    comparisons = [i for i in r.items if "properties" in i]
    checks = [i for i in r.items if "properties" not in i]
    failed = [i for i in r.items if not i["pass"]]
    summary = {
        "viewport": "360x780", "browser": f"Chromium {version}", "sheet": sheet_url,
        "comparisons": len(comparisons), "properties_compared": sum(i["properties"] for i in comparisons),
        "checks": len(checks), "failed": len(failed), "seconds": round(time.monotonic() - started, 1),
        "pass": not failed,
    }
    (out / "states-sheet.json").write_text(json.dumps({"summary": summary, "items": r.items}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("STATES SHEET", json.dumps(summary), flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
