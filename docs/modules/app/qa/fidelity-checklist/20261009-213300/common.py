"""Shared helpers for the fidelity finder's checklist scripts (scratch, read-only on the product).

Every script opens its own headless Chromium, pins the clock to Thursday 8 October 2026 09:00 local time the way
the plugin harness does, and writes only JSON next to itself.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(r"{workspace}\examples\streaks")
SCRATCH = Path(__file__).resolve().parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:52346/"
FIXED = datetime.fromisoformat("2026-10-08T09:00:00")
SEED = (ROOT / "tests/browser/fidelity/seed-sample.js").read_text(encoding="utf-8")
GOLDEN = {
    "S1": ROOT / "docs/design/today.html",
    "S2": ROOT / "docs/design/today-empty.html",
    "M1": ROOT / "docs/design/delete-dialog.html",
    "ST": ROOT / "docs/design/states.html",
}
VIEWPORTS = {"390": (390, 844), "1280": (1280, 800)}
LAUNCH_ARGS = ["--force-color-profile=srgb", "--hide-scrollbars"]


def launch(pw):
    return pw.chromium.launch(args=LAUNCH_ARGS)


def open_page(browser, url, vp, seed=False, reduced="no-preference", settle=500, clock=True):
    ctx = browser.new_context(
        viewport={"width": vp[0], "height": vp[1]},
        device_scale_factor=1,
        color_scheme="light",
        reduced_motion=reduced,
        locale="en-US",
    )
    page = ctx.new_page()
    if clock:
        page.clock.set_fixed_time(FIXED)
    if seed:
        page.add_init_script(SEED)
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(settle)
    return ctx, page


def golden_url(key):
    return GOLDEN[key].as_uri()


class Rows:
    """Collects PASS or FAIL rows with the measured value next to the expected one."""

    def __init__(self):
        self.rows = []

    def chk(self, row_id, cond, measured, expected, note=""):
        self.rows.append(
            {
                "id": row_id,
                "result": "PASS" if cond else "FAIL",
                "measured": measured,
                "expected": expected,
                "note": note,
            }
        )
        return cond

    def near(self, row_id, value, target, tol, measured_text=None, expected_text=None, note=""):
        ok = abs(value - target) <= tol
        return self.chk(
            row_id,
            ok,
            measured_text if measured_text is not None else value,
            expected_text if expected_text is not None else target,
            note,
        )

    def save(self, name):
        (SCRATCH / name).write_text(json.dumps(self.rows, indent=2, ensure_ascii=False), encoding="utf-8")

    def summary(self):
        passed = sum(1 for r in self.rows if r["result"] == "PASS")
        failed = [r["id"] for r in self.rows if r["result"] == "FAIL"]
        return passed, failed


def save_json(name, data):
    (SCRATCH / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# A serialised copy of a page's body: every element with its attributes, own text, rectangle, all computed
# styles, and the computed styles of its ::before and ::after when they generate a box.
TREE_JS = r"""
() => {
  const SKIP = new Set(["SCRIPT", "STYLE", "LINK", "META", "TITLE"]);
  const round = (v) => Math.round(v * 1000) / 1000;
  function allStyles(el, pseudo) {
    const cs = getComputedStyle(el, pseudo);
    const o = {};
    for (let i = 0; i < cs.length; i++) { const p = cs[i]; o[p] = cs.getPropertyValue(p); }
    return o;
  }
  function ser(el) {
    const r = el.getBoundingClientRect();
    const attrs = {};
    for (const a of el.attributes) attrs[a.name] = a.value;
    let text = "";
    for (const n of el.childNodes) if (n.nodeType === 3) text += n.nodeValue;
    const node = {
      tag: el.tagName.toLowerCase(),
      attrs,
      text: text.replace(/\s+/g, " ").trim(),
      rect: [round(r.x), round(r.y), round(r.width), round(r.height)],
      style: allStyles(el),
      children: [],
    };
    for (const ps of ["::before", "::after"]) {
      const c = getComputedStyle(el, ps).content;
      if (c !== "none" && c !== "normal") node["pseudo" + ps] = allStyles(el, ps);
    }
    for (const c of el.children) if (!SKIP.has(c.tagName)) node.children.push(ser(c));
    return node;
  }
  return { html: allStyles(document.documentElement), body: ser(document.body),
           scroll: [document.documentElement.scrollWidth, document.documentElement.scrollHeight] };
}
"""
