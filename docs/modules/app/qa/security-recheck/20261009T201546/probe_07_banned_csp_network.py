"""Regression for R21 to R26 on the changed files (src/app.js, src/view.js), plus the over-swallow measurements.

Part 1 (static): banned APIs in the two changed files and the rest of src/: markup sinks (innerHTML, outerHTML,
insertAdjacentHTML, document.write, eval, new Function, Function(, setTimeout/setInterval with a string), network
(fetch, XMLHttpRequest, WebSocket, EventSource, sendBeacon, import(), absolute URLs), other storage (sessionStorage,
indexedDB, cookie), globals (window., globalThis assignments, a hook), timers/deferral (setTimeout, requestAnimationFrame,
queueMicrotask, Promise) and clock reads (new Date, Date.now, performance.now). The expected hits are listed.
Part 2 (running app): one session through the guard paths (tick, add, open, held double click, cancel, delete, reload) with
a request log; the R1 CSP string; a fetch and an inline script refused; window gains no property; query strings and
fragments change nothing.
Part 3 (over-swallow, measured): what the page guard holds after a mouse press in the dialog when the next action is a
keyboard activation, and the Add form.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import re

from lib import ROOT, Run, box, centre, events, fmt_clicks, make_context, open_app, press, reseed, snap, verdict

R1_CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"

PATTERNS = {
    "markup sinks": r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|\beval\s*\(|new\s+Function|\bFunction\s*\(|set(Timeout|Interval)\s*\(\s*[\"'`]",
    "network": r"\bfetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|\bimport\s*\(|https?://|new\s+Worker|serviceWorker",
    "other storage": r"sessionStorage|indexedDB|document\.cookie|caches\.",
    "globals": r"\bwindow\s*[.\[]|globalThis|\bself\s*\.|\btop\s*\.|\bparent\s*\.",
    "deferral": r"setTimeout|requestAnimationFrame|queueMicrotask|Promise|\basync\b|\bawait\b",
    "clock": r"new\s+Date|Date\.now|performance\.now",
    "interval": r"setInterval",
}


def part1(say):
    say("== Part 1: banned APIs, static ==")
    for name in ("src/app.js", "src/view.js"):
        text = (ROOT / name).read_text(encoding="utf-8")
        for label, pat in PATTERNS.items():
            lines = [(i + 1, l.strip()[:90]) for i, l in enumerate(text.splitlines()) if re.search(pat, l) and not l.strip().startswith(("*", "//", "/*"))]
            say(f"  {name:12s} {label:14s}: {len(lines)} hit(s) {lines if lines else ''}")
    say("  (expected: the one `new Date` in readToday, the one setInterval(checkDay), the SVG namespace string in view.js)")
    others = [p for p in sorted((ROOT / "src").glob("*.js")) if p.name not in ("app.js", "view.js")]
    for p in others:
        text = p.read_text(encoding="utf-8")
        total = sum(len([1 for l in text.splitlines() if re.search(pat, l) and not l.strip().startswith(("*", "//", "/*"))]) for label, pat in PATTERNS.items() if label not in ("clock", "interval"))
        say(f"  {p.name:12s} (unchanged since 6cfe05f) banned-pattern hits: {total}")


def part2(run, say):
    say("== Part 2: running app ==")
    ctx = make_context(run.browser, (390, 844), True)
    page = ctx.new_page()
    requests, console_errors, page_errors, js_dialogs, sockets, workers = [], [], [], [], [], []
    page.on("request", lambda r: requests.append((r.method, r.url)))
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("websocket", lambda w: sockets.append(w.url))
    page.on("worker", lambda w: workers.append(w.url))
    page.on("dialog", lambda d: (js_dialogs.append(d.message), d.dismiss()))
    page.goto(run.base)  # empty storage: the real first-run path
    page.wait_for_selector("p.empty")
    page.locator("#new-habit").fill("Drink water")
    page.keyboard.press("Enter")
    page.locator("#new-habit").fill("Walk")
    page.get_by_role("button", name="Add", exact=True).click()
    page.wait_for_timeout(700)
    press(page, *centre(page.locator("li.habit:nth-child(1) button.day").nth(6).bounding_box()), True)
    page.wait_for_timeout(100)
    press(page, *centre(page.locator("li.habit:nth-child(2) .icon-btn").bounding_box()), True)
    page.wait_for_timeout(100)
    press(page, *centre(box(page, "dialog .btn-danger")), True)  # held
    page.wait_for_timeout(600)
    press(page, *centre(box(page, "dialog .btn-secondary")), True)  # cancel
    page.wait_for_timeout(600)
    press(page, *centre(page.locator("li.habit:nth-child(2) .icon-btn").bounding_box()), True)
    page.wait_for_timeout(650)
    press(page, *centre(box(page, "dialog .btn-danger")), True)  # delete
    page.wait_for_timeout(600)
    page.reload()
    page.wait_for_selector("li.habit")
    page.wait_for_timeout(300)
    after = snap(page)
    say(f"  session end: habits={after['names']}, dialog open={after['open']}")
    paths = sorted({re.sub(r"^http://127\.0\.0\.1:\d+", "", u) for _, u in requests})
    say(f"  requests: {len(requests)}, methods {sorted({m for m, _ in requests})}, all same origin: {all(u.startswith(run.base[:-1]) for _, u in requests)}, any query string: {any('?' in u for _, u in requests)}")
    say(f"  paths: {paths}")
    say(f"  console errors: {console_errors}; page errors: {page_errors}; JS dialogs: {js_dialogs}; websockets: {sockets}; workers: {workers}")
    csp = page.evaluate("() => document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]').getAttribute('content')")
    say(f"  CSP meta equals the R1 string: {csp == R1_CSP}")
    probe = page.evaluate("""async () => {
      const violations = [];
      document.addEventListener('securitypolicyviolation', (e) => violations.push(e.violatedDirective), true);
      let fetchResult;
      try { await fetch(location.origin + '/index.html'); fetchResult = 'fetch allowed'; } catch (e) { fetchResult = 'fetch refused: ' + e.name; }
      const s = document.createElement('script'); s.textContent = 'window.__inline = 1'; document.head.append(s);
      const img = document.createElement('img'); img.setAttribute('onerror', 'window.__handler = 1'); img.src = 'data:,'; document.body.append(img);
      await new Promise((r) => setTimeout(r, 300));
      return { fetchResult, inline: window.__inline === 1, handler: window.__handler === 1, violations };
    }""")
    say(f"  CSP in force: {probe['fetchResult']}; inline script ran: {probe['inline']}; inline handler ran: {probe['handler']}; violations seen: {sorted(set(probe['violations']))}")
    ctx.close()

    base_props = None
    ctx = make_context(run.browser, (390, 844), False)
    page = ctx.new_page()
    page.goto(run.base + "__blank__")
    base_props = set(page.evaluate("() => Object.getOwnPropertyNames(window)"))
    page.goto(run.base)
    page.wait_for_selector("p.empty")
    app_props = set(page.evaluate("() => Object.getOwnPropertyNames(window)"))
    extra = sorted(app_props - base_props - {"__ev"})
    missing = sorted(base_props - app_props)
    say(f"  window own properties the app added (probe's __ev excluded): {extra}; missing: {missing}")
    bodies = {}
    for path in ("", "?demo=1", "?seed", "#sample", "?sample=1&seed=1&demo=true#sample", "?state=%7B%7D"):
        page.goto(run.base + path)
        page.wait_for_selector("p.empty")
        bodies[path] = (page.locator("body").inner_text(), page.evaluate("() => Object.keys(localStorage)"))
    say(f"  query strings and fragments boot like /: {all(v == bodies[''] for v in bodies.values())}; storage keys after each: {sorted({str(v[1]) for v in bodies.values()})}")
    ctx.close()


def part3(run, say):
    say("== Part 3: what the page guard holds after a mouse press in the dialog, for keyboard activations ==")
    ctx, page = open_app(run.browser, run.base, (1440, 900), False)
    try:
        trash = lambda row: page.locator(f"li.habit:nth-child({row}) .icon-btn")
        reseed(page)
        before = snap(page)
        press(page, *centre(trash(1).bounding_box()), False)
        page.wait_for_selector("dialog[open]")
        page.wait_for_timeout(650)
        press(page, *centre(box(page, "dialog .btn-secondary")), False)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")  # focus was returned to the trash button by the app; a keyboard click on it
        page.wait_for_timeout(200)
        s = snap(page)
        say(f"  mouse Cancel, Enter on the focused trash +~100 ms: dialog open={s['open']} (held by the page guard if False); focus={s['active']!r}; clicks: {fmt_clicks(events(page)[-2:])}")
        page.wait_for_timeout(600)
        page.keyboard.press("Enter")
        page.wait_for_selector("dialog[open]")
        say("  same Enter +~900 ms after the Cancel press: the dialog opens")
        reseed(page)
        press(page, *centre(trash(1).bounding_box()), False)
        page.wait_for_selector("dialog[open]")
        page.wait_for_timeout(650)
        press(page, *centre(box(page, "dialog .btn-secondary")), False)
        page.wait_for_timeout(100)
        page.locator("#new-habit").fill("Typed fast")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        say(f"  mouse Cancel, then typing a name and Enter within ~500 ms: habits={snap(page)['names']} (the add is held if 3)")
    finally:
        ctx.close()


def main():
    with Run() as run:
        say = run.say
        part1(say)
        part2(run, say)
        part3(run, say)
    run.finish("probe_07")


if __name__ == "__main__":
    main()
