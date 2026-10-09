"""T3 (second layer) and T5: the meta CSP in force in the running app, against inline script, inline handlers, eval,
javascript: URLs, external and data: scripts, every outbound channel, <base>, and a native form submit with the script
blocked. A canary listener (a thread in this process) records any request that gets through.

Each attempt runs inside the app page (CDP evaluate, which the CSP does not govern) and creates the thing the CSP must
stop. Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import json
import re
import time
from lib import Run, Canary, open_app, state_text, new_context, attach, ROOT

SPEC_CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; "
            "object-src 'none'; base-uri 'none'; form-action 'none'")

ATTEMPTS = r"""
async (canary) => {
  const out = {};
  const violations = [];
  document.addEventListener('securitypolicyviolation', (e) => violations.push(e.violatedDirective + ' <- ' + (e.blockedURI || e.sample || '').toString().slice(0, 50)));
  const tick = (ms = 150) => new Promise((r) => setTimeout(r, ms));
  const attempt = async (name, fn) => { try { out[name] = await fn(); } catch (e) { out[name] = 'threw ' + e.name + ': ' + String(e.message).slice(0, 60); } };

  await attempt('inline <script> via DOM', async () => { const s = document.createElement('script'); s.textContent = 'window.__a1 = 1'; document.head.append(s); await tick(); return 'ran=' + (window.__a1 === 1); });
  await attempt('inline <script> via insertAdjacentHTML', async () => { document.body.insertAdjacentHTML('beforeend', '<script>window.__a2 = 1<\/script>'); await tick(); return 'ran=' + (window.__a2 === 1); });
  await attempt('<img onerror> inline handler', async () => { document.body.insertAdjacentHTML('beforeend', '<img src=x onerror="window.__a3 = 1">'); await tick(300); return 'ran=' + (window.__a3 === 1); });
  await attempt('<svg onload> inline handler', async () => { document.body.insertAdjacentHTML('beforeend', '<svg onload="window.__a4 = 1"></svg>'); await tick(); return 'ran=' + (window.__a4 === 1); });
  await attempt('onclick attribute then click', async () => { const b = document.createElement('button'); b.setAttribute('onclick', 'window.__a5 = 1'); document.body.append(b); b.click(); await tick(); return 'ran=' + (window.__a5 === 1); });
  await attempt('onclick property (JS function, not CSP-governed)', async () => { const b = document.createElement('button'); b.onclick = () => { window.__a5b = 1; }; b.click(); return 'ran=' + (window.__a5b === 1) + ' (needs script already running)'; });
  await attempt('javascript: link click', async () => { const a = document.createElement('a'); a.href = 'javascript:window.__a6 = 1'; document.body.append(a); a.click(); await tick(); return 'ran=' + (window.__a6 === 1); });
  await attempt('eval()', async () => { eval('window.__a7 = 1'); return 'ran=' + (window.__a7 === 1); });
  await attempt('new Function()', async () => { new Function('window.__a8 = 1')(); return 'ran=' + (window.__a8 === 1); });
  await attempt("setTimeout('string')", async () => { setTimeout('window.__a9 = 1', 0); await tick(); return 'ran=' + (window.__a9 === 1); });
  await attempt('external <script src=canary>', async () => { const s = document.createElement('script'); s.src = canary + 'x.js'; document.head.append(s); await tick(300); return 'appended'; });
  await attempt('data: <script src>', async () => { const s = document.createElement('script'); s.src = 'data:text/javascript,window.__a10=1'; document.head.append(s); await tick(300); return 'ran=' + (window.__a10 === 1); });
  await attempt('blob: worker', async () => { const w = new Worker(URL.createObjectURL(new Blob(['postMessage(1)']))); await tick(300); return 'created ' + typeof w; });
  await attempt('dynamic import(canary)', async () => { await import(canary + 'm.js'); return 'imported'; });
  await attempt('same-origin <script src=/src/storage.js type=module> (script-src self allows it)', async () => { const s = document.createElement('script'); s.type = 'module'; s.src = '/src/storage.js'; document.head.append(s); await tick(300); return 'appended'; });
  await attempt('fetch(canary)', async () => { await fetch(canary + 'f'); return 'resolved'; });
  await attempt('fetch(canary, no-cors)', async () => { await fetch(canary + 'f2', { mode: 'no-cors' }); return 'resolved'; });
  await attempt('fetch(same-origin /index.html)', async () => { await fetch('/index.html'); return 'resolved'; });
  await attempt('XMLHttpRequest(canary)', async () => new Promise((res) => { const x = new XMLHttpRequest(); x.open('GET', canary + 'x'); x.onerror = () => res('onerror'); x.onload = () => res('loaded'); try { x.send(); } catch (e) { res('threw ' + e.name); } }));
  await attempt('WebSocket(ws canary)', async () => new Promise((res) => { const w = new WebSocket(canary.replace('http', 'ws') + 'w'); w.onerror = () => res('onerror'); w.onopen = () => res('open'); setTimeout(() => res('timeout'), 1500); }));
  await attempt('EventSource(canary)', async () => new Promise((res) => { const e = new EventSource(canary + 'es'); e.onerror = () => res('onerror'); e.onopen = () => res('open'); setTimeout(() => res('timeout'), 1500); }));
  await attempt('navigator.sendBeacon(canary)', async () => 'returned ' + navigator.sendBeacon(canary + 'b', 'x'));
  await attempt('new Image().src = canary', async () => new Promise((res) => { const i = new Image(); i.onload = () => res('loaded'); i.onerror = () => res('onerror'); i.src = canary + 'i.gif'; setTimeout(() => res('timeout'), 1500); }));
  await attempt('<link rel=stylesheet href=canary>', async () => new Promise((res) => { const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = canary + 'c.css'; l.onload = () => res('loaded'); l.onerror = () => res('onerror'); document.head.append(l); setTimeout(() => res('timeout'), 1500); }));
  await attempt('<style>@import canary</style>', async () => { const s = document.createElement('style'); s.textContent = '@import url(' + canary + 'imp.css); body{background:url(' + canary + 'bg.gif)}'; document.head.append(s); await tick(500); return 'appended'; });
  await attempt('<iframe src=canary>', async () => new Promise((res) => { const f = document.createElement('iframe'); f.onload = () => res('loaded'); f.onerror = () => res('onerror'); f.src = canary + 'fr'; document.body.append(f); setTimeout(() => res('timeout'), 1500); }));
  await attempt('<object data=canary>', async () => { const o = document.createElement('object'); o.data = canary + 'o'; document.body.append(o); await tick(400); return 'appended'; });
  await attempt('<embed src=canary>', async () => { const o = document.createElement('embed'); o.src = canary + 'e'; document.body.append(o); await tick(400); return 'appended'; });
  await attempt('<audio src=canary>', async () => { const a = document.createElement('audio'); a.src = canary + 'a.mp3'; a.preload = 'auto'; document.body.append(a); await tick(400); return 'appended'; });
  await attempt('<form action=canary>.submit()', async () => { const f = document.createElement('form'); f.action = canary + 'form'; f.method = 'GET'; f.innerHTML = '<input name=d value=secret>'; document.body.append(f); f.submit(); await tick(500); return 'submitted; still at ' + location.pathname; });
  await attempt('<base href=canary>', async () => { const before = document.baseURI; const b = document.createElement('base'); b.href = canary; document.head.prepend(b); await tick(); return 'baseURI changed=' + (document.baseURI !== before); });
  await attempt('ping attribute', async () => { const a = document.createElement('a'); a.href = '#x'; a.ping = canary + 'ping'; document.body.append(a); a.click(); await tick(300); return 'clicked'; });
  await attempt('window.open(canary) [navigation, not CSP-governed]', async () => { const w = window.open(canary + 'open'); await tick(300); return 'opened=' + (w !== null); });
  await attempt('DNS prefetch link [not CSP-governed]', async () => { const l = document.createElement('link'); l.rel = 'dns-prefetch'; l.href = canary; document.head.append(l); await tick(); return 'appended'; });
  out.__violations = violations;
  return out;
}
"""


def main():
    canary = Canary()
    try:
        with Run() as run:
            b, base = run.browser, run.base
            ctx, page, log = open_app(b, base, storage=state_text([{"name": "Read", "done": []}]))
            ctx.on("page", lambda p: print(f"      [popup opened: {p.url}]", flush=True))

            meta = page.evaluate("() => document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]').content")
            print(f"meta CSP equals spec R1 string: {meta == SPEC_CSP}")
            print(f"   {meta}")
            order = page.evaluate("() => [...document.head.children].map(e => e.tagName.toLowerCase() + (e.getAttribute('http-equiv') ? '[csp]' : ''))")
            print(f"head order: {order}  (csp precedes link and script: {order.index('meta[csp]') < order.index('script')})")
            print("directives absent from the meta policy (frame-ancestors / report-uri / sandbox are ignored in meta anyway):",
                  [d for d in ("frame-ancestors", "report-uri", "report-to", "sandbox", "img-src", "font-src", "frame-src", "worker-src", "media-src", "manifest-src", "navigate-to", "trusted-types", "require-trusted-types-for", "upgrade-insecure-requests") if d not in meta])

            # positive control: the canary answers a CSP-free page
            c2 = new_context(b)
            p2 = c2.new_page()
            p2.goto(base + "__seed__")
            ok = p2.evaluate("async (u) => { try { const r = await fetch(u + 'control'); return r.status; } catch (e) { return 'threw ' + e.message; } }", canary.url)
            print(f"positive control (CSP-free same-site 404 page fetches the canary): {ok}; canary hits: {canary.hits}")
            c2.close()
            canary.hits.clear()

            t0 = time.perf_counter()
            result = page.evaluate(ATTEMPTS, canary.url)
            time.sleep(1.0)
            violations = result.pop("__violations")
            print("--- attempts inside the running app page")
            for k, v in result.items():
                print(f"   {k:<92} {v}")
            print(f"--- securitypolicyviolation events ({len(violations)}):")
            for v in violations:
                print("   ", v)
            print(f"--- canary hits after all attempts: {canary.hits}")
            print(f"--- requests the page itself logged to a non-app origin: {[r for r in log.requests if canary.url in r['url']]}")
            print(f"--- page errors: {log.errors}")
            ctx.close()

            # form-action 'none' with the script blocked (T5: native submission putting the name in a URL)
            ctx = new_context(b)
            page = ctx.new_page()
            page.route("**/src/app.js", lambda route: route.abort())
            log = attach(page)
            page.goto(base)
            page.locator("#new-habit").click()
            page.keyboard.type("No alcohol secret")
            before = page.url
            page.keyboard.press("Enter")
            time.sleep(1.0)
            page.locator("button.btn-primary").click()
            time.sleep(1.0)
            print("--- app.js blocked, the add form submitted natively (Enter and the Add button)")
            print(f"   url before={before} after={page.url}  navigations with query: {[r['url'] for r in log.requests if '?' in r['url']]}")
            print(f"   console: {[c['text'][:140] for c in log.console]}")
            ctx.close()

            # javascript disabled entirely
            ctx = new_context(b, java_script_enabled=False)
            page = ctx.new_page()
            log = attach(page)
            page.goto(base)
            page.locator("#new-habit").fill("No alcohol secret")
            page.keyboard.press("Enter")
            time.sleep(1.0)
            print("--- JavaScript disabled, Enter in the field")
            print(f"   url after={page.url}  requests with query: {[r['url'] for r in log.requests if '?' in r['url']]}")
            print(f"   console: {[c['text'][:140] for c in log.console]}")
            ctx.close()
    finally:
        canary.stop()
    print("done")


if __name__ == "__main__":
    main()
