"""Does Event.timeStamp of a click follow Playwright's installed clock, for a mouse click, a tap and a keyboard click?

The re-check asks whether the new edge tests of test_delete.py could pass for the wrong reason, for example because the clock
never moves Event.timeStamp (so "499 ms" would be real elapsed time, a few milliseconds, and "500 ms" the same). This probe
takes the app out of the question: a bare page with one button that records, for every click, event.timeStamp,
performance.now(), Date.now() and event.detail. The setup is the suite's: a context with a touch screen, clock installed at
noon, paused at 12:00:20, then run_for.

For each input it clicks, then runs the clock 499 ms (and in a second row 500 ms, and 1 ms), clicks again, and prints the
difference of the two event.timeStamp values. A control row waits 700 ms of REAL time with the clock paused: the difference
must stay near 0 (so the stamps are not real time).

No server and no project file: the page is set with set_content on about:blank. One headless Chromium, closed at the end.
The script saves its own printed output as probe_timestamp_output.txt next to itself.
Run: python -B probe_timestamp.py   (any cwd)
"""
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
TZ = "Asia/Kuala_Lumpur"
NOON = "2026-10-08T12:00:00+08:00"
PAUSE_AT = "2026-10-08T12:00:20+08:00"
LOG = []

PAGE = """<!doctype html><meta charset=utf-8>
<button id=b style="position:fixed;left:20px;top:20px;width:160px;height:60px">target</button>
<script>
window.rows = [];
document.getElementById('b').addEventListener('click', (e) => {
  window.rows.push({ ts: e.timeStamp, now: performance.now(), date: Date.now(), detail: e.detail });
});
</script>"""


def say(text=""):
    print(text, flush=True)
    LOG.append(text)


def rows(page):
    return page.evaluate("() => window.rows")


def trial(browser, kind, advance_ms, real_wait_ms=0):
    context = browser.new_context(
        viewport={"width": 390, "height": 844}, device_scale_factor=1, timezone_id=TZ, locale="en-US", has_touch=True
    )
    try:
        context.clock.install(time=NOON)
        page = context.new_page()
        page.set_content(PAGE)
        page.clock.pause_at(PAUSE_AT)
        point = (100, 50)

        def press():
            if kind == "mouse":
                page.mouse.click(*point)
            elif kind == "touch":
                page.touchscreen.tap(*point)
            else:
                page.keyboard.press("Enter")

        if kind == "keyboard":
            page.locator("#b").focus()
        press()
        if real_wait_ms:
            time.sleep(real_wait_ms / 1000)
        if advance_ms:
            page.clock.run_for(advance_ms)
        press()
        got = rows(page)
        assert len(got) == 2, got
        return got
    finally:
        context.close()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            say("input     clock moved  real wait  ts1 -> ts2 (event.timeStamp)  diff    performance.now diff  Date.now diff  detail")
            for kind in ("mouse", "touch", "keyboard"):
                for advance, real in ((499, 0), (500, 0), (1, 0), (0, 700)):
                    got = trial(browser, kind, advance, real)
                    d_ts = got[1]["ts"] - got[0]["ts"]
                    d_now = got[1]["now"] - got[0]["now"]
                    d_date = got[1]["date"] - got[0]["date"]
                    say(
                        f"{kind:9} {advance:>6} ms  {real:>6} ms  {got[0]['ts']:.3f} -> {got[1]['ts']:.3f}  {d_ts:9.3f}  {d_now:9.3f}  {d_date:9}  {got[0]['detail']},{got[1]['detail']}"
                    )
        finally:
            browser.close()


try:
    main()
finally:
    (HERE / "probe_timestamp_output.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
