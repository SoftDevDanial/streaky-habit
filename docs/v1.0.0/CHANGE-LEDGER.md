# CHANGE LEDGER - v1.0.0

> The version's ONE attribution record and the human's only complete view of what happened.
> `STATE.md` is *situation*, handoffs are *resume points*, `findings/` are *evidence*. **None of them is
> the record.** `sdlc:uat` derives its cases from the **scope sections** below and its handover from
> **Needs the human**, so an item that is not here never reaches the human.
>
> **Rules (constitution, The CHANGE LEDGER):** updated at **every close** (round, fix batch, module, live
> gate, finder loop, decision, deferral) · corrections are **additive and dated**, never a silent
> rewrite · **staleness check** at every phase boundary: newest dated entry here vs newest file in
> `./docs/progress/handoff/`. Handoff newer means this file is stale.

**Version:** v1.0.0 · **Opened:** 2026-10-08 by `sdlc:plan` as ~~v0.1.0~~ · **Relabelled:** 2026-10-09 to
v1.0.0 on the owner's word (see Off-scope, the USER row of that date). Same version, same scope. Plan-phase
documents written before that date still say v0.1.0. · **Sealed:** not yet (see `SEAL.md` once sealed)

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
| 8 | The habit-logic builder appended one test block with a shell heredoc to an in-project path, against the constitution's heredoc rule (the builder reported it itself) | 2026-10-09 execute | Payload had no backslashes; the next test run confirmed the content. Later edits used the Edit and Write tools | LANE (sdlc-backend-dev) | No damage. Recorded as a process breach |
| 9 | habit-logic code review round 1: PASS, 0 blocker, 10 warning (a locale test that cannot fail on Windows, a frozen-input check that misses Date setters, three false comments, heatmap week logic coupled to the strip width, doc drift) | 2026-10-09 execute | Routed to sdlc-dev-solver. WR-04 ruled: add weekdayIndex(key) to the dates.js Contracts so the strip width and days-per-week stop sharing a constant | LANE (sdlc-code-reviewer) found, ORCH ruled WR-04 | Open, solver running |
| 10 | habit-logic code review round 1, all 10 warnings | 2026-10-09 execute | Fixed in 9 commits (73fb59b to da6586f). weekdayIndex added per the WR-04 ruling; locale and Date-mutation tests now proven able to fail with mutants; false comments corrected. 61 tests pass, every commit green alone | LANE (sdlc-dev-solver) | Solved, pending the code-review re-check |
| 11 | Agents fell back to shell writes because their definitions lacked the tool: sdlc-plan-checker had no Write (it must write PLAN-CHECK.md), sdlc-planner had no Edit (it fixes specs after a BLOCK) | 2026-10-09 execute | sdlc 2.1.3 adds Write to the plan-checker and Edit to the planner | ORCH (plugin) | Solved in the plugin, applies to agents spawned in a new session |
| 12 | habit-logic security audit: FAIL issues_found, 0 critical, 0 high, 3 MEDIUM. All 7 threat-model mitigations present and held under hostile input (prototype pollution, input mutation, hostile date keys, limits, no outside reach) | 2026-10-09 execute | findings/security.md. Evidence `qa/security/20261009T115752/` | LANE (sdlc-security-auditor) | Routed to sdlc-security-solver |
| 13 | SEC-01 `runLength` could loop forever on keys outside the valid range, so a bad saved key would hang the tab on every load (blocked today by the app decoder) | 2026-10-09 execute | Loop bounded by the size of the day set. Commit `add5043`. 0 differences on 81,706 valid cases against the old code | LANE (sdlc-security-solver) | Solved, security re-check pending |
| 14 | SEC-02 `validateName` copied the whole name into an array to count it (+161 MiB heap for a 5M-unit CJK name) | 2026-10-09 execute | Private `longerThan` stops at the 41st code point. Commit `e83acb4`. 0 differences on 51,202 cases | LANE (sdlc-security-solver) | Solved, security re-check pending |
| 15 | SEC-03 the R16 purity scan missed `new Date` without parentheses, `Date()` and every network or storage call (3 planted mutants stayed green) | 2026-10-09 execute | Two named pattern tables in `tests/purity.test.js`, red on all 26 mutants, no false hits. Commit `3750d67`, comment corrections `eb2003b`. Suite 61 to 64, all pass | LANE (sdlc-security-solver) | Solved, security re-check pending |
| 16 | habit-logic security re-check: SEC-02 and SEC-03 CLOSED. SEC-01 REOPENED, the bound stops one walk but `bestStreak` starts a walk per run start, and white-space spellings of one far-out key make it O(n^2) (4,000 keys 8 s, 20,000 over 60 s). SEC-04 NEW, the clock scan misses `Temporal.Now` | 2026-10-09 execute | Re-check section in findings/security.md, evidence `qa/security/20261009T124854/`, commit `3457432` | LANE (sdlc-security-auditor) | Routed to sdlc-security-solver round 2 |
| 17 | How to close SEC-01 for good | 2026-10-09 execute | Ruled: filter `done` through `isDateKey` before any walk, keep the size bound as a second guard. SEC-04 also bans `eval` and `Function(` so a clock read cannot hide in a built string | ORCH | Ruled, reversible |
| 18 | habit-logic code-review re-check: PASS, 0 blocker, 6 warning (WR-11 comment stripper hides code after `//` or `/*` inside strings; WR-12 R6 and R7 silent on the isDateKey filter; WR-13 raw invisible characters in a test constant; WR-14 Date check misses a partial mutation; WR-15 runLength size bound unreachable; WR-16 BUILD.md restates a derivation). 346,950 valid-input differential cases, 0 mismatches | 2026-10-09 execute | Re-check section in findings/code-review.md, evidence `qa/code-review/20261009-131935/`, commit `fa7838d` | LANE (sdlc-code-reviewer, sonnet) | Routed to sdlc-dev-solver (sonnet) |
| 19 | Rulings on the re-check warnings | 2026-10-09 execute | All six fixed as the reviewer suggests. WR-15 reverses the earlier ruling to keep the size bound: unreachable, untestable code is deleted. Extra scan evasions (`Date["now"]`, `Date?.now()`) accepted as residual, the R16 note already leaves alias forms to review. Stop rule: no further code-review round, the QA finder runs next | ORCH | Ruled, reversible |
| 20 | The code-review finder has no Edit tool, so appending to its verdict meant rewriting the file, and Write could not carry two raw characters from round 1; it restored them with `git apply` | 2026-10-09 execute | Disclosed in the findings file. The brief asked for an additive append, which the finder's tools do not support well. Later briefs may let finders overwrite their own verdict (latest wins, as the constitution allows) | LANE (sdlc-code-reviewer) | No damage. Recorded |
| 21 | habit-logic QA finder: PASS. 32 scenarios (149 rows) pass, 0 fail, 0 untested; every R1 to R16 covered; 176 independent probe rows agree | 2026-10-09 execute | findings/qa.md, evidence `qa/qa/20261009-140635/`, commit `de0156a` | LANE (sdlc-qa-tester, haiku) | Solved |
| 22 | habit-logic module close: code review PASS (two rounds, stop rule), security PASS 0 findings (three rounds), QA PASS. Credential gate CLEAN over 583 files (controls pass). Suite 66 of 66. Last green `de0156a` | 2026-10-09 execute | README reconcile deferred to the app module close, where the project README is written (the logic module has no user-facing surface of its own) | ORCH | Module closed |
| 23 | Version label for this run | 2026-10-09 execute | Relabelled v0.1.0 to v1.0.0. Owner's words: "Make sure both app reach a stable 1.0 version. Then i will test it out." Folder moved to `docs/v1.0.0/`, STATE `version: 1.0.0`, plan documents keep their historical label | USER | Done |
| 24 | app module built: 10 tasks, commits `b6e5069` to `ed9ff9d`, build record `f4563ab`. 115 browser tests and 66 unit tests pass. Builder self-check with the plugin harness: 0 mismatched pixels on all six captures; live e2e script 11 of 11 in a scratch run (the official gate run is still to do) | 2026-10-09 execute | docs/modules/app/BUILD.md (judgment calls, README reconcile list) | LANE (sdlc-frontend-dev, sonnet) | Built, finders next |
| 25 | The app builder wrote two small edits with a short Python write and ran one read-only Python call through a heredoc, against the Write and Edit rule (reported by the builder) | 2026-10-09 execute | Content checked with git diff by the builder | LANE (sdlc-frontend-dev) | No damage. Recorded as a process breach |

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
