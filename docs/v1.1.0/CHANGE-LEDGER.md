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
| S7 | A livelier look, chosen from five directions | OPEN, F2 accepted, lock and goldens next | USER | 0 |
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

### S4 - Habits that cannot be saved say so
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** ORCH
**Source:** D-01, owner: "If its the same as split, then no need." Split's ruling (move into 1.1.0) applied by analogy.

If the browser blocks or fills its storage, the page tells the user the habits are not being saved on this device.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (accepted limit) | 2026-10-10 seal | Copy and state in the design round, then plan | ORCH | Open |

### S5 - Tested in Safari's engine too
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** ORCH
**Source:** D-01, owner: "If its the same as split, then no need." Split's ruling (move into 1.1.0) applied by analogy.

The browser tests and the gates also run in WebKit, the engine of Safari on iPhone.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Carried from v1.0.0 (only Chromium was tested) | 2026-10-10 seal | Plan, then build | ORCH | Open |

### S6 - The logo in the app
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** owner: "Wheres the logo. I dont see it being used for both"

The logo shows in the app's header and as the browser tab icon.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's comment. Corrects the v1.0.0 reading "no header mark in the app" | 2026-10-10 seal | Design round | USER | Open |

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
