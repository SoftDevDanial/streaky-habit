"""Dialog screenshots for hostile names, taken after the 200 ms enter animation (probe_06 shot the first frame, before
the dialog had faded in, so its dialog-*.png files show only the page). Output: shots/dlg-*.png.
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, HERE

SHOTS = HERE / "shots"
CASES = {
    "rlo-spoof-tail": "Read 20 pages‮ dleiys .gnp",
    "rlo-prefix": "‮Reversed text here",
    "rlo-only-quotes": "‮",
    "invisible-zwsp": "​" * 40,
    "zalgo": "Z" + "҉̸̶̀́̂̃̄̅̕" * 3 + "̆" * 9,
    "forty-W": "W" * 40,
    "dialog-words": 'a" and "Delete habit',
}


def main():
    SHOTS.mkdir(exist_ok=True)
    with Run() as run:
        b, base = run.browser, run.base
        for slug, name in CASES.items():
            ctx, page, log = open_app(b, base, storage=state_text([{"name": name, "done": ["2026-10-08"]}, {"name": "Second", "done": []}]), viewport=(360, 780))
            page.locator(".habit-head .icon-btn").first.click()
            page.wait_for_timeout(450)
            info = page.evaluate("() => ({title: document.querySelector('#del-title').textContent, open: document.querySelector('dialog').open, focus: document.activeElement.textContent.trim()})")
            page.screenshot(path=str(HERE / "shots" / f"dlg-{slug}.png"))
            print(f"{slug}: dialog open={info['open']} focus={info['focus']!r} title={info['title']!r}", flush=True)
            ctx.close()
    print("done")


if __name__ == "__main__":
    main()
