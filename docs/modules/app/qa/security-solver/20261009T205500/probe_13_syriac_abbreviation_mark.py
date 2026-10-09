"""U+070F SYRIAC ABBREVIATION MARK: the one code point outside the stripped set that probe_12 flagged.

The first run of probe_12 (it rounded left edges to whole pixels) flagged names that hold U+070F alone, at the start or at the end
as "out of place", on the working tree (with the strip) and on the commit before the fix. This looks at the exact numbers and at
the picture, to tell a real reordering of the title's quotes from a rounding artefact of the mark's 0.4 px wide glyph (it is a
bidi class AL format character whose glyph is a small bar). Result: the quotes are in place (see evidence.md); the artefact came
from rounding, and probe_12 now compares exact edges.
For each name: the reading-order positions of the opening quote, the visible name characters, the closing quote and the
question mark, the width of each character's box, and a screenshot of the dialog in shots/ (written by Playwright).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
RECHECK = HERE.parents[1] / "security-recheck" / "20261009T201546"
sys.path.insert(0, str(RECHECK))

from lib import Run, open_app, state_text  # noqa: E402
from probe_06_sec02_title import ok  # noqa: E402

SAM = chr(0x070F)
ALEF = chr(0x05D0)
NAMES = {
    "sam-alone": SAM,
    "x-sam": "x" + SAM,
    "sam-x": SAM + "x",
    "x-sam-yz": "x" + SAM + "y z",
    "alef-sam-abc": ALEF + SAM + "abc",
    "read-sam-pages": "Read" + SAM + " pages",
}

DETAIL = """() => {
  const heading = document.querySelector('#del-title');
  const node = heading.firstChild;
  const lineHeight = parseFloat(getComputedStyle(heading).lineHeight);
  const base = heading.getBoundingClientRect().top;
  const text = node.data;
  const out = [];
  for (let i = 0; i < text.length; i++) {
    const r = document.createRange();
    r.setStart(node, i);
    r.setEnd(node, i + 1);
    const b = r.getBoundingClientRect();
    out.push([text.charCodeAt(i).toString(16).padStart(4, '0'), Math.round(b.left * 10) / 10, Math.round(b.width * 10) / 10]);
  }
  return out;
}"""


def main():
    shots = HERE / "shots"
    with Run() as run:
        say = run.say
        for label, name in NAMES.items():
            ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": name, "done": []}]))
            try:
                page.locator("button.icon-btn").first.click()
                page.wait_for_selector("dialog[open]")
                page.locator("dialog").evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")
                detail = page.evaluate(DETAIL)
                shots.mkdir(exist_ok=True)
                page.locator("dialog").screenshot(path=str(shots / f"sec06-sam-{label}.png"))
                say(f"  {label}: [code, left, width] per character of the title: {detail}")
            finally:
                ctx.close()
    # No Run.finish: it would write into the re-check folder.


if __name__ == "__main__":
    main()
