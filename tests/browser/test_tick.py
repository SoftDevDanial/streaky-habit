"""R8: ticking a day (app qa.md, Tick the week)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import add_habit, cell, day, is_focused, pattern, row, sample_state, shot, stored, streak, tab_until

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
    heat_handle = cell(page, date).element_handle()

    button.click()

    assert handle.evaluate("(element) => element.isConnected") is True
    assert heat_handle.evaluate("(element) => element.isConnected") is True  # the heat cell is set in place too
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


def test_R6_best_goes_back_to_zero_in_place_when_the_only_tick_is_undone(app):
    """The tick path updates the streak line in place, so a best of 0 must remove the span.best it had added."""
    page = app()
    add_habit(page, "Read 20 pages")
    button = day(page, "Read 20 pages", "2026-10-08")

    button.click()
    assert streak(page, "Read 20 pages") == {"cur": "1 day", "cur_class": "cur", "best": "Best 1", "children": 2}

    button.click()
    assert streak(page, "Read 20 pages") == {"cur": "No streak yet", "cur_class": "cur none", "best": None, "children": 1}


# Text writes inside the list only: childList and characterData, not attributes, because a tick always
# sets aria-pressed and the like. Each record is named by the row and the class of the element written.
WATCH_TEXT_WRITES = """() => {
  const seen = [];
  const observer = new MutationObserver((records) => seen.push(...records));
  observer.observe(document.querySelector('ul.habits'), { childList: true, characterData: true, subtree: true });
  return { seen, observer };
}"""
TEXT_WRITES_SO_FAR = """({ seen, observer }) => {
  seen.push(...observer.takeRecords());
  return seen.map((record) => {
    const target = record.target.nodeType === Node.TEXT_NODE ? record.target.parentElement : record.target;
    return target.closest('li.habit').querySelector('.habit-name').textContent + ' ' + target.className;
  });
}"""


def test_JC3_a_tick_writes_only_the_text_that_changed(app):
    """BUILD JC3: replacing a live-region text with an identical one can make a screen reader read it again,
    so ticking Stretch's today (3 days to 4 days, best stays 9) may touch nothing but that one streak text."""
    page = app(storage=sample_state())
    watch = page.evaluate_handle(WATCH_TEXT_WRITES)

    day(page, "Stretch 10 minutes", "2026-10-08").click()

    assert streak(page, "Stretch 10 minutes")["cur"] == "4 days"
    assert watch.evaluate(TEXT_WRITES_SO_FAR) == ["Stretch 10 minutes cur"]


def test_R8_ticking_twice_restores_the_saved_value(app):
    before = sample_state()
    page = app(storage=before)
    button = day(page, "Read 20 pages", "2026-10-05")
    button.click()
    assert json.loads(stored(page)) != json.loads(before)
    button.click()
    assert json.loads(stored(page)) == json.loads(before)
