"""R16, R17 and R41, kept on the device. Changes surviving a reload, the note after unreadable saved data, and the save
warning (app qa.md, Feature "Kept on the device"). The storage unit scenario is in tests/storage.test.js (task 14).

Each test seeds storage before the app loads, or fails storage from the test side with the drivers of qa.md (D-a to
D-e, conftest.py), presses with real gestures and reads the banners, the rows, the focus, boxes, the console and the
saved text.
"""
import json

import pytest
from playwright.sync_api import expect

import conftest
from conftest import (
    FAIL_GETITEM,
    FAIL_GETTER,
    FAIL_SETITEM,
    FAIL_SETITEM_PROBE,
    NOON,
    SAMPLE_HABITS,
    STORAGE_READ_MARK,
    TODAY,
    add_habit,
    band_day,
    bead,
    bin_btn,
    canon_tree,
    clear_fill,
    confirm_delete,
    done_btn,
    encode,
    fill_quota,
    let_guard_pass,
    mutation_log,
    mutations,
    record,
    row_numbers,
    sample_state,
    storage_switch,
    stored,
    tick,
    twelve_state,
    write_count,
    write_evidence,
    year_btn,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
WARNING = "Your habits are not being saved on this device. Changes will be lost when you close this tab."
NOTE = "Your saved habits could not be read, so the list was reset."
EMPTY_STATE = '{"version":1,"habits":[]}'
CLOSE = "button.icon-btn[aria-label='Close']"

# The two banners of spec Contracts as `canon_tree` gives them (tag, sorted attributes, own text, children).
WARN_TREE = ["div", ["class=banner warn", "role=status"], "", [["p", [], WARNING, []]]]
NOTE_TREE = [
    "div",
    ["class=banner note", "role=status"],
    "",
    [
        ["p", [], NOTE, []],
        [
            "button",
            ["aria-label=Dismiss note", "class=icon-btn", "type=button"],
            "",
            [["svg", ["aria-hidden=true", "class=ph"], "", [["use", ["href=#i-x"], "", []]]]],
        ],
    ],
]

# Each row as (name, Current, Best, Done today's aria-pressed). The sample day (qa.md, measured sample values).
SAMPLE_ROWS = [
    ("Read 20 pages", "4 days", "9", "true"),
    ("Stretch 10 minutes", "2 days", "5", "false"),
    ("No phone after 11pm", "No streak yet", "14", "false"),
]


def banners(page):
    """Each child of div.banners as a `canon_tree` tree, in order."""
    return canon_tree(page, "div.banners")[3]


def rows_shown(page):
    """Each row in list order as (name, Current, Best, Done today's aria-pressed), Current like "4 days" or "No streak
    yet" and Best None when the row has no Best block."""
    shown = []
    for name in page.locator("ul.rows > li.row h3.r-name").all_text_contents():
        numbers = row_numbers(page, name)
        shown.append((name, numbers["current"], numbers["best"], done_btn(page, name).get_attribute("aria-pressed")))
    return shown


def with_days(edits, habits=SAMPLE_HABITS):
    """`habits` with each name's date of `edits` added to its done list, or taken out when already there, in order."""
    return [
        {"name": habit["name"], "done": sorted(set(habit["done"]) ^ ({edits[habit["name"]]} if habit["name"] in edits else set()))}
        for habit in habits
    ]


def field_has_focus(page):
    return page.evaluate("() => document.activeElement === document.querySelector('#nh')")


def console_markers(page, prefix):
    """The console messages starting with `prefix` that the page's log holds, after a round trip so all have arrived."""
    page.evaluate("() => 0")
    return [message["text"] for message in record(page).console if message["text"].startswith(prefix)]


# ---------------------------------------------------------------------------------------------------------------
# Persistence (R16)


def test_R16_R32_changes_survive_a_reload_and_a_closed_tab(app):
    page = app(viewport=DESKTOP, storage=sample_state(), install_time=NOON)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    done_btn(page, "Stretch 10 minutes").click()
    band_day(page, "2026-09-22").click()
    tick(page, "Read 20 pages").click()
    page.locator(f"dialog.dlg-day {CLOSE}").click()
    let_guard_pass(page)
    year_btn(page, "No phone after 11pm").click()
    bead(page, "2026-10-09").click()
    page.locator(f"dialog.dlg-year {CLOSE}").click()
    let_guard_pass(page)
    add_habit(page, "Drink water")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)

    page.reload()
    kept = [
        ("Read 20 pages", "4 days", "13", "true"),
        ("Stretch 10 minutes", "3 days", "5", "true"),
        ("No phone after 11pm", "8 days", "14", "false"),
    ]
    drink = ("Drink water", "No streak yet", None, "false")
    assert rows_shown(page) == kept + [drink], "the reload did not show the edited habits in order"
    edited = with_days({"Read 20 pages": "2026-09-22", "Stretch 10 minutes": TODAY, "No phone after 11pm": "2026-10-09"})
    assert stored(page) == encode(edited + [{"name": "Drink water", "done": []}])

    bin_btn(page, "Drink water").click()
    confirm_delete(page, bin_btn(page, "Drink water"))
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    page.reload()
    assert rows_shown(page) == kept, "the reload after the delete did not show the three habits"
    assert "Drink water" not in stored(page)

    context = page.context
    page.close()
    again = context.new_page()
    again.goto(conftest.BASE_URL)
    assert rows_shown(again) == kept, "a new page in the same browser did not show the same habits"


def test_R16_loading_writes_nothing(app):
    pretty = json.dumps({"version": 1, "habits": SAMPLE_HABITS}, indent=2)
    assert "\n" in pretty
    page = app(storage=pretty, count_writes=True)
    page.wait_for_timeout(2000)
    assert stored(page) == pretty, "loading changed the saved text"
    assert write_count(page) == 0, "loading wrote to storage"
    assert rows_shown(page) == SAMPLE_ROWS


# ---------------------------------------------------------------------------------------------------------------
# The unreadable note (R17)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("{", id="not JSON"),
        pytest.param("null", id="JSON null"),
        pytest.param("[]", id="an array"),
        pytest.param('{"version":2,"habits":[]}', id="wrong version"),
        pytest.param('{"version":"1","habits":[]}', id="version as text"),
        pytest.param('{"version":1,"habits":{}}', id="no habits array"),
        pytest.param(encode([{"name": f"H{n}", "done": []} for n in range(1, 14)]), id="13 habits"),
        pytest.param('{"version":1,"habits":[{"name":"","done":[]}]}', id="empty name"),
        pytest.param('{"version":1,"habits":[{"name":" Read","done":[]}]}', id="untrimmed name"),
        pytest.param('{"version":1,"habits":[{"name":"Read twenty pages before bed every night.","done":[]}]}', id="41 characters"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":[]},{"name":"read","done":[]}]}', id="duplicate ignoring case"),
        pytest.param('{"version":1,"habits":[{"name":5,"done":[]}]}', id="name not text"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":"2026-10-08"}]}', id="done not a list"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":["2026-02-30"]}]}', id="impossible date"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":["2026-10-08T00:00"]}]}', id="date with a time"),
        pytest.param('{"version":1,"habits":[null]}', id="habit is null"),
    ],
)
def test_R17_unreadable_saved_data_resets_the_list_and_shows_the_note(app, raw):
    page = app(viewport=DESKTOP, storage=raw)
    assert banners(page) == [NOTE_TREE], "div.banners does not hold exactly the note"
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    expect(page.locator("ul.rows > li.row")).to_have_count(0)
    expect(band_day(page, TODAY)).to_have_attribute("aria-label", "Sat 10 Oct, 0 of 0 habits")
    assert stored(page) == EMPTY_STATE


def shows_the_empty_list(page):
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)


def drops_fields_it_does_not_know(page):
    assert rows_shown(page) == [("Read", "1 day", "1", "true")]
    done_btn(page, "Read").click()
    expect(done_btn(page, "Read")).to_have_attribute("aria-pressed", "false")
    saved = stored(page)
    assert "color" not in saved and "theme" not in saved, saved


def counts_a_repeated_day_once(page):
    assert rows_shown(page) == [("Read", "2 days", "2", "true")]


def draws_no_day_after_today(page):
    expect(page.locator('button[data-key="2026-10-11"]')).to_have_count(0)
    assert rows_shown(page) == [("Read", "No streak yet", "1", "false")]


def lets_no_key_reach_the_prototype(page):
    assert [name for name, *_ in rows_shown(page)] == ["Read"]
    assert page.evaluate("() => typeof ({}).polluted") == "undefined"


@pytest.mark.parametrize(
    "raw, result",
    [
        pytest.param('{"version":1,"habits":[]}', shows_the_empty_list, id="no habits"),
        pytest.param(
            '{"version":1,"habits":[{"name":"Read","done":["2026-10-10"],"color":"red"}],"theme":"dark"}',
            drops_fields_it_does_not_know,
            id="extra fields",
        ),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":["2026-10-10","2026-10-09","2026-10-10"]}]}', counts_a_repeated_day_once, id="a repeated day"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":["2026-10-11"]}]}', draws_no_day_after_today, id="a day after today"),
        pytest.param('{"version":1,"habits":[{"name":"Read","done":[],"__proto__":{"polluted":true}}]}', lets_no_key_reach_the_prototype, id="__proto__ key"),
    ],
)
def test_R17_readable_edge_cases_load_without_a_note(app, raw, result):
    page = app(storage=raw)
    assert banners(page) == [], "div.banners has a child for a readable value"
    result(page)


def test_R17_R22_dismiss_removes_the_note_moves_focus_to_the_field_and_the_note_does_not_come_back(app):
    page = app(storage="{")
    page.get_by_role("button", name="Dismiss note", exact=True).click()
    expect(page.locator("div.banner.note")).to_have_count(0)
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    assert field_has_focus(page), "Dismiss did not move focus to the field"

    page.reload()
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    assert banners(page) == [], "the note came back on the next load"

    page.goto(conftest.BASE_URL + "__seed__")
    page.evaluate("() => localStorage.setItem('streaks.state', '{')")
    page.goto(conftest.BASE_URL)
    assert banners(page) == [NOTE_TREE], "a new unreadable value did not show the note again"


GAPS_JS = """(above) => {
  const box = (selector) => document.querySelector(selector)?.getBoundingClientRect();
  const [note, aboveBox, banners, frameWrap] = ['div.banner.note', above, 'div.banners', 'div.frame-wrap'].map(box);
  return note ? { noteBelowAbove: note.top - aboveBox.bottom, frameBelowBanners: frameWrap.top - banners.bottom } : null;
}"""


@pytest.mark.parametrize(
    "viewport, above",
    [
        pytest.param(PHONE, "header.top", id="390x844"),
        pytest.param(DESKTOP, "section.band", id="1280x800"),
    ],
)
def test_R17_the_note_sits_between_the_top_of_the_page_and_the_list(app, viewport, above):
    page = app(viewport=viewport, storage="{")
    gaps = page.evaluate(GAPS_JS, above)
    assert gaps is not None, "no div.banner.note to measure"
    # Within half a pixel, because WebKit lays 100dvh out in 1/64 px units and the boxes below the header follow it.
    assert abs(gaps["noteBelowAbove"] - 12) <= 0.5 and abs(gaps["frameBelowBanners"] - 12) <= 0.5, gaps


def test_R17_R41_an_unreadable_value_whose_reset_save_fails_shows_the_warning_above_the_note(app):
    page = app(storage="{", init_script=FAIL_SETITEM)
    assert banners(page) == [WARN_TREE, NOTE_TREE], "div.banners does not hold the warning and then the note"
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    assert stored(page) == "{"

    storage_switch(page, False)
    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    assert banners(page) == [NOTE_TREE], "a working save did not remove the warning, or removed the note"
    assert stored(page) == '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'


def test_R17_R41_R28_the_banners_have_the_markup_of_the_golden(app):
    """Not a qa.md scenario. The two banners together, node for node against the S4 and S5 frames of states.html."""
    page = app(storage="{", init_script=FAIL_SETITEM)
    golden = [
        canon_tree(page, "section[aria-labelledby=s4] div.banner.warn", golden="states.html"),
        canon_tree(page, "section[aria-labelledby=s5] div.banner.note", golden="states.html"),
    ]
    assert golden == [WARN_TREE, NOTE_TREE], "this file's banner trees differ from the golden"
    assert banners(page) == golden


# ---------------------------------------------------------------------------------------------------------------
# The save warning (R41)


@pytest.mark.parametrize(
    "storage",
    [
        pytest.param(None, id="a fresh day"),
        pytest.param(sample_state(), id="the sample day"),
        pytest.param(twelve_state(), id="twelve habits"),
    ],
)
def test_R41_a_cold_boot_with_working_storage_shows_no_warning_and_writes_nothing(app, storage):
    page = app(storage=storage, count_writes=True)
    expect(page.locator("ul.rows > li")).not_to_have_count(0)
    page.wait_for_timeout(2000)
    assert page.locator("div.banner.warn").count() == 0, "a warning showed at a boot that saved nothing"
    assert write_count(page) == 0, "the boot wrote to storage"


def test_R41_the_first_failing_save_shows_the_warning_and_the_change_stays(app):
    page = app(storage=sample_state(), init_script=FAIL_SETITEM, record=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    assert page.locator("div.banner.warn").count() == 0, "a warning showed before any save"

    done_btn(page, "Stretch 10 minutes").click()
    assert banners(page)[:1] == [WARN_TREE], "the first child of div.banners is not the warning"
    assert row_numbers(page, "Stretch 10 minutes")["current"] == "3 days"
    expect(done_btn(page, "Stretch 10 minutes")).to_have_attribute("aria-pressed", "true")
    assert stored(page) == sample_state()
    assert record(page).errors == []


def test_R41_while_saves_keep_failing_the_warning_stays_the_same_element(app):
    page = app(storage=sample_state(), init_script=FAIL_SETITEM)
    done_btn(page, "Stretch 10 minutes").click()
    warning = page.locator("div.banner.warn").element_handle()
    log = mutation_log(page, "div.banners")

    done_btn(page, "Read 20 pages").click()
    add_habit(page, "Drink water")
    expect(page.locator("ul.rows > li.row")).to_have_count(4)
    assert warning.evaluate(
        "(node) => node.isConnected && document.querySelectorAll('div.banner.warn').length === 1"
    ), "the warning was replaced while saves kept failing"
    assert mutations(log) == {"added": 0, "removed": 0}, "div.banners changed while saves kept failing"

    page.reload()
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    assert page.locator("div.banner.warn").count() == 0, "a warning showed after a reload that saved nothing"
    assert rows_shown(page) == SAMPLE_ROWS


def test_R41_the_next_working_save_removes_the_warning_and_storage_then_holds_what_is_on_screen(app):
    page = app(storage=sample_state(), init_script=FAIL_SETITEM)
    done_btn(page, "Stretch 10 minutes").click()
    done_btn(page, "Read 20 pages").click()
    log = mutation_log(page, "div.banners")

    storage_switch(page, False)
    done_btn(page, "No phone after 11pm").click()
    assert page.locator("div.banner.warn").count() == 0, "the warning stayed after a working save"
    assert mutations(log) == {"added": 0, "removed": 1}, "div.banners did not lose exactly one child"
    assert stored(page) == encode(with_days({"Read 20 pages": TODAY, "Stretch 10 minutes": TODAY, "No phone after 11pm": TODAY}))


def test_R41_storage_refused_at_boot_shows_the_warning_in_the_first_render_and_clears_when_storage_returns(app):
    page = app(storage=sample_state(), init_script=FAIL_GETTER, record=True)
    assert banners(page) == [WARN_TREE], "div.banners does not hold only the warning after a refused read"
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    expect(page.locator("ul.rows > li.row")).to_have_count(0)

    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    assert banners(page) == [WARN_TREE], "the warning went while saves kept failing"

    storage_switch(page, False)
    add_habit(page, "Stretch 10 minutes")
    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    assert page.locator("div.banner.warn").count() == 0, "the warning stayed after a working save"
    assert stored(page) == '{"version":1,"habits":[{"name":"Read 20 pages","done":[]},{"name":"Stretch 10 minutes","done":[]}]}'
    assert record(page).errors == []


def test_R41_a_read_that_throws_at_boot_shows_the_warning_and_the_first_working_save_clears_it(app):
    page = app(storage=sample_state(), init_script=FAIL_GETITEM, record=True)
    assert banners(page) == [WARN_TREE], "div.banners does not hold only the warning after a read that threw"
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    expect(page.locator("ul.rows > li.row")).to_have_count(0)

    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    assert page.locator("div.banner.warn").count() == 0, "the warning stayed after setItem worked"
    storage_switch(page, False)
    assert stored(page) == '{"version":1,"habits":[{"name":"Read 20 pages","done":[]}]}'
    assert record(page).errors == []


def test_R41_a_real_full_quota_shows_the_warning_and_clears_when_space_returns(app):
    page = app(storage=sample_state(), record=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    write_evidence("quota-fill", fill_quota(page))
    done_btn(page, "Stretch 10 minutes").click()
    assert banners(page) == [WARN_TREE], "a save into a full store did not show the warning"
    assert stored(page) == sample_state()

    clear_fill(page)
    done_btn(page, "Read 20 pages").click()
    assert page.locator("div.banner.warn").count() == 0, "the warning stayed after space returned"
    assert stored(page) == encode(with_days({"Stretch 10 minutes": TODAY, "Read 20 pages": TODAY}))
    assert record(page).errors == []


def test_R41_the_app_never_reads_the_error_it_catches(app):
    page = app(storage=sample_state(), init_script=FAIL_SETITEM_PROBE, record=True)
    done_btn(page, "Stretch 10 minutes").click()
    assert banners(page) == [WARN_TREE], "a failed save did not show the warning"
    assert console_markers(page, STORAGE_READ_MARK) == [], "the app read the error it caught"
    assert record(page).errors == []
