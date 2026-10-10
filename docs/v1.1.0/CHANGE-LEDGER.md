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
| S1 | Edit any past day | OPEN | USER | 0 |
| S2 | The streak line says which is Current and which is Best | OPEN | USER | 0 |
| S3 | A delete guard that does not depend on time | OPEN | USER | 0 |
| S4 | Habits that cannot be saved say so | OPEN | USER | 0 |
| S5 | Tested in Safari's engine too | OPEN | USER | 0 |
| S6 | The logo in the app | OPEN | USER | 0 |
| S7 | A livelier look, chosen from five directions | OPEN | USER | 0 |
| S8 | A name that is free to use | OPEN | USER | 1 |

---

## Scope sections

### S1 - Edit any past day
**Status:** OPEN · **Opened:** 2026-10-10 · **Tag:** USER
**Source:** UAT-02 and UAT-F2, owner: "a big limitation is that we cant input something that we did last week or change a specific date habit incase we input it wrong or want to add something we just remembered." Then: "For streaks, the missing previous dates is actually a big thing." Approved for 1.1.0: "3.  Yes."

The user can open an older day and tick or untick its habits, to fix a mistake or add something remembered late. Reverses the v1.0.0 non-goal "Editing days older than the last 7" (an ORCH call).

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the owner's UAT request | 2026-10-10 seal | Brainstorm delta (how far back, days before a habit existed, how the day is opened), design, plan to follow | USER | Open |

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

---

## Needs the human

### H-01 - The name (S8)
- **What:** "Streaky" and "Streaky Habit" are taken in spirit by three habit trackers. His fallback is his own name with the app name ("Danial's Streaks") or another way to make it his.
- **Why an agent cannot decide it:** the name of his public showcase piece is his.
- **Options:** decided in the design round, beside the wordmark.
- **Ruling:** (pending)

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `OPEN` · `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
