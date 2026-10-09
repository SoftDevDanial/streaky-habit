"""Regression QA: the gap of ST-06 (app qa.md, "The sheet's S5 note ... 32 above the empty message").

The first checklist run read margin-top of p.empty (0px on both sides, the gap is not a margin of the message):
the note carries `margin-bottom: var(--space-7)` (src/styles.css, .note). This script measures the gap itself,
from the bottom edge of the note to the top edge of the empty message, live (at 360 x 780, the app in the
unreadable-data state reached by seeding "{" and loading) and on the sheet's S5 frame, and the note's
computed margin-bottom. Output: st06-gap.json in --out.
Usage: python st06_gap.py --base-url http://127.0.0.1:<port>/ --out <folder>
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "tests" / "browser"))

from playwright.sync_api import expect, sync_playwright  # noqa: E402

from conftest import open_app  # noqa: E402

GAP_JS = """(pair) => {
  const [noteSel, emptySel] = pair;
  const note = document.querySelector(noteSel);
  const empty = document.querySelector(emptySel);
  const n = note.getBoundingClientRect(), e = empty.getBoundingClientRect();
  return { gap: Math.round((e.top - n.bottom) * 100) / 100, noteMarginBottom: getComputedStyle(note).marginBottom,
           emptyMarginTop: getComputedStyle(empty).marginTop };
}"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        context, page = open_app(browser, viewport=(360, 780), reduced_motion="reduce", storage="{", base_url=base)
        expect(page.locator("div.note")).to_be_visible()
        result["live"] = page.evaluate(GAP_JS, ["div.note", "p.empty"])
        context.close()

        context = browser.new_context(viewport={"width": 360, "height": 780}, device_scale_factor=1, color_scheme="light", reduced_motion="reduce")
        sheet = context.new_page()
        sheet.goto(base + "docs/design/states.html")
        result["sheet"] = sheet.evaluate(GAP_JS, ["div.note", "p.empty"])
        context.close()
        browser.close()
    result["pass"] = result["live"]["gap"] == 32 and result["live"]["noteMarginBottom"] == "32px"
    (out / "st06-gap.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
