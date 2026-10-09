"""T7 reproduction on the sample data: double click on each row's trash icon CENTRE, at common viewports.

For each viewport and each of the three sample rows: open the app on the sample, double click the exact centre of that
row's trash button (the middle of the icon, the most natural target), and report whether the habit was deleted, with
nothing else done. Then the same with the click point moved to the icon edge. Also: how long after the first click does
the Delete habit button receive pointer events (the dialog fades in over 200 ms, so it is hit-testable while invisible)?
Run: PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, open_app, state_text, row_names, SAMPLE_HABITS

SEED = state_text(SAMPLE_HABITS)
VIEWPORTS = [(1280, 800), (1366, 768), (1440, 900), (1536, 864), (1920, 1080), (1024, 768), (1280, 720), (1280, 1024), (800, 600), (768, 1024), (390, 844), (360, 780), (412, 915)]


def main():
    with Run() as run:
        b, base = run.browser, run.base
        print("--- double click on the CENTRE of each row's trash button (sample, 3 habits)")
        for vp in VIEWPORTS:
            out = []
            for name in ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"]:
                ctx, page, log = open_app(b, base, storage=SEED, viewport=vp)
                trash = page.get_by_role("button", name=f"Delete {name}", exact=True)
                box = trash.bounding_box()
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                page.mouse.dblclick(x, y)
                page.wait_for_timeout(350)
                left = row_names(page)
                state = "DELETED" if name not in left else ("dialog open" if page.evaluate("() => document.querySelector('dialog').open") else "kept")
                out.append(f"{name.split()[0]}={state}")
                ctx.close()
            print(f"   {vp[0]}x{vp[1]}: {', '.join(out)}")

        print("--- how soon is the Delete habit button hit-testable after the trash click? (1280 x 800, row 3)")
        ctx, page, log = open_app(b, base, storage=SEED, viewport=(1280, 800))
        trash = page.get_by_role("button", name="Delete No phone after 11pm", exact=True)
        box = trash.bounding_box()
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        result = page.evaluate(
            """([x, y]) => new Promise((resolve) => {
              const t0 = performance.now();
              const samples = [];
              document.querySelector('.habit:nth-child(3) .icon-btn').click();
              const d = document.querySelector('dialog');
              const tick = () => {
                const e = document.elementFromPoint(x, y);
                const op = getComputedStyle(d).opacity;
                samples.push([Math.round(performance.now() - t0), e ? (e.closest('button') ? e.closest('button').textContent.trim() || e.closest('button').className : e.tagName) : null, op]);
                if (performance.now() - t0 < 320) requestAnimationFrame(tick); else resolve(samples);
              };
              tick();
            })""",
            [x, y],
        )
        seen = []
        for t, el, op in result:
            if not seen or seen[-1][1:] != (el, op):
                seen.append((t, el, op))
        print("   (ms after first click, element under the pointer, dialog opacity) at each change:")
        for s in seen[:14]:
            print("     ", s)
        ctx.close()
    print("done")


if __name__ == "__main__":
    main()
