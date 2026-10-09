"""Where are the quotes and the question mark of the delete dialog's title drawn when the name carries bidirectional
controls? Left to right order of: opening quote, the name's visible characters, closing quote, question mark.

Run for each name twice: with the served src/view.js (the fix, FSI and PDI around the name) and with the title line put
back to `Delete "${habitName}"?` in memory (page.route), which is the state before the fix. src/ is not touched.
Names marked "bypass?" contain an isolate-closing character (U+2069) or an isolate opener, to see whether the
isolate itself can be closed from inside the name.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root). Writes nothing.
"""
import pathlib
import sys

sys.path.insert(0, "{workspace}/examples/streaks/docs/modules/app/qa/security/20261009T165000")
from lib import Run, open_app, state_text, ROOT  # noqa: E402

RLO, LRO, RLE, LRE, RLI, LRI, FSI, PDI = (chr(c) for c in (0x202E, 0x202D, 0x202B, 0x202A, 0x2067, 0x2066, 0x2068, 0x2069))
NAMES = {
    "rlo first": RLO + "Reversed text here",
    "rlo in the middle": "Read 20 pages" + RLO + " dleiys .gnp",
    "three rlo": "a" + RLO + "b" + RLO + "c" + RLO,
    "lro": LRO + "abc def",
    "rle": RLE + "abc def",
    "rli": RLI + "abc def",
    "bypass? pdi then rlo": "x" + PDI + RLO + "y z",
    "bypass? two pdi then rlo": "x" + PDI + PDI + RLO + "y z",
    "bypass? rlo then pdi": RLO + "abc" + PDI + "def",
    "bypass? fsi then rlo": FSI + "x" + RLO + "y z",
    "bypass? lri": LRI + "abc def",
    "bypass? paragraph sep U+2029": "x" + chr(0x2029) + RLO + "y z",
    "bypass? line sep U+2028": "x" + chr(0x2028) + RLO + "y z",
    "bypass? next line U+0085": "x" + chr(0x85) + RLO + "y z",
    "bypass? newline": "x" + chr(10) + RLO + "y z",
    "bypass? U+001C": "x" + chr(0x1C) + RLO + "y z",
    "bypass? pdf then rlo": "x" + chr(0x202C) + RLO + "y z",
}

LEFTS = """() => {
  const heading = document.querySelector('#del-title');
  const node = heading.firstChild;
  const rect = (index) => { const r = document.createRange(); r.setStart(node, index); r.setEnd(node, index + 1); return r.getBoundingClientRect(); };
  const text = node.data;
  const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
  const inside = [];
  for (let i = open + 1; i < close; i++) if (rect(i).width > 0) inside.push(Math.round(rect(i).left));
  return { open: Math.round(rect(open).left), inside, close: Math.round(rect(close).left), question: Math.round(rect(question).left), shown: heading.innerText };
}"""


def title_of_page(run, name, patched_view):
    ctx, page, log = open_app(run.browser, run.base, storage=state_text([{"name": name, "done": []}]), viewport=(390, 844))
    try:
        if patched_view is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
            page.reload()
        page.wait_for_selector("li.habit")
        page.locator("button.icon-btn").first.click()
        page.wait_for_selector("dialog[open]")
        return page.evaluate(LEFTS)
    finally:
        ctx.close()


def verdict(spots):
    ok = bool(spots["inside"]) and spots["open"] < min(spots["inside"]) and max(spots["inside"]) < spots["close"] < spots["question"]
    return "quotes in place" if ok else "QUOTES MOVED"


def main():
    view_text = (pathlib.Path(ROOT) / "src" / "view.js").read_text(encoding="utf-8")
    fixed_line = '$("#del-title").textContent = `Delete "' + chr(92) + "u{2068}${habitName}" + chr(92) + 'u{2069}"?`;'
    assert view_text.count(fixed_line) == 1, "the fixed title line is not in src/view.js"
    unfixed_view = view_text.replace(fixed_line, '$("#del-title").textContent = `Delete "${habitName}"?`;')
    with Run() as run:
        for label, name in NAMES.items():
            before = title_of_page(run, name, unfixed_view)
            after = title_of_page(run, name, None)
            print(f"  {label:28s} before the fix: {verdict(before):15s} open={before['open']} name={before['inside'][:3]}.. close={before['close']} ?={before['question']}")
            print(f"  {'':28s} with the fix:    {verdict(after):15s} open={after['open']} name={after['inside'][:3]}.. close={after['close']} ?={after['question']}", flush=True)
    print("done")


if __name__ == "__main__":
    main()
