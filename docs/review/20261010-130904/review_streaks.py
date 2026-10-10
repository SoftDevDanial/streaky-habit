"""Stakeholder review drive of Streaks: the brainstorm's key flows and rules, real gestures, cold boot, no seed.

usage: python -B review_streaks.py <base url> <out dir>
Writes results.json and one screenshot per check group into <out dir>. Never touches the OS clipboard.
The clock is installed at a fixed local time (Asia/Kuala_Lumpur) so the dates are known, and moved only for the midnight check.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
TZ = timezone(timedelta(hours=8))
NOON = datetime(2026, 10, 10, 12, 0, 0, tzinfo=TZ)  # Saturday 10 October
results, requests = [], []
ISO = "⁦⁧⁨⁩"


def clean(s):
    return "".join(ch for ch in s if ch not in ISO).strip()


def check(group, name, ok, seen):
    results.append({"group": group, "check": name, "result": "PASS" if ok else "FAIL", "seen": seen})
    print(("PASS " if ok else "FAIL ") + group + " :: " + name + " :: " + str(seen)[:160], flush=True)


def new_page(browser, width=390, height=844, at=NOON):
    ctx = browser.new_context(viewport={"width": width, "height": height}, timezone_id="Asia/Kuala_Lumpur", locale="en-GB")
    page = ctx.new_page()
    page.on("request", lambda r: requests.append(r.url))
    page.clock.install(time=at)
    return ctx, page


def rows(page):
    return [clean(t) for t in page.locator("li.habit h3").all_inner_texts()]


def row(page, name):
    return page.locator("li.habit").filter(has=page.locator("h3", has_text=name))


def add(page, name, via="click"):
    field = page.get_by_label("New habit")
    field.click()
    field.fill("")
    page.keyboard.type(name)
    if via == "enter":
        page.keyboard.press("Enter")
    else:
        page.get_by_role("button", name="Add", exact=True).click()


with sync_playwright() as p:
    browser = p.chromium.launch()
    try:
        # Flow 1, first visit
        ctx, page = new_page(browser)
        page.goto(BASE)
        body = page.locator("main").inner_text()
        check("flow 1 first visit", "empty list says how to start", "No habits yet." in body and "Add one you want to do every day." in body, body[:120])
        check("flow 1 first visit", "nothing stored before the first change", page.evaluate("localStorage.length") == 0, page.evaluate("localStorage.length"))
        add(page, "Read 20 pages")
        r = row(page, "Read 20 pages")
        days = r.locator("button.day")
        labels = days.evaluate_all("els => els.map(e => e.getAttribute('aria-label'))")
        check("flow 1 first visit", "habit appears with 7 empty days", days.count() == 7 and all(d.get_attribute("aria-pressed") == "false" for d in days.all()), labels)
        check("flow 1 first visit", "streak line says No streak yet", "No streak yet" in r.inner_text(), clean(r.inner_text())[:80])
        check("rules", "week strip oldest left, today right, names like Mark Tue 6 Oct as done", labels[0] == "Mark Sun 4 Oct as done" and labels[-1] == "Mark Sat 10 Oct as done", [labels[0], labels[-1]])
        page.screenshot(path=str(OUT / "01-first-visit.png"))

        # Flow 2, daily tick on two habits
        add(page, "Stretch 10 minutes", via="enter")
        check("rules", "new habits go to the bottom", rows(page) == ["Read 20 pages", "Stretch 10 minutes"], rows(page))
        for name in ("Read 20 pages", "Stretch 10 minutes"):
            row(page, name).get_by_role("button", name="Mark Sat 10 Oct as done").click()
        lines = [clean(row(page, n).inner_text()) for n in ("Read 20 pages", "Stretch 10 minutes")]
        check("flow 2 daily tick", "each streak goes to 1 day, Best 1", all("1 day" in l and "Best 1" in l for l in lines), [l[:60] for l in lines])
        cell = page.get_by_role("img", name="Sat 10 Oct, 2 of 2 habits")
        check("flow 2 daily tick", "today's heatmap cell reads 2 of 2 habits", cell.count() == 1, cell.count())
        page.screenshot(path=str(OUT / "02-daily-tick.png"))

        # Flow 3, catch up yesterday
        row(page, "Read 20 pages").get_by_role("button", name="Mark Fri 9 Oct as done").click()
        l = clean(row(page, "Read 20 pages").inner_text())
        check("flow 3 catch up", "yesterday counts, 2 days and Best 2", "2 days" in l and "Best 2" in l, l[:60])
        check("flow 3 catch up", "yesterday's heatmap cell reads 1 of 2 habits", page.get_by_role("img", name="Fri 9 Oct, 1 of 2 habits").count() == 1, None)
        row(page, "Stretch 10 minutes").get_by_role("button", name="Mark Sat 10 Oct as done").click()
        l2 = clean(row(page, "Stretch 10 minutes").inner_text())
        check("rules", "untick the only done day: No streak yet and no Best (best is 0, so it is not shown)", "No streak yet" in l2 and "Best" not in l2, l2[:60])
        row(page, "Stretch 10 minutes").get_by_role("button", name="Mark Sat 10 Oct as done").click()
        page.screenshot(path=str(OUT / "03-catch-up.png"))

        # Flow 4, delete with confirm, cancel keeps
        row(page, "Stretch 10 minutes").get_by_role("button", name="Delete Stretch 10 minutes").click()
        dlg = page.locator("dialog[open]")
        title = clean(dlg.inner_text())
        check("flow 4 delete", "dialog asks the brainstorm's question", 'Delete "Stretch 10 minutes"?' in title and "Its history is deleted too." in title, title[:100])
        page.screenshot(path=str(OUT / "04-dialog.png"))
        page.wait_for_timeout(700)
        dlg.get_by_role("button", name="Cancel").click()
        check("flow 4 delete", "Cancel keeps the habit", rows(page) == ["Read 20 pages", "Stretch 10 minutes"], rows(page))
        # A page click within 500 ms of a press in the dialog is dropped (README, Behaviour worth knowing). Prove it, then wait it out.
        row(page, "Stretch 10 minutes").get_by_role("button", name="Delete Stretch 10 minutes").click()
        check("behaviour", "a page click right after Cancel is dropped (the documented guard)", page.locator("dialog[open]").count() == 0, page.locator("dialog[open]").count())
        page.wait_for_timeout(700)
        row(page, "Stretch 10 minutes").get_by_role("button", name="Delete Stretch 10 minutes").click()
        page.wait_for_timeout(700)
        page.locator("dialog[open]").get_by_role("button", name="Delete habit").click()
        page.wait_for_timeout(300)
        stored = page.evaluate("localStorage.getItem('streaks.state')")
        check("flow 4 delete", "Delete habit removes it and its history", rows(page) == ["Read 20 pages"] and "Stretch" not in stored, rows(page))
        check("flow 4 delete", "heatmap counts the current habits only", page.get_by_role("img", name="Sat 10 Oct, 1 of 1 habits").count() == 1, None)
        page.screenshot(path=str(OUT / "05-deleted.png"))

        # C7 kept on the device
        page.reload()
        l = clean(row(page, "Read 20 pages").inner_text())
        check("C7 kept", "reload keeps the habit, its ticks and its streak", rows(page) == ["Read 20 pages"] and "2 days" in l, l[:60])

        # Name rules
        msg = page.locator("#new-habit-msg")
        add(page, "   ")
        check("rules", "empty name error", clean(msg.inner_text()) == "Name the habit first.", clean(msg.inner_text()))
        add(page, "x" * 41)
        check("rules", "41 characters error", clean(msg.inner_text()) == "Keep it to 40 characters or fewer.", clean(msg.inner_text()))
        add(page, "  READ 20 PAGES ")
        check("rules", "duplicate ignoring case and spaces", clean(msg.inner_text()) == "You already track this habit.", clean(msg.inner_text()))
        check("rules", "the typed text stays after an error", page.get_by_label("New habit").input_value() == "  READ 20 PAGES ", page.get_by_label("New habit").input_value())
        add(page, "y" * 40)
        check("rules", "exactly 40 characters is accepted", "y" * 40 in rows(page), len(rows(page)))
        page.screenshot(path=str(OUT / "06-name-rules.png"))

        # At most 12
        n = 3
        while len(rows(page)) < 12:
            add(page, f"Habit {n}")
            n += 1
        field, button = page.get_by_label("New habit"), page.get_by_role("button", name="Add", exact=True)
        note = clean(msg.inner_text())
        check("rules", "at 12 the field and Add are disabled with the note", field.is_disabled() and button.is_disabled() and note == "You track 12 habits, the most this app holds. Delete one to add another.", note)
        page.screenshot(path=str(OUT / "07-twelve.png"), full_page=True)

        # Non-goals: per habit only 7 beads and one delete button, no rename, reorder, export
        per_row = page.locator("li.habit").first.locator("button").count()
        all_buttons = page.locator("button").all_inner_texts()
        check("non-goals", "a habit row holds 7 day buttons and 1 delete button, nothing else", per_row == 8, per_row)
        check("non-goals", "no rename, reorder, export, import, reminder or theme control", not any(w in " ".join(all_buttons).lower() for w in ("rename", "export", "import", "remind", "theme", "move", "edit")), [b for b in all_buttons if b.strip()][:6])
        ctx.close()

        # Unreadable storage resets with a dismissible note
        ctx, page = new_page(browser)
        page.goto(BASE)
        page.evaluate("localStorage.setItem('streaks.state', '{not json')")
        page.reload()
        note = page.get_by_role("status")
        text = clean(page.locator(".note").inner_text()) if page.locator(".note").count() else ""
        check("rules", "unreadable saved data resets with the note", "Your saved habits could not be read, so the list was reset." in text, text)
        page.screenshot(path=str(OUT / "08-reset-note.png"))
        page.get_by_role("button", name="Dismiss note").click()
        check("rules", "the note can be dismissed", page.locator(".note").count() == 0 or not page.locator(".note").is_visible(), None)
        ctx.close()

        # Midnight rollover while open
        ctx, page = new_page(browser, at=datetime(2026, 10, 10, 23, 59, 40, tzinfo=TZ))
        page.goto(BASE)
        add(page, "Read 20 pages")
        before = row(page, "Read 20 pages").locator("button.day").last.get_attribute("aria-label")
        page.clock.run_for(60_000)
        page.wait_for_timeout(200)
        after = row(page, "Read 20 pages").locator("button.day").last.get_attribute("aria-label")
        date = clean(page.locator("time").first.inner_text())
        check("rules", "left open over midnight, the strip moves to the new day within a minute", before == "Mark Sat 10 Oct as done" and after == "Mark Sun 11 Oct as done", [before, after, date])
        ctx.close()

        # Phone 360 px and keyboard
        ctx, page = new_page(browser, width=360, height=780)
        page.goto(BASE)
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.id || document.activeElement.tagName")
        page.keyboard.type("Drink water")
        page.keyboard.press("Enter")
        for _ in range(7):
            page.keyboard.press("Tab")
        lab = page.evaluate("document.activeElement.getAttribute('aria-label')")
        page.keyboard.press("Space")
        pressed = page.evaluate("document.activeElement.getAttribute('aria-pressed')")
        check("rules", "keyboard: Tab to the field, Enter adds, Tab to a day, Space ticks it", rows(page) == ["Drink water"] and pressed == "true", [focused, lab, pressed])
        sw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        check("rules", "360 px phone, no sideways scroll", sw[0] <= sw[1], sw)
        page.screenshot(path=str(OUT / "09-phone-360-keyboard.png"), full_page=True)
        ctx.close()

        # Reduced motion
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        page = ctx.new_page()
        page.on("request", lambda r: requests.append(r.url))
        page.goto(BASE)
        dur = page.evaluate("getComputedStyle(document.querySelector('button.add, .btn-primary')).transitionDuration")
        check("rules", "reduced motion switches transitions off", all(float(d.rstrip('s')) == 0 for d in dur.split(",")), dur)
        ctx.close()
    finally:
        browser.close()

outside = sorted({u for u in requests if not u.startswith(BASE)})
check("privacy", "every request went to the app's own address", not outside, outside)
fails = [r for r in results if r["result"] == "FAIL"]
(OUT / "results.json").write_text(json.dumps({"base": BASE, "checks": results, "requests": len(requests), "fails": len(fails)}, indent=1), encoding="utf-8")
print(f"{len(results) - len(fails)} of {len(results)} checks PASS")
