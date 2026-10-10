# UAT: Streaks 1.0.0

> **Sitting 1 of 1.** Seven cases, one per scope section of `docs/v1.0.0/CHANGE-LEDGER.md`.
> Written from your seat: "I asked for X. Is X there, does it look right, can I use it?"
>
> **How to use this.** The app is already running. The orchestrator started it and gives you the address
> when it hands this over. Work the cases in order, because each one starts where the last one ended. On each
> case, record **your** verdict in the right-hand column. Every case gets a verdict, including the ones you
> could not do. `BLOCKED` means "I could not work out how to do this", and that is a real and useful answer.
>
> **The tester column is already filled in.** An agent drove every case before you. Its verdict is there so
> you can check it against yours. If it says PASS and you find FAIL, that is a finding about our testing,
> and one of the most valuable things you can give us. Nothing overwrites your verdict or the tester's.

**App URL:** `http://127.0.0.1:8731/` (running on this computer since 2026-10-10 13:17, started by the orchestrator)
**Starting state:** an empty Streaks page, "No habits yet." Nothing is saved yet in this browser for that address.
**Roughly how long:** 7 cases, about 15 minutes. A desktop browser is fine. Narrow the window to see the phone layout if you like.

---

## Cases

### UAT-01: I can add a habit by name
**Scope:** C1 Add a habit · **Ledger status:** SHIPPED

**Problem.** You asked for a habit list you build yourself. A name goes in, the habit joins the list, and
the list refuses a name it already has instead of making a second copy.

**Preconditions.** The empty first screen. It reads "No habits yet." and "Add one you want to do every day."

**Steps.**
1. Click the text field under "New habit".
2. Type `Read 20 pages`.
3. Click the green **Add** button to the right of the field.
4. Click the text field again, then type `Stretch 10 minutes` in it. (After a click on Add, the keyboard stays on
   the Add button, so typing straight away would press Add again.)
5. Press **Enter**.
6. Type `read 20 pages` (all lower case) in the field.
7. Press **Enter**.

**Expected result.** After step 3, "Read 20 pages" appears with a row of 7 hollow circles (the last 7 days,
today on the right with a thin ring around it) and the line "No streak yet". After step 5, "Stretch 10
minutes" appears under it. After step 7, no third habit appears. Red text under the field reads "You
already track this habit." and your typed text stays in the field. That message and the red border stay
until your next add, through the next cases. That is expected, not a stuck error.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| BLOCKED (script) as first written: step 4 had no click on the field, so the first space pressed Add. With the click added (the step as it reads now), steps 4 to 7 matched. Fixed before handover | "Pass, not sure why its blocked by tester but it was good" (2026-10-10) | none. The BLOCKED was the first draft of this script, fixed before you got it (findings.md UAT-F1) |

---

### UAT-02: I can tick and untick the days of this week
**Scope:** C2 Tick the week · **Ledger status:** SHIPPED

**Problem.** You asked to tick off a habit for today and for the last few days if you forgot, and to undo a
tick made by mistake.

**Preconditions.** UAT-01 done: two habits, nothing ticked. Clear the field first (select its text and delete it).

**Steps.**
1. On "Read 20 pages", click the rightmost circle (today, the one with the thin outer ring).
2. On "Read 20 pages", click the circle just left of it (yesterday).
3. On "Read 20 pages", click the rightmost circle again.
4. On "Read 20 pages", click the rightmost circle once more.

**Expected result.** After step 1, today's circle fills green with a white check. After step 2, yesterday
fills too and a thick green line joins the two filled circles. After step 3, today goes back to a hollow
circle. After step 4, it is filled again and joined to yesterday.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: today filled with a white check, yesterday filled and joined by a 4 px green line, step 3 hollow, step 4 filled and joined again | "Pass . I like the design for this week what we have done but a big limitation is that we cant input something that we did last week or change a specific date habit incase we input it wrong or want to add something we just remembered. Think about it and if its a good idea then implement it. If not report to me why. Also, we can have a continous streak for something we do for weeks also. LIke, read 20 pages, i read everydya. Then next week also everyday, it should be a continous streak." (2026-10-10) | Past days: In 1.1.0, your yes on 2026-10-10 (findings.md UAT-F2). Streak across weeks: already works, proof in findings.md UAT-F3 |

---

### UAT-03: The streak counts days in a row and does not break before today is over
**Scope:** C3 Current streak · **Ledger status:** SHIPPED

**Problem.** You asked to see how many days in a row a habit has been done, counted so that not having
ticked today yet does not wipe the streak while today is still going.

**Preconditions.** UAT-02 done: "Read 20 pages" has yesterday and today ticked.

**Steps.**
1. Read the line under "Read 20 pages".
2. Click today's circle on "Read 20 pages" to untick it.
3. Read the line under "Read 20 pages" again.
4. Click today's circle again to tick it.

**Expected result.** At step 1 the line reads "2 days" in green, then "Best 2" in grey. At step 3 it reads
"1 day" (yesterday still counts, because today is not over), and a dashed green line runs from yesterday
into today's open circle. "Best" reads 1 at that moment, because the best streak is worked out from the days
ticked now. After step 4 it reads "2 days" and "Best 2" again with a solid line.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: "2 days" and "Best 2", then "1 day" with a dashed line into today's open circle, then "2 days" with a solid line | "Pass. I think it needs to show that left side is current and right is best" (2026-10-10) | In 1.1.0, your yes on 2026-10-10 (findings.md UAT-F4) |

---

### UAT-04: The best streak remembers the longest run
**Scope:** C4 Best streak · **Ledger status:** SHIPPED

**Problem.** You asked to see the longest run a habit has had, next to the current one, so a good run earlier
in its history still shows when today's run is shorter. It is worked out from the days that are ticked, so
unticking a day can lower it.

**Preconditions.** UAT-03 done. "Stretch 10 minutes" has nothing ticked.

**Steps.**
1. On "Stretch 10 minutes", click the 2nd circle from the left.
2. Click the 3rd circle from the left.
3. Click the 4th circle from the left.
4. Click the rightmost circle (today).
5. Read the line under "Stretch 10 minutes".

**Expected result.** The line reads "1 day" (only today, because yesterday is not ticked) and then "Best 3"
(the three days in a row from steps 1 to 3). The three filled circles are joined by one thick line. Today is
filled but not joined to them.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: "1 day" then "Best 3", one thick line joins circles 2 to 4, today filled and not joined | "Pass" (2026-10-10) | none |

---

### UAT-05: The heatmap shows how much of each day got done
**Scope:** C5 12-week heatmap · **Ledger status:** SHIPPED

**Problem.** You asked for one picture of the last 12 weeks for all habits together, darker on days when
more of them were done.

**Preconditions.** UAT-04 done. Both habits have today ticked. Find the panel "Last 12 weeks" (on a wide
window it is on the right, on a narrow one it is below "New habit"). Today's dot has a thin ring around it.

**Steps.**
1. Look at today's ringed dot in the heatmap.
2. Untick today's circle on "Stretch 10 minutes".
3. Look at today's ringed dot again.
4. Tick today's circle on "Stretch 10 minutes" again.

**Expected result.** At step 1 today's dot is the largest, darkest kind, the same as "All" at the right end
of the legend under the grid. At step 3 it is smaller and lighter (half the habits done). After step 4 it is
the largest again. Days after today have no dot at all.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: today's dot 17 px darkest (same as "All"), 11 px lighter at step 3 (the middle legend dot), 17 px again at step 4, the day after today has no dot | "Pass" (2026-10-10) | none |

---

### UAT-06: I can delete a habit, but only on purpose
**Scope:** C6 Delete a habit · **Ledger status:** SHIPPED (one accepted limit, below)

**Problem.** You asked to remove a habit with its history, after a confirmation, so one slip cannot delete
it. To stop a quick double click from opening the question and answering it in the same gesture, two short
safety pauses were added. They are new to you, so this case asks you to judge them.

**Preconditions.** UAT-05 done. Two habits.

**Steps.**
1. Click the bin icon at the right of "Stretch 10 minutes".
2. Read the question that opens.
3. Click **Cancel**.
4. Click the bin icon at the right of "Stretch 10 minutes" again.
5. Wait one second.
6. Click **Delete habit**.

**Expected result.** At step 2 a box in the middle of the page asks `Delete "Stretch 10 minutes"?` with "Its
history is deleted too." under it, and two buttons, **Cancel** and **Delete habit**. After step 3 the box
closes and both habits are still there. After step 6 "Stretch 10 minutes" is gone and "Read 20 pages" is
unchanged. The heatmap now counts one habit: today's dot stays the largest kind, the dots of days where only
"Stretch 10 minutes" was ticked go hollow, and yesterday's dot grows to the largest kind.

**You are being asked to rule on this.** "Delete habit" ignores clicks for the first half second after the
box opens, and right after you press anywhere in the box, a click on the page behind is ignored for half a
second. If you click the bin within half a second of pressing Cancel, nothing happens. Can you live with
that? Options: keep it for 1.0 (our recommendation, it is what stops the accidental delete) / change it now.
Separately, a slow double click (more than half a second apart) on the bin can still go through to "Delete
habit". That is fixed in 1.1.0 with a guard that does not depend on time.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: the box asked the question with both buttons, Cancel kept both habits, after a one second wait Delete habit removed only "Stretch 10 minutes", today reads 1 of 1 habits. Extra: a bin click right after Cancel and a Delete habit click 250 ms after opening were both ignored | "Pass" (2026-10-10) | Pauses kept. Your words: "very minor, i think just keep it unless its an easy change (fast meaning a few lines only). Barely noticebly by a human." The 1.1.0 time-free guard replaces the Delete habit pause anyway |

---

### UAT-07: My habits are still there when I come back
**Scope:** C7 Kept on the device · **Ledger status:** SHIPPED

**Problem.** You asked for everything to stay on this device with no account, so a reload or a closed tab
loses nothing.

**Preconditions.** UAT-06 done. One habit, "Read 20 pages", with yesterday and today ticked.

**Steps.**
1. Press **F5** to reload the page.
2. Close the browser tab.
3. Open a new tab and go to the app address again.

**Expected result.** After step 1 and after step 3 the page shows "Read 20 pages" with the same filled
circles, "2 days" and "Best 2", and the same heatmap.

| tester (pre-run) | YOUR verdict | next step (agreed with you) |
|---|---|---|
| PASS: after a reload, and after closing the tab and opening a new one, the circles, "2 days", "Best 2" and all 84 heatmap cells were the same | "Pass" (2026-10-10) | none |

---

## Verdict summary

| case | scope | tester | you | next step |
|---|---|---|---|---|
| UAT-01 | C1 Add a habit | BLOCKED (script), fixed, then steps matched | PASS | see the case |
| UAT-02 | C2 Tick the week | PASS | PASS | see the case |
| UAT-03 | C3 Current streak | PASS | PASS | see the case |
| UAT-04 | C4 Best streak | PASS | PASS | none |
| UAT-05 | C5 12-week heatmap | PASS | PASS | none |
| UAT-06 | C6 Delete a habit | PASS | PASS | none |
| UAT-07 | C7 Kept on the device | PASS | PASS | none |

The tester's PASS shows the script can be run. It is not the proof that the feature works. That is your verdict.
Pre-run evidence: `pre-run/20261010-132500/` (the driver, 122 checks, a screenshot per case).

**Legend.** `PASS` it does what the case says · `FAIL` it does not · `BLOCKED` you could not run it. Say
which: the control was not where the script said, the starting state was unreachable, or the result was not
something you could see.

---

# (a) OPEN: needs your decision

> Every fork we could not settle ourselves. Each one is a decision you make, not a status line. Read from
> `CHANGE-LEDGER.md`, Needs the human. Deferrals are listed too, because a deferral is a decision we made
> on your behalf, and you can overturn it.

### H-01: The choices made while you delegated the run
- **What it is.** You handed this run over ("Auto create with lifecycles for 2 projects"). Every product and
  design choice inside it was made for you: a habit tracker rather than a plain todo list, the "Quiet beads"
  look, the clarify-gate answers, the planner's calls.
- **Why it needs you.** Requirements and design are yours to decide. An agent may only propose them.
- **Options.** Accept them as they are · reopen any one of them (it then becomes work for a later version).
- **Recommendation.** Skim `docs/design-explore/round-1/compare.html` (the three looks side by side) and
  `docs/design/RULINGS.md`. Those carry the most taste. Everything else is in the ledger.
- **Your ruling (2026-10-10).** "Yes but not fully as i have given comments about it. For both app, they both are functioning fluidly which is very good. But design wise for both is not that good. For streaks, the missing previous dates is actually a big thing. Overall , its good but not superbly."

### D-01: The limits we accepted for 1.0 on your behalf
- **What it is.** Each was found during this version and kept on purpose.
  - A slow double click on the bin can still delete. **Planned for 1.1.0.**
  - The half-second safety pauses in the delete box (UAT-06 asks you about them).
  - If the browser blocks or fills its storage, changes stay on screen but are not saved, with no message.
  - Another page on the same `github.io` address can read the saved names, because that host gives every
    project one shared address.
  - Two open tabs do not see each other's changes. The last one to save wins.
  - A name made of many stacked accent marks draws over its neighbours.
  - With the computer's clock set to the year 10000 or later, the next load resets every habit.
  - Only Chrome's engine (Chromium) was tested. Safari and Firefox were not.
- **Why it needs you.** Deferring is a decision we made for you.
- **Options.** Keep each as a known limit · move any one into 1.1.0.
- **Recommendation.** Keep them. 1.1.0 already takes the one a person is likely to meet (the slow double click).
- **Your ruling (2026-10-10).** "If its the same as split, then no need. If its something that really requires my attention then sure." So Split's rulings apply to the items the two apps share: the silent failed save and the Safari engine go into 1.1.0, the shared github.io address and two tabs stay. The slow double click was already planned for 1.1.0. The two Streaks-only items (stacked accent marks, a clock set past the year 9999) are minor and stay as known limits.

### D-02: The app's name
- **What it is.** A well-known iPhone habit tracker is also called "Streaks".
- **Why it needs you.** The name of a public showcase piece is yours to choose.
- **Options.** Keep "Streaks" (it is a portfolio example, not a product) · rename it before publishing.
- **Recommendation.** Keep it, and say "example app" wherever it is shown. Renaming touches the approved
  design and every document.
- **Your ruling (2026-10-10).** "Streaky Habit". Then, after the name check: "Check if its ok to be used. Also, for split, change it to SplitIO. Also, if both names cant be used, then add Danials [app name] Or if theres a better way to make it uniquely to me." Neither name is free (findings.md D-02), so the name is chosen with you in the 1.1.0 design round.

---

# (b) SOLVED: in plain language

### A quick double click could delete a habit by accident
- **The problem.** The bin and the "Delete habit" button sit where a fast double click can hit both, so one
  gesture could open the question and answer yes.
- **What I did.** "Delete habit" ignores clicks for half a second after the box opens, and a click on the
  page right after a press in the box is ignored for half a second too.
- **Why this and not the others.** Moving the button would change the approved design, which an agent may not
  do. A guard that does not depend on time is better, and it is planned for 1.1.0, where it can go through the
  design step properly.

### A habit name could scramble the delete question
- **The problem.** Hidden text-direction characters typed into a name could reorder the words of the delete
  question, so it could read as if it named a different habit.
- **What I did.** The question shows the name fenced off from the words around it, with those hidden
  characters left out of that one copy. The saved name is exactly what you typed.
- **Why this and not the others.** The other option was to refuse names that hold those characters when you
  type them. That changes which names the app accepts, a product rule that is yours to set, and it would have
  reopened the finished logic part of the app. Changing only the question's copy closes the problem without
  touching your data or your rules.

### Damaged saved data
- **The problem.** If what the browser saved cannot be read, the page could fail or show nonsense.
- **What I did.** The page treats the saved text as untrusted. Anything it cannot read starts an empty list and
  shows a note saying the list was reset, which you can dismiss.
- **Why this and not the others.** Trying to repair half-read data could show you habits you never made. Your
  brainstorm asked for exactly this note.

### A damaged save could freeze the page while counting a streak
- **The problem.** A crafted save with odd dates could make the streak count run for a very long time.
- **What I did.** The counting skips anything that is not a real date, so it always finishes quickly.
- **Why this and not the others.** The loader already rejects such a save. The counting got its own guard too,
  so a future change to the loader cannot bring the freeze back.

### The version number
- **The problem.** The run started as 0.1.0.
- **What I did.** Renamed it 1.0.0 after you said "Make sure both app reach a stable 1.0 version."
- **Why this and not the others.** It is your label to set. Nothing else changed with it.

---

## Residuals you should know about, that are not cases

- The page turning over to the new day at midnight while left open is **not in your script** (it needs
  midnight). The tester checked it with a controlled clock: at 23:59:40 plus 60 seconds the strip, the header
  date and the heatmap all moved to the next day. The review drive checked it too.
- The 12-habit limit and the name length rules are not in your script. The review drive checked them.
- Safari and Firefox are **NOT RUN**. Only Chromium was tested.
