"""R1 and R2: the shipped entry point and the golden stylesheet (app qa.md, "Shipped entry point")."""
import re
from html.parser import HTMLParser

from conftest import DESIGN_DIR, ROOT

INDEX_HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SRC_DIR = ROOT / "src"

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'"
)
EXPECTED_HEAD = [
    {"tag": "meta", "charset": "utf-8"},
    {"tag": "meta", "http-equiv": "Content-Security-Policy", "content": CSP},
    {"tag": "meta", "name": "viewport", "content": "width=device-width, initial-scale=1"},
    {"tag": "title", "text": "Streaks"},
    {"tag": "link", "rel": "stylesheet", "href": "src/styles.css"},
    {"tag": "script", "type": "module", "src": "src/app.js"},
]


class PageReader(HTMLParser):
    """Collects the head's element children and comments, and every src and href value of the page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.head_children = []
        self.head_comments = []
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.urls += [value for name, value in attrs if name in ("src", "href")]
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


def test_R1_head_csp_and_relative_urls():
    assert INDEX_HTML.startswith("<!doctype html>")
    assert re.search(r"<html lang=\"en\">", INDEX_HTML)

    reader = PageReader()
    reader.feed(INDEX_HTML)
    assert reader.head_children == EXPECTED_HEAD
    assert any("Phosphor Icons (MIT)" in comment for comment in reader.head_comments)

    assert reader.urls, "index.html names at least its stylesheet and script"
    for url in reader.urls:
        assert not url.startswith("/"), url
        assert "://" not in url, url

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


def golden_icon_paths():
    """Path data of the three sprite symbols: i-check and i-trash from today.html, i-x from states.html."""
    paths = {}
    for screen, symbols in (("today.html", ("i-check", "i-trash")), ("states.html", ("i-x",))):
        golden = (DESIGN_DIR / screen).read_text(encoding="utf-8")
        for symbol in symbols:
            found = re.search(rf'<symbol id="{symbol}" viewBox="0 0 256 256"><path d="([^"]+)"/></symbol>', golden)
            assert found, f"{symbol} in {screen}"
            paths[symbol] = found.group(1)
    return paths


def test_R1_static_skeleton(app):
    page = app()

    children = page.evaluate(
        "() => Array.from(document.body.children).map((e) => e.tagName.toLowerCase() + '.' + (e.getAttribute('class') || ''))"
    )
    assert children == ["svg.", "div.page", "dialog.dialog"]

    sprite = page.locator("body > svg")
    assert sprite.get_attribute("width") == "0"
    assert sprite.get_attribute("height") == "0"
    assert sprite.get_attribute("aria-hidden") == "true"
    symbols = page.evaluate(
        "() => Array.from(document.querySelectorAll('body > svg > symbol')).map((s) => [s.id, s.querySelector('path').getAttribute('d')])"
    )
    assert [name for name, _ in symbols] == ["i-check", "i-trash", "i-x"]
    assert dict(symbols) == golden_icon_paths()

    dialog = page.locator("dialog.dialog")
    assert dialog.evaluate("(d) => d.open") is False
    assert dialog.get_attribute("role") == "alertdialog"
    assert dialog.get_attribute("aria-modal") == "true"
    assert dialog.get_attribute("aria-labelledby") == "del-title"
    assert dialog.get_attribute("aria-describedby") == "del-body"


STYLE_BLOCK = re.compile(r":root \{.*?/\* ---------- end components ---------- \*/", re.DOTALL)
GOLDEN_SCREENS = ("today.html", "today-empty.html", "delete-dialog.html", "states.html")

# (what the change is, the golden text, the text the app has instead), each applied once. App spec R2.
R2_CHANGES = [
    (
        "the .scrim rule is removed",
        ".scrim { position: fixed; inset: 0; z-index: var(--z-scrim); background: var(--scrim); }",
        "",
    ),
    (
        "the scrim-in animation selector loses .scrim",
        ".scrim, .dialog::backdrop { animation: scrim-in var(--dur) var(--ease); }",
        ".dialog::backdrop { animation: scrim-in var(--dur) var(--ease); }",
    ),
    (
        "the backdrop colour has a fallback",
        ".dialog::backdrop { background: var(--scrim); }",
        ".dialog::backdrop { background: var(--scrim, rgb(28 37 35 / 0.5)); }",
    ),
    (
        "reduced motion reaches the backdrop",
        "*, *::before, *::after { transition: none !important; animation: none !important; }",
        "*, *::before, *::after, ::backdrop { transition: none !important; animation: none !important; }",
    ),
]


def golden_style(screen):
    golden = (DESIGN_DIR / screen).read_text(encoding="utf-8")
    found = STYLE_BLOCK.search(golden)
    assert found, f"{screen} has the golden style block"
    return found.group(0)


def comparable(css):
    """Comments removed and runs of white space collapsed, the comparison R2 asks for."""
    return re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)).strip()


def test_R2_golden_style_block_is_the_same_in_every_golden():
    reference = comparable(golden_style("today.html"))
    for screen in GOLDEN_SCREENS[1:]:
        assert comparable(golden_style(screen)) == reference, screen


def test_R2_stylesheet_is_the_golden_css_with_the_listed_changes():
    expected = golden_style("today.html")
    for what, before, after in R2_CHANGES:
        assert expected.count(before) == 1, f"golden has exactly one place for: {what}"
        expected = expected.replace(before, after)

    assert comparable((SRC_DIR / "styles.css").read_text(encoding="utf-8")) == comparable(expected)
