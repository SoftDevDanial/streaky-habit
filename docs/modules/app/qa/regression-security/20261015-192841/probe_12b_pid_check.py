"""Instrument check for probe_12. Are the renderer ids of CDP SystemInfo.getProcessInfo the OS PIDs that
Get-Process measures? Opens one blank page in headless Chromium, lists the CDP renderer ids, and lists the OS
processes with those ids (name, parent, start time, working set). No server, no app, writes no file.
Run: timeout 120 python -u -B probe_12b_pid_check.py
"""
import json
import subprocess
import sys

sys.dont_write_bytecode = True
import lib  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402


def os_view(pids):
    ids = ",".join(str(p) for p in pids)
    cmd = (f"Get-CimInstance Win32_Process | Where-Object {{ @({ids}) -contains $_.ProcessId }} | "
           "ForEach-Object { '{0}|{1}|{2}|{3}|{4}' -f $_.ProcessId, $_.Name, $_.ParentProcessId, $_.CreationDate, "
           "[math]::Round($_.WorkingSetSize/1MB) }")
    res = subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=30)
    return [line for line in res.stdout.splitlines() if line.strip()]


with sync_playwright() as p:
    browser = lib.launch(p, "chromium")
    try:
        cdp = browser.new_browser_cdp_session()
        ctx = browser.new_context()
        ctx.add_init_script(lib.CLIPBOARD_STANDIN)
        page = ctx.new_page()
        page.goto("about:blank")
        info = cdp.send("SystemInfo.getProcessInfo")["processInfo"]
        ids = [(i["type"], i["id"]) for i in info]
        print(json.dumps({"cdpProcesses": ids}), flush=True)
        print(json.dumps({"osView": os_view([i for _, i in ids])}), flush=True)
        renderer_names = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='chrome-headless-shell.exe'\" | Where-Object { $_.CommandLine -match '--type=renderer' } | "
             "ForEach-Object { '{0}|{1}|{2}' -f $_.ProcessId, $_.ParentProcessId, $_.CreationDate }"],
            capture_output=True, text=True, timeout=30).stdout.split()
        print(json.dumps({"allHeadlessRenderersOnMachine": renderer_names}), flush=True)
    finally:
        browser.close()
