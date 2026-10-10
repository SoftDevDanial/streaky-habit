---
version: 1.0.0
kind: uat-pre-run
sitting: 1 of 1
ran_against: running-app @ http://127.0.0.1:8731/
counts: { pass: 6, fail: 0, blocked_product: 0, blocked_script: 1 }
---
# UAT pre-run, sitting 1 of 1

A tester PASS here means the script is runnable. It is not evidence the feature works, and it must not be cited as the version's proof. The human's verdict column in `TEST-CASES.md` was not touched, and nothing in `TEST-CASES.md` was edited.

How it was driven: Python Playwright 1.61.0, headless Chromium, one fresh context for all seven cases in the written order, 1280 x 800, timezone Asia/Kuala_Lumpur, locale en-GB, the real clock (2026-10-10, about 13:27 local). Every click was a real gesture (no force, no dispatch_event), and before each one `elementFromPoint` at the click point was asserted to resolve inside the intended control. Colours, thick and dashed lines and dot sizes were read from the painted pixels of a screenshot as well as from computed style. Console errors and warnings during the run: none.

| case | verdict | observed | screenshot |
|------|---------|----------|------------|
| UAT-01 | BLOCKED (script) | Steps 1-3 and 5-7 matched the Expected result. Step 4 as written does not work: after the mouse click on Add, focus stays on the Add button, so typing `Stretch 10 minutes` without clicking the field first presses Add on the first space (red "Name the habit first.") and only `10 minutes` lands in the field. After I clicked the field myself, steps 5-7 all matched. | uat01-step4-literal-typing-lost.png, uat01-final.png |
| UAT-02 | PASS | Today fills green with a white check; yesterday fills and a 4 px green line joins them; step 3 today hollow again; step 4 filled and joined again. | uat02-final.png |
| UAT-03 | PASS | "2 days" green then "Best 2" grey; step 3 "1 day" with a dashed green line from yesterday into today's open circle; step 4 "2 days" with a solid line. Step 3 also reads "Best 1" (see confusion note 3). | uat03-step3-row.png, uat03-final.png |
| UAT-04 | PASS | Circles 2, 3, 4 and today ticked; "1 day" then "Best 3"; one thick line joins circles 2 to 4; today is filled and not joined. | uat04-final.png |
| UAT-05 | PASS | Today's ringed dot is 17 px, rgb(46,90,80), the same as the legend "All" dot; after step 2 it is 11 px, rgb(79,124,112), the same as the legend middle dot ("1 of 2 habits"); after step 4 it is 17 px again. The one day after today (Sun 11 Oct) has no dot. | uat05-step1-heat.png, uat05-step3-heat.png, uat05-final.png |
| UAT-06 | PASS | The box opens centred with `Delete "Stretch 10 minutes"?`, "Its history is deleted too.", Cancel and Delete habit. Cancel closes it and both habits remain. After the one second wait, Delete habit removes only "Stretch 10 minutes"; "Read 20 pages" is unchanged; today's cell reads "1 of 1 habits" and is the largest kind. | uat06-dialog.png, uat06-final.png |
| UAT-07 | PASS | After reload and after closing the tab and opening a new one, "Read 20 pages" shows the same filled circles, "2 days", "Best 2", and all 84 heatmap cells are identical. No reset note. F5 pressed through automation does not reload headless Chromium, so `page.reload()` was used as instructed. | uat07-step1-after-reload.png, uat07-final.png |

## Script defects

- **UAT-01 step 4: a control not named (the field is never clicked again).** Real behaviour: a mouse click on Add leaves focus on the Add button (this is the specified behaviour, app spec R10, so it is not a product bug). A person who types straight away gets a red "Name the habit first." and a field holding only `10 minutes`; pressing Enter at step 5 would then add a habit called "10 minutes" and every later case drifts from the script. Say instead: "Click the text field again. Type `Stretch 10 minutes` in it."

## Things in the script a person may find confusing (none changed a verdict)

1. **A leftover red error from UAT-01 stays on screen through UAT-02 to UAT-06.** After step 7 the field has a red border and "You already track this habit." under it. Clearing the field (UAT-02 precondition) does not remove them; they go only on the next add. A person may think the app is stuck in an error state. The script could say so in UAT-02's preconditions ("the red line under the field stays until you add something; ignore it").
2. **UAT-02 precondition "select its text and delete it".** Works (click the field, Ctrl+A, Delete), but it is one more thing to do before step 1 and the field holds the lower-case duplicate `read 20 pages`.
3. **UAT-03 step 3: the line also reads "Best 1".** The Expected says only "1 day". "Best" is worked out from the days currently ticked, so unticking today drops Best from 2 to 1. UAT-04's Problem text ("the longest run a habit has ever had", "an old good run is not lost") may lead the owner to expect Best never goes down. Either add "Best 1" to the Expected for step 3 with a one line reason, or reword the Problem.
4. **UAT-06 Expected, "today's dot is the largest kind again".** Today's dot never changed: it was the largest kind before the delete (2 of 2) and after (1 of 1). What visibly changes is other days: the Mon to Wed dots (only Stretch was ticked) turn hollow and Fri's dot grows to the largest. Suggest "today's dot stays the largest kind; the Mon to Wed dots go hollow and Fri's gets bigger".
5. **UAT-07 step 1 "Press F5".** Fine for a person. Only automation cannot press it in headless Chromium.
6. **UAT-06 step 4 timing.** At a normal human pace the 0.5 s guard is never met, so the owner will probably not see it at all, which makes the "you are being asked to rule" paragraph abstract. I measured it (below) so the paragraph can quote it.

## Extras (not cases)

**Midnight rollover, separate fresh context, Playwright clock installed at 23:59:40 local today.** One habit added and today ticked, then `page.clock.run_for(60000)`. Before: clock 23:59:41, header "Saturday 10 October", week strip last day "Mark Sat 10 Oct as done". After 60 s: clock 00:00:41, header "Sunday 11 October", strip now Mon 5 to Sun 11, last day "Mark Sun 11 Oct as done" (**the last day moved to tomorrow: yes**). The Saturday tick moved to the second last circle, a dashed line joins it to the new open circle, the line reads "1 day", "Best 1", and the heatmap's ringed cell is now Sunday ("Sun 11 Oct, 0 of 1 habits"). Screenshots: extra-midnight-before.png, extra-midnight-after.png.

**The two half-second pauses of UAT-06, measured so the owner's ruling rests on an observation** (done after UAT-07 so no case was affected):
- A click on the bin right after pressing Cancel is ignored; no box opens.
- A click on the bin after a calm second opens the box.
- A click on Delete habit about 250 ms after the box opened is ignored (the click's default was prevented, the box stayed open, the habit stayed).
- Not tested: the slow double click that the script says still goes through.

## Run notes

- I ran the driver twice. In the first run three UAT-05/06 checks failed and the midnight extra was wrong, all because of my own measurement (a legend dot read through an anti-aliased row, the ring's declared 1.5 px drawn as 1 px at 1x, and the fake time passed in the wrong unit). I fixed those in `run_prerun.py` and re-ran from a fresh context; the product behaved identically in both runs. The evidence here is the second run. In both runs UAT-01 step 4 behaved the same way.
- Not covered: narrow window layout, keyboard-only use, Safari and Firefox (Chromium only), the 12-habit limit and name-length rules (not in the script).

## Evidence

Folder: `{workspace}\examples\streaks\docs\v1.0.0\user-test-2026-10-10\pre-run\20261010-132500\`. Contains `run_prerun.py` (the driver), `results.json` (verdicts), `results-raw.json` (every check with its detail, 122 checks) and the screenshots named above.

## PROCESSES

- `python.exe run_prerun.py` (my driver), run twice, each launching one headless Chromium through Playwright, plus one short diagnostic script in the session scratchpad (also one Chromium). Why: to drive the cases. All of them exited; a process listing after the last run showed no Chromium, no Playwright driver. STOPPED.
- The `python -m http.server` on 127.0.0.1:8731 (pid 12828) is the orchestrator's. I did not start, stop or touch it; it still answered 200 at the end. A second `python.exe` (pid 16396) was already running and is not mine.
- Every wait was bounded: fixed pauses of 0.3 to 1.5 s, element waits capped at 5 s, each shell command capped at 400 s.
