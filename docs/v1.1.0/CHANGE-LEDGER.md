# CHANGE LEDGER - v1.1.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** · corrections are **additive and
> dated**, never a silent rewrite · **staleness check** at every phase boundary.

**Version:** v1.1.0 · **Opened:** 2026-10-10 at the v1.0.0 seal, from the owner's UAT verdicts and rulings
(`docs/v1.0.0/user-test-2026-10-10/`, `docs/v1.0.0/SEAL.md`) · **Sealed:** not yet

> **This version is not delegated.** The owner asked to run the design phase with him. Decisions he makes are
> tagged USER, decisions the orchestrator makes in between are tagged ORCH and stay reversible.

## At a glance

| scope | title | status | tag | open items |
|---|---|---|---|---|
| S1 | Edit any past day | OPEN, reach now 12 months | USER | 0 |
| S2 | The streak line says which is Current and which is Best | OPEN | USER | 0 |
| S3 | A delete guard that does not depend on time | OPEN | USER | 0 |
| S4 | Habits that cannot be saved say so | OPEN | USER | 0 |
| S5 | Tested in Safari's engine too | OPEN | USER | 0 |
| S6 | The logo in the app | OPEN | USER | 0 |
| S7 | A livelier look, chosen from five directions | OPEN, goldens final in docs/design (2026-10-13), plan next | USER | 0 |
| S8 | A name that is free to use | OPEN, name ruled | USER | 0 |

---

## Scope sections

### S1 - Edit any past day
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** UAT-02 and UAT-F2, owner: "a big limitation is that we cant input something that we did last week or change a specific date habit incase we input it wrong or want to add something we just remembered." Then: "For streaks, the missing previous dates is actually a big thing." Approved for 1.1.0: "3.  Yes."

The user can open an older day and tick or untick its habits, to fix a mistake or add something remembered late. Reverses the v1.0.0 non-goal "Editing days older than the last 7" (an ORCH call).

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's UAT request | 2026-10-10 seal | Brainstorm delta (how far back, days before a habit existed, how the day is opened), design, plan to follow | USER | Open |
| 2 | Reach and route changed by the owner's round 1 ruling (H-02): each habit gets its own year view covering the last 12 months, and a day tapped in the overview still opens the day editor | 2026-10-10 21:49 design | Brainstorm delta "Round 1 rulings" appended, round 2 brief | USER | Open |
| 3 | A third route added by the owner's round 2 ruling (H-02): the overview gets its own year view of the last 12 months, every habit together, and a day tapped there opens the day editor | 2026-10-10 22:59 design | Brainstorm "Round 2 rulings", `round-2/BRIEF-F2.md` | USER, ORCH on the readings | Open |
| 4 | Clarify gate part 2, items the planner found where no input decides (CG-12, CG-13, CG-19) | 2026-10-13 21:15 plan | USER, his recommended answers. CG-12 "'0 of 0 habits', 'No habits yet.'", the day editor with no habits (app R19). Corrected 2026-10-13 21:30 after the plan check (N4), CG-12 is app R36, not R19. CG-13 "28 February last year", the reach on 29 February (habit-logic task 8). CG-19 (in the four accepted together) a day editor left open on the oldest day past midnight stays on its day and its ticks change nothing | USER | Ruled |

### S2 - The streak line says which is Current and which is Best
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** UAT-03 and UAT-F4, owner: "I think it needs to show that left side is current and right is best". Approved for 1.1.0: "3.  Yes."

Each habit's streak line names its two numbers, so nobody has to guess which is the current run.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's UAT request | 2026-10-10 seal | Design round | USER | Open |

### S3 - A delete guard that does not depend on time
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** the owner's v1.1.0 choice on 2026-10-09 ("Fix the v1.0 limits"). UAT-06 pauses kept for 1.0, owner: "very minor, i think just keep it unless its an easy change".

A slow double click can never delete a habit, and Delete habit no longer waits half a second.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 | 2026-10-10 seal | Plan, then build | USER | Open |
| 2 | Clarify gate part 2, items the planner found where no input decides (CG-10, CG-11) | 2026-10-13 21:05 plan | USER, his recommended answers. CG-10 "Ignore a click on the same spot", Delete habit ignores a mouse or touch click inside the box of the control that opened the dialog or counted as a second click, a keyboard press always works, no time window (app R13). CG-11 "Keep and extend it", the 1.0 half-second guard against taps falling through a popup stays and covers every popup (app R14) | USER | Ruled |

### S4 - Habits that cannot be saved say so
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** ORCH
**Source:** D-01, owner: "If its the same as split, then no need." Split's ruling (move into 1.1.0) applied by analogy.

If the browser blocks or fills its storage, the page tells the user the habits are not being saved on this device.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (accepted limit) | 2026-10-10 seal | Copy and state in the design round, then plan | ORCH | Open |
| 2 | Clarify gate part 1 on the research (docs/brainstorm/research/save-warning-and-tab-icon.md), CG-1 and CG-2 | 2026-10-13 18:45 plan | USER "Yes, show it at once (Recommended)", the warning shows at boot when the browser refuses storage outright. USER on the known limit "Yes not it in the readme. maybe we can note that since this is a showcase, a detection isnt built. Or if its bad for showcase then just note the limitations". ORCH reading, the README states the limit and its reason (a private window and Safari's 7-day clean-up report every save as working, so no page can tell), not "not built", since no reliable detection exists. UAT drives the warning with storage blocked in the browser settings. The plan replaces the 1.0 rule that a failed save shows no message | USER, ORCH on the README wording | Ruled, plan next |
| 3 | Clarify gate part 2, items the planner found where no input decides (CG-17) | 2026-10-13 21:15 plan | USER "Save warning first", the warning comes before the unreadable note, as in Splity Tab (app R16, R41). Corrected 2026-10-13 21:30 after the plan check (N4), CG-17 is app R17 and R41, not R16 and R41 | USER | Ruled |

### S5 - Tested in Safari's engine too
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** ORCH
**Source:** D-01, owner: "If its the same as split, then no need." Split's ruling (move into 1.1.0) applied by analogy.

The browser tests and the gates also run in WebKit, the engine of Safari on iPhone.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (only Chromium was tested) | 2026-10-10 seal | Plan, then build | ORCH | Open |
| 2 | Clarify gate part 1 on the research (docs/brainstorm/research/webkit-testing.md). The owner asked "Do we really need to test it on safari? Does this do any impact for showcase. Also, will playwright be used in the future". Answered in chat (every iPhone browser runs WebKit, links get opened on phones, Playwright already runs every build of both apps) | 2026-10-13 18:40 plan | USER "Keep it, install WebKit (Recommended)", so the build may run python -m playwright install webkit (about 62 MB, Playwright's download server). USER "Suites and live gates (Recommended)", the pixel match against the goldens stays Chromium only. No preference on two questions, so the recommendations apply. A WebKit failure in the suites or the live gates blocks the seal. Chromium-only tests are skipped in WebKit with a written reason and counted. Where WebKit acts differently by design the spec states each engine's behaviour. The v1.1.0 UAT adds a few cases he runs on his own iPhone. The plan amends the CLAUDE.md stack line and the 1.0 spec lines that say Chromium only | USER, ORCH on the two without a preference | Ruled, plan next |

### S6 - The logo in the app
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "Wheres the logo. I dont see it being used for both"

The logo shows in the app's header and as the browser tab icon.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's comment. Corrects the v1.0.0 reading "no header mark in the app" | 2026-10-10 seal | Design round | USER | Open |
| 2 | Clarify gate part 1 on the research (docs/brainstorm/research/save-warning-and-tab-icon.md). The golden's tab icon is a data URL, which both apps' CSP blocks and the 1.0 no-scheme rules forbid. CG-3 and CG-4 | 2026-10-13 18:45 plan | USER "Yes, a file (Recommended)", the tab icon ships as src/icon.svg, the golden's decoded SVG byte for byte, linked from index.html, CSP as strict as 1.0. Only the head link differs from the golden, nothing visible. USER "Header and tab only (Recommended)", Safari 26 showing one icon colour in both themes is accepted as Safari's bug and checked in UAT. A home-screen icon is deferred (off-scope row 7) | USER | Ruled, plan next |

### S7 - A livelier look, chosen from five directions
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "Both designs are great but is just that its so dull. Need to spice it up so it looks nicer" and "Propose 5 designs for both app. Doesnt need to be working, i just want the design part." Then: "as long as i can see the design. Including popups and modals or anything that requires a button click"

A new look the owner picks from five clickable static directions, then a new golden set.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's comment | 2026-10-10 seal | Design round with him | USER | Open |
| 2 | Round 1, five clickable directions on the key screen with every popup and state reachable | 2026-10-10 design | A Night Console `44362bd`, B Neon Thread `6776272`, C Daylight Instrument `c3dbdb5`, D Orbit Rings `2784715`, E Command Line `10ab8da`, each by its own designer agent with render checks at 390, 360 and 1280 px (0 console errors, no sideways scroll at 360). round-1/compare.html `a5ca2a9` with the orchestrator's pick A, runner-up B. All five turn the 12-week heatmap on its side so every past day is a tap target, a 1.0 rule change put to the owner (H-02) | ORCH (designer agents) | Waiting for the owner's pick (H-02) |
| 3 | Owner's pick (H-02 ruling): D Orbit Rings' look, with a new layout of his own (a habit list, a per-habit year view, an overview calendar) | 2026-10-10 21:43 design | Round 2 brief `round-2/BRIEF.md`, one new direction F "Orbit List". His words and the readings in H-02 | USER, ORCH on the readings | Round 2 next |
| 4 | Round 2 direction F Orbit List built (`a2867e1`, 122 of 122 render asserts). Owner's review of F (H-02 round 2 ruling): keep the overview at 12 weeks, add a year popup for the overview on desktop and phone, add a delete button on every habit row | 2026-10-10 22:59 design | `round-2/BRIEF-F2.md`, revision F2 "Orbit List, revised" built from F by one designer agent | USER, ORCH on the readings | F2 next |
| 5 | Revision F2 "Orbit List, revised" built by one designer agent: the overview's year view P4 (every habit, the last 12 months, from the band on a desktop and from P3 on a phone) and a bin on every row. Verified on disk: designer's 252 of 252 asserts, the orchestrator's own 60 of 60 at 1280, 390 and 360 px (no page scroll, 366 P4 days, P4 day opens P1, Esc order P1 then P4 then P3, row bin opens M1 with that habit's name, focus after a delete, add field unmoved, 0 console errors, 0 network). round-2/compare.html (round 1 D, F, F2, every reading flagged) | 2026-10-10 23:45 design | `4701776` F2, compare page this commit. Orchestrator's pick F2 | ORCH (designer agent) | Owner reviewed, row 6 |
| 6 | Owner's review of F2 (H-02 final ruling): "everything looks good. Only thing is the numbers surrounded by the yellow lines should be centered. Feels like its downwards abit." Measured: the ring numbers sat 1.38 viewBox units low on a desktop and 1.55 on a phone (of 40), from `dominant-baseline: central` (the font's em box, not the digits) plus a y of 20.5. Fixed by the orchestrator in f2.html: the alphabetic baseline at y 20 with dy .367em (half a figure height), and proportional figures so a "1" no longer pulls a number right. After the fix 0.12 units off on a desktop and 0.36 on a phone, horizontal within 0.6. Then: "Both looks good. We can procceed as usual" | 2026-10-11 00:58 design | f2.html `.c-num` and the two ring text elements, this commit | USER, ORCH (the fix) | F2 accepted. Design proceeds to step 5 |
| 7 | Design steps 5, 6 and 8 composed from F2 by one composer agent. system.md and system.css locked, nine goldens in design-explore/v1.1.0/final/ (today, day-editor, year-view, overview, overview-year, delete-dialog, today-empty, today-full, states), sample-history.json, MANIFEST, LINKS, SELF-CRITIQUE. Its check 97 of 97 | 2026-10-11 02:19 design | `809477f`. The composer's two shortcuts fixed by the orchestrator `2b7b712`: K1 under P3 and P4 is today.html's K1 with its band, states.html inlines system.css byte for byte (check tightened, 97 of 97) | LANE (composer), ORCH on the fixes | Solved |
| 8 | Design step 7, wire and verify. The flow check found one golden defect. Chromium's own accessibility tree read the Overview button as "Overview , today 1 of 3 habits done" (a hidden span beside a flex item gets a space). Its helper also clicked an inert Close under the top dialog | 2026-10-11 12:00 design | Overview button carries the documented name as aria-label, the span is gone, nothing visible changed. flowcheck_v.py skips inert matches, clicks radios through their label, matches raw clicks by point, runs a link without a width at 360, 390 and 1280. FLOW-CHECK.md 49 of 49 links, zero errors. check.py 97 of 97 after the change | ORCH | Solved |
| 9 | The composer's copy list, seven interaction rules and three open items needed a written record before plan, as 1.0 had | 2026-10-11 13:50 design | docs/design-explore/v1.1.0/RULINGS.md. Copy and rules approved as written, phone header 12 px (`d786d25`), the up to 1 px sideways ink of ring and bead numbers left as is, desktop day cells 40 to 42 px accepted (WCAG 2.5.8 met), the mark redrawn from the orbit ring. SELF-CRITIQUE open items 1 and 2 marked ruled. check.py 97 of 97. This commit | USER | Solved |
| 10 | The mark redrawn from the orbit ring (RULINGS, The mark). Logo round 1 with the logo-design skill | 2026-10-11 21:05 design | Five directions drawn by designer agents and reviewed by logo-qa agents (logo/QA.md), T1, T3 and T4 passed, T2 and T5 retired. Owner's board round picked T6, the 1.0 thread with one ring arc round the top left bead. T6 drawn and passed QA 18 of 24, arc ends moved onto whole pixels. Owner rulings, no tile or background anywhere, the favicon's 1 px open ring accepted as in 1.0, dark amber #9A5B00 on light grounds (the favicon switches under prefers-color-scheme light). T6 approved. Swapped into the eight final goldens' header mark and tab icon (viewBox 0 0 28 28). check.py 97 of 97, FLOW-CHECK 49 of 49 links, zero errors | USER, LANE (designer and QA agents), ORCH on the swap | T6 in final/. docs/design/ only at the finalize gate with his word |
| 11 | Design step 9, finalize gate. Asked to approve the nine final goldens with T6 and to replace 1.0's goldens in docs/design/, the owner answered "Yes, but later" (2026-10-11 23:45, RULINGS) | 2026-10-13 design | final/ copied into docs/design/, 23 files (9 goldens with their .md, system.css, system.md, sample-history.json, LINKS.json, MANIFEST.md), 12 new and 11 replacing 1.0's (1.0's stay in tag v1.0.0), every SHA-256 equal to its source. v1.1.0 rulings beside 1.0's as docs/design/RULINGS-v1.1.0.md (1.0's RULINGS.md still stands unless replaced), as 1.0's finalize copied its rulings. checks/ and SELF-CRITIQUE.md stay in design-explore (the checks reach round-2/). check.py rerun with its golden folder pointed at docs/design/, 97 of 97, every results section equal to the final/ run (design-explore/v1.1.0/finalize/). Phase skills loaded throughout the round, taste-skill and frontend-design (docs/design/system.md) | USER (the approval), ORCH (the copy) | Solved. Goldens immutable, plan next |
| 12 | Clarify gate part 2, items the planner found where no input decides (CG-14, CG-15, CG-16, CG-18) | 2026-10-13 21:15 plan | USER. CG-15 "Yes, show the new row", the list frame scrolls to a new habit. CG-14, CG-16 and CG-18 "Accept all four", focus after a rollover removes the focused control goes to the top popup's open-focus target or the page's first control, the overview popup labels the newest row, the oldest row and any row whose Monday is day 1 to 7, focus after deleting the last row from the year view goes to the Year button of the row above or the add field | USER | Ruled |
| 13 | The finalize copy of 2026-10-13 replaced docs/design/sample-history.json with the v1.1.0 format, which the sealed 1.0 suites still read. tests/browser/conftest.py reads heatmapLevels at import and three unit test files import the sample, so the suites are red before any v1.1.0 work. The finalize check (check.py, 97 of 97) covered the goldens, not the app's suites. Also two golden notes disagree with the goldens (today.md names a today-warning.html that does not exist, and says states.html shows hover, focus and press, it holds only the S2, S4 and S5 frames). Goldens are immutable, the golden HTML wins | 2026-10-13 19:20 plan | Found by the planner. The plan's first tasks restore the 1.0 file byte for byte as tests/fixtures/sample-history-v1.0.0.json and point the 1.0 tests at it (habit-logic task 6, app task 11). The planner also fixed four defects in its own contracts, each with a dated note (the WebKit focus note, a ring.js contract, the design-row task range, two task cross-references) | ORCH (planner) | Fix planned, plan check verifies the red state |

### S8 - A name that is free to use
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** D-02, owner: "Streaky Habit", then "Check if its ok to be used... if both names cant be used, then add Danials [app name] Or if theres a better way to make it uniquely to me."

A product name no other habit app uses, shown in the new wordmark and the logo lockup.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Name check: "Streaky" is used by three habit trackers (two on the App Store, one on Google Play). Not usable | 2026-10-10 seal | His fallback applies. Chosen with him in the design round | USER | Open |

---

## Off-scope and new

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | The UAT script layout, owner: "i want steps and expected result in a table... Bigger fonts for UAT number... include some sort of verdict selection examples" | 2026-10-10 seal | Process, not app: the layout is designed in the same round as S7 and used for the 1.1.0 UAT | USER | Open |
| 2 | Owner's answers before the design round (2026-10-10 16:42): "1. Decide for me. Lets have a starting ground. We can work from there" "2. I like those futuristic type of apps or websites. Like discord and stuff like that. Futuristic but minimal." "3. I like that a lot." "4. Lets go with that first." "5. Danial's Splity Tab and Danial's Streaky Habit. Logo wise, dont need danial or even initial D. Danial is just to make it unique." "6. Sure" | 2026-10-10 brainstorm | Name set (S8), feeling words and the five directions chosen by the orchestrator as the starting ground, the past-day reach and the spare-sen line approved, three UAT sheet layouts. Name check: no app named "Splity" or "Splity Tab" found (nearest "Splitly"), and the "Danial's" prefix keeps both names unique | USER | Ruled |
| 3 | Brainstorm delta for v1.1.0 | 2026-10-10 brainstorm | Appended to docs/brainstorm/brainstorm.md: the name, the new and changed capabilities, the rules (USER where he decided, ORCH where the orchestrator settled details so design can start), the grill log rows. One theme may now be dark. Still system fonts and no network | USER, ORCH | Written |
| 4 | Design brief for v1.1.0 with the five directions | 2026-10-10 design | docs/design-explore/v1.1.0/BRIEF.md: who, the key screen's job, feeling words, his words, constraints, the logo rule, the inventory with exact figures, the prototype rules, five direction theses | ORCH | Written, design round next |
| 5 | UAT sheet layout chosen (row 1). Designed once in the Split folder with real Split cases and used for both apps. Owner 2026-10-10, after three layouts and two revisions: "Besides that i am happy with the design." Full words and the rules (PASS, FAIL, BLOCKED with a note on any, a tick or cross per expected line, NOT RUN and RETEST set by the sheet) in the Split v1.1.0 ledger, Off-scope row 5 | 2026-10-10 design | split/docs/design-explore/v1.1.0/uat-sheet/c2.html "C revised". TEST-CASES.md stays the record | USER | Ruled. Used for the 1.1.0 UAT of both apps |
| 6 | Plan phase opened (sdlc:continue, sdlc 2.6.0). The project's docs/constitution.md was the older copy, without the sections Gates and evidence and the clipboard rule, and the explainer role | 2026-10-13 18:20 plan | docs/constitution.md replaced with the installed sdlc 2.6.0 copy (SHA-256 equal to the plugin's), so every plan and build agent reads the current law. Two researchers started, WebKit testing (S5) and the save warning with the tab icon (S4, S6), findings in docs/brainstorm/research/, shared by both apps | ORCH | Reversible, the old copy is in git |
| 7 | A home-screen icon (iPhone and Android) | 2026-10-13 18:45 plan | Not built in v1.1.0. Why, a home-screen icon needs a filled tile, against the owner's no-tile ruling, and iOS paints a transparent icon black. Blocking item, a tile logo round with the owner | USER "Header and tab only (Recommended)" | DEFERRED |
| 8 | Planner process note. One planner edited its own qa.md with one sed -i in the shell, against the Write-tool rule | 2026-10-13 21:15 plan | Only its own file inside the project changed, and it checked the result with grep. Later briefs forbid any shell write | ORCH (planner) | Noted |
| 9 | Plan check (coverage gate) on the v1.1.0 contracts. BLOCK, 1 BLOCK, 11 FLAG, 7 NOTE (docs/modules/PLAN-CHECK.md). B1, task 11 expects the sealed 179 passed on the unchanged src, but four more 1.0 browser tests read goldens the finalize replaced. F1, the contracts still marked CG-10 to CG-19 pending after the owner ruled them. Others on an example figure, the 1.0 strip tests, the clipboard stand-in in fidelity scripts, a live gate control, the RED-first method for new exports, README items, prose colons, checklist rows, a retired scenario marker, a threat row | 2026-10-13 21:27 plan | Routed to one planner fix pass. B1 by restoring the four 1.0 goldens from tag v1.0.0 as test fixtures, the same approach as the 1.0 sample (ORCH, reversible). N4 was two wrong citations in this ledger, corrected in place with a dated note | ORCH (plan checker, routing) | Fix pass running, re-check next |
| 10 | Plan check fix pass on B1, F1 to F11, N1 to N7 | 2026-10-13 21:55 plan | One planner pass with Edit only. B1, the four 1.0 goldens come back byte for byte from tag v1.0.0 into tests/fixtures/design-v1.0.0/ at app task 11 (blob ids named), task 12 removes them with their readers. F1, CG-10 to CG-19 marked ruled with ledger rows. F3, task 12 removes the 1.0 browser test files and names who rewrites each, @R30 moves to a new test_engines.py. F4, the clipboard stand-in loads before the page in every fidelity seed. F5, a live gate control run with --control seeded that must fail. F6, the RED-first method is a throwaway stub. F8, prose colons and the semicolon removed. App scenarios 165 live, checklist 139 rows | ORCH (planner) | Fixed per the planner, re-check running |

---

## Needs the human

### H-01 - The name (S8)
- **What:** "Streaky" and "Streaky Habit" are taken in spirit by three habit trackers. His fallback is his own name with the app name ("Danial's Streaks") or another way to make it his.
- **Why an agent cannot decide it:** the name of his public showcase piece is his.
- **Options:** decided in the design round, beside the wordmark.
- **Ruling:** (pending)
- **Ruling, added 2026-10-10:** "Danial's Splity Tab and Danial's Streaky Habit. Logo wise, dont need danial or even initial D." (Off-scope row 2). The logo and header show "Streaky Habit".

### H-02 - Which design direction, and the heatmap turned on its side (S7)
- **What:** round 1 gave five directions (round-1/compare.html). All five make weeks the rows and weekdays the 7 columns (C only below 720 px), where the 1.0 rule was 12 columns, one per week.
- **Why an agent cannot decide it:** the look is his pick, and the heatmap shape is a 1.0 rule.
- **Options:** pick one direction, ask for a mix (one new direction in round 2), or reject all. Accept or refuse the turned heatmap.
- **Recommendation:** A Night Console (closest to "like discord", a date on every past day, the most rewarding tick), runner-up B Neon Thread. Accept the turned heatmap: 12 columns give about 24 px per day on a phone, 7 columns give 41 to 47 px, and every past day must now be a tap target.
- **Ruling, 2026-10-10 21:43 (owner's words):** "1. I like Orbit Rings. 2. For dekstop, make the numbers in the calendar bigger. The habit should be fixed so th at if thers multiple habit, it doesnt make the input field pushed down. 3. You know what, i think we need to change the design. Design is like this instead. Colors, fonts and all of that is good. Instead, we list down the habits . Each list will have 3 functionality. A button or icon to say that we did that habit today ( so its like a daily thing someone needs to login and click it). But if they forget and they remember later on, they can click the second button to open a modal. The modal will show all days of the year and we can click the date which we remember we did. Each list will have its own current and best streak number both at the list level and modal level. The big calendar on the right, we can have an overview at the top. So it will be an overview at the top, bottom is the div that contains the list and its scrollable. Not the page but the div only. Outside of that div either before or after, is the input. Design calendar wise for overview, i like the current orbit ones but just make the number bigger. 4. For mobile, using the same logic before, have a fixed input below. Then at the top or a button somewhere that will show overview calendar as a popup or a different page. Below that is the list and the same logic as desktop."
- **Clarified, 2026-10-10 21:49 (his answers):** the year view shows the **last 12 months** (today back to the same date last year, future days closed). Tapping a day in the overview **opens that day** in the day editor (every habit for that day), a second way to fix the past.
- **Readings (ORCH, reversible, flagged on the round 2 page):** (a) The per-habit seven-day ring goes, replaced by the row's Done today button and the year view. (b) The turned heatmap is accepted by "i like the current orbit ones": the overview keeps D's small rings with one segment per habit and the 12 weeks, numbers bigger. On a wide desktop band its orientation is the designer's call, shown to him. (c) The input sits below the list on every width, like a chat composer, pinned on the phone. (d) Delete habit moves into the habit's year view, so each row keeps his three functions. (e) Done today toggles, a second tap unticks today.
- **Round 2 ruling, 2026-10-10 22:59 (owner's words, after seeing F):** "For streaky mobile or overview, it should be last 12 weeks but have a button to check last year because each habit on the list has yearly selection so we need some sort of yearly popup for overview as well. Both desktop and mobile. Also, n eed button or icon to remove a habit in the list itself as well"
- **Readings (ORCH, reversible, flagged on the round 2 compare page):** (f) The overview's year view (P4) shows every habit together in D's small rings, the same last 12 months as a habit's year view, newest month first, and a day tapped there opens the day editor. (g) Its Year button sits in the overview band's header on a desktop and in the overview popup's header on a phone. (h) Delete habit stays in the habit's year view too ("as well"), so a habit can be deleted from its row or from its year view.
- **Round 2 recommendation (ORCH, 2026-10-10 23:45):** take F2 forward (`round-2/compare.html`). Designer readings put to him there: the bin on the name line on a phone and in its own column after the name on a desktop, weeks as columns on the desktop band, the word "Year" without an icon, the amber thread in P2, and one inherited pair at 2.97 to 1 (a thin not-done segment on a hovered or open day), left for the lock step.
- **Final ruling, 2026-10-11 00:52 to 00:58 (owner's words):** "For Streaky, everything looks good. Only thing is the numbers surrounded by the yellow lines should be centered. Feels like its downwards abit." Then "Both looks good. We can procceed as usual". **F2 is the direction**, with the ring numbers centred (S7 row 6). Readings (a) to (h) and the designer's readings stand as shown on the compare page. The 2.97 pair is the orchestrator's call at the lock step.

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `OPEN` · `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
