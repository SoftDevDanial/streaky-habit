"""R10, R11 and R12, the composer. Adding a habit, the name errors and the twelve-habit state (app qa.md, Feature "Add
a habit").

Each test types and presses with real gestures and reads the DOM, the focus, boxes and the saved text.
"""
import json
import math

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    ARCS12,
    CIRCLE_SEG,
    SAMPLE_HABITS,
    TODAY,
    TODAY_CIRCLE,
    add_button,
    add_habit,
    band_day,
    bin_btn,
    confirm_delete,
    current_block,
    done_btn,
    number,
    plain_state,
    ring_of,
    ring_parts,
    sample_state,
    seg,
    stats_tree,
    stored,
    twelve_state,
    type_name,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
LIMIT_NOTE = "You track 12 habits, the most this app holds. Delete one to add another."
EMPTY = "Name the habit first."
TOO_LONG = "Keep it to 40 characters or fewer."
DUPLICATE = "You already track this habit."

# The message line as spec Contracts draws it, hidden and empty, an error, or the 12-habit note.
QUIET = {"hidden": True, "classes": "field-msg", "text": ""}
NOTE = {"hidden": False, "classes": "field-msg note", "text": LIMIT_NOTE}


def error(text):
    return {"hidden": False, "classes": "field-msg err", "text": text}


COMPOSER_JS = """() => {
  const field = document.querySelector('#nh');
  const message = document.querySelector('#nh-msg');
  return {
    full: document.querySelector('form.composer').classList.contains('is-full'),
    fieldDisabled: field.disabled,
    addDisabled: document.querySelector('#add-btn').disabled,
    value: field.value,
    invalid: field.getAttribute('aria-invalid'),
    describedBy: field.getAttribute('aria-describedby'),
    message: { hidden: message.hidden, classes: message.className, text: message.textContent },
  };
}"""

ACTIVE_JS = """() => {
  const active = document.activeElement;
  if (active === document.querySelector('#nh')) return 'field';
  if (active === document.querySelector('#add-btn')) return 'add';
  if (active === document.body) return 'body';
  return document.querySelector('ul.rows').contains(active) ? 'a control in ul.rows' : active.localName;
}"""

# The frame's visible part is its border box less its borders, read from the computed style rather than from the
# rounded clientHeight, so a row on the edge is not judged by a rounding.
FRAME_JS = """() => {
  const frame = document.querySelector('div.frame');
  const style = getComputedStyle(frame);
  const box = frame.getBoundingClientRect();
  const rows = frame.querySelectorAll('ul.rows > li.row');
  const last = rows[rows.length - 1].getBoundingClientRect();
  return {
    scrollTop: frame.scrollTop,
    scrollHeight: frame.scrollHeight,
    clientHeight: frame.clientHeight,
    visible: { top: box.top + parseFloat(style.borderTopWidth), bottom: box.bottom - parseFloat(style.borderBottomWidth) },
    last: { top: last.top, bottom: last.bottom },
  };
}"""


def composer(page):
    return page.evaluate(COMPOSER_JS)


def active_control(page):
    """'field', 'add', 'body', 'a control in ul.rows' or the tag name of document.activeElement."""
    return page.evaluate(ACTIVE_JS)


def field_top(page):
    return page.locator("#nh").evaluate("(field) => field.getBoundingClientRect().top")


def js_number(value):
    """`Math.round(value * 100) / 100` written as JavaScript writes the number (spec R42)."""
    rounded = math.floor(value * 100 + 0.5) / 100
    return str(int(rounded)) if rounded.is_integer() else repr(rounded)


def arc_path(i, n):
    """The `d` of segment i of n by spec R42's arc rule, worked out here so the test does not reuse src/ring.js."""
    step = 360 / n
    gap = min(22, 0.3 * step)
    large = 1 if step - gap > 180 else 0

    def point(degrees):
        angle = math.radians(degrees)
        return f"{js_number(20 + 15 * math.sin(angle))} {js_number(20 - 15 * math.cos(angle))}"

    return f"M{point(i * step + gap / 2)}A15 15 0 {large} 1 {point((i + 1) * step - gap / 2)}"


# ---------------------------------------------------------------------------------------------------------------


def test_R10_R16_R32_the_first_habit_on_a_fresh_day(app, engine):
    page = app(viewport=PHONE)
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.empty")).to_have_count(0)
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(1)
    expect(rows.locator(":scope > div.r-head > h3#rn-1")).to_have_text("Read 20 pages")
    assert stats_tree(rows.locator(":scope > p.stats")) == [current_block()]
    expect(done_btn(page, "Read 20 pages")).to_have_attribute("aria-pressed", "false")
    state = composer(page)
    assert (state["value"], state["message"], state["invalid"]) == ("", QUIET, None), state
    expect(band_day(page, TODAY)).to_have_attribute("aria-label", "Sat 10 Oct, 0 of 1 habits")
    assert ring_parts(page, f'section.band button.hc[data-key="{TODAY}"] > svg') == ring_of([TODAY_CIRCLE, CIRCLE_SEG, number(10)])
    expect(page.locator("button.ov-btn")).to_have_attribute("aria-label", "Overview, today 0 of 1 habits done")
    assert stored(page) == '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'
    # A mouse click focuses the button in Chromium and nothing in WebKit, and the app moves no focus after an add.
    assert active_control(page) == ("add" if engine == "chromium" else "body")


def test_R10_R32_enter_adds_at_the_bottom_trimmed_and_the_band_recounts(app):
    # The arc rule written here reproduces the goldens' arcs first, so its four-segment paths can be trusted below.
    assert [arc_path(i, 3) for i in range(3)] == ARCS3
    assert [arc_path(i, 12) for i in range(12)] == ARCS12
    page = app(viewport=DESKTOP, storage=sample_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    add_habit(page, "  Drink water  ", enter=True)
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(4)
    assert rows.nth(3).locator(":scope > div.r-head > h3#rn-4").text_content() == "Drink water"
    july = band_day(page, "2026-07-21")
    expect(july).to_have_attribute("aria-label", "Tue 21 Jul, 3 of 4 habits")
    expected = [seg(arc_path(i, 4), i < 3) for i in range(4)] + [number(21)]
    assert ring_parts(page, 'section.band button.hc[data-key="2026-07-21"] > svg') == ring_of(expected)
    expect(band_day(page, TODAY)).to_have_attribute("aria-label", "Sat 10 Oct, 1 of 4 habits")
    saved = json.loads(stored(page))["habits"]
    assert saved == [*SAMPLE_HABITS, {"name": "Drink water", "done": []}]
    assert active_control(page) == "field"


def test_R10_the_frame_scrolls_to_show_the_new_row_cg15(app):
    page = app(viewport=PHONE, storage=plain_state(6))
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(6)
    assert page.evaluate(FRAME_JS)["scrollTop"] == 0
    add_habit(page, "Habit 7", enter=True)
    expect(rows).to_have_count(7)
    expect(rows.nth(6).locator(":scope > div.r-head > h3.r-name")).to_have_text("Habit 7")
    found = page.evaluate(FRAME_JS)
    assert found["scrollHeight"] > found["clientHeight"], found
    assert found["scrollTop"] > 0, found
    assert found["visible"]["top"] <= found["last"]["top"] and found["last"]["bottom"] <= found["visible"]["bottom"], found
    assert active_control(page) == "field"


@pytest.mark.parametrize(
    "viewport, typed, message",
    [
        pytest.param(PHONE, "", EMPTY, id="390x844-nothing"),
        pytest.param(PHONE, "   ", EMPTY, id="390x844-three-spaces"),
        pytest.param(PHONE, "Walk to the end of the street and back after dinner", TOO_LONG, id="390x844-51-characters"),
        pytest.param(PHONE, "Read twenty pages before bed every night.", TOO_LONG, id="390x844-41-characters"),
        pytest.param(PHONE, "read 20 pages", DUPLICATE, id="390x844-other-case"),
        pytest.param(PHONE, " STRETCH 10 MINUTES ", DUPLICATE, id="390x844-spaces-and-capitals"),
        pytest.param(DESKTOP, "", EMPTY, id="1280x800-nothing"),
    ],
)
def test_R11_rejected_names_keep_the_text_and_show_one_message_above_the_field(app, viewport, typed, message):
    page = app(viewport=viewport, storage=sample_state())
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(3)
    saved = stored(page)
    top = field_top(page)
    add_habit(page, typed)
    state = composer(page)
    assert state["message"] == error(message), state
    expect(page.locator("#nh-msg")).to_be_visible()
    message_bottom = page.locator("#nh-msg").evaluate("(line) => line.getBoundingClientRect().bottom")
    assert message_bottom <= field_top(page), (message_bottom, field_top(page))
    assert field_top(page) == top
    assert (state["invalid"], state["value"]) == ("true", typed), state
    # The app puts focus on the field in both engines, also after a click on Add (spec R11).
    assert active_control(page) == "field"
    expect(rows).to_have_count(3)
    assert stored(page) == saved


def test_R11_exactly_40_characters_is_accepted(app):
    name = "Read twenty pages before bed every night"
    assert len(name) == 40
    page = app(storage=sample_state())
    add_habit(page, name)
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(4)
    expect(rows.nth(3).locator(":scope > div.r-head > h3.r-name")).to_have_text(name)
    assert composer(page)["message"] == QUIET


def test_R11_no_message_while_typing(app):
    page = app(storage=sample_state())
    typed = "Walk to the end of the street and back after dinner"
    type_name(page, typed)
    state = composer(page)
    assert (state["value"], state["message"], state["invalid"]) == (typed, QUIET, None), state


def test_R11_typing_clears_a_message_at_once(app):
    page = app(storage=sample_state())
    add_button(page).click()
    state = composer(page)
    assert (state["message"], state["invalid"]) == (error(EMPTY), "true"), state
    # No click on the field first. The error left focus there (R11), and the typing lands where focus is.
    page.keyboard.type("D")
    state = composer(page)
    assert (state["message"], state["invalid"], state["value"]) == (QUIET, None, "D"), state


def test_R11_one_message_at_a_time_replaced_then_cleared_on_success(app):
    page = app(storage=sample_state())
    add_button(page).click()
    assert composer(page)["message"] == error(EMPTY)
    page.keyboard.type("read 20 pages")
    assert composer(page)["message"] == QUIET
    page.keyboard.press("Enter")
    assert composer(page)["message"] == error(DUPLICATE)
    page.locator("#nh").fill("")
    page.keyboard.type("Drink water")
    page.keyboard.press("Enter")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    state = composer(page)
    assert (state["message"], state["invalid"]) == (QUIET, None), state


def test_R12_the_twelfth_habit_closes_the_composer(app):
    page = app(storage=plain_state(11))
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(11)
    add_habit(page, "Habit 12")
    expect(rows).to_have_count(12)
    expect(rows.locator(":scope > div.r-head > button.btn-bin")).to_have_count(12)
    state = composer(page)
    assert state["full"] is True, state
    assert (state["fieldDisabled"], state["addDisabled"]) == (True, True), state
    assert state["message"] == NOTE, state
    assert (state["describedBy"], state["invalid"]) == ("nh-msg", None), state
    assert active_control(page) not in ("field", "a control in ul.rows")


@pytest.mark.parametrize("viewport", [pytest.param(PHONE, id="390x844"), pytest.param(DESKTOP, id="1280x800")])
def test_R12_twelve_habits_at_load(app, viewport):
    page = app(viewport=viewport, storage=twelve_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(12)
    state = composer(page)
    assert (state["full"], state["fieldDisabled"], state["addDisabled"], state["message"]) == (True, True, True, NOTE), state


def test_R12_R15_deleting_one_of_twelve_opens_the_composer_again(app):
    page = app(storage=twelve_state())
    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(12)
    opener = bin_btn(page, "Floss")
    opener.click()
    expect(page.locator("dialog.dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)
    expect(rows).to_have_count(11)
    state = composer(page)
    assert (state["full"], state["fieldDisabled"], state["addDisabled"], state["message"]) == (False, False, False, QUIET), state
