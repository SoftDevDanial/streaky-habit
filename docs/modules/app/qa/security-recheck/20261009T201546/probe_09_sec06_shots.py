"""Screenshots for SEC-06: the delete dialog for a name that is a Hebrew letter, U+2066 LRI (no closer) and 'abc', with the
fix (served src/view.js) and with the title line put back to the unfixed form in memory. Saves PNGs of the dialog box in
shots/ in this folder, and prints the title text as stored in the node and the habit deleted by Delete habit (it must still be
the habit named in the dialog; the display is the only thing that moves).
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -B <this file>   (cwd = project root)
"""
import pathlib

from chars import ALEF, BS, LRI
from lib import HERE, ROOT, Run, box, centre, open_app, press, snap, state_text

NAME = ALEF + LRI + "abc"
OTHER = {"name": "Other habit", "done": []}


def shot(run, patched, label):
    ctx, page = open_app(run.browser, run.base, (390, 844), False, seed=state_text([{"name": NAME, "done": []}, OTHER]))
    try:
        if patched is not None:
            page.route("**/src/view.js", lambda route, request: route.fulfill(status=200, content_type="text/javascript", body=patched))
            page.reload()
            page.wait_for_selector("li.habit")
        page.locator("li.habit:nth-child(1) .icon-btn").click()
        page.wait_for_selector("dialog[open]")
        page.wait_for_timeout(500)
        out = pathlib.Path(HERE) / "shots"
        out.mkdir(exist_ok=True)
        page.locator("dialog").screenshot(path=str(out / f"sec06-{label}.png"))
        return page, ctx
    except Exception:
        ctx.close()
        raise


def main():
    with Run() as run:
        say = run.say
        view = (ROOT / "src/view.js").read_text(encoding="utf-8")
        fixed_line = '$("#del-title").textContent = `Delete "' + BS + "u{2068}${habitName}" + BS + 'u{2069}"?`;'
        assert view.count(fixed_line) == 1
        unfixed = view.replace(fixed_line, '$("#del-title").textContent = `Delete "${habitName}"?`;')
        for label, patched in (("unfixed", unfixed), ("fixed", None)):
            page, ctx = shot(run, patched, label)
            try:
                say(f"  {label}: title text as stored in the node (repr): {page.locator('#del-title').text_content()!r}; screenshot shots/sec06-{label}.png")
                if label == "fixed":
                    before = snap(page)
                    page.wait_for_timeout(600)
                    press(page, *centre(box(page, "dialog .btn-danger")), False)
                    page.wait_for_timeout(400)
                    after = snap(page)
                    say(f"  fixed: Delete habit on this dialog removes: {sorted(set(before['names']) - set(after['names']))!r} (the habit named in the title); left: {after['names']!r}")
            finally:
                ctx.close()
    run.finish("probe_09")


if __name__ == "__main__":
    main()
