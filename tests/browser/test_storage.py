"""R16, R17, R18: kept on the device, unreadable saved data, storage failures (app qa.md, Kept on the device)."""
import json

import pytest
from playwright.sync_api import expect

from conftest import (
    BASE_URL,
    SAMPLE_HABITS,
    add_habit,
    cell,
    day,
    open_delete_dialog,
    record,
    sample_state,
    shot,
    stored,
    streak,
    write_count,
)

NOTE_TEXT = "Your saved habits could not be read, so the list was reset."
EMPTY_STATE = '{"version":1,"habits":[]}'


def test_R16_changes_survive_a_reload_and_a_closed_tab(app):
    page = app(storage=sample_state())
    day(page, "Stretch 10 minutes", "2026-10-08").click()
    add_habit(page, "Drink water")
    open_delete_dialog(page, "No phone after 11pm")
    page.get_by_role("button", name="Delete habit", exact=True).click()
    expect(page.locator("li.habit")).to_have_count(3)

    def check_screen(screen):
        assert screen.locator("h3.habit-name").all_inner_texts() == ["Read 20 pages", "Stretch 10 minutes", "Drink water"]
        expect(day(screen, "Stretch 10 minutes", "2026-10-08")).to_have_attribute("aria-pressed", "true")
        line = streak(screen, "Stretch 10 minutes")
        assert (line["cur"], line["best"]) == ("4 days", "Best 9")

    page.reload()
    check_screen(page)
    stretch = dict(SAMPLE_HABITS[1], done=SAMPLE_HABITS[1]["done"] + ["2026-10-08"])
    assert json.loads(stored(page)) == {
        "version": 1,
        "habits": [SAMPLE_HABITS[0], stretch, {"name": "Drink water", "done": []}],
    }

    page.close()
    reopened = page.context.new_page()
    reopened.goto(BASE_URL)
    check_screen(reopened)


# case, raw text. The 13-habit case is built, the rest are written out.
THIRTEEN = json.dumps({"version": 1, "habits": [{"name": f"H{n}", "done": []} for n in range(1, 14)]})
UNREADABLE = [
    ("not JSON", "{"),
    ("JSON null", "null"),
    ("an array", "[]"),
    ("wrong version", '{"version":2,"habits":[]}'),
    ("version as text", '{"version":"1","habits":[]}'),
    ("no habits array", '{"version":1,"habits":{}}'),
    ("13 habits", THIRTEEN),
    ("empty name", '{"version":1,"habits":[{"name":"","done":[]}]}'),
    ("untrimmed name", '{"version":1,"habits":[{"name":" Read","done":[]}]}'),
    ("41 characters", '{"version":1,"habits":[{"name":"Read twenty pages before bed every night.","done":[]}]}'),
    ("duplicate ignoring case", '{"version":1,"habits":[{"name":"Read","done":[]},{"name":"read","done":[]}]}'),
    ("name not text", '{"version":1,"habits":[{"name":5,"done":[]}]}'),
    ("done not a list", '{"version":1,"habits":[{"name":"Read","done":"2026-10-08"}]}'),
    ("impossible date", '{"version":1,"habits":[{"name":"Read","done":["2026-02-30"]}]}'),
    ("date with a time", '{"version":1,"habits":[{"name":"Read","done":["2026-10-08T00:00"]}]}'),
    ("habit is null", '{"version":1,"habits":[null]}'),
]


@pytest.mark.parametrize("case, raw", UNREADABLE, ids=[case for case, _ in UNREADABLE])
def test_R17_unreadable_saved_data_resets_the_list_and_shows_the_note(app, case, raw):
    page = app(storage=raw)
    if case == "not JSON":
        shot(page, "08-note")

    first = page.locator(".col-main > *").first
    assert first.get_attribute("class") == "note"
    assert first.get_attribute("role") == "status"
    expect(first.locator("p.note-text")).to_have_text(NOTE_TEXT)
    dismiss = first.get_by_role("button", name="Dismiss note", exact=True)
    assert dismiss.get_attribute("class") == "icon-btn"
    assert dismiss.locator("use").get_attribute("href") == "#i-x"
    assert page.locator("p.empty").count() == 1 and page.locator("ul.habits").count() == 0
    assert cell(page, "2026-10-08").get_attribute("aria-label") == "Thu 8 Oct, 0 of 0 habits"
    assert stored(page) == EMPTY_STATE


READABLE = [
    ("empty list", '{"version":1,"habits":[]}'),
    ("extra properties", '{"version":1,"habits":[{"name":"Read","done":["2026-10-08"],"color":"red"}],"theme":"dark"}'),
    ("unsorted and duplicated days", '{"version":1,"habits":[{"name":"Read","done":["2026-10-08","2026-10-07","2026-10-08"]}]}'),
    ("a day after today", '{"version":1,"habits":[{"name":"Read","done":["2026-10-09"]}]}'),
    ("a __proto__ key", '{"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"polluted":true}}]}'),
]


@pytest.mark.parametrize("case, raw", READABLE, ids=[case for case, _ in READABLE])
def test_R17_readable_edge_cases_load_without_a_note(app, case, raw):
    page = app(storage=raw)
    assert page.locator("div.note").count() == 0
    assert stored(page) == raw  # loading writes nothing

    if case == "empty list":
        expect(page.locator("p.empty")).to_have_count(1)
    elif case == "extra properties":
        assert page.locator("h3.habit-name").all_inner_texts() == ["Read"]
        expect(day(page, "Read", "2026-10-08")).to_have_attribute("aria-pressed", "true")
        day(page, "Read", "2026-10-07").click()
        assert "color" not in stored(page) and "theme" not in stored(page)
    elif case == "unsorted and duplicated days":
        line = streak(page, "Read")
        assert (line["cur"], line["best"]) == ("2 days", "Best 2")
    elif case == "a day after today":
        assert page.locator('button[data-date="2026-10-09"]').count() == 0
        line = streak(page, "Read")
        assert (line["cur"], line["best"]) == ("No streak yet", "Best 1")
    else:
        assert page.locator("h3.habit-name").all_inner_texts() == ["Read"]
        assert page.evaluate("() => ({}).polluted") is None


def test_R17_dismiss_removes_the_note_moves_focus_to_the_field_and_it_does_not_come_back(app):
    page = app(storage="{", count_writes=True)
    assert write_count(page) == 1  # the reset itself, the one save R16 allows besides add, tick and delete
    page.get_by_role("button", name="Dismiss note", exact=True).click()
    expect(page.locator("div.note")).to_have_count(0)
    assert page.locator("p.empty").count() == 1
    expect(page.locator("#new-habit")).to_be_focused()
    assert write_count(page) == 1  # Dismiss changes nothing else (R17), so it saves nothing

    page.reload()
    assert page.locator("div.note").count() == 0

    page.goto(BASE_URL + "__seed__")
    page.evaluate("() => localStorage.setItem('streaks.state', '{')")
    page.goto(BASE_URL)
    expect(page.locator("div.note")).to_have_count(1)


def test_R17_on_desktop_the_note_sits_in_the_left_column(app):
    page = app(storage="{", viewport=(1280, 800))
    note = page.locator("div.note").bounding_box()
    column = page.locator("div.col-main").bounding_box()
    assert (column["x"], column["width"]) == (168, 500)
    assert column["x"] <= note["x"] and note["x"] + note["width"] <= column["x"] + column["width"]
    assert page.locator("section.heat").bounding_box()["x"] == 732


def throwing_storage_script(target, name):
    return f"""Object.defineProperty({target}, '{name}', {{
      configurable: true,
      get() {{ throw new DOMException('denied', 'SecurityError'); }},
    }});"""


def test_R18_storage_that_cannot_be_used_at_all(app):
    page = app(init_script=throwing_storage_script("window", "localStorage"), record=True)
    assert page.locator("p.empty").count() == 1
    assert page.locator("div.note").count() == 0

    add_habit(page, "Read 20 pages")
    day(page, "Read 20 pages", "2026-10-08").click()
    line = streak(page, "Read 20 pages")
    assert (line["cur"], line["best"]) == ("1 day", "Best 1")
    log = record(page)
    assert log.errors == []
    assert [m for m in log.console if m["type"] == "error"] == []


def test_R18_a_save_that_fails(app):
    script = """Storage.prototype.setItem = function () {
      throw new DOMException('full', 'QuotaExceededError');
    };"""
    page = app(storage=sample_state(), init_script=script, record=True)
    day(page, "Stretch 10 minutes", "2026-10-08").click()
    add_habit(page, "Drink water")

    line = streak(page, "Stretch 10 minutes")
    assert (line["cur"], line["best"]) == ("4 days", "Best 9")
    assert page.locator("h3.habit-name").all_inner_texts()[3] == "Drink water"
    expect(page.locator("#new-habit-msg")).to_have_text("")
    log = record(page)
    assert log.errors == []
    assert [m for m in log.console if m["type"] == "error"] == []
    assert stored(page) == sample_state()  # nothing could be saved
