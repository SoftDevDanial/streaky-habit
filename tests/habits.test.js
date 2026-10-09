import test from "node:test";
import assert from "node:assert/strict";
import sample from "../docs/design/sample-history.json" with { type: "json" };
import {
  MAX_HABITS,
  MAX_NAME_LENGTH,
  weekWindow,
  currentStreak,
  bestStreak,
  runContinues,
  toggleDay,
} from "../src/habits.js";

const TODAY = "2026-10-08";

// A fresh copy per test, so no test can leak a change into another through the imported JSON.
const sampleHabits = () => structuredClone(sample.habits);

const isAscendingUnique = (done) => {
  const expected = [...new Set(done)].sort();
  return expected.length === done.length && expected.every((key, position) => key === done[position]);
};

test("@R13 @R14 the limits are exported", () => {
  assert.equal(MAX_NAME_LENGTH, 40);
  assert.equal(MAX_HABITS, 12);
});

test("@R5 the seven days of the strip", () => {
  const rows = [
    ["2026-10-08", ["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]],
    ["2027-01-03", ["2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-03"]],
    ["2028-03-02", ["2028-02-25", "2028-02-26", "2028-02-27", "2028-02-28", "2028-02-29", "2028-03-01", "2028-03-02"]],
  ];
  for (const [today, days] of rows) {
    assert.deepEqual(weekWindow(today), days, today);
  }
});

test("@R5 the strip has 7 keys, the last is today, and every call returns a new array", () => {
  const first = weekWindow(TODAY);
  assert.equal(first.length, 7);
  assert.equal(first.at(-1), TODAY);
  assert.notEqual(weekWindow(TODAY), first);
});

test("@R6 a streak does not break until today is over", () => {
  const rows = [
    [[], 0],
    [["2026-10-07"], 1],
    [["2026-10-06"], 0],
    [["2026-10-09"], 0],
    [["2026-10-08", "2026-10-08"], 1],
    [["2026-09-30", "2026-10-01"], 0],
    [["2026-10-08", "2026-10-06", "2026-10-07"], 3],
    [["2026-10-07", "2026-10-08", "2026-10-09"], 2],
  ];
  for (const [done, current] of rows) {
    assert.equal(currentStreak(done, TODAY), current, JSON.stringify(done));
  }
});

test("@R6 a streak runs across a month, a year and a leap day", () => {
  assert.equal(currentStreak(["2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02"], "2027-01-02"), 4);
  assert.equal(currentStreak(["2028-02-28", "2028-02-29", "2028-03-01"], "2028-03-01"), 3);
  assert.equal(currentStreak(["2028-02-28", "2028-02-29", "2028-03-01"], "2028-03-02"), 3);
});

test("@R6 a streak that crosses a DST change", () => {
  const before = process.env.TZ;
  process.env.TZ = "America/New_York";
  try {
    assert.equal(currentStreak(["2026-03-07", "2026-03-08", "2026-03-09"], "2026-03-09"), 3);
    assert.equal(currentStreak(["2026-10-31", "2026-11-01", "2026-11-02"], "2026-11-02"), 3);
  } finally {
    if (before === undefined) delete process.env.TZ;
    else process.env.TZ = before;
  }
});

test("@R7 the longest run in the whole history", () => {
  const rows = [
    [[], 0],
    [["2026-12-30", "2026-12-31", "2027-01-01"], 3],
    [["2028-02-28", "2028-02-29", "2028-03-01"], 3],
    [["2026-02-28", "2026-03-01"], 2],
    [["2026-10-08", "2026-10-08"], 1],
    [["2026-10-01", "2026-10-03"], 1],
    [["2026-10-09", "2026-10-08", "2026-10-07"], 3],
  ];
  for (const [done, best] of rows) {
    assert.equal(bestStreak(done), best, JSON.stringify(done));
  }
});

test("@R7 the best run may be old, and a later shorter run does not replace it", () => {
  const done = ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2026-10-07", "2026-10-08"];
  assert.equal(bestStreak(done), 4);
});

test("@R8 the run flag needs the first strip day and the day before it", () => {
  const rows = [
    ["both", ["2026-10-01", "2026-10-02"], TODAY, true],
    ["only the first strip day", ["2026-10-02"], TODAY, false],
    ["only the day before", ["2026-10-01"], TODAY, false],
    ["neither", ["2026-10-04", "2026-10-05"], TODAY, false],
    ["both, in reverse order with a duplicate", ["2026-10-02", "2026-10-01", "2026-10-02"], TODAY, true],
    ["both, one day later the window moved on", ["2026-10-01", "2026-10-02"], "2026-10-09", false],
    ["the moved window", ["2026-10-02", "2026-10-03"], "2026-10-09", true],
    ["a whole strip but nothing before it", weekWindow(TODAY), TODAY, false],
    ["empty", [], TODAY, false],
  ];
  for (const [label, done, today, expected] of rows) {
    assert.equal(runContinues(done, today), expected, label);
  }
});

test("@R9 ticking a day inside the window", () => {
  const rows = [
    [1, "2026-10-08", true, 4],
    [0, "2026-10-08", false, 5],
    [2, "2026-10-07", true, 3],
    [1, "2026-10-04", true, 7],
    [1, "2026-10-02", false, 3],
    [0, "2026-10-02", true, 10],
  ];
  for (const [index, date, nowContains, current] of rows) {
    const input = sampleHabits();
    const snapshot = structuredClone(input);
    const result = toggleDay(input, index, date, TODAY);
    const label = `index ${index} date ${date}`;

    assert.notEqual(result, input, label);
    assert.equal(result.length, input.length, label);
    assert.equal(result[index].done.includes(date), nowContains, label);
    assert.ok(isAscendingUnique(result[index].done), label);
    assert.equal(result[index].name, input[index].name, label);
    assert.equal(currentStreak(result[index].done, TODAY), current, label);
    result.forEach((habit, position) => {
      if (position !== index) assert.deepEqual(habit, input[position], `${label} other ${position}`);
      assert.notEqual(habit, input[position], `${label} new object ${position}`);
    });
    assert.deepEqual(input, snapshot, `${label} input unchanged`);
  }
});

test("@R9 days outside the window and bad indexes change nothing", () => {
  const rows = [
    [0, "2026-10-01"],
    [1, "2026-10-09"],
    [2, "2026-07-20"],
    [3, "2026-10-08"],
    [-1, "2026-10-08"],
    [0.5, "2026-10-08"],
    [Number.NaN, "2026-10-08"],
    [undefined, "2026-10-08"],
  ];
  for (const [index, date] of rows) {
    const input = sampleHabits();
    const result = toggleDay(input, index, date, TODAY);
    const label = `index ${index} date ${date}`;
    assert.notEqual(result, input, label);
    assert.deepEqual(result, sample.habits, label);
    assert.deepEqual(input, sample.habits, `${label} input unchanged`);
    result.forEach((habit, position) => assert.notEqual(habit, input[position], `${label} new object ${position}`));
  }
});

test("@R9 both ends of the window are editable and ticking twice restores the habit", () => {
  for (const date of ["2026-10-02", "2026-10-08"]) {
    const input = sampleHabits();
    const once = toggleDay(input, 2, date, TODAY);
    const twice = toggleDay(once, 2, date, TODAY);
    assert.notDeepEqual(once[2].done, input[2].done, date);
    assert.deepEqual(twice, input, date);
  }
});

test("@R9 an unsorted or duplicated done array comes back ascending without duplicates", () => {
  const input = [{ name: "A", done: ["2026-10-05", "2026-09-01", "2026-10-05"] }];
  const result = toggleDay(input, 0, "2026-10-03", TODAY);
  assert.deepEqual(result[0].done, ["2026-09-01", "2026-10-03", "2026-10-05"]);
});

test("@R9 an empty habit list stays empty", () => {
  assert.deepEqual(toggleDay([], 0, TODAY, TODAY), []);
});
