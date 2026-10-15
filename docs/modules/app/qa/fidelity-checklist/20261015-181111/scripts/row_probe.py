"""Explicit values of the FE checklist rows K1 to S3, read on the golden and on the app in the capture states (task 28).

Run from the project root:  python -B <this file> <checklist folder>
Renders each screen as the harness does (dom_compare.render) at each gate viewport, evaluates one expression per
check on both sides, and compares the app's value with the row's stated value and with the golden's. A check marked
app-only reads something the golden draws with a static stand-in (MANIFEST), so only the app's value is judged.
Writes <checklist>/row-probe.json, refusing to overwrite. One server.
"""
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_runner as gr  # noqa: E402

OUT = pathlib.Path(sys.argv[1]) / "row-probe.json"
if OUT.exists():
    sys.exit(f"refused, {OUT} exists")
sys.argv = [sys.argv[0], str(pathlib.Path(sys.argv[1]) / "_unused")]  # dom_compare reads argv[1] at import
import dom_compare as dc  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

T = "(s) => document.querySelector(s)?.textContent.trim()"
A = "([s, a]) => document.querySelector(s)?.getAttribute(a)"
N = "(s) => document.querySelectorAll(s).length"
CS = "([s, p]) => { const e = document.querySelector(s); return e ? getComputedStyle(e).getPropertyValue(p) : null; }"
LIST_T = "(s) => Array.from(document.querySelectorAll(s), (e) => e.textContent.trim())"
LIST_A = "([s, a]) => Array.from(document.querySelectorAll(s), (e) => e.getAttribute(a))"
FIRST_LAST = "([s, a]) => { const l = Array.from(document.querySelectorAll(s), (e) => e.getAttribute(a)); return [l.length, l[0], l[l.length - 1]]; }"
W = "(s) => { const e = document.querySelector(s); return e ? Math.round(e.getBoundingClientRect().width * 100) / 100 : null; }"
MODAL = "(s) => document.querySelector(s)?.matches(':modal') ?? null"

K1_COMMON = [
    ("K1-03", "tab title", "() => document.title", None, "Danial's Streaky Habit", False),
    ("K1-03", "icon link href (R29)", "() => document.querySelector('link[rel~=icon]').getAttribute('href')", None, "src/icon.svg", True),
    ("K1-02", "sprite symbols", "() => Array.from(document.querySelectorAll('body > svg symbol'), (s) => s.id)", None, ["i-x", "i-plus", "i-check", "i-trash"], False),
    ("K1-08", "word", T, "h1.word", "Streaky Habit", False),
    ("K1-11", "date text", T, "time.date", "Saturday 10 October", False),
    ("K1-11", "date datetime", A, ["time.date", "datetime"], "2026-10-10", False),
    ("K1-25", "banners empty and not displayed", "() => [document.querySelector('div.banners').children.length, getComputedStyle(document.querySelector('div.banners')).display]", None, [0, "none"], False),
    ("K1-26", "hidden heading", T, "h2#h-habits.sr", "Habits", False),
    ("K1-26", "list labelled by it", A, ["ul.rows", "aria-labelledby"], "h-habits", False),
    ("K1-39", "composer novalidate", "() => document.querySelector('form.composer').hasAttribute('novalidate')", None, True, False),
    ("K1-40", "field label", T, "label.add-label[for=nh]", "New habit", False),
    ("K1-41", "field attributes", "() => { const i = document.querySelector('input#nh'); return [i.className, i.getAttribute('autocomplete'), i.getAttribute('spellcheck'), i.getAttribute('aria-describedby'), i.hasAttribute('placeholder'), i.value]; }", None, ["input", "off", "false", "nh-msg", False, ""], False),
    ("K1-42", "Add button", "() => { const b = document.querySelector('button#add-btn.btn.btn-primary'); return [b.type, b.textContent.trim(), b.querySelector('use').getAttribute('href')]; }", None, ["submit", "Add", "#i-plus"], False),
    ("K1-43", "message line", "() => { const m = document.querySelector('p#nh-msg.field-msg'); return [m.getAttribute('aria-live'), m.hidden, m.textContent]; }", None, ["polite", True, ""], False),
]
K1_SAMPLE = [
    ("K1-09", "Overview name", A, ["button.ov-btn", "aria-label"], "Overview, today 1 of 3 habits done", False),
    ("K1-13", "band heading and Year", "() => [document.querySelector('h2#h-ov').textContent, document.querySelector('section.band button.btn-all').getAttribute('aria-label'), document.querySelector('section.band button.btn-all').textContent.trim()]", None, ["Last 12 weeks", "Year view, all habits", "Year"], False),
    ("K1-14", "band hint", T, "section.band p.hint", "Tap a day to change it.", False),
    ("K1-17", "month axis", LIST_T, "section.band div.og-mo", ["Jul", "", "Aug", "", "", "", "", "Sep", "", "", "", "Oct"], False),
    ("K1-18", "weekday axis", LIST_T, "section.band div.og-wd", ["M", "T", "W", "T", "F", "S", "S"], False),
    ("K1-19", "band day buttons, first and last name", FIRST_LAST, ["section.band button.hc", "aria-label"], [83, "Mon 20 Jul, 2 of 3 habits", "Sat 10 Oct, 1 of 3 habits"], False),
    ("K1-23", "today cell", "() => { const t = document.querySelector('section.band [aria-current=date]'); return t ? [t.dataset.key, t.tagName] : null; }", None, ["2026-10-10", "BUTTON"], False),
    ("K1-24", "after today", "() => { const s = document.querySelectorAll('section.band span.hc'); return [s.length, s[0]?.getAttribute('aria-hidden'), s[0]?.children.length]; }", None, [1, "true", 0], False),
    ("K1-30", "habit names", LIST_T, "h3.r-name", ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"], False),
    ("K1-31", "bin names", LIST_A, ["button.btn-bin", "aria-label"], ['Delete "Read 20 pages"', 'Delete "Stretch 10 minutes"', 'Delete "No phone after 11pm"'], False),
    ("K1-33", "Current numbers", LIST_T, "span.stat:not(.best) b.num", ["4", "2"], False),
    ("K1-34", "No streak yet", LIST_T, "span.none", ["No streak yet"], False),
    ("K1-35", "Best numbers", LIST_T, "span.stat.best b.num", ["9", "5", "14"], False),
    ("K1-36", "Year names", LIST_A, ["button.btn-year", "aria-label"], ["Year view, Read 20 pages", "Year view, Stretch 10 minutes", "Year view, No phone after 11pm"], False),
    ("K1-37/38", "Done today pressed states", LIST_A, ["button.btn-done", "aria-pressed"], ["true", "false", "false"], False),
]
PHONE_ONLY = [("K1-09", "Overview displayed below 1024", CS, ["button.ov-btn", "display"], "flex", False),
              ("K1-12", "band not displayed below 1024", CS, ["section.band", "display"], "none", False)]
DESK_ONLY = [("K1-09", "Overview not displayed from 1024", CS, ["button.ov-btn", "display"], "none", False),
             ("K1-12", "band displayed from 1024", CS, ["section.band", "display"], "grid", False)]

SCREENS = {
    "today": K1_COMMON + K1_SAMPLE + [("K1-44", "no dialog open", N, "dialog[open]", 0, False)],
    "day-editor": [
        ("P1-08", "title", T, "h2#day-title", "Tuesday 22 September", False),
        ("P1-09", "subtitle", T, "p#day-sub.dlg-sub", "1 of 3 habits", False),
        ("P1-10", "Close", A, ["dialog.dlg-day button.icon-btn", "aria-label"], "Close", False),
        ("P1-12", "tick names", LIST_T, "dialog.dlg-day span.tname", ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"], False),
        ("P1-13/14", "tick pressed", LIST_A, ["dialog.dlg-day button.tick", "aria-pressed"], ["false", "false", "true"], False),
        ("P1-16", "tick numbers", LIST_T, "dialog.dlg-day span.tstat", ["Current 4 days Best 9", "Current 2 days Best 5", "No streak yet Best 14"], False),
        ("P1-03", "open day cell", "() => Array.from(document.querySelectorAll('button.hc.is-open'), (b) => b.dataset.key).filter((k, i, a) => a.indexOf(k) === i)", None, ["2026-09-22"], False),
        ("P1-01/02", "P1 is modal", MODAL, "dialog.dlg-day", True, True),
    ],
    "year-view": [
        ("P2-04", "title and subtitle", "() => [document.querySelector('#yr-title').textContent, document.querySelector('#yr-sub').textContent]", None, ["Read 20 pages", "The last 12 months"], False),
        ("P2-05", "numbers", LIST_T, "dialog.dlg-year p.yr-stats b.num", ["4", "9"], False),
        ("P2-06", "Delete habit", "() => { const b = document.querySelector('dialog.dlg-year button.btn-del'); return [b.type, b.textContent.trim()]; }", None, ["button", "Delete habit"], False),
        ("P2-07", "hint", T, "dialog.dlg-year p.hint", "Tap a day to mark it done or not done.", False),
        ("P2-11", "month titles", "() => { const h = Array.from(document.querySelectorAll('dialog.dlg-year h3'), (e) => e.textContent); return [h.length, h[0], h[h.length - 1]]; }", None, [13, "October 2026", "October 2025"], False),
        ("P2-13", "lead cells", N, "dialog.dlg-year span.yc.lead", 39, False),
        ("P2-15/16/21", "day buttons, first and last name", FIRST_LAST, ["dialog.dlg-year button.yc", "aria-label"], [366, "Mark Fri 10 Oct 2025 as done", "Mark Sat 10 Oct 2026 as done"], False),
        ("P2-16", "done beads", N, "dialog.dlg-year button.yc[aria-pressed=true]", 250, False),
        ("P2-15", "not-done beads", N, "dialog.dlg-year button.yc[aria-pressed=false]", 116, False),
        ("P2-18", "today", "() => document.querySelector('dialog.dlg-year [aria-current=date]')?.getAttribute('aria-label')", None, "Mark Sat 10 Oct 2026 as done", False),
        ("P2-01/02", "P2 is modal", MODAL, "dialog.dlg-year", True, True),
    ],
    "overview": [
        ("P3-02", "head", "() => [document.querySelector('#ov-title').textContent, document.querySelector('dialog.dlg-ov p.hint').textContent, document.querySelector('dialog.dlg-ov button.btn-all').getAttribute('aria-label')]", None, ["Last 12 weeks", "Tap a day to change it.", "Year view, all habits"], False),
        ("P3-04", "weekday letters", LIST_T, "dialog.dlg-ov div.og-wd", ["M", "T", "W", "T", "F", "S", "S"], False),
        ("P3-05", "month column", LIST_T, "dialog.dlg-ov div.og-mo", ["Oct", "", "", "", "Sep", "", "", "", "", "Aug", "", "Jul"], False),
        ("P3-06", "cells, first and last", "() => { const k = Array.from(document.querySelectorAll('dialog.dlg-ov button.hc'), (b) => b.dataset.key); return [k.length, k[0], k[k.length - 1]]; }", None, [83, "2026-10-05", "2026-07-26"], False),
        ("P3-09", "empty cell", N, "dialog.dlg-ov span.hc", 1, False),
        ("P3-01", "P3 is modal", MODAL, "dialog.dlg-ov", True, True),
    ],
    "overview-year": [
        ("P4-03", "head", "() => [document.querySelector('#all-title').textContent, document.querySelector('#all-sub').textContent]", None, ["All habits", "The last 12 months"], False),
        ("P4-04", "hint", T, "dialog.dlg-all p.hint", "Tap a day to change it.", False),
        ("P4-05", "months", "() => { const h = Array.from(document.querySelectorAll('dialog.dlg-all h3'), (e) => e.textContent); return [h.length, h[0], h[h.length - 1]]; }", None, [13, "October 2026", "October 2025"], False),
        ("P4-08", "rings, first and last name", FIRST_LAST, ["dialog.dlg-all button.hc", "aria-label"], [366, "Fri 10 Oct 2025, 3 of 3 habits", "Sat 10 Oct 2026, 1 of 3 habits"], False),
        ("P4-09", "closed days", N, "dialog.dlg-all span.hc.closed", 21, False),
        ("P4-10", "blank cells", N, "dialog.dlg-all span.hc.blank", 9, False),
        ("P4-01/02", "P4 is modal", MODAL, "dialog.dlg-all", True, True),
    ],
    "delete-dialog": [
        ("M1-03", "dialog attributes", "() => { const d = document.querySelector('dialog.dlg-del'); return [d.getAttribute('role'), d.getAttribute('aria-modal'), d.getAttribute('aria-labelledby'), d.getAttribute('aria-describedby')]; }", None, ["alertdialog", "true", "del-title", "del-body"], False),
        ("M1-03", "opened with showModal", MODAL, "dialog.dlg-del", True, True),
        ("M1-05", "title with the isolate marks", T, "h2#del-title", 'Delete "⁨Stretch 10 minutes⁩"?', True),
        ("M1-06", "body", T, "p#del-body", "Its history is deleted too.", False),
        ("M1-08/09", "buttons", "() => Array.from(document.querySelectorAll('dialog.dlg-del div.dlg-actions button'), (b) => [b.className, b.type, b.textContent.trim()])", None, [["btn btn-secondary", "button", "Cancel"], ["btn btn-danger", "button", "Delete habit"]], False),
        ("M1-01", "a page button cannot take focus", "() => { const b = document.querySelector('button.btn-bin'); b.focus(); return document.activeElement === b; }", None, False, True),
    ],
    "today-empty": K1_COMMON + [
        ("S1-03", "lead and line", "() => [document.querySelector('li.empty p.lead').textContent, document.querySelector('li.empty p.line').textContent]", None, ["No habits yet.", "Add one you want to do every day."], False),
        ("S1-04", "band day names", FIRST_LAST, ["section.band button.hc", "aria-label"], [83, "Mon 20 Jul, 0 of 0 habits", "Sat 10 Oct, 0 of 0 habits"], False),
        ("S1-07", "Overview name", A, ["button.ov-btn", "aria-label"], "Overview, today 0 of 0 habits done", False),
        ("S1-08", "frame holds only the empty state", "() => Array.from(document.querySelectorAll('ul.rows > *'), (e) => e.className)", None, ["empty"], False),
        ("S1-09", "composer enabled", "() => [document.querySelector('#nh').disabled, document.querySelector('#add-btn').disabled]", None, [False, False], False),
    ],
    "today-full": [
        ("S3-02", "twelve rows", N, "ul.rows li.row", 12, False),
        ("S3-03", "frame scrolls at its top with the bottom fade", "() => { const f = document.querySelector('div.frame'); return [f.scrollHeight > f.clientHeight, f.scrollTop, document.querySelector('div.frame-wrap').className]; }", None, [True, 0, "frame-wrap more-below"], False),
        ("S3-06", "composer full, field and Add disabled", "() => [document.querySelector('form.composer').className, document.querySelector('#nh').disabled, document.querySelector('#add-btn').disabled]", None, ["composer is-full", True, True], False),
        ("S3-07", "note", "() => { const m = document.querySelector('p#nh-msg'); return [m.className, m.hidden, m.textContent]; }", None, ["field-msg note", False, "You track 12 habits, the most this app holds. Delete one to add another."], False),
        ("S3-09", "Overview name", A, ["button.ov-btn", "aria-label"], "Overview, today 7 of 12 habits done", False),
        ("S3-09", "first band day name", "() => document.querySelector('section.band button.hc')?.getAttribute('aria-label')", None, "Mon 20 Jul, 7 of 12 habits", False),
        ("S3-10", "no page scroll", "() => [document.documentElement.scrollHeight, innerHeight]", None, "equal", False),
    ],
}
WIDTHS = {"delete-dialog": ("M1-03", "dialog width", W, "dialog.dlg-del", {"360x780": 328, "390x844": 358, "1280x800": 400}, False)}


def run_checks(page, checks):
    out = []
    for row, what, expr, arg, expected, app_only in checks:
        try:
            value = page.evaluate(expr, arg) if arg is not None else page.evaluate(expr)
        except Exception as error:  # a missing element reads as an error, never as a pass
            value = f"error: {str(error)[:120]}"
        out.append(value)
    return out


def main():
    proc, port, cmd = gr.start_server()
    base = f"http://127.0.0.1:{port}/"
    result = {"server": {"pid": proc.pid, "port": port, "command": cmd}, "head": gr.git("rev-parse", "HEAD"), "checks": []}
    print(json.dumps(result["server"]), flush=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--hide-scrollbars"])
            for screen, viewports, flags in gr.CAPTURES:
                init_js = after_js = None
                if "--candidate-init-script" in flags:
                    init_js = pathlib.Path(flags[flags.index("--candidate-init-script") + 1]).read_text(encoding="utf-8")
                if "--candidate-after-load" in flags:
                    after_js = pathlib.Path(flags[flags.index("--candidate-after-load") + 1]).read_text(encoding="utf-8")
                for vp in viewports:
                    checks = list(SCREENS[screen])
                    if screen in ("today", "today-empty", "today-full"):
                        checks += DESK_ONLY if vp == "1280x800" else PHONE_ONLY
                    if screen in WIDTHS:
                        row, what, expr, arg, exp, app_only = WIDTHS[screen]
                        checks.append((row, what, expr, arg, exp[vp], app_only))
                    values = {}
                    for side, url, i_js, a_js in (("golden", (gr.ROOT / "docs" / "design" / f"{screen}.html").resolve().as_uri(), None, None),
                                                  ("app", base, init_js, after_js)):
                        w, h = (int(v) for v in vp.split("x"))
                        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, reduced_motion="reduce",
                                                  color_scheme="dark", bypass_csp=True)
                        page = ctx.new_page()
                        page.clock.set_fixed_time(dc.datetime.datetime.fromisoformat(gr.FIXED))
                        page.add_init_script(dc.harness.FREEZE_INIT_JS)
                        if i_js:
                            page.add_init_script(i_js)
                        page.goto(url, wait_until="networkidle", timeout=30000)
                        if a_js:
                            page.evaluate(f"async () => {{ {a_js}\n }}")
                        page.wait_for_timeout(200)
                        values[side] = run_checks(page, checks)
                        ctx.close()
                    for n, (row, what, expr, arg, expected, app_only) in enumerate(checks):
                        app, gold = values["app"][n], values["golden"][n]
                        if expected == "equal":
                            ok_app = isinstance(app, list) and app[0] == app[1]
                            ok_gold = isinstance(gold, list) and gold[0] == gold[1]
                        else:
                            ok_app, ok_gold = app == expected, gold == expected
                        rec = {"capture": f"{screen}-{vp}", "row": row, "check": what, "expected": expected, "app": app,
                               "golden": gold, "app_only": app_only, "app_matches_row": ok_app,
                               "golden_matches_row": None if app_only else ok_gold, "app_equals_golden": app == gold}
                        result["checks"].append(rec)
                        if not ok_app or (not app_only and not ok_gold):
                            print(json.dumps(rec, ensure_ascii=True)[:500], flush=True)
            browser.close()
    finally:
        result["stopped"] = gr.stop_server(proc, port)
        c = result["checks"]
        result["totals"] = {"checks": len(c), "app_matches_row": sum(r["app_matches_row"] for r in c),
                            "golden_matches_row": sum(1 for r in c if r["golden_matches_row"]),
                            "app_only": sum(1 for r in c if r["app_only"])}
        OUT.write_text(json.dumps(result, indent=1, ensure_ascii=True), encoding="utf-8")
        print(json.dumps({"totals": result["totals"], "stopped": result["stopped"]}), flush=True)


if __name__ == "__main__":
    main()
