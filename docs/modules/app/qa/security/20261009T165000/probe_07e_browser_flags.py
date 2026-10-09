"""T10 follow-up: which Chromium command line does Playwright use, and does it disable third-party storage partitioning?

Launches headless Chromium the default way, finds its browser process by the PID diff in lib.Run, and prints its
--disable-features and --enable-features switches from the process command line (CIM query). Read-only.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import subprocess
from lib import Run


def main():
    with Run() as run:
        pids = sorted(run.browser_pids)
        print("new browser pids:", pids)
        script = "Get-CimInstance Win32_Process -Filter \"ProcessId=%d\" | ForEach-Object { $_.CommandLine }"
        for pid in pids:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", script % pid], capture_output=True, text=True, timeout=60).stdout.strip()
            if "--type=" in out:
                continue
            print(f"--- pid {pid} command line (main browser process)")
            for token in out.replace('" "', '"\n"').split(" --"):
                t = token.strip()
                if t.startswith(("disable-features", "enable-features", "disable-blink-features", "headless", "user-data-dir", "remote-debugging")):
                    print("   --" + t[:900])
            print("   version:", run.browser.version)
    print("done")


if __name__ == "__main__":
    main()
