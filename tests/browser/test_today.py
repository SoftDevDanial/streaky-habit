"""R31, R32 and R16: Done today, and one edit updating every view at once (app qa.md, Feature "Done today and every
view at once").

Each test presses with real gestures and reads the DOM, the focus and the saved text. Scenarios and rows that tick in
a popup use a feature of a later task, so they carry a strict xfail mark naming that task (qa.md, "Scenarios that wait
on a later task", W7 to W13). Two scenarios succeed tests of the 1.0 test_tick.py (spec task 12).
"""
import json
import re

import pytest
from playwright.sync_api import expect

from conftest import (
    NOON,
    SAMPLE_HABITS,
    TODAY,
    add_habit,
    band_day,
    bead,
    best_block,
    bin_btn,
    confirm_delete,
    current_block,
    done_btn,
    encode,
    let_guard_pass,
    p3_day,
    p4_day,
    row,
    row_numbers,
    sample_state,
    stats_tree,
    stored,
    tick,
    write_count,
    year_btn,
)

DESKTOP = (1280, 800)

ON_SEGMENTS_JS = """(svg) => Array.from(svg.querySelectorAll(':scope > .seg')).map((segment) => segment.classList.contains('on'))"""


def segments_on(locator):
    """The `on` state of each segment of the ring svg under `locator`, in order."""
    return locator.evaluate(ON_SEGMENTS_JS)


def has_class(locator, name):
    return locator.evaluate("(node, name) => node.classList.contains(name)", name)


def classes_in(locator, name):
    """How many elements at or under `locator` carry the class `name`."""
    return locator.evaluate("(node, name) => node.querySelectorAll('.' + name).length + (node.classList.contains(name) ? 1 : 0)", name)


def stored_done(page, name):
    return next(habit["done"] for habit in json.loads(stored(page))["habits"] if habit["name"] == name)


# ---------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "habit, pressed, current, best, count, contained",
    [
        ("Stretch 10 minutes", "true", "3 days", "5", 2, True),
        ("Read 20 pages", "false", "3 days", "9", 0, False),
        ("No phone after 11pm", "true", "1 day", "14", 2, True),
    ],
)
def test_R31_R16_done_today_presses_and_unpresses(app, engine, habit, pressed, current, best, count, contained):
    page = app(storage=sample_state())
    handle = done_btn(page, habit).element_handle()
    handle.click()
    assert handle.evaluate("(button) => button.isConnected") is True
    assert handle.get_attribute("aria-pressed") == pressed
    assert row_numbers(page, habit) == {"current": current, "best": best}
    expect(band_day(page, TODAY)).to_have_attribute("aria-label", f"Sat 10 Oct, {count} of 3 habits")
    assert (TODAY in stored_done(page, habit)) is contained
    active = handle.evaluate("(button) => document.activeElement === button")
    if engine == "chromium":
        assert active is True
    else:
        assert active is False
        assert page.evaluate("() => document.activeElement === document.body") is True


def test_R31_keyboard_presses_keep_focus(app):
    page = app(storage=sample_state())
    button = done_btn(page, "Stretch 10 minutes")
    expect(button).to_be_attached()
    is_focused = "(button) => document.activeElement === button"
    for _ in range(40):
        if button.evaluate(is_focused):
            break
        page.keyboard.press("Tab")
    assert button.evaluate(is_focused), "Tab never reached Done today, Stretch 10 minutes"

    page.keyboard.press("Space")
    expect(button).to_have_attribute("aria-pressed", "true")
    assert button.evaluate(is_focused)
    assert row_numbers(page, "Stretch 10 minutes")["current"] == "3 days"

    page.keyboard.press("Enter")
    expect(button).to_have_attribute("aria-pressed", "false")
    assert button.evaluate(is_focused)
    assert row_numbers(page, "Stretch 10 minutes") == {"current": "2 days", "best": "5"}


def test_R31_R16_pressing_twice_restores_the_saved_value(app):
    text = sample_state()
    page = app(storage=text)
    button = done_btn(page, "Stretch 10 minutes")
    button.click()
    expect(button).to_have_attribute("aria-pressed", "true")
    button.click()
    expect(button).to_have_attribute("aria-pressed", "false")
    assert json.loads(stored(page)) == json.loads(text)


@pytest.mark.xfail(strict=True, reason="task 19")
def test_R32_R16_one_done_today_updates_every_place_at_once_and_only_what_changed_moves(app):
    page = app(viewport=DESKTOP, storage=sample_state(), count_writes=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    done_btn(page, "Stretch 10 minutes").click()
    assert write_count(page) == 1

    stretch = row(page, "Stretch 10 minutes")
    assert row_numbers(page, "Stretch 10 minutes") == {"current": "3 days", "best": "5"}
    assert has_class(stretch.locator(".stat.cur > span.val"), "bump")
    assert not has_class(stretch.locator(".stat.best > span.val"), "bump")
    assert has_class(done_btn(page, "Stretch 10 minutes"), "pop")
    assert not has_class(done_btn(page, "Read 20 pages"), "pop")
    assert not has_class(done_btn(page, "No phone after 11pm"), "pop")
    assert classes_in(row(page, "Read 20 pages"), "bump") == 0
    assert classes_in(row(page, "No phone after 11pm"), "bump") == 0

    today = band_day(page, TODAY)
    expect(today).to_have_attribute("aria-label", "Sat 10 Oct, 2 of 3 habits")
    assert segments_on(today.locator(":scope > svg")) == [True, True, False]
    assert has_class(today, "pop")
    assert page.locator("section.band button.hc.pop").count() == 1

    ring = page.locator("button.ov-btn > span.ov-ring")
    assert has_class(ring, "pop")
    expect(page.locator("button.ov-btn")).to_have_attribute("aria-label", "Overview, today 2 of 3 habits done")
    assert segments_on(ring.locator(":scope > svg")) == [True, True, False]

    year_btn(page, "Stretch 10 minutes").click()
    expect(bead(page, TODAY)).to_have_attribute("aria-pressed", "true")
    expect(bead(page, TODAY)).to_have_class(re.compile(r"(?=.*\bon\b)(?=.*\btoday\b)(?=.*\bl\b)"))
    expect(bead(page, "2026-10-09")).to_have_class(re.compile(r"\br\b"))


def test_R32_R37_a_tick_in_p1_over_p3_updates_p3_and_the_row_and_leaves_todays_ring_alone(app):
    page = app(storage=sample_state())
    page.locator("button.ov-btn").click()
    page.locator("dialog.dlg-ov").get_by_role("button", name="Tue 22 Sep, 1 of 3 habits", exact=True).click()
    tick(page, "Read 20 pages").click()

    day = p3_day(page, "2026-09-22")
    expect(day).to_have_attribute("aria-label", "Tue 22 Sep, 2 of 3 habits")
    assert segments_on(day.locator(":scope > svg")) == [True, False, True]
    expect(day).to_have_class(re.compile(r"(?=.*\bpop\b)(?=.*\bis-open\b)"))
    assert row_numbers(page, "Read 20 pages") == {"current": "4 days", "best": "13"}
    read = row(page, "Read 20 pages")
    assert has_class(read.locator(".stat.best > span.val"), "bump")
    assert not has_class(read.locator(".stat.cur > span.val"), "bump")
    expect(band_day(page, "2026-09-22")).to_have_attribute("aria-label", "Tue 22 Sep, 2 of 3 habits")
    expect(page.locator("button.ov-btn")).to_have_attribute("aria-label", "Overview, today 1 of 3 habits done")
    assert not has_class(page.locator("button.ov-btn > span.ov-ring"), "pop")


@pytest.mark.xfail(strict=True, reason="task 20")
def test_R32_R39_a_tick_in_p1_over_p4_updates_p4_and_p3_beneath_it(app):
    page = app(storage=sample_state())
    page.locator("button.ov-btn").click()
    page.locator("dialog.dlg-ov button.btn-all").click()
    page.locator("dialog.dlg-all").get_by_role("button", name="Tue 22 Sep 2026, 1 of 3 habits", exact=True).click()
    tick(page, "Stretch 10 minutes").click()

    expect(p4_day(page, "2026-09-22")).to_have_attribute("aria-label", "Tue 22 Sep 2026, 2 of 3 habits")
    assert has_class(p4_day(page, "2026-09-22"), "pop")
    expect(p3_day(page, "2026-09-22")).to_have_attribute("aria-label", "Tue 22 Sep, 2 of 3 habits")
    assert row_numbers(page, "Stretch 10 minutes") == {"current": "2 days", "best": "5"}
    assert classes_in(row(page, "Stretch 10 minutes"), "bump") == 0


@pytest.mark.xfail(strict=True, reason="task 19")
def test_R32_R34_a_tick_in_p2_updates_p2_the_row_and_the_band(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    year_btn(page, "No phone after 11pm").click()
    bead(page, "2026-10-09").click()

    stats = page.locator("dialog.dlg-year p.yr-stats")
    assert stats_tree(stats) == [current_block(8, "days"), best_block(14)]
    assert has_class(stats.locator(".stat.cur > span.val"), "bump")
    assert row_numbers(page, "No phone after 11pm") == {"current": "8 days", "best": "14"}
    day = band_day(page, "2026-10-09")
    expect(day).to_have_attribute("aria-label", "Fri 9 Oct, 3 of 3 habits")
    expect(day.locator(":scope > svg > circle.c-core")).to_have_count(1)
    expect(day.locator(":scope > svg > text.c-num.on")).to_have_count(1)
    assert has_class(day, "pop")


@pytest.mark.xfail(strict=True, reason="task 22")
def test_R32_R16_each_edit_saves_once_and_opening_or_closing_a_popup_saves_nothing(app):
    page = app(viewport=DESKTOP, storage=sample_state(), count_writes=True, install_time=NOON)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    close = "button.icon-btn[aria-label='Close']"
    year_btn(page, "Read 20 pages").click()
    page.locator(f"dialog.dlg-year {close}").click()
    let_guard_pass(page)
    page.locator("section.band button.btn-all").click()
    page.locator(f"dialog.dlg-all {close}").click()
    let_guard_pass(page)
    band_day(page, "2026-09-22").click()
    page.locator(f"dialog.dlg-day {close}").click()
    let_guard_pass(page)
    assert write_count(page) == 0

    done_btn(page, "Stretch 10 minutes").click()
    assert write_count(page) == 1

    band_day(page, "2026-09-22").click()
    tick(page, "Read 20 pages").click()
    page.locator(f"dialog.dlg-day {close}").click()
    let_guard_pass(page)
    assert write_count(page) == 2

    year_btn(page, "No phone after 11pm").click()
    bead(page, "2026-10-09").click()
    page.locator(f"dialog.dlg-year {close}").click()
    let_guard_pass(page)
    assert write_count(page) == 3

    add_habit(page, "Drink water")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    assert write_count(page) == 4

    bin_btn(page, "Drink water").click()
    confirm_delete(page, bin_btn(page, "Drink water"))
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    assert write_count(page) == 5

    edits = {"Read 20 pages": "2026-09-22", "Stretch 10 minutes": TODAY, "No phone after 11pm": "2026-10-09"}
    on_screen = [{"name": h["name"], "done": sorted(set(h["done"]) | {edits[h["name"]]})} for h in SAMPLE_HABITS]
    assert stored(page) == encode(on_screen)


ONE_HABIT = encode([{"name": "Habit 1", "done": []}])


def open_for_habit_1(page, popup):
    if popup == "P1":
        band_day(page, TODAY).click()
        expect(page.locator("dialog.dlg-day")).to_have_attribute("open", "")
    elif popup == "P2":
        year_btn(page, "Habit 1").click()
        expect(page.locator("dialog.dlg-year")).to_have_attribute("open", "")


def control_for_habit_1(page, popup):
    return {"none": done_btn(page, "Habit 1"), "P1": tick(page, "Habit 1"), "P2": bead(page, TODAY)}[popup]


TSTAT_JS = """(stat) => Array.from(stat.children).map((node) => [[node.localName, ...node.classList].join('.'), node.textContent])"""


def check_after(page, popup, ticked):
    if popup == "none":
        expect(done_btn(page, "Habit 1")).to_have_attribute("aria-pressed", "true" if ticked else "false")
    elif popup == "P1":
        stat = tick(page, "Habit 1").locator(":scope > span.tstat")
        expected = [["span.tcur", "Current 1 day"], ["span", "Best 1"]] if ticked else [["span.tcur.none", "No streak yet"]]
        assert stat.evaluate(TSTAT_JS) == expected
    else:
        stats = page.locator("dialog.dlg-year p.yr-stats")
        assert stats_tree(stats) == ([current_block(1, "day"), best_block(1)] if ticked else [current_block()])


@pytest.mark.parametrize(
    "popup",
    [
        "none",
        "P1",
        pytest.param("P2", marks=pytest.mark.xfail(strict=True, reason="task 19")),
    ],
)
def test_R6_R32_best_back_to_0_removes_the_best_block_in_every_place(app, popup):
    page = app(viewport=DESKTOP, storage=ONE_HABIT)
    stats = row(page, "Habit 1").locator(":scope > p.stats")
    expect(stats).to_be_attached()
    open_for_habit_1(page, popup)
    assert stats_tree(stats) == [current_block()]

    control_for_habit_1(page, popup).click()
    assert stats_tree(stats) == [current_block(1, "day"), best_block(1)]
    check_after(page, popup, ticked=True)

    control_for_habit_1(page, popup).click()
    assert stats_tree(stats) == [current_block()]
    check_after(page, popup, ticked=False)


@pytest.mark.parametrize(
    "popup",
    [
        "P1",
        pytest.param("P2", marks=pytest.mark.xfail(strict=True, reason="task 19")),
    ],
)
def test_R32_a_tick_that_changes_current_and_leaves_best_moves_current_only(app, popup):
    page = app(viewport=DESKTOP, storage=sample_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    if popup == "P1":
        band_day(page, TODAY).click()
        tick(page, "Stretch 10 minutes").click()
    else:
        year_btn(page, "Stretch 10 minutes").click()
        bead(page, TODAY).click()

    stretch = row(page, "Stretch 10 minutes")
    assert row_numbers(page, "Stretch 10 minutes") == {"current": "3 days", "best": "5"}
    assert has_class(stretch.locator(".stat.cur > span.val"), "bump")
    assert not has_class(stretch.locator(".stat.best > span.val"), "bump")
    assert classes_in(row(page, "Read 20 pages"), "bump") == 0
    assert classes_in(row(page, "No phone after 11pm"), "bump") == 0

    if popup == "P1":
        texts = tick(page, "Stretch 10 minutes").locator(":scope > span.tstat").evaluate(TSTAT_JS)
        assert [text for _, text in texts] == ["Current 3 days", "Best 5"]
    else:
        stats = page.locator("dialog.dlg-year p.yr-stats")
        assert stats_tree(stats) == [current_block(3, "days"), best_block(5)]
        assert has_class(stats.locator(".stat.cur > span.val"), "bump")
        assert not has_class(stats.locator(".stat.best > span.val"), "bump")
