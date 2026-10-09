"""T7 secondary: a double click on 'Delete habit' (a deliberate delete, clicked twice). Where does the second click land?

After the first click the dialog closes and the list re-renders without the deleted row, so the second click reaches
whatever is now under the Delete button: a day button toggles a day, a trash button opens another dialog. This sweeps the
scroll position at 390 x 844 and 1440 x 900 with 12 habits, double clicks 'Delete habit' and reports what changed besides
the deleted row.
Run: PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python <this file>   (cwd = project root)
"""
from lib import Run, new_context, state_text

HABITS = [{"name": f"Habit {i:02d}", "done": []} for i in range(1, 13)]
SEED = state_text(HABITS)

STATES = "() => [...document.querySelectorAll('li.habit')].map(r => [r.querySelector('.habit-name').textContent, [...r.querySelectorAll('button.day')].map(b => b.getAttribute('aria-pressed')[0]).join('')])"


def main():
    with Run() as run:
        b, base = run.browser, run.base
        for label, vp in [("390x844", (390, 844)), ("1440x900", (1440, 900))]:
            ctx = new_context(b, viewport=vp)
            page = ctx.new_page()
            page.goto(base + "__seed__")
            page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
            page.goto(base)
            page.wait_for_selector("li.habit")
            max_scroll = page.evaluate("() => document.documentElement.scrollHeight - innerHeight")
            outcomes = {}
            examples = {}
            for sy in range(0, max_scroll + 1, 60):
                page.goto(base)
                page.wait_for_selector("li.habit")
                page.evaluate("(y) => window.scrollTo(0, y)", sy)
                row = 5  # a middle row
                page.locator(".habit-head .icon-btn").nth(row).click()
                d = page.locator("dialog .btn-danger").bounding_box()
                x, y = d["x"] + d["width"] / 2, d["y"] + d["height"] / 2
                before = page.evaluate(STATES)
                under_after = None
                page.mouse.dblclick(x, y)
                page.wait_for_timeout(500)
                after = page.evaluate(STATES)
                expected = [r for i, r in enumerate(before) if i != row]
                diff = [(a[0], e[1], a[1]) for a, e in zip(after, expected) if a != e]
                dialog_open = page.evaluate("() => document.querySelector('dialog').open")
                kind = "tick" if diff else ("dialog reopened" if dialog_open else "nothing")
                outcomes[kind] = outcomes.get(kind, 0) + 1
                if kind != "nothing" and kind not in examples:
                    examples[kind] = (sy, diff[:2] if diff else None)
                # reset the stored state for the next iteration
                page.evaluate("(t) => localStorage.setItem('streaks.state', t)", SEED)
            ctx.close()
            print(f"{label}: scroll positions tried {len(range(0, max_scroll + 1, 60))}; outcome of the second click: {outcomes}; examples {examples}")
    print("done")


if __name__ == "__main__":
    main()
