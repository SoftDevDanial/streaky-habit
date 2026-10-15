"""T3, R24, R26. Hostile names, planted in storage and typed, through every v1.1.0 sink, in each engine.

Sinks: row h3, the bin's, Year's and Done today's names, P1's tick (name and .tname), P2's #yr-title, M1's
title (opened from P2). Also: element census, on* attributes, JS dialogs, page errors, CSP violations,
requests, clipboard markers, and window's own properties against a blank same-origin page with the same clock.
Run 2: every popup is driven by the keyboard, and each Escape waits until the popup's `close` event has run
(a capture listener logs it), so the app is never driven faster than its close events.
Usage: python -B probe_01_names.py [chromium] [webkit]
"""
import json
import time

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"
NAMES = [
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(2)>",
    '"><script>alert(3)</script>',
    "javascript:alert(4)",
    "<style>*{display:none}</style>",
    '<iframe srcdoc="<b>x</b>">',
    "__proto__",
    "constructor",
    'x"],body,[a="',
    "&lt;b&gt;bold&lt;/b&gt;",
    "<base href=//evil.invalid/>",
    "{{7*7}} ${7*7} %s %n",
]
DONE = ["2026-10-10", "2026-10-09", "2026-10-08", "2026-09-22", "2025-10-10"]

CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"

CENSUS_JS = """() => {
  const count = (s) => document.querySelectorAll(s).length;
  const onAttrs = [];
  for (const el of document.querySelectorAll('*')) for (const a of el.attributes) if (/^on/i.test(a.name)) onAttrs.push(el.tagName + ' ' + a.name);
  return { img: count('img'), script: count('script'), iframe: count('iframe'), style: count('style'), a: count('a'),
           base: count('base'), object: count('object'), embed: count('embed'), link: count('link'), meta: count('meta'),
           form: count('form'), onAttrs, baseURI: document.baseURI, title: document.title };
}"""

WINDOW_KEYS_JS = "() => Object.getOwnPropertyNames(window).sort()"

ROWS_JS = """() => Array.from(document.querySelectorAll('ul.rows > li.row')).map((row) => {
  const h3 = row.querySelector('h3');
  return { h3: h3.textContent, h3Children: h3.childElementCount,
    bin: row.querySelector('button.btn-bin').getAttribute('aria-label'),
    year: row.querySelector('button.btn-year').getAttribute('aria-label'),
    done: row.querySelector('button.btn-done').getAttribute('aria-label') };
})"""

TICKS_JS = """() => Array.from(document.querySelectorAll('dialog.dlg-day ul.day-list button.tick')).map((b) => ({
  label: b.getAttribute('aria-label'), tname: b.querySelector('.tname').textContent,
  tnameChildren: b.querySelector('.tname').childElementCount }))"""


def press(page, locator, opens):
    locator.focus()
    page.keyboard.press("Enter")
    page.wait_for_function(f"() => document.querySelector('{opens}').open", timeout=5000)


def escape(s, closes):
    before = sum(1 for c in s.console if c.startswith("log: closed:"))
    s.page.keyboard.press("Escape")
    deadline = time.time() + 5
    while sum(1 for c in s.console if c.startswith("log: closed:")) == before:
        if time.time() > deadline:
            raise RuntimeError(f"close of {closes} not seen, gave up after 5 s")
        s.page.wait_for_timeout(20)


def check_sinks(s, names, label):
    page = s.page
    out = {"label": label, "problems": []}
    rows = page.evaluate(ROWS_JS)
    out["rows"] = len(rows)
    for name, row in zip(names, rows):
        expect = {"h3": name, "h3Children": 0, "bin": f'Delete "{name}"', "year": f"Year view, {name}", "done": f"Done today, {name}"}
        if row != expect:
            out["problems"].append({"row": name, "got": row})
    if page.viewport_size["width"] >= 1024:
        press(page, page.locator("section.band button.hc[aria-current=date]"), "dialog.dlg-day")
    else:
        press(page, page.locator("button.ov-btn"), "dialog.dlg-ov")
        press(page, page.locator("dialog.dlg-ov button.hc[aria-current=date]"), "dialog.dlg-day")
    ticks = page.evaluate(TICKS_JS)
    out["ticks"] = len(ticks)
    for name, tick in zip(names, ticks):
        if tick != {"label": name, "tname": name, "tnameChildren": 0}:
            out["problems"].append({"tick": name, "got": tick})
    escape(s, "P1")
    if page.viewport_size["width"] < 1024:
        escape(s, "P3")
    for index, name in enumerate(names):
        press(page, page.locator("ul.rows > li.row").nth(index).locator("button.btn-year"), "dialog.dlg-year")
        title = page.evaluate("() => { const h = document.querySelector('#yr-title'); return [h.textContent, h.childElementCount]; }")
        if title != [name, 0]:
            out["problems"].append({"p2": name, "got": title})
        press(page, page.locator("dialog.dlg-year button.btn-del"), "dialog.dlg-del")
        m1 = page.evaluate("() => { const h = document.querySelector('#del-title'); return [h.textContent, h.childElementCount]; }")
        if m1 != [f'Delete "⁨{name}⁩"?', 0]:
            out["problems"].append({"m1": name, "got": m1})
        escape(s, "M1")
        escape(s, "P2")
        if page.evaluate("() => document.querySelectorAll('dialog[open]').length"):
            out["problems"].append({"left open after": name})
    out["census"] = page.evaluate(CENSUS_JS)
    out["stored_names_equal"] = [h["name"] for h in json.loads(s.stored())["habits"]] == names
    return out


def finish(s, r, base_keys, before=None):
    if before is not None:
        r["stored_unchanged"] = s.stored() == before
    keys = set(s.page.evaluate(WINDOW_KEYS_JS))
    r["window_added"] = sorted(keys - base_keys)
    r["window_missing"] = sorted(base_keys - keys)
    r["dialogs"], r["errors"], r["csp"] = s.dialogs, s.errors, s.csp()
    r["console_errors"] = [c for c in s.console if c.startswith("error") and "404" not in c]
    r["clipboard"] = s.clipboard_marks()
    r["requests"] = sorted({q.split(" ")[0] + " " + q.split(" ")[1].replace(s.base, "/") for q in s.requests})
    r["closes_seen"] = sum(1 for c in s.console if c.startswith("log: closed:"))


def run(engine, base):
    results = {"engine": engine}
    with sync_playwright() as p:
        browser = lib.launch(p, engine)
        results["version"] = browser.version
        try:
            blank = lib.Session(browser, base, path="__seed__", clock=NOON)
            base_keys = set(blank.page.evaluate(WINDOW_KEYS_JS))
            blank.close()
            state = lib.encode([{"name": n, "done": DONE} for n in NAMES])
            for viewport in ((1280, 800), (390, 844)):
                s = lib.Session(browser, base, viewport=viewport, seed_js=lib.SEED_TEXT, seed_arg=state, clock=NOON, init=[CLOSE_LOGGER])
                try:
                    before = s.stored()
                    r = check_sinks(s, NAMES, f"planted {viewport[0]}x{viewport[1]}")
                    finish(s, r, base_keys, before)
                    results[r["label"]] = r
                finally:
                    s.close()
            s = lib.Session(browser, base, viewport=(1280, 800), clock=NOON, init=[CLOSE_LOGGER])
            try:
                for name in NAMES:
                    field = s.page.locator("#nh")
                    field.fill(name)
                    field.press("Enter")
                r = check_sinks(s, NAMES, "typed 1280x800")
                finish(s, r, base_keys)
                results[r["label"]] = r
            finally:
                s.close()
        finally:
            browser.close()
    return results


def main():
    proc, port, log = lib.start_server()
    try:
        base = f"http://127.0.0.1:{port}/"
        for engine in lib.engines_from_argv():
            t0 = time.time()
            print(json.dumps(run(engine, base), ensure_ascii=True))
            print(f"[{engine}] {time.time() - t0:.1f} s")
    finally:
        lib.stop_server(proc, port)
        print("[server] request lines:", len(log), "non-GET:", [l for l in log if '"GET ' not in l and "HTTP" in l][:5])
        print("[server] paths:", sorted({l.split('"')[1].split(" ")[1] for l in log if l.count('"') >= 2}))


if __name__ == "__main__":
    main()
