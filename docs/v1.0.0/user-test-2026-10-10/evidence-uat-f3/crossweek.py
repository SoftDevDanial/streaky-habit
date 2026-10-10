"""Tick one habit's today on 10 days in a row (the clock moves one day at a time) and read the streak line each day.
usage: python -B streaks_crossweek.py <base url>
"""
import sys
from datetime import datetime, timedelta, timezone

from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
start = datetime(2026, 10, 1, 12, 0, tzinfo=timezone(timedelta(hours=8)))
with sync_playwright() as p:
    browser = p.chromium.launch()
    try:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, timezone_id="Asia/Kuala_Lumpur", locale="en-GB")
        page = ctx.new_page()
        page.clock.install(time=start)
        page.goto(BASE)
        field = page.get_by_label("New habit")
        field.click()
        page.keyboard.type("Read 20 pages")
        page.keyboard.press("Enter")
        for day in range(10):
            if day:
                page.clock.run_for(24 * 3600 * 1000)
                page.wait_for_timeout(200)
            row = page.locator("li.habit").first
            row.locator("button.day").last.click()
            line = " ".join(row.locator("p, .meta, .streak").all_inner_texts()) or row.inner_text()
            print((start + timedelta(days=day)).strftime("%a %d %b"), "::", " ".join(line.split())[:80])
        page.screenshot(path=sys.argv[2] if len(sys.argv) > 2 else "crossweek.png", full_page=True)
    finally:
        browser.close()
