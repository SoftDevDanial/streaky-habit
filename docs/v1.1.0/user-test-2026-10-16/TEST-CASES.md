# UAT, Danial's Streaky Habit 1.1.0

> **Sitting 1 of 2.** Cases derived **one per scope section** of `./docs/v1.1.0/CHANGE-LEDGER.md`. S5 has five,
> because its own ruling (S5 row 2) asks for "a few cases he runs on his own iPhone". Each of those walks one
> other scope's claim again in Safari. Sitting 1 is UAT-01 to UAT-07 at your desk. Sitting 2 is UAT-08 to
> UAT-12 on your iPhone.
> Written from the requester's seat. *"I asked for X. Is X there, does it look right, can I use it?"*
>
> **This file is the record.** You work from `TEST-SHEET.html` beside it, which holds the same cases. Your
> marks, verdicts and notes come back through the sheet's "Results for the chat" and are written here word
> for word, with the date.

**App URL.** Sitting 1, `http://127.0.0.1:8741/` on this PC, started for you by the orchestrator. Sitting 2, the orchestrator gives you the address for your iPhone when you start this sitting.
**Starting state.** Nothing saved for this address in Chrome. The header shows the amber mark, "Streaky Habit", and "Friday 16 October" at the right. Under it the band "Last 12 weeks" with a **Year** button and "Tap a day to change it.", and a grid of numbered thin grey rings from Monday 27 July to Friday 16 October. Today, 16, has a white outer circle, and the places for Saturday 17 and Sunday 18 are empty. The band's legend reads "None", one ring, "All". The list box reads "No habits yet." and "Add one you want to do every day." beside a dotted orbit. At the bottom sit "New habit", an empty field and an amber **Add**.
**Roughly how long.** 12 cases. Sitting 1 about 45 minutes, sitting 2 about 35 minutes.

**Before you begin.**
- Use Chrome for sitting 1. UAT-05 and UAT-07 use Chrome's own settings.
- Keep the Chrome window at least 1024 px wide. A maximised window is fine. Narrower than that, the app switches to its phone layout and sitting 1 no longer matches.
- Every date assumes you test on Friday 16 October 2026. On another day the dates move with today, so tell the orchestrator first and it dates the sheet again.
- Work the cases in order. Each one starts where the last one ended.
- Reading a ring. A day's ring has one arc per habit in list order, clockwise from 12 o'clock. With three habits the first habit is the arc between 12 and 4 o'clock, the second between 4 and 8, the third between 8 and 12. Done is a thick amber arc, not done a thin grey one. When every habit is done the middle fills amber and the number turns dark. Today has a white outer circle.
- Tester. The automated UAT pre-run agent ran every case before you on 16 October 2026, sitting 1 in headless Chromium at 1280 x 800, sitting 2 in headless WebKit, Safari's engine on Windows, at 390 x 664 and 390 x 844. It is not an iPhone and has no Chrome or Safari interface, so each tester note names the lines only you can check. A green tester row proves the script can be run, not that the feature works.
- Status. Every scope still reads OPEN in the ledger. SHIPPED is written at the seal, so OPEN here means built and reviewed, waiting for your verdict.

## Verdict guide

| Verdict | What it means | Example from this version |
|---|---|---|
| **PASS** | Every line you checked matches the sheet, or a cross you marked does not matter to you. | **UAT-02, step 7.** The No phone after 11pm row read Current 1 day and Best 2, exactly as listed. |
| **FAIL** | A line does not match and it matters. The line gets a cross and the note says what you saw. | **UAT-09, step 2.** The 27 July day sat half under the day editor, where the sheet says the whole day shows above it. |
| **BLOCKED** | You could not run it. The note says why. The control was not where the sheet said, the start could not be reached, or the result was not something you could see. | **UAT-07, step 2.** Chrome's page has no line "Not allowed to save data on your device", so the address could not be blocked. |
| **NOTE** | Any verdict can carry a note. A note on a PASS becomes a finding for a later version. | **UAT-08.** "Pass, but I want no white ring after a tap" becomes your ruling on open item A1 (H-07). |

There are only three verdicts. The sheet itself shows two states that nobody chooses. **NOT RUN** means no
verdict yet, and the case comes back at the next sitting. **RETEST** means it failed, was fixed, and is
handed back, with the first verdict kept beside the new one.

**Line marks.** Every line under *You should see* gets a tick (it matches) or a cross (it does not). A case
can PASS with a cross when you decide the difference does not matter. The cross stays on record.

---

## Cases

### UAT-01

**I can open any past day and fix it, three ways**

| | |
|---|---|
| **Scope** | S1 Edit any past day · OPEN, built · sitting 1 |
| **Problem** | In 1.0 you could tick only the last 7 days. Your words at the 1.0 test, "a big limitation is that we cant input something that we did last week or change a specific date habit incase we input it wrong or want to add something we just remembered." 1.1.0 lets you open any day of the last 12 months and tick or untick it, three ways that you ruled in the design round. A day in the band opens the day editor. A habit's Year opens that habit's year. The band's Year opens every habit's year, and a day there opens the day editor too. Days after today stay closed. The phone part, where a low day stays in sight above the day editor, is UAT-09. |
| **Before you start** | The starting state above. Add three habits first. Click the **New habit** field at the bottom, type `Read 20 pages` and press Enter. Type `Stretch 10 minutes` and press Enter. Type `No phone after 11pm` and press Enter. The list then holds those three rows in that order, each reading "Current" and "No streak yet" with no Best. |

| # | Do this | You should see |
|---|---|---|
| 1 | In the band, click **15** in the last column, fourth row (the T for Thursday). | The day editor opens in the middle of the window over the dimmed page<br>Its title reads "Thursday 15 October"<br>The line under the title reads "0 of 3 habits"<br>The ring at its top left has three thin grey arcs and no number<br>Three rows with an empty circle each, "Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"<br>Under each of the three names it reads "No streak yet"<br>A **Close** x sits at its top right<br>In the band behind it, 15 is outlined in amber |
| 2 | Click the empty circle beside "Read 20 pages". | The circle fills amber with a dark check<br>Under Read 20 pages it reads "Current 1 day" in amber<br>Beside that it reads "Best 1"<br>The line under the title reads "1 of 3 habits"<br>The ring at the top left shows one thick amber arc between 12 and 4 o'clock |
| 3 | Click **Close**, the x at the top right of the day editor. | The day editor closes<br>In the band, 15 shows one thick amber arc between 12 and 4 o'clock<br>On the Read 20 pages row, under "Current" it reads 1 in amber, then "day"<br>It shows "Best" with 1 under it |
| 4 | On the Stretch 10 minutes row, click **Year**. | A large window opens titled "Stretch 10 minutes"<br>Under the title it reads "The last 12 months"<br>It shows "Current" with "No streak yet" under it<br>There is no Best<br>**Delete habit** with a bin sits at the right<br>It reads "Tap a day to mark it done or not done."<br>A legend shows an amber dot "Done" and an empty circle "Not done"<br>The top row holds three months, "October 2026", "September 2026", "August 2026"<br>In October 2026, 1 to 16 are circled numbers<br>16 has a white ring round it (today)<br>17 to 31 October 2026 are dim numbers with no circle |
| 5 | Point at this window and scroll down until it stops. | The last month is "October 2025", alone at the left of the bottom row<br>1 to 15 October 2025 are blank, with no number<br>16 to 31 October 2025 are circled numbers<br>16 sits under the T for Thursday |
| 6 | Click **16** in October 2025. | 16 fills amber<br>"Current" still reads "No streak yet"<br>"Best" appears with 1 under it |
| 7 | Click **17** in October 2025, next to it. | 17 fills amber<br>A short amber thread joins 16 and 17<br>"Best" reads 2<br>"Current" still reads "No streak yet" |
| 8 | Click **17** again. | 17 is an empty circle again<br>The thread is gone<br>"Best" reads 1 |
| 9 | Click **Close**, the x at the top right of the window. | The window closes<br>The Stretch 10 minutes row shows "Current" with "No streak yet" under it<br>It shows "Best" with 1 under it |
| 10 | In the band, click **Year**, beside "Last 12 weeks". | A large window opens titled "All habits"<br>Under the title it reads "The last 12 months"<br>It reads "Tap a day to change it."<br>A legend at the right reads "None", four small rings, "All"<br>The top row holds three months, October 2026 first<br>15 October 2026 shows one thick amber arc between 12 and 4 o'clock<br>16 October 2026 has a white outer circle and no amber<br>17 to 31 October 2026 are dim numbers with no ring |
| 11 | Point at this window and scroll down until it stops. | The last month is "October 2025"<br>1 to 15 October 2025 are blank<br>16 October 2025 shows one thick amber arc between 4 and 8 o'clock |
| 12 | Click **16** in October 2025. | The day editor opens over the year window<br>Its title reads "Thursday 16 October"<br>The line under the title reads "1 of 3 habits"<br>Read 20 pages has an empty circle, then "Current 1 day" and "Best 1"<br>Stretch 10 minutes has an amber circle with a check, then "No streak yet" and "Best 1"<br>No phone after 11pm has an empty circle, then "No streak yet" |
| 13 | Click the empty circle beside "No phone after 11pm". | The circle fills amber with a dark check<br>Under No phone after 11pm it reads "No streak yet", then "Best 1"<br>The line under the title reads "2 of 3 habits" |
| 14 | Press **Esc**. | The day editor closes and the year window stays open<br>16 October 2025 shows two thick amber arcs, between 4 and 8 and between 8 and 12 o'clock |
| 15 | Press **Esc**. | The year window closes<br>The No phone after 11pm row shows "Current" with "No streak yet" under it<br>It shows "Best" with 1 under it |
| **Note** | Days after today are closed on purpose, so they have no ring and no circle. The day editor's title carries no year, so 16 October 2025 reads "Thursday 16 October". Current and Best in the day editor are each habit's numbers today, not as of the chosen day. Current counts yesterday's run while today is not over, which is why step 3 reads 1 day. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in Chromium at 1280 x 800, on the re-run after step 3 was reworded. Nothing here was out of its reach. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-02

**Each streak line names Current and Best**

| | |
|---|---|
| **Scope** | S2 The streak line says which is Current and which is Best · OPEN, built · sitting 1 |
| **Problem** | At the 1.0 test you said "I think it needs to show that left side is current and right is best". Every streak line now carries the labels Current and Best, on the row, in the day editor and in a habit's year. This case makes the two numbers differ, so the labels matter. |
| **Before you start** | UAT-01 done. Read 20 pages reads Current 1 day and Best 1. Stretch 10 minutes and No phone after 11pm each read Current with "No streak yet", and Best 1. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the Read 20 pages row. | A small label "Current" sits above its first number<br>Under "Current" it reads 1 in amber, then "day"<br>A small label "Best" sits to the right<br>Under "Best" it reads 1 in white |
| 2 | Look at the Stretch 10 minutes row. | It shows "Current" with "No streak yet" under it<br>It shows "Best" with 1 under it |
| 3 | On the No phone after 11pm row, click **Year**. | A large window opens titled "No phone after 11pm"<br>It shows "Current" with "No streak yet" under it<br>It shows "Best" with 1 under it |
| 4 | In October 2026, click **13**. | 13 fills amber<br>"Best" still reads 1<br>"Current" still reads "No streak yet" |
| 5 | Click **14**, next to it. | 14 fills amber<br>A short amber thread joins 13 and 14<br>"Best" reads 2<br>"Current" still reads "No streak yet" |
| 6 | Click **Close**, the x at the top right of the window. | The window closes<br>The No phone after 11pm row shows "Current" with "No streak yet" under it<br>It shows "Best" with 2 under it |
| 7 | On the No phone after 11pm row, click **Done today**. | Done today turns amber with a dark check<br>"Current" reads 1 in amber, then "day"<br>"Best" reads 2<br>In the band, 16 shows one thick amber arc between 8 and 12 o'clock |
| 8 | In the band, click **16**, the last column, fifth row (the F for Friday). | The day editor opens, titled "Friday 16 October"<br>The line under the title reads "1 of 3 habits"<br>Read 20 pages has an empty circle, then "Current 1 day" and "Best 1"<br>Stretch 10 minutes has an empty circle, then "No streak yet" and "Best 1"<br>No phone after 11pm has an amber circle with a check, then "Current 1 day" and "Best 2" |
| 9 | Click **Close**, the x at the top right of the day editor. | The day editor closes<br>The Read 20 pages row shows "Current" 1 "day" and "Best" 1<br>The No phone after 11pm row shows "Current" 1 "day" and "Best" 2 |
| **Note** | Best is worked out from the days ticked as they are now. When Current is 0 the row says "No streak yet". When Best is 0 there is no Best at all, as on a new habit. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in Chromium at 1280 x 800. Nothing here was out of its reach. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-03

**The new amber look, and a list that scrolls inside its box while the add field stays put**

| | |
|---|---|
| **Scope** | S7 A livelier look, chosen from five directions · OPEN, built · sitting 1 |
| **Problem** | You found 1.0 "so dull" and asked for five directions. You picked Orbit Rings' look with a layout of your own (F2 "Orbit List"). In Round 1 you said the list scrolls inside its own box, "Not the page but the div only", and that many habits must not push the input field down. This case looks at the main screen and fills it to twelve habits. You saw the popups in UAT-01 and UAT-02. The phone look is UAT-08. |
| **Before you start** | UAT-02 done. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the header. | The page background is near black<br>An amber mark sits at the top left<br>"Streaky Habit" sits beside it in white bold<br>"Friday 16 October" sits in grey at the right end of the same line |
| 2 | Look at the band. | It sits in a rounded box under the header<br>"Last 12 weeks" sits at its top left, with a **Year** button beside it<br>"Tap a day to change it." sits under the title<br>M T W T F S S run down the left of the grid<br>Jul, Aug, Sep and Oct sit above the grid<br>Each day is a ring of three thin grey arcs with its number in the middle<br>13 and 14 October show one thick amber arc between 8 and 12 o'clock<br>15 October shows one thick amber arc between 12 and 4 o'clock<br>16 October shows one thick amber arc between 8 and 12 o'clock and a white outer circle<br>The places for 17 and 18 October are empty<br>The legend at the bottom left reads "None", four small rings, "All" |
| 3 | Look at the list and the bottom of the window. | Three rows sit in one rounded box under the band<br>Each row is one line, the name, a bin, Current, Best, **Year**, **Done today**<br>Done today on No phone after 11pm is amber with a dark check<br>Done today on the other two is outlined, with an empty circle<br>The New habit box sits at the bottom of the window<br>Its label "New habit" sits left of the field<br>An amber **Add** sits at the right of the field |
| 4 | On the Read 20 pages row, click **Done today**. | Done today turns amber with a dark check<br>"Current" reads 2, then "days"<br>"Best" reads 2<br>In the band, 16 shows thick amber arcs between 12 and 4 and between 8 and 12 o'clock |
| 5 | On the Stretch 10 minutes row, click **Done today**. | Done today turns amber with a dark check<br>"Current" reads 1, then "day"<br>"Best" reads 1<br>In the band, all three arcs of 16 are thick amber<br>The middle of 16 fills amber and its number turns dark |
| 6 | Click the **New habit** field, type `Habit 4` and press Enter. | A fourth row "Habit 4" appears under No phone after 11pm<br>It shows "Current" with "No streak yet" and no Best<br>The field is empty again<br>Every ring in the band now has four arcs<br>The middle of 16 is no longer filled |
| 7 | In the same way, add `Habit 5`, `Habit 6`, `Habit 7`, `Habit 8`, `Habit 9`, `Habit 10`, `Habit 11` and `Habit 12`, pressing Enter after each. | "Habit 12" is the last row in view<br>The list box reaches down to the New habit box, and the rows scroll inside it<br>The top edge of the list box fades over the row under it<br>The New habit box is still at the bottom of the window, where it was at step 3<br>The note above the field reads "You track 12 habits, the most this app holds. Delete one to add another."<br>The field and **Add** are greyed out<br>The header and the band have not moved |
| 8 | Point at the list and scroll the mouse wheel up until it stops. | The rows move inside the list box<br>"Read 20 pages" is the top row again<br>The bottom edge of the list box now fades over the row above it<br>The header, the band and the New habit box stay where they are |
| 9 | Point at the band and scroll the mouse wheel down. | Nothing on the page moves |
| **Note** | The list scrolling inside its box and the add field staying put are your own Round 1 ruling. The note and the grey field at twelve habits are the app's limit of twelve habits. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in Chromium at 1280 x 800. The list scrolled inside its box while the header, the band and the New habit box stayed put. Nothing here was out of its reach. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-04

**A double click on a bin never deletes, and Delete habit acts at once**

| | |
|---|---|
| **Scope** | S3 A delete guard that does not depend on time · OPEN, built · sitting 1 |
| **Problem** | In 1.0, Delete habit ignored clicks for half a second after the dialog opened. A slower second click could still delete where the bin lay under Delete habit, and a quick deliberate click had to wait. You chose to fix the 1.0 limits. Now a click on the spot of the button that opened the dialog, and the second click of any double click, are ignored, a key press always works, and there is no timer. The tap version on your iPhone is UAT-10. |
| **Before you start** | UAT-03 done, twelve habits. Point at the list and scroll down until it stops, so Habit 12 is the last row in view. |

| # | Do this | You should see |
|---|---|---|
| 1 | On the Habit 12 row, click the bin once, wait about one second, then click the same spot again without moving the mouse. | The first click opens a dialog titled Delete "Habit 12"? |
| 2 | Press **Esc**. | No dialog is open<br>Habit 12 is still the last row<br>The note "You track 12 habits, the most this app holds. Delete one to add another." still shows above the field |
| 3 | On the Habit 12 row, double-click the bin quickly. | A dialog flashes open and closes again at once<br>No dialog is open afterwards |
| 4 | Press **Esc**. | Nothing changes, since no dialog is open<br>Habit 12 is still the last row<br>The twelve-habit note still shows above the field |
| 5 | On the Habit 12 row, click **Year**. | A large window opens titled "Habit 12"<br>It shows "Current" with "No streak yet" under it<br>**Delete habit** with a bin sits at its right |
| 6 | Double-click **Delete habit** quickly. | No delete dialog is open<br>The Habit 12 window is still open |
| 7 | Click **Close**, the x at the top right of the Habit 12 window. | The window closes<br>Habit 12 is still the last row<br>The twelve-habit note still shows above the field |
| 8 | On the Habit 12 row, click the bin once. | A dialog opens in the middle of the window<br>Its title reads Delete "Habit 12"?<br>Under it, "Its history is deleted too."<br>**Cancel** sits on the left, outlined<br>**Delete habit** sits on the right, in red |
| 9 | Straight away, click the word "habit" on the red **Delete habit** button. | The dialog closes at once<br>Habit 12 is gone<br>Habit 11 is the last row<br>The twelve-habit note is gone<br>The New habit field and **Add** can be used again, and Add is amber |
| **Note** | Whether the second click of step 1 lands on Delete habit or on the dim page beside the dialog depends on your window's height. Either way it must delete nothing, which step 2 checks. In steps 3 and 6 the second click lands on the dim page around the dialog, which closes it like Cancel and deletes nothing. So in step 3 the dialog only flashes, and step 4's Esc then does nothing. Step 9 names the word "habit" because a click on the exact spot of the bin you clicked first is ignored on purpose, and on some window heights the left end of Delete habit lies over that bin. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched in Chromium at 1280 x 800 on the re-run. The quick double click's dialog showed for about 140 ms and closed, Esc then changed nothing, and nothing was deleted. Delete habit acted at once. Its first run was blocked by the old step 3 wording, fixed before you got it. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-05

**The logo in the header and on the browser tab, in light and dark**

| | |
|---|---|
| **Scope** | S6 The logo in the app · OPEN, built · sitting 1 |
| **Problem** | At the 1.0 seal you asked "Wheres the logo. I dont see it being used for both". The mark you approved now shows in the header and as the tab icon. The icon is a bright amber on a dark tab and a darker amber on a light one. Safari shows one colour in both modes, a Safari bug you accepted, which UAT-12 looks at on your iPhone. A home-screen icon is not built in 1.1.0. |
| **Before you start** | UAT-04 done, in Chrome. Windows is in dark mode (Settings, Personalization, Colors, Choose your mode, Dark). Chrome follows Windows, which is its default. This PC has no Firefox, so steps 5 and 7 are for Firefox only. Skip them, mark each of their lines with a cross, write "no Firefox" in your note and go on. Those crosses alone do not fail the case. |

| # | Do this | You should see |
|---|---|---|
| 1 | Look at the header. | An amber mark sits left of "Streaky Habit"<br>The mark holds no letter and no initial |
| 2 | Look at the app's tab at the top of Chrome. | The tab shows the same mark as the header<br>The mark on the tab is bright amber |
| 3 | Switch Windows to light mode (Settings, Personalization, Colors, Choose your mode, Light). | Windows and Chrome turn light<br>The app's page stays dark, it has one dark look |
| 4 | Click the app's tab in Chrome and press **F5**. | The tab icon is now a darker amber<br>The mark is easy to see on the light tab |
| 5 | Firefox only, skip it without Firefox. Open Firefox and go to `http://127.0.0.1:8741/`. | Firefox shows the first screen with "No habits yet.", since each browser keeps its own habits<br>The Firefox tab shows the same mark in the darker amber |
| 6 | Switch Windows back to dark mode. | Windows and Chrome turn dark |
| 7 | Firefox only, skip it without Firefox. In Firefox, press **F5**. | The Firefox tab icon is bright amber again |
| 8 | Click the app's tab in Chrome and press **F5**. | The Chrome tab icon is bright amber again |
| **Note** | Without Firefox, steps 5 and 7 take a cross on each line and "no Firefox" in your note, as the start of this case says. Steps 6 and 8 are for everyone, since UAT-06 needs Windows dark and Chrome on the app's tab. Safari on a Mac is not asked for here, see the residuals. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. It could check 3 of 13 lines and all 3 match, the amber mark with no letter and the page staying dark under a light preference. It has no browser tab, no Windows mode switch and no Firefox, so only you can check steps 2, 4, 6 and 8, step 3 line 1, and the Firefox steps 5 and 7. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-06

**The full name on the tab, the short name in the header**

| | |
|---|---|
| **Scope** | S8 A name that is free to use · OPEN, built · sitting 1 |
| **Problem** | The name check found "Streaky" used by three habit trackers. You ruled "Danial's Splity Tab and Danial's Streaky Habit. Logo wise, dont need danial or even initial D." The full name is the page title, the header shows Streaky Habit, and the mark carries no name and no initial. The README header still shows the 1.0 name until the seal, see open item A3. |
| **Before you start** | UAT-05 done. Back in Chrome on the app's tab, Windows in dark mode. |

| # | Do this | You should see |
|---|---|---|
| 1 | Point at the app's tab in Chrome and wait a moment. | A card under the tab shows the name "Danial's Streaky Habit" |
| 2 | Look at the header. | It reads "Streaky Habit", without "Danial's"<br>The mark beside it holds no D and no initial |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | The header and the mark matched. It has no tab hover card, so only you can check step 1. The page title does read Danial's Streaky Habit. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-07

**When the browser will not save, the app says so**

| | |
|---|---|
| **Scope** | S4 Habits that cannot be saved say so · OPEN, built · sitting 1 |
| **Problem** | In 1.0, when the browser blocked or filled its storage, changes were lost with no message. Now a warning shows while saving fails, also from the first screen when the browser blocks storage outright, and it goes once saving works. Here you block storage for this address in Chrome. Private browsing and Safari's 7-day clean-up cannot show the warning, because the browser reports every save as working. That is a known limit in the README. |
| **Before you start** | UAT-06 done. Chrome on the app with eleven habits, Read 20 pages first and Habit 11 last. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open a new Chrome tab, type `chrome://settings/content/siteData` in the address bar and press **Enter**. | The settings page "On-device site data" opens |
| 2 | Under "Customized behaviors", click **Add** beside "Not allowed to save data on your device". | A small box "Add a site" opens with a "Site" field |
| 3 | Type `http://127.0.0.1:8741` and click **Add**. | "http://127.0.0.1:8741" is listed under "Not allowed to save data on your device" |
| 4 | Click the app's tab and press **F5**. | A box with an amber edge sits between the band and the list<br>It reads "Your habits are not being saved on this device. Changes will be lost when you close this tab."<br>It has no close button<br>The list reads "No habits yet.", since the app cannot read what it saved<br>Every ring in the band is one thin grey circle |
| 5 | Click the **New habit** field, type `Water` and press Enter. | A row "Water" appears with "Current" and "No streak yet"<br>The warning is still there |
| 6 | On the Water row, click **Done today**. | Done today turns amber with a dark check<br>"Current" reads 1, then "day"<br>"Best" reads 1<br>The warning is still there |
| 7 | Go back to the settings tab, click the three dots beside "http://127.0.0.1:8741" and click **Remove**. | "http://127.0.0.1:8741" is no longer listed |
| 8 | Click the app's tab and press **F5**. | No warning shows<br>Eleven habits are back, Read 20 pages first and Habit 11 last<br>Read 20 pages shows "Current" 2 "days" and "Best" 2<br>Water is not in the list |
| **Note** | Reload at step 8 before you change anything. Once the block is gone, a change in the page that was still open saves that page's list, which holds only Water, over your eleven saved habits, see open item H-08. If the eleven habits do not come back at step 8, Chrome dropped the address's saved data when you blocked it. Mark that line with a cross and say so in your note. Chrome may spell "Customized behaviors" the British way. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched. It cannot open Chrome's settings pages, so only you can check steps 1, 2, 3 and 7. A stand-in blocked and freed storage in their place, so it could not see whether Chrome keeps the saved habits during a block. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-08

**Every screen on your iPhone, and the white ring after a tap**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, every screen on your iPhone · OPEN, built · sitting 2 |
| **Problem** | Every iPhone browser runs Safari's engine, and 1.0 was tested only in Chrome's. The automated runs now cover Safari's engine too, but not a real iPhone, its touch, its on-screen keyboard or its settings. Your ruling for S5 asked for a few cases on your own iPhone, UAT-08 to UAT-12. This one looks at each screen. It also holds open item A1 (H-07), which only your eyes can rule on. |
| **Before you start** | Sitting 2 starts here, on your iPhone in Safari. The orchestrator gives you the address for your iPhone when you start this sitting. Use a normal tab, never a Private one. Block All Cookies (Settings, Apps, Safari) is off. Light or dark mode does not matter, the app has one dark look. Nothing is saved for that address on the iPhone, so the app opens on its first screen. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open the address in Safari. | The amber mark and "Streaky Habit" sit at the top left<br>An **Overview** button with one thin empty ring sits at the top right<br>"Friday 16 October" sits on its own line under them<br>A box reads "No habits yet." and "Add one you want to do every day." beside a dotted orbit<br>The New habit box sits at the bottom of the screen<br>"New habit" sits above the field, with an amber **Add** at the field's right |
| 2 | Tap the **New habit** field. | The keyboard opens<br>The New habit field is visible above the keyboard<br>**Add** is visible beside the field |
| 3 | Type `Read 20 pages` and tap the return key at the bottom right of the keyboard. | A row "Read 20 pages" appears<br>Its bin sits at the row's top right<br>Its second line shows "Current" with "No streak yet", then **Year** and **Done today**<br>The field is empty again |
| 4 | Tap the field, type `Stretch 10 minutes` and tap the return key. | A row "Stretch 10 minutes" appears under Read 20 pages |
| 5 | Tap the field, type `No phone after 11pm` and tap the return key. | A row "No phone after 11pm" appears under Stretch 10 minutes |
| 6 | Tap **Done** above the keyboard. | The keyboard closes<br>The New habit box is back at the bottom of the screen |
| 7 | On the Read 20 pages row, tap **Done today**. | Done today turns amber with a dark check<br>"Current" reads 1, then "day"<br>"Best" reads 1<br>The ring on the Overview button shows one thick amber arc between 12 and 4 o'clock |
| 8 | Tap **Overview**. | A full-screen sheet opens titled "Last 12 weeks"<br>"Tap a day to change it." sits under the title<br>**Year** and **Close** (an x) sit at its top right<br>M T W T F S S run across the top of the grid<br>The newest week is the top row, 12 to 16, then two empty places<br>Down the left, "Oct" twice, "Sep" and "Aug" label rows<br>16 has a white outer circle and one thick amber arc between 12 and 4 o'clock<br>A thin white ring is drawn round Close, see the note |
| 9 | Tap **15** in the top row. | The day editor rises from the bottom<br>Its title reads "Thursday 15 October"<br>The line under the title reads "0 of 3 habits"<br>Read 20 pages reads "Current 1 day" and "Best 1"<br>Stretch 10 minutes reads "No streak yet"<br>No phone after 11pm reads "No streak yet"<br>15 is outlined in amber above the day editor<br>A thin white ring is drawn round the Read 20 pages row, see the note |
| 10 | Tap the empty circle beside "Read 20 pages". | The circle fills amber with a dark check<br>Under Read 20 pages it reads "Current 2 days" and "Best 2"<br>The line under the title reads "1 of 3 habits" |
| 11 | Tap **Close**, the x at the top right of the day editor. | The day editor goes down and the sheet shows again<br>15 shows one thick amber arc between 12 and 4 o'clock |
| 12 | Scroll the sheet down until it stops (swipe up on the grid). | The bottom row is 27, 28, 29, 30, 31, 1, 2, labelled "Jul"<br>The legend under the grid reads "None", four small rings, "All" |
| 13 | Tap **Year** at the top right of the sheet. | A full-screen sheet opens titled "All habits"<br>Under the title it reads "The last 12 months"<br>It reads "Tap a day to change it."<br>The legend reads "None", four small rings, "All"<br>One month per row, "October 2026" first<br>15 and 16 October 2026 each show one thick amber arc between 12 and 4 o'clock<br>17 to 31 October 2026 are dim numbers with no ring<br>A thin white ring is drawn round Close, see the note |
| 14 | Tap **Close** on All habits. | The Last 12 weeks sheet shows again |
| 15 | Tap **Close** on Last 12 weeks. | The list shows again with its three rows |
| 16 | On the Read 20 pages row, tap **Year**. | A full-screen sheet opens titled "Read 20 pages"<br>Under the title it reads "The last 12 months"<br>It shows "Current" with 2 in amber and "days"<br>It shows "Best" with 2<br>**Delete habit** with a bin sits at the right<br>It reads "Tap a day to mark it done or not done."<br>A legend shows "Done" and "Not done"<br>One month per row, "October 2026" first<br>15 and 16 are amber and joined by a short amber thread<br>16 has a white ring round it (today)<br>A thin white ring is drawn round Close, see the note |
| 17 | Tap **Close**. | The list shows again |
| 18 | On the No phone after 11pm row, tap the bin. | A dialog opens in the middle of the screen<br>Its title reads Delete "No phone after 11pm"?<br>Under it, "Its history is deleted too."<br>**Cancel** sits on the left and a red **Delete habit** on the right<br>A thin white ring is drawn round Cancel, see the note |
| 19 | Tap **Cancel**. | The dialog closes<br>No phone after 11pm is still in the list |
| **Note** | **You are being asked to rule on this (open item A1, H-07).** In Safari's engine a popup opened by a tap draws the white keyboard ring on the control the app focuses first, Close in the sheets, the first habit in the day editor, Cancel in the delete dialog. The design and Chrome draw none. A keyboard user gets the same ring on purpose. Option 1, keep it, a line in the test notes, nothing to build. Option 2, remove it, which goes back to the plan or the design because it changes how focus is set. We recommend option 1, it is Safari's own rule and it helps a keyboard user. Write your choice in your note. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by the script at 390 x 664, on step 8 line 6 only. The Jul label was below the screen edge there. That line was reworded after the run in the tester's own words and not run again. Every other line it could drive matched at 390 x 664, and every one matched at 390 x 844. It has no on-screen keyboard, so only you can check step 2 and step 6. The white rings of A1 showed round Close, the first habit and Cancel, as listed. It ran Safari's engine on Windows, not an iPhone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-09

**On the phone, a low day and last year's oldest day stay in sight above the day editor**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S1 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | On a phone the overview's twelve weeks fill the screen, so a day in the lower weeks hid under the day editor, and so did last year's oldest days. You ruled "Fix, give P3 room" and "Same fix for P4". While the day editor is open, the sheet under it gets room at its bottom and scrolls so the chosen day sits above the editor. With nine or more habits only part of the day can show, see open item A4. This case uses three habits. |
| **Before you start** | UAT-08 done. The list holds Read 20 pages, Stretch 10 minutes and No phone after 11pm. Read 20 pages reads Current 2 days and Best 2. |

| # | Do this | You should see |
|---|---|---|
| 1 | Tap **Overview**. | The Last 12 weeks sheet opens<br>Its bottom row, at the foot of the sheet (scroll down if it is cut off), is 27 July to 2 August, labelled "Jul" |
| 2 | Tap **27** in the bottom row, the part that shows is enough. | The day editor rises from the bottom<br>Its title reads "Monday 27 July"<br>The line under the title reads "0 of 3 habits"<br>27 is outlined in amber<br>The whole of 27 shows between the sheet's title area and the top of the day editor |
| 3 | Tap the empty circle beside "Stretch 10 minutes". | The circle fills amber with a dark check<br>Under Stretch 10 minutes it reads "No streak yet", then "Best 1"<br>The line under the title reads "1 of 3 habits"<br>27 above shows one thick amber arc between 4 and 8 o'clock |
| 4 | Tap **Close**, the x at the top right of the day editor. | The day editor goes down<br>27 July is still in view<br>On a screen tall enough for the whole grid the top row, 12 to 16 October, shows too, otherwise scroll up to see it<br>27 July shows one thick amber arc between 4 and 8 o'clock |
| 5 | Tap **Year** at the top right of the sheet. | The All habits sheet opens, "October 2026" first |
| 6 | Scroll down inside All habits until it stops. | The last month is "October 2025"<br>1 to 15 October 2025 are blank<br>16 sits under the T for Thursday |
| 7 | Tap **16** in October 2025. | The day editor rises from the bottom<br>Its title reads "Thursday 16 October"<br>The line under the title reads "0 of 3 habits"<br>16 is outlined in amber<br>The whole of 16 shows above the top of the day editor |
| 8 | Tap the empty circle beside "No phone after 11pm". | The circle fills amber with a dark check<br>Under No phone after 11pm it reads "No streak yet", then "Best 1"<br>The line under the title reads "1 of 3 habits" |
| 9 | Tap **Close**, the x at the top right of the day editor. | The day editor goes down<br>16 October 2025 shows one thick amber arc between 8 and 12 o'clock |
| 10 | Tap **Close** on All habits. | The Last 12 weeks sheet shows again |
| 11 | Tap **Close** on Last 12 weeks. | The Stretch 10 minutes row shows "Current" with "No streak yet" and "Best" with 1<br>The No phone after 11pm row shows "Current" with "No streak yet" and "Best" with 1 |
| **Note** | The room under the day editor exists only while it is open, so the sheet looks as designed the rest of the time. The white rings of UAT-08 show here too, they are part of your ruling on A1. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched at 390 x 664 and at 390 x 844 on the re-run, in Safari's engine on Windows. At 390 x 664 steps 1 and 4 needed the scrolls their lines allow. 27 July and 16 October 2025 each showed whole above the day editor. Only you can check it on a real iPhone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-10

**On the phone, double taps on a bin or on Delete habit delete nothing**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S3 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The delete guard of UAT-04 has to hold for taps too, and Safari's engine counts a quick second tap differently from Chrome's. The second tap of a double tap may land on Delete habit, where it is ignored, or on the dim page beside the dialog, which closes it like Cancel. Either way nothing is deleted. A deliberate tap on Delete habit acts at once. |
| **Before you start** | UAT-09 done, three habits. |

| # | Do this | You should see |
|---|---|---|
| 1 | On the Stretch 10 minutes row, double-tap the bin quickly. | The first tap opens the delete dialog for Stretch 10 minutes, which may close again at once if the second tap lands on the dim page |
| 2 | Tap the date line, "Friday 16 October", under the name. | No dialog is open<br>Stretch 10 minutes is still in the list<br>The list still holds three habits |
| 3 | On the Stretch 10 minutes row, tap the bin once, wait about one second, then tap the same spot again. | The first tap opens a dialog titled Delete "Stretch 10 minutes"? |
| 4 | Tap the date line, "Friday 16 October". | No dialog is open<br>Stretch 10 minutes is still in the list |
| 5 | On the Stretch 10 minutes row, tap **Year**. | A full-screen sheet opens titled "Stretch 10 minutes"<br>**Delete habit** with a bin sits at the right of its numbers |
| 6 | Double-tap **Delete habit** quickly. | No delete dialog is open<br>The Stretch 10 minutes sheet is still open |
| 7 | Tap **Delete habit** once. | A dialog opens titled Delete "Stretch 10 minutes"?<br>Under it, "Its history is deleted too."<br>**Cancel** sits on the left and a red **Delete habit** on the right |
| 8 | Straight away, tap **Delete habit** in the dialog. | The dialog and the Stretch 10 minutes sheet close at once<br>Stretch 10 minutes is gone<br>The list holds Read 20 pages and No phone after 11pm |
| **Note** | A tap on the date line closes the dialog if it is still open, and does nothing if it is not, so steps 2 and 4 end the same way whatever the second tap did. If Safari zooms in on a double tap, pinch the page back to its normal size before the next step. The zoom is Safari's own. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line matched at 390 x 664 and at 390 x 844 on the re-run. Each quick double tap's dialog closed again on the dim page after about 140 ms, and nothing was deleted. Its taps are clicks in Safari's engine on Windows, so how real fingers land is yours to check. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-11

**With Block All Cookies on, the app warns that nothing is saved**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S4 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The save warning of UAT-07, in Safari on your iPhone, with the setting that blocks storage there. A Private tab cannot show the warning, a known limit, so this case never uses one. |
| **Before you start** | UAT-10 done. The list holds Read 20 pages and No phone after 11pm. |

| # | Do this | You should see |
|---|---|---|
| 1 | Open the Settings app, then Apps, then Safari, and turn on **Block All Cookies**. | The Block All Cookies switch is on |
| 2 | Go back to Safari, tap the address bar and tap **Go** on the keyboard. | The page loads again<br>A box with an amber edge sits under the date line<br>It reads "Your habits are not being saved on this device. Changes will be lost when you close this tab."<br>It has no close button<br>The list reads "No habits yet."<br>The ring on the Overview button is one thin empty circle |
| 3 | Tap the **New habit** field, type `Water` and tap the return key. | A row "Water" appears with "Current" and "No streak yet"<br>The warning is still there |
| 4 | Tap **Done** above the keyboard. | The keyboard closes |
| 5 | On the Water row, tap **Done today**. | Done today turns amber with a dark check<br>"Current" reads 1, then "day"<br>"Best" reads 1<br>The warning is still there |
| 6 | In Settings, Apps, Safari, turn off **Block All Cookies**. | The Block All Cookies switch is off |
| 7 | Go back to Safari, tap the address bar and tap **Go**. | No warning shows<br>Read 20 pages and No phone after 11pm are back<br>Read 20 pages shows "Current" 2 "days" and "Best" 2<br>Water is not in the list |
| **Note** | If iOS asks you to confirm at step 1, confirm the block. Reload at step 7 before you change anything. Once the block is gone, a change in the page that was still open saves its list, which holds only Water, over your saved habits, see open item H-08. If the two habits do not come back at step 7, Safari dropped the saved data when you blocked it. Mark that line with a cross and say so in your note. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | PASS | Every line it could drive matched. It has no iOS Settings and no on-screen keyboard, so only you can check steps 1, 4 and 6. A stand-in blocked and freed storage in place of Block All Cookies, so it could not see what Safari's own setting does to the saved habits. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

### UAT-12

**The tab icon in Safari in light and dark, and what the home screen shows**

| | |
|---|---|
| **Scope** | S5 Tested in Safari's engine too, with S6 on your iPhone · OPEN, built · sitting 2 |
| **Problem** | The tab icon of UAT-05, in Safari on your iPhone. Safari 26 ignores the light and dark switch inside an icon, a Safari bug you accepted for 1.1.0, so the mark is expected in one colour in both modes, most likely the darker amber. A home-screen icon is not built in 1.1.0. The last steps only record what iOS draws from the tab icon, as information for a later version. |
| **Before you start** | UAT-11 done, Safari on the app. The iPhone is in dark mode (Settings, Display and Brightness, Dark). |

| # | Do this | You should see |
|---|---|---|
| 1 | Tap the tabs button at the bottom right of Safari. | The tab overview opens<br>The app's tab shows the mark beside "Danial's Streaky Habit"<br>The mark is the darker amber, not the bright amber of Chrome's dark tab |
| 2 | Open Settings, then Display and Brightness, and choose **Light**. | The iPhone turns light |
| 3 | Go back to Safari's tab overview. | The mark is the same darker amber as at step 1<br>The mark is easy to see on the light tab |
| 4 | Tap the app's tab. | The app shows again |
| 5 | Open Safari's Share menu and tap **Add to Home Screen**. | A panel shows the name "Danial's Streaky Habit" or a shortened form of it<br>An icon sits beside the name |
| 6 | Tap **Add**. | A new icon for the app sits on your home screen |
| **Note** | Information only from step 5. Describe in your note what iOS drew. A home-screen icon needs a filled tile, which goes against your no-tile ruling, so it waits for a later logo round. You can remove the new icon afterwards. Switch the iPhone back to the mode you use. | |

| | Verdict | Note |
|---|---|---|
| **Tester** (an AI agent, before you) | BLOCKED | Blocked by its seat, not the app. Every line needs Safari's tab overview, iOS Settings, the Share menu or the home screen, so the whole case is yours alone. |
| **You** | | |
| **Your marks** | | |
| **Next step** (written by the AI agent, agreed with you) | | |

---

## Verdict summary

| case | sitting | scope | T tester | U user | crosses | next step |
|---|---|---|---|---|---|---|
| UAT-01 | 1 | S1 | PASS | | | |
| UAT-02 | 1 | S2 | PASS | | | |
| UAT-03 | 1 | S7 | PASS | | | |
| UAT-04 | 1 | S3 | PASS | | | |
| UAT-05 | 1 | S6 | BLOCKED (seat) | | | |
| UAT-06 | 1 | S8 | PASS | | | |
| UAT-07 | 1 | S4 | PASS | | | |
| UAT-08 | 2 | S5 | BLOCKED (script, step 8 line 6, reworded, not run again) | | | |
| UAT-09 | 2 | S5 with S1 | PASS | | | |
| UAT-10 | 2 | S5 with S3 | PASS | | | |
| UAT-11 | 2 | S5 with S4 | PASS | | | |
| UAT-12 | 2 | S5 with S6 | BLOCKED (seat) | | | |

---

# (a) OPEN. Needs your decision

> Every fork we could not settle ourselves. Each one is a **decision you make**, not a status line.
> Read from `CHANGE-LEDGER.md` §Needs the human and the orchestrator's own rulings. **Deferrals are listed
> too.** A deferral is a decision we made on your behalf, so you can overturn it.

### A1. The white ring after a tap in Safari (H-07)

| | |
|---|---|
| **What it is** | In Safari's engine every popup opened by a tap or a click draws the white keyboard focus ring on the control the app focuses first. That is Close in the three sheets, the first habit in the day editor and Cancel in the delete dialog. The design and Chrome draw none. Opened with the keyboard, both draw it, as designed. You see it in UAT-08. |
| **Why it needs you** | It is a visible difference from the approved design on your iPhone, and removing it changes how focus is set or changes the design. It went unseen because the pixel match runs in Chrome's engine only, your ruling for S5. |
| **Options** | (1) Keep it. A line in the test notes and the ledger, nothing to build. (2) Remove it. Back to the plan, which would tell Safari the focus is not from a keyboard against the approved focus rule, or back to the design. |
| **Recommendation** | (1). It is Safari's own rule, and the ring helps someone who uses a keyboard. For v1.2.0, a look check of the open popups in Safari's engine would catch the next difference of this kind. |
| **Your ruling** | |

### H-08. Saved habits can be overwritten when storage comes back while the page is open

| | |
|---|---|
| **What it is** | If the browser blocks storage when the page opens, the page starts with an empty list and shows the save warning. If storage is allowed again while that page is still open, the next tick or add saves the short list over every habit saved before. A reload first keeps them. It was found by reading the code while this script was written, and UAT-07 and UAT-11 reload first so it does not bite. A probe in a test browser confirmed it. Three habits were saved, storage was blocked and the page loaded again, Water was added, then storage came back and Water was ticked with no reload. Only Water was left, and the three earlier habits were gone. The probe used a stand-in that tests the app's own logic, not whether Chrome or Safari let an open page save again. |
| **Why it needs you** | It is data loss in a path the contract allows, and any fix changes what the page does after a failed start. That is a logic change, which goes back through the plan. |
| **Options** | (1) After a failed start, save nothing until a reload, so the warning stays and the old habits survive. Anything added in that page is lost, as the warning already says. (2) Before the first save after a failed start, read the saved habits again and refuse to write over any found there, with the warning kept. (3) Keep it, as a limit row in the README. |
| **Recommendation** | (1). It is the simplest rule that never loses saved habits, and the warning already says that page is not saving. Whether it is built in 1.1.0 or 1.2.0 is your call. |
| **Your ruling** | |

### A2. How your iPhone reaches the app for sitting 2 (new)

| | |
|---|---|
| **What it is** | Sitting 2 needs the app on your iPhone. The app runs on this PC at 127.0.0.1, an address only this PC can open. |
| **Why it needs you** | The first option opens a port on your home network for the length of the sitting, so it is your call. |
| **Options** | (1) The orchestrator serves the app on this PC's Wi-Fi address for sitting 2 only. Windows asks once whether to let Python through its firewall, and you answer that prompt. The server stops when the sitting ends. (2) The iPhone cases wait for the published page after the seal. |
| **Recommendation** | (1). The iPhone cases are the only check on a real phone, and they should inform the seal, not follow it. |
| **Your ruling** | |

### A3. The README header shows 1.0 until the seal (review D2)

| | |
|---|---|
| **What it is** | The README's top block, the lockup, tagline, badges, screenshot and the name Streaks, still shows 1.0. The rest of the README describes 1.1.0, and a note under the header says so. |
| **Why it needs you** | It is a deferral we made. You can overturn it. |
| **Options** | (1) Keep it, and make the header at the seal from the sealed build. (2) Update it now from this build. |
| **Recommendation** | (1), so the pictures show exactly what you seal. |
| **Your ruling** | |

### A4. Many habits on a phone, the chosen day shows only in part above the day editor (review D4)

| | |
|---|---|
| **What it is** | With nine or more habits the day editor reaches its full height, 85 percent of the screen. The day you opened can then show only in part above it, as little as 5 px of a year-view day on a small phone at twelve habits. The sheet scrolls so the top of the day meets the sheet's title area. |
| **Why it needs you** | No rule covered it, so we ruled it ourselves. It is visible. |
| **Options** | (1) Accept it for 1.1.0. (2) Ask for a design change in a later version. |
| **Recommendation** | (1). Most lists hold fewer habits, and the day stays outlined. Look at (2) for v1.2.0 if it bothers you. |
| **Your ruling** | |

### A5. Local paths in the repository before it goes public (off-scope row 20)

| | |
|---|---|
| **What it is** | Of 2,163 tracked files, 75 hold D:/ paths and 15 hold your Windows user path. None holds your email or a secret. The published page never serves them, but a public repository would show them. |
| **Why it needs you** | Your choice for publish prep, after the seals. The same check is owed for Split. |
| **Options** | (1) Scrub the records before the repository goes public. (2) Publish them as they are. |
| **Recommendation** | No strong recommendation, it is a preference call. Scrubbing hides your user folder name. Keeping them keeps the records exactly as they happened. |
| **Your ruling** | |

### A6. Smaller calls we made for you

| | |
|---|---|
| **What it is** | (a) In a desktop window narrower than 768 px a thin scrollbar shows while the day editor is open over the overview. (b) At a Monday midnight with the day editor open, the redraw can move the chosen day under the editor. (c) With the device clock in the year 10000 or later the year views show odd months or nothing, and nothing is saved or lost, after your 13-month bound. (d) Code tidy-ups wait for the v1.2.0 plan, unused fields, one guard with two names in the tests, a test constant nothing reads, and the wording "between 1 and 13 months". (e) The design notes print one colour as #2D271C where the design paints #2C261C, a rounding left to the design phase. (f) The scope statuses move to SHIPPED at the seal. (g) The records are committed at each session end. |
| **Why it needs you** | Each one is ours and reversible. |
| **Options** | Accept all, or name the ones you want changed. |
| **Recommendation** | Accept all. None changes what you see in normal use. |
| **Your ruling** | |

---

# (b) SOLVED, in plain language

> Three beats each. **No R#, no file paths, no agent names, no test counts.** Those live in the batch docs.
> The third beat matters most, because it makes a decision cheap to overturn later.

### A low day hid behind the day editor on a phone

| | |
|---|---|
| **The problem** | On a phone the overview's twelve weeks fill the screen with nothing to scroll, so a day in the lower weeks, such as late July, stayed hidden under the day editor. Last year's oldest days in the year of all habits did the same. |
| **What I did** | While the day editor is open, the sheet under it gets extra room at its bottom, as tall as the editor, and scrolls so the chosen day sits above the editor. The room goes when the editor closes. The year of all habits works the same way. |
| **Why this and not the others** | Accepting the gap would have left out of sight the very days you most need to fix. A design change was not needed, because the room hides behind the editor in the designed state. We first told you the year of all habits was fine. The planner then worked out that its oldest month had the same gap, and you ruled the same fix for it. |

### A check failed, and the app was right

| | |
|---|---|
| **The problem** | An automated check on that room failed most of the time in Chrome's engine. |
| **What I did** | The check read the page a moment before the app had tidied up after closing the editor. We fixed the check, not the app, and it then passed every time. |
| **Why this and not the others** | Changing the app to suit a mistimed check would have added a delay that helps no one. |

### Delete no longer depends on time

| | |
|---|---|
| **The problem** | In 1.0, Delete habit ignored clicks for half a second after the dialog opened. A slower second click could still delete where the bin lay under Delete habit, and a quick deliberate click had to wait. |
| **What I did** | Delete habit now ignores a click on the exact spot of the button that opened the dialog, and the second click of any double click. A key press always works. There is no timer, so a deliberate click acts at once. |
| **Why this and not the others** | A longer timer would still let a slower click through and make every deliberate click wait longer. Counting clicks alone misses a slow double click and is not proven for taps in Safari. The one cost is that a click on the part of Delete habit lying exactly over that bin does nothing. |

### Taps that fall through a popup

| | |
|---|---|
| **The problem** | A tap that closes a popup can send the second tap of the same gesture to what lies behind it, a Done today button, a day or a bin. |
| **What I did** | You kept the 1.0 half-second hold, and we extended it to every popup. For half a second after a tap inside a popup, a tap on what lies beneath is ignored. |
| **Why this and not the others** | Dropping it would let double taps act behind the popup. The cost is that a tap on Done today within half a second of closing a sheet is ignored, and a tap a moment later works. |

### A save that fails now says so

| | |
|---|---|
| **The problem** | In 1.0, if the browser blocked or filled its storage, changes were lost with no message. |
| **What I did** | A warning shows while saving fails, decided by the latest save, and from the first screen when the browser blocks storage outright. It goes after the next save that works. |
| **Why this and not the others** | A test write or a timer would add writes and delays for nothing the latest save does not already show. Private browsing and Safari's 7-day clean-up report every save as working, so no page can detect them. The README states that limit instead of claiming a detector. |

### The tab icon as its own file

| | |
|---|---|
| **The problem** | The design carried the tab icon inside the page in a form the app's security rules block. |
| **What I did** | The same icon ships as its own small file, byte for byte the design's. |
| **Why this and not the others** | Loosening the security rules for one icon would weaken them for everything else. |

### Safari's engine in every run

| | |
|---|---|
| **The problem** | 1.0 was tested only in Chrome's engine, and every iPhone browser runs Safari's. |
| **What I did** | Every behaviour test and the cold-start live check now run in both engines. The pixel match against the design stays in Chrome's engine, as you chose. |
| **Why this and not the others** | The other option was pixel matching in both engines. You chose tests and live checks. The cost showed up as the white ring of open item A1, which only a look in Safari's engine could catch. |

### Focus after dismissing the reset note at twelve habits

| | |
|---|---|
| **The problem** | With habits added up to twelve while the "could not be read" note showed, Dismiss sent keyboard focus to nothing, because the field was switched off. |
| **What I did** | Focus now goes to the page's first control in that case, the same fallback the app uses after midnight. |
| **Why this and not the others** | Naming it as a known limit would break the rule that keyboard focus never lands on nothing, and the change was small. |

### The year views and a far-future clock

| | |
|---|---|
| **The problem** | With the device clock set in October to December of the year 10000, opening a year view froze the tab and its memory kept growing. |
| **What I did** | The list of months now stops after 13, as the code already promised. The tab answers at once at those dates. |
| **Why this and not the others** | Accepting it would have left a freeze, which is worse than an error. The fix was small and easy to test. Odd but harmless year views at such dates remain, see A6. |

### A fixer skipped the design guidance

| | |
|---|---|
| **The problem** | A fixer changed interface code without first loading the design guidance the rules require. |
| **What I did** | You accepted it. Nothing visible had changed, and the later pixel match found every screen equal to its design. Every later brief that touches the interface names the guidance. |
| **Why this and not the others** | A review pass for edits that only moved code and comments would have cost a round for no visible gain. |

### The old green page during the build

| | |
|---|---|
| **The problem** | You saw the 1.0 green and white page in the app's browser pane mid-build and stopped everything. |
| **What I did** | We checked the new design files against the archive, all equal, and showed you renders. The page you saw was a planned test of the unchanged 1.0 app, run before the rewrite. |
| **Why this and not the others** | That baseline proved the old checks held in Safari's engine before anything changed. We now warn you before such a run. |

---

## Residuals you should know about, that are not cases

- Private browsing and Safari's 7-day clean-up lose every habit with no warning. The browser reports nothing the page could show. The README says so.
- Safari shows the tab icon in one colour in both modes. Safari's bug, accepted for 1.1.0, seen in UAT-12.
- No home-screen icon in 1.1.0. It needs a filled tile, against your no-tile ruling. Deferred to a later logo round.
- Two open tabs do not see each other's changes, and the last save wins.
- Another page on the same github.io address can read the saved names.
- A name made of many combining marks draws over its neighbours.
- Firefox is not covered by the automated runs. UAT-05 looks at its tab icon only.
- Safari on a Mac is NOT RUN. The plan lists it for the tab icon, and no case asks for it because this sheet does not assume you have a Mac. Say so if you have one.
- The app left open past midnight is NOT RUN as a case. The automated runs and the review check it.
- A tap on Done today within half a second of closing a popup with a tap is ignored on purpose, see (b).
