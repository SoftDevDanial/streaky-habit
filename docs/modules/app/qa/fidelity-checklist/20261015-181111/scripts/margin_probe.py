"""Follow-up of the states check (task 28): why the composer's computed margin-top differs between the sheet and the app.

Run from the project root:  python -B <this file> <checklist folder>
Reads, for form.composer in states.html (specimen s2a) and in the app after an empty submit (ST-01), the computed
margin-top, the declared margin-top of every stylesheet rule that matches it, its parent's display, and the free
space in its parent. Also makes the noblur copies of the five after-load scripts in this scratch folder (the last
line, document.activeElement.blur(), removed) for the gate runner's noblur batch. Writes
<checklist>/states-composer-margin/probe.json, refusing to overwrite. One server.
"""
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_runner as gr  # noqa: E402

sys.path.insert(0, str(gr.ROOT / "tests" / "browser"))
import conftest as cf  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

OUT = pathlib.Path(sys.argv[1]) / sys.argv[2]
if OUT.exists():
    sys.exit(f"refused, {OUT} exists")

PROBE_JS = """(selector) => {
  const el = document.querySelector(selector);
  const declared = [];
  for (const sheet of document.styleSheets) {
    for (const rule of sheet.cssRules) {
      const rules = (rule instanceof CSSMediaRule) ? Array.from(rule.cssRules).map((r) => [r, rule.conditionText]) : [[rule, null]];
      for (const [r, cond] of rules) {
        if (!r.selectorText || !r.style) continue;
        if (cond && !matchMedia(cond).matches) continue;
        if (el.matches(r.selectorText) && (r.style.getPropertyValue('margin-top') || r.style.getPropertyValue('margin')))
          declared.push({ selector: r.selectorText, media: cond, margin_top: r.style.getPropertyValue('margin-top'), margin: r.style.getPropertyValue('margin') });
      }
    }
  }
  const parent = el.parentElement;
  return { computed_margin_top: getComputedStyle(el).marginTop, declared, parent: parent.tagName.toLowerCase() + '.' + parent.className,
           parent_display: getComputedStyle(parent).display, parent_flex_direction: getComputedStyle(parent).flexDirection };
}"""

# noblur copies of the after-load scripts, for the gate runner (scratch only, never the project)
for name in ("open-day-editor.js", "open-year-view.js", "open-overview.js", "open-overview-year.js", "open-delete-dialog.js"):
    lines = (gr.ROOT / "tests" / "browser" / "fidelity" / name).read_text(encoding="utf-8").rstrip("\n").split("\n")
    assert lines[-1] == "document.activeElement.blur();", (name, lines[-1])
    (HERE / ("noblur-" + name)).write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

proc, port, cmd = gr.start_server()
base = f"http://127.0.0.1:{port}/"
result = {"server": {"pid": proc.pid, "port": port, "command": cmd}, "head": gr.git("rev-parse", "HEAD"), "viewports": {}}
OUT.mkdir(parents=True)
try:
    with sync_playwright() as pw:
        browser = cf.launch(pw, "chromium")
        for vp in ((360, 780), (1280, 800)):
            sctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, device_scale_factor=1, color_scheme="dark")
            sctx.add_init_script(cf.CLIPBOARD_STANDIN)
            sheet = sctx.new_page()
            sheet.goto((gr.ROOT / "docs" / "design" / "states.html").resolve().as_uri())
            ctx, page = cf.open_app(browser, viewport=vp, storage=cf.sample_state(), base_url=base)
            before = page.evaluate(PROBE_JS, "form.composer")
            page.click("#add-btn")
            page.wait_for_function("() => !document.querySelector('#nh-msg').hidden", timeout=5000)
            after = page.evaluate(PROBE_JS, "form.composer")
            result["viewports"][f"{vp[0]}x{vp[1]}"] = {"sheet_s2a": sheet.evaluate(PROBE_JS, "section[aria-labelledby=s2a] form.composer"),
                                                     "app_K1_before_submit": before, "app_after_empty_submit": after}
            ctx.close()
            sctx.close()
        browser.close()
finally:
    result["stopped"] = gr.stop_server(proc, port)
    (OUT / "probe.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))
