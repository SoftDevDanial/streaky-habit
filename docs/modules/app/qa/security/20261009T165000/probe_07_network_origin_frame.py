"""T5 / R25 / R26 / T9 / T10: the request log over a full session, globals and query strings, the shared origin and framing.

1. Every request over a full session (open, tick, add, delete, reload, midnight rollover, visibility change), logged at
   the context level (popups and workers included), plus websockets, workers and service workers.
2. R26: window property diff against a blank same-origin page, and /?demo=1, /?seed, /#sample against /.
3. T9: a sibling page of the same origin writes streaks.state while the app is open, and again before load.
4. T10: the app framed from a cross-site page (localhost over 127.0.0.1) and a same-site page; is it framed, and does the
   frame see the first-party habits?
After a fake clock is installed this probe waits with expect(), because in-page polling uses the mocked timers.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import re
from urllib.parse import urlsplit
from playwright.sync_api import expect
from lib import Run, new_context, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)


def main():
    with Run() as run:
        b, base = run.browser, run.base
        origin = base.rstrip("/")
        port = urlsplit(base).port

        print("--- 1. request log over a full session (context level)")
        ctx = new_context(b, fixed_time=None, install_time="2026-10-08T23:58:00+08:00")
        reqs, ws, workers, sw = [], [], [], []
        ctx.on("request", lambda r: reqs.append((r.method, r.url, r.resource_type)))
        ctx.on("serviceworker", lambda w: sw.append(w.url))
        page = ctx.new_page()
        page.on("websocket", lambda w: ws.append(w.url))
        page.on("worker", lambda w: workers.append(w.url))
        console, errors = [], []
        page.on("console", lambda m: console.append((m.type, m.text)))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(base + "__seed__")
        page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
        reqs.clear()
        console.clear()
        page.goto(base)
        expect(page.locator("li.habit")).to_have_count(3)
        page.locator("li.habit").nth(1).locator("button.day").last.click()
        page.locator("#new-habit").click()
        page.keyboard.type("Drink water")
        page.get_by_role("button", name="Add", exact=True).click()
        expect(page.locator("li.habit")).to_have_count(4)
        page.get_by_role("button", name="Delete Read 20 pages", exact=True).click()
        page.locator("dialog .btn-danger").click()
        expect(page.locator("li.habit")).to_have_count(3)
        page.reload()
        expect(page.locator("li.habit")).to_have_count(3)
        page.clock.run_for(180_000)
        expect(page.locator(".date time")).to_have_attribute("datetime", "2026-10-09")
        page.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
        page.get_by_role("button", name="Delete Drink water", exact=True).click()
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        uniq = sorted({(m, urlsplit(u).path, urlsplit(u).query, urlsplit(u).netloc == urlsplit(base).netloc) for m, u, t in reqs})
        for m, p, q, same in uniq:
            print(f"    {m} {p}{('?' + q) if q else ''}  same-origin={same}")
        off = [r for r in reqs if urlsplit(r[1]).netloc != urlsplit(base).netloc or r[0] != "GET" or urlsplit(r[1]).query]
        print(f"    total requests {len(reqs)}; off-origin / non-GET / with query: {off}")
        print(f"    websockets={ws} workers={workers} service workers={sw} ctx.service_workers={[w.url for w in ctx.service_workers]}")
        print(f"    console messages: {console}  page errors: {errors}")
        print(f"    navigator.serviceWorker registrations: {page.evaluate('async () => (await navigator.serviceWorker.getRegistrations()).length')}")
        ctx.close()

        print("--- 2. R26 globals and query strings")
        ctx = new_context(b)
        page = ctx.new_page()
        page.goto(base + "__seed__")
        blank = set(page.evaluate("() => Object.getOwnPropertyNames(window)"))
        page.goto(base)
        page.wait_for_selector(".cells .hc")
        app_props = set(page.evaluate("() => Object.getOwnPropertyNames(window)"))
        print(f"    properties on window of the app page but not on a blank same-origin page: {sorted(app_props - blank)}")
        print(f"    properties on the blank page but not the app page: {sorted(blank - app_props)}")
        base_html = page.evaluate("() => document.body.innerHTML")
        for suffix in ["?demo=1", "?seed", "#sample", "?sample=1&seed=1&demo=true#sample", "?state=%7B%7D"]:
            ctx2 = new_context(b)
            p2 = ctx2.new_page()
            reqs2 = []
            p2.on("request", lambda r: reqs2.append(r.url))
            p2.goto(base + suffix)
            p2.wait_for_selector(".cells .hc")
            same = p2.evaluate("() => document.body.innerHTML") == base_html
            print(f"    {suffix:<40} body equals '/': {same}; storage keys={p2.evaluate('() => localStorage.length')}")
            ctx2.close()
        ctx.close()

        print("--- 3. T9 a sibling page of the same origin writes the key")
        ctx = new_context(b)
        app = ctx.new_page()
        app.goto(base)
        app.wait_for_selector(".cells .hc")
        sib = ctx.new_page()
        sib.goto(base + "__seed__")
        evil = state_text([{"name": "<img src=x onerror=window.__pwned=1>", "done": ["2026-10-08"]}])
        sib.evaluate("(t) => localStorage.setItem('streaks.state', t)", evil)
        app.wait_for_timeout(800)
        print(f"    app open, sibling writes: app rows (no storage listener, so unchanged until reload) = {row_names(app)}")
        app.locator("#new-habit").click()
        app.keyboard.type("Mine")
        app.keyboard.press("Enter")
        print(f"    app then saves: stored = {sib.evaluate('() => localStorage.getItem(\"streaks.state\")')[:90]}  (the sibling's value is overwritten, last save wins)")
        sib.evaluate("(t) => localStorage.setItem('streaks.state', t)", evil)
        app.reload()
        app.wait_for_selector("li.habit")
        print(f"    reload after the plant: rows={row_names(app)} pwned={app.evaluate('() => window.__pwned')}")
        print("    the sibling can also READ the habit names and history:", sib.evaluate("() => localStorage.getItem('streaks.state')")[:90])
        ctx.close()

        print("--- 4. T10 framing")
        for label, top_origin in [("cross-site (localhost over 127.0.0.1)", f"http://localhost:{port}"), ("same-site other origin (127.0.0.1:1 over 127.0.0.1:port)", "http://127.0.0.1:1")]:
            ctx = new_context(b)
            first = ctx.new_page()
            first.goto(base + "__seed__")
            first.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
            first.goto(base)
            first.wait_for_selector("li.habit")
            first_rows = row_names(first)
            top = ctx.new_page()
            html = f'<!doctype html><title>attacker</title><iframe id="f" src="{origin}/" style="width:390px;height:844px"></iframe>'
            top.route(re.compile(re.escape(top_origin) + r"/frame\.html.*"), lambda route, html=html: route.fulfill(status=200, content_type="text/html", body=html))
            top.goto(top_origin + "/frame.html")
            frame = top.frame_locator("#f")
            top.wait_for_timeout(1500)
            framed = frame.locator(".cells .hc").count() > 0
            rows = frame.locator("h3.habit-name").all_text_contents()
            print(f"    {label}: app rendered inside the frame={framed}; framed app habits={rows} (first-party habits were {first_rows})")
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
