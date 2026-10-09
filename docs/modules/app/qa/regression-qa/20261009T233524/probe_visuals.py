"""Regression QA probe: three visual details seen in the five-flow screenshots at 390 x 844.

1. Bead colour right after a tick, and after the clock runs on (is a transition still running under the
   paused clock?). Read-only: computed styles, real clicks.
2. Whether the dialog's backdrop covers the whole phone viewport (a viewport-only capture, not full page).
3. Whether the input after a mouse delete matches :focus-visible (a ring shows only then).
Output: probe-visuals.json and probe-*.png in --out. Usage: python probe_visuals.py --base-url <url> --out <folder>
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import expect, sync_playwright

NOON = "2026-10-08T12:00:00+08:00"
PAUSE_AT = "2026-10-08T12:00:20+08:00"
READ, STRETCH = "Read 20 pages", "Stretch 10 minutes"
BEAD_JS = """(key) => {
  const b = document.querySelector('li.habit button.day[data-date="' + key + '"]');
  const s = getComputedStyle(b.querySelector('.bead') || b);
  return { pressed: b.getAttribute('aria-pressed'), background: s.backgroundColor, transitionDuration: s.transitionDuration };
}"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="light",
                                      reduced_motion="no-preference", timezone_id="Asia/Kuala_Lumpur", locale="en-US")
        context.set_default_timeout(5000)
        context.clock.install(time=NOON)
        page = context.new_page()
        page.goto(args.base_url)
        page.clock.pause_at(PAUSE_AT)
        page.locator("#new-habit").click()
        page.keyboard.type(READ)
        page.get_by_role("button", name="Add", exact=True).click()
        page.locator("#new-habit").click()
        page.keyboard.type(STRETCH)
        page.keyboard.press("Enter")
        expect(page.locator("li.habit")).to_have_count(2)

        read_row = page.locator("li.habit").filter(has=page.get_by_text(READ, exact=True))
        read_row.locator('button.day[data-date="2026-10-08"]').click()
        read_row.locator('button.day[data-date="2026-10-07"]').click()
        yesterday = "2026-10-07"
        # 1. bead colour: right after the tick, after real waiting, after the paused clock runs 600 ms
        result["bead_wed7_right_after_tick"] = page.evaluate(BEAD_JS, yesterday)
        result["bead_thu8_ticked_earlier"] = page.evaluate(BEAD_JS, "2026-10-08")
        page.wait_for_timeout(800)
        result["bead_wed7_after_800ms_real_wait"] = page.evaluate(BEAD_JS, yesterday)
        page.clock.run_for(600)
        result["bead_wed7_after_clock_run_600ms"] = page.evaluate(BEAD_JS, yesterday)
        page.screenshot(path=str(out / "probe-1-bead-after-clock-run.png"))

        # 2. backdrop coverage: viewport-only capture with the dialog open
        page.get_by_role("button", name=f"Delete {STRETCH}", exact=True).click()
        expect(page.locator("dialog.dialog")).to_have_attribute("open", "")
        page.wait_for_timeout(300)
        page.clock.run_for(600)
        page.screenshot(path=str(out / "probe-2-dialog-viewport-only.png"), full_page=False)
        result["dialog_open_viewport"] = page.evaluate(
            "() => ({ w: innerWidth, h: innerHeight, scrollH: document.documentElement.scrollHeight, "
            "htmlOverflow: getComputedStyle(document.documentElement).overflow })")

        # 3. focus ring after a mouse delete
        page.get_by_role("button", name="Delete habit", exact=True).click()
        page.wait_for_function("() => !document.querySelector('dialog.dialog').open", polling=100)
        page.clock.run_for(600)
        result["after_mouse_delete_focus"] = page.evaluate(
            "() => ({ id: document.activeElement.id, focusVisible: document.activeElement.matches(':focus-visible'), "
            "outlineStyle: getComputedStyle(document.activeElement).outlineStyle, "
            "outlineWidth: getComputedStyle(document.activeElement).outlineWidth })")
        page.screenshot(path=str(out / "probe-3-after-mouse-delete.png"), full_page=False)
        context.close()
        browser.close()

    (out / "probe-visuals.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
