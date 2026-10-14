import test from "node:test";
import assert from "node:assert/strict";
import sample from "./fixtures/sample-history-v1.0.0.json" with { type: "json" };
import { isDateKey } from "../src/dates.js";
import { currentStreak, bestStreak, heatmapCells, monthLabels } from "../src/habits.js";

// The sample is read-only golden data. Tests pass a clone, so no call can change the imported sample a later test reads.
const habits = structuredClone(sample.habits);
const TODAY = "2026-10-08";
const NEXT_DAY = "2026-10-09";

const byName = (name) => habits.find((habit) => habit.name === name);

test("@R6 @R7 @R9 @R10 @R12 fixture check: the sample is today 2026-10-08 with three habits whose days are valid, ascending and unique", () => {
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

test("@R6 @R7 the sample's streaks on the 1.0 key screen", () => {
  const rows = [
    ["Read 20 pages", 6, 14],
    ["Stretch 10 minutes", 3, 9],
    ["No phone after 11pm", 1, 4],
  ];
  for (const [name, current, best] of rows) {
    const { done } = byName(name);
    assert.equal(currentStreak(done, TODAY), current, `${name} current streak`);
    assert.equal(bestStreak(done), best, `${name} best streak`);
  }
});

test("@R6 the same sample one day later", () => {
  const rows = [
    ["Read 20 pages", 6],
    ["Stretch 10 minutes", 0],
    ["No phone after 11pm", 1],
  ];
  for (const [name, current] of rows) {
    assert.equal(currentStreak(byName(name).done, NEXT_DAY), current, `${name} current streak`);
  }
});

test("@R7 the best runs sit in the older history", () => {
  assert.equal(bestStreak(byName("Read 20 pages").done), 14);
  assert.equal(bestStreak(byName("Stretch 10 minutes").done), 9);
  assert.equal(bestStreak(byName("No phone after 11pm").done), 4);
});

test("@R10 the 1.0 sample's 12 weeks", () => {
  const cells = heatmapCells(habits, TODAY);
  const byKey = new Map(cells.map((cell) => [cell.key, cell]));

  const todayCell = byKey.get(TODAY);
  assert.deepEqual([todayCell.column, todayCell.row, todayCell.today], [12, 4, true]);

  // The fixture's heatmapLevels is only the list of the 81 days up to today. Its levels are not read, a level is gone in v1.1.0.
  const goldenKeys = Object.keys(sample.heatmapLevels);
  assert.equal(goldenKeys.length, 81);
  for (const key of goldenKeys) {
    const cell = byKey.get(key);
    assert.ok(cell, `cell for ${key}`);
    assert.equal(cell.total, 3, `total of ${key}`);
    assert.deepEqual(cell.done, habits.map((habit) => habit.done.includes(key)), `done of ${key}`);
    assert.equal(cell.count, cell.done.filter(Boolean).length, `count of ${key}`);
  }

  const notFuture = cells.filter((cell) => !cell.future).map((cell) => cell.key);
  assert.deepEqual([...notFuture].sort(), [...goldenKeys].sort());

  const distribution = [0, 1, 2, 3].map((count) => notFuture.filter((key) => byKey.get(key).count === count).length);
  assert.deepEqual(distribution, [3, 30, 28, 20]);

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
