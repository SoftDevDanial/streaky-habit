import test from "node:test";
import assert from "node:assert/strict";
import sample from "../docs/design/sample-history.json" with { type: "json" };
import { isDateKey, shortDate } from "../src/dates.js";
import {
  weekWindow,
  currentStreak,
  bestStreak,
  runContinues,
  heatmapCells,
  monthLabels,
} from "../src/habits.js";

// The sample is read-only golden data. Tests pass a clone, so no call can change the imported sample a later test reads.
const habits = structuredClone(sample.habits);
const TODAY = "2026-10-08";
const NEXT_DAY = "2026-10-09";

const byName = (name) => habits.find((habit) => habit.name === name);

test("@R5 @R6 @R7 @R8 @R9 @R10 @R11 @R12 fixture check: the sample is today 2026-10-08 with three habits whose days are valid, ascending and unique", () => {
  assert.equal(sample.today, TODAY);
  assert.deepEqual(
    habits.map((habit) => habit.name),
    ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"],
  );
  for (const habit of habits) {
    assert.ok(habit.done.every(isDateKey), habit.name);
    assert.deepEqual(habit.done, [...new Set(habit.done)].sort(), habit.name);
  }
});

test("@R5 @R6 @R7 @R8 the sample's strips and streaks on the key screen", () => {
  const rows = [
    ["Read 20 pages", ". D D D D D D", 6, 14, false],
    ["Stretch 10 minutes", "D D . D D D .", 3, 9, true],
    ["No phone after 11pm", ". D . . D . D", 1, 4, false],
  ];
  for (const [name, strip, current, best, run] of rows) {
    const { done } = byName(name);
    const drawn = weekWindow(TODAY).map((key) => (done.includes(key) ? "D" : ".")).join(" ");
    assert.equal(drawn, strip, `${name} strip`);
    assert.equal(currentStreak(done, TODAY), current, `${name} current streak`);
    assert.equal(bestStreak(done), best, `${name} best streak`);
    assert.equal(runContinues(done, TODAY), run, `${name} run flag`);
  }
});

test("@R5 the strip runs from Fri 2 Oct to Thu 8 Oct", () => {
  const days = weekWindow(TODAY);
  assert.equal(days[0], "2026-10-02");
  assert.equal(days[6], TODAY);
  assert.deepEqual([shortDate(days[0]), shortDate(days[6])], ["Fri 2 Oct", "Thu 8 Oct"]);
});

test("@R6 @R8 the same sample one day later", () => {
  const rows = [
    ["Read 20 pages", 6, false],
    ["Stretch 10 minutes", 0, true],
    ["No phone after 11pm", 1, false],
  ];
  for (const [name, current, run] of rows) {
    const { done } = byName(name);
    assert.equal(currentStreak(done, NEXT_DAY), current, `${name} current streak`);
    assert.equal(runContinues(done, NEXT_DAY), run, `${name} run flag`);
  }
});

test("@R7 the best runs sit in the older history", () => {
  assert.equal(bestStreak(byName("Read 20 pages").done), 14);
  assert.equal(bestStreak(byName("Stretch 10 minutes").done), 9);
  assert.equal(bestStreak(byName("No phone after 11pm").done), 4);
});

test("@R10 @R11 the sample's heatmap equals the golden", () => {
  const cells = heatmapCells(habits, TODAY);
  const byKey = new Map(cells.map((cell) => [cell.key, cell]));

  const todayCell = byKey.get(TODAY);
  assert.deepEqual([todayCell.column, todayCell.row, todayCell.today], [12, 4, true]);

  const goldenKeys = Object.keys(sample.heatmapLevels);
  assert.equal(goldenKeys.length, 81);
  for (const key of goldenKeys) {
    const cell = byKey.get(key);
    assert.ok(cell, `cell for ${key}`);
    assert.equal(cell.level, sample.heatmapLevels[key], `level of ${key}`);
    assert.equal(cell.total, 3, `total of ${key}`);
    assert.equal(cell.count, habits.filter((habit) => habit.done.includes(key)).length, `count of ${key}`);
  }

  const notFuture = cells.filter((cell) => !cell.future).map((cell) => cell.key);
  assert.deepEqual([...notFuture].sort(), [...goldenKeys].sort());

  const distribution = [0, 1, 2, 3, 4].map((level) => goldenKeys.filter((key) => byKey.get(key).level === level).length);
  assert.deepEqual(distribution, [3, 30, 28, 0, 20]);

  for (const key of ["2026-10-09", "2026-10-10", "2026-10-11"]) {
    assert.equal(byKey.get(key).future, true, key);
  }
  assert.equal(cells.filter((cell) => cell.future).length, 3);
});

test("@R12 the sample's month axis equals the golden: Jul 1, Aug 3, Sep 8, Oct 12", () => {
  assert.deepEqual(monthLabels(sample.today), [
    { column: 1, month: "Jul" },
    { column: 3, month: "Aug" },
    { column: 8, month: "Sep" },
    { column: 12, month: "Oct" },
  ]);
});
