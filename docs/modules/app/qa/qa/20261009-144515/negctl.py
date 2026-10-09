"""Negative control for probe.py: the oracle comparison must report a difference when the app and the model disagree.

Usage: python negctl.py <base_url>
Each case below deliberately lets the model fall behind the app (or vice versa); every one must report problems.
"""
import sys

BASE = sys.argv[1]
sys.argv = ["probe.py", BASE]
import probe  # noqa: E402  (reads sys.argv at import)
from playwright.sync_api import sync_playwright  # noqa: E402


def main():
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            # 1. app ticks a day, model does not
            S = probe.Sess(browser, storage=probe.seed_text(probe.SAMPLE))
            S.day(0, "2026-10-05").click()
            problems = probe.diff_model(S.snap(), probe.sample_model())
            results.append(("tick not in model is detected", bool(problems), problems[:2]))
            S.close()

            # 2. app deletes a habit, model does not
            S = probe.Sess(browser, storage=probe.seed_text(probe.SAMPLE))
            S.open_delete("Read 20 pages")
            S.confirm_delete()
            problems = probe.diff_model(S.snap(), probe.sample_model())
            results.append(("delete not in model is detected", bool(problems), problems[:2]))
            S.close()

            # 3. model on the wrong day
            S = probe.Sess(browser, storage=probe.seed_text(probe.SAMPLE))
            problems = probe.diff_model(S.snap(), probe.sample_model("2026-10-09"))
            results.append(("wrong model day is detected", bool(problems), problems[:2]))
            S.close()

            # 4. the write counter sees a save and the focus reader names the focused element
            S = probe.Sess(browser, storage=probe.seed_text(probe.SAMPLE))
            before = len(S.writes())
            S.day(0, "2026-10-05").click()
            results.append(("write counter sees one save after a tick", len(S.writes()) == before + 1, len(S.writes()) - before))
            results.append(("focus reader names the ticked button", S.active_label() == "Mark Mon 5 Oct as done", S.active_label()))
            S.close()

            # 5. an unreadable-data run must not look like a clean first visit
            S = probe.Sess(browser, storage="{")
            problems = probe.diff_model(S.snap(), probe.Model(probe.D("2026-10-08")))
            results.append(("note page still equals the empty model for the list (sanity: model ignores the note)", problems == [], problems[:2]))
            results.append(("note is read by the snapshot", S.snap()["note"] is not None, S.snap()["note"]))
            S.close()
        finally:
            browser.close()
    for name, ok, observed in results:
        print(("OK   " if ok else "BAD  ") + name + " :: " + str(observed)[:200])
    print("NEGCTL all as expected" if all(ok for _, ok, _ in results) else "NEGCTL PROBLEM")


if __name__ == "__main__":
    main()
