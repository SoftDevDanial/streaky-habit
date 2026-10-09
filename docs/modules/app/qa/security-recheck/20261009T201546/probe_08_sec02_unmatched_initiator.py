"""SEC-02 hunt: a name that holds an isolate INITIATOR (U+2066 LRI, U+2067 RLI, U+2068 FSI) with no closer.

Why: the fix writes `Delete "`, FSI, name, PDI, `"?`. The PDI closes the NEAREST open isolate, so an unmatched initiator
inside the name takes the title's own PDI and leaves the title's FSI open to the end of the line. If a strong
right-to-left letter comes before the initiator, the title's isolate resolves right to left, and the closing quote and the
question mark (neutral characters at its end) are drawn to the LEFT of the name. The solver's probe_03 tried initiators only
after a Latin letter, where the isolate stays left to right.
Each name is measured with the fix (served src/view.js) and with the title line put back to the unfixed form in memory
(page.route, nothing on disk changes). Positions are in reading order (line, then left to right); 'in place' means
open quote < name < close quote < question mark.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
from chars import ALEF, BS, LRI, MEEM, PDI, RLI, RLO, FSI, SHALOM
from lib import ROOT, Run, open_app, state_text

NAMES = {
    "alef + LRI + abc": ALEF + LRI + "abc",
    "alef + RLI + abc": ALEF + RLI + "abc",
    "alef + FSI + abc": ALEF + FSI + "abc",
    "shalom + LRI (initiator last)": SHALOM + LRI,
    "shalom + space + abc + LRI": SHALOM + " abc" + LRI,
    "meem + LRI + x": MEEM + LRI + "x",
    "alef + LRI + abc + RLO (override too)": ALEF + LRI + "abc" + RLO,
    "CONTROL latin + LRI + alef": "x" + LRI + ALEF,
    "CONTROL alef + LRI + abc + PDI (balanced pair)": ALEF + LRI + "abc" + PDI,
    "CONTROL alef only": ALEF,
    "CONTROL shalom + space + abc": SHALOM + " abc",
    "KNOWN RESIDUAL x + PDI + RLO + y z": "x" + PDI + RLO + "y z",
}

KEYS = """() => {
  const heading = document.querySelector('#del-title');
  const node = heading.firstChild;
  const lineHeight = parseFloat(getComputedStyle(heading).lineHeight);
  const base = heading.getBoundingClientRect().top;
  const rect = (index) => { const r = document.createRange(); r.setStart(node, index); r.setEnd(node, index + 1); return r.getBoundingClientRect(); };
  const key = (r) => Math.round((r.top - base) / lineHeight) * 100000 + Math.round(r.left);
  const text = node.data;
  const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
  const inside = [];
  for (let i = open + 1; i < close; i++) { const r = rect(i); if (r.width > 0) inside.push(key(r)); }
  return { open: key(rect(open)), inside, close: key(rect(close)), question: key(rect(question)) };
}"""


def spots(run, name, patched_view=None, vp=(390, 844)):
    ctx, page = open_app(run.browser, run.base, vp, False, seed=state_text([{"name": name, "done": []}]))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        s = page.evaluate(KEYS)
        s["stored_same"] = page.evaluate("() => JSON.parse(localStorage.getItem('streaks.state')).habits[0].name") == name
        s["page_errors"] = list(page.errors)
        return s
    finally:
        ctx.close()


def ok(s):
    inside = s["inside"]
    if not inside:
        return s["open"] < s["close"] < s["question"]
    return s["open"] < min(inside) and max(inside) < s["close"] < s["question"]


def main():
    with Run() as run:
        say = run.say
        view = (ROOT / "src/view.js").read_text(encoding="utf-8")
        fixed_line = '$("#del-title").textContent = `Delete "' + BS + "u{2068}${habitName}" + BS + 'u{2069}"?`;'
        assert view.count(fixed_line) == 1
        unfixed = view.replace(fixed_line, '$("#del-title").textContent = `Delete "${habitName}"?`;')
        say("== unmatched isolate initiators in the name, 390x844 ==")
        for label, name in NAMES.items():
            before = spots(run, name, unfixed)
            after = spots(run, name)
            say(f"  {label:48s} unfixed: {'in place' if ok(before) else 'QUOTES MOVED':12s} | fixed: {'in place' if ok(after) else 'QUOTES MOVED':12s} fixed positions open {after['open']}, name {after['inside'][:1]}..{after['inside'][-1:]}, close {after['close']}, ? {after['question']}; name stored unchanged: {after['stored_same']}; page errors: {after['page_errors']}")
    run.finish("probe_08")


if __name__ == "__main__":
    main()
