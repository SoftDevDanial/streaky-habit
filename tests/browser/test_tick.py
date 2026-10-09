"""R8: ticking a day (app qa.md, Tick the week)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import cell, day, is_focused, pattern, row, sample_state, shot, stored, streak, tab_until

# habit, date, pressed after, current, best, run continues, heat level, heat name, saved afterwards
TICKS = [
    ("Stretch 10 minutes", "2026-10-08", "true", "4 days", "Best 9", True, 4, "Thu 8 Oct, 3 of 3 habits", True),
    ("Read 20 pages", "2026-10-08", "false", "5 days", "Best 14", False, 1, "Thu 8 Oct, 1 of 3 habits", False),
    ("No phone after 11pm", "2026-10-07", "true", "3 days", "Best 4", False, 4, "Wed 7 Oct, 3 of 3 habits", True),
    ("Stretch 10 minutes", "2026-10-04", "true", "7 days", "Best 9", True, 2, "Sun 4 Oct, 2 of 3 habits", True),
    ("Stretch 10 minutes", "2026-10-02", "false", "3 days", "Best 9", False, 0, "Fri 2 Oct, 0 of 3 habits", False),
    ("Read 20 pages", "2026-10-02", "true", "10 days", "Best 14", True, 2, "Fri 2 Oct, 2 of 3 habits", True),
]


@pytest.mark.parametrize("habit, date, pressed, current, best, run, level, name, saved", TICKS)
def test_R8_toggling_a_day_updates_the_bead_in_place(app, habit, date, pressed, current, best, run, level, name, saved):
    page = app(storage=sample_state())
    button = day(page, habit, date)
    handle = button.element_handle()

    button.click()

    assert handle.evaluate("(element) => element.isConnected") is True
    assert handle.get_attribute("aria-pressed") == pressed
    line = streak(page, habit)
    assert (line["cur"], line["best"]) == (current, best)
    strip = row(page, habit).locator("div.strip")
    assert (strip.get_attribute("data-run-continues") is not None) is run
    heat = cell(page, date)
    classes = heat.get_attribute("class").split()
    assert [c for c in classes if c.startswith("l") and c[1:].isdigit()] == [f"l{level}"]
    assert heat.get_attribute("aria-label") == name
    done = next(h for h in json.loads(stored(page))["habits"] if h["name"] == habit)["done"]
    assert (date in done) is saved
    if (habit, date) == ("Stretch 10 minutes", "2026-10-08"):
        shot(page, "03-ticked")


def test_R8_the_name_does_not_change_with_the_state(app):
    page = app(storage=sample_state())
    button = day(page, "Stretch 10 minutes", "2026-10-08")
    button.click()
    expect(button).to_have_attribute("aria-label", "Mark Thu 8 Oct as done")
    expect(button).to_have_attribute("aria-pressed", "true")


def test_R8_keyboard_toggling_keeps_focus(app):
    page = app(storage=sample_state())
    button = day(page, "Stretch 10 minutes", "2026-10-08")
    tab_until(page, button)

    page.keyboard.press("Space")
    expect(button).to_have_attribute("aria-pressed", "true")
    assert is_focused(button)

    page.keyboard.press("Enter")
    expect(button).to_have_attribute("aria-pressed", "false")
    assert is_focused(button)
    assert pattern(page, "Stretch 10 minutes") == "D D . D D D ."
    line = streak(page, "Stretch 10 minutes")
    assert (line["cur"], line["best"]) == ("3 days", "Best 9")


def test_R8_ticking_twice_restores_the_saved_value(app):
    before = sample_state()
    page = app(storage=before)
    button = day(page, "Read 20 pages", "2026-10-05")
    button.click()
    assert json.loads(stored(page)) != json.loads(before)
    button.click()
    assert json.loads(stored(page)) == json.loads(before)
