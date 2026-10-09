"""SEC-06 completeness: does ANY single character c of the Basic Multilingual Plane still move the title's quotes?

The spec note says that with the bidi format characters taken out nothing left in the name can close or open an isolate. This
sweeps every BMP code point c (the surrogates D800 to DFFF excluded, they are not characters) through the real
`openDeleteDialog` of the served page, in three name shapes, and measures where the opening quote, the visible characters of
the name, the closing quote and the question mark are drawn (reading order: line, then left edge).
  A: "x" c RLO "y z"           (the SEC-02 residual shape: a closer or separator, then an override)
  B: ALEF c "abc"              (the SEC-06 shape: a right-to-left letter, then c, then Latin)
  G: ALEF c "abc" ALEF         (c between right-to-left, left-to-right and right-to-left letters)
Two trees: BASE (commit 8e655e8, the title before the fix: its view.js put back in memory with page.route) and the working tree
(the fix). Expected: the fix moves nothing, BASE moves the code points of the stripped set (and any others, which would show a
trigger the strip list lacks).
Left edges are compared exactly, not rounded: a first run that rounded them to whole pixels flagged U+070F (SYRIAC ABBREVIATION
MARK, a 0.4 px wide glyph) in a few shapes, and probe_13 showed the rounded edges of the mark and of the next quote were equal
while the exact edges were in order, so the flag was a rounding artefact and the picture shows the quotes in place.
`import('/src/view.js')` in the page is the same module instance the app uses. The dialog stays open: showModal on an open
modal dialog is a no-op, so only the title text changes between names. Nothing is stored or saved.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
RECHECK = pathlib.Path(__file__).resolve().parents[2] / "security-recheck" / "20261009T201546"
sys.path.insert(0, str(RECHECK))

from lib import ROOT, Run, open_app, state_text  # noqa: E402

STEP = 4096

PRELUDE = """
  const view = await import('/src/view.js');
  const heading = document.querySelector('#del-title');
  const lineHeight = parseFloat(getComputedStyle(heading).lineHeight);
  const ALEF = String.fromCharCode(0x05D0), RLO = String.fromCharCode(0x202E), LRI = String.fromCharCode(0x2066);
  const inPlace = () => {
    const node = heading.firstChild;
    const base = heading.getBoundingClientRect().top;
    const place = (i) => {
      const r = document.createRange();
      r.setStart(node, i);
      r.setEnd(node, i + 1);
      const b = r.getBoundingClientRect();
      return { width: b.width, key: Math.round((b.top - base) / lineHeight) * 100000 + b.left };
    };
    const text = node.data;
    const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
    const inside = [];
    for (let i = open + 1; i < close; i++) { const p = place(i); if (p.width > 0) inside.push(p.key); }
    const o = place(open).key, c = place(close).key, q = place(question).key;
    return inside.length ? (o < Math.min(...inside) && Math.max(...inside) < c && c < q) : (o < c && c < q);
  };
"""

SWEEP = "async ([first, last]) => {" + PRELUDE + """
  const shapes = {
    A: (c) => 'x' + c + RLO + 'y z',
    B: (c) => ALEF + c + 'abc',
    G: (c) => ALEF + c + 'abc' + ALEF,
  };
  const moved = { A: [], B: [], G: [] };
  let swept = 0;
  for (let code = first; code < last; code++) {
    if (code >= 0xD800 && code <= 0xDFFF) continue;
    swept++;
    const c = String.fromCharCode(code);
    for (const [shape, make] of Object.entries(shapes)) {
      view.openDeleteDialog(make(c));
      if (!inPlace()) moved[shape].push(code);
    }
  }
  return { swept, moved };
}"""


def ranges(codes):
    """[1, 2, 3, 7] as 'U+0001-U+0003 U+0007'."""
    out, start, previous = [], None, None
    for code in codes:
        if start is None:
            start = previous = code
        elif code == previous + 1:
            previous = code
        else:
            out.append((start, previous))
            start = previous = code
    if start is not None:
        out.append((start, previous))
    return " ".join(f"U+{a:04X}" if a == b else f"U+{a:04X}-U+{b:04X}" for a, b in out)


BASE = "8e655e8"  # the commit before the fix (HEAD moved to the fix, so the base is named)


def committed_view():
    return subprocess.run(["git", "show", f"{BASE}:src/view.js"], cwd=str(ROOT), capture_output=True, check=True).stdout.decode("utf-8")


def sweep(run, label, patched_view):
    ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": "Plain", "done": []}]))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        totals = {"A": [], "B": [], "G": []}
        swept = 0
        for first in range(0, 0x10000, STEP):
            result = page.evaluate(SWEEP, [first, min(first + STEP, 0x10000)])
            swept += result["swept"]
            for shape, codes in result["moved"].items():
                totals[shape].extend(codes)
        run.say(f"  {label}: {swept} code points swept in 3 shapes; page errors: {page.errors}")
        for shape, codes in totals.items():
            run.say(f"    shape {shape}: {len(codes)} code points move the quotes: {ranges(codes) if codes else 'none'}")
        return totals
    finally:
        ctx.close()


EXTRA = "async (names) => {" + PRELUDE + """
  const bad = [];
  names.forEach((name, index) => {
    view.openDeleteDialog(name);
    if (!inPlace()) bad.push(index);
  });
  return bad;
}"""


def first_name_shapes(c1):
    """Hand-written shapes around one character, for the one outlier of the sweep (U+070F)."""
    alef, rlo, lri = chr(0x05D0), chr(0x202E), chr(0x2066)
    return {
        "c alone": c1, "x c": "x" + c1, "c x": c1 + "x", "alef c": alef + c1, "c alef": c1 + alef, "x c y z": "x" + c1 + "y z",
        "alef c abc alef": alef + c1 + "abc" + alef, "x c alef y": "x" + c1 + alef + "y", "5 x c": c1 * 5, "ab c cd c e": "ab" + c1 + " cd" + c1 + "e",
        "alef c c abc": alef + c1 + c1 + "abc", "c alef abc": c1 + alef + "abc",
        "x c RLO y z (override kept in the name)": "x" + c1 + rlo + "y z", "alef c LRI abc (opener kept in the name)": alef + c1 + lri + "abc",
    }


def evaluate_names(page, names):
    """Indices of the names (a list of str) that are NOT in place, in batches."""
    bad = []
    for first in range(0, len(names), STEP):
        bad.extend(first + i for i in page.evaluate(EXTRA, names[first:first + STEP]))
    return bad


def second_round(run, label, patched_view):
    """The 14 hand-written shapes around U+070F, and a pair sweep: every BMP code point of a class that can affect ordering
    (B, S, WS, BN, AN, AL, R, NSM) in front of each of six companions, in two shapes."""
    import unicodedata

    ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": "Plain", "done": []}]))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        shapes = first_name_shapes(chr(0x070F))
        bad = evaluate_names(page, list(shapes.values()))
        run.say(f"  {label}: U+070F in {len(shapes)} hand-written shapes, out of place: {[list(shapes)[i] for i in bad] if bad else 'none'}")
        classes = {"B", "S", "WS", "BN", "AN", "AL", "R", "NSM"}
        firsts = [c for c in range(0x10000) if not 0xD800 <= c <= 0xDFFF and unicodedata.bidirectional(chr(c)) in classes]
        companions = [chr(0x05D0), "a", "1", "-", chr(0x070F), " "]
        names, labels = [], []
        for c in firsts:
            for companion in companions:
                names.append("x" + chr(c) + companion + "y z")
                labels.append(("x c d y z", c, companion))
                names.append(chr(0x05D0) + chr(c) + companion + "abc")
                labels.append(("alef c d abc", c, companion))
        bad = evaluate_names(page, names)
        run.say(f"  {label}: pair sweep, {len(firsts)} code points of classes {sorted(classes)} x {len(companions)} companions x 2 shapes = {len(names)} names; out of place: {len(bad)}")
        for i in bad[:30]:
            shape, c, companion = labels[i]
            run.say(f"    {shape}: U+{c:04X} + U+{ord(companion):04X}")
        run.say(f"  page errors: {page.errors}")
        return len(bad)
    finally:
        ctx.close()


def main():
    head_view = committed_view()
    with Run() as run:
        run.say("== every BMP code point c through the real openDeleteDialog, quotes in reading order ==")
        head = sweep(run, f"{BASE} (title without the strip)", head_view)
        fixed = sweep(run, "working tree (with the strip)", None)
        stripped = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {0x0085, 0x2029} | set(range(0x001C, 0x001F))
        outside = sorted({c for codes in head.values() for c in codes} - stripped)
        run.say(f"  code points that move the quotes at {BASE} and are NOT in the stripped set: {ranges(outside) if outside else 'none'}")
        run.say(f"  code points that still move the quotes with the fix: {sum(len(v) for v in fixed.values())}")
        run.say("== second round: U+070F shapes and a pair sweep ==")
        second_round(run, f"{BASE} (title without the strip)", head_view)
        second_round(run, "working tree (with the strip)", None)


if __name__ == "__main__":
    main()
