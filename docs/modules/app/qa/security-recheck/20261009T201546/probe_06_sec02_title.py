"""SEC-02 as fixed: the isolate around the name in the delete dialog's title, and the source bytes.

Part 1 (bytes): src/*.js, src/styles.css, index.html, tests/browser/*.py, tests/browser/fidelity/*.js are scanned for raw
bidirectional format characters (U+061C, U+200E, U+200F, U+202A-U+202E, U+2066-U+2069) and for every non-ASCII byte in
the two changed source files. The escape text for U+2068 and U+2069 must appear once each in src/view.js.
Part 2 (geometry): where the opening quote, the visible characters of the name, the closing quote and the question mark
are drawn, in reading order (line first, then left to right), with the served src/view.js (the fix) and with the title
line put back to the unfixed form in memory (page.route, nothing on disk changes). The five names are the ones of the
suite, plus more, plus two names that are the accepted residual (an isolate closer inside the name), shown only to
confirm the recorded behaviour and not to file it again.
Part 3: the title stays one text node with no child element, the stored name is unchanged, the trash button's accessible
name has no mark, the page does not scroll sideways at 320, 360 and 390 with a long override name that wraps.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import re

from chars import BS, FSI, LRE, LRI, LRO, MARHABA, OLAM, PDI, RLE, RLI, RLO, SHALOM, chars
from lib import ROOT, Run, open_app, state_text

BIDI = re.compile("[" + chars(0x061C, 0x200E, 0x200F, 0x202A) + "-" + chr(0x202E) + chr(0x2066) + "-" + chr(0x2069) + "]")
ESC_FSI = BS + "u{2068}"
ESC_PDI = BS + "u{2069}"

FIVE = {
    "rlo first": RLO + "Reversed text here",
    "rlo in the middle": "Read 20 pages" + RLO + " dleiys .gnp",
    "three rlo": "a" + RLO + "b" + RLO + "c" + RLO,
    "rle": RLE + "abc def",
    "rli": RLI + "abc def",
}
MORE = {
    "lro": LRO + "abc def",
    "lre": LRE + "abc def",
    "lri": LRI + "abc def",
    "rlo then text then rlo": RLO + "ab" + RLO + "cd",
    "40 x rlo (no visible name)": RLO * 40,
    "rlo + 30 letters": RLO + "x" * 30,
    "hebrew name": SHALOM + " " + OLAM,
    "arabic then latin": MARHABA + " hello",
}
RESIDUAL = {
    "RESIDUAL (accepted) pdi then rlo": "x" + PDI + RLO + "y z",
    "RESIDUAL (accepted) U+2029 then rlo": "x" + chr(0x2029) + RLO + "y z",
}

# Reading-order key of a character: its line (top relative to the first line, in line heights) times 100000, plus its left.
KEYS = """() => {
  const heading = document.querySelector('#del-title');
  const node = heading.firstChild;
  const style = getComputedStyle(heading);
  const lineHeight = parseFloat(style.lineHeight);
  const base = heading.getBoundingClientRect().top;
  const rect = (index) => { const r = document.createRange(); r.setStart(node, index); r.setEnd(node, index + 1); return r.getBoundingClientRect(); };
  const key = (r) => Math.round((r.top - base) / lineHeight) * 100000 + Math.round(r.left);
  const text = node.data;
  const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
  const inside = [];
  for (let i = open + 1; i < close; i++) { const r = rect(i); if (r.width > 0) inside.push(key(r)); }
  return { nodes: heading.childNodes.length, childElements: heading.children.length, open: key(rect(open)), inside,
    close: key(rect(close)), question: key(rect(question)), text };
}"""


def part1(say):
    say("== Part 1: source bytes ==")
    files = [p for pat in ("src/*.js", "src/styles.css", "index.html", "tests/browser/*.py", "tests/browser/fidelity/*.js") for p in sorted(ROOT.glob(pat))]
    hits = {}
    for p in files:
        found = BIDI.findall(p.read_bytes().decode("utf-8"))
        if found:
            hits[str(p.relative_to(ROOT))] = [f"U+{ord(c):04X}" for c in found]
    say(f"  files scanned for raw bidi format characters: {len(files)}; files with any: {hits if hits else 'none'}")
    for name in ("src/app.js", "src/view.js"):
        raw = (ROOT / name).read_bytes()
        say(f"  {name}: {len(raw)} bytes, non-ASCII bytes: {sum(1 for b in raw if b > 127)}")
    view = (ROOT / "src/view.js").read_text(encoding="utf-8")
    say(f"  src/view.js holds the escape text {ESC_FSI} {view.count(ESC_FSI)} time(s) and {ESC_PDI} {view.count(ESC_PDI)} time(s)")
    line = [l for l in view.splitlines() if "#del-title" in l and "textContent" in l]
    say(f"  title line: {line[0].strip() if line else None}")
    fidelity = (ROOT / "tests/browser/fidelity/open-delete-dialog.js").read_text(encoding="utf-8")
    say(f"  fidelity script escapes: {ESC_FSI} {fidelity.count(ESC_FSI)}, {ESC_PDI} {fidelity.count(ESC_PDI)}")


def title_spots(run, name, patched_view=None, vp=(390, 844)):
    ctx, page = open_app(run.browser, run.base, vp, False, seed=state_text([{"name": name, "done": []}]))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        spots = page.evaluate(KEYS)
        spots["stored"] = page.evaluate("() => localStorage.getItem('streaks.state')")
        spots["trash_label"] = page.locator("button.icon-btn").first.get_attribute("aria-label")
        spots["scroll_width"] = page.evaluate("() => document.documentElement.scrollWidth")
        return spots
    finally:
        ctx.close()


def ok(spots):
    inside = spots["inside"]
    if not inside:
        return spots["open"] < spots["close"] < spots["question"]
    return spots["open"] < min(inside) and max(inside) < spots["close"] < spots["question"]


def fixed_title_line():
    return '$("#del-title").textContent = `Delete "' + ESC_FSI + "${habitName}" + ESC_PDI + '"?`;'


def main():
    with Run() as run:
        say = run.say
        part1(say)
        view = (ROOT / "src/view.js").read_text(encoding="utf-8")
        assert view.count(fixed_title_line()) == 1, "the fixed title line is not in src/view.js"
        unfixed = view.replace(fixed_title_line(), '$("#del-title").textContent = `Delete "${habitName}"?`;')
        say("== Part 2: where the quotes are drawn (390x844); 'in place' = open quote < name < close quote < question mark, in reading order ==")
        counts = {"five_fixed_in_place": 0, "five_unfixed_moved": 0}
        for group, names in (("the five names of the suite", FIVE), ("more", MORE), ("accepted residual, for the record", RESIDUAL)):
            say(f"  -- {group} --")
            for label, name in names.items():
                before = title_spots(run, name, unfixed)
                after = title_spots(run, name)
                if group.startswith("the five"):
                    counts["five_fixed_in_place"] += ok(after)
                    counts["five_unfixed_moved"] += not ok(before)
                say(f"    {label:36s} unfixed: {'in place' if ok(before) else 'QUOTES MOVED':12s} | fixed: {'in place' if ok(after) else 'QUOTES MOVED':12s} (open {after['open']}, name {after['inside'][:1]}..{after['inside'][-1:]}, close {after['close']}, ? {after['question']}); one text node, no child element: {after['nodes'] == 1 and after['childElements'] == 0}")
        say(f"  five suite names: {counts['five_fixed_in_place']} of 5 in place with the fix, {counts['five_unfixed_moved']} of 5 moved without it")
        say("== Part 3: other properties of the title ==")
        for vp in ((320, 568), (360, 640), (390, 844)):
            s = title_spots(run, RLO + "x" * 36 + RLO, None, vp)
            say(f"  {vp[0]}x{vp[1]} wrapping override name: scrollWidth {s['scroll_width']} (viewport {vp[0]}), quotes in place in reading order: {ok(s)}")
        s = title_spots(run, "Read" + RLO + " it", None)
        say(f"  stored text for 'Read<RLO> it' holds no FSI/PDI (the marks are display only): {FSI not in s['stored'] and PDI not in s['stored']}")
        say(f"  trash button aria-label has no FSI/PDI: {FSI not in s['trash_label'] and PDI not in s['trash_label']} ({s['trash_label']!r})")
        ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": "Plain name", "done": []}]))
        try:
            page.locator("button.icon-btn").first.click()
            page.wait_for_selector("dialog[open]")
            snapshot = page.locator("dialog").aria_snapshot()
            say(f"  dialog accessible name (aria snapshot first line, repr): {snapshot.splitlines()[0]!r}")
            say(f"  page errors: {page.errors}")
        finally:
            ctx.close()
    run.finish("probe_06")


if __name__ == "__main__":
    main()
