"""How the renderer behaves while the year 10000 October press hangs (CS-01), Chromium only.

Security finder (read-only), regression 2026-10-15. Run: timeout 300 python -u -B probe_12_hang_memory.py
One headless Chromium, the clock fixed at 10000-10-15 12:00 (UTC+8), and a control at 9999-10-15 in the same browser.
After the press on the row's Year it samples, through the browser's own CDP session (SystemInfo.getProcessInfo), the
renderer processes' CPU time, and through PowerShell the working set of exactly those PIDs, at about 1, 4, 8 and 12 s.
Stops after the last sample, whatever it shows, and closes the browser. Prints JSON lines, writes no file.
"""
import json
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout  # noqa: E402
from probe_11_year10000 import epoch_s, add  # noqa: E402

SAMPLES_S = (1, 4, 8, 12)


def renderers(cdp):
    info = cdp.send("SystemInfo.getProcessInfo")["processInfo"]
    return {p["id"]: round(p["cpuTime"], 2) for p in info if p["type"] == "renderer"}


def working_sets(pids):
    if not pids:
        return {}
    ids = ",".join(str(p) for p in pids)
    cmd = f"Get-Process -Id {ids} -ErrorAction SilentlyContinue | ForEach-Object {{ '{{0}} {{1}}' -f $_.Id, $_.WorkingSet64 }}"
    res = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=30)
    out = {}
    parts = res.stdout.split()
    for i in range(0, len(parts) - 1, 2):
        out[int(parts[i])] = round(int(parts[i + 1]) / 1048576)
    return out


def main():
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            browser = lib.launch(p, "chromium")
            started = time.time()
            try:
                cdp = browser.new_browser_cdp_session()
                control = lib.Session(browser, base, viewport=(1280, 800), clock=epoch_s(9999, 10, 15))
                add(control, "Read")
                t = time.time()
                control.page.click("ul.rows > li.row button.btn-year", timeout=3000)
                open_ms = round((time.time() - t) * 1000)
                opened = control.page.evaluate("() => Array.from(document.querySelectorAll('dialog[open]')).map((d) => d.className).join(',')")
                print(json.dumps({"case": "control 9999-10-15", "press": "returned", "pressMs": open_ms, "open": opened}), flush=True)
                control.close()
                s = lib.Session(browser, base, viewport=(1280, 800), clock=epoch_s(10000, 10, 15))
                add(s, "Read")
                before = renderers(cdp)
                print(json.dumps({"case": "10000-10-15", "step": "before the press", "rendererCpu": before,
                                  "rendererMiB": working_sets(before.keys())}), flush=True)
                t0 = time.time()
                try:
                    s.page.click("ul.rows > li.row button.btn-year", timeout=1000, no_wait_after=True)
                    press = "returned"
                except PlaywrightTimeout:
                    press = "timed out after 1 s"
                print(json.dumps({"case": "10000-10-15", "step": "pressed the row's Year", "press": press}), flush=True)
                for mark in SAMPLES_S:
                    wait = mark - (time.time() - t0)
                    if wait > 0:
                        time.sleep(wait)
                    now = renderers(cdp)
                    print(json.dumps({"case": "10000-10-15", "step": f"sample at {round(time.time() - t0, 1)} s", "rendererCpu": now,
                                      "rendererMiB": working_sets(now.keys())}), flush=True)
            finally:
                t2 = time.time()
                browser.close()
                print(json.dumps({"step": "browser closed", "closeSeconds": round(time.time() - t2, 2), "runSeconds": round(time.time() - started, 1)}), flush=True)
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
