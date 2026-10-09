"""T10 with third-party storage partitioning ON, as in a current Chrome (probe_07d ran on Playwright's default Chromium,
whose command line carries --disable-features=...ThirdPartyStoragePartitioning..., so its frame saw first-party storage).

Relaunches headless Chromium with that default switch removed and a --disable-features list that no longer names
ThirdPartyStoragePartitioning. Checks the new command line, then repeats the framing test: cross-site top
(localhost:p2) over the app (127.0.0.1:p1), and same-site top (127.0.0.1:p2).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from lib import Server, new_context, state_text, row_names, SAMPLE_HABITS, procs_named

SEED = state_text(SAMPLE_HABITS)
DEFAULT_DISABLE = ("--disable-features=AvoidUnnecessaryBeforeUnloadCheckSync,BoundaryEventDispatchTracksNodeRemoval,DestroyProfileOnBrowserClose,"
                   "DialMediaRouteProvider,GlobalMediaControls,HttpsUpgrades,LensOverlay,MediaRouter,PaintHolding,ThirdPartyStoragePartitioning,"
                   "Translate,AutoDeElevate,RenderDocument,OptimizationHints,msForceBrowserSignIn,msEdgeUpdateLaunchServicesPreferredVersion")
MY_DISABLE = DEFAULT_DISABLE.replace("ThirdPartyStoragePartitioning,", "")


def make_top(origin):
    page = f'<!doctype html><title>attacker</title><iframe id="f" src="{origin}/" style="width:390px;height:844px;border:0"></iframe>'.encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    before = procs_named()
    server = Server().start()
    pw = sync_playwright().start()
    browser = None
    top_server = None
    try:
        browser = pw.chromium.launch(headless=True, ignore_default_args=[DEFAULT_DISABLE], args=[MY_DISABLE])
        new = sorted(p for p, _ in procs_named() - before)
        print("[browser] new pids", new, "version", browser.version)
        for pid in new:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", f"Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\" | ForEach-Object {{ $_.CommandLine }}"],
                                 capture_output=True, text=True, timeout=60).stdout
            if "--type=" not in out and out.strip():
                feats = [t for t in out.split(" --") if t.startswith("disable-features")]
                print("   main process disable-features names ThirdPartyStoragePartitioning:", any("ThirdPartyStoragePartitioning" in t for t in feats), "| count of disable-features switches:", len(feats))
        base = server.base
        origin = base.rstrip("/")
        top_server = make_top(origin)
        p2 = top_server.server_address[1]
        for label, top_origin in [("cross-site (top localhost:p2, frame 127.0.0.1:p1)", f"http://localhost:{p2}"),
                                  ("same-site other origin (top 127.0.0.1:p2, frame 127.0.0.1:p1)", f"http://127.0.0.1:{p2}")]:
            ctx = new_context(browser)
            first = ctx.new_page()
            first.goto(base + "__seed__")
            first.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
            first.goto(base)
            first.wait_for_selector("li.habit")
            first_rows = row_names(first)
            top = ctx.new_page()
            top.goto(top_origin + "/frame.html")
            top.wait_for_timeout(2000)
            frames = [f for f in top.frames if f != top.main_frame]
            f = frames[0] if frames else None
            cells = f.evaluate("() => document.querySelectorAll('.cells .hc').length") if f else None
            rows = f.evaluate("() => [...document.querySelectorAll('h3.habit-name')].map(e => e.textContent)") if f else None
            ls = f.evaluate("() => { try { return 'ok, streaks.state ' + (localStorage.getItem('streaks.state') ? 'present' : 'absent'); } catch (e) { return 'threw ' + e.name; } }") if f else None
            print(label)
            print(f"    frame rendered the app (cells={cells}); framed habits={rows}; first-party habits={first_rows}; framed localStorage: {ls}")
            if f:
                f.locator("#new-habit").click()
                top.keyboard.type("Framed add")
                top.keyboard.press("Enter")
                top.wait_for_timeout(300)
                first.reload()
                first.wait_for_selector(".cells .hc")
                print(f"    after a habit is typed into the framed copy, first-party habits: {row_names(first)}")
            ctx.close()
    finally:
        if top_server is not None:
            top_server.shutdown()
            top_server.server_close()
        if browser is not None:
            browser.close()
        pw.stop()
        server.stop()
        time.sleep(1.0)
        left = sorted(p for p, _ in procs_named() - before)
        print("[browser] pids still alive from this run:", left)
    print("done")


if __name__ == "__main__":
    main()
