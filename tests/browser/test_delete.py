"""R13, R14, R15: the delete dialog, keeping a habit, deleting it (app qa.md, Delete a habit)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import (
    SAMPLE_HABITS,
    add_habit,
    canonical_pair,
    cell,
    center,
    day,
    open_delete_dialog,
    pattern,
    plain_state,
    sample_state,
    shot,
    stored,
    streak,
    trash,
)

LONG_NAME = "Read twenty pages before bed every night"


def dialog(page):
    return page.locator("dialog.dialog")


def cancel(page):
    return dialog(page).get_by_role("button", name="Cancel", exact=True)


def confirm(page):
    return dialog(page).get_by_role("button", name="Delete habit", exact=True)


def level_classes(locator):
    return [c for c in locator.get_attribute("class").split() if c[0] == "l" and c[1:].isdigit()]


def test_R13_the_confirmation_opens_as_a_modal_with_focus_on_cancel(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Read 20 pages")
    shot(page, "07-dialog")

    assert dialog(page).evaluate("(d) => d.open && d.matches(':modal')") is True
    expect(page.locator("#del-title")).to_have_text('Delete "Read 20 pages"?')
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
    before = sample_state()
    page = app(storage=before)
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
    assert stored(page) == before
    expect(trash(page, "Stretch 10 minutes")).to_be_focused()


def test_R14_clicks_inside_the_box_and_drags_out_of_it_keep_the_dialog_open(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Stretch 10 minutes")

    box = dialog(page).bounding_box()
    page.mouse.click(box["x"] + 6, box["y"] + 6)
    expect(dialog(page)).to_have_attribute("open", "")
    expect(page.locator("#del-title")).to_have_text('Delete "Stretch 10 minutes"?')

    x, y = center(page.locator("#del-title"))
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(5, 5)
    page.mouse.up()
    expect(dialog(page)).to_have_attribute("open", "")


def test_R14_esc_after_an_earlier_delete_still_keeps_the_habit(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "No phone after 11pm")
    confirm(page).click()
    expect(page.locator("li.habit")).to_have_count(2)

    open_delete_dialog(page, "Stretch 10 minutes")
    page.keyboard.press("Escape")
    expect(dialog(page)).not_to_have_attribute("open", "")
    assert page.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "Stretch 10 minutes"]


def test_R15_deleting_a_habit_moves_focus_to_the_next_one_and_recounts(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Read 20 pages")
    confirm(page).click()

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
    page = app(storage=sample_state())
    open_delete_dialog(page, "No phone after 11pm")
    confirm(page).click()

    expect(page.locator("#new-habit")).to_be_focused()
    today = cell(page, "2026-10-08")
    assert today.get_attribute("aria-label") == "Thu 8 Oct, 1 of 2 habits"
    assert level_classes(today) == ["l2"]


def test_R15_deleting_the_only_habit_shows_the_empty_message(app):
    page = app()
    add_habit(page, "Read 20 pages")
    day(page, "Read 20 pages", "2026-10-08").click()
    open_delete_dialog(page, "Read 20 pages")
    confirm(page).click()

    expect(page.locator("p.empty")).to_have_count(1)
    assert page.locator("ul.habits").count() == 0
    expect(page.locator("#new-habit")).to_be_focused()
    today = cell(page, "2026-10-08")
    assert today.get_attribute("aria-label") == "Thu 8 Oct, 0 of 0 habits"
    assert level_classes(today) == ["l0"]
    assert stored(page) == '{"version":1,"habits":[]}'


def test_R15_history_goes_with_the_habit(app):
    page = app(storage=sample_state())
    open_delete_dialog(page, "Stretch 10 minutes")
    confirm(page).click()
    expect(page.locator("li.habit")).to_have_count(2)
    add_habit(page, "Stretch 10 minutes")

    new_row = page.locator("li.habit").last
    assert new_row.locator("h3").inner_text() == "Stretch 10 minutes"
    assert pattern(page, "Stretch 10 minutes") == ". . . . . . ."
    assert streak(page, "Stretch 10 minutes") == {
        "cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1
    }


def test_R12_deleting_one_of_twelve_enables_the_form_again(app):
    page = app(storage=plain_state(12))
    open_delete_dialog(page, "Habit 5")
    confirm(page).click()

    expect(page.locator("li.habit")).to_have_count(11)
    expect(page.locator("#new-habit")).to_be_enabled()
    expect(page.get_by_role("button", name="Add", exact=True)).to_be_enabled()
    expect(page.locator("#new-habit-msg")).to_have_text("")
    expect(page.locator("#new-habit-msg")).to_have_class("field-msg field-error")
