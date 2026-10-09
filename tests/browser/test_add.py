"""R10, R11, R12: adding a habit, rejected names, the twelve-habit limit (app qa.md, Add a habit)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import (
    add_button,
    add_habit,
    cell,
    is_focused,
    plain_state,
    row,
    sample_state,
    shot,
    stored,
    streak,
    type_name,
)

EMOJI = chr(0x1F600)  # one code point, two UTF-16 units


def names(page):
    return page.locator("h3.habit-name").all_inner_texts()


def level_classes(locator):
    return [c for c in locator.get_attribute("class").split() if c[0] == "l" and c[1:].isdigit()]


def test_R10_the_first_habit_on_a_fresh_day(app):
    page = app()
    add_habit(page, "Read 20 pages")
    shot(page, "04-added")

    assert page.locator("p.empty").count() == 0
    assert page.locator("ul.habits > li.habit").count() == 1
    expect(page.locator("#h1-name")).to_have_text("Read 20 pages")
    buttons = row(page, "Read 20 pages").locator("button.day")
    assert buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('aria-pressed'))") == ["false"] * 7
    assert buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('aria-current'))") == [None] * 6 + ["date"]
    assert streak(page, "Read 20 pages") == {"cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1}
    expect(page.locator("#new-habit")).to_have_value("")
    expect(page.locator("#new-habit-msg")).to_have_text("")
    assert page.locator("#new-habit").get_attribute("aria-invalid") is None
    today = cell(page, "2026-10-08")
    expect(today).to_have_attribute("aria-label", "Thu 8 Oct, 0 of 1 habits")
    assert level_classes(today) == ["l0"]
    assert stored(page) == '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'


def test_R10_enter_adds_at_the_bottom_trimmed_and_the_heatmap_recounts(app):
    page = app(storage=sample_state())
    add_habit(page, "  Drink water  ", enter=True)

    assert names(page) == ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm", "Drink water"]
    expect(page.locator("li.habit").nth(3).locator("h3")).to_have_id("h4-name")
    for date, label, level in [
        ("2026-07-20", "Mon 20 Jul, 3 of 4 habits", 3),
        ("2026-10-06", "Tue 6 Oct, 3 of 4 habits", 3),
        ("2026-10-08", "Thu 8 Oct, 2 of 4 habits", 2),
        ("2026-07-21", "Tue 21 Jul, 1 of 4 habits", 1),
        ("2026-08-12", "Wed 12 Aug, 0 of 4 habits", 0),
    ]:
        heat = cell(page, date)
        assert heat.get_attribute("aria-label") == label
        assert level_classes(heat) == [f"l{level}"], date
    assert json.loads(stored(page))["habits"][-1] == {"name": "Drink water", "done": []}
    assert is_focused(page.locator("#new-habit"))


def test_R6_a_habit_just_added_has_no_streak_and_no_best(app):
    page = app(storage=sample_state(), fixed_time="2026-10-12T12:00:00+08:00")
    add_habit(page, "Drink water")
    assert streak(page, "Drink water") == {"cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1}


REJECTED = [
    ("", "Name the habit first."),
    ("   ", "Name the habit first."),
    ("Walk to the end of the street and back after dinner", "Keep it to 40 characters or fewer."),
    ("Read twenty pages before bed every night.", "Keep it to 40 characters or fewer."),
    ("read 20 pages", "You already track this habit."),
    (" STRETCH 10 MINUTES ", "You already track this habit."),
]


@pytest.mark.parametrize("typed, message", REJECTED)
def test_R11_rejected_names_keep_the_text_and_show_one_message(app, typed, message):
    before = sample_state()
    page = app(storage=before)
    field = page.locator("#new-habit")
    field.fill(typed)
    add_button(page).click()

    expect(page.locator("#new-habit-msg")).to_have_text(message)
    expect(page.locator("#new-habit-msg")).to_have_class("field-msg field-error")
    expect(field).to_have_attribute("aria-invalid", "true")
    expect(field).to_have_value(typed)
    assert is_focused(field)
    assert page.locator("li.habit").count() == 3
    assert stored(page) == before
    if typed == "read 20 pages":
        shot(page, "05-error")


def test_R11_exactly_40_characters_is_accepted(app):
    page = app(storage=sample_state())
    add_habit(page, "Read twenty pages before bed every night")
    assert page.locator("li.habit").count() == 4
    assert names(page)[3] == "Read twenty pages before bed every night"
    expect(page.locator("#new-habit-msg")).to_have_text("")


def test_R11_length_counts_code_points_not_utf16_units(app):
    page = app()
    field = page.locator("#new-habit")
    field.fill(EMOJI * 41)
    add_button(page).click()
    expect(page.locator("#new-habit-msg")).to_have_text("Keep it to 40 characters or fewer.")
    assert page.locator("li.habit").count() == 0

    field.fill(EMOJI * 40)
    add_button(page).click()
    assert page.locator("li.habit").count() == 1
    expect(page.locator("#new-habit-msg")).to_have_text("")
    assert names(page) == [EMOJI * 40]


def test_R11_no_message_while_typing(app):
    page = app(storage=sample_state())
    type_name(page, "Walk to the end of the street and back after dinner")
    expect(page.locator("#new-habit-msg")).to_have_text("")
    assert page.locator("#new-habit").get_attribute("aria-invalid") is None


def test_R11_one_message_at_a_time_replaced_then_cleared_on_success(app):
    page = app(storage=sample_state())
    add_button(page).click()
    expect(page.locator("#new-habit-msg")).to_have_text("Name the habit first.")

    type_name(page, "read 20 pages")
    page.keyboard.press("Enter")
    expect(page.locator("#new-habit-msg")).to_have_text("You already track this habit.")

    page.locator("#new-habit").fill("")
    type_name(page, "Drink water")
    page.keyboard.press("Enter")
    expect(page.locator("#new-habit-msg")).to_have_text("")
    expect(page.locator("#new-habit-msg")).to_have_class("field-msg field-error")
    assert page.locator("#new-habit").get_attribute("aria-invalid") is None
    assert page.locator("li.habit").count() == 4


def test_R12_the_twelfth_habit_disables_the_form(app):
    page = app(storage=plain_state(11))
    add_habit(page, "Habit 12")
    shot(page, "06-twelve")

    assert page.locator("li.habit").count() == 12
    expect(page.locator("#new-habit")).to_be_disabled()
    expect(add_button(page)).to_be_disabled()
    message = page.locator("#new-habit-msg")
    expect(message).to_have_text("You track 12 habits, the most this app holds. Delete one to add another.")
    expect(message).to_have_class("field-msg field-note")
    expect(page.locator("#new-habit")).to_have_attribute("aria-describedby", "new-habit-msg")
    expect(page.locator("#new-habit")).to_have_value("")
