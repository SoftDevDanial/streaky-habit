"""R1, R2 and R29: the shipped entry point, the stylesheet and the tab icon (app qa.md, Feature "Shipped entry point,
stylesheet and icon").

These three files are copied from the goldens, so each test compares a file with the golden text it must equal, or
opens the page and reads what the skeleton and the icon link give. They read index.html, src/, docs/design/ (read
only) and the running app, and pass or fail. The sub-path scenario adds a habit, so it waits on a later task with a
strict xfail mark (qa.md, "Scenarios that wait on a later task", W2).
"""
import io
import re
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import pytest
from PIL import Image  # the fidelity harness reads its screenshots with Pillow too
from playwright.sync_api import expect

import conftest
from conftest import CLIPBOARD_STANDIN, DESIGN_DIR, ROOT, add_habit, record, sample_state

INDEX_HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SRC_DIR = ROOT / "src"
GOLDEN_K1 = (DESIGN_DIR / "today.html").read_text(encoding="utf-8")

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'"
)
EXPECTED_HEAD = [
    {"tag": "meta", "charset": "utf-8"},
    {"tag": "meta", "http-equiv": "Content-Security-Policy", "content": CSP},
    {"tag": "meta", "name": "viewport", "content": "width=device-width, initial-scale=1, viewport-fit=cover"},
    {"tag": "title", "text": "Danial's Streaky Habit"},
    {"tag": "link", "rel": "icon", "type": "image/svg+xml", "href": "src/icon.svg"},
    {"tag": "link", "rel": "stylesheet", "href": "src/styles.css"},
    {"tag": "script", "type": "module", "src": "src/app.js"},
]


class PageReader(HTMLParser):
    """Collects the head's element children and comments, every src and href value, every xmlns attribute, and
    the href of each link whose rel holds the token "icon"."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.head_children = []
        self.head_comments = []
        self.urls = []
        self.xmlns = []
        self.icon_hrefs = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.urls += [value for name, value in attrs if name in ("src", "href")]
        self.xmlns += [f"{tag} {name}" for name, _ in attrs if name == "xmlns" or name.startswith("xmlns:")]
        if tag == "link" and "icon" in (attributes.get("rel") or "").split():
            self.icon_hrefs.append(attributes.get("href"))
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_head = False
        elif self.in_head:
            self.head_children.append({"tag": tag, **attributes})
            self.in_title = tag == "title"

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        self.in_title = False

    def handle_data(self, data):
        if self.in_head and self.in_title:
            self.head_children[-1]["text"] = self.head_children[-1].get("text", "") + data

    def handle_comment(self, data):
        if self.in_head:
            self.head_comments.append(data)


def read_page(text):
    reader = PageReader()
    reader.feed(text)
    reader.close()
    return reader


def test_R1_head_csp_icon_link_and_relative_urls():
    assert INDEX_HTML.startswith("<!doctype html>")
    assert re.search(r"<html lang=\"en\">", INDEX_HTML)

    reader = read_page(INDEX_HTML)
    assert reader.head_children == EXPECTED_HEAD
    credit = [comment for comment in reader.head_comments if "Phosphor Icons (MIT)" in comment]
    assert len(credit) == 1, reader.head_comments
    for glyph in ('"x"', '"plus"', '"trash"', '"check"'):
        assert glyph in credit[0], glyph
    assert "mark is the app's own" in credit[0]

    assert reader.urls, "index.html names at least its icon, stylesheet and script"
    for url in reader.urls:
        assert not url.startswith("/"), url
        assert "://" not in url, url
    assert reader.xmlns == []

    # `import "x"`, `import { a } from "x"`, `import * as a from "x"` and `export { a } from "x"`.
    specifier = re.compile(
        r"""^\s*(?:import\s+(?:[\w$*{},\s]+?\s+from\s+)?|export\s+(?:\*|\{[^}]*\})\s+from\s+)["']([^"']+)["']""",
        re.MULTILINE,
    )
    checked = 0
    for source in sorted(SRC_DIR.glob("*.js")):
        for found in specifier.findall(source.read_text(encoding="utf-8")):
            assert found.startswith("./"), f"{source.name} imports {found}"
            checked += 1
    assert checked >= 1, "the specifier pattern finds the import in habits.js"


@pytest.mark.xfail(strict=True, reason="task 21")
def test_R1_R29_the_app_works_from_a_sub_path(app):
    if not conftest.SUBPATH_URL:
        pytest.skip("BLOCKED: STREAKS_BASE_URL names a server but STREAKS_SUBPATH_URL is not set (serve the project's parent folder)")
    page = app(base_url=conftest.SUBPATH_URL)
    expect(page.locator("ul.rows > *")).to_have_count(1)
    expect(page.locator("ul.rows > li.empty")).to_have_count(1)
    expect(page.locator("div.ovg-cols button.hc")).to_have_count(83)
    icon_href = page.evaluate("() => document.querySelector('link[rel~=\"icon\"]').href")
    assert icon_href == conftest.SUBPATH_URL + "src/icon.svg"
    add_habit(page, "Read 20 pages")
    expect(page.locator("ul.rows > li.row")).to_have_count(1)


SYMBOL_IDS = ["i-x", "i-plus", "i-check", "i-trash"]
EXPECTED_BODY = [
    ["svg", None],
    ["div", "app"],
    ["dialog", "dlg-full dlg-ov"],
    ["dialog", "dlg-full dlg-all"],
    ["dialog", "dlg-full dlg-year"],
    ["dialog", "dlg-day"],
    ["dialog", "dlg-del"],
]
EXPECTED_DIALOGS = [
    # class, role, aria-modal, aria-labelledby, aria-describedby, as the qa.md table lists them
    {"class": "dlg-full dlg-ov", "role": None, "aria-modal": "true", "aria-labelledby": "ov-title", "aria-describedby": None},
    {"class": "dlg-full dlg-all", "role": None, "aria-modal": "true", "aria-labelledby": "all-title", "aria-describedby": "all-sub"},
    {"class": "dlg-full dlg-year", "role": None, "aria-modal": "true", "aria-labelledby": "yr-title", "aria-describedby": "yr-sub"},
    {"class": "dlg-day", "role": None, "aria-modal": "true", "aria-labelledby": "day-title", "aria-describedby": "day-sub"},
    {"class": "dlg-del", "role": "alertdialog", "aria-modal": "true", "aria-labelledby": "del-title", "aria-describedby": "del-body"},
]

_SKELETON_JS = """() => {
  const attrs = (element, names) => Object.fromEntries(names.map((name) => [name, element.getAttribute(name)]));
  const paths = (element) => Array.from(element.querySelectorAll('path')).map((path) => path.getAttribute('d'));
  const sprite = document.body.firstElementChild;
  const mark = document.querySelector('svg.mark');
  return {
    body: Array.from(document.body.children).map((element) => [element.localName, element.getAttribute('class')]),
    sprite: attrs(sprite, ['width', 'height', 'aria-hidden', 'focusable']),
    symbols: Array.from(sprite.querySelectorAll(':scope > symbol')).map((symbol) => [symbol.id, paths(symbol)]),
    mark: mark && { ...attrs(mark, ['viewBox', 'aria-hidden', 'focusable']), paths: paths(mark) },
    openDialogs: document.querySelectorAll('dialog[open]').length,
    dialogs: Array.from(document.querySelectorAll('dialog')).map((dialog) =>
      attrs(dialog, ['class', 'role', 'aria-modal', 'aria-labelledby', 'aria-describedby'])),
    standIns: document.querySelectorAll('.scrim, .below-desktop, [inert]').length,
    m1Buttons: Array.from(document.querySelectorAll('dialog.dlg-del button')).map((button) =>
      [button.parentElement.className, button.textContent, button.getAttribute('class'), button.getAttribute('type')]),
    forms: Array.from(document.querySelectorAll('form')).map((form) => form.getAttribute('class')),
  };
}"""


def golden_icon_paths():
    """{symbol id: path data} of the four sprite symbols in the K1 golden."""
    paths = {}
    for symbol in SYMBOL_IDS:
        found = re.search(rf'<symbol id="{symbol}" viewBox="0 0 256 256"><path d="([^"]+)"/></symbol>', GOLDEN_K1)
        assert found, f"{symbol} in today.html"
        paths[symbol] = found.group(1)
    return paths


def golden_mark_path():
    found = re.search(r'<svg class="mark" viewBox="0 0 28 28" aria-hidden="true" focusable="false"><path d="([^"]+)"/></svg>', GOLDEN_K1)
    assert found, "the mark in today.html"
    return found.group(1)


def test_R1_static_skeleton_and_the_five_dialogs(app):
    page = app()
    found = page.evaluate(_SKELETON_JS)

    assert found["body"] == EXPECTED_BODY
    assert found["sprite"] == {"width": "0", "height": "0", "aria-hidden": "true", "focusable": "false"}
    icons = golden_icon_paths()
    assert found["symbols"] == [[symbol, [icons[symbol]]] for symbol in SYMBOL_IDS]
    assert found["mark"] == {"viewBox": "0 0 28 28", "aria-hidden": "true", "focusable": "false", "paths": [golden_mark_path()]}
    assert found["openDialogs"] == 0
    assert found["dialogs"] == EXPECTED_DIALOGS
    assert found["standIns"] == 0
    assert found["m1Buttons"] == [
        ["dlg-actions", "Cancel", "btn btn-secondary", "button"],
        ["dlg-actions", "Delete habit", "btn btn-danger", "button"],
    ]
    assert found["forms"] == ["composer"]


STAND_INS_COMMENT = "/* ---------- golden stand-ins"
# (golden text, the text the app has instead), each found exactly once. Changes 2 and 3 of spec R2. Change 1, the
# stand-ins block left out, is the end of the slice in `golden_css`.
R2_CHANGES = [
    (
        "dialog[open]::backdrop, .scrim{ animation:fade 180ms var(--ease); }",
        "dialog[open]::backdrop{ animation:fade 180ms var(--ease); }",
    ),
    (
        "dialog::backdrop{ background:var(--scrim); }",
        "dialog::backdrop{ background:var(--scrim, rgba(10,11,13,.74)); }",
    ),
    (
        ".dlg-day::backdrop{ background:var(--scrim-soft); }",
        ".dlg-day::backdrop{ background:var(--scrim-soft, rgba(10,11,13,.52)); }",
    ),
]


def golden_css():
    """docs/design/system.css from ":root{" up to, and not including, the comment that opens the stand-ins block."""
    text = (DESIGN_DIR / "system.css").read_text(encoding="utf-8")
    start, end = text.index(":root{"), text.index(STAND_INS_COMMENT)
    assert start < end
    return text[start:end]


def comparable(css):
    """Comments removed and runs of white space collapsed to one space, the comparison R2 asks for."""
    return re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)).strip()


def test_R2_stylesheet_is_system_css_without_its_stand_ins_with_the_listed_changes():
    expected = golden_css()
    for before, after in R2_CHANGES:
        assert expected.count(before) == 1, f"the golden has exactly one place for: {before}"
        expected = expected.replace(before, after)

    styles = (SRC_DIR / "styles.css").read_text(encoding="utf-8")
    assert comparable(styles) == comparable(expected)
    for stand_in in (".scrim", "dialog[open]{", ".below-desktop"):
        assert stand_in not in styles, stand_in


ICON_GOLDENS = (
    "today.html", "day-editor.html", "year-view.html", "overview.html",
    "overview-year.html", "delete-dialog.html", "today-empty.html", "today-full.html",
)
SVG_ROOT = "{http://www.w3.org/2000/svg}svg"


def test_R29_the_icon_file_is_the_goldens_icon_byte_for_byte():
    hrefs = {golden: read_page((DESIGN_DIR / golden).read_text(encoding="utf-8")).icon_hrefs for golden in ICON_GOLDENS}
    assert all(len(found) == 1 for found in hrefs.values()), hrefs
    distinct = {found[0] for found in hrefs.values()}
    assert len(distinct) == 1, "the eight goldens carry one identical icon href"
    href = distinct.pop()
    assert href.startswith("data:image/svg+xml,")
    assert read_page((DESIGN_DIR / "states.html").read_text(encoding="utf-8")).icon_hrefs == []

    expected = urllib.parse.unquote(href.split(",", 1)[1], encoding="utf-8").encode("utf-8")
    actual = (SRC_DIR / "icon.svg").read_bytes()
    assert actual == expected
    root = ET.fromstring(actual)
    assert root.tag == SVG_ROOT
    assert root.get("viewBox") == "0 0 16 16"


# Loads the href into an Image under the live CSP, then waits 2 seconds more for a late violation report. Bounded,
# it settles 2 seconds after load or error, or reports "none within 5 s".
_LOAD_ICON_JS = """(href) => new Promise((resolve) => {
  const violations = [];
  document.addEventListener('securitypolicyviolation', (event) => violations.push(event.violatedDirective));
  const image = new Image();
  const settle = (event) =>
    setTimeout(() => resolve({ event, widthAboveZero: image.naturalWidth > 0, violations }), 2000);
  const giveUp = setTimeout(() => resolve({ event: 'none within 5 s', widthAboveZero: false, violations }), 5000);
  image.onload = () => { clearTimeout(giveUp); settle('load'); };
  image.onerror = () => { clearTimeout(giveUp); settle('error'); };
  image.src = href;
})"""


def test_R29_R25_the_page_links_the_icon_and_the_policy_lets_it_load(app):
    page = app(storage=sample_state(), record=True)
    icon_links = page.evaluate(
        "() => Array.from(document.querySelectorAll('link')).filter((link) => link.relList.contains('icon')).map((link) => link.href)"
    )
    assert icon_links == [conftest.BASE_URL + "src/icon.svg"]
    assert page.evaluate(_LOAD_ICON_JS, icon_links[0]) == {"event": "load", "widthAboveZero": True, "violations": []}
    log = record(page)
    assert [message for message in log.console if message["type"] == "error"] == []
    assert log.errors == []


CO1_REASON = (
    "CO-1, WebKit draws the colour scheme of SVG images by its own rules, open WebKit bugs 199134 and 316640 "
    "(research save-warning-and-tab-icon, B8 item 4)"
)
ICON_SIZE = 160  # px for the 16 unit viewBox, so one unit is 10 px
# The path's first part, "M8.5 5H11.5 ... 11.5 8H8.5", is the bar from (8.5, 5) to (11.5, 8). Its middle, (10, 6.5),
# lies 1.5 units from every edge of the bar, so its pixel is the fill colour with no edge blending.
FILL_POINT = (100, 65)
_SHOW_ICON_JS = """(src) => new Promise((resolve, reject) => {
  const image = document.createElement('img');
  image.id = 'icon';
  image.width = image.height = %d;
  image.style.display = 'block';
  const giveUp = setTimeout(() => reject(new Error('the icon neither loaded nor failed within 5 s')), 5000);
  image.onload = () => { clearTimeout(giveUp); resolve(); };
  image.onerror = () => { clearTimeout(giveUp); reject(new Error('the icon failed to load')); };
  image.src = src;
  document.body.replaceChildren(image);
})""" % ICON_SIZE


@pytest.mark.chromium_only(reason=CO1_REASON)
def test_R29_the_icon_is_amber_in_a_dark_theme_and_dark_amber_in_a_light_theme(browser):
    context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, color_scheme="dark")
    context.add_init_script(CLIPBOARD_STANDIN)
    try:
        page = context.new_page()
        page.goto(conftest.BASE_URL + "__seed__")
        page.evaluate(_SHOW_ICON_JS, "src/icon.svg")
        readings = {}
        for scheme in ("dark", "light"):
            page.emulate_media(color_scheme=scheme)
            screenshot = page.locator("#icon").screenshot()
            readings[scheme] = Image.open(io.BytesIO(screenshot)).convert("RGB").getpixel(FILL_POINT)
        assert readings == {"dark": (255, 176, 32), "light": (154, 91, 0)}
    finally:
        context.close()
