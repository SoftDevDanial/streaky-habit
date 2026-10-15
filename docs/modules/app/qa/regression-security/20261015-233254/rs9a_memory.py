"""Re-check of task 9a. Does memory stay flat after a year view opens at 10000-10-15 (the old freeze grew ~90 MiB/s)?

Security finder (read-only), re-check 2026-10-15. Run: timeout 300 python -u -B rs9a_memory.py <chromium|webkit>
One headless browser per case. The working set of every process descended from this probe's own python (the
Playwright driver, the browser and its children, the http.server excluded by PID) is read from Win32_Process
through PowerShell, so no other agent's browser is counted. Samples before the press and at about 1, 4, 8 and 12 s
after it, and again after 20 open and close cycles of P2 and P4. Each sample also checks the page answers within 3 s.
Cases: control 9999-10-15 and 10000-10-15, 1280 x 800. Prints JSON lines, writes no file.
"""
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout  # noqa: E402
from probe_11_year10000 import epoch_s  # noqa: E402

SAMPLES_S = (1, 4, 8, 12)
PS = ("Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,WorkingSetSize,"
      "@{n='Created';e={$_.CreationDate.ToFileTimeUtc()}} | ConvertTo-Json -Compress")


def tree(server_pid):
    res = subprocess.run(["powershell.exe", "-NoProfile", "-Command", PS], capture_output=True, text=True, timeout=60)
    procs = json.loads(res.stdout)
    children = {}
    me = None
    for p in procs:
        children.setdefault(p["ParentProcessId"], []).append(p)
        if p["ProcessId"] == os.getpid():
            me = p
    # A true child is created after its parent. Windows keeps a dead parent's PID in ParentProcessId and reuses PIDs,
    # so without this check an unrelated old process can look like a child (run 1 counted Discord.exe that way).
    out, stack = [], [me]
    while stack:
        parent = stack.pop()
        for p in children.get(parent["ProcessId"], []):
            if p["ProcessId"] == server_pid or p["Created"] < parent["Created"]:
                continue
            if p["Name"].lower() in ("powershell.exe", "conhost.exe") and parent is me:
                continue  # the sampler itself
            out.append(p)
            stack.append(p)
    return out


def sample(server_pid, page):
    procs = tree(server_pid)
    try:
        page.wait_for_function("() => true", timeout=3000)
        answers = True
    except PlaywrightTimeout:
        answers = False
    mib = sorted(((round(p["WorkingSetSize"] / 1048576), p["Name"], p["ProcessId"]) for p in procs), reverse=True)
    return {"answers": answers, "totalMiB": sum(m for m, _, _ in mib), "largest": mib[:3], "processes": len(mib)}


def press(page, selector):
    try:
        page.click(selector, timeout=3000, no_wait_after=True)
        return "returned"
    except PlaywrightTimeout:
        return "timed out after 3 s"


def is_open(page, cls):
    try:
        return page.wait_for_function(f"() => ({{ v: !!document.querySelector('dialog.{cls}')?.open }})", timeout=3000).json_value()["v"]
    except PlaywrightTimeout:
        return None


def run_case(p, engine, base, server_pid, case, clock_s):
    browser = lib.launch(p, engine)
    try:
        s = lib.Session(browser, base, viewport=(1280, 800), clock=clock_s)
        s.page.fill("#nh", "Read", timeout=3000)
        s.page.press("#nh", "Enter", timeout=3000)
        s.page.wait_for_timeout(500)
        print(json.dumps({"engine": engine, "case": case, "step": "before any year view", **sample(server_pid, s.page)}), flush=True)
        for opener, cls, name in (("ul.rows > li.row button.btn-year", "dlg-year", "P2"), ("section.band button.btn-all", "dlg-all", "P4")):
            t0 = time.time()
            result = press(s.page, opener)
            print(json.dumps({"engine": engine, "case": case, "step": f"pressed {name}", "press": result, "open": is_open(s.page, cls)}), flush=True)
            for mark in SAMPLES_S:
                wait = mark - (time.time() - t0)
                if wait > 0:
                    time.sleep(wait)
                print(json.dumps({"engine": engine, "case": case, "step": f"{name} open, sample at {round(time.time() - t0, 1)} s",
                                  **sample(server_pid, s.page)}), flush=True)
            s.page.keyboard.press("Escape")
            s.page.wait_for_timeout(600)
        t1 = time.time()
        opened = 0
        for _ in range(20):
            for opener, cls in (("ul.rows > li.row button.btn-year", "dlg-year"), ("section.band button.btn-all", "dlg-all")):
                if press(s.page, opener) == "returned" and is_open(s.page, cls):
                    opened += 1
                s.page.keyboard.press("Escape")
                s.page.wait_for_timeout(50)
        print(json.dumps({"engine": engine, "case": case, "step": "after 20 open and close cycles of P2 and P4",
                          "opened": opened, "of": 40, "cycleSeconds": round(time.time() - t1, 1),
                          "pageErrors": len(s.errors), **sample(server_pid, s.page)}), flush=True)
        time.sleep(4)
        print(json.dumps({"engine": engine, "case": case, "step": "4 s later", **sample(server_pid, s.page)}), flush=True)
    finally:
        t = time.time()
        browser.close()
        print(json.dumps({"engine": engine, "case": case, "step": "browser closed", "closeSeconds": round(time.time() - t, 2)}), flush=True)


def main():
    engine = sys.argv[1]
    proc, port, _ = lib.start_server()
    base = f"http://127.0.0.1:{port}/"
    try:
        with sync_playwright() as p:
            run_case(p, engine, base, proc.pid, "control 9999-10-15", epoch_s(9999, 10, 15))
            run_case(p, engine, base, proc.pid, "10000-10-15", epoch_s(10000, 10, 15))
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
