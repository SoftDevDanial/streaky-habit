# CHANGE LEDGER - v0.1.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** (round, fix batch, module, live
> gate, finder loop, decision, deferral) · corrections are **additive and dated**, never a silent
> rewrite · **staleness check** at every phase boundary: newest dated entry here vs newest file in
> `./docs/progress/handoff/`. Handoff newer means this file is stale.

**Version:** v0.1.0 · **Opened:** 2026-10-08 by `sdlc:plan` · **Sealed:** not yet (see `SEAL.md` once sealed)

> **This run was delegated.** The owner asked for the whole lifecycle to be created ("Auto create with
> lifecycles for 2 projects", 2026-10-08). Every decision an agent or the orchestrator took in his place is
> tagged **ORCH** and is reversible. The human UAT verdicts and the seal are his alone.

## At a glance

| scope | title | status | tag | open items |
|---|---|---|---|---|
| C1 | Add a habit | NOT SHIPPED | IN SCOPE | 0 |
| C2 | Tick the week | NOT SHIPPED | IN SCOPE | 0 |
| C3 | Current streak | NOT SHIPPED | IN SCOPE | 0 |
| C4 | Best streak | NOT SHIPPED | IN SCOPE | 0 |
| C5 | 12-week heatmap | NOT SHIPPED | IN SCOPE | 0 |
| C6 | Delete a habit | NOT SHIPPED | IN SCOPE | 0 |
| C7 | Kept on the device | NOT SHIPPED | IN SCOPE | 0 |

---

## Scope sections

### C1 - Add a habit
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R13, R14 · app R10, R11, R12
**Proof:** not yet (set at the module's live gate and at regression)

Name a habit and it joins the list (1 to 40 characters, unique, up to 12).

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C2 - Tick the week
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R5, R9 · app R7, R8
**Proof:** not yet (set at the module's live gate and at regression)

Each habit shows the last 7 days and a tap marks a day done or not done.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C3 - Current streak
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R6 · app R6, R8
**Proof:** not yet (set at the module's live gate and at regression)

Days in a row, counted so the streak does not break until today is over.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C4 - Best streak
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R7 · app R6
**Proof:** not yet (set at the module's live gate and at regression)

The longest run the habit has ever had.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C5 - 12-week heatmap
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R10, R11, R12 · app R9
**Proof:** not yet (set at the module's live gate and at regression)

One grid for all habits, darker when more habits were done that day.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C6 - Delete a habit
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** habit-logic R15 · app R13, R14, R15
**Proof:** not yet (set at the module's live gate and at regression)

Removes the habit and its history after a confirmation.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

### C7 - Kept on the device
**Status:** NOT SHIPPED · **Opened:** 2026-10-08 · **Closed:** not yet · **Tag:** IN SCOPE
**Implemented by:** app R16, R17, R18 (and local days R19, R20)
**Proof:** not yet (set at the module's live gate and at regression)

Habits and history survive reloads on the same browser, and the day turns over at local midnight.

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | Scope opened from the brainstorm capability | 2026-10-08 plan | Specced | ORCH (planner lane) | Open |

---

## Clarify-gate rulings (plan, 2026-10-08)

| # | Question | Ruling | Who | Outcome |
|---|---|---|---|---|
| CG-1 | Broken unit test command | Fixed in CLAUDE.md (see Off-scope 4) | ORCH | Ruled 2026-10-08, reversible |
| CG-2 | How fidelity reaches S1 and M1 | Plugin harness 2.1.1+ flags; seed and after-load scripts stay test-side | ORCH | Ruled 2026-10-08, reversible |
| CG-3 | Native `::backdrop` differences | Add the `var(--scrim, rgb(28 37 35 / 0.5))` fallback and `::backdrop` to the reduced-motion rule | ORCH | Ruled 2026-10-08, reversible |
| CG-4 | What counts as unreadable saved data | Strict schema for anything that would lose data, harmless oddities repaired, empty state saved at once after a reset | ORCH | Ruled 2026-10-08, reversible |
| CG-5 | Storage blocked or a save fails | Keep working in memory, never crash. Accepted residual: changes are lost on reload without a warning | ORCH | Ruled 2026-10-08, reversible |
| CG-6 | What does a backdrop click do? | Acts as Cancel, including focus return; matches the design flow check and Split | ORCH | Ruled 2026-10-08, reversible |
| CG-7 | Focus when the focused control disappears | Dismiss moves focus to "New habit"; at the 12th add focus stays and the note is announced | ORCH | Ruled 2026-10-08, reversible |
| CG-8 | What "40 characters" counts | Unicode code points | ORCH | Ruled 2026-10-08, reversible |
| CG-9 | Two open tabs | No sync, last save wins. Accepted residual | ORCH | Ruled 2026-10-08, reversible |

---

## Off-scope and new

| # | Problem found | When | What changed | Who | Outcome |
|---|---|---|---|---|---|
| 1 | The plugin fidelity harness could only load a URL, so an app with saved data, a date or a dialog could not reach a golden's state without a test hook in the app | 2026-10-08 plan | sdlc 2.1.0 adds `--candidate-init-script`, `--candidate-after-load`, `--fixed-time`, `--browser-arg`. Control: seeded candidate 0.0%, unseeded 5.1% | ORCH (plugin) | Solved in the plugin |
| 2 | The harness freeze script was an uninvoked arrow function, so `Date.now` and `Math.random` were never pinned (measured) | 2026-10-08 plan | sdlc 2.1.1 invokes it and pins time through Playwright's clock. Verified 0.0% self-diff on a page that prints the time | ORCH (plugin) | Solved in the plugin |
| 3 | A strict CSP (`style-src 'self'`) crashed the harness, which had pushed the Split plan to loosen its own policy | 2026-10-08 plan | sdlc 2.1.2 renders with `bypass_csp`; QA and the live gate still enforce the policy. Control: 2.1.1 crashed, 2.1.2 0.0% | ORCH (plugin) | Solved in the plugin |
| 4 | `node --test tests/` in CLAUDE.md exits 1 on Node 24.11.1 (measured by the planner) | 2026-10-08 plan | CLAUDE.md now uses `node --test "tests/**/*.test.js"` and adds `python -m pytest tests/browser -q` | ORCH | Solved |
| 5 | Plan coverage gate (sdlc-plan-checker) | 2026-10-08 plan | PASS, 0 block, 7 flag. All 44 R# tested, 103 design elements with checklist rows | LANE (sdlc-plan-checker) | Solved |
| 6 | 7 FLAGs: icon template option, seeding order in open_app, @R27 request rule, @R19 clock race, @R16 comment scan, S2-01 position, harness version history | 2026-10-08 plan | Fixed as ruled, each old statement kept with a dated note (PLAN-CHECK.md, FLAG fixes) | LANE (sdlc-planner, sonnet) | Solved |
| 7 | The browser itself requests /favicon.ico and a static server answers 404, which Chromium logs as a console error. Tests require a clean console | 2026-10-08 plan | Ruling: tests ignore exactly that one message (a 404 for /favicon.ico). The app does not ship a favicon (not in the brainstorm or goldens) | ORCH | Ruled, reversible |

---

## Needs the human

### H-01 - Review the decisions taken under delegation
- **Why an agent cannot decide it:** requirement and design choices belong to the owner. He delegated
  them for this run, so each one is recorded and reversible.
- **Where they are:** the brainstorm grill log (`docs/brainstorm/brainstorm.md`), the design picks
  (`docs/design-explore/round-1/DECISION.md`), the design rulings (`docs/design/RULINGS.md`), the
  clarify-gate rulings above, and the planner decisions in `docs/modules/ROADMAP.md`.
- **Recommendation:** read the two compare pages and the rulings first. They carry the most taste.
- **Ruling:** (pending)

---

## Field reference

| field | values | why |
|---|---|---|
| Status | `SHIPPED` · `PARTIAL` · `NOT SHIPPED` | Whether the scope actually landed, as a field, not prose. |
| Tag | `IN SCOPE` · `ORCH` · `USER` · `DEFERRED` | Who owns the decision. `ORCH` items are reversible; the human may overturn any of them. |
| Proof | measurement + where it lives | Without it, "Solved" is a claim. |
| Who | `USER` · `ORCH` · `LANE` (+ which agent) · `IN SCOPE` | Who authored the change. |
| Outcome | `Solved` · `PARTIAL` · `DEFERRED → vX.Y.Z` · `WITHDRAWN` · `NEEDS THE HUMAN` | `WITHDRAWN` keeps a wrong finding visible, so the record never reads cleaner than reality. |
