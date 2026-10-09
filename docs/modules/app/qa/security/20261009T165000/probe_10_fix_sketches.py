"""Verified fix sketches for the two UI findings, applied IN MEMORY by route interception (src/ is never touched).

A. T7 tap-through: an arming window. A click on 'Delete habit' within ARM_MS of the click that opened the dialog is
   cancelled (preventDefault stops the form submit). event.timeStamp is the browser's event time, not the page clock.
   Checks, with the patched app.js: the double click and double tap that deleted before now keep the habit; a deliberate
   click after the window deletes; Enter on the focused button after the window deletes; Cancel works at once.
B. Bidi: wrap the name in the dialog title with FSI and PDI (U+2068, U+2069). Screenshot with an unterminated override.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, new_context, attach, state_text, row_names, SAMPLE_HABITS, ROOT, HERE

SEED = state_text(SAMPLE_HABITS)
ARM_MS = 500

PATCH_APP = """
// --- fix sketch (probe_10): arming window for 'Delete habit'
let openedAt = -Infinity;
document.addEventListener("click", (e) => { if (e.target.closest && e.target.closest(".habit-head .icon-btn")) openedAt = e.timeStamp; }, true);
document.querySelector(".dialog").addEventListener("click", (e) => {
  if (e.target.closest && e.target.closest("button.btn-danger") && e.timeStamp - openedAt < %d) e.preventDefault();
}, true);
boot();
""" % ARM_MS


def open_patched(b, base, vp, touch, patch_app=True, patch_view=False, storage=SEED):
    kw = {"has_touch": True, "is_mobile": True} if touch else {}
    ctx = new_context(b, viewport=vp, **kw)
    page = ctx.new_page()
    page.goto(base + "__seed__")
    page.evaluate("(t) => localStorage.setItem('streaks.state', t)", storage)
    app_text = (ROOT / "src" / "app.js").read_text(encoding="utf-8")
    assert app_text.rstrip().endswith("boot();")
    patched_app = app_text.rstrip()[: -len("boot();")] + PATCH_APP
    view_text = (ROOT / "src" / "view.js").read_text(encoding="utf-8")
    old = '$("#del-title").textContent = `Delete "${habitName}"?`;'
    assert old in view_text
    patched_view = view_text.replace(old, '$("#del-title").textContent = `Delete "\\u2068${habitName}\\u2069"?`;')
    if patch_app:
        page.route("**/src/app.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_app))
    if patch_view:
        page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched_view))
    log = attach(page)
    page.goto(base)
    page.wait_for_selector("li.habit")
    return ctx, page, log


def overlap_point(page):
    trash = page.get_by_role("button", name="Delete No phone after 11pm", exact=True)
    rect = trash.bounding_box()
    trash.click()
    d = page.locator("dialog .btn-danger").bounding_box()
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    left, right = max(rect["x"], d["x"]), min(rect["x"] + rect["width"], d["x"] + d["width"])
    top, bottom = max(rect["y"], d["y"]), min(rect["y"] + rect["height"], d["y"] + d["height"])
    return (left + right) / 2, (top + bottom) / 2


def main():
    with Run() as run:
        b, base = run.browser, run.base
        print("--- A. arming window, patched app.js in memory (ARM_MS=%d)" % ARM_MS)
        for label, vp, touch in [("1440x900 mouse", (1440, 900), False), ("412x915 touch", (412, 915), True)]:
            ctx, page, log = open_patched(b, base, vp, touch)
            x, y = overlap_point(page)
            for gap in (0, 120, 300):
                ctx.close()
                ctx, page, log = open_patched(b, base, vp, touch)
                if touch:
                    page.touchscreen.tap(x, y)
                    page.wait_for_timeout(gap)
                    page.touchscreen.tap(x, y)
                else:
                    page.mouse.click(x, y)
                    page.wait_for_timeout(gap)
                    page.mouse.click(x, y)
                page.wait_for_timeout(700)
                print(f"    {label}: two activations {gap} ms apart at the overlap -> rows={len(row_names(page))} (3 means kept), dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')}")
            ctx.close()
        ctx, page, log = open_patched(b, base, (1440, 900), False)
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.wait_for_timeout(ARM_MS + 150)
        page.locator("dialog .btn-danger").click()
        page.wait_for_timeout(500)
        print(f"    deliberate click after the window deletes: rows={row_names(page)}")
        ctx.close()
        ctx, page, log = open_patched(b, base, (1440, 900), False)
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.wait_for_timeout(ARM_MS + 150)
        page.locator("dialog .btn-danger").focus()
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        print(f"    Enter on the focused Delete button after the window deletes: rows={row_names(page)}")
        ctx.close()
        ctx, page, log = open_patched(b, base, (1440, 900), False)
        page.get_by_role("button", name="Delete Stretch 10 minutes", exact=True).click()
        page.locator("dialog .btn-secondary").click()
        page.wait_for_timeout(300)
        print(f"    Cancel at once works: rows={len(row_names(page))} dialog open={page.evaluate('() => document.querySelector(\"dialog\").open')} errors={log.errors}")
        ctx.close()

        print("--- B. FSI/PDI around the name in the dialog title (patched view.js in memory)")
        hostile = state_text([{"name": "Read 20 pages‮ dleiys .gnp", "done": []}, {"name": "‮Reversed text here", "done": []}])
        ctx, page, log = open_patched(b, base, (360, 780), False, patch_app=False, patch_view=True, storage=hostile)
        for i, slug in enumerate(["fix-rlo-spoof-tail", "fix-rlo-prefix"]):
            page.locator(".habit-head .icon-btn").nth(i).click()
            page.wait_for_timeout(450)
            page.screenshot(path=str(HERE / "shots" / f"{slug}.png"))
            print(f"    {slug}: title text = {page.locator('#del-title').inner_text()!r}")
            page.keyboard.press("Escape")
            page.wait_for_timeout(250)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
