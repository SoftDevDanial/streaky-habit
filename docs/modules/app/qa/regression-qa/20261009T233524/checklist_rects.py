"""Regression QA: the numbers in the FE element checklist (app qa.md, R28 "Each screen is 1-to-1 with its golden",
rows S1, S2, M1) and the explicit measures of the states sheet rows (ST-01, ST-04, ST-05, ST-06), read from the
running app with getBoundingClientRect and getComputedStyle. The pixel gate (harness, 0 mismatched pixels) is
run separately; this checks the numbers the checklist writes down, which the pixel gate does not name.

The rows checked here are the ones the checklist states as numbers. The descriptive rows (roles, names,
classes, hover and focus looks) are covered by the states-sheet driver, the DOM tests and the functional
scenarios, and are not repeated here.

Gestures: the sample day, the fresh day, the twelve-habit day and the open delete dialog are reached with real
clicks and typing. The clock is the suite's fixed 2026-10-08 12:00 and reduced motion is "reduce" (as the
harness renders).
Output: checklist-rects.json in --out. Usage: python checklist_rects.py --base-url http://127.0.0.1:<port>/ --out <folder>
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

READ, STRETCH, NO_PHONE = "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"
RECT_JS = "(el) => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }"
PSEUDO_WIDTH_JS = "(el, p) => parseFloat(getComputedStyle(el, p).width)"
STYLE_JS = "(el, p) => getComputedStyle(el).getPropertyValue(p)"

results = []


def rect(locator):
    return locator.evaluate(RECT_JS)


def check(row_id, label, value, expected, tol=0.6):
    if isinstance(expected, str):
        ok = value == expected
    else:
        ok = value is not None and abs(value - expected) <= tol
    results.append({"row": row_id, "check": label, "value": value, "expected": expected, "pass": bool(ok)})
    print(("PASS " if ok else "FAIL ") + f"{row_id} {label}: {value} (expected {expected})", flush=True)


def sample_checks(browser, base, viewport, desktop):
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=sample_state(), base_url=base)
    expect(page.locator("li.habit")).to_have_count(3)
    tag = f"{viewport[0]}x{viewport[1]}"
    rows = [row(page, READ), row(page, STRETCH), row(page, NO_PHONE)]
    first_day = rows[0].locator("button.day").nth(0)
    if not desktop:
        for index, top in enumerate([77, 273, 469]):
            check(f"S1-09 {tag}", f"row {index + 1} top", rect(rows[index])[1], top)
        check(f"S1-23 {tag}", "add form top", rect(page.locator("form.add"))[1], 673)
        check(f"S1-28 {tag}", "heat panel top", rect(page.locator("section.heat"))[1], 793)
        check(f"S1-28 {tag}", "heat panel width", rect(page.locator("section.heat"))[2], 350)
        check(f"S1-20 {tag}", "day cell width", rect(first_day)[2], 50)
        check(f"S1-20 {tag}", "day cell height", rect(first_day)[3], 92)
        check(f"S1-21 {tag}", "bead width", rect(first_day.locator(".bead"))[2], 36)
        check(f"S1-21 {tag}", "bead height", rect(first_day.locator(".bead"))[3], 36)
        check(f"S1-32 {tag}", "heat cell width", rect(page.locator('.cells .hc[data-date="2026-10-08"]'))[2], 23.8, 0.1)
        check(f"S1-19 {tag}", "trash width", rect(rows[0].locator("button.icon-btn"))[2], 44)
        check(f"S1-19 {tag}", "trash height", rect(rows[0].locator("button.icon-btn"))[3], 44)
        check(f"S1-25 {tag}", "input width", rect(page.locator("#new-habit"))[2], 256)
    else:
        for index, top in enumerate([101, 301, 501]):
            check(f"S1-09 {tag}", f"row {index + 1} top", rect(rows[index])[1], top)
        check(f"S1-23 {tag}", "add form top", rect(page.locator("form.add"))[1], 709)
        check(f"S1-28 {tag}", "heat panel top (level with the first habit)", rect(page.locator("section.heat"))[1], 101)
        check(f"S1-28 {tag}", "heat panel width", rect(page.locator("section.heat"))[2], 380)
        check(f"S1-07 {tag}", "heat panel x", rect(page.locator("section.heat"))[0], 732)
        check(f"S1-07 {tag}", "main column x", rect(page.locator("div.col-main"))[0], 168)
        check(f"S1-07 {tag}", "main column width", rect(page.locator("div.col-main"))[2], 500)
        check(f"S1-21 {tag}", "bead width", rect(first_day.locator(".bead"))[2], 40)
        check(f"S1-20 {tag}", "day cell width", rect(first_day)[2], 71.4, 0.1)
        check(f"S1-20 {tag}", "day cell height", rect(first_day)[3], 96)
        check(f"S1-32 {tag}", "heat cell width", rect(page.locator('.cells .hc[data-date="2026-10-08"]'))[2], 24.9, 0.1)
        check(f"S1-25 {tag}", "input width", rect(page.locator("#new-habit"))[2], 406)
    check(f"S1-25 {tag}", "input height", rect(page.locator("#new-habit"))[3], 48)
    add = page.get_by_role("button", name="Add", exact=True)
    check(f"S1-26 {tag}", "Add height", rect(add)[3], 48)
    check(f"S1-26 {tag}", "Add width", rect(add)[2], 82)
    input_box, add_box = rect(page.locator("#new-habit")), rect(add)
    check(f"S1-26 {tag}", "Add 12 px right of the input", round(add_box[0] - (input_box[0] + input_box[2]), 2), 12)
    check(f"S1-27 {tag}", "message line hidden while empty (height)", rect(page.locator("#new-habit-msg"))[3], 0)
    heading = rect(page.locator("#habits-title"))
    check(f"S1-08 {tag}", "hidden list heading width", heading[2], 1, 1.5)
    check(f"S1-08 {tag}", "hidden list heading height", heading[3], 1, 1.5)

    # S1-33: the dot of each level, from the sample's own levels (level 0, 1, 2 and 4)
    sample = json.loads((ROOT / "docs" / "design" / "sample-history.json").read_text(encoding="utf-8"))
    picked = {}
    for key in sorted(sample["heatmapLevels"]):
        level = sample["heatmapLevels"][key]
        if key < "2026-10-08" and level not in picked:
            picked[level] = key
    for level, expected in ((0, 6), (1, 7), (2, 11), (4, 17)):
        cell = page.locator(f'.cells .hc[data-date="{picked[level]}"]')
        check(f"S1-33 {tag}", f"level {level} dot width ({picked[level]})", cell.evaluate(PSEUDO_WIDTH_JS, "::before"), expected)
    context.close()


def fresh_checks(browser, base, viewport):
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=None, base_url=base)
    expect(page.locator("p.empty")).to_be_visible()
    tag = f"{viewport[0]}x{viewport[1]}"
    desktop = viewport[0] >= 900
    empty_top = 101 if desktop else 77
    form_top = 197 if desktop else 173
    heat_top = 101 if desktop else 293
    check(f"S2-02 {tag}", "empty message top", rect(page.locator("p.empty"))[1], empty_top)
    check(f"S2-02 {tag}", "empty message height", rect(page.locator("p.empty"))[3], 56)
    check(f"S2-03 {tag}", "add form top", rect(page.locator("form.add"))[1], form_top)
    check(f"S2-04 {tag}", "heat panel top", rect(page.locator("section.heat"))[1], heat_top)
    if not desktop:
        heat = rect(page.locator("section.heat"))
        check(f"S2-04 {tag}", "heat panel ends at 588", round(heat[1] + heat[3], 2), 588)
    context.close()


def dialog_checks(browser, base, viewport):
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=sample_state(), base_url=base)
    expect(page.locator("li.habit")).to_have_count(3)
    page.get_by_role("button", name=f"Delete {READ}", exact=True).click()
    expect(page.locator("dialog.dialog")).to_have_attribute("open", "")
    tag = f"{viewport[0]}x{viewport[1]}"
    dialog = page.locator("dialog.dialog")
    box = rect(dialog)
    cancel = dialog.get_by_role("button", name="Cancel", exact=True)
    delete = dialog.get_by_role("button", name="Delete habit", exact=True)
    if viewport[0] < 900:
        check(f"M1-03 {tag}", "dialog x", box[0], 20)
        check(f"M1-03 {tag}", "dialog y", box[1], 332)
        check(f"M1-03 {tag}", "dialog width", box[2], 350)
        check(f"M1-03 {tag}", "dialog height", box[3], 180, 1)
        check(f"M1-06 {tag}", "Cancel width", rect(cancel)[2], 145)
        check(f"M1-06 {tag}", "Delete habit width", rect(delete)[2], 145)
    else:
        check(f"M1-03 {tag}", "dialog x", box[0], 440)
        check(f"M1-03 {tag}", "dialog y", box[1], 310)
        check(f"M1-03 {tag}", "dialog width", box[2], 400)
        check(f"M1-03 {tag}", "dialog height", box[3], 180, 1)
        check(f"M1-06 {tag}", "Cancel width", rect(cancel)[2], 170)
        check(f"M1-06 {tag}", "Delete habit width", rect(delete)[2], 170)
    check(f"M1-06 {tag}", "Cancel 48 tall", rect(cancel)[3], 48)
    check(f"M1-06 {tag}", "Delete habit 48 tall", rect(delete)[3], 48)
    context.close()


def states_checks(browser, base):
    viewport = (360, 780)

    # ST-01: the error line sits 8 px below the row and the form grows by 28 px
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=sample_state(), base_url=base)
    form = page.locator("form.add")
    before = rect(form)[3]
    page.get_by_role("button", name="Add", exact=True).click()
    expect(page.locator("#new-habit-msg")).to_have_text("Name the habit first.")
    after = rect(form)[3]
    check("ST-01 360x780", "form grows by 28 px when the error shows", round(after - before, 2), 28)
    field = rect(page.locator("#new-habit"))
    message = rect(page.locator("#new-habit-msg"))
    check("ST-01 360x780", "message 8 px below the row", round(message[1] - (field[1] + field[3]), 2), 8)
    context.close()

    # ST-04: the twelve-habit note wraps to two lines, 40 px tall at 14/20
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=plain_state(12), base_url=base)
    expect(page.locator("#new-habit-msg")).to_have_text("You track 12 habits, the most this app holds. Delete one to add another.")
    check("ST-04 360x780", "twelve-habit note is 40 px tall (two lines)", rect(page.locator("#new-habit-msg"))[3], 40)
    context.close()

    # ST-06: the note has padding 8 8 8 20, a 44 px dismiss button 8 px from its top and right edges, and 32 px above the empty message
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage="{", base_url=base)
    expect(page.locator("div.note")).to_be_visible()
    note = page.locator("div.note")
    padding = " ".join(note.evaluate(STYLE_JS, p) for p in ("padding-top", "padding-right", "padding-bottom", "padding-left"))
    check("ST-06 360x780", "note padding 8 8 8 20", padding, "8px 8px 8px 20px")
    dismiss = rect(page.locator("div.note button"))
    note_box = rect(note)
    check("ST-06 360x780", "dismiss button width", dismiss[2], 44)
    check("ST-06 360x780", "dismiss button height", dismiss[3], 44)
    check("ST-06 360x780", "dismiss 8 px from the top edge", round(dismiss[1] - note_box[1], 2), 8)
    check("ST-06 360x780", "dismiss 8 px from the right edge", round(note_box[0] + note_box[2] - (dismiss[0] + dismiss[2]), 2), 8)
    check("ST-06 360x780", "empty message 32 px below the note (margin-top)", page.locator("p.empty").evaluate(STYLE_JS, "margin-top"), "32px")
    context.close()

    # ST-05: a just-added row at 360 has 32 px beads
    context, page = open_app(browser, viewport=viewport, reduced_motion="reduce", storage=None, base_url=base)
    page.locator("#new-habit").click()
    page.keyboard.type(READ)
    page.get_by_role("button", name="Add", exact=True).click()
    expect(row(page, READ)).to_have_count(1)
    bead = row(page, READ).locator("button.day").nth(0).locator(".bead")
    check("ST-05 360x780", "bead width at 360", rect(bead)[2], 32)
    check("ST-05 360x780", "bead height at 360", rect(bead)[3], 32)
    context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    started = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        sample_checks(browser, base, (390, 844), desktop=False)
        sample_checks(browser, base, (1280, 800), desktop=True)
        fresh_checks(browser, base, (390, 844))
        fresh_checks(browser, base, (1280, 800))
        dialog_checks(browser, base, (390, 844))
        dialog_checks(browser, base, (1280, 800))
        states_checks(browser, base)
        version = browser.version
        browser.close()
    failed = [r for r in results if not r["pass"]]
    summary = {"checks": len(results), "failed": len(failed), "browser": f"Chromium {version}",
               "seconds": round(time.monotonic() - started, 1), "pass": not failed}
    (out / "checklist-rects.json").write_text(json.dumps({"summary": summary, "checks": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print("CHECKLIST RECTS", json.dumps(summary), flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
