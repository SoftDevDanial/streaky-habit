# SEAL: Streaks v1.1.0

**Sealed:** 2026-10-16, on the owner's word at 19:38: "seal both".
**Tag:** `v1.1.0` (local, on the commit that adds this file). This folder is read-only from here on.
**Next working version:** 1.2.0, not opened yet. H-09 can go out alone as 1.1.1 if the owner asks.

## Checks at the seal
- Staleness. The newest ledger entry is S1 row 40 (19:38), newer than the newest handoff (05:34), so the ledger is current.
- Credential gate. Clean over the whole tree (4,220 files), exit 0, the planted control caught and 0 false hits on prose.
- Last green code. `src/` and `index.html` last changed at `40848ce` (2026-10-15 22:38). `sdlc:regression --full`
  passed on it at `18a4227` (2026-10-15 23:58), the cold boot 21 of 21 in Chromium and WebKit with red controls. The
  review, the UAT pre-run, the owner's sitting and the Android layout run all ran on the same code.

## What shipped (from the ledger)

| scope | title | status |
|---|---|---|
| S1 | Edit any past day | SHIPPED, with H-09 below |
| S2 | The streak line says which is Current and which is Best | SHIPPED |
| S3 | A delete guard that does not depend on time | SHIPPED |
| S4 | Habits that cannot be saved say so | SHIPPED, with H-08 below |
| S5 | Tested in Safari's engine too | SHIPPED, the phone cases not run on a real phone |
| S6 | The logo in the app | SHIPPED |
| S7 | A livelier look, chosen from five directions | SHIPPED, with H-09 below |
| S8 | A name that is free to use | SHIPPED |

## UAT (2026-10-16, sitting 1 at the owner's desk, sitting 2 not run on a phone)

| case | scope | tester (pre-run) | owner | Android layout run |
|---|---|---|---|---|
| UAT-01 | S1 Edit any past day | PASS | PASS, one line crossed (step 10, H-09) | |
| UAT-02 | S2 Current and Best | PASS | PASS | |
| UAT-03 | S7 A livelier look | PASS | PASS, with a note (the 12 habit limit, a future upgrade) | |
| UAT-04 | S3 Delete guard | PASS | PASS | |
| UAT-05 | S6 The logo | BLOCKED (seat) | PASS, 3 lines not marked | |
| UAT-06 | S8 The name | PASS | PASS | |
| UAT-07 | S4 Cannot be saved | PASS | PASS | |
| UAT-08 | S5, every screen on a phone | BLOCKED (one script line, repaired) | BLOCKED, not run on an iPhone | PASS |
| UAT-09 | S5 with S1 | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-10 | S5 with S3 | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-11 | S5 with S4 | PASS | BLOCKED, not run on an iPhone | PASS |
| UAT-12 | S5 with S6 | BLOCKED (seat) | BLOCKED, not run on an iPhone | BLOCKED (seat) |

The owner's ruling on the phone cases, "Iphone test cases and even phones just remain as blocked or fail or as not
run. Yes its not what the apps themselves do but data integrity saying its passed when its not tested is bad. So not
run is better with note on why. But the release is still good to be released as it doesnt depend on iphone." The
Android layout run is evidence only. Where tester and owner disagree, the owner's cross on UAT-01 step 10 is the one
that matters, a bug the pre-run and the pixel match could not see because headless Chromium hides scrollbars.
Script, verdicts in his words, and findings: `user-test-2026-10-16/`.

## Known residuals, as ruled
| residual | ruling |
|---|---|
| H-09 the All habits window shows two months per row on a desktop that draws scrollbars (Chrome on Windows) | Deferred to the next version, a bug found at UAT (`docs/future/bugs-found.md`), README known limit |
| H-08 storage allowed again with no reload, the next change saves over the earlier habits | Kept, the warning already says that page is not saving (owner, "No fix needed") |
| H-07 in Safari's engine a popup opened by a tap shows the keyboard focus ring | Kept as built, not checked on a real iPhone |
| Nine or more habits on a phone, the chosen day shows only in part above the day editor | Kept for 1.1.0, the unlimited habits upgrade covers it |
| At most 12 habits | Kept on purpose, an intentional limit (owner, UAT-03) |
| No real iPhone or Android phone used | Phone layouts checked in emulation only (owner's ruling) |
| The earlier limits in the README's Known limits | As listed there |

## Going into the next version
H-09 (`docs/future/bugs-found.md`), the unlimited habits upgrade with a colour per habit (`docs/future/unlimited-habits.md`,
a brainstorm first), the ledger's DEFERRED rows, and the publish prep choice on local paths (handover A5).
