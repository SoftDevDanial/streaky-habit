"""Re-runs the two states-sheet cases that the first pass (states_sheet.py) flagged, with the mouse parked away from the
page first. Both flags were the test's own pointer: after a click on Add the pointer still sat on the Add button (hover
fill --bead-deep), and after typing a habit the pointer sat where the new row's last bead appeared (hover stroke --bead).
This script reuses the helper half of states_sheet.py unchanged and writes states_sheet_rerun.json.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / "states_sheet.py").read_text(encoding="utf-8").split("def run():")[0]
exec(compile(source, "states_sheet_helpers", "exec"))  # noqa: S102  (our own file, helpers only)

cases = Cases()
facts = {}
with sync_playwright() as pw:
    browser = launch(pw)
    sctx, sheet = ctx_page(browser, golden_url("ST"))

    # ST-01 again: submit an empty name, park the pointer, blur, wait out the 180ms transitions
    ctx, page = ctx_page(browser, BASE)
    before = page.evaluate("() => document.querySelector('form.add').getBoundingClientRect().height")
    page.get_by_role("button", name="Add").click()
    page.mouse.move(2, 2)
    page.evaluate("() => document.activeElement.blur()")
    page.wait_for_timeout(600)
    after = page.evaluate("() => document.querySelector('form.add').getBoundingClientRect().height")
    for what, sspec, lspec in (("Add button", {"css": "form:has(#s3a) .btn"}, {"css": ".add .btn"}), ("input", {"css": "#s3a"}, {"css": "#new-habit"}),
                               ("message", {"css": "#s3a-msg"}, {"css": "#new-habit-msg"}), ("label", {"css": "form:has(#s3a) .add-label"}, {"css": "label.add-label"})):
        s_el, l_el = getp(sheet, sspec), getp(page, lspec)
        cases.add("ST-01", f"S3 empty (rerun, pointer parked): {what}", s_el, l_el, sizes=(what == "Add button"))
        if what == "input":
            cases.out[-1]["diffs"] = [d for d in cases.out[-1]["diffs"] if d[0] != "__w"]
    facts["ST-01"] = {"form_height_before": before, "form_height_after": after, "grew_by": round(after - before, 2)}
    ctx.close()

    # ST-05 again: add the habit with the keyboard, park the pointer, wait
    ctx, page = ctx_page(browser, BASE)
    page.locator("#new-habit").click()
    page.keyboard.type("Read 20 pages")
    page.keyboard.press("Enter")
    page.mouse.move(2, 2)
    page.wait_for_timeout(700)
    live_rows = page.evaluate(DUMP_JS, {"spec": {"css": "li.habit"}, "keys": STD})
    sheet_rows = sheet.evaluate(DUMP_JS, {"spec": {"css": "li.habit:has(#new-name)"}, "keys": STD})
    cases.add_dump("ST-05", "A habit just added (rerun, pointer parked): the whole row, every element", sheet_rows, live_rows, skip=("text-align",))
    facts["ST-05"] = {"elements_compared": len(live_rows), "streak_line": next(e["text"] for e in live_rows if e["cls"] == "cur none"),
                      "best_elements": sum(1 for e in live_rows if e["cls"] == "best"), "name": next(e["text"] for e in live_rows if e["cls"] == "habit-name"),
                      "beads": sum(1 for e in live_rows if e["cls"] == "bead"),
                      "pressed_beads": page.evaluate("() => document.querySelectorAll('li.habit .day[aria-pressed=true]').length"),
                      "today_bead_shadow": next(e["props"]["box-shadow"] for e in live_rows if e["cls"] == "bead" and e["props"]["box-shadow"] != "none"),
                      "thread_halves_first_two_slots": [e.get("pseudo") for e in live_rows if e["cls"] == "slot"][:2]}
    ctx.close()
    browser.close()

(HERE / "states_sheet_rerun.json").write_text(json.dumps({"cases": cases.out, "facts": facts}, indent=2, ensure_ascii=False), encoding="utf-8")
for c in cases.out:
    print(c["row"], c["case"], "diffs:", c["diffs"][:5])
print(json.dumps(facts, indent=1)[:1500])
