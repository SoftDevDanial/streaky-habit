"""Bidi and control characters in the v1.1.0 name sinks, and layout under hostile names (SEC-02 and SEC-06 family).

Part 1  For each name, in P1 the tick's .tname and its .tstat ("Current ... Best ..."), and in P2 #yr-title with
        the stats below it: does any part of the text that follows the name move? Measured with Range rects on
        the characters of .tstat and .yr-stats (reading order = left edges increasing for these LTR strings), and
        the computed display and unicode-bidi of the elements that hold the name. M1's title is checked as well.
Part 2  At 360 x 780 with 12 hostile names: scrollWidth of the page with K1, P1, P2 and M1 showing.
Usage: python -B probe_05_bidi_layout.py [chromium] [webkit]
"""
import json
import time

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"
RLO, LRO, RLE, PDF, LRI, RLI, FSI, PDI, PS = "‮", "‭", "‫", "‬", "⁦", "⁧", "⁨", "⁩", " "
ALEF, SHALOM = "א", "שלום"
NAMES = {
    "RLO prefix": RLO + "Reversed text here",
    "RLO middle": "Read 20 pages" + RLO + "dleiys gnp",
    "RLE": RLE + "abc def",
    "LRI after alef": ALEF + LRI + "abc",
    "FSI after alef": ALEF + FSI + "abc",
    "PDI then RLO": "x" + PDI + RLO + "yz",
    "U+2029 then RLO": "x" + PS + RLO + "yz",
    "U+0085 then RLO": "x\u0085" + RLO + "yz",
    "40 x RLO": RLO * 40,
    "Hebrew word": SHALOM + " abc",
    "plain control": "Plain name",
}
DONE = ["2026-10-10", "2026-10-09", "2026-09-07", "2026-09-08"]
CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"

ORDER_JS = """(sel) => {
  const el = document.querySelector(sel);
  const text = el.textContent;
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const lefts = [];
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    for (let i = 0; i < node.length; i++) {
      if (/\\s/.test(node.data[i])) continue;
      const r = document.createRange(); r.setStart(node, i); r.setEnd(node, i + 1);
      const rect = r.getBoundingClientRect(); lefts.push([Math.round(rect.top), rect.left]);
    }
  }
  let inOrder = true;
  for (let i = 1; i < lefts.length; i++) if (lefts[i][0] === lefts[i - 1][0] && lefts[i][1] < lefts[i - 1][1] - 0.5) inOrder = false;
  return { text, inOrder };
}"""

STYLE_JS = """(sel) => { const s = getComputedStyle(document.querySelector(sel)); return s.display + '/' + s.unicodeBidi; }"""

TITLE_ORDER_JS = """() => {
  const h = document.querySelector('#del-title');
  const node = h.firstChild, data = node.data;
  const at = (i) => { const r = document.createRange(); r.setStart(node, i); r.setEnd(node, i + 1); return r.getBoundingClientRect().left; };
  const open = data.indexOf('"'), close = data.lastIndexOf('"'), q = data.lastIndexOf('?');
  return at(open) < at(close) && at(close) < at(q);
}"""


def key(page, sel, opens):
    page.locator(sel).first.focus()
    page.keyboard.press("Enter")
    page.wait_for_function(f"() => document.querySelector('{opens}').open", timeout=5000)


def esc(s):
    n = sum(1 for c in s.console if c.startswith("log: closed:"))
    s.page.keyboard.press("Escape")
    deadline = time.time() + 5
    while sum(1 for c in s.console if c.startswith("log: closed:")) == n:
        if time.time() > deadline:
            raise RuntimeError("close not seen, gave up after 5 s")
        s.page.wait_for_timeout(20)


def run(engine, base):
    out = {"engine": engine}
    with sync_playwright() as p:
        browser = lib.launch(p, engine)
        out["version"] = browser.version
        try:
            for label, name in NAMES.items():
                state = lib.encode([{"name": name, "done": DONE}, {"name": "Second", "done": DONE}])
                s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=state, clock=NOON, init=[CLOSE_LOGGER], route_log=False)
                try:
                    page = s.page
                    r = {}
                    key(page, "section.band button.hc[aria-current=date]", "dialog.dlg-day")
                    r["p1 tstat"] = page.evaluate(ORDER_JS, "dialog.dlg-day ul.day-list li:first-child .tstat")
                    r["p1 second tick"] = page.evaluate(ORDER_JS, "dialog.dlg-day ul.day-list li:nth-child(2) .tname")["inOrder"]
                    r["tick, tname styles"] = [page.evaluate(STYLE_JS, "dialog.dlg-day button.tick"), page.evaluate(STYLE_JS, "dialog.dlg-day .tname")]
                    esc(s)
                    key(page, "ul.rows > li.row button.btn-year", "dialog.dlg-year")
                    r["p2 stats"] = page.evaluate(ORDER_JS, "dialog.dlg-year p.yr-stats")
                    r["p2 sub"] = page.evaluate(ORDER_JS, "#yr-sub")["inOrder"]
                    r["h2 style"] = page.evaluate(STYLE_JS, "#yr-title")
                    key(page, "dialog.dlg-year button.btn-del", "dialog.dlg-del")
                    r["m1 quotes in place"] = page.evaluate(TITLE_ORDER_JS)
                    esc(s)
                    esc(s)
                    r["row stats"] = page.evaluate(ORDER_JS, "ul.rows > li.row:first-child p.stats")["inOrder"]
                    r["errors"] = s.errors
                    out[label] = r
                finally:
                    s.close()
            # Part 2, layout at 360 x 780
            wide = ["W" * 40, "Ｗ" * 40, "x" + "́" * 39, "\U0001F468‍\U0001F469‍\U0001F467" * 5,
                    "a" * 40, "-" * 40, "1" * 40, SHALOM * 10, "​" * 40, RLO * 40, "ا" * 40, "一" * 40]
            state = lib.encode([{"name": n, "done": DONE} for n in wide])
            s = lib.Session(browser, base, viewport=(360, 780), seed_js=lib.SEED_TEXT, seed_arg=state, clock=NOON, init=[CLOSE_LOGGER], route_log=False)
            try:
                page = s.page
                sw = {"K1": page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]")}
                key(page, "button.ov-btn", "dialog.dlg-ov")
                key(page, "dialog.dlg-ov button.hc[aria-current=date]", "dialog.dlg-day")
                sw["P1 over P3"] = page.evaluate("() => [document.documentElement.scrollWidth, Math.round(document.querySelector('dialog.dlg-day .dlg-box').getBoundingClientRect().right)]")
                esc(s)
                esc(s)
                for i in (0, 1, 3, 9):
                    key(page, f"ul.rows > li.row:nth-child({i + 1}) button.btn-year", "dialog.dlg-year")
                    key(page, "dialog.dlg-year button.btn-del", "dialog.dlg-del")
                    sw[f"P2 and M1, name {i + 1}"] = page.evaluate("""() => [document.documentElement.scrollWidth,
                      Math.round(document.querySelector('dialog.dlg-year .dlg-box').getBoundingClientRect().right),
                      Math.round(document.querySelector('dialog.dlg-del .dlg-box').getBoundingClientRect().right),
                      Math.round(document.querySelector('dialog.dlg-del button.btn-danger').getBoundingClientRect().right)]""")
                    esc(s)
                    esc(s)
                sw["errors"] = s.errors
                out["layout 360x780"] = sw
            finally:
                s.close()
        finally:
            browser.close()
    return out


def main():
    proc, port, _ = lib.start_server()
    try:
        for engine in lib.engines_from_argv():
            for k, v in run(engine, f"http://127.0.0.1:{port}/").items():
                print(f"{k}: {json.dumps(v, ensure_ascii=True)}", flush=True)
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
