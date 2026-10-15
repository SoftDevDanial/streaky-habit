"""R38, R39 and R40: the overview popup P3 on a phone and the year of all habits P4 (app qa.md, Feature "The overview
popup and the year of all habits").

Each test opens the running app on the sample day and drives the Overview button, P3's Year or the band's Year with
real gestures. P4's months are also compared cell by cell with `overview-year.html` (read only).
"""
import datetime

import pytest
from playwright.sync_api import expect

from conftest import (
    ARCS3,
    CORE,
    DESIGN_DIR,
    NOON,
    TODAY,
    TODAY_CIRCLE,
    grid_children,
    legend_parts,
    let_guard_pass,
    number,
    ring_of,
    ring_parts,
    sample_state,
    seg,
    short_date,
    wait_for_close,
    watch_close,
    year_date,
)

PHONE = (390, 844)
DESKTOP = (1280, 800)

OVERVIEW_HEAD_JS = """() => {
  const head = document.querySelector('dialog.dlg-ov div.ov-head');
  const named = (node) => [[node.localName, ...node.classList].join('.'), node.id || null,
    node.getAttribute('aria-label'), node.children.length && node.localName !== 'button' ? null : node.textContent];
  return Array.from(head.querySelectorAll('h2, p, button')).map(named);
}"""

GRID_ATTRS_JS = """() => { const grid = document.querySelector('dialog.dlg-ov div.ovg-rows');
  return [grid.getAttribute('role'), grid.getAttribute('aria-labelledby'), grid.childElementCount,
    grid.nextElementSibling && [grid.nextElementSibling.className, grid.nextElementSibling.getAttribute('aria-hidden')]]; }"""


def day_keys(first, count):
    start = datetime.date.fromisoformat(first)
    return [(start + datetime.timedelta(days=i)).isoformat() for i in range(count)]


def test_R38_R42_the_overview_button_opens_p3(app):
    page = app(viewport=PHONE, storage=sample_state())
    button = page.locator("button.ov-btn")
    expect(button).to_have_attribute("type", "button")
    expect(button).to_have_attribute("aria-haspopup", "dialog")
    expect(button).to_have_attribute("aria-label", "Overview, today 1 of 3 habits done")
    expect(button).to_have_text("Overview")
    expect(button.locator(":scope > span.ov-ring")).to_have_attribute("aria-hidden", "true")
    ring_box = button.locator(":scope > span.ov-ring > svg").bounding_box()
    assert (ring_box["width"], ring_box["height"]) == (28, 28)
    assert ring_parts(page, "button.ov-btn > span.ov-ring > svg") == ring_of(
        [seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]
    )

    button.click()
    dialog = page.locator("dialog.dlg-ov")
    expect(dialog).to_have_attribute("open", "")
    assert dialog.evaluate("(d) => d.matches(':modal')") is True
    expect(dialog.get_by_role("button", name="Close", exact=True)).to_be_focused()
    assert dialog.locator("div.sheet-body").evaluate("(body) => body.scrollTop") == 0

    assert page.evaluate(OVERVIEW_HEAD_JS) == [
        ["h2", "ov-title", None, "Last 12 weeks"],
        ["p.hint", None, None, "Tap a day to change it."],
        ["button.btn-all", None, "Year view, all habits", "Year"],
        ["button.icon-btn", None, "Close", ""],
    ]
    assert page.evaluate(GRID_ATTRS_JS) == ["group", "ov-title", 104, ["legend", "true"]]

    grid = grid_children(page, "dialog.dlg-ov div.ovg-rows")
    assert grid[0]["tag"] == "div" and grid[0]["hidden"] == "true" and grid[0]["text"] == "" and grid[0]["cls"] is None
    assert [(cell["cls"], cell["hidden"], cell["text"]) for cell in grid[1:8]] == [("og-wd", "true", letter) for letter in "MTWTFSS"]
    rows = [grid[8 + 8 * week: 16 + 8 * week] for week in range(12)]
    assert [(r[0]["tag"], r[0]["cls"], r[0]["hidden"]) for r in rows] == [("div", "og-mo", "true")] * 12
    assert [r[0]["text"] for r in rows] == ["Oct", "", "", "", "Sep", "", "", "", "", "Aug", "", "Jul"]

    first, last = rows[0][1:], rows[11][1:]
    assert [cell["key"] for cell in first[:6]] == day_keys("2026-10-05", 6)
    assert (first[6]["tag"], first[6]["cls"], first[6]["hidden"], first[6]["ring"]) == ("span", "hc", "true", None)
    assert [cell["key"] for cell in last] == day_keys("2026-07-20", 7)

    buttons = [cell for r in rows for cell in r[1:] if cell["tag"] == "button"]
    assert len(buttons) == 83
    band = {cell["key"]: cell for cell in grid_children(page, "section.band div.ovg-cols") if cell["tag"] == "button"}
    for cell in buttons:
        twin = band[cell["key"]]
        assert (cell["cls"], cell["type"], cell["popup"], cell["label"], cell["current"], cell["ring"]) == (
            twin["cls"], twin["type"], twin["popup"], twin["label"], twin["current"], twin["ring"]
        ), cell["key"]
        assert cell["label"].startswith(short_date(cell["key"]) + ", ")
    today = next(cell for cell in buttons if cell["key"] == TODAY)
    assert today["current"] == "date" and today["ring"]["parts"][0] == TODAY_CIRCLE
    assert [cell["key"] for cell in buttons if cell["current"]] == [TODAY]

    legend = legend_parts(page, "dialog.dlg-ov div.sheet-body > div.legend")
    assert legend == [
        "span:None",
        ring_of([seg(ARCS3[0], False), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE]),
        "span:All",
    ]


@pytest.mark.parametrize("action", ["clicks Close", "presses Escape"])
def test_R38_R40_p3_closes_and_gives_focus_back_to_overview(app, action):
    page = app(viewport=PHONE, storage=sample_state())
    page.locator("button.ov-btn").click()
    dialog = page.locator("dialog.dlg-ov")
    expect(dialog).to_have_attribute("open", "")
    watch = watch_close(page, "dialog.dlg-ov")
    if action == "clicks Close":
        dialog.get_by_role("button", name="Close", exact=True).click()
    else:
        page.keyboard.press("Escape")
    wait_for_close(watch)  # the app's close handler has run (conftest watch_close)
    expect(page.locator("button.ov-btn")).to_be_focused()


def test_R38_R22_p3_cannot_be_reached_on_a_desktop(app):
    page = app(viewport=(1280, 800), storage=sample_state())
    expect(page.locator("section.band div.ovg-cols > button.hc")).to_have_count(83)
    assert page.evaluate("() => document.activeElement === document.body") is True
    for press in range(1, 96):
        page.keyboard.press("Tab")
        found = page.evaluate(
            """() => ({ overview: document.activeElement === document.querySelector('button.ov-btn'),
                        open: document.querySelector('dialog.dlg-ov').open })"""
        )
        assert found == {"overview": False, "open": False}, f"after Tab {press}"


# P4 read the same way from the app's document and from overview-year.html parsed by DOMParser (no script runs). The
# golden draws a segment as <use class="seg" href="#a3-i">, the app as <path class="seg" d="...">, so a ring is read as
# its sequence of parts (today circle, segments with their state, core, number), whose geometry test_R39 checks apart.
P4_JS = """(text) => {
  const root = text ? new DOMParser().parseFromString(text, 'text/html') : document;
  const dialog = root.querySelector('dialog.dlg-all');
  const part = (node) => {
    if (node.classList.contains('c-today')) return 'today';
    if (node.classList.contains('c-core')) return 'core';
    if (node.classList.contains('seg')) return node.classList.contains('on') ? 'seg.on' : 'seg';
    if (node.localName === 'text') return `num.${node.getAttribute('class')}:${node.textContent}@${['x', 'y', 'dy'].map((name) => node.getAttribute(name))}`;
    return node.localName;
  };
  const ring = (svg) => svg && [svg.getAttribute('viewBox'), svg.getAttribute('aria-hidden'), Array.from(svg.children).map(part).join(' ')];
  const cell = (node) => [node.localName, node.getAttribute('class'), node.getAttribute('aria-hidden'), node.getAttribute('type'),
    node.getAttribute('data-key'), node.getAttribute('aria-haspopup'), node.getAttribute('aria-label'), node.getAttribute('aria-current'),
    node.children.length ? null : node.textContent, ring(node.querySelector(':scope > svg')), node.childElementCount];
  const named = (node) => [[node.localName, ...node.classList].join('.'), node.id || null, node.getAttribute('aria-label'),
    node.getAttribute('aria-hidden'), ['div', 'section'].includes(node.localName) && node.children.length ? null : node.textContent.trim()];
  const months = dialog.querySelector('div.sheet-body > div.months');
  return {
    dialog: ['aria-modal', 'aria-labelledby', 'aria-describedby'].map((name) => dialog.getAttribute(name)),
    head: Array.from(dialog.querySelectorAll('div.sheet-head div, div.sheet-head h2, div.sheet-head p, div.sheet-head button')).map(named),
    months: [months.className, months.childElementCount],
    sections: Array.from(months.children).map((section) => {
      const grid = section.querySelector(':scope > div.mgrid');
      return {
        section: [section.localName, section.className, section.getAttribute('aria-labelledby'), section.childElementCount],
        h3: [section.firstElementChild.localName, section.firstElementChild.id, section.firstElementChild.textContent],
        grid: [grid.getAttribute('role'), grid.getAttribute('aria-labelledby')],
        cells: Array.from(grid.children).map(cell),
      };
    }),
  };
}"""

GOLDEN_P4 = (DESIGN_DIR / "overview-year.html").read_text(encoding="utf-8")


def p4_year(page):
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    return page.evaluate(P4_JS, None)


def open_p4_from_p3(page):
    page.locator("button.ov-btn").click()
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    page.locator("dialog.dlg-ov button.btn-all").click()
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")


def test_R39_R42_the_bands_year_opens_p4(app):
    page = app(viewport=DESKTOP, storage=sample_state())
    page.locator("section.band").get_by_role("button", name="Year view, all habits", exact=True).click()
    dialog = page.locator("dialog.dlg-all")
    expect(dialog).to_have_attribute("open", "")
    assert dialog.evaluate("(d) => d.matches(':modal')") is True
    assert page.evaluate("() => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).length") == 1
    expect(dialog.get_by_role("button", name="Close", exact=True)).to_be_focused()
    assert dialog.locator("div.sheet-body").evaluate("(body) => body.scrollTop") == 0

    found = p4_year(page)
    golden = page.evaluate(P4_JS, GOLDEN_P4)
    assert found["dialog"] == golden["dialog"] == ["true", "all-title", "all-sub"]
    assert found["head"] == golden["head"]
    assert [h for h in found["head"] if h[0] in ("h2", "p.dlg-sub", "button.icon-btn", "div.yr-tools", "p.hint", "div.legend")] == [
        ["h2", "all-title", None, None, "All habits"],
        ["p.dlg-sub", "all-sub", None, None, "The last 12 months"],
        ["button.icon-btn", None, "Close", None, ""],
        ["div.yr-tools", None, None, None, None],
        ["p.hint", None, None, None, "Tap a day to change it."],
        ["div.legend", None, None, "true", None],
    ]
    assert legend_parts(page, "dialog.dlg-all div.yr-tools > div.legend") == [
        "span:None",
        ring_of([seg(ARCS3[0], False), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], False)]),
        ring_of([seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE]),
        "span:All",
    ]

    assert found["months"] == golden["months"] == ["months months-all", 13]
    months = [(2026, 10 - i) if i < 10 else (2025, 22 - i) for i in range(13)]
    assert [s["section"] for s in found["sections"]] == [["section", "month", f"amo-{y}-{m}", 2] for y, m in months]
    assert [s["h3"][1:] for s in found["sections"]] == [
        [f"amo-{y}-{m}", f"{datetime.date(y, m, 1):%B} {y}"] for y, m in months
    ]
    assert [s["grid"] for s in found["sections"]] == [["group", f"amo-{y}-{m}"] for y, m in months]
    for index, (mine, twin) in enumerate(zip(found["sections"], golden["sections"])):
        assert mine == twin, f"month {index + 1} differs from overview-year.html"
    assert len(found["sections"]) == len(golden["sections"])

    cells = [cell for s in found["sections"] for cell in s["cells"]]
    for s in found["sections"]:
        assert [(c[0], c[1], c[2], c[8]) for c in s["cells"][:7]] == [("span", "mwd", "true", letter) for letter in "MTWTFSS"]
    by_class = lambda name: [c for c in cells if c[1] == name]  # noqa: E731
    buttons = [c for c in cells if c[0] == "button"]
    assert len(buttons) == 366
    assert all(c[1] == "hc" and c[3] == "button" and c[5] == "dialog" for c in buttons)
    assert sorted(c[4] for c in buttons)[0] == "2025-10-10" and sorted(c[4] for c in buttons)[-1] == TODAY
    assert all(c[6].startswith(year_date(c[4]) + ", ") and c[6].endswith(" of 3 habits") for c in buttons)
    assert "Fri 10 Oct 2025, 3 of 3 habits" in [c[6] for c in buttons]
    assert "Sat 10 Oct 2026, 1 of 3 habits" in [c[6] for c in buttons]
    closed = by_class("hc closed")
    assert [c[9] for c in closed] == [["0 0 40 40", "true", f"num.c-num dim:{day}@20,20,.352em"] for day in range(11, 32)]
    assert all(c[0] == "span" and c[2] == "true" for c in closed)
    blank = by_class("hc blank")
    assert len(blank) == 9 and all(c[0] == "span" and c[2] == "true" and c[10] == 0 for c in blank)
    lead = by_class("hc lead")
    assert len(lead) == 39 and all(c[0] == "span" and c[2] == "true" and c[10] == 0 for c in lead)
    lead_per_month = [sum(c[1] == "hc lead" for c in s["cells"]) for s in found["sections"]]
    assert [lead_per_month[i] for i in (0, 1, 2, 3, 12)] == [3, 1, 5, 2, 2]

    assert [c[4] for c in buttons if c[7] is not None] == [TODAY]
    assert [c[4] for c in buttons if c[9][2].startswith("today ")] == [TODAY]
    on_counts = [c[9][2].split().count("seg.on") for c in buttons]
    assert [on_counts.count(n) for n in range(4)] == [18, 96, 153, 99]
    assert all(("core" in c[9][2].split()) == (c[9][2].split().count("seg.on") == 3) for c in buttons)
    assert ring_parts(page, f'dialog.dlg-all button.hc[data-key="{TODAY}"] > svg') == ring_of(
        [TODAY_CIRCLE, seg(ARCS3[0], True), seg(ARCS3[1], False), seg(ARCS3[2], False), number(10)]
    )
    assert ring_parts(page, 'dialog.dlg-all button.hc[data-key="2025-10-10"] > svg') == ring_of(
        [seg(ARCS3[0], True), seg(ARCS3[1], True), seg(ARCS3[2], True), CORE, number(10, on=True)]
    )


def test_R39_p4_on_a_phone_covers_p3(app):
    page = app(viewport=PHONE, storage=sample_state())
    open_p4_from_p3(page)
    expect(page.locator("dialog.dlg-ov")).to_have_attribute("open", "")
    page.wait_for_function(
        "() => document.querySelector('dialog.dlg-all > div.dlg-box').getAnimations().length === 0", timeout=5000
    )
    box = page.locator("dialog.dlg-all > div.dlg-box").bounding_box()
    # Within half a pixel, as test_year.py reads P2's box. WebKit lays 100dvh out in 1/64 px units (843.984375 here).
    assert all(abs(found - wanted) <= 0.5 for found, wanted in zip(
        (box["x"], box["y"], box["width"], box["height"]), (0, 0, 390, 844))), box
    expect(page.locator("dialog.dlg-all").get_by_role("button", name="Close", exact=True)).to_be_focused()


def test_R39_p4_opens_again_at_its_top_after_it_closed_scrolled(app):
    page = app(viewport=PHONE, storage=sample_state(), install_time=NOON)
    open_p4_from_p3(page)
    body = page.locator("dialog.dlg-all div.sheet-body")
    page.locator('dialog.dlg-all button.hc[data-key="2025-10-10"]').click()
    expect(page.locator("dialog.dlg-day")).to_have_attribute("open", "")
    for name in ("dlg-day", "dlg-all"):
        assert body.evaluate("(node) => node.scrollTop") > 0, f"P4 is not scrolled before {name} closes"
        watch = watch_close(page, f"dialog.{name}")
        page.keyboard.press("Escape")
        wait_for_close(watch)
    let_guard_pass(page)  # the click on P4's day holds clicks on P3 and the page for 500 ms (R14)
    page.locator("dialog.dlg-ov button.btn-all").click()
    expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    assert body.evaluate("(node) => node.scrollTop") == 0, "P4 opened again where it was scrolled to"


@pytest.mark.parametrize(
    "viewport, opener, action",
    [
        pytest.param(DESKTOP, "the band's Year", "clicks Close", id="1280x800 band Close"),
        pytest.param(DESKTOP, "the band's Year", "presses Escape", id="1280x800 band Escape"),
        pytest.param(DESKTOP, "the band's Year", "clicks the viewport point (5, 5)", id="1280x800 band backdrop"),
        pytest.param(PHONE, "P3's Year", "clicks Close", id="390x844 P3 Close"),
        pytest.param(PHONE, "P3's Year", "presses Escape", id="390x844 P3 Escape"),
    ],
)
def test_R39_R40_p4_closes_and_gives_focus_back_to_the_year_that_opened_it(app, viewport, opener, action):
    page = app(viewport=viewport, storage=sample_state())
    if opener == "the band's Year":
        year = page.locator("section.band button.btn-all")
        year.click()
        expect(page.locator("dialog.dlg-all")).to_have_attribute("open", "")
    else:
        open_p4_from_p3(page)
        year = page.locator("dialog.dlg-ov button.btn-all")
    dialog = page.locator("dialog.dlg-all")
    watch = watch_close(page, "dialog.dlg-all")
    if action == "clicks Close":
        dialog.get_by_role("button", name="Close", exact=True).click()
    elif action == "presses Escape":
        page.keyboard.press("Escape")
    else:
        box = dialog.locator(":scope > div.dlg-box").bounding_box()
        assert not (box["x"] <= 5 <= box["x"] + box["width"] and box["y"] <= 5 <= box["y"] + box["height"]), box
        page.mouse.click(5, 5)
    wait_for_close(watch)  # the app's close handler has run (conftest watch_close)
    still_open = page.evaluate("() => Array.from(document.querySelectorAll('dialog')).filter((d) => d.open).map((d) => d.classList[d.classList.length - 1])")
    assert still_open == ([] if opener == "the band's Year" else ["dlg-ov"]), still_open
    expect(year).to_be_focused()
