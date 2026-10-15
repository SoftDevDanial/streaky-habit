"""T5, R25, R26, R41 (SW2), T13. Nothing leaves the device, the CSP holds, no hooks, in each engine.

Part 1  Egress attempts from inside the app's page against a canary http.server on another port (another origin).
        The canary's own log is the ground truth: any line there is a request that left the page.
Part 2  Every v1.1.0 flow at 1280 and 390, with every request logged (pass-through route): add, Done today, P1 from
        the band, P4, P1 over P4, P3, P4 over P3, P1 over P3, P2, a bead, M1 kept and done, a failing save with the
        warning (thrown value watched), a failing read at boot, a reload, a rollover with P4 open.
Part 3  Query strings and fragments boot like "/", window keys equal a same-origin blank page with the same clock.
Part 4  The icon link's href loaded as an image under the live CSP: load fires, no violation.
Usage: python -B probe_04_csp_network.py [chromium] [webkit]
"""
import json
import time

from playwright.sync_api import sync_playwright

import conftest
import lib

NOON = "2026-10-10T12:00:00+08:00"
SAMPLE = lib.encode(conftest.SAMPLE_HABITS)
CLOSE_LOGGER = "document.addEventListener('close', (e) => console.log('closed:' + e.target.className), true);"

ATTEMPTS_JS = """async (canary) => {
  const results = {};
  const tryIt = async (name, fn) => { try { const r = await fn(); results[name] = 'ran: ' + String(r).slice(0, 60); } catch (e) { results[name] = 'threw: ' + e.name; } };
  const add = (html) => { const t = document.createElement('template'); t.innerHTML = html; const n = t.content.firstElementChild; document.body.append(n); return n; };
  await tryIt('fetch cross-origin', () => fetch(canary + '/fetch').then((r) => r.status));
  await tryIt('fetch same-origin', () => fetch('/same-origin').then((r) => r.status));
  await tryIt('xhr', () => new Promise((ok, no) => { const x = new XMLHttpRequest(); x.open('GET', canary + '/xhr'); x.onload = () => ok(x.status); x.onerror = () => no(new Error('xhr error')); x.send(); }));
  await tryIt('websocket', () => new Promise((ok, no) => { const w = new WebSocket(canary.replace('http', 'ws') + '/ws'); w.onopen = () => ok('open'); w.onerror = () => no(new Error('ws error')); setTimeout(() => ok('no event'), 500); }));
  await tryIt('eventsource', () => new Promise((ok) => { const e = new EventSource(canary + '/es'); e.onerror = () => ok('error event'); setTimeout(() => ok('no event'), 500); }));
  await tryIt('sendBeacon', () => navigator.sendBeacon(canary + '/beacon', 'x'));
  await tryIt('img', () => new Promise((ok) => { const i = new Image(); i.onload = () => ok('load'); i.onerror = () => ok('error'); i.src = canary + '/img'; }));
  await tryIt('stylesheet link', () => new Promise((ok) => { const l = add('<link rel="stylesheet" href="' + canary + '/css">'); l.onload = () => ok('load'); l.onerror = () => ok('error'); setTimeout(() => ok('no event'), 500); }));
  await tryIt('inline style @import and url()', () => { add('<style>@import url(' + canary + '/import.css); body{background:url(' + canary + '/bg.png)}</style>'); return new Promise((ok) => setTimeout(() => ok('added'), 300)); });
  await tryIt('style attribute url()', () => { const d = add('<div style="background:url(' + canary + '/attr.png);width:5px;height:5px"></div>'); return new Promise((ok) => setTimeout(() => ok(getComputedStyle(d).backgroundImage.slice(0, 30)), 300)); });
  await tryIt('iframe', () => new Promise((ok) => { const f = add('<iframe src="' + canary + '/frame"></iframe>'); f.onload = () => ok('load'); setTimeout(() => ok('no event'), 500); }));
  await tryIt('object', () => { add('<object data="' + canary + '/object"></object>'); return new Promise((ok) => setTimeout(() => ok('added'), 300)); });
  await tryIt('embed', () => { add('<embed src="' + canary + '/embed">'); return new Promise((ok) => setTimeout(() => ok('added'), 300)); });
  await tryIt('audio', () => new Promise((ok) => { const a = add('<audio src="' + canary + '/audio"></audio>'); a.onerror = () => ok('error'); setTimeout(() => ok('no event'), 500); }));
  await tryIt('prefetch link', () => { add('<link rel="prefetch" href="' + canary + '/prefetch">'); return new Promise((ok) => setTimeout(() => ok('added'), 300)); });
  await tryIt('external script', () => new Promise((ok) => { const s = document.createElement('script'); s.src = canary + '/x.js'; s.onload = () => ok('load'); s.onerror = () => ok('error'); document.head.append(s); }));
  await tryIt('inline script', () => { const s = document.createElement('script'); s.textContent = "console.log('pwned-inline')"; document.head.append(s); return 'added'; });
  await tryIt('inline handler', () => { add('<img src="nothing.png" onerror="console.log(\\'pwned-handler\\')">'); return new Promise((ok) => setTimeout(() => ok('added'), 300)); });
  await tryIt('eval', () => eval('1 + 1'));
  await tryIt('new Function', () => new Function('return 2')());
  await tryIt('string setTimeout', () => { setTimeout("console.log('pwned-timeout')", 0); return new Promise((ok) => setTimeout(() => ok('scheduled'), 100)); });
  await tryIt('dynamic import', () => import(canary + '/mod.js'));
  await tryIt('blob worker', () => new Worker(URL.createObjectURL(new Blob(['postMessage(1)'], { type: 'text/javascript' }))));
  await tryIt('base element', () => { add('<base href="' + canary + '/base/">'); return document.baseURI; });
  await tryIt('form submit', () => { const f = add('<form action="' + canary + '/form" method="post"><input name="n" value="No alcohol"></form>'); f.submit(); return new Promise((ok) => setTimeout(() => ok('submitted'), 500)); });
  return results;
}"""


def flows(s, page, width):
    def key(sel):
        page.locator(sel).first.focus()
        page.keyboard.press("Enter")

    def esc():
        n = sum(1 for c in s.console if c.startswith("log: closed:"))
        page.keyboard.press("Escape")
        deadline = time.time() + 5
        while sum(1 for c in s.console if c.startswith("log: closed:")) == n:
            if time.time() > deadline:
                raise RuntimeError("close not seen, gave up after 5 s")
            page.wait_for_timeout(20)

    page.locator("#nh").fill("Drink water")
    page.locator("#nh").press("Enter")
    key("ul.rows > li.row button.btn-done")
    if width >= 1024:
        key("section.band button.hc[data-key='2026-09-22']")
        key("dialog.dlg-day button.tick")
        esc()
        key("section.band button.btn-all")
        key("dialog.dlg-all button.hc[data-key='2025-10-10']")
        key("dialog.dlg-day button.tick")
        esc()
        esc()
    else:
        key("button.ov-btn")
        key("dialog.dlg-ov button.hc[data-key='2026-09-22']")
        key("dialog.dlg-day button.tick")
        esc()
        key("dialog.dlg-ov button.btn-all")
        key("dialog.dlg-all button.hc[data-key='2025-10-11']")
        key("dialog.dlg-day button.tick")
        esc()
        esc()
        esc()
    key("ul.rows > li.row button.btn-year")
    key("dialog.dlg-year button.yc[data-key='2026-01-15']")
    key("dialog.dlg-year button.btn-del")
    esc()
    key("dialog.dlg-year button.btn-del")
    key("dialog.dlg-del button.btn-danger")
    page.wait_for_timeout(200)


def run(engine, base, canary, canary_log):
    out = {"engine": engine}
    with sync_playwright() as p:
        browser = lib.launch(p, engine)
        out["version"] = browser.version
        try:
            # Part 1
            s = lib.Session(browser, base, viewport=(1280, 800), seed_js=lib.SEED_TEXT, seed_arg=SAMPLE, clock=NOON)
            try:
                before = len(canary_log)
                out["attempts"] = s.page.evaluate(ATTEMPTS_JS, canary)
                s.page.wait_for_timeout(1000)
                out["canary_lines_from_attempts"] = canary_log[before:]
                out["violations"] = sorted({c.split(":", 2)[2].split(":")[0] for c in s.csp()})
                out["pwned_markers"] = [c for c in s.console if "pwned" in c and "csp-violation" not in c]
                out["attempt_page_errors"] = s.errors
                out["popups_opened"] = len(s.ctx.pages) - 1
            finally:
                s.close()
            # Part 2
            blank = lib.Session(browser, base, path="__seed__", clock=NOON)
            base_keys = set(blank.page.evaluate("() => Object.getOwnPropertyNames(window)"))
            blank.close()
            for width, height in ((1280, 800), (390, 844)):
                s = lib.Session(browser, base, viewport=(width, height), seed_js=lib.SEED_TEXT, seed_arg=SAMPLE,
                                init=[CLOSE_LOGGER, conftest.FAIL_SETITEM_PROBE], install_clock="2026-10-10T23:59:30+08:00")
                try:
                    lib_page = s.page
                    conftest.storage_switch(lib_page, False)
                    flows(s, lib_page, width)
                    conftest.storage_switch(lib_page, True)
                    lib_page.locator("ul.rows > li.row button.btn-done").first.focus()
                    lib_page.keyboard.press("Enter")
                    warn = lib_page.evaluate("() => document.querySelectorAll('div.banner.warn').length")
                    if width >= 1024:
                        lib_page.locator("section.band button.btn-all").focus()
                        lib_page.keyboard.press("Enter")
                    lib_page.clock.run_for(45000)  # past local midnight, the 30 s check redraws, P4 open at 1280
                    date = lib_page.evaluate("() => document.querySelector('time.date').textContent")
                    keys = set(lib_page.evaluate("() => Object.getOwnPropertyNames(window)"))
                    lib_page.reload()
                    r = {"warning_shown_on_failed_save": warn, "date_after_rollover": date,
                         "thrown_value_read": [c for c in s.console if conftest.STORAGE_READ_MARK in c],
                         "requests": sorted({q.replace(base, "/") for q in s.requests}),
                         "query_strings": [q for q in s.requests if "?" in q], "violations": s.csp(),
                         "errors": s.errors, "console_errors": [c for c in s.console if c.startswith("error") and "404" not in c],
                         "clipboard": s.clipboard_marks(),
                         "window_added": sorted(keys - base_keys - {"__pwClock"}), "window_missing": sorted(base_keys - keys)}
                    out[f"flows {width}x{height}"] = r
                finally:
                    s.close()
            # failing read at boot
            s = lib.Session(browser, base, viewport=(390, 844), clock=NOON, init=[conftest.FAIL_GETTER])
            try:
                out["boot with storage denied"] = {"warn": s.page.evaluate("() => document.querySelectorAll('div.banner.warn').length"),
                                                   "rows_or_empty": s.page.evaluate("() => document.querySelectorAll('ul.rows > li').length"),
                                                   "errors": s.errors, "requests": sorted({q.replace(base, "/") for q in s.requests})}
            finally:
                s.close()
            # Part 3
            ref = lib.Session(browser, base, viewport=(390, 844), clock=NOON)
            ref_body = ref.page.evaluate("() => document.body.innerHTML")
            ref.close()
            same = {}
            for path in ["?demo=1", "?seed", "#sample", "?sample=1&seed=1&demo=true#sample", "?state=%7B%22version%22%3A1%7D", "index.html?debug=1"]:
                s = lib.Session(browser, base, viewport=(390, 844), clock=NOON, path=path)
                try:
                    same[path] = {"body_equal": s.page.evaluate("() => document.body.innerHTML") == ref_body,
                                  "storage_keys": s.page.evaluate("() => localStorage.length")}
                finally:
                    s.close()
            out["query and fragment"] = same
            # Part 4
            s = lib.Session(browser, base, viewport=(390, 844), clock=NOON)
            try:
                out["icon as image"] = s.page.evaluate("""() => new Promise((ok) => { const i = new Image();
                  i.onload = () => ok(['load', i.naturalWidth]); i.onerror = () => ok(['error']);
                  i.src = document.querySelector('link[rel=icon]').href; })""")
                out["icon violations"] = s.csp()
            finally:
                s.close()
        finally:
            browser.close()
    return out


def main():
    proc, port, log = lib.start_server()
    canary_dir = lib.HERE  # serves this evidence folder; every path asked for is logged
    cproc, cport, clog = lib.start_server(canary_dir)
    try:
        base = f"http://127.0.0.1:{port}/"
        canary = f"http://127.0.0.1:{cport}"
        for engine in lib.engines_from_argv():
            result = run(engine, base, canary, clog)
            for k, v in result.items():
                print(f"{k}: {json.dumps(v, ensure_ascii=True)}", flush=True)
    finally:
        lib.stop_server(cproc, cport)
        lib.stop_server(proc, port)
        print("[canary] all lines:", clog)
        print("[app server] non-GET or query lines:", [l for l in log if ('"GET ' not in l or "?" in l) and "HTTP" in l])


if __name__ == "__main__":
    main()
