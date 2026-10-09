# Evidence: security solver, SEC-06 (app module), 2026-10-09

Written by the security solver (diagnose and patch in one context). Base `8e655e8` on `main`, clean tree. Ruling applied: ORCH 2026-10-09 (reversible), fix (b) of the re-check, exactly. Scope: SEC-06 only, plus the SEC-02 residual (b) that the same fix closes. Commands run from the project root, `PYTHONDONTWRITEBYTECODE=1`, headless Chromium 149 through Playwright, servers started on free `127.0.0.1` ports and stopped by exact PID.

## What is in this folder

| File | What it is |
|---|---|
| `evidence.md` | this index and the outputs |
| `mutants_sec06.py`, `run_mutants.py` | 22 mutants of the fix, run with the code-review finder's `mut.py` (it serves the working tree with the patch applied in memory, so no project file is written) |
| `serve_and_run.py` | serves the project root on a free port, runs commands against it, stops the server by PID (used for the fidelity harness and `live_e2e.py`) |
| `probe_11_sec06_real_tree.py` | the 27 names of the re-check's `probe_10`, on the real tree: title line before the fix against the fix |
| `probe_12_bmp_sweep.py` | every Basic Multilingual Plane code point through the real `openDeleteDialog`, 3 name shapes, then a pair sweep |
| `probe_13_syriac_abbreviation_mark.py` | what turned out to be a rounding artefact in the first run of probe_12 (U+070F), looked at in numbers and pictures |
| `probe_14_sec06_shots.py`, `shots/` | before and after pictures of the repro name; the U+070F pictures |
| `live-e2e-scratch/` | the cold-boot gate `tests/browser/live_e2e.py` against a served copy (not the official `live-e2e` folder) |

## 1. Diagnosis (confirmed on the running app, not taken on trust)

Path: a habit name (typed, or written to `streaks.state` by a sibling page, T9) is stored as given, `fillRow` writes it to the list, the trash button's click goes to `askToDelete`, and `view.openDeleteDialog(habitName)` writes `Delete "`, U+2068, name, U+2069, `"?` as one text node in `h2#del-title`. That text node is the sink.

Cause (bidi algorithm): U+2069 closes the nearest open isolate. An isolate opener (U+2066 to U+2068) inside the name with no closer takes the title's own U+2069, so the title's U+2068 stays open to the end of the line. With a strong right-to-left letter before the opener, the title's isolate resolves right to left and the neutral closing quote and question mark that follow are drawn to the left of the name. A U+2069 or a paragraph separator inside the name closes the title's isolate early (the SEC-02 residual (b)).

Reproduced before touching `src/`: the name U+05D0, U+2066, `abc` at 390x844 gives the title text on screen `Delete "?"abc` then the alef (`shots/sec06-alef-lri-abc-before-8e655e8.png`); with the fix it reads `Delete "abc` alef `"?` (`shots/sec06-alef-lri-abc-fixed.png`). It is a display spoof of the confirmation screen; the habit named in the title is still the habit deleted. Severity LOW stands. Not a false positive.

## 2. The patch (ORCH ruling, fix (b))

`src/view.js`: new module constant `TITLE_STRIPPED = /[\u{202A}-\u{202E}\u{2066}-\u{2069}\u{0085}\u{001C}-\u{001E}\u{2029}]/gu` (written as escape text), and `openDeleteDialog` writes `Delete "\u{2068}${habitName.replace(TITLE_STRIPPED, "")}\u{2069}"?`. The U+2068 and U+2069 stay around the name. The stored name, `fillRow` (the list row and the trash button's `aria-label`) and every other place are untouched. No habit-logic file and no `src/styles.css`, `docs/design/` or `index.html` change.

The `src/view.js` comments were updated in the same patch: the old docblock said the isolate alone keeps the quotes in place, which the strip now qualifies, and the new docblock above `TITLE_STRIPPED` says why the strip exists.

Bytes (after the Edit, checked with a read-only count): `src/view.js` 13300 bytes, 0 non-ASCII bytes; the file holds the escape text `\u{...}` and no raw character. The Edit tool did not turn the escapes into raw characters this time. A scan of 31 files (`src/*.js`, `src/styles.css`, `index.html`, `tests/browser/*.py`, `tests/browser/fidelity/*.js`, spec, qa, BUILD, the findings file and this folder's `.py` files) found no raw U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E or U+2029, and no em or en dash. The only non-ASCII characters are 10 in `spec.md` and 18 in `findings/security.md`, which were there before this round.

## 3. Tests

`tests/browser/test_delete.py` (the SEC-02 block is now "SEC-02 and SEC-06: the name in the title"), `tests/browser/conftest.py` (the `dialog_title` docstring, which would otherwise claim an exact title for any stored name).

| Test | Rows | What it pins |
|---|---|---|
| `test_SEC02_SEC06_R13_the_title_shows_the_name_without_format_characters_and_its_quotes_stay_in_place` | 16 | for each name: one text node and no child element, the opening quote lies left of every visible name character, they lie left of the closing quote, which lies left of the question mark (reading order, exact left edges, line first); and the title text equals `Delete "`, FSI, the shown name, PDI, `"?` (`dialog_title(shown)`). Rows: the 5 SEC-02 override names (now with the stripped name written out), the 5 SEC-06 shapes of probe_08 (alef + LRI + abc, alef + FSI + abc, Hebrew word + LRI, Hebrew word + space + abc + LRI, Arabic meem + LRI + x), the 2 accepted-residual names (U+2069 then an override, U+2029 then an override), a matched pair (alef, LRI, abc, PDI), and 3 names with nothing to strip (plain, a Hebrew name, alef alone) |
| `test_SEC06_R13_every_character_of_the_stripped_set_is_left_out_of_the_title` | 1 | all 14 stripped code points, one at a time between letters, leave `x` fifteen times |
| `test_SEC06_R13_the_neighbours_of_the_stripped_ranges_and_other_invisible_characters_stay_in_the_title` | 1 | 16 characters the strip must not touch (U+0084, U+0086, U+001B, U+001F, U+2028, U+202F, U+2065, U+206A, U+200E, U+200F, U+061C, U+200B, U+200C, U+200D, U+2060, U+FEFF) stay in the title |
| `test_SEC06_R13_only_the_titles_copy_loses_the_characters_and_the_habit_named_in_it_is_the_one_deleted` | 1 | the list row, the trash button's `aria-label` and the stored text keep the name as typed, opening writes nothing (`count_writes`), and confirming deletes that habit only |

Browser tests went from 162 to 176: the old 5-row SEC-02 test became the 16-row test (+11), plus 3 new tests (+3). The old test could not stay as it was, because for the five override names `dialog_title(name)` is no longer the title (the override characters are now left out); its five ids are kept in the new test with the shown name written out by hand, not computed with the app's rule.

One correction during the round: my first version of the position check rounded each left edge to whole pixels, like the re-check's probes. A glyph that is 0.4 px wide (U+070F) made two rounded edges equal and a strict `<` failed; the committed test compares exact edges, as the SEC-02 test did. The fix commit was amended once, before anything else was committed on top of it, for this reason (`git commit --amend`, not pushed anywhere).

## 4. Red, then green

**Red, the literal tree without the fix** (the strip call taken out of `src/view.js` by an Edit, the final tests, then put back by an Edit and `git diff --quiet src/view.js` exit 0, 13300 bytes, 0 non-ASCII): `python -m pytest tests/browser/test_delete.py -v -p no:cacheprovider --tb=line -k SEC06`

```
15 failed, 4 passed, 46 deselected in 4.98s
```

| Row | Without the fix | Why |
|---|---|---|
| rlo first, rlo in the middle, three rlo, rle, rli (SEC-02) | FAIL (5) | the quotes were in place (the isolate holds) but the title text still holds the override characters |
| alef lri abc, alef fsi abc, Hebrew word lri, Hebrew word space abc lri, Arabic meem lri x (SEC-06) | FAIL (5) | `max(inside) < close` fails: some name character is drawn at or right of the closing quote (measured: opening quote at 101.64, rightmost name character at 154.1, 154.1, 153.1, 186.8 and 134.4 for the five rows in that order; the characters of alef lri abc sit at 154.13, 125.41, 134.80, 145.64) |
| x pdi rlo y z, x paragraph separator rlo y z (residual (b)) | FAIL (2) | the same assertion (rightmost name characters at 147.7 and 152.7) |
| alef lri abc pdi (matched pair) | FAIL | the quotes were in place at the base, but the title text still holds the pair |
| stripped set (14 characters) | FAIL | `characters in the title:` lists U+202A to U+202E, U+2066 to U+2069, U+0085, U+001C to U+001E, U+2029 |
| only the title's copy loses the characters | FAIL | the title still holds U+2066 |
| plain, hebrew, alef alone | pass | nothing to strip (controls) |
| the neighbours of the stripped ranges | pass | nothing to strip (control) |

The same tests with the mutant `S6-no-strip` served from memory (section 5) gave the identical `15 failed, 4 passed`. The first red run, with the first version of the tests (rounded edges), also gave `15 failed, 4 passed`.

**Green, the fix in place:**

```
python -m pytest tests/browser/test_delete.py -q -p no:cacheprovider -k SEC06   (three runs)
19 passed, 46 deselected in 4.68s / 4.67s / 5.01s
```

## 5. Mutants (22, served from memory by `mut.py`, `-k SEC06`, `--maxfail 1000`, run on the final tests)

| Mutant | What it changes | Verdict | Failed of 19 |
|---|---|---|---|
| S6-no-strip | the title uses the name as stored (the tree before the fix) | KILLED | 15 |
| S6-missing-2066-2069 | the strip lacks U+2066 to U+2069 (the ruling's example) | KILLED | 10 |
| S6-missing-202A-202E | lacks U+202A to U+202E | KILLED | 7 |
| S6-missing-2066-only | lacks U+2066 only | KILLED | 7 |
| S6-missing-2068 | lacks U+2068 only | KILLED | 2 |
| S6-missing-2069 | lacks U+2069 only | KILLED | 3 |
| S6-missing-202E | lacks U+202E only | KILLED | 6 |
| S6-missing-0085 | lacks U+0085 | KILLED | 1 |
| S6-missing-001C-001E | lacks U+001C to U+001E | KILLED | 1 |
| S6-short-001E | stops at U+001D | KILLED | 1 |
| S6-missing-2029 | lacks U+2029 | KILLED | 2 |
| S6-wide-low-2065 | second range starts at U+2065 | KILLED | 1 |
| S6-wide-high-206A | second range ends at U+206A | KILLED | 1 |
| S6-wide-high-202F | first range ends at U+202F | KILLED | 1 |
| S6-wide-low-2028 | first range starts at U+2028 | KILLED | 1 |
| S6-wide-marks | U+200E, U+200F, U+061C stripped too | KILLED | 1 |
| S6-wide-0084-0086 | U+0085 widened to U+0084 to U+0086 | KILLED | 1 |
| S6-no-g-flag | only the first match is removed | KILLED | 5 |
| S6-replace-with-space | a space replaces each stripped character | KILLED | 15 |
| S6-list-too | the list row's name is stripped too | KILLED | 1 |
| S6-label-too | the trash button's `aria-label` is stripped too | KILLED | 1 |
| S6-no-isolate-marks | the strip stays, the FSI and PDI go (the SEC-02 control removed) | KILLED | 19 |

22 of 22 killed, no survivor. After the mutant runs `git status` showed no change to `src/`.

## 6. Suites

| Suite | Result |
|---|---|
| `python -m pytest tests/browser -q -p no:cacheprovider` | **176 passed**, 0 failed, 0 skipped, 52.63 s (162 at the start, +14). Two runs, 176 each (before and after the exact-edge change to the test); conftest stopped its two servers and checked that both ports refuse connections |
| `node --test "tests/**/*.test.js"` | **99 pass**, 0 fail, 0 skipped (unchanged, habit-logic untouched) |

## 7. Fidelity, M1 (the delete dialog), harness `fidelity.py` 2.1.3, the qa.md flags

```
python -B {sdlc}/harness/fidelity.py --golden ./docs/design/delete-dialog.html --candidate <served root> --viewport <390x844|1280x800> --dpr 1 --color-scheme light --fixed-time 2026-10-08T09:00:00 --candidate-init-script tests/browser/fidelity/seed-sample.js --candidate-after-load tests/browser/fidelity/open-delete-dialog.js --out ./harness/_scratch/fidelity-m1-<viewport>-sec06/
390x844  : mismatch_pixels 0 of 443040,  dimensions_match true, golden and candidate 390 x 1136, threshold 0.1
1280x800 : mismatch_pixels 0 of 1071360, dimensions_match true, golden and candidate 1280 x 837, threshold 0.1
```

(Output in the git-ignored `harness/_scratch/`, as the previous round did; `docs/design/` was only read. The state script `open-delete-dialog.js` checks the title text `Delete "`, U+2068, `Read 20 pages`, U+2069, `"?`; the sample name holds none of the stripped characters, so it needed no change.)

## 8. Cold-boot live gate, `tests/browser/live_e2e.py` against a served copy, into `live-e2e-scratch/`

```
GATE PASS: 11 of 11 steps. summary.json: steps 11, steps_passed 11, requests 21, requests_outside_the_rule 0, console_errors 0, page_errors 0,
browser Chromium 149.0.7827.55, start_date and end_date 2026-10-09, void_if_the_date_changed false.
```

The dialog title the steps saw is `Delete "`, U+2068, `Stretch 10 minutes`, U+2069, `"?`. The official `@R27` run is the orchestrator's.

## 9. Probes on the real tree

**probe_11** (27 names of the re-check's `probe_10`, 390x844, the title line of `8e655e8` put back in memory against the working tree): in place at `8e655e8` 17 of 27, in place with the fix **27 of 27**; the title text equals `Delete "`, FSI, the name without the 14 characters (stripped with a Python set written independently of the app's regex), PDI, `"?` for 27 of 27; the trash button's `aria-label` and the stored name equal the typed name for 27 of 27. The ten that moved at `8e655e8` are the five SEC-06 names, `alef + RLI + abc`, `alef + LRI + abc + RLO`, the two accepted-residual names, and `x + PDI + RLO + y z` (the re-check's "KNOWN RESIDUAL" row). The controls (latin + LRI + alef, matched pair, alef alone, Hebrew word + space + abc) were in place both ways.

**probe_12** (completeness; every BMP code point c except the surrogates, 63488 code points, through the real `openDeleteDialog` of the page, reading-order check with exact left edges):

```
8e655e8 (title without the strip), shape A "x" c RLO "y z":  6 code points move the quotes: U+001C-U+001E U+0085 U+2029 U+2069
8e655e8, shape B  ALEF c "abc":                               3 code points move the quotes: U+2066-U+2068
8e655e8, shape G  ALEF c "abc" ALEF:                          3 code points move the quotes: U+2066-U+2068
code points that move the quotes at 8e655e8 and are NOT in the stripped set: none
working tree (with the strip), shapes A, B, G:                0 code points move the quotes
second round, U+070F in 14 hand-written shapes: 8e655e8 1 out of place (the one that keeps an opener in the name), working tree none
second round, pair sweep (2528 code points of bidi classes AL AN B BN NSM R S WS x 6 companions x 2 shapes = 30336 names): out of place at 8e655e8 0, with the fix 0
page errors: none
```

So the triggers at the base are exactly members of the stripped set, none of the other 63,000 code points moves the quotes alone or in front of a companion, and with the strip none does.

**probe_13 and the U+070F false alarm.** The first run of probe_12 rounded left edges to whole pixels and flagged U+070F (SYRIAC ABBREVIATION MARK) alone, first or last in a name, on both trees. probe_13 printed the exact edges: for the name `x` + U+070F the opening quote is at 101.6, `x` at 109.5, the mark at 118.6 (0.4 px wide), the closing quote at 118.9 and the question mark at 126.8: in order. Rounded, 118.6 and 118.9 are both 119, and a strict `<` failed. The pictures (`shots/sec06-sam-*.png`) show the quotes in place with a small bar where the mark is. It was a measurement artefact, not a title spoof, and probe_12 now compares exact edges (the committed test does too).

**probe_14** pictures: `shots/sec06-alef-lri-abc-before-8e655e8.png` (`Delete "?"abc` alef), `shots/sec06-alef-lri-abc-fixed.png` (`Delete "abc` alef `"?`), and the same pair for `x`, U+2069, U+202E, `y z`.

## 10. Credential gate

`python -B {sdlc}/harness/credential_sweep.py --staged`, run unpiped from the project root before each commit: exit 0 each time (positive control true, negative control 0 false hits). Commits: the fix and its tests, the amend of that commit, the spec, qa and BUILD notes, and the findings section with this folder.

## 11. Observations (not findings, left alone)

- A name made only of stripped characters shows as an empty pair of quotes in the title. It showed an empty pair before (an all-invisible name is valid, the `habit-logic` audit noted it), so nothing got worse.
- Two stored names that differ only in stripped characters (`ab` and `a`, U+202E, `b`) show the same title. The dialog is opened from the row that was pressed and "Delete habit" deletes that row, so which habit goes is not in doubt, but the title cannot tell them apart.
- A name that holds a matched isolate pair (alef, U+2066, `abc`, U+2069) loses the pair in the title. That is the accepted cost named in the R13 note.
- The re-check's probes (`probe_06`, `probe_08`, `probe_10`) round left edges to whole pixels. That can only add false alarms for very narrow glyphs, it cannot hide a real reordering (the moved names are tens of pixels off). Worth knowing for whoever reuses them.
- The combining-mark overprint (SEC-02 residual (a)) stays accepted for v1.0 and untested, as ruled.
- Safari and Firefox were not run (CLAUDE.md: headless Chromium only). The bidi algorithm is the same standard, but the isolate behaviour at the edges was measured in Chromium only.

## 12. Processes and process notes

PROCESSES: started and stopped.
- `python -m pytest` runs: two `http.server` each (conftest), stopped by conftest, which printed that both ports refuse connections each time.
- The mutant runner: one in-process server thread and one pytest child per mutant, waited for by the runner.
- `serve_and_run.py`: two servers (one for the two fidelity runs, one for `live_e2e.py`), each stopped by exact PID in a `finally` block with the port check printed (`accepts connections: False`).
- Probes 11 to 14: one `http.server` and one headless Chromium each, stopped by exact PID (the probes' `Run` context prints the refusal check and a before and after process diff; every PID this run started was gone).
- One mistake of mine: a `find /` I ran to look for a helper script, which the shell moved to the background; I identified it by its command line (`find.exe / -name serve_and_run.py`, PID 47904, mine) and stopped it with `taskkill /PID 47904 /F`. Nothing else was touched.
- Processes of other agents were present during the round (another project's `python.exe` probe, its `http.server`, `node.exe` and `chrome-headless-shell.exe` tree, Opera, system services). None was started by this run, none was touched.

Lapses against "Write and Edit tools only": none. Every file I created or changed was made with Write or Edit. The fidelity harness, `live_e2e.py`, pytest and Playwright wrote their own outputs (`harness/_scratch/`, `live-e2e-scratch/`, `shots/`). `git add`, `git commit` and one `git commit --amend` were the only git writes. No `docs/progress/` or `docs/v1.0.0/` file was staged or edited. The clipboard was never touched and `bypass_csp` was never used (the probes import `/src/view.js` from `page.evaluate`, which the page's CSP `script-src 'self'` allows).
