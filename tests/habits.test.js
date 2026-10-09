import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import sample from "../docs/design/sample-history.json" with { type: "json" };
import {
  MAX_HABITS,
  MAX_NAME_LENGTH,
  weekWindow,
  currentStreak,
  bestStreak,
  runContinues,
  toggleDay,
  heatLevel,
  heatmapCells,
  monthLabels,
  validateName,
  addHabit,
  deleteHabit,
} from "../src/habits.js";
import { addDays, dayParts } from "../src/dates.js";

const TODAY = "2026-10-08";
const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

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

// A walk that never ends would block this file's process for good, so the call runs in a child that is
// killed at the cap. A regression then fails the test instead of hanging the suite.
const WALK_CAP_MS = 5_000;
function streakInChild(name, ...args) {
  const habitsUrl = new URL("../src/habits.js", import.meta.url).href;
  const program = `
    const { ${name} } = await import(${JSON.stringify(habitsUrl)});
    process.stdout.write(JSON.stringify(${name}(...${JSON.stringify(args)})));
  `;
  try {
    return JSON.parse(
      execFileSync(process.execPath, ["--input-type=module", "--eval", program], {
        encoding: "utf8",
        timeout: WALK_CAP_MS,
        killSignal: "SIGKILL",
      }),
    );
  } catch (error) {
    if (error.code === "ETIMEDOUT") assert.fail(`${name} gave no result within ${WALK_CAP_MS} ms, child pid ${error.pid} killed`);
    throw error;
  }
}

test("@R7 the best-run walk ends on keys outside the valid range, where the next day repeats itself", () => {
  // Past 2^53 days, adding one day rounds back to the same count. The app's decoder drops such keys,
  // because they fail isDateKey, but the walk must still end if one gets through.
  const runStart = "24660873954866-12-02";
  const stuck = "24660873954866-12-04";
  assert.equal(addDays(runStart, 1), stuck, "precondition: the run start's next day is the stuck key");
  assert.equal(addDays(stuck, 1), stuck, "precondition: the stuck key's next day is itself");
  assert.ok(![runStart, stuck].includes(addDays(runStart, -1)), "precondition: the run start begins a run");

  const best = streakInChild("bestStreak", [runStart, stuck]);
  assert.ok(Number.isInteger(best) && best >= 0 && best <= 2, `bestStreak gave ${best}, more than the 2 distinct days`);
});

test("@R6 the current-run walk ends on the cycle below year 0001", () => {
  // Year -1 is written "00-1", which reads back as year 0, so going back from 0000-01-03 returns to it.
  const cycle = ["0000-01-03"];
  while (cycle.length < 12) cycle.push(addDays(cycle.at(-1), -1));
  assert.equal(new Set(cycle).size, 12, "precondition: 12 distinct keys");
  assert.equal(addDays(cycle.at(-1), -1), cycle[0], "precondition: the 12 keys form a cycle");

  const current = streakInChild("currentStreak", cycle, cycle[0]);
  assert.ok(
    Number.isInteger(current) && current >= 0 && current <= 12,
    `currentStreak gave ${current}, more than the 12 distinct days`,
  );
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

test("@R10 the 12-week grid around today", () => {
  const rows = [
    ["2026-10-08", "2026-07-20", "2026-10-11", 3],
    ["2026-10-11", "2026-07-20", "2026-10-11", 0],
    ["2026-10-05", "2026-07-20", "2026-10-11", 6],
    ["2026-10-12", "2026-07-27", "2026-10-18", 6],
    ["2027-01-07", "2026-10-19", "2027-01-10", 3],
  ];
  for (const [today, first, last, futureCount] of rows) {
    const cells = heatmapCells([], today);
    assert.equal(cells.length, 84, today);
    cells.forEach((cell, position) => {
      assert.equal(cell.column, Math.floor(position / 7) + 1, `${today} column of #${position}`);
      assert.equal(cell.row, (position % 7) + 1, `${today} row of #${position}`);
      assert.equal(cell.key, addDays(first, position), `${today} key of #${position}`);
      assert.equal(dayParts(cell.key).weekday, WEEKDAYS[cell.row - 1], `${today} weekday of #${position}`);
    });
    assert.deepEqual([cells[0].key, cells[0].column, cells[0].row], [first, 1, 1], today);
    assert.deepEqual([cells[83].key, cells[83].column, cells[83].row], [last, 12, 7], today);

    const future = cells.filter((cell) => cell.future);
    assert.equal(future.length, futureCount, today);
    for (const cell of future) {
      assert.ok(cell.key > today, `${today} future ${cell.key}`);
      assert.deepEqual([cell.count, cell.level], [null, null], `${today} future ${cell.key}`);
    }
    assert.ok(cells.filter((cell) => !cell.future).every((cell) => cell.key <= today), today);

    const todays = cells.filter((cell) => cell.today);
    assert.equal(todays.length, 1, today);
    assert.equal(todays[0].key, today, today);

    for (const cell of cells.filter((c) => !c.future)) {
      assert.deepEqual([cell.count, cell.total, cell.level], [0, 0, 0], `${today} ${cell.key}`);
    }
  }
});

test("@R10 a cell carries exactly the contract fields, and a habit counts once per day", () => {
  const habits = [
    { name: "A", done: ["2026-10-08", "2026-10-08"] },
    { name: "B", done: ["2026-10-08"] },
    { name: "C", done: [] },
  ];
  const cells = heatmapCells(habits, TODAY);
  assert.deepEqual(cells[11 * 7 + 3], {
    key: "2026-10-08",
    column: 12,
    row: 4,
    today: true,
    future: false,
    count: 2,
    total: 3,
    level: 2,
  });
  assert.deepEqual(cells[11 * 7 + 4], {
    key: "2026-10-09",
    column: 12,
    row: 5,
    today: false,
    future: true,
    count: null,
    total: 3,
    level: null,
  });
});

test("@R10 @R11 a fourth habit makes level 3 appear", () => {
  const habits = [...sampleHabits(), { name: "Drink water", done: [] }];
  const byKey = new Map(heatmapCells(habits, TODAY).map((cell) => [cell.key, cell]));
  const rows = [
    ["2026-07-20", 3, 3],
    ["2026-10-06", 3, 3],
    ["2026-10-08", 2, 2],
    ["2026-07-21", 1, 1],
    ["2026-08-12", 0, 0],
  ];
  for (const [key, count, level] of rows) {
    assert.deepEqual([byKey.get(key).count, byKey.get(key).total, byKey.get(key).level], [count, 4, level], key);
  }
});

test("@R10 the arguments are not changed and the cells are new objects", () => {
  const habits = sampleHabits();
  const first = heatmapCells(habits, TODAY);
  const second = heatmapCells(habits, TODAY);
  assert.deepEqual(habits, sample.habits);
  assert.notEqual(first, second);
  assert.notEqual(first[0], second[0]);
});

test("@R11 levels from the share of habits done", () => {
  const rows = [
    [1, [0, 4]],
    [2, [0, 2, 4]],
    [3, [0, 1, 2, 4]],
    [4, [0, 1, 2, 3, 4]],
    [5, [0, 1, 2, 2, 3, 4]],
    [6, [0, 1, 1, 2, 2, 3, 4]],
    [12, [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4]],
  ];
  for (const [total, levels] of rows) {
    const actual = Array.from({ length: total + 1 }, (_, count) => heatLevel(count, total));
    assert.deepEqual(actual, levels, `total ${total}`);
  }
});

test("@R11 no habits means level 0", () => {
  assert.equal(heatLevel(0, 0), 0);
});

test("@R12 month labels over the first column whose Monday is in the month", () => {
  const rows = [
    ["2026-10-08", [{ column: 1, month: "Jul" }, { column: 3, month: "Aug" }, { column: 8, month: "Sep" }, { column: 12, month: "Oct" }]],
    ["2026-10-12", [{ column: 1, month: "Jul" }, { column: 2, month: "Aug" }, { column: 7, month: "Sep" }, { column: 11, month: "Oct" }]],
    ["2027-01-07", [{ column: 1, month: "Oct" }, { column: 3, month: "Nov" }, { column: 8, month: "Dec" }, { column: 12, month: "Jan" }]],
    ["2026-03-31", [{ column: 1, month: "Jan" }, { column: 4, month: "Feb" }, { column: 8, month: "Mar" }]],
  ];
  for (const [today, labels] of rows) {
    assert.deepEqual(monthLabels(today), labels, today);
  }
});

test("@R12 each label sits on the first column whose Monday is in its month, for more start days", () => {
  const mondays = (today) => {
    const cells = heatmapCells([], today);
    return Array.from({ length: 12 }, (_, column) => cells[column * 7].key);
  };
  for (const today of ["2026-10-08", "2026-02-01", "2028-03-01", "2026-12-28", "2027-01-04"]) {
    const labels = monthLabels(today);
    const columns = mondays(today);
    assert.equal(labels[0].column, 1, today);
    for (const { column, month } of labels) {
      assert.equal(dayParts(columns[column - 1]).month, month, `${today} column ${column}`);
      if (column > 1) assert.notEqual(dayParts(columns[column - 2]).month, month, `${today} column ${column}`);
    }
    const monthsInGrid = columns.map((key) => dayParts(key).month);
    assert.equal(labels.length, new Set(monthsInGrid).size, today);
  }
});

const EXISTING_NAMES = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"];
const FORTY_EMOJI = "\u{1F4DA}".repeat(40);

test("@R13 name checks in the order empty, too long, duplicate", () => {
  const rows = [
    ["", { ok: false, error: "empty" }],
    ["   ", { ok: false, error: "empty" }],
    ["\t \n", { ok: false, error: "empty" }],
    ["Walk to the end of the street and back after dinner", { ok: false, error: "too-long" }],
    ["Read twenty pages before bed every night", { ok: true, name: "Read twenty pages before bed every night" }],
    ["Read twenty pages before bed every night.", { ok: false, error: "too-long" }],
    ["  Drink water  ", { ok: true, name: "Drink water" }],
    ["read 20 pages", { ok: false, error: "duplicate" }],
    [" STRETCH 10 MINUTES ", { ok: false, error: "duplicate" }],
    ["Read 20 pages", { ok: false, error: "duplicate" }],
  ];
  for (const [raw, result] of rows) {
    assert.deepEqual(validateName(raw, EXISTING_NAMES), result, JSON.stringify(raw));
  }
});

test("@R13 the length rule counts the trimmed name, so padding never makes a 40 character name too long", () => {
  const forty = "Read twenty pages before bed every night";
  assert.equal(Array.from(forty).length, 40);
  assert.deepEqual(validateName(`   ${forty}   `, []), { ok: true, name: forty });
});

test("@R13 too long is checked before duplicate", () => {
  const long = "Read twenty pages before bed every night.";
  assert.deepEqual(validateName(long, [long]), { ok: false, error: "too-long" });
});

test("@R13 length counts code points, not UTF-16 units", () => {
  assert.equal(FORTY_EMOJI.length, 80);
  assert.deepEqual(validateName(FORTY_EMOJI, []), { ok: true, name: FORTY_EMOJI });
  assert.deepEqual(validateName(`${FORTY_EMOJI}\u{1F4DA}`, []), { ok: false, error: "too-long" });
});

test("@R13 trim removes no-break space, em space and BOM as well as plain spaces, and the duplicate check lower-cases both sides", () => {
  assert.deepEqual(validateName("\u00A0\u2003Drink water\uFEFF ", []), { ok: true, name: "Drink water" });
  assert.deepEqual(validateName("Étude", ["éTUDE"]), { ok: false, error: "duplicate" });
});

test("@R13 a very long name is rejected without hanging", () => {
  const started = performance.now();
  assert.deepEqual(validateName("x".repeat(1_000_000), EXISTING_NAMES), { ok: false, error: "too-long" });
  assert.ok(performance.now() - started < 1000);
});

test("@R14 a new habit goes to the bottom", () => {
  const input = sampleHabits();
  const result = addHabit(input, "  Drink water  ");
  assert.equal(result.ok, true);
  assert.deepEqual(
    result.habits.map((habit) => habit.name),
    [...EXISTING_NAMES, "Drink water"],
  );
  assert.deepEqual(result.habits[3], { name: "Drink water", done: [] });
  assert.deepEqual(result.habits.slice(0, 3), sample.habits);
  assert.notEqual(result.habits, input);
  result.habits.forEach((habit, position) => {
    if (position < 3) assert.notEqual(habit, input[position], `habit ${position} is a new object`);
  });
  assert.deepEqual(input, sample.habits);
});

test("@R14 a rejected name returns its error", () => {
  assert.deepEqual(addHabit(sampleHabits(), "read 20 pages"), { ok: false, error: "duplicate" });
  assert.deepEqual(addHabit(sampleHabits(), "   "), { ok: false, error: "empty" });
  assert.deepEqual(addHabit(sampleHabits(), "x".repeat(41)), { ok: false, error: "too-long" });
});

test("@R14 the limit of 12 habits is checked before the name", () => {
  const listOf = (count) => Array.from({ length: count }, (_, i) => ({ name: `Habit ${i + 1}`, done: [] }));

  const eleven = addHabit(listOf(11), "Habit 12");
  assert.equal(eleven.ok, true);
  assert.equal(eleven.habits.length, 12);
  assert.equal(eleven.habits.at(-1).name, "Habit 12");

  assert.deepEqual(addHabit(listOf(12), "Habit 13"), { ok: false, error: "limit" });
  assert.deepEqual(addHabit(listOf(12), ""), { ok: false, error: "limit" });
  assert.deepEqual(addHabit(listOf(12), "Habit 1"), { ok: false, error: "limit" });
  assert.deepEqual(addHabit(listOf(13), "Habit 14"), { ok: false, error: "limit" });
  assert.deepEqual(addHabit(listOf(11), ""), { ok: false, error: "empty" });
});

test("@R14 adding to an empty list works", () => {
  assert.deepEqual(addHabit([], " Run "), { ok: true, habits: [{ name: "Run", done: [] }] });
});

test("@R15 deleting a habit", () => {
  const rows = [
    [0, ["Stretch 10 minutes", "No phone after 11pm"]],
    [2, ["Read 20 pages", "Stretch 10 minutes"]],
    [1, ["Read 20 pages", "No phone after 11pm"]],
    [3, EXISTING_NAMES],
    [-1, EXISTING_NAMES],
    [0.5, EXISTING_NAMES],
    [Number.NaN, EXISTING_NAMES],
    [undefined, EXISTING_NAMES],
  ];
  for (const [index, names] of rows) {
    const input = sampleHabits();
    const result = deleteHabit(input, index);
    const label = `index ${index}`;
    assert.deepEqual(result.map((habit) => habit.name), names, label);
    result.forEach((habit) => {
      const original = input.find((candidate) => candidate.name === habit.name);
      assert.deepEqual(habit, original, `${label} ${habit.name} keeps its done days`);
      assert.notEqual(habit, original, `${label} ${habit.name} is a new object`);
    });
    assert.notEqual(result, input, label);
    assert.deepEqual(input, sample.habits, `${label} input unchanged`);
  }
});

test("@R15 deleting from an empty list returns an empty list", () => {
  assert.deepEqual(deleteHabit([], 0), []);
});
