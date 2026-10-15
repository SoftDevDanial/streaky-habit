"""How many UTF-16 code units the engine's localStorage takes under the app's key, in a throwaway context.
Doubling, then a binary search, each attempt timed, printed unbuffered (run with python -u -B).
Usage: python -u -B probe_03a_quota.py <engine>
"""
import sys
import time

from playwright.sync_api import sync_playwright

import lib

TRY_JS = """(n) => { const t = performance.now();
  try { localStorage.setItem('streaks.state', 'a'.repeat(n)); localStorage.removeItem('streaks.state'); return [true, performance.now() - t]; }
  catch (e) { return [false, performance.now() - t]; } }"""


def main():
    engine = sys.argv[1]
    proc, port, _ = lib.start_server()
    try:
        with sync_playwright() as p:
            browser = lib.launch(p, engine)
            try:
                s = lib.Session(browser, f"http://127.0.0.1:{port}/", path="__seed__", route_log=False, timeout_ms=60000)
                print("engine", engine, browser.version, flush=True)
                n, ok_n = 1 << 20, 0
                while n <= (1 << 26):
                    ok, ms = s.page.evaluate(TRY_JS, n)
                    print(f"try {n} -> {ok} in {ms:.0f} ms", flush=True)
                    if not ok:
                        break
                    ok_n, n = n, n * 2
                lo, hi = ok_n, n
                while hi - lo > 1024:
                    mid = (lo + hi) // 2
                    ok, ms = s.page.evaluate(TRY_JS, mid)
                    lo, hi = (mid, hi) if ok else (lo, mid)
                print(f"quota_chars between {lo} and {hi}", flush=True)
                s.close()
            finally:
                browser.close()
    finally:
        lib.stop_server(proc, port)


if __name__ == "__main__":
    main()
