"""R13, R14, R15: the delete dialog, keeping a habit, deleting it (app qa.md, Delete a habit)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import (
    FSI,
    GUARD_WINDOW_MS,
    NOON,
    PAUSE_AT,
    PDI,
    SAMPLE_HABITS,
    add_habit,
    canonical_pair,
    cell,
    center,
    confirm_delete,
    day,
    dialog_title,
    let_guard_pass,
    level_classes,
    open_delete_dialog,
    pattern,
    plain_state,
    pretty_sample_state,
    sample_state,
    shot,
    state_text,
    stored,
    streak,
    trash,
    write_count,
)

LONG_NAME = "Read twenty pages before bed every night"


def dialog(page):
    return page.locator("dialog.dialog")


def cancel(page):
    return dialog(page).get_by_role("button", name="Cancel", exact=True)


def confirm(page):
    return dialog(page).get_by_role("button", name="Delete habit", exact=True)


def test_R13_the_confirmation_opens_as_a_modal_with_focus_on_cancel(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Read 20 pages")
    shot(page, "07-dialog")

    assert dialog(page).evaluate("(d) => d.open && d.matches(':modal')") is True
    expect(page.locator("#del-title")).to_have_text(dialog_title("Read 20 pages"))
    expect(page.locator("#del-body")).to_have_text("Its history is deleted too.")
    buttons = dialog(page).locator("form.dialog-actions button")
    assert buttons.all_inner_texts() == ["Cancel", "Delete habit"]
    assert buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('value'))") == ["cancel", "delete"]
    expect(cancel(page)).to_be_focused()
    assert page.evaluate("() => getComputedStyle(document.documentElement).overflow") == "hidden"

    page.mouse.wheel(0, 800)
    page.wait_for_timeout(100)
    assert page.evaluate("() => window.scrollY") == 0

    x, y = center(page.locator("button.icon-btn[aria-label='Delete Stretch 10 minutes']"))
    page.mouse.click(x, y)
    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.locator("li.habit").count() == 3
    expect(trash(page, "Read 20 pages")).to_be_focused()


def test_R28_the_open_dialog_has_the_markup_of_the_golden(app):
    """Beyond the qa.md scenarios: the dialog opened for Read 20 pages equals the dialog of delete-dialog.html."""
    page = app(storage=sample_state())
    open_delete_dialog(page, "Read 20 pages")
    live, golden = canonical_pair(page, "delete-dialog.html", "dialog.dialog")
    # The one difference from the golden is the pair of invisible isolate marks inside the title's quotes
    # (spec R13 note, SEC-02); test_SEC02 below pins exactly where they sit.
    live = live.replace(f'"{FSI}', '"').replace(f'{PDI}"', '"')
    assert live == golden


def test_R13_tab_never_leaves_the_dialog_for_the_page(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Read 20 pages")
    for _ in range(4):
        page.keyboard.press("Tab")
        assert page.evaluate("() => !document.querySelector('.page').contains(document.activeElement)")


def test_R13_a_long_name_wraps_in_the_title_and_the_box_keeps_its_width(app):
    page = app(storage=json.dumps({"version": 1, "habits": [{"name": LONG_NAME, "done": []}]}))
    open_delete_dialog(page, LONG_NAME)
    assert dialog(page).bounding_box()["width"] == 350
    assert page.locator("#del-title").bounding_box()["height"] > 28


@pytest.mark.parametrize("action", ["cancel", "escape", "backdrop"])
def test_R14_cancel_esc_and_a_backdrop_click_keep_the_habit(app, action):
    before = pretty_sample_state()  # indented, so a save of the same habits would change the text
    page = app(storage=before, count_writes=True)
    open_delete_dialog(page, "Stretch 10 minutes")
    if action == "cancel":
        cancel(page).click()
    elif action == "escape":
        page.keyboard.press("Escape")
    else:
        page.mouse.click(5, 5)

    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.locator("li.habit").count() == 3
    line = streak(page, "Stretch 10 minutes")
    assert (line["cur"], line["best"]) == ("3 days", "Best 9")
    assert pattern(page, "Stretch 10 minutes") == "D D . D D D ."
    expect(trash(page, "Stretch 10 minutes")).to_be_focused()
    page.wait_for_timeout(100)  # the dialog's close event is a queued task that can still be pending here
    assert write_count(page) == 0
    assert stored(page) == before


def test_R14_clicks_inside_the_box_and_drags_out_of_it_keep_the_dialog_open(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Stretch 10 minutes")

    box = dialog(page).bounding_box()
    page.mouse.click(box["x"] + 6, box["y"] + 6)
    expect(dialog(page)).to_have_attribute("open", "")
    expect(page.locator("#del-title")).to_have_text(dialog_title("Stretch 10 minutes"))

    x, y = center(page.locator("#del-title"))
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(5, 5)
    page.mouse.up()
    expect(dialog(page)).to_have_attribute("open", "")


def test_R14_a_drag_that_starts_on_the_backdrop_and_ends_in_the_box_keeps_the_dialog_open(app):
    """R14 closes on a click pressed AND released outside the box; the other way round is not that."""
    page = app(storage=sample_state())
    open_delete_dialog(page, "Stretch 10 minutes")

    page.mouse.move(5, 5)
    page.mouse.down()
    x, y = center(page.locator("#del-title"))
    page.mouse.move(x, y)
    page.mouse.up()

    expect(dialog(page)).to_have_attribute("open", "")
    expect(page.locator("#del-title")).to_have_text(dialog_title("Stretch 10 minutes"))


def test_R11_the_message_stays_until_the_next_submit_across_a_delete(app):
    """Deleting a habit renders the list again; that must not clear an error the user has not answered."""
    page = app(storage=sample_state(), install_time=NOON)
    page.locator("#new-habit").fill("read 20 pages")
    page.keyboard.press("Enter")
    message = page.locator("#new-habit-msg")
    expect(message).to_have_text("You already track this habit.")

    open_delete_dialog(page, "No phone after 11pm")
    confirm_delete(page)

    expect(page.locator("li.habit")).to_have_count(2)
    expect(message).to_have_text("You already track this habit.")
    expect(message).to_have_class("field-msg field-error")
    expect(page.locator("#new-habit")).to_have_attribute("aria-invalid", "true")
    expect(page.locator("#new-habit")).to_have_value("read 20 pages")


def test_R14_esc_after_an_earlier_delete_still_keeps_the_habit(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "No phone after 11pm")
    confirm_delete(page)
    expect(page.locator("li.habit")).to_have_count(2)

    open_delete_dialog(page, "Stretch 10 minutes")
    page.keyboard.press("Escape")
    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "Stretch 10 minutes"]


def test_R15_deleting_a_habit_moves_focus_to_the_next_one_and_recounts(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "Read 20 pages")
    confirm_delete(page)

    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(page.locator("h3.habit-name")).to_have_count(2)
    assert page.locator("h3.habit-name").all_inner_texts() == ["Stretch 10 minutes", "No phone after 11pm"]
    assert page.locator("h3.habit-name").evaluate_all("(els) => els.map((e) => e.id)") == ["h1-name", "h2-name"]
    expect(trash(page, "Stretch 10 minutes")).to_be_focused()
    for date, label, level in [
        ("2026-07-20", "Mon 20 Jul, 2 of 2 habits", 4),
        ("2026-07-21", "Tue 21 Jul, 1 of 2 habits", 2),
        ("2026-10-08", "Thu 8 Oct, 1 of 2 habits", 2),
    ]:
        assert cell(page, date).get_attribute("aria-label") == label
        assert level_classes(cell(page, date)) == [f"l{level}"], date
    assert json.loads(stored(page)) == {"version": 1, "habits": SAMPLE_HABITS[1:]}
    assert "Read 20 pages" not in stored(page)


def test_R15_deleting_the_bottom_habit_moves_focus_to_the_field(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "No phone after 11pm")
    confirm_delete(page)

    expect(page.locator("#new-habit")).to_be_focused()
    today = cell(page, "2026-10-08")
    assert today.get_attribute("aria-label") == "Thu 8 Oct, 1 of 2 habits"
    assert level_classes(today) == ["l2"]


def test_R15_deleting_the_only_habit_shows_the_empty_message(app):
    page = app(install_time=NOON)
    add_habit(page, "Read 20 pages")
    day(page, "Read 20 pages", "2026-10-08").click()
    open_delete_dialog(page, "Read 20 pages")
    confirm_delete(page)

    expect(page.locator("p.empty")).to_have_count(1)
    assert page.locator("ul.habits").count() == 0
    expect(page.locator("#new-habit")).to_be_focused()
    today = cell(page, "2026-10-08")
    assert today.get_attribute("aria-label") == "Thu 8 Oct, 0 of 0 habits"
    assert level_classes(today) == ["l0"]
    assert stored(page) == '{"version":1,"habits":[]}'


def test_R15_history_goes_with_the_habit(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "Stretch 10 minutes")
    confirm_delete(page)
    expect(page.locator("li.habit")).to_have_count(2)
    add_habit(page, "Stretch 10 minutes")

    new_row = page.locator("li.habit").last
    assert new_row.locator("h3").inner_text() == "Stretch 10 minutes"
    assert pattern(page, "Stretch 10 minutes") == ". . . . . . ."
    assert streak(page, "Stretch 10 minutes") == {
        "cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1
    }


def test_R12_deleting_one_of_twelve_enables_the_form_again(app):
    page = app(storage=plain_state(12), install_time=NOON)
    open_delete_dialog(page, "Habit 5")
    confirm_delete(page)

    expect(page.locator("li.habit")).to_have_count(11)
    expect(page.locator("#new-habit")).to_be_enabled()
    expect(page.get_by_role("button", name="Add", exact=True)).to_be_enabled()
    expect(page.locator("#new-habit-msg")).to_have_text("")
    expect(page.locator("#new-habit-msg")).to_have_class("field-msg field-error")


# ---------------------------------------------------------------------------- SEC-01 (T7): the guard window
#
# The second click of a double click or double tap lands where the first one left the screen. The dialog opens
# under the pointer, and on narrow screens and some desktop layouts "Delete habit" lies where the trash button
# was, so it can confirm the delete. Once a click has closed the dialog, it lands on the page behind it, which
# can tick a bead. These tests freeze an installed clock: Event.timeStamp follows it, so two presses made while
# it is frozen are at the same instant on any machine, and `run_for` moves past the window with no sleep.
# Under a frozen clock a locator click can wait forever (it waits on animation frames), so the gestures are raw
# mouse and touch input.

DESKTOP, PHONE, SMALL_PHONE = (1440, 900), (412, 915), (375, 667)
TAP_THROUGH_HABIT = "No phone after 11pm"  # the third row: its trash button overlaps "Delete habit" at both sizes
SIZES = [(390, 844), PHONE, DESKTOP]
SIZE_IDS = ["390x844", "412x915", "1440x900"]
INPUTS = [False, True]
INPUT_IDS = ["mouse", "touch"]

# The centre of the first day bead whose centre lies outside the open dialog's box, so on the backdrop.
BEAD_ON_THE_BACKDROP = """() => {
  const box = document.querySelector('dialog.dialog').getBoundingClientRect();
  for (const bead of document.querySelectorAll('button.day')) {
    const r = bead.getBoundingClientRect();
    const x = r.x + r.width / 2, y = r.y + r.height / 2;
    if (x < box.left || x > box.right || y < box.top || y > box.bottom) return [x, y];
  }
  return null;
}"""
BEAD_AT_POINT = "([x, y]) => document.elementFromPoint(x, y)?.closest('button.day') != null"


def open_by_mouse(page, name):
    page.mouse.click(*center(trash(page, name)))
    expect(dialog(page)).to_have_attribute("open", "")
    # Its entrance moves the box by a few pixels, so wait for the rest position before measuring it.
    dialog(page).evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")


def click_confirm(page):
    page.mouse.click(*center(confirm(page)))


def press_twice(page, point, touch):
    """A double click, or two taps, at one point: what a person's double click or double tap sends."""
    if touch:
        page.touchscreen.tap(*point)
        page.touchscreen.tap(*point)
    else:
        page.mouse.dblclick(*point)


def overlap_point(page, name):
    """The middle of the screen area where the trash button of `name` and the dialog's 'Delete habit' overlap.

    Found by opening the dialog once and closing it again. It fails when the two do not overlap, or when the
    point does not hit the trash button (dialog closed) and then 'Delete habit' (dialog open), so a layout
    change cannot turn the tests below into tests that pass because nothing overlaps any more.
    """
    trash_box = trash(page, name).bounding_box()
    open_delete_dialog(page, name)
    dialog(page).evaluate("(d) => Promise.all(d.getAnimations().map((a) => a.finished))")  # rest position
    confirm_box = confirm(page).bounding_box()
    left, top = max(trash_box["x"], confirm_box["x"]), max(trash_box["y"], confirm_box["y"])
    right = min(trash_box["x"] + trash_box["width"], confirm_box["x"] + confirm_box["width"])
    bottom = min(trash_box["y"] + trash_box["height"], confirm_box["y"] + confirm_box["height"])
    assert right > left and bottom > top, "the trash button and 'Delete habit' do not overlap at this size"
    point = ((left + right) / 2, (top + bottom) / 2)
    assert page.evaluate("([x, y]) => !!document.elementFromPoint(x, y).closest('button.btn-danger')", point)
    page.keyboard.press("Escape")
    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(trash(page, name)).to_be_focused()  # the close event has run, so it cannot land on the next opening
    assert page.evaluate(
        "([x, y, label]) => document.elementFromPoint(x, y).closest('button')?.getAttribute('aria-label') === label",
        [*point, f"Delete {name}"],
    )
    return point


@pytest.mark.parametrize("viewport", [DESKTOP, PHONE], ids=["1440x900", "412x915"])
@pytest.mark.parametrize("touch", [False, True], ids=["mouse", "touch"])
def test_SEC01_R13_a_double_click_or_tap_on_the_trash_button_cannot_delete(app, viewport, touch):
    before = pretty_sample_state()  # indented, so a save of the same habits would change the text
    page = app(storage=before, viewport=viewport, touch=touch, install_time=NOON, count_writes=True)
    point = overlap_point(page, TAP_THROUGH_HABIT)
    page.clock.pause_at(PAUSE_AT)

    press_twice(page, point, touch)

    expect(dialog(page)).to_have_attribute("open", "")
    expect(page.locator("#del-title")).to_have_text(dialog_title(TAP_THROUGH_HABIT))
    assert page.locator("li.habit").count() == 3
    assert write_count(page) == 0
    assert stored(page) == before

    page.keyboard.press("Escape")  # the way out is still open, and keeping saves nothing
    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(trash(page, TAP_THROUGH_HABIT)).to_be_focused()
    assert page.locator("li.habit").count() == 3
    assert write_count(page) == 0
    assert stored(page) == before


@pytest.mark.parametrize("action", ["cancel", "escape", "backdrop"])
def test_SEC01_R14_cancel_esc_and_a_backdrop_click_work_at_the_instant_of_opening(app, action):
    before = pretty_sample_state()
    page = app(storage=before, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Stretch 10 minutes")

    if action == "cancel":
        page.mouse.click(*center(cancel(page)))
    elif action == "escape":
        page.keyboard.press("Escape")
    else:
        page.mouse.click(5, 5)

    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(trash(page, "Stretch 10 minutes")).to_be_focused()
    assert page.locator("li.habit").count() == 3
    assert write_count(page) == 0
    assert stored(page) == before


def test_SEC01_R13_a_click_inside_the_window_is_ignored_and_one_after_it_deletes(app):
    before = pretty_sample_state()
    page = app(storage=before, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Stretch 10 minutes")

    page.clock.run_for(GUARD_WINDOW_MS - 100)
    click_confirm(page)
    expect(dialog(page)).to_have_attribute("open", "")
    assert page.locator("li.habit").count() == 3
    assert write_count(page) == 0
    assert stored(page) == before

    page.clock.run_for(200)  # 100 ms past the window, at the very point the last click was refused
    click_confirm(page)
    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(page.locator("li.habit")).to_have_count(2)
    assert page.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "No phone after 11pm"]
    assert write_count(page) == 1


def test_SEC01_R13_every_opening_starts_the_window_again(app):
    """A window that ran only from the first opening would let a later opening's second click through."""
    before = pretty_sample_state()
    page = app(storage=before, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Stretch 10 minutes")
    let_guard_pass(page)
    page.keyboard.press("Escape")
    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(trash(page, "Stretch 10 minutes")).to_be_focused()  # the close event has run (it is queued after close())

    open_by_mouse(page, "Stretch 10 minutes")  # a new opening click, long after the first window ended
    click_confirm(page)
    expect(dialog(page)).to_have_attribute("open", "")
    assert page.locator("li.habit").count() == 3
    assert stored(page) == before

    let_guard_pass(page)
    click_confirm(page)
    expect(page.locator("li.habit")).to_have_count(2)


def test_SEC01_R15_a_deliberate_click_after_the_window_deletes(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "Stretch 10 minutes")
    confirm_delete(page)

    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "No phone after 11pm"]


def test_SEC01_R15_enter_on_delete_habit_after_the_window_deletes(app):
    page = app(storage=sample_state(), install_time=NOON)
    open_delete_dialog(page, "Stretch 10 minutes")
    let_guard_pass(page)

    page.keyboard.press("Tab")  # from Cancel to Delete habit
    expect(confirm(page)).to_be_focused()
    page.keyboard.press("Enter")

    expect(page.locator("li.habit")).to_have_count(2)
    assert page.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "No phone after 11pm"]


# The second click after the dialog has closed. The first press closes the dialog and the second lands on the
# page behind it. A tick changes saved data, so each case checks that the habits and the stored text are exactly
# what the first press alone leaves, and that a day bead really lay under the second press (so the case cannot
# pass because nothing was there). Focus is not asserted: the second press's mousedown moves it either way.


@pytest.mark.parametrize("touch", INPUTS, ids=INPUT_IDS)
@pytest.mark.parametrize("size", SIZES, ids=SIZE_IDS)
def test_SEC01_R14_a_double_click_or_tap_on_the_backdrop_does_not_tick_the_bead_behind(app, size, touch):
    before = pretty_sample_state()
    page = app(storage=before, viewport=size, touch=touch, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    point = page.evaluate(BEAD_ON_THE_BACKDROP)
    assert point is not None, "no day bead lies on the backdrop at this size"

    press_twice(page, point, touch)

    expect(dialog(page)).not_to_have_attribute("open", "")  # the first press closed it
    assert page.evaluate(BEAD_AT_POINT, point)
    assert write_count(page) == 0
    assert stored(page) == before


@pytest.mark.parametrize("touch", INPUTS, ids=INPUT_IDS)
def test_SEC01_R14_a_double_click_or_tap_on_the_backdrop_does_not_press_add(app, touch):
    """At 390 x 844 Add lies on the backdrop. A name typed before the dialog opened must not be added by the second press."""
    before = pretty_sample_state()
    page = app(storage=before, touch=touch, install_time=NOON, count_writes=True)
    add = page.locator("form.add button[type=submit]")
    point = center(add)
    page.locator("#new-habit").fill("Drink water")
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    box = dialog(page).bounding_box()
    assert not (box["x"] <= point[0] <= box["x"] + box["width"] and box["y"] <= point[1] <= box["y"] + box["height"])

    press_twice(page, point, touch)

    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.evaluate("([x, y]) => document.elementFromPoint(x, y)?.closest('button')?.textContent === 'Add'", point)
    expect(page.locator("#new-habit")).to_have_value("Drink water")  # an add would have emptied the field
    assert page.locator("li.habit").count() == 3
    assert write_count(page) == 0
    assert stored(page) == before


@pytest.mark.parametrize("touch", INPUTS, ids=INPUT_IDS)
@pytest.mark.parametrize("size", [SMALL_PHONE, (360, 640)], ids=["375x667", "360x640"])
def test_SEC01_R14_a_double_click_or_tap_on_cancel_does_not_tick_the_bead_behind(app, size, touch):
    """On small phones Cancel lies over the second habit's beads (the dialog is centred and the rows are 196 px apart)."""
    before = pretty_sample_state()
    page = app(storage=before, viewport=size, touch=touch, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    point = center(cancel(page))

    press_twice(page, point, touch)

    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.evaluate(BEAD_AT_POINT, point)
    assert write_count(page) == 0
    assert stored(page) == before


@pytest.mark.parametrize("touch", INPUTS, ids=INPUT_IDS)
def test_SEC01_R15_a_double_click_or_tap_on_delete_habit_deletes_once_and_ticks_nothing(app, touch):
    """On small phones the habit below slides up under 'Delete habit' as the row goes, so a bead lies under the second press."""
    page = app(storage=pretty_sample_state(), viewport=SMALL_PHONE, touch=touch, install_time=NOON, count_writes=True)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    let_guard_pass(page)  # past the opening window, so the first press is a deliberate one
    point = center(confirm(page))

    press_twice(page, point, touch)

    expect(page.locator("li.habit")).to_have_count(2)
    assert page.locator("h3.habit-name").all_inner_texts() == ["Stretch 10 minutes", "No phone after 11pm"]
    assert page.evaluate(BEAD_AT_POINT, point)
    assert json.loads(stored(page)) == {"version": 1, "habits": SAMPLE_HABITS[1:]}  # no tick on the survivors
    assert write_count(page) == 1


@pytest.mark.parametrize("key", ["Enter", "Space", "Escape"])
def test_SEC01_R14_closing_with_the_keyboard_does_not_hold_the_next_click(app, key):
    """Keyboard paths are unchanged: only a mouse or touch click in the dialog starts the page's guard window.

    Enter and Space act on Cancel, which has focus when the dialog opens.
    """
    page = app(storage=sample_state(), install_time=NOON)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    page.keyboard.press(key)
    expect(dialog(page)).not_to_have_attribute("open", "")
    expect(trash(page, "Read 20 pages")).to_be_focused()

    bead = day(page, "Stretch 10 minutes", "2026-10-08")
    expect(bead).to_have_attribute("aria-pressed", "false")
    page.mouse.click(*center(bead))  # at the very instant the dialog closed

    expect(bead).to_have_attribute("aria-pressed", "true")


def test_SEC01_R14_the_page_listens_again_once_the_window_has_passed(app):
    page = app(storage=sample_state(), install_time=NOON)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    page.mouse.click(5, 5)  # the backdrop
    expect(dialog(page)).not_to_have_attribute("open", "")
    bead = day(page, "Stretch 10 minutes", "2026-10-08")

    page.clock.run_for(GUARD_WINDOW_MS - 100)
    page.mouse.click(*center(bead))
    expect(bead).to_have_attribute("aria-pressed", "false")  # still inside the window: ignored

    page.clock.run_for(200)
    page.mouse.click(*center(bead))
    expect(bead).to_have_attribute("aria-pressed", "true")


def test_SEC01_R14_cancel_still_works_right_after_a_click_inside_the_box(app):
    """The page's guard must not reach into the dialog: a press in the box and then Cancel at once both work."""
    page = app(storage=sample_state(), install_time=NOON)
    page.clock.pause_at(PAUSE_AT)
    open_by_mouse(page, "Read 20 pages")
    box = dialog(page).bounding_box()
    page.mouse.click(box["x"] + 6, box["y"] + 6)  # the padding: no button, the dialog stays open
    expect(dialog(page)).to_have_attribute("open", "")

    page.mouse.click(*center(cancel(page)))

    expect(dialog(page)).not_to_have_attribute("open", "")


# ---------------------------------------------------------------------------- SEC-02 and SEC-06: the name in the title
#
# An unterminated bidirectional override in a name reorders the text after it, including the title's own closing
# quote and question mark: the dialog showed `Delete "?"ereh txet desreveR` for the name "<RLO>Reversed text here".
# Two controls in `openDeleteDialog` work together. SEC-02: the name sits between FSI and PDI, so an override cannot
# get out of it. SEC-06: the title's copy of the name has the bidi format characters taken out (U+202A to U+202E,
# U+2066 to U+2069, U+0085, U+001C to U+001E, U+2029), because the isolate alone is not enough. A U+2069 or a
# paragraph separator inside the name closes the title's own isolate early, and an isolate opener inside the name
# with no closer takes the title's U+2069, so after a right-to-left letter the title's isolate resolved right to
# left and drew the closing quote and the question mark on the wrong side of the name. Only the title's copy
# changes: the list row, the trash button's label and the stored name keep the name as typed. Stacks of combining
# marks that overprint the line are not covered (accepted for v1.0, spec R13 note), so no test claims them.

RLO, RLE, RLI = chr(0x202E), chr(0x202B), chr(0x2067)
LRI = chr(0x2066)
PARAGRAPH_SEPARATOR = chr(0x2029)
ALEF, MEEM = chr(0x05D0), chr(0x0645)
SHALOM = "".join(chr(code) for code in (0x05E9, 0x05DC, 0x05D5, 0x05DD))  # a Hebrew word
OLAM = "".join(chr(code) for code in (0x05E2, 0x05D5, 0x05DC, 0x05DD))  # another one

# Each row is (the name as stored, the name as the title shows it).
OVERRIDING_NAMES = {  # SEC-02: the five of the audit
    "rlo first": (RLO + "Reversed text here", "Reversed text here"),
    "rlo in the middle": ("Read 20 pages" + RLO + " dleiys .gnp", "Read 20 pages dleiys .gnp"),
    "three rlo": ("a" + RLO + "b" + RLO + "c" + RLO, "abc"),
    "rle": (RLE + "abc def", "abc def"),
    "rli": (RLI + "abc def", "abc def"),
}
ISOLATE_OPENER_NAMES = {  # SEC-06: the title with only the isolate moved the quotes for these, and before SEC-02 it did not
    "alef lri abc": (ALEF + LRI + "abc", ALEF + "abc"),
    "alef fsi abc": (ALEF + FSI + "abc", ALEF + "abc"),
    "hebrew word lri": (SHALOM + LRI, SHALOM),
    "hebrew word space abc lri": (SHALOM + " abc" + LRI, SHALOM + " abc"),
    "arabic meem lri x": (MEEM + LRI + "x", MEEM + "x"),
}
CLOSED_EARLY_NAMES = {  # the SEC-02 residual (b), closed by the same strip, and its cost: a matched pair goes too
    "x pdi rlo y z": ("x" + PDI + RLO + "y z", "xy z"),
    "x paragraph separator rlo y z": ("x" + PARAGRAPH_SEPARATOR + RLO + "y z", "xy z"),
    "alef lri abc pdi": (ALEF + LRI + "abc" + PDI, ALEF + "abc"),
}
UNMARKED_NAMES = {  # nothing to take out: the title shows exactly the name
    "plain": ("Read 20 pages", "Read 20 pages"),
    "hebrew": (SHALOM + " " + OLAM, SHALOM + " " + OLAM),
    "alef alone": (ALEF, ALEF),
}
TITLE_NAMES = {**OVERRIDING_NAMES, **ISOLATE_OPENER_NAMES, **CLOSED_EARLY_NAMES, **UNMARKED_NAMES}

# The fourteen characters the title leaves out, and sixteen that it keeps: the ones next to the ranges, and other
# invisible and directional characters (U+200E, U+200F and U+061C are marks too, but not the ones that need to go).
STRIPPED = [0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069, 0x0085, 0x001C, 0x001D, 0x001E, 0x2029]
KEPT = [0x0084, 0x0086, 0x001B, 0x001F, 0x2028, 0x202F, 0x2065, 0x206A, 0x200E, 0x200F, 0x061C, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF]


def spaced(codes):
    """'x', then each code point followed by 'x': a name cannot end in white space, and the letters keep each one apart."""
    return "x" + "".join(chr(code) + "x" for code in codes)


def left_over(text):
    """The characters of `text` that are not printable ASCII, as U+XXXX, for an assertion message."""
    return [f"U+{ord(character):04X}" for character in text if not 32 <= ord(character) < 127]

# Where the title's quotes, question mark and name characters are drawn, in reading order: the line (in line
# heights) times 100000, plus the left edge. A character with no width (the marks themselves) is left out of `inside`.
TITLE_CHARACTER_SPOTS = """() => {
  const heading = document.querySelector('#del-title');
  const node = heading.firstChild;
  const lineHeight = parseFloat(getComputedStyle(heading).lineHeight);
  const top = heading.getBoundingClientRect().top;
  const spot = (index) => {
    const range = document.createRange();
    range.setStart(node, index);
    range.setEnd(node, index + 1);
    const box = range.getBoundingClientRect();
    return { width: box.width, place: Math.round((box.top - top) / lineHeight) * 100000 + box.left };
  };
  const text = node.data;
  const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
  const inside = [];
  for (let i = open + 1; i < close; i++) if (spot(i).width > 0) inside.push(spot(i).place);
  return { nodes: heading.childNodes.length, children: heading.children.length,
    open: spot(open).place, inside, close: spot(close).place, question: spot(question).place };
}"""


def open_title_dialog(app, name):
    """The app with one habit stored as `name`, and its delete dialog open."""
    page = app(storage=state_text([{"name": name, "done": []}]))
    page.locator("button.icon-btn").first.click()
    expect(dialog(page)).to_have_attribute("open", "")
    return page


@pytest.mark.parametrize("stored_name, shown_name", list(TITLE_NAMES.values()), ids=list(TITLE_NAMES))
def test_SEC02_SEC06_R13_the_title_shows_the_name_without_format_characters_and_its_quotes_stay_in_place(
    app, stored_name, shown_name
):
    page = open_title_dialog(app, stored_name)

    spots = page.evaluate(TITLE_CHARACTER_SPOTS)
    assert spots["nodes"] == 1 and spots["children"] == 0  # still one text node and no child element (R24)
    assert spots["inside"], "the name drew no character"
    assert spots["open"] < min(spots["inside"]), spots
    assert max(spots["inside"]) < spots["close"] < spots["question"], spots
    assert page.locator("#del-title").text_content() == dialog_title(shown_name)


def test_SEC06_R13_every_character_of_the_stripped_set_is_left_out_of_the_title(app):
    page = open_title_dialog(app, spaced(STRIPPED))

    title = page.locator("#del-title").text_content()
    assert title == dialog_title("x" * (len(STRIPPED) + 1)), f"characters in the title: {left_over(title)}"


def test_SEC06_R13_the_neighbours_of_the_stripped_ranges_and_other_invisible_characters_stay_in_the_title(app):
    name = spaced(KEPT)
    page = open_title_dialog(app, name)

    title = page.locator("#del-title").text_content()
    assert title == dialog_title(name), f"characters in the title: {left_over(title)}"


def test_SEC06_R13_only_the_titles_copy_loses_the_characters_and_the_habit_named_in_it_is_the_one_deleted(app):
    """The list row, the trash button's label and the stored name keep the name as typed; opening saves nothing."""
    name = ALEF + LRI + "abc"
    before = state_text([{"name": name, "done": []}, {"name": "Other habit", "done": []}])
    page = app(storage=before, install_time=NOON, count_writes=True)
    page.locator("button.icon-btn").first.click()
    expect(dialog(page)).to_have_attribute("open", "")

    assert page.locator("#del-title").text_content() == dialog_title(ALEF + "abc")
    assert page.locator("h3.habit-name").all_inner_texts() == [name, "Other habit"]
    assert page.locator("button.icon-btn").first.get_attribute("aria-label") == f"Delete {name}"
    assert stored(page) == before
    assert write_count(page) == 0

    confirm_delete(page)

    expect(page.locator("li.habit")).to_have_count(1)
    assert page.locator("h3.habit-name").all_inner_texts() == ["Other habit"]
    assert json.loads(stored(page))["habits"] == [{"name": "Other habit", "done": []}]
