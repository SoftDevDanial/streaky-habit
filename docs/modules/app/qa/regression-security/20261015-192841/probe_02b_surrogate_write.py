"""Follow-up to probe_02, case "control and lone surrogate names": stored_unchanged_after_load was false.
Did the app write at load (R16 says loading writes nothing), or did the test transport change the text?
The value is built and compared inside the page, so no lone surrogate crosses the Playwright protocol, and a
setItem counter (console marker) shows whether the app wrote.
Usage: python -B probe_02b_surrogate_write.py [chromium] [webkit]
"""
import json

from playwright.sync_api import sync_playwright

import lib

NOON = "2026-10-10T12:00:00+08:00"
BUILD = """() => {
  const names = ['\\u0000', 'a\\nb', '\\ud800', '\\udc00x', '\\u202e reversed', '\\u2069 closer', '\\u200b', 'tab\\tname', '\\u001f', '\\u0085next'];
  const text = JSON.stringify({ version: 1, habits: names.map((name) => ({ name, done: [] })) });
  localStorage.setItem('streaks.state', text);
  sessionStorage.setItem('planted', text);
}"""
COUNTER = """(() => { const set = Storage.prototype.setItem;
  Storage.prototype.setItem = function (k, v) { if (this === window.localStorage) console.log('setItem:' + k); return set.call(this, k, v); }; })();"""
COMPARE = """() => ({ same: localStorage.getItem('streaks.state') === sessionStorage.getItem('planted'),
  storedLength: localStorage.getItem('streaks.state').length, plantedLength: sessionStorage.getItem('planted').length,
  rows: document.querySelectorAll('ul.rows > li.row').length,
  names: Array.from(document.querySelectorAll('ul.rows h3')).map((h) => Array.from(h.textContent).map((c) => c.codePointAt(0).toString(16)).join(' ')) })"""


def main():
    proc, port, _ = lib.start_server()
    try:
        base = f"http://127.0.0.1:{port}/"
        with sync_playwright() as p:
            for engine in lib.engines_from_argv():
                browser = lib.launch(p, engine)
                try:
                    s = lib.Session(browser, base, viewport=(1280, 800), seed_js=BUILD, clock=NOON, init=[COUNTER])
                    result = s.page.evaluate(COMPARE)
                    result["app_setItem_calls"] = [c for c in s.console if "setItem:" in c]
                    result["errors"] = s.errors
                    print(engine, browser.version, json.dumps(result, ensure_ascii=True))
                    s.close()
                finally:
                    browser.close()
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
