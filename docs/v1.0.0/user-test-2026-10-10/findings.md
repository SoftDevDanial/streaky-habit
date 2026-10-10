# UAT findings: Streaks 1.0.0, sitting 1 (2026-10-10)

The owner's verdicts are 7 of 7 PASS. The tester agreed on every verdict that it reached on the final script.
Each finding below is keyed by its case and routed (LITE for a script or wording fix, FULL for a new scope).

| id | case | what the owner said | routing | status |
|---|---|---|---|---|
| UAT-F1 | UAT-01 | "not sure why its blocked by tester but it was good" | Answer only | Closed: the BLOCKED was the first draft of the script, not the app |
| UAT-F2 | UAT-02 | "a big limitation is that we cant input something that we did last week or change a specific date habit incase we input it wrong or want to add something we just remembered. Think about it and if its a good idea then implement it. If not report to me why." | FULL: a new 1.1.0 scope | Assessed a good idea. In 1.1.0, his yes on 2026-10-10 |
| UAT-F3 | UAT-02 | "we can have a continous streak for something we do for weeks also. LIke, read 20 pages, i read everydya. Then next week also everyday, it should be a continous streak." | Checked, no change needed | Closed: already works, proof below |
| UAT-F4 | UAT-03 | "I think it needs to show that left side is current and right is best" | FULL: a 1.1.0 design change (the streak line is in the golden) | In 1.1.0, his yes on 2026-10-10 |
| D-02 | handover | "Streaky Habit", then "if both names cant be used, then add Danials [app name] Or if theres a better way to make it uniquely to me" | FULL: a rename touches the golden wordmark, the logo lockup and every document | Neither name is free, the name is chosen in the 1.1.0 design round |

## UAT-F1: why the tester said BLOCKED
The first draft of UAT-01 step 4 typed straight after a click on Add. The keyboard was still on the Add button, so the
first space pressed Add again. The tester marked the case BLOCKED for a script reason, the step was rewritten to click
the field first, and the tester drove the new step and it matched. The owner tested the fixed script, so his PASS is right.

## UAT-F2: editing past days
**Assessment: a good idea.** A tracker you cannot correct drifts away from the truth, and the brainstorm's non-goal
("Editing days older than the last 7") was an orchestrator call made under delegation, not the owner's. Points the
1.1.0 brainstorm and design must settle: how far back (the 12-week heatmap is the natural reach, tapping a day there
could open that day), whether a day before a habit was added can be ticked, and how a past edit shows in the streaks.
The core already counts any ticked day, so the change is mostly where and how a past day is opened.

## UAT-F3: a streak across weeks
**Already works.** The streak counts back through the whole history, not just the visible week. Proof with a
controlled clock, one habit ticked on 10 days in a row from Thursday 1 to Saturday 10 October: the line reads
"1 day" on day 1 and "10 days, Best 10" on day 10, and the thread runs off the left edge of the week strip to show
the run goes on (`evidence-uat-f3/`). The 1.0 script only covered one week, which is why it did not show.

## D-02: "Streaky Habit"
Two habit trackers already use the name "Streaky": "Habit Tracking: Streaky" on the App Store (with a yearly heatmap)
and "Streaky: Habit Tracker" on Google Play. "Streaky Habit" sits close to both. It is his call, so the rename waits
for his confirmation, and it would land in 1.1.0 through the design phase.

**Second check (2026-10-10 16:31), after he asked for "SplitIO" for Split.** A third tracker, "Streaky: Streak, Habit Tracker", is also on the App Store. "SplitIO" is Split.io, the feature-flag company Harness bought in 2024, a well-known name in software. Neither is free, so his fallback applies: his own name with the app name, or another way to make it his. The name and the wordmark are chosen together in the 1.1.0 design round.

## Owner comments on both apps (2026-10-10)
Recorded word for word in the CHANGE-LEDGER. Logo not seen in the apps, both designs too plain,
a better test-case layout with a design round run with him, and UAT material in the public showcase. Routing is
agreed with him in the conversation that follows.
