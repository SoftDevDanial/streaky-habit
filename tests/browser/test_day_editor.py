"""R36 and R37: the day editor P1, opening it on a day and ticking in it (app qa.md, Feature "The day editor").

Each test opens P1 with real gestures from the band (1280), from P3 or from P4, and reads the DOM, the focus, boxes and
the saved text. On a phone P1 is a bottom sheet over its host, P3 or P4, which gets room and scrolls so the chosen day
stays in sight (rule 4, R36, owner ruling H-03).
"""
import json
import re

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    CIRCLE_SEG,
    NOON,
    TODAY,
    add_habit,
    band_day,
    bin_btn,
    confirm_delete,
    done_btn,
    focus_after_a_click_in_a_popup,
    let_guard_pass,
    p3_day,
    p4_day,
    ring_of,
    ring_parts,
    row_numbers,
    sample_state,
    seg,
    stored,
    tick,
    twelve_state,
    wait_for_close,
    watch_close,
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
    watch = watch_close(page, "dialog.dlg-day")
    if action == "clicks Close":
        day_dialog(page).get_by_role("button", name="Close", exact=True).click()
    elif action == "presses Escape":
        page.keyboard.press("Escape")
    else:
        box = day_dialog(page).locator(":scope > div.dlg-box").bounding_box()
        assert not (box["x"] <= 5 <= box["x"] + box["width"] and box["y"] <= 5 <= box["y"] + box["height"]), box
        page.mouse.click(5, 5)
    wait_for_close(watch)  # the app's close handler has run (conftest watch_close)
    expect(page.locator("button.hc.is-open")).to_have_count(0)
    expect(band_day(page, SEP_22)).to_be_focused()


# What rule 4 measures in P1's host (P3 or P4) and in P1. `p1` is the dialog element, where the sheet rests, and
# `sheet` its div.dlg-box. `padding` is the host body's computed and inline padding-bottom (R36, the room).
SIGHT_JS = """([cls, key]) => {
  const host = document.querySelector(`dialog.${cls}`);
  const body = host.querySelector('div.sheet-body');
  const day = host.querySelector(`button.hc[data-key="${key}"]`);
  const rect = (node) => { const r = node.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, height: r.height }; };
  return {
    hostOpen: host.open,
    p1Open: document.querySelector('dialog.dlg-day').open,
    head: rect(host.querySelector('div.sheet-head')),
    body: rect(body),
    day: rect(day),
    open: day.classList.contains('is-open'),
    sheet: rect(document.querySelector('dialog.dlg-day > div.dlg-box')),
    p1: rect(document.querySelector('dialog.dlg-day')),
    scroll: body.scrollTop,
    maxScroll: body.scrollHeight - body.clientHeight,
    padding: [getComputedStyle(body).paddingBottom, body.style.paddingBottom],
    viewport: [window.innerWidth, window.innerHeight],
  };
}"""

PADDING_JS = "(cls) => { const body = document.querySelector(`dialog.${cls} div.sheet-body`); return [getComputedStyle(body).paddingBottom, body.style.paddingBottom]; }"

HOSTS = {"P3": "dlg-ov", "P4": "dlg-all"}


def open_host(page, host):
    """P3 from the Overview button, and P4 from P3's Year, as a phone user opens them. Returns the host's class."""
    page.locator("button.ov-btn").click()
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    if host == "P4":
        page.locator("dialog.dlg-ov button.btn-all").click()
        expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    return HOSTS[host]


def host_day(page, host, key):
    return p3_day(page, key) if host == "P3" else p4_day(page, key)


def settle(page):
    """Boxes are measured where they rest, once every open dialog's box has ended its rise or its sheet slide."""
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('dialog[open] > div.dlg-box')).every((box) => box.getAnimations().length === 0)",
        timeout=5000,
    )


def assert_p1_is_a_bottom_sheet(found):
    width, height = found["viewport"]
    sheet = found["sheet"]
    assert found["hostOpen"] is True and found["p1Open"] is True, found
    assert abs(sheet["bottom"] - height) <= 1 and abs(sheet["left"]) <= 1 and abs(sheet["right"] - width) <= 1, found


def px(value):
    assert value.endswith("px"), value
    return float(value[:-2])


@pytest.mark.parametrize(
    "viewport, host, key, scroll",
    [
        pytest.param(PHONE, "P3", SEP_22, "0", id="390x844 P3 2026-09-22"),
        pytest.param((360, 780), "P3", SEP_22, "0", id="360x780 P3 2026-09-22"),
        pytest.param(PHONE, "P3", "2026-07-20", "above 0", id="390x844 P3 2026-07-20"),
        pytest.param((360, 780), "P3", "2026-07-20", "above 0", id="360x780 P3 2026-07-20"),
        pytest.param(PHONE, "P4", SEP_22, "any value", id="390x844 P4 2026-09-22"),
        pytest.param(PHONE, "P4", "2025-10-10", "above 0", id="390x844 P4 2025-10-10"),
    ],
)
def test_R36_on_a_phone_the_chosen_day_stays_in_sight_above_p1(app, viewport, host, key, scroll):
    page = app(viewport=viewport, storage=sample_state())
    cls = open_host(page, host)
    host_day(page, host, key).click()
    expect(day_dialog(page)).to_have_attribute("open", "")
    settle(page)
    found = page.evaluate(SIGHT_JS, [cls, key])
    assert_p1_is_a_bottom_sheet(found)
    assert found["head"]["bottom"] <= found["day"]["top"] and found["day"]["bottom"] <= found["sheet"]["top"], found
    assert found["open"] is True, found
    if scroll == "0":
        assert found["scroll"] == 0, found
    elif scroll == "above 0":
        assert found["scroll"] > 0, found


CLOSE_P1 = {
    "presses Escape": lambda page: page.keyboard.press("Escape"),
    "clicks Close": lambda page: day_dialog(page).get_by_role("button", name="Close", exact=True).click(),
}


@pytest.mark.parametrize(
    "viewport, host, key, action, room",
    [
        pytest.param(PHONE, "P3", "2026-07-20", "presses Escape", "P1's height", id="390x844 P3 2026-07-20"),
        pytest.param((360, 780), "P3", "2026-07-20", "clicks Close", "P1's height", id="360x780 P3 2026-07-20"),
        pytest.param(PHONE, "P3", SEP_22, "clicks the viewport point (5, 5)", "P1's height", id="390x844 P3 2026-09-22"),
        pytest.param((800, 900), "P3", "2026-07-20", "presses Escape", "none", id="800x900 P3 2026-07-20"),
        pytest.param(PHONE, "P4", "2025-10-10", "presses Escape", "P1's height", id="390x844 P4 2025-10-10"),
        pytest.param((360, 780), "P4", "2025-10-10", "clicks Close", "P1's height", id="360x780 P4 2025-10-10"),
    ],
)
def test_R36_on_a_phone_the_host_of_p1_gets_room_while_p1_is_open_over_it_and_loses_it_when_p1_closes(
    app, viewport, host, key, action, room
):
    page = app(viewport=viewport, storage=sample_state())
    cls = open_host(page, host)
    assert page.evaluate(PADDING_JS, cls) == ["24px", ""]

    host_day(page, host, key).click()
    expect(day_dialog(page)).to_have_attribute("open", "")
    settle(page)
    found = page.evaluate(SIGHT_JS, [cls, key])
    assert found["hostOpen"] is True and found["p1Open"] is True, found
    if room == "none":
        assert found["padding"] == ["24px", ""], found
    else:
        # P1 sits at the bottom, so its height is the distance from its top edge to the viewport's bottom.
        assert abs(found["p1"]["bottom"] - found["viewport"][1]) <= 1, found
        assert abs(px(found["padding"][0]) - found["p1"]["height"]) <= 1, found
        if host == "P4":
            assert page.evaluate(PADDING_JS, "dlg-ov")[1] == "", "P3 beneath P4 got room"

    # The room is released in the app's close handler, a queued task. In Chromium the browser's own focus restore can
    # show the day focused before it runs, so the read waits for the close event (conftest watch_close).
    watch = watch_close(page, "dialog.dlg-day")
    if action == "clicks the viewport point (5, 5)":
        box = found["sheet"]
        assert not (box["left"] <= 5 <= box["right"] and box["top"] <= 5 <= box["bottom"]), box
        page.mouse.click(5, 5)
    else:
        CLOSE_P1[action](page)
    wait_for_close(watch)
    expect(page.locator(f"dialog.{cls}")).to_have_attribute("open", "")
    expect(host_day(page, host, key)).to_be_focused()
    after = page.evaluate(SIGHT_JS, [cls, key])
    assert after["padding"] == ["24px", ""], after
    assert after["body"]["top"] <= after["day"]["top"] and after["day"]["bottom"] <= after["body"]["bottom"], after
    if host == "P3":
        assert after["maxScroll"] == 0 and after["scroll"] == 0, after
    else:
        expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
        assert page.evaluate(PADDING_JS, "dlg-ov")[1] == ""


@pytest.mark.parametrize(
    "viewport, host, key",
    [
        pytest.param(PHONE, "P3", "2026-07-20", id="390x844 P3 2026-07-20"),
        pytest.param((360, 780), "P4", "2025-10-10", id="360x780 P4 2025-10-10"),
    ],
)
def test_R36_with_twelve_habits_on_a_phone_the_chosen_days_top_meets_the_hosts_head(app, viewport, host, key):
    page = app(viewport=viewport, storage=twelve_state())
    cls = open_host(page, host)
    host_day(page, host, key).click()
    expect(day_dialog(page)).to_have_attribute("open", "")
    settle(page)
    found = page.evaluate(SIGHT_JS, [cls, key])
    assert_p1_is_a_bottom_sheet(found)
    gap = found["sheet"]["top"] - found["head"]["bottom"]
    assert gap < found["day"]["height"], f"precondition, the whole day fits in the gap of {gap} px: {found}"
    assert abs(found["day"]["top"] - found["head"]["bottom"]) <= 1, found
    assert found["scroll"] > 0, found
    assert found["open"] is True, found


def test_R36_R39_a_p4_day_opens_p1_over_p4_on_a_desktop(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    page.locator("section.band button.btn-all").click()
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    page.locator("dialog.dlg-all").get_by_role("button", name="Tue 22 Sep 2026, 1 of 3 habits", exact=True).click()
    expect(day_dialog(page)).to_have_attribute("open", "")
    expect(day_dialog(page).locator("h2#day-title")).to_have_text("Tuesday 22 September")
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    expect(band_day(page, SEP_22)).to_have_class(re.compile(r"\bis-open\b"))
    expect(p4_day(page, SEP_22)).to_have_class(re.compile(r"\bis-open\b"))

    watch = watch_close(page, "dialog.dlg-day")
    page.keyboard.press("Escape")
    wait_for_close(watch)
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    expect(p4_day(page, SEP_22)).to_be_focused()


TICK_NAMES_JS = "() => Array.from(document.querySelectorAll('dialog.dlg-day ul.day-list button.tick'), (tick) => tick.getAttribute('aria-label'))"


def test_R36_p1_lists_the_habits_there_are_when_it_opens(app):
    page = app(viewport=DESKTOP, storage=sample_state(), install_time=NOON)

    def reopen():
        open_from_band(page, SEP_22)
        return page.evaluate(TICK_NAMES_JS), day_dialog(page).locator("p#day-sub").text_content()

    def close():
        watch = watch_close(page, "dialog.dlg-day")
        page.keyboard.press("Escape")
        wait_for_close(watch)

    assert reopen() == (["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"], "1 of 3 habits")
    close()
    add_habit(page, "Drink water", enter=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    assert reopen() == (["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm", "Drink water"], "1 of 4 habits")
    close()
    opener = bin_btn(page, "Stretch 10 minutes")
    opener.click()
    expect(page.locator("dialog.dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    let_guard_pass(page)  # the click on Delete habit holds the page's clicks for 500 ms (R14)
    assert reopen() == (["Read 20 pages", "No phone after 11pm", "Drink water"], "1 of 3 habits")


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
    popped = page.evaluate("() => Array.from(document.querySelectorAll('dialog.dlg-day button.tick.pop'), (tick) => tick.getAttribute('aria-label'))")
    assert popped == ["Read 20 pages"], f"a tick that did not change carries pop (R32): {popped}"
    expect(day_dialog(page)).to_have_attribute("open", "")
    assert tick_stat(page, "Read 20 pages") == [["span.tcur", "Current 4 days"], ["span", "Best 13"]]
    expect(day_dialog(page).locator("p#day-sub")).to_have_text("2 of 3 habits")
    assert mini_ring(page) == three(0, 2)
    expect(band_day(page, SEP_22)).to_have_attribute("aria-label", "Tue 22 Sep, 2 of 3 habits")
    expect(band_day(page, SEP_22)).to_have_class(re.compile(r"\bis-open\b"))
    assert row_numbers(page, "Read 20 pages")["best"] == "13"
    assert write_count(page) == 1
    focus_after_a_click_in_a_popup(engine, handle, "dialog.dlg-day")


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
