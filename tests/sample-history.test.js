import test from "node:test";
import assert from "node:assert/strict";
import sample from "./fixtures/sample-history-v1.0.0.json" with { type: "json" };
import { readFileSync } from "node:fs";
import { addDays, isDateKey } from "../src/dates.js";
import {
  currentStreak,
  bestStreak,
  toggleDay,
  heatmapCells,
  monthLabels,
  doneFlags,
  yearMonths,
} from "../src/habits.js";
import { sampleHabits } from "./fixtures/sample.js";

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

// The v1.1.0 sample is docs/design/sample-history.json, read only. sampleHabits converts its 366-character
// done strings into habits, and `file` below is read a second time raw, so the conversion is checked
// against the file's own characters and not against itself.
const V110_FILE = new URL("../docs/design/sample-history.json", import.meta.url);
const v110File = JSON.parse(readFileSync(V110_FILE, "utf8"));
const v110Habits = () => sampleHabits(V110_FILE);
const V110_TODAY = "2026-10-10";
const firstThree = () => v110Habits().slice(0, 3);
const byV110Name = (all, name) => all.find((habit) => habit.name === name);

test("@R9 @R10 @R19 fixture check: the v1.1.0 sample is today 2026-10-10 with twelve habits of 366 days", () => {
  assert.equal(v110File.today, V110_TODAY);
  assert.equal(v110File.from, "2025-10-10");
  assert.equal(v110File.to, V110_TODAY);
  const all = v110Habits();
  assert.equal(all.length, 12);
  assert.deepEqual(
    all.slice(0, 3).map((habit) => habit.name),
    ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"],
  );
  for (const [position, habit] of all.entries()) {
    assert.equal(v110File.habits[position].done.length, 366, habit.name);
    assert.ok(habit.done.every(isDateKey), habit.name);
    assert.deepEqual(habit.done, [...new Set(habit.done)].sort(), habit.name);
    assert.ok(habit.done.every((key) => key >= v110File.from && key <= v110File.to), habit.name);
  }
});

test("@R19 which habits are done on a day, for the v1.1.0 sample's first three habits", () => {
  const rows = [
    ["2026-10-10", [true, false, false]],
    ["2026-09-22", [false, false, true]],
    ["2026-07-21", [true, true, true]],
    ["2026-10-11", [false, false, false]],
  ];
  for (const [key, flags] of rows) {
    assert.deepEqual(doneFlags(firstThree(), key), flags, key);
  }
});

test("@R19 all twelve habits on 2026-10-10 give the golden's 7 done, and none on an empty list", () => {
  assert.deepEqual(doneFlags([], V110_TODAY), []);
  const flags = doneFlags(v110Habits(), V110_TODAY);
  assert.deepEqual(flags, [true, false, false, true, false, true, true, true, false, true, true, false]);
  assert.equal(flags.filter(Boolean).length, 7);
});

test("@R19 @R6 @R7 the goldens' Current and Best come from the v1.1.0 sample", () => {
  const rows = [
    ["Read 20 pages", 4, 9],
    ["Stretch 10 minutes", 2, 5],
    ["No phone after 11pm", 0, 14],
    ["Drink 2 litres of water", 1, 11],
    ["Walk 8,000 steps", 1, 11],
    ["Journal one page", 8, 11],
    ["Practise guitar", 1, 11],
    ["Cook dinner at home", 5, 11],
    ["Lights out by midnight", 2, 11],
    ["Meditate 5 minutes", 2, 11],
    ["Floss", 1, 11],
    ["Learn 10 Malay words", 1, 11],
  ];
  const all = v110Habits();
  assert.equal(rows.length, all.length);
  for (const [name, current, best] of rows) {
    const { done } = byV110Name(all, name);
    assert.equal(currentStreak(done, V110_TODAY), current, `${name} current streak`);
    assert.equal(bestStreak(done), best, `${name} best streak`);
  }
});

test("@R10 @R19 the v1.1.0 sample's band of 12 weeks", () => {
  const cells = heatmapCells(firstThree(), V110_TODAY);
  const byKey = new Map(cells.map((cell) => [cell.key, cell]));
  assert.equal(cells.length, 84);
  assert.deepEqual([cells[0].key, cells[83].key], ["2026-07-20", "2026-10-11"]);

  const todayCell = byKey.get(V110_TODAY);
  assert.deepEqual([todayCell.column, todayCell.row, todayCell.today], [12, 6, true]);
  assert.deepEqual(cells.filter((cell) => cell.future).map((cell) => cell.key), ["2026-10-11"]);

  assert.deepEqual(
    [byKey.get("2026-09-22").done, byKey.get("2026-09-22").count],
    [[false, false, true], 1],
  );
  assert.deepEqual(
    [byKey.get("2026-07-21").done, byKey.get("2026-07-21").count],
    [[true, true, true], 3],
  );
  assert.deepEqual([todayCell.done, todayCell.count], [[true, false, false], 1]);

  const notFuture = cells.filter((cell) => !cell.future);
  assert.equal(notFuture.length, 83);
  const distribution = [0, 1, 2, 3].map((count) => notFuture.filter((cell) => cell.count === count).length);
  assert.deepEqual(distribution, [2, 16, 47, 18]);
});

test("@R9 @R6 @R7 ticks on the v1.1.0 sample move Current and Best", () => {
  const rows = [
    [1, "2026-10-10", true, 3, 5],
    [0, "2026-10-10", false, 3, 9],
    [0, "2026-09-22", true, 4, 13],
    [2, "2026-10-09", true, 8, 14],
    [0, "2025-10-10", false, 4, 9],
  ];
  for (const [index, date, nowContains, current, best] of rows) {
    const input = firstThree();
    const result = toggleDay(input, index, date, V110_TODAY);
    const label = `index ${index} date ${date}`;
    assert.equal(result[index].done.includes(date), nowContains, label);
    assert.equal(currentStreak(result[index].done, V110_TODAY), current, `${label} current`);
    assert.equal(bestStreak(result[index].done), best, `${label} best`);
    result.forEach((habit, position) => {
      if (position !== index) assert.deepEqual(habit, input[position], `${label} other ${position}`);
    });
  }
});

test("@R9 the edges of the v1.1.0 year: the day before the start and the day after today change nothing", () => {
  for (const date of ["2025-10-09", "2026-10-11"]) {
    const input = firstThree();
    assert.deepEqual(toggleDay(input, 0, date, V110_TODAY), input, date);
  }
});

test("@R20 @R19 the v1.1.0 sample's year has 366 open days and each one reads the file's own character", () => {
  const months = yearMonths(V110_TODAY);
  const kinds = months.flatMap((month) => month.days).reduce((counts, { kind }) => ({ ...counts, [kind]: counts[kind] + 1 }), {
    open: 0,
    closed: 0,
    empty: 0,
  });
  assert.deepEqual(kinds, { open: 366, closed: 21, empty: 9 });

  const openKeys = months
    .flatMap((month) => month.days)
    .filter((day) => day.kind === "open")
    .map((day) => day.key)
    .sort();
  assert.equal(openKeys.length, v110File.habits[0].done.length);
  assert.deepEqual([openKeys[0], openKeys.at(-1)], [v110File.from, v110File.to]);
  assert.equal(addDays(openKeys[0], 365), openKeys.at(-1), "the open days are 366 days in a row");

  const all = v110Habits();
  openKeys.forEach((key, position) => {
    assert.deepEqual(
      doneFlags(all, key),
      v110File.habits.map((habit) => habit.done[position] === "1"),
      key,
    );
  });
});
