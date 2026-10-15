"""T1, T2, R16, R17. Crafted stored values through the strict decoder, in each engine.

Each case is planted in a fresh throwaway context through the same-origin /__seed__ page, then the app loads.
Unreadable values must reset to the empty state with the S5 note. Readable values must load and stay byte for
byte until the first change, and the first change must save only { version, habits[{ name, done }] }.
For readable cases the probe opens P4, P2 and P1 by keyboard and checks that no control exists for a day
before the year start or after today. Prototype integrity is compared with a clean page.
A last part edits data-key attributes in the DOM (a defence-in-depth check, it needs script on the page) and
ticks, to show toggleDay still refuses days outside the year.
Usage: python -B probe_02_tamper.py [chromium] [webkit]
"""
import json
import time

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"
EMPTY = '{"version":1,"habits":[]}'
CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"


def h(name, done=()):
    return {"name": name, "done": list(done)}


def state(habits):
    return json.dumps({"version": 1, "habits": habits}, separators=(",", ":"), ensure_ascii=False)


UNREADABLE = {
    "not json": "{",
    "json null": "null",
    "array": "[]",
    "version 2": '{"version":2,"habits":[]}',
    "version string": '{"version":"1","habits":[]}',
    "habits missing": '{"version":1}',
    "habits object": '{"version":1,"habits":{}}',
    "13 habits": state([h(f"H{i}") for i in range(13)]),
    "duplicate ignoring case": state([h("Read"), h("read")]),
    "untrimmed name": state([h(" Read")]),
    "empty name": state([h("")]),
    "41 code points": state([h("x" * 41)]),
    "41 emoji": state([h("\U0001F600" * 41)]),
    "name number": '{"version":1,"habits":[{"name":5,"done":[]}]}',
    "done string": '{"version":1,"habits":[{"name":"A","done":"2026-10-10"}]}',
    "done 29 Feb 2026": state([h("A", ["2026-02-29"])]),
    "done 2026-1-1": state([h("A", ["2026-1-1"])]),
    "done leading space": state([h("A", [" 2026-10-10"])]),
    "done trailing newline": state([h("A", ["2026-10-10\n"])]),
    "done number": '{"version":1,"habits":[{"name":"A","done":[20261010]}]}',
    "done object": '{"version":1,"habits":[{"name":"A","done":[{"__proto__":{"x":1}}]}]}',
    "done year 0000": state([h("A", ["0000-01-01"])]),
    "done year 10000": state([h("A", ["10000-01-01"])]),
    "done far key": state([h("A", ["24660873954866-12-02"])]),
    "done fullwidth digits": state([h("A", ["２０２６-10-10"])]),
    "habit as array": '{"version":1,"habits":[["A",[]]]}',
    "habit null": '{"version":1,"habits":[null]}',
    "name only in __proto__": '{"version":1,"habits":[{"__proto__":{"name":"A","done":[]}}]}',
    "version only in __proto__": '{"__proto__":{"version":1},"habits":[]}',
}

READABLE = {
    "extra and __proto__ keys": '{"version":1,"habits":[{"name":"A","done":["2026-10-10"],"extra":1,"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":4}}}],"__proto__":{"polluted":2},"constructor":{"prototype":{"polluted":3}},"x":"y"}',
    "unsorted with duplicates": state([h("A", ["2026-10-10", "2026-10-01", "2026-10-10", "2026-09-30"])]),
    "dates outside the year": state([h("Edges", ["0001-01-01", "1999-12-31", "2025-10-08", "2025-10-09", "2025-10-10", "2026-10-09", "2026-10-10", "2026-10-11", "2026-10-12", "2027-01-01", "9999-12-31"])]),
    "object-key names": state([h(n) for n in ["__proto__", "constructor", "toString", "hasOwnProperty", "valueOf", "prototype", "__defineGetter__", "length", "then", "rn-1", "nh", "del-title"]]),
    "control and lone surrogate names": state([h(n) for n in ["\u0000", "a\nb", "\ud800", "\udc00x", "‮ reversed", "⁩ closer", "​", "tab\tname", "\u001f", "\u0085next"]]),
    "deep nesting in an extra key": '{"version":1,"habits":[],"x":' + "[" * 20000 + "]" * 20000 + "}",
    "4 MB extra string": '{"version":1,"habits":[{"name":"A","done":[]}],"pad":"' + "a" * 4_000_000 + '"}',
}

PROTO_JS = """() => ({ object: Object.getOwnPropertyNames(Object.prototype).sort().join(','),
  array: Object.getOwnPropertyNames(Array.prototype).sort().join(','),
  polluted: [({}).polluted, [].polluted, (() => 0).polluted].map(String).join(',') })"""

VIEW_JS = """() => ({ rows: document.querySelectorAll('ul.rows > li.row').length,
  empty: document.querySelectorAll('ul.rows > li.empty').length,
  note: document.querySelectorAll('div.banners > div.banner.note').length,
  warn: document.querySelectorAll('div.banners > div.banner.warn').length })"""

KEYS_JS = """(sel) => { const k = Array.from(document.querySelectorAll(sel)).map((b) => b.getAttribute('data-key')).sort();
  return k.length ? [k.length, k[0], k[k.length - 1]] : [0]; }"""


def wait_closes(s, count_before, want):
    deadline = time.time() + 5
    while sum(1 for c in s.console if c.startswith("log: closed:")) < count_before + want:
        if time.time() > deadline:
            raise RuntimeError("close not seen, gave up after 5 s")
        s.page.wait_for_timeout(20)


def kb(page, selector, opens):
    page.locator(selector).first.focus()
    page.keyboard.press("Enter")
    page.wait_for_function(f"() => document.querySelector('{opens}').open", timeout=5000)


def esc(s):
    n = sum(1 for c in s.console if c.startswith("log: closed:"))
    s.page.keyboard.press("Escape")
    wait_closes(s, n, 1)


def run(engine, base):
    out = {"engine": engine}
    with sync_playwright() as p:
        browser = lib.launch(p, engine)
        out["version"] = browser.version
        try:
            clean = lib.Session(browser, base, viewport=(1280, 800), clock=NOON)
            clean_proto = clean.page.evaluate(PROTO_JS)
            clean.close()
            for label, text in UNREADABLE.items():
                s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=text, clock=NOON)
                try:
                    v = s.page.evaluate(VIEW_JS)
                    ok = v == {"rows": 0, "empty": 1, "note": 1, "warn": 0} and s.stored() == EMPTY
                    proto_ok = s.page.evaluate(PROTO_JS) == clean_proto
                    out[f"U {label}"] = {"reset_with_note": ok, "proto_clean": proto_ok, "errors": s.errors,
                                         "console_errors": [c for c in s.console if c.startswith("error") and "404" not in c]}
                    if not ok:
                        out[f"U {label}"]["view"] = v
                finally:
                    s.close()
            for label, text in READABLE.items():
                s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=text, clock=NOON,
                                init=[CLOSE_LOGGER], nav_timeout_ms=30000)
                try:
                    r = {"view": s.page.evaluate(VIEW_JS)}
                    r["stored_unchanged_after_load"] = s.stored() == text
                    r["proto_clean"] = s.page.evaluate(PROTO_JS) == clean_proto
                    if r["view"]["rows"]:
                        kb(s.page, "section.band button.btn-all", "dialog.dlg-all")
                        r["p4_day_keys"] = s.page.evaluate(KEYS_JS, "dialog.dlg-all button.hc")
                        esc(s)
                        kb(s.page, "ul.rows > li.row button.btn-year", "dialog.dlg-year")
                        r["p2_bead_keys"] = s.page.evaluate(KEYS_JS, "dialog.dlg-year button.yc")
                        r["p2_stats"] = s.page.evaluate("() => document.querySelector('p.yr-stats').textContent")
                        esc(s)
                        r["band_day_keys"] = s.page.evaluate(KEYS_JS, "section.band button.hc")
                        kb(s.page, "section.band button.hc[aria-current=date]", "dialog.dlg-day")
                        r["p1_title"] = s.page.evaluate("() => document.querySelector('#day-title').textContent")
                        esc(s)
                        s.page.locator("ul.rows > li.row button.btn-done").first.focus()
                        s.page.keyboard.press("Enter")
                        saved = json.loads(s.stored())
                        r["saved_top_keys"] = sorted(saved)
                        r["saved_habit_keys"] = sorted({k for habit in saved["habits"] for k in habit})
                        r["saved_names_equal"] = [x["name"] for x in saved["habits"]] == [x["name"] for x in json.loads(text)["habits"]]
                        if label == "dates outside the year":
                            r["saved_done"] = saved["habits"][0]["done"]
                    r["errors"] = s.errors
                    r["console_errors"] = [c for c in s.console if c.startswith("error") and "404" not in c]
                    out[f"R {label}"] = r
                finally:
                    s.close()

            # data-key edits in the DOM, then a keyboard tick: toggleDay must refuse days outside the year
            text = state([h("A", ["2026-10-10"])])
            s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=text, clock=NOON, init=[CLOSE_LOGGER])
            try:
                tamper = {}
                for key in ["2027-01-01", "2025-10-09", "1999-01-01", "__proto__", "", "2026-02-30", "x".join(["2026-10-01"] * 2)]:
                    s.page.evaluate("(k) => document.querySelector('section.band button.hc').setAttribute('data-key', k)", key)
                    kb(s.page, "section.band button.hc", "dialog.dlg-day")
                    title = s.page.evaluate("() => document.querySelector('#day-title').textContent")
                    s.page.locator("dialog.dlg-day button.tick").first.focus()
                    s.page.keyboard.press("Enter")
                    esc(s)
                    tamper[f"band {key!r}"] = {"p1_title": title, "stored_unchanged": s.stored() == text}
                kb(s.page, "ul.rows > li.row button.btn-year", "dialog.dlg-year")
                for key in ["2027-01-01", "2025-10-09", "__proto__"]:
                    s.page.evaluate("(k) => document.querySelector('dialog.dlg-year button.yc').setAttribute('data-key', k)", key)
                    s.page.locator("dialog.dlg-year button.yc").first.focus()
                    s.page.keyboard.press("Enter")
                    tamper[f"bead {key!r}"] = {"stored_unchanged": s.stored() == text}
                esc(s)
                tamper["errors"] = s.errors
                out["DOM data-key edits"] = tamper
            finally:
                s.close()
        finally:
            browser.close()
    return out


def main():
    proc, port, log = lib.start_server()
    try:
        base = f"http://127.0.0.1:{port}/"
        for engine in lib.engines_from_argv():
            t0 = time.time()
            result = run(engine, base)
            for key, value in result.items():
                print(f"{key}: {json.dumps(value, ensure_ascii=True)}")
            print(f"[{engine}] {time.time() - t0:.1f} s")
    finally:
        lib.stop_server(proc, port)
        print("[server] non-GET lines:", [l for l in log if '"GET ' not in l and "HTTP" in l][:5])


if __name__ == "__main__":
    main()
