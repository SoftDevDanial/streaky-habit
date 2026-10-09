"""Follow-up probes after the mutation spot-check: the gaps it showed (sorted and de-duplicated saves,
dialog returnValue persistence in this Chromium). Usage: python probe2.py <base_url>"""
import json
import sys

BASE = sys.argv[1]
sys.argv = ["probe.py", BASE]
import probe  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--force-color-profile=srgb"])
        try:
            # (a) unsorted + duplicated saved days: the next save is sorted and de-duplicated
            raw = '{"version":1,"habits":[{"name":"Read","done":["2026-10-08","2026-10-07","2026-10-08"]}]}'
            S = probe.Sess(browser, storage=raw)
            S.day(0, "2026-10-05").click()
            saved = json.loads(S.snap()["stored"])["habits"][0]["done"]
            probe.rec("P2.sorted", "R16/R17", "after loading unsorted+duplicated days and ticking another day, the saved list is ascending and has no duplicates",
                      saved == ["2026-10-05", "2026-10-07", "2026-10-08"], saved)
            S.day(0, "2026-10-08").click()
            saved = json.loads(S.snap()["stored"])["habits"][0]["done"]
            probe.rec("P2.dedupe-toggle", "R8/R17", "un-ticking a day that was saved twice removes it completely",
                      saved == ["2026-10-05", "2026-10-07"] and S.day(0, "2026-10-08").get_attribute("aria-pressed") == "false", saved)
            S.close()
            # a future day kept in storage survives a save (spec: dates after today are kept)
            raw = '{"version":1,"habits":[{"name":"Read","done":["2026-10-09","2026-10-08"]}]}'
            S = probe.Sess(browser, storage=raw)
            S.day(0, "2026-10-07").click()
            saved = json.loads(S.snap()["stored"])["habits"][0]["done"]
            probe.rec("P2.future-kept", "R17", "a saved future day (2026-10-09) is kept by the next save and never shown",
                      saved == ["2026-10-07", "2026-10-08", "2026-10-09"] and S.page.locator('button[data-date="2026-10-09"]').count() == 0, saved)
            S.close()
            # extra properties vanish at the next save, __proto__ key ignored
            raw = '{"version":1,"habits":[{"name":"Read","done":[],"color":"red","__proto__":{"polluted":true}}],"theme":"dark"}'
            S = probe.Sess(browser, storage=raw)
            S.day(0, "2026-10-08").click()
            probe.rec("P2.extras", "R17", "extra properties are dropped at the next save",
                      S.snap()["stored"] == '{"version":1,"habits":[{"name":"Read","done":["2026-10-08"]}]}', S.snap()["stored"])
            S.close()
            # (b) returnValue persistence in this Chromium, on a plain dialog (no app code)
            ctx = browser.new_context()
            page = ctx.new_page()
            page.set_content("<dialog id=d><form method=dialog><button value=cancel>c</button><button id=del value=delete>d</button></form></dialog>")
            page.evaluate("() => document.getElementById('d').showModal()")
            page.locator("#del").click()
            first = page.evaluate("() => document.getElementById('d').returnValue")
            page.evaluate("() => document.getElementById('d').showModal()")
            page.keyboard.press("Escape")
            second = page.evaluate("() => document.getElementById('d').returnValue")
            print("returnValue after submit:", repr(first), "| after reopen + Escape:", repr(second), "| chromium", browser.version)
            probe.rec("P2.returnValue", "R14", "(info) plain dialog: returnValue after Esc following an earlier 'delete' submit", True, f"after submit {first!r}, after reopen+Esc {second!r}")
            ctx.close()
        finally:
            browser.close()
    results = [r for r in probe.RESULTS]
    (probe.OUT / "probe2-results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
