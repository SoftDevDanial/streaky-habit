"""R33 and R34: a habit's year view P2, opened from a row's Year, and ticking a day in it (app qa.md, Feature "A habit's
year view").

Each test opens P2 with real gestures and reads the DOM, the focus, boxes and the saved text. The expected days come
from a test-side calendar (conftest `year_date`, `month_title`), and the whole popup is also compared with the golden
`year-view.html` (read only). "A day before a habit was added can be ticked" also adds a habit (qa.md, "Scenarios
that wait on a later task", W19).
"""
import calendar
import datetime
import json

import pytest
from playwright.sync_api import expect

from conftest import (
    TODAY,
    add_habit,
    bead,
    best_block,
    canon_tree,
    current_block,
    first_difference,
    focus_after_a_click_in_a_popup,
    month_title,
    row,
    row_numbers,
    sample_state,
    stats_tree,
    stored,
    wait_for_close,
    watch_close,
    write_count,
    year_btn,
    year_date,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)
YEAR_START = "2025-10-10"  # today's date one year back (habit-logic yearStart), the oldest day P2 can tick

HEAD_JS = """() => {
  const head = document.querySelector('dialog.dlg-year div.sheet-head');
  const tagged = (node) => [node.localName, ...node.classList].join('.');
  const remove = head.querySelector('div.yr-mid > button.btn-del');
  const use = remove.querySelector(':scope > svg > use');
  const legend = head.querySelector('div.yr-tools > p.yr-legend');
  return {
    mid: Array.from(head.querySelector('div.yr-mid').children).map(tagged),
    remove: [remove.getAttribute('type'), remove.getAttribute('aria-haspopup'), use.parentElement.getAttribute('aria-hidden'),
      use.getAttribute('href'), remove.textContent],
    tools: Array.from(head.querySelector('div.yr-tools').children).map(tagged),
    hint: head.querySelector('div.yr-tools > p.hint').textContent,
    legend: [legend.getAttribute('aria-hidden'), Array.from(legend.children).map((node) => [tagged(node), node.textContent])],
  };
}"""

MONTHS_JS = """() => Array.from(document.querySelectorAll('dialog.dlg-year div.months > *')).map((section) => {
  const heading = section.querySelector(':scope > h3');
  const grid = section.querySelector(':scope > div.mgrid');
  return {
    tag: [section.localName, ...section.classList].join('.'),
    labelledby: section.getAttribute('aria-labelledby'),
    parts: Array.from(section.children).map((node) => [node.localName, ...node.classList].join('.')),
    heading: heading && [heading.id, heading.textContent],
    grid: grid && [grid.getAttribute('role'), grid.getAttribute('aria-labelledby')],
    cells: grid ? Array.from(grid.children).map((cell) => {
      const face = cell.querySelector(':scope > span.bead');
      const svg = face && face.querySelector(':scope > svg');
      return {
        tag: cell.localName,
        classes: Array.from(cell.classList).sort(),
        hidden: cell.getAttribute('aria-hidden'),
        type: cell.getAttribute('type'),
        key: cell.getAttribute('data-key'),
        pressed: cell.getAttribute('aria-pressed'),
        label: cell.getAttribute('aria-label'),
        current: cell.getAttribute('aria-current'),
        text: cell.textContent,
        children: cell.childElementCount,
        face: face && [face.childElementCount, svg && svg.getAttribute('aria-hidden'), svg ? Array.from(svg.children).map(
          (node) => [node.localName, node.getAttribute('x'), node.getAttribute('y'), node.getAttribute('dy'), node.textContent]) : null],
      };
    }) : [],
  };
})"""

SECTIONS_JS = """(ids) => ids.map((id) => {
  const box = document.querySelector(`dialog.dlg-year section[aria-labelledby="${id}"]`).getBoundingClientRect();
  return { top: box.top, bottom: box.bottom, left: box.left, right: box.right };
})"""

DAY_CELL_JS = """([id, day]) => {
  const grid = document.querySelector(`dialog.dlg-year section[aria-labelledby="${id}"] > div.mgrid`);
  const cell = Array.from(grid.children).filter((node) => !node.matches('.mwd, .lead'))[day - 1];
  return [cell.localName, Array.from(cell.classList).sort(), cell.textContent];
}"""


def year_dialog(page):
    return page.locator("dialog.dlg-year")


def open_year(page, name):
    year_btn(page, name).click()
    expect(year_dialog(page)).to_have_attribute("open", "")


def year_stats(page):
    return year_dialog(page).locator("div.yr-mid > p.yr-stats")


def classes_of(locator):
    return set(locator.evaluate("(node) => Array.from(node.classList)"))


def months_newest_first():
    """(year, month) from today's month back to the year start's month, the 13 months of the year views."""
    year, month = int(TODAY[:4]), int(TODAY[5:7])
    oldest = (int(YEAR_START[:4]), int(YEAR_START[5:7]))
    months = []
    while (year, month) >= oldest:
        months.append((year, month))
        year, month = (year, month - 1) if month > 1 else (year - 1, 12)
    return months


def days_between(first, last):
    start = datetime.date.fromisoformat(first)
    return [(start + datetime.timedelta(days=i)).isoformat() for i in range((datetime.date.fromisoformat(last) - start).days + 1)]


def wait_until_still(page):
    """The box rises for 220 ms as P2 opens. Its resting place is measured once its animation has ended."""
    page.wait_for_function(
        "() => document.querySelector('dialog.dlg-year > div.dlg-box').getAnimations().length === 0", timeout=5000
    )


# ---------------------------------------------------------------------------------------------------------------


def test_R33_R6_year_opens_the_habits_year_view(app):
    page = app(viewport=PHONE, storage=sample_state())
    year_btn(page, "Read 20 pages").click()
    dialog = year_dialog(page)
    expect(dialog).to_have_attribute("open", "")
    assert dialog.evaluate("(d) => d.matches(':modal')") is True
    expect(dialog.get_by_role("button", name="Close", exact=True)).to_be_focused()
    assert dialog.locator("div.sheet-body").evaluate("(body) => body.scrollTop") == 0

    expect(dialog.locator("h2#yr-title")).to_have_text("Read 20 pages")
    expect(dialog.locator("p#yr-sub")).to_have_text("The last 12 months")
    assert stats_tree(year_stats(page)) == [current_block(4, "days"), best_block(9)]
    assert page.evaluate(HEAD_JS) == {
        "mid": ["p.yr-stats", "button.btn-del"],
        "remove": ["button", None, "true", "#i-trash", "Delete habit"],
        "tools": ["p.hint", "p.yr-legend"],
        "hint": "Tap a day to mark it done or not done.",
        "legend": ["true", [["span.mini.on", ""], ["span", "Done"], ["span.mini", ""], ["span", "Not done"]]],
    }

    sections = page.evaluate(MONTHS_JS)
    months = months_newest_first()
    ids = [f"mo-{year}-{month}" for year, month in months]
    assert len(months) == 13 and len(sections) == 13, [section["labelledby"] for section in sections]
    assert [section["tag"] for section in sections] == ["section.month"] * 13
    assert [section["labelledby"] for section in sections] == ids
    assert [section["heading"] for section in sections] == [[id_, month_title(*month)] for id_, month in zip(ids, months)]
    assert sections[0]["heading"][1] == "October 2026" and sections[-1]["heading"][1] == "October 2025"

    beads, closed, blank, lead = [], [], [], []
    for section, (year, month), id_ in zip(sections, months, ids):
        assert section["parts"] == ["h3", "div.mgrid"], id_
        assert section["grid"] == ["group", id_], id_
        cells = section["cells"]
        assert [(c["tag"], c["classes"], c["hidden"], c["text"]) for c in cells[:7]] == [
            ("span", ["mwd"], "true", letter) for letter in "MTWTFSS"
        ], id_
        leading = datetime.date(year, month, 1).weekday()
        assert [(c["tag"], c["classes"]) for c in cells[7:7 + leading]] == [("span", ["lead", "yc"])] * leading, id_
        lead += cells[7:7 + leading]
        days = cells[7 + leading:]
        assert len(days) == calendar.monthrange(year, month)[1], id_
        for day, cell in enumerate(days, 1):
            cell["date"] = (f"{year:04d}-{month:02d}-{day:02d}", day)
            if cell["tag"] == "button":
                beads.append(cell)
            elif "closed" in cell["classes"]:
                closed.append(cell)
            else:
                blank.append(cell)

    assert len(beads) == 366
    assert sorted(cell["date"][0] for cell in beads) == days_between(YEAR_START, TODAY)
    for cell in beads:
        key, day = cell["date"]
        assert (cell["key"], cell["type"], cell["label"]) == (key, "button", f"Mark {year_date(key)} as done"), cell
        assert cell["children"] == 1 and cell["face"] == [1, "true", [["text", "50%", "50%", ".352em", str(day)]]], cell
    names = {cell["key"]: cell["label"] for cell in beads}
    assert (names[YEAR_START], names[TODAY]) == ("Mark Fri 10 Oct 2025 as done", "Mark Sat 10 Oct 2026 as done")

    done = [cell for cell in beads if cell["pressed"] == "true"]
    not_done = [cell for cell in beads if cell["pressed"] == "false"]
    assert (len(done), len(not_done)) == (250, 116)
    assert all("on" in cell["classes"] for cell in done)
    assert all(not {"on", "l", "r"} & set(cell["classes"]) for cell in not_done)
    threads = [frozenset(cell["classes"]) - {"yc", "today"} for cell in done]
    assert {kind: threads.count(kind) for kind in set(threads)} == {
        frozenset({"on", "l", "r"}): 127,
        frozenset({"on", "l"}): 56,
        frozenset({"on", "r"}): 56,
        frozenset({"on"}): 11,
    }
    today = [cell for cell in beads if "today" in cell["classes"] or cell["current"] is not None]
    assert [(cell["key"], cell["current"]) for cell in today] == [(TODAY, "date")]
    assert {"on", "l"} <= set(today[0]["classes"]) and "r" not in today[0]["classes"]
    oldest = next(cell for cell in beads if cell["key"] == YEAR_START)
    assert {"on", "r"} <= set(oldest["classes"]) and "l" not in oldest["classes"]

    assert [cell["date"][0] for cell in closed] == days_between("2026-10-11", "2026-10-31")
    for cell in closed:
        assert (cell["tag"], cell["classes"], cell["hidden"], cell["key"]) == ("span", ["closed", "yc"], "true", None), cell
        assert cell["face"] == [1, "true", [["text", "50%", "50%", ".352em", str(cell["date"][1])]]], cell
    assert [cell["date"][0] for cell in blank] == days_between("2025-10-01", "2025-10-09")
    assert len(lead) == 39
    for cell in blank + lead:
        assert (cell["tag"], cell["hidden"], cell["children"], cell["text"]) == ("span", "true", 0, ""), cell
    assert all(cell["classes"] == ["blank", "yc"] for cell in blank)

    # The whole popup, head and months, against the golden: the bead classes match it day by day.
    difference = first_difference(
        canon_tree(page, "dialog.dlg-year > div.dlg-box"), canon_tree(page, "dialog.dlg-year > div.dlg-box", golden="year-view.html")
    )
    assert difference is None, difference


@pytest.mark.parametrize(
    "viewport, action",
    [
        pytest.param(PHONE, "clicks Close", id="390x844 Close"),
        pytest.param(PHONE, "presses Escape", id="390x844 Escape"),
        pytest.param(DESKTOP, "clicks Close", id="1280x800 Close"),
        pytest.param(DESKTOP, "presses Escape", id="1280x800 Escape"),
        pytest.param(DESKTOP, "clicks the viewport point (5, 5)", id="1280x800 backdrop"),
    ],
)
def test_R33_R40_p2_closes_and_gives_focus_back_to_its_year(app, viewport, action):
    page = app(viewport=viewport, storage=sample_state())
    open_year(page, "Read 20 pages")
    dialog = year_dialog(page)
    watch = watch_close(page, "dialog.dlg-year")
    if action == "clicks Close":
        dialog.get_by_role("button", name="Close", exact=True).click()
    elif action == "presses Escape":
        page.keyboard.press("Escape")
    else:
        box = dialog.locator(":scope > div.dlg-box").bounding_box()
        assert not (box["x"] <= 5 <= box["x"] + box["width"] and box["y"] <= 5 <= box["y"] + box["height"]), box
        page.mouse.click(5, 5)
    wait_for_close(watch)  # the app's close handler has run, so the focus read is the app's (conftest watch_close)
    expect(year_btn(page, "Read 20 pages")).to_be_focused()


@pytest.mark.parametrize("viewport", [pytest.param(PHONE, id="390x844"), pytest.param(DESKTOP, id="1280x800")])
def test_R33_p2_per_width(app, viewport):
    page = app(viewport=viewport, storage=sample_state())
    open_year(page, "Read 20 pages")
    wait_until_still(page)
    box = year_dialog(page).locator(":scope > div.dlg-box").bounding_box()
    first, second, third = page.evaluate(SECTIONS_JS, ["mo-2026-10", "mo-2026-9", "mo-2026-8"])
    if viewport == PHONE:
        assert all(abs(found - wanted) <= 0.5 for found, wanted in zip(
            (box["x"], box["y"], box["width"], box["height"]), (0, 0, 390, 844))), box
        assert first["bottom"] <= second["top"] and second["bottom"] <= third["top"], (first, second, third)
    else:
        assert abs(box["width"] - 980) <= 0.5 and abs(box["x"] + box["width"] / 2 - 640) <= 0.5, box
        assert box["height"] <= 752, box
        tops = [first["top"], second["top"], third["top"]]
        assert max(tops) - min(tops) <= 1, tops
        assert first["right"] <= second["left"] and second["right"] <= third["left"], (first, second, third)


def test_R34_R32_ticking_a_day_in_the_year_view(app, engine):
    page = app(viewport=PHONE, storage=sample_state(), count_writes=True)
    open_year(page, "No phone after 11pm")
    assert "r" not in classes_of(bead(page, "2026-10-08"))
    handle = bead(page, "2026-10-09").element_handle()
    handle.click()
    assert handle.evaluate("(button) => button.isConnected") is True
    assert handle.get_attribute("aria-pressed") == "true"
    classes = set(handle.evaluate("(button) => Array.from(button.classList)"))
    assert {"on", "l", "pop"} <= classes and "r" not in classes, classes
    assert "r" in classes_of(bead(page, "2026-10-08"))
    # The neighbour 2026-10-08 changed its thread, not its done state, so it keeps its bead still (R32, R34).
    popped = page.evaluate("() => Array.from(document.querySelectorAll('dialog.dlg-year button.yc.pop'), (bead) => bead.dataset.key)")
    assert popped == ["2026-10-09"], f"a bead that did not change carries pop: {popped}"
    assert stats_tree(year_stats(page)) == [current_block(8, "days"), best_block(14)]
    assert write_count(page) == 1
    assert row_numbers(page, "No phone after 11pm")["current"] == "8 days"
    focus_after_a_click_in_a_popup(engine, handle, "dialog.dlg-year")


def test_R34_R16_untick_and_tick_again(app):
    text = sample_state()
    page = app(viewport=PHONE, storage=text)
    open_year(page, "Read 20 pages")
    keys = ["2026-10-07", "2026-10-08", "2026-10-09"]

    def state():
        # "pop" marks the edit, not the state, and a ticked bead must carry it (R32), so it is left out of "as before".
        return [classes_of(bead(page, key)) - {"pop"} for key in keys]

    before = state()
    assert "r" in before[0] and "l" in before[2], before

    target = bead(page, "2026-10-08")
    target.click()
    expect(target).to_have_attribute("aria-pressed", "false")
    after = state()
    assert not {"on", "l", "r"} & after[1], after
    assert "r" not in after[0] and "l" not in after[2], after
    assert stats_tree(year_stats(page))[0] == current_block(2, "days")

    target.click()
    expect(target).to_have_attribute("aria-pressed", "true")
    assert state() == before
    assert json.loads(stored(page)) == json.loads(text)


def test_R34_R10_a_day_before_a_habit_was_added_can_be_ticked(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    add_habit(page, "Drink water")
    expect(row(page, "Drink water")).to_have_count(1)
    open_year(page, "Drink water")
    target = bead(page, "2026-03-15")
    target.click()
    expect(target).to_have_attribute("aria-pressed", "true")
    assert "on" in classes_of(target)
    assert json.loads(stored(page))["habits"][-1] == {"name": "Drink water", "done": ["2026-03-15"]}
    assert stats_tree(year_stats(page)) == [current_block(), best_block(1)]


def test_R34_no_control_exists_after_today_or_before_the_year(app):
    page = app(viewport=PHONE, storage=sample_state())
    open_year(page, "Read 20 pages")
    assert page.locator('button[data-key="2026-10-11"], button[data-key="2025-10-09"]').count() == 0
    assert page.evaluate(DAY_CELL_JS, ["mo-2026-10", 11]) == ["span", ["closed", "yc"], "11"]
    assert page.evaluate(DAY_CELL_JS, ["mo-2025-10", 9]) == ["span", ["blank", "yc"], ""]


def test_R34_R22_beads_are_reached_and_ticked_with_the_keyboard(app):
    page = app(viewport=PHONE, storage=sample_state())
    year = year_btn(page, "Stretch 10 minutes")
    expect(year).to_be_attached()
    is_focused = "(node) => document.activeElement === node"
    assert page.evaluate("() => document.activeElement === document.body") is True
    for _ in range(40):
        if year.evaluate(is_focused):
            break
        page.keyboard.press("Tab")
    assert year.evaluate(is_focused), "Tab never reached Year view, Stretch 10 minutes"
    page.keyboard.press("Enter")
    expect(year_dialog(page)).to_have_attribute("open", "")
    expect(year_dialog(page).locator("h2#yr-title")).to_have_text("Stretch 10 minutes")
    expect(year_dialog(page).get_by_role("button", name="Close", exact=True)).to_be_focused()

    page.keyboard.press("Tab")
    expect(year_dialog(page).locator("button.btn-del")).to_be_focused()
    page.keyboard.press("Tab")
    first = bead(page, "2026-10-01")
    expect(first).to_be_focused()
    expect(first).to_have_attribute("aria-label", "Mark Thu 1 Oct 2026 as done")
    expect(first).to_have_attribute("aria-pressed", "true")

    page.keyboard.press("Space")
    expect(first).to_have_attribute("aria-pressed", "false")
    assert first.evaluate(is_focused)
