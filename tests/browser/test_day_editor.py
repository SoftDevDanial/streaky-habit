"""R36 and R37: the day editor P1, opening it on a day and ticking in it (app qa.md, Feature "The day editor").

Each test opens P1 with real gestures from the band (1280) or from P3 (phone) and reads the DOM, the focus, boxes and
the saved text. Task 20 adds the scenario and the two W22 rows that open P1 from P4.
"""
import json
import re

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    CIRCLE_SEG,
    TODAY,
    band_day,
    done_btn,
    p3_day,
    ring_of,
    ring_parts,
    row_numbers,
    sample_state,
    seg,
    stored,
    tick,
    write_count,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
SEP_22 = "2026-09-22"

TICKS_JS = """() => Array.from(document.querySelectorAll('dialog.dlg-day ul.day-list > li')).map((item) => {
  const button = item.firstElementChild;
  const use = button.querySelector(':scope > span.tbox > svg > use');
  const stat = button.querySelector(':scope > span.tstat');
  return {
    item: [item.className, item.childElementCount],
    button: [button.localName, button.getAttribute('type'), button.getAttribute('aria-label'),
      button.getAttribute('aria-pressed'), button.classList.contains('on'), button.getAttribute('aria-describedby')],
    parts: Array.from(button.children).map((node) => [node.localName, node.className, node.id || null]),
    check: use && [use.parentElement.getAttribute('aria-hidden'), use.getAttribute('href')],
    name: button.querySelector(':scope > span.tname').textContent,
    stat: Array.from(stat.children).map((node) => [[node.localName, ...node.classList].join('.'), node.textContent]),
  };
})"""

OPEN_MARKS_JS = """(key) => {
  const days = Array.from(document.querySelectorAll('button.hc'));
  return {
    chosen: days.filter((day) => day.dataset.key === key).map((day) => day.classList.contains('is-open')),
    others: days.filter((day) => day.dataset.key !== key && day.classList.contains('is-open')).length,
  };
}"""


def day_dialog(page):
    return page.locator("dialog.dlg-day")


def open_from_band(page, key):
    band_day(page, key).click()
    expect(day_dialog(page)).to_have_attribute("open", "")


def tick_stat(page, name):
    return tick(page, name).locator(":scope > span.tstat").evaluate(
        "(stat) => Array.from(stat.children).map((node) => [[node.localName, ...node.classList].join('.'), node.textContent])"
    )


def mini_ring(page):
    return ring_parts(page, "dialog.dlg-day div.day-mini > svg")


def three(*on):
    return ring_of([seg(ARCS3[i], i in on) for i in range(3)])


def focus_after_a_mouse_click_in_p1(engine, handle):
    """In Chromium a clicked button keeps focus. WebKit focuses no button on a mouse press (spec Invariants, engine
    note), and inside a modal dialog it leaves focus on the dialog element, not on body (measured at task 18, qa.md
    "Engine differences by design"). Either way the app has not moved focus."""
    active = handle.evaluate("(button) => document.activeElement === button ? 'tick' : document.activeElement.localName + '.' + document.activeElement.className")
    assert active == ("tick" if engine == "chromium" else "dialog.dlg-day"), active


# ---------------------------------------------------------------------------------------------------------------


def test_R36_R42_a_band_day_opens_p1(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    page.locator("section.band").get_by_role("button", name="Tue 22 Sep, 1 of 3 habits", exact=True).click()
    dialog = day_dialog(page)
    expect(dialog).to_have_attribute("open", "")
    assert dialog.evaluate("(d) => d.matches(':modal')") is True
    expect(tick(page, "Read 20 pages")).to_be_focused()

    expect(dialog.locator("div.day-mini")).to_have_attribute("aria-hidden", "true")
    assert mini_ring(page) == three(2)
    expect(dialog.locator("h2#day-title")).to_have_text("Tuesday 22 September")
    expect(dialog.locator("p#day-sub")).to_have_text("1 of 3 habits")

    expected = [
        ("Read 20 pages", "false", False, "ts-1", [["span.tcur", "Current 4 days"], ["span", "Best 9"]]),
        ("Stretch 10 minutes", "false", False, "ts-2", [["span.tcur", "Current 2 days"], ["span", "Best 5"]]),
        ("No phone after 11pm", "true", True, "ts-3", [["span.tcur.none", "No streak yet"], ["span", "Best 14"]]),
    ]
    ticks = page.evaluate(TICKS_JS)
    assert len(ticks) == 3
    for found, (name, pressed, on, stat_id, stat) in zip(ticks, expected):
        assert found["item"] == ["", 1], found
        assert found["button"] == ["button", "button", name, pressed, on, stat_id], found
        assert found["parts"] == [["span", "tbox", None], ["span", "tname", None], ["span", "tstat", stat_id]], found
        assert found["check"] == ["true", "#i-check"], found
        assert found["name"] == name
        assert found["stat"] == stat, found

    marks = page.evaluate(OPEN_MARKS_JS, SEP_22)
    assert marks["chosen"] and all(marks["chosen"]), marks
    assert marks["others"] == 0, marks


@pytest.mark.parametrize("action", ["clicks Close", "presses Escape", "clicks the viewport point (5, 5)"])
def test_R36_R40_p1_closes_and_gives_focus_back_to_its_day(app, action):
    page = app(viewport=DESKTOP, storage=sample_state())
    open_from_band(page, SEP_22)
    if action == "clicks Close":
        day_dialog(page).get_by_role("button", name="Close", exact=True).click()
    elif action == "presses Escape":
        page.keyboard.press("Escape")
    else:
        box = day_dialog(page).locator(":scope > div.dlg-box").bounding_box()
        assert not (box["x"] <= 5 <= box["x"] + box["width"] and box["y"] <= 5 <= box["y"] + box["height"]), box
        page.mouse.click(5, 5)
    page.wait_for_function("() => !document.querySelector('dialog.dlg-day').open", timeout=5000)
    expect(page.locator("button.hc.is-open")).to_have_count(0)
    expect(band_day(page, SEP_22)).to_be_focused()


SIGHT_JS = """([key]) => {
  const host = document.querySelector('dialog.dlg-ov');
  const day = host.querySelector(`div.ovg-rows button.hc[data-key="${key}"]`);
  const rect = (node) => { const r = node.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, right: r.right }; };
  return {
    hostOpen: host.open,
    head: rect(host.querySelector('div.sheet-head')),
    day: rect(day),
    open: day.classList.contains('is-open'),
    sheet: rect(document.querySelector('dialog.dlg-day > div.dlg-box')),
    scroll: host.querySelector('div.sheet-body').scrollTop,
    viewport: [window.innerWidth, window.innerHeight],
  };
}"""


# Blocker B1 of BUILD.md task 18, not a later task. At 390x844 and 360x780 the golden P3 fits its 12 weeks with no
# overflow (its sheet body's scrollHeight equals its clientHeight), so no scroll can lift 2026-07-20 above P1. These two
# rows stay visible and strict until the orchestrator rules on rule 4 against the golden layout.
BLOCKED_B1 = pytest.mark.xfail(strict=True, reason="blocked B1, P3 has no scroll room on a phone (BUILD.md task 18)")


@pytest.mark.parametrize(
    "viewport, key, scrolled",
    [
        pytest.param(PHONE, SEP_22, False, id="390x844 P3 2026-09-22"),
        pytest.param((360, 780), SEP_22, False, id="360x780 P3 2026-09-22"),
        pytest.param(PHONE, "2026-07-20", True, marks=BLOCKED_B1, id="390x844 P3 2026-07-20"),
        pytest.param((360, 780), "2026-07-20", True, marks=BLOCKED_B1, id="360x780 P3 2026-07-20"),
    ],
)
def test_R36_on_a_phone_the_chosen_day_stays_in_sight_above_p1(app, viewport, key, scrolled):
    page = app(viewport=viewport, storage=sample_state())
    page.locator("button.ov-btn").click()
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    p3_day(page, key).click()
    expect(day_dialog(page)).to_have_attribute("open", "")
    # The sheet slides up for 260 ms. Its resting place is measured once its animation has ended.
    page.wait_for_function(
        "() => document.querySelector('dialog.dlg-day > div.dlg-box').getAnimations().length === 0", timeout=5000
    )
    found = page.evaluate(SIGHT_JS, [key])
    width, height = found["viewport"]
    sheet = found["sheet"]
    assert found["hostOpen"] is True, found
    assert abs(sheet["bottom"] - height) <= 1 and abs(sheet["left"]) <= 1 and abs(sheet["right"] - width) <= 1, found
    assert found["head"]["bottom"] <= found["day"]["top"] and found["day"]["bottom"] <= sheet["top"], found
    assert found["open"] is True, found
    if scrolled:
        assert found["scroll"] > 0, found
    else:
        assert found["scroll"] == 0, found


def test_R36_R3_a_day_opens_p1_when_there_are_no_habits(app):
    page = app(viewport=DESKTOP)
    page.locator("section.band").get_by_role("button", name="Sat 10 Oct, 0 of 0 habits", exact=True).click()
    dialog = day_dialog(page)
    expect(dialog).to_have_attribute("open", "")
    expect(dialog.locator("h2#day-title")).to_have_text("Saturday 10 October")
    expect(dialog.locator("p#day-sub")).to_have_text("0 of 0 habits")
    assert mini_ring(page) == ring_of([CIRCLE_SEG])
    items = dialog.locator("ul.day-list > li")
    expect(items).to_have_count(1)
    expect(items).to_have_class("day-empty")
    expect(items).to_have_text("No habits yet.")
    expect(dialog.locator("button.tick")).to_have_count(0)
    expect(dialog.get_by_role("button", name="Close", exact=True)).to_be_focused()


def test_R37_R32_ticking_a_past_day_in_p1(app, engine):
    page = app(viewport=DESKTOP, storage=sample_state(), count_writes=True)
    open_from_band(page, SEP_22)
    handle = tick(page, "Read 20 pages").element_handle()
    handle.click()
    assert handle.evaluate("(button) => button.isConnected") is True
    assert handle.get_attribute("aria-pressed") == "true"
    assert handle.evaluate("(button) => ['on', 'pop'].every((name) => button.classList.contains(name))") is True
    expect(day_dialog(page)).to_have_attribute("open", "")
    assert tick_stat(page, "Read 20 pages") == [["span.tcur", "Current 4 days"], ["span", "Best 13"]]
    expect(day_dialog(page).locator("p#day-sub")).to_have_text("2 of 3 habits")
    assert mini_ring(page) == three(0, 2)
    expect(band_day(page, SEP_22)).to_have_attribute("aria-label", "Tue 22 Sep, 2 of 3 habits")
    expect(band_day(page, SEP_22)).to_have_class(re.compile(r"\bis-open\b"))
    assert row_numbers(page, "Read 20 pages")["best"] == "13"
    assert write_count(page) == 1
    focus_after_a_mouse_click_in_p1(engine, handle)


def test_R37_keyboard_ticks_keep_focus_and_a_second_tick_restores_the_saved_value(app):
    text = sample_state()
    page = app(viewport=DESKTOP, storage=text)
    day = band_day(page, SEP_22)
    expect(day).to_be_attached()
    is_focused = "(node) => document.activeElement === node"
    for _ in range(100):
        if day.evaluate(is_focused):
            break
        page.keyboard.press("Tab")
    assert day.evaluate(is_focused), "Tab never reached the band's 2026-09-22 button"
    page.keyboard.press("Enter")
    expect(day_dialog(page)).to_have_attribute("open", "")
    expect(tick(page, "Read 20 pages")).to_be_focused()

    page.keyboard.press("Tab")
    stretch = tick(page, "Stretch 10 minutes")
    expect(stretch).to_be_focused()
    page.keyboard.press("Space")
    expect(stretch).to_have_attribute("aria-pressed", "true")
    assert stretch.evaluate(is_focused)
    expect(day_dialog(page).locator("p#day-sub")).to_have_text("2 of 3 habits")

    page.keyboard.press("Enter")
    expect(stretch).to_have_attribute("aria-pressed", "false")
    assert stretch.evaluate(is_focused)
    expect(day_dialog(page).locator("p#day-sub")).to_have_text("1 of 3 habits")
    assert json.loads(stored(page)) == json.loads(text)


def test_R37_R31_ticking_today_in_p1_presses_done_today(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    open_from_band(page, TODAY)
    tick(page, "Stretch 10 minutes").click()
    expect(done_btn(page, "Stretch 10 minutes")).to_have_attribute("aria-pressed", "true")
    assert row_numbers(page, "Stretch 10 minutes")["current"] == "3 days"
    expect(band_day(page, TODAY)).to_have_attribute("aria-label", "Sat 10 Oct, 2 of 3 habits")
