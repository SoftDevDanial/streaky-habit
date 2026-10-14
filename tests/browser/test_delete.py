"""R13, R14 and R15, deleting a habit from a row's bin or from P2's Delete habit, the time-free guard of Delete habit
(CG-10), the tap-through guard of every popup (CG-11) and focus after a delete (CG-18) (app qa.md, Feature "Delete a
habit").

Each test presses with real gestures and reads which dialogs are open, the rows, the focus, the saved text and the
number of writes. The guard scenarios run on an installed clock that is paused (qa.md, "the clock installed and
paused"). Event timestamps follow it, so presses made while it is paused happen at one instant on any machine, and
`run_for` moves past a window with no sleep. Under a paused clock a locator click can wait forever on animation frames,
so those presses are raw mouse and touch input at measured points, and each point is checked to lie on the control the
scenario names, so a layout change can fail a precondition but never pass a scenario because nothing was there.
"""
import json
import pathlib

import pytest
from playwright.sync_api import expect

import conftest
from conftest import (
    FSI,
    GUARD_WINDOW_MS,
    NOON,
    PAUSE_AT,
    PDI,
    SAMPLE_HABITS,
    TWELVE,
    add_button,
    add_habit,
    band_day,
    bead,
    bin_btn,
    canon_tree,
    confirm_delete,
    current_block,
    dialog_title,
    done_btn,
    encode,
    first_difference,
    let_guard_pass,
    p3_day,
    point_beside,
    press_twice,
    row,
    row_numbers,
    sample_state,
    stats_tree,
    stored,
    twelve_state,
    wait_for_close,
    watch_close,
    write_count,
    year_btn,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
SAMPLE_NAMES = [habit["name"] for habit in SAMPLE_HABITS]
TWELVE_NAMES = [habit["name"] for habit in TWELVE]
STATES = {"the sample day": SAMPLE_HABITS, "twelve habits": TWELVE}


def pretty(habits):
    """The stored text of `habits`, indented, so a save of the very same habits would still change it."""
    return json.dumps({"version": 1, "habits": habits}, indent=1, ensure_ascii=False)


def dialog(page, cls):
    return page.locator(f"dialog.{cls}")


def cancel(page):
    return page.locator("dialog.dlg-del div.dlg-actions > button.btn-secondary")


def confirm(page):
    """M1's Delete habit."""
    return page.locator("dialog.dlg-del div.dlg-actions > button.btn-danger")


def p2_delete(page):
    """P2's Delete habit."""
    return page.locator("dialog.dlg-year button.btn-del")


def close_of(page, cls):
    return page.locator(f"dialog.{cls} button.icon-btn")


def title(page):
    return page.locator("#del-title").text_content()


def names(page):
    return page.locator("ul.rows > li.row h3.r-name").all_text_contents()


def open_dialogs(page):
    """The last class of each open dialog, in document order (dlg-ov, dlg-all, dlg-year, dlg-day, dlg-del)."""
    return page.evaluate("() => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).map((d) => d.classList[d.classList.length - 1])")


def middle(box):
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def centre(locator):
    box = locator.bounding_box()
    assert box is not None, f"{locator} is not shown"
    return middle(box)


def inside(point, box):
    x, y = point
    return box["x"] <= x <= box["x"] + box["width"] and box["y"] <= y <= box["y"] + box["height"]


def intersection(a, b):
    left, top = max(a["x"], b["x"]), max(a["y"], b["y"])
    right, bottom = min(a["x"] + a["width"], b["x"] + b["width"]), min(a["y"] + a["height"], b["y"] + b["height"])
    if right <= left or bottom <= top:
        return None
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def settle(page, cls):
    """Wait until the open dialog's entrance has played (its box rises 8 px), so a box measured now is where it rests.

    CSS animations run on the page's own timeline, so they end under a paused clock too (measured in 1.0).
    """
    dialog(page, cls).evaluate("(node) => Promise.all(node.getAnimations({ subtree: true }).map((a) => a.finished)).then(() => true)")


UNDER_JS = """([x, y, selector]) => {
  const node = document.elementFromPoint(x, y);
  const control = node && node.closest('button, input');
  return !!control && control === node.closest(selector);
}"""


def under(page, point, selector):
    """True when the topmost control at `point` is the one `selector` matches."""
    return page.evaluate(UNDER_JS, [point[0], point[1], selector])


def bin_selector(name):
    return f"ul.rows button.btn-bin[aria-label='Delete \"{name}\"']"


def done_selector(name):
    return f"ul.rows button.btn-done[aria-label='Done today, {name}']"


def press(page, point, how):
    """One mouse click or one tap at `point`."""
    if how == "touch":
        page.touchscreen.tap(*point)
    else:
        page.mouse.click(*point)


def tab_to(page, target, limit=200):
    """Press Tab until the locator `target` has focus. Fails after `limit` presses."""
    for _ in range(limit):
        if target.evaluate("(node) => node === document.activeElement"):
            return
        page.keyboard.press("Tab")
    pytest.fail(f"{target} did not take focus in {limit} presses of Tab")


def write_evidence(name, data):
    """Write `data` as JSON into the run's evidence folder (STREAKS_EVIDENCE_DIR, ending with the engine), when set."""
    if not conftest.EVIDENCE_DIR:
        return
    folder = pathlib.Path(conftest.EVIDENCE_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


FRAME_BOX_JS = """() => {
  const frame = document.querySelector('div.frame');
  const box = frame.getBoundingClientRect();
  return { x: box.left + frame.clientLeft, y: box.top + frame.clientTop, width: frame.clientWidth, height: frame.clientHeight };
}"""


def frame_box(page):
    """The visible part of div.frame, its client box in the viewport."""
    return page.evaluate(FRAME_BOX_JS)


def fully_inside(box, outer):
    return (
        box["x"] >= outer["x"] - 0.5 and box["y"] >= outer["y"] - 0.5
        and box["x"] + box["width"] <= outer["x"] + outer["width"] + 0.5
        and box["y"] + box["height"] <= outer["y"] + outer["height"] + 0.5
    )


def overlap_point(page, habits, evidence):
    """The habit whose bin M1's Delete habit covers most, and the middle of that overlap.

    M1 is opened from each bin that lies fully in the frame's visible part (a person can press only those where they
    are) and closed again with Escape, and every box measured goes to the evidence. Fails when no bin overlaps, and
    checks that the bin lies under the point while M1 is closed.
    """
    frame = frame_box(page)
    rows = []
    for habit in habits:
        opener = bin_btn(page, habit["name"])
        entry = {"name": habit["name"], "bin": opener.bounding_box()}
        rows.append(entry)
        if not fully_inside(entry["bin"], frame):
            continue
        page.mouse.click(*middle(entry["bin"]))
        expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
        settle(page, "dlg-del")
        entry["deleteHabit"] = confirm(page).bounding_box()
        entry["overlap"] = intersection(entry["bin"], entry["deleteHabit"])
        escape_m1(page)
        expect(opener).to_be_focused()
    write_evidence(evidence, {"frame": frame, "rows": rows})
    overlapping = [entry for entry in rows if entry.get("overlap")]
    assert overlapping, f"no bin lies under M1's Delete habit (boxes in {evidence}.json): {rows}"
    best = max(overlapping, key=lambda entry: entry["overlap"]["width"] * entry["overlap"]["height"])
    point = middle(best["overlap"])
    assert under(page, point, bin_selector(best["name"])), f"the bin of {best['name']} is not under {point}"
    return best["name"], point


def escape_m1(page):
    """Escape closes M1, and the app's close handler has run once this returns (so a next opening never meets it)."""
    watch = watch_close(page, "dialog.dlg-del")
    page.keyboard.press("Escape")
    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    wait_for_close(watch)


def assert_kept(page, name, everyone, before):
    """M1 is still open for `name`, every habit is listed, nothing was written and the stored text is `before`."""
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    assert title(page) == dialog_title(name)
    assert names(page) == everyone
    assert write_count(page) == 0
    assert stored(page) == before


# Each click that reaches M1's Delete habit, read by a test-side capture listener on window. It adds no property to
# window, and the handle keeps the array.
DETAILS_JS = """() => {
  const details = [];
  window.addEventListener('click', (event) => {
    if (event.target.closest && event.target.closest('dialog.dlg-del button.btn-danger')) details.push(event.detail);
  }, true);
  return details;
}"""


# ------------------------------------------------------------------------------------------------- opening M1 (R13)


def test_R13_a_bin_opens_m1_with_focus_on_cancel(app):
    page = app(storage=sample_state())
    bin_btn(page, "Read 20 pages").click()

    m1 = dialog(page, "dlg-del")
    assert m1.evaluate("(node) => node.open && node.matches(':modal')") is True
    assert title(page) == dialog_title("Read 20 pages")
    assert page.locator("#del-body").text_content() == "Its history is deleted too."
    buttons = m1.locator("div.dlg-actions > button")
    assert buttons.evaluate_all("(nodes) => nodes.map((n) => [n.textContent, n.getAttribute('type')])") == [
        ["Cancel", "button"],
        ["Delete habit", "button"],
    ]
    expect(cancel(page)).to_be_focused()
    assert page.evaluate("() => getComputedStyle(document.documentElement).overflow") == "hidden"

    page.mouse.wheel(0, 800)
    page.wait_for_timeout(200)
    assert page.evaluate("() => window.scrollY") == 0


def without_isolates(tree):
    """A `canon_tree` tree with the two invisible isolate marks of the title taken out of every text."""
    tag, attributes, text, children = tree
    return [tag, attributes, text.replace(FSI, "").replace(PDI, ""), [without_isolates(child) for child in children]]


def test_R13_R28_m1_has_the_markup_of_the_golden(app):
    """Beyond the qa.md scenarios. M1 opened from Stretch's bin, the state `delete-dialog.html` draws, has the golden's
    markup node for node. The one difference is the pair of isolate marks inside the title's quotes (SEC-02), which the
    title scenarios below pin."""
    page = app(storage=sample_state())
    bin_btn(page, "Stretch 10 minutes").click()
    found = without_isolates(canon_tree(page, "dialog.dlg-del"))
    expected = canon_tree(page, "dialog.dlg-del", golden="delete-dialog.html")
    assert first_difference(found, expected) is None, first_difference(found, expected)


def test_R13_R33_delete_habit_in_the_year_view_opens_m1_over_it(app):
    page = app(storage=sample_state())
    year_btn(page, "Read 20 pages").click()
    expect(dialog(page, "dlg-year")).to_have_attribute("open", "")
    p2_delete(page).click()

    assert open_dialogs(page) == ["dlg-year", "dlg-del"]
    assert page.evaluate("() => ['dlg-year', 'dlg-del'].map((cls) => document.querySelector('dialog.' + cls).matches(':modal'))") == [True, True]
    box = page.locator("dialog.dlg-del > div.dlg-box").bounding_box()
    assert page.evaluate("([x, y]) => !!document.elementFromPoint(x, y).closest('dialog.dlg-del')", list(middle(box)))
    assert title(page) == dialog_title("Read 20 pages")
    expect(cancel(page)).to_be_focused()


LONG_NAME = "Read twenty pages before bed every night"


def test_R13_a_long_name_wraps_in_the_title_and_the_box_keeps_its_width(app):
    page = app(viewport=PHONE, storage=encode([{"name": LONG_NAME, "done": []}]))
    bin_btn(page, LONG_NAME).click()
    found = page.evaluate(
        """() => {
      const title = document.querySelector('#del-title');
      return { width: document.querySelector('dialog.dlg-del').getBoundingClientRect().width,
        height: title.getBoundingClientRect().height, line: getComputedStyle(title).lineHeight };
    }"""
    )
    assert found["width"] == 358, found
    assert found["line"] == "26px" and found["height"] > 26, found


# ------------------------------------------------------------------------------- the time-free guard (R13, CG-10)

OVERLAP_ROWS = [
    pytest.param("the sample day", DESKTOP, "mouse", id="sample-1280x800-mouse"),
    pytest.param("the sample day", DESKTOP, "touch", id="sample-1280x800-touch"),
    pytest.param("twelve habits", PHONE, "mouse", id="twelve-390x844-mouse"),
    pytest.param("twelve habits", PHONE, "touch", id="twelve-390x844-touch"),
]


def open_for_overlap(app, state, viewport, how):
    habits = STATES[state]
    before = pretty(habits)
    page = app(viewport=viewport, storage=before, touch=how == "touch", install_time=NOON, count_writes=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(len(habits))
    return page, habits, before


@pytest.mark.parametrize("state, viewport, how", OVERLAP_ROWS)
def test_R13_a_slow_double_click_on_a_bin_that_lies_under_delete_habit_cannot_delete(app, state, viewport, how):
    page, habits, before = open_for_overlap(app, state, viewport, how)
    name, point = overlap_point(page, habits, f"delete-overlap-slow-{state.replace(' ', '-')}-{viewport[0]}x{viewport[1]}-{how}")
    page.clock.pause_at(PAUSE_AT)

    press(page, point, how)
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    assert name in title(page)
    settle(page, "dlg-del")
    assert under(page, point, "dialog.dlg-del button.btn-danger"), f"Delete habit is not under {point}"
    page.clock.run_for(2000)
    press(page, point, how)

    assert_kept(page, name, [habit["name"] for habit in habits], before)
    escape_m1(page)
    expect(bin_btn(page, name)).to_be_focused()


@pytest.mark.parametrize("state, viewport, how", OVERLAP_ROWS)
def test_R13_a_fast_double_click_or_double_tap_on_a_bin_under_delete_habit_cannot_delete(app, state, viewport, how):
    page, habits, before = open_for_overlap(app, state, viewport, how)
    evidence = f"delete-overlap-fast-{state.replace(' ', '-')}-{viewport[0]}x{viewport[1]}-{how}"
    name, point = overlap_point(page, habits, evidence)
    page.clock.pause_at(PAUSE_AT)
    details = page.evaluate_handle(DETAILS_JS)

    press_twice(page, *point, how)
    write_evidence(f"{evidence}-click-details", {"point": point, "detailsOfClicksOnDeleteHabit": details.json_value()})

    assert_kept(page, name, [habit["name"] for habit in habits], before)
    escape_m1(page)
    expect(bin_btn(page, name)).to_be_focused()


def test_R13_a_press_with_a_click_count_of_2_on_delete_habit_away_from_the_bin_does_nothing(app):
    before = pretty(SAMPLE_HABITS)
    page = app(viewport=PHONE, storage=before, install_time=NOON, count_writes=True)
    opener = bin_btn(page, "Stretch 10 minutes")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    settle(page, "dlg-del")
    page.clock.pause_at(PAUSE_AT)
    point = point_beside(confirm(page), opener)
    assert under(page, point, "dialog.dlg-del button.btn-danger") and not inside(point, opener.bounding_box())
    details = page.evaluate_handle(DETAILS_JS)

    page.mouse.move(*point)
    page.mouse.down(click_count=2)
    page.mouse.up(click_count=2)

    assert details.json_value() == [2]
    assert_kept(page, "Stretch 10 minutes", SAMPLE_NAMES, before)


@pytest.mark.parametrize(
    "viewport, how",
    [
        pytest.param(PHONE, "mouse", id="390x844-mouse"),
        pytest.param(PHONE, "touch", id="390x844-touch"),
        pytest.param(DESKTOP, "mouse", id="1280x800-mouse"),
    ],
)
def test_R13_R15_one_press_on_delete_habit_away_from_the_bin_deletes_at_once(app, viewport, how):
    page = app(viewport=viewport, storage=sample_state(), touch=how == "touch", install_time=NOON, count_writes=True)
    opener = bin_btn(page, "Stretch 10 minutes")
    opening = centre(opener)
    page.clock.pause_at(PAUSE_AT)

    press(page, opening, how)
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    settle(page, "dlg-del")
    point = point_beside(confirm(page), opener)
    assert under(page, point, "dialog.dlg-del button.btn-danger") and not inside(point, opener.bounding_box())
    press(page, point, how)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    assert names(page) == ["Read 20 pages", "No phone after 11pm"]
    assert write_count(page) == 1


def test_R13_R15_enter_on_delete_habit_deletes_at_once(app):
    page = app(storage=sample_state(), install_time=NOON, count_writes=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(3)
    page.clock.pause_at(PAUSE_AT)
    tab_to(page, bin_btn(page, "Stretch 10 minutes"))

    page.keyboard.press("Enter")
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    expect(cancel(page)).to_be_focused()
    page.keyboard.press("Tab")
    expect(confirm(page)).to_be_focused()
    page.keyboard.press("Enter")

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    assert names(page) == ["Read 20 pages", "No phone after 11pm"]
    assert write_count(page) == 1
    expect(bin_btn(page, "No phone after 11pm")).to_be_focused()


def test_R13_R15_the_keyboard_deletes_even_when_delete_habit_lies_over_the_bin(app):
    page, habits, _ = open_for_overlap(app, "the sample day", DESKTOP, "mouse")
    name, _ = overlap_point(page, habits, "delete-overlap-keyboard-sample-1280x800")
    page.clock.pause_at(PAUSE_AT)
    tab_to(page, bin_btn(page, name))

    page.keyboard.press("Enter")
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    page.keyboard.press("Tab")
    expect(confirm(page)).to_be_focused()
    page.keyboard.press("Enter")

    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    assert names(page) == [habit["name"] for habit in habits if habit["name"] != name]


# --------------------------------------------------------------------------------------------------- keep (R14)


@pytest.mark.parametrize(
    "viewport, opener, action, still_open",
    [
        pytest.param(PHONE, "bin", "cancel", [], id="390x844-bin-cancel"),
        pytest.param(PHONE, "bin", "escape", [], id="390x844-bin-escape"),
        pytest.param(PHONE, "bin", "backdrop", [], id="390x844-bin-backdrop"),
        pytest.param(DESKTOP, "p2", "cancel", ["dlg-year"], id="1280x800-p2-cancel"),
        pytest.param(DESKTOP, "p2", "escape", ["dlg-year"], id="1280x800-p2-escape"),
        pytest.param(DESKTOP, "p2", "backdrop", ["dlg-year"], id="1280x800-p2-backdrop"),
    ],
)
def test_R14_cancel_esc_and_a_backdrop_click_keep_the_habit_and_give_focus_back(app, viewport, opener, action, still_open):
    before = pretty(SAMPLE_HABITS)
    page = app(viewport=viewport, storage=before, count_writes=True)
    if opener == "bin":
        control = bin_btn(page, "Stretch 10 minutes")
    else:
        year_btn(page, "Stretch 10 minutes").click()
        expect(dialog(page, "dlg-year")).to_have_attribute("open", "")
        control = p2_delete(page)
    control.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    watch = watch_close(page, "dialog.dlg-del")

    if action == "cancel":
        cancel(page).click()
    elif action == "escape":
        page.keyboard.press("Escape")
    else:
        assert not inside((5, 5), page.locator("dialog.dlg-del > div.dlg-box").bounding_box())
        page.mouse.click(5, 5)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    wait_for_close(watch)
    expect(control).to_be_focused()
    assert names(page) == SAMPLE_NAMES
    assert row_numbers(page, "Stretch 10 minutes") == {"current": "2 days", "best": "5"}
    assert stored(page) == before
    assert write_count(page) == 0
    assert open_dialogs(page) == still_open


def test_R14_esc_after_an_earlier_delete_still_keeps_the_habit(app):
    page = app(storage=sample_state(), install_time=NOON)
    opener = bin_btn(page, "No phone after 11pm")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)
    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    let_guard_pass(page)

    bin_btn(page, "Stretch 10 minutes").click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    escape_m1(page)

    assert names(page) == ["Read 20 pages", "Stretch 10 minutes"]
    expect(bin_btn(page, "Stretch 10 minutes")).to_be_focused()


@pytest.mark.parametrize("action", ["cancel", "escape", "backdrop"])
def test_R14_cancel_esc_and_a_backdrop_click_work_at_the_instant_of_opening(app, action):
    before = pretty(SAMPLE_HABITS)
    page = app(storage=before, install_time=NOON, count_writes=True)
    opener = bin_btn(page, "Stretch 10 minutes")
    opening = centre(opener)
    page.clock.pause_at(PAUSE_AT)

    page.mouse.click(*opening)
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    watch = watch_close(page, "dialog.dlg-del")
    if action == "cancel":
        page.mouse.click(*centre(cancel(page)))
    elif action == "escape":
        page.keyboard.press("Escape")
    else:
        assert not inside((5, 5), page.locator("dialog.dlg-del > div.dlg-box").bounding_box())
        page.mouse.click(5, 5)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    wait_for_close(watch)
    expect(opener).to_be_focused()
    assert names(page) == SAMPLE_NAMES
    assert write_count(page) == 0
    assert stored(page) == before


def test_R14_cancel_still_works_right_after_a_click_inside_the_box(app):
    page = app(storage=sample_state(), install_time=NOON)
    bin_btn(page, "Read 20 pages").click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    settle(page, "dlg-del")
    page.clock.pause_at(PAUSE_AT)
    box = page.locator("dialog.dlg-del > div.dlg-box").bounding_box()
    point = (box["x"] + 6, box["y"] + 6)
    assert page.evaluate(
        "([x, y]) => { const node = document.elementFromPoint(x, y); return !!node.closest('dialog.dlg-del') && !node.closest('button'); }",
        list(point),
    )

    page.mouse.click(*point)
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    page.mouse.click(*centre(cancel(page)))

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")


# ------------------------------------------------------------------------------ the tap-through guard (R14, CG-11)


def open_m1_from_read(page):
    bin_btn(page, "Read 20 pages").click()
    return "dlg-del"


def open_p1_from_the_band(page):
    band_day(page, "2026-09-22").click()
    return "dlg-day"


def open_p3(page):
    page.locator("button.ov-btn").click()
    return "dlg-ov"


def open_p3_then_p1(page):
    open_p3(page)
    p3_day(page, "2026-09-22").click()
    return "dlg-day"


def open_p3_then_p4(page):
    open_p3(page)
    page.locator("dialog.dlg-ov button.btn-all").click()
    return "dlg-all"


def open_p2_for_read(page):
    year_btn(page, "Read 20 pages").click()
    return "dlg-year"


OPEN = {
    "M1 from Read's bin": open_m1_from_read,
    "P1 for 2026-09-22 from the band": open_p1_from_the_band,
    "P3": open_p3,
    "P3, then P1 for 2026-09-22": open_p3_then_p1,
    "P3, then P4 from its Year": open_p3_then_p4,
    "P2 for Read": open_p2_for_read,
}


def open_and_pause(page, popups):
    """Open `popups` with clicks while the clock runs, let the entrance play, pause the clock and return the top
    dialog's class. The clock jumps 20 seconds at the pause, far past any window the opening clicks started."""
    top = OPEN[popups](page)
    expect(dialog(page, top)).to_have_attribute("open", "")
    settle(page, top)
    page.clock.pause_at(PAUSE_AT)
    return top


BAND_JULY_20 = "section.band button.hc[data-key='2026-07-20']"
P3_OCTOBER_5 = "dialog.dlg-ov button.hc[data-key='2026-10-05']"


def no_p1(page):
    return "dlg-day" not in open_dialogs(page)


def stretch_not_done(page):
    return done_btn(page, "Stretch 10 minutes").get_attribute("aria-pressed") == "false"


def p3_open_and_no_p1(page):
    return open_dialogs(page) == ["dlg-ov"]


@pytest.mark.parametrize(
    "viewport, how, popups, behind, result",
    [
        pytest.param(PHONE, "mouse", "M1 from Read's bin", done_selector("Stretch 10 minutes"), stretch_not_done, id="390x844-mouse-M1"),
        pytest.param(PHONE, "touch", "M1 from Read's bin", done_selector("Stretch 10 minutes"), stretch_not_done, id="390x844-touch-M1"),
        pytest.param(DESKTOP, "mouse", "M1 from Read's bin", BAND_JULY_20, no_p1, id="1280x800-mouse-M1"),
        pytest.param(DESKTOP, "touch", "M1 from Read's bin", BAND_JULY_20, no_p1, id="1280x800-touch-M1"),
        pytest.param(DESKTOP, "mouse", "P1 for 2026-09-22 from the band", BAND_JULY_20, no_p1, id="1280x800-mouse-P1"),
        pytest.param(PHONE, "mouse", "P3, then P1 for 2026-09-22", P3_OCTOBER_5, p3_open_and_no_p1, id="390x844-mouse-P3-then-P1"),
        pytest.param(PHONE, "touch", "P3, then P1 for 2026-09-22", P3_OCTOBER_5, p3_open_and_no_p1, id="390x844-touch-P3-then-P1"),
    ],
)
def test_R14_a_double_press_on_a_backdrop_does_not_reach_the_control_behind_it(app, viewport, how, popups, behind, result):
    before = pretty(SAMPLE_HABITS)
    page = app(viewport=viewport, storage=before, touch=how == "touch", install_time=NOON)
    top = open_and_pause(page, popups)
    point = centre(page.locator(behind))
    assert not inside(point, page.locator(f"dialog.{top} > div.dlg-box").bounding_box()), f"{behind} lies inside the top popup's box"

    press_twice(page, *point, how)

    expect(dialog(page, top)).not_to_have_attribute("open", "")
    assert result(page), (result.__name__, open_dialogs(page))
    assert stored(page) == before
    assert under(page, point, behind), f"{behind} is not under {point}"  # after the result: a press that got through can cover it


@pytest.mark.parametrize(
    "viewport, how, popups, behind, result",
    [
        pytest.param(PHONE, "mouse", "P2 for Read", "button.ov-btn", lambda page: "dlg-ov" not in open_dialogs(page), id="390x844-mouse-P2"),
        pytest.param(PHONE, "touch", "P2 for Read", "button.ov-btn", lambda page: "dlg-ov" not in open_dialogs(page), id="390x844-touch-P2"),
        pytest.param(PHONE, "mouse", "P3", "button.ov-btn", lambda page: "dlg-ov" not in open_dialogs(page), id="390x844-mouse-P3"),
        pytest.param(PHONE, "mouse", "P3, then P4 from its Year", "dialog.dlg-ov button.icon-btn", lambda page: open_dialogs(page) == ["dlg-ov"], id="390x844-mouse-P3-then-P4"),
        pytest.param(DESKTOP, "mouse", "P1 for 2026-09-22 from the band", "section.band button.hc", no_p1, id="1280x800-mouse-P1"),
    ],
)
def test_R14_a_double_press_on_close_does_not_reach_the_control_behind_it(app, viewport, how, popups, behind, result):
    page = app(viewport=viewport, storage=sample_state(), touch=how == "touch", install_time=NOON)
    top = open_and_pause(page, popups)
    point = centre(close_of(page, top))

    press_twice(page, *point, how)

    expect(dialog(page, top)).not_to_have_attribute("open", "")
    assert result(page), open_dialogs(page)
    assert under(page, point, behind), f"{behind} is not under {point}"  # after the result: a press that got through can cover it


@pytest.mark.parametrize("how", ["mouse", "touch"])
def test_R14_R10_a_double_press_on_the_backdrop_over_add_does_not_add_a_typed_name(app, how):
    before = pretty(SAMPLE_HABITS)
    page = app(viewport=PHONE, storage=before, touch=how == "touch", install_time=NOON, count_writes=True)
    page.locator("#nh").fill("Drink water")
    top = open_and_pause(page, "M1 from Read's bin")
    point = centre(add_button(page))
    assert not inside(point, page.locator("dialog.dlg-del > div.dlg-box").bounding_box()), "Add lies inside M1's box"

    press_twice(page, *point, how)

    expect(dialog(page, top)).not_to_have_attribute("open", "")
    assert under(page, point, "#add-btn"), f"Add is not under {point}"
    expect(page.locator("#nh")).to_have_value("Drink water")  # an add would have emptied the field
    assert names(page) == SAMPLE_NAMES
    assert write_count(page) == 0
    assert stored(page) == before


def test_R14_R15_a_double_click_on_delete_habit_deletes_once_and_nothing_behind_acts(app):
    page = app(viewport=PHONE, storage=twelve_state(), install_time=NOON, count_writes=True)
    expect(page.locator("ul.rows > li.row")).to_have_count(12)
    pressed = {name: done_btn(page, name).get_attribute("aria-pressed") for name in TWELVE_NAMES}
    opener = bin_btn(page, "Journal one page")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    settle(page, "dlg-del")
    page.clock.pause_at(PAUSE_AT)
    # The part of Delete habit that lies over Journal's own Done today. The rows below a deleted row move up by one
    # row and the frame does not scroll, so the next row's Done today lies there after the delete, in either engine.
    over = intersection(confirm(page).bounding_box(), done_btn(page, "Journal one page").bounding_box())
    assert over is not None, "Delete habit does not lie over Journal's Done today"
    point = middle(over)
    assert under(page, point, "dialog.dlg-del button.btn-danger") and not inside(point, opener.bounding_box())

    page.mouse.dblclick(*point)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    assert names(page) == [name for name in TWELVE_NAMES if name != "Journal one page"]
    assert write_count(page) == 1
    behind = page.evaluate(
        "([x, y]) => { const button = document.elementFromPoint(x, y)?.closest('ul.rows button.btn-done'); return button && [button.getAttribute('aria-label'), button.getAttribute('aria-pressed')]; }",
        list(point),
    )
    assert behind is not None, f"no Done today button lies under {point}"
    label, state = behind
    assert state == pressed[label.removeprefix("Done today, ")], behind
    assert stored(page) == encode([habit for habit in TWELVE if habit["name"] != "Journal one page"])


@pytest.mark.parametrize("how", ["mouse", "touch"])
def test_R14_the_layer_behind_listens_again_once_the_window_has_passed(app, how):
    page = app(viewport=PHONE, storage=sample_state(), touch=how == "touch", install_time=NOON)
    top = open_and_pause(page, "P2 for Read")
    press(page, centre(close_of(page, top)), how)
    expect(dialog(page, top)).not_to_have_attribute("open", "")
    overview = centre(page.locator("button.ov-btn"))

    page.clock.run_for(GUARD_WINDOW_MS - 1)
    press(page, overview, how)
    assert "dlg-ov" not in open_dialogs(page)

    page.clock.run_for(1)
    press(page, overview, how)
    expect(dialog(page, "dlg-ov")).to_have_attribute("open", "")


@pytest.mark.parametrize("key", ["Enter", "Space", "Escape"])
def test_R14_closing_with_the_keyboard_holds_nothing(app, key):
    """Enter and Space act on Cancel, which has focus."""
    page = app(storage=sample_state(), install_time=NOON)
    opener = bin_btn(page, "Read 20 pages")
    opening = centre(opener)
    page.clock.pause_at(PAUSE_AT)
    page.mouse.click(*opening)
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    expect(cancel(page)).to_be_focused()
    watch = watch_close(page, "dialog.dlg-del")

    page.keyboard.press(key)
    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    wait_for_close(watch)
    expect(opener).to_be_focused()
    done = done_btn(page, "Stretch 10 minutes")
    expect(done).to_have_attribute("aria-pressed", "false")
    page.mouse.click(*centre(done))

    expect(done).to_have_attribute("aria-pressed", "true")


def test_R14_clicks_inside_the_same_popup_or_in_a_popup_opened_after_it_are_never_held(app):
    page = app(viewport=PHONE, storage=sample_state(), install_time=NOON)
    opening = centre(year_btn(page, "Read 20 pages"))
    page.clock.pause_at(PAUSE_AT)

    page.mouse.click(*opening)
    expect(dialog(page, "dlg-year")).to_have_attribute("open", "")
    settle(page, "dlg-year")
    for key in ("2026-10-06", "2026-10-03"):
        page.mouse.click(*centre(bead(page, key)))
    expect(bead(page, "2026-10-06")).to_have_attribute("aria-pressed", "true")
    expect(bead(page, "2026-10-03")).to_have_attribute("aria-pressed", "true")

    page.mouse.click(*centre(p2_delete(page)))
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    settle(page, "dlg-del")
    watch = watch_close(page, "dialog.dlg-del")
    page.mouse.click(*centre(cancel(page)))
    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    wait_for_close(watch)
    expect(p2_delete(page)).to_be_focused()
    assert open_dialogs(page) == ["dlg-year"]

    october_2 = bead(page, "2026-10-02")
    expect(october_2).to_have_attribute("aria-pressed", "true")
    page.mouse.click(*centre(october_2))
    assert october_2.get_attribute("aria-pressed") == "true", "a click on P2 right after Cancel reached the bead"

    page.clock.run_for(GUARD_WINDOW_MS)
    page.mouse.click(*centre(october_2))
    expect(october_2).to_have_attribute("aria-pressed", "false")


# -------------------------------------------------------------------------------------------------- delete (R15)


def test_R15_R32_deleting_from_a_bin_moves_focus_to_the_next_bin_and_recounts(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    opener = bin_btn(page, "Stretch 10 minutes")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    assert page.locator("ul.rows > li.row h3.r-name").evaluate_all("(nodes) => nodes.map((n) => [n.textContent, n.id])") == [
        ["Read 20 pages", "rn-1"],
        ["No phone after 11pm", "rn-2"],
    ]
    expect(bin_btn(page, "No phone after 11pm")).to_be_focused()
    july_21 = band_day(page, "2026-07-21")
    expect(july_21).to_have_attribute("aria-label", "Tue 21 Jul, 2 of 2 habits")
    expect(july_21.locator(":scope > svg > circle.c-core")).to_have_count(1)
    expect(band_day(page, "2026-10-10")).to_have_attribute("aria-label", "Sat 10 Oct, 1 of 2 habits")
    assert json.loads(stored(page)) == {"version": 1, "habits": [SAMPLE_HABITS[0], SAMPLE_HABITS[2]]}


def test_R15_deleting_the_last_row_moves_focus_to_the_bin_above(app):
    page = app(storage=sample_state())
    opener = bin_btn(page, "No phone after 11pm")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)

    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    expect(bin_btn(page, "Stretch 10 minutes")).to_be_focused()
    expect(band_day(page, "2026-10-10")).to_have_attribute("aria-label", "Sat 10 Oct, 1 of 2 habits")


def test_R15_R3_deleting_the_only_habit_shows_the_empty_list(app):
    page = app()
    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    done_btn(page, "Read 20 pages").click()
    expect(done_btn(page, "Read 20 pages")).to_have_attribute("aria-pressed", "true")
    opener = bin_btn(page, "Read 20 pages")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)

    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    expect(page.locator("ul.rows > li.row")).to_have_count(0)
    expect(page.locator("#nh")).to_be_focused()
    today = band_day(page, "2026-10-10")
    expect(today).to_have_attribute("aria-label", "Sat 10 Oct, 0 of 0 habits")
    expect(today.locator(":scope > svg > circle.seg")).to_have_count(1)
    expect(today.locator(":scope > svg > .seg.on")).to_have_count(0)
    assert stored(page) == '{"version":1,"habits":[]}'


@pytest.mark.parametrize(
    "storage, habit, focus",
    [
        pytest.param(sample_state(), "Read 20 pages", "Year view, Stretch 10 minutes", id="sample-Read"),
        pytest.param(sample_state(), "No phone after 11pm", "Year view, Stretch 10 minutes", id="sample-No-phone"),
        pytest.param(encode([{"name": "Read", "done": []}]), "Read", "the field", id="one-habit-Read"),
    ],
)
def test_R15_R33_deleting_from_the_year_view_closes_both_popups_and_moves_focus(app, storage, habit, focus):
    page = app(viewport=PHONE, storage=storage)
    year_btn(page, habit).click()
    expect(dialog(page, "dlg-year")).to_have_attribute("open", "")
    opener = p2_delete(page)
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)

    expect(dialog(page, "dlg-del")).not_to_have_attribute("open", "")
    expect(dialog(page, "dlg-year")).not_to_have_attribute("open", "")
    assert open_dialogs(page) == []
    assert habit not in names(page)
    target = page.locator("#nh") if focus == "the field" else page.get_by_role("button", name=focus, exact=True)
    expect(target).to_be_focused()


def test_R15_history_goes_with_the_habit(app):
    page = app(storage=sample_state(), install_time=NOON)
    opener = bin_btn(page, "Stretch 10 minutes")
    opener.click()
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    confirm_delete(page, opener)
    expect(page.locator("ul.rows > li.row")).to_have_count(2)
    let_guard_pass(page)
    add_habit(page, "Stretch 10 minutes")

    rows = page.locator("ul.rows > li.row")
    expect(rows).to_have_count(3)
    assert names(page)[-1] == "Stretch 10 minutes"
    assert stats_tree(row(page, "Stretch 10 minutes").locator(":scope > p.stats")) == [current_block()]
    expect(done_btn(page, "Stretch 10 minutes")).to_have_attribute("aria-pressed", "false")
    year_btn(page, "Stretch 10 minutes").click()
    expect(dialog(page, "dlg-year")).to_have_attribute("open", "")
    expect(page.locator("dialog.dlg-year button.yc")).to_have_count(366)
    expect(page.locator("dialog.dlg-year .yc.on")).to_have_count(0)


def test_R15_a_focused_row_out_of_sight_is_scrolled_into_view(app):
    page = app(viewport=PHONE, storage=twelve_state())
    expect(page.locator("ul.rows > li.row")).to_have_count(12)
    read = bin_btn(page, "Read 20 pages")
    tab_to(page, read)
    frame = page.locator("div.frame")
    page.mouse.move(*centre(frame))
    page.mouse.wheel(0, 3000)
    page.wait_for_function(
        "() => { const f = document.querySelector('div.frame'); return f.scrollTop + f.clientHeight >= f.scrollHeight; }", timeout=5000
    )
    expect(read).to_be_focused()
    assert not fully_inside(read.bounding_box(), frame_box(page)), "Read's bin is still in sight"

    page.keyboard.press("Enter")
    expect(dialog(page, "dlg-del")).to_have_attribute("open", "")
    page.keyboard.press("Tab")
    expect(confirm(page)).to_be_focused()
    page.keyboard.press("Enter")

    expect(page.locator("ul.rows > li.row")).to_have_count(11)
    assert "Read 20 pages" not in names(page)
    stretch = bin_btn(page, "Stretch 10 minutes")
    expect(stretch).to_be_focused()
    box, visible = stretch.bounding_box(), frame_box(page)
    assert fully_inside(box, visible), {"bin": box, "frame": visible}


# ---------------------------------------------------------------------------- the title's name (SEC-02 and SEC-06)
#
# An unterminated bidirectional override in a name reorders the text after it, the title's own closing quote and
# question mark included. Two controls work together. SEC-02, the name sits between U+2068 and U+2069, so an override
# cannot get out of it. SEC-06, the title's copy of the name has the bidi format characters taken out (U+202A to
# U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E, U+2029), because a U+2069 or a paragraph separator inside the name
# closes the title's isolate early, and an isolate opener inside the name with no closer takes the title's U+2069. Only
# the title's copy changes. The row, the bin's name and the stored name keep the name as typed.

RLO, RLE, RLI, LRI = chr(0x202E), chr(0x202B), chr(0x2067), chr(0x2066)
PARAGRAPH_SEPARATOR = chr(0x2029)
ALEF, MEEM = chr(0x05D0), chr(0x0645)
SHALOM = "".join(chr(code) for code in (0x05E9, 0x05DC, 0x05D5, 0x05DD))  # a Hebrew word
OLAM = "".join(chr(code) for code in (0x05E2, 0x05D5, 0x05DC, 0x05DD))  # another one

# (the name as stored, the name as the title shows it), in the order of qa.md's Examples.
TITLE_NAMES = {
    "rlo-first": (RLO + "Reversed text here", "Reversed text here"),
    "rlo-in-the-middle": ("Read 20 pages" + RLO + " dleiys .gnp", "Read 20 pages dleiys .gnp"),
    "three-rlo": ("a" + RLO + "b" + RLO + "c" + RLO, "abc"),
    "rle": (RLE + "abc def", "abc def"),
    "rli": (RLI + "abc def", "abc def"),
    "alef-lri-abc": (ALEF + LRI + "abc", ALEF + "abc"),
    "alef-fsi-abc": (ALEF + FSI + "abc", ALEF + "abc"),
    "hebrew-word-lri": (SHALOM + LRI, SHALOM),
    "hebrew-word-space-abc-lri": (SHALOM + " abc" + LRI, SHALOM + " abc"),
    "meem-lri-x": (MEEM + LRI + "x", MEEM + "x"),
    "x-pdi-rlo-y-z": ("x" + PDI + RLO + "y z", "xy z"),
    "x-paragraph-separator-rlo-y-z": ("x" + PARAGRAPH_SEPARATOR + RLO + "y z", "xy z"),
    "alef-lri-abc-pdi": (ALEF + LRI + "abc" + PDI, ALEF + "abc"),
    "plain": ("Read 20 pages", "Read 20 pages"),
    "two-hebrew-words": (SHALOM + " " + OLAM, SHALOM + " " + OLAM),
    "alef-alone": (ALEF, ALEF),
}

# The fourteen characters the title leaves out, and sixteen it keeps, the neighbours of the ranges and other invisible
# and directional characters (U+200E, U+200F and U+061C are marks too, but not the ones that must go).
STRIPPED = [0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069, 0x0085, 0x001C, 0x001D, 0x001E, 0x2029]
KEPT = [0x0084, 0x0086, 0x001B, 0x001F, 0x2028, 0x202F, 0x2065, 0x206A, 0x200E, 0x200F, 0x061C, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF]


def spaced(codes):
    """'x', then each code point followed by 'x'. A name cannot end in white space, and the letters keep each apart."""
    return "x" + "".join(chr(code) + "x" for code in codes)


def left_over(text):
    """The characters of `text` that are not printable ASCII, as U+XXXX, for an assertion message."""
    return [f"U+{ord(character):04X}" for character in text if not 32 <= ord(character) < 127]


# Where the title's quotes, question mark and name characters are drawn, in reading order. The line (in line heights)
# times 100000, plus the left edge. A character with no width (the marks themselves) is left out of `inside`.
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
  if (!node || node.nodeType !== Node.TEXT_NODE) return { nodes: heading.childNodes.length, children: heading.children.length };
  const text = node.data;
  const open = text.indexOf('"'), close = text.lastIndexOf('"'), question = text.lastIndexOf('?');
  const inside = [];
  for (let i = open + 1; i < close; i++) if (spot(i).width > 0) inside.push(spot(i).place);
  return { nodes: heading.childNodes.length, children: heading.children.length,
    open: spot(open).place, inside, close: spot(close).place, question: spot(question).place };
}"""


def open_title_dialog(app, name):
    """The app with one habit stored as `name`, and M1 open from its bin."""
    page = app(storage=encode([{"name": name, "done": []}]))
    page.locator("ul.rows button.btn-bin").first.click()
    return page


@pytest.mark.parametrize("stored_name, shown_name", list(TITLE_NAMES.values()), ids=list(TITLE_NAMES))
def test_R13_the_title_shows_the_name_without_bidi_format_characters_and_its_quotes_stay_in_place(app, stored_name, shown_name):
    page = open_title_dialog(app, stored_name)

    assert title(page) == dialog_title(shown_name), f"characters in the title: {left_over(title(page))}"
    spots = page.evaluate(TITLE_CHARACTER_SPOTS)
    assert spots["nodes"] == 1 and spots["children"] == 0, spots  # one text node and no child element (R24)
    assert spots["inside"], "the name drew no character"
    assert spots["open"] < min(spots["inside"]), spots
    assert max(spots["inside"]) < spots["close"] < spots["question"], spots


def test_R13_every_character_of_the_stripped_set_is_left_out_of_the_title(app):
    page = open_title_dialog(app, spaced(STRIPPED))

    text = title(page)
    assert text == dialog_title("x" * (len(STRIPPED) + 1)), f"characters in the title: {left_over(text)}"


def test_R13_the_neighbours_of_the_stripped_ranges_and_other_invisible_characters_stay_in_the_title(app):
    name = spaced(KEPT)
    page = open_title_dialog(app, name)

    text = title(page)
    assert text == dialog_title(name), f"characters in the title: {left_over(text)}"


def test_R13_R15_only_the_titles_copy_loses_the_characters_and_the_habit_named_in_it_is_the_one_deleted(app):
    name = ALEF + LRI + "abc"
    before = encode([{"name": name, "done": []}, {"name": "Other habit", "done": []}])
    page = app(storage=before, count_writes=True)
    page.locator("ul.rows button.btn-bin").first.click()

    assert title(page) == dialog_title(ALEF + "abc"), f"characters in the title: {left_over(title(page) or '')}"
    assert names(page) == [name, "Other habit"]
    assert page.locator("ul.rows button.btn-bin").first.get_attribute("aria-label") == f'Delete "{name}"'
    assert stored(page) == before
    assert write_count(page) == 0

    page.keyboard.press("Tab")
    expect(confirm(page)).to_be_focused()
    page.keyboard.press("Enter")

    expect(page.locator("ul.rows > li.row")).to_have_count(1)
    assert names(page) == ["Other habit"]
    assert json.loads(stored(page))["habits"] == [{"name": "Other habit", "done": []}]
