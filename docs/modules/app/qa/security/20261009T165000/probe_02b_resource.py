"""T8 continued (probe_02 stopped at its tick wait for the 12-habit case, a bug in that probe's selector).

Worst-case valid histories near the 5 MB origin quota: boot time, one tick, one add, one delete, and the cost of the
rollover re-render. Also R16 (load writes nothing for a readable value).
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
import datetime as dt
import json
import time
from lib import Run, open_app, state_text, stored

ISO = "2026-10-08"


def days(n, start=dt.date(1, 1, 1), step=1):
    return [(start + dt.timedelta(days=i * step)).isoformat() for i in range(n)]


def timed_tick(page, log, label):
    t1 = time.perf_counter()
    page.locator("button.day:last-child").first.click()
    page.wait_for_function("() => document.querySelector('button.day:last-child').getAttribute('aria-pressed') === 'true'")
    print(f"      {label} tick: {round((time.perf_counter() - t1) * 1000)}ms; cons_err={len(log.console_errors())} page_err={len(log.errors)}", flush=True)


def main():
    with Run() as run:
        b, base = run.browser, run.base

        d12 = [days(33_000, dt.date(1 + i * 90, 1, 1)) for i in range(12)]
        raw = state_text([{"name": f"Habit {i}", "done": d12[i]} for i in range(12)])
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=120000)
        print(f"T8 valid 12 habits x 33k days ({len(raw)} chars): boot {round((time.perf_counter() - t0) * 1000)}ms", flush=True)
        timed_tick(page, log, "12 x 33k")
        # the add input is disabled at 12 habits; delete one (opens the dialog, Delete habit) and time it
        t1 = time.perf_counter()
        page.locator(".habit-head .icon-btn").first.click()
        page.get_by_role("button", name="Delete habit").click()
        page.wait_for_function("() => document.querySelectorAll('li.habit').length === 11")
        print(f"      12 x 33k delete: {round((time.perf_counter() - t1) * 1000)}ms", flush=True)
        ctx.close()

        # rollover cost with the biggest valid state: install a clock 1 minute before midnight, run across it
        raw = state_text([{"name": "a", "done": days(400_000)}])
        ctx, page, log = open_app(b, base, storage=raw, fixed_time=None, install_time="2026-10-08T23:59:00+08:00")
        page.wait_for_selector(".habits .habit", timeout=120000)
        t1 = time.perf_counter()
        page.clock.run_for(61_000)
        page.wait_for_function("() => document.querySelector('.date time').getAttribute('datetime') === '2026-10-09'")
        print(f"T8 rollover re-render with 400k valid days: {round((time.perf_counter() - t1) * 1000)}ms; cons_err={len(log.console_errors())}", flush=True)
        ctx.close()

        # alternate days: each key is its own run start in bestStreak
        raw = state_text([{"name": "a", "done": days(190_000, dt.date(1, 1, 1), 2)}])
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=120000)
        print(f"T8 190k alternate days ({len(raw)} chars): boot {round((time.perf_counter() - t0) * 1000)}ms  streak={page.locator('.streak').inner_text()!r}", flush=True)
        ctx.close()

        # R16: a readable value is left byte for byte
        pretty = json.dumps({"version": 1, "habits": [{"name": "Read", "done": [ISO], "color": "red"}], "theme": "dark"}, indent=2)
        ctx, page, log = open_app(b, base, storage=pretty)
        page.wait_for_selector(".habits .habit")
        time.sleep(1.0)
        print(f"R16 readable pretty-printed value with extras: unchanged after load = {stored(page) == pretty}", flush=True)
        ctx.close()

        # large but sane: 12 habits, each 365*5 dates (5 years of daily ticks)
        raw = state_text([{"name": f"Habit {i}", "done": days(1825, dt.date(2021, 10, 8))} for i in range(12)])
        t0 = time.perf_counter()
        ctx, page, log = open_app(b, base, storage=raw)
        page.wait_for_selector(".habits .habit", timeout=60000)
        print(f"Realistic heavy user (12 habits x 5 years daily, {len(raw)} chars): boot {round((time.perf_counter() - t0) * 1000)}ms", flush=True)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
