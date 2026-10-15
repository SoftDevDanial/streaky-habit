import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { Worker } from "node:worker_threads";
import sample from "./fixtures/sample-history-v1.0.0.json" with { type: "json" };
import {
  MAX_HABITS,
  MAX_NAME_LENGTH,
  currentStreak,
  bestStreak,
  toggleDay,
  heatmapCells,
  monthLabels,
  yearStart,
  doneFlags,
  yearMonths,
  validateName,
  addHabit,
  deleteHabit,
} from "../src/habits.js";
import { addDays, dayParts, isDateKey, monthTitle, weekdayIndex } from "../src/dates.js";

const TODAY = "2026-10-08";
const YEAR_START = "2025-10-08";
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
// killed at the cap. A regression then fails the test instead of hanging the suite. The arguments go in
// on stdin, because a long input does not fit on a command line.
const WALK_CAP_MS = 5_000;
function streakInChild(name, ...args) {
  const habitsUrl = new URL("../src/habits.js", import.meta.url).href;
  const program = `
    const { ${name} } = await import(${JSON.stringify(habitsUrl)});
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    process.stdout.write(JSON.stringify(${name}(...JSON.parse(Buffer.concat(chunks).toString("utf8")))));
  `;
  try {
    return JSON.parse(
      execFileSync(process.execPath, ["--input-type=module", "--eval", program], {
        input: JSON.stringify(args),
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

// Near 2^53 days, floating-point rounding makes adding one day return the same key, so the day after
// FAR_START is FAR_STUCK and the day after FAR_STUCK is itself. The app's decoder treats saved data
// holding such a key as unreadable, because it fails isDateKey, but the streaks must still end, and
// count only valid days, if one gets through.
const FAR_START = "24660873954866-12-02";
const FAR_STUCK = "24660873954866-12-04";

test("@R7 the best-run walk ends on keys outside the valid range, where the next day repeats itself", () => {
  assert.equal(addDays(FAR_START, 1), FAR_STUCK, "precondition: the run start's next day is the stuck key");
  assert.equal(addDays(FAR_STUCK, 1), FAR_STUCK, "precondition: the stuck key's next day is itself");
  assert.ok(![FAR_START, FAR_STUCK].includes(addDays(FAR_START, -1)), "precondition: the run start begins a run");

  const best = streakInChild("bestStreak", [FAR_START, FAR_STUCK]);
  assert.ok(Number.isInteger(best) && best >= 0 && best <= 2, `bestStreak gave ${best}, more than the 2 distinct days`);
});

test("@R6 the current-run walk ends on the cycle below year 0001", () => {
  // Year -1 is written "00-1", so the day before 0000-01-01 reads back as 0000-01-12, and going back
  // from 0000-01-03 returns to it after 12 days.
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

// parseKey reads each part with Number(), which ignores white space, so FAR_START has thousands of
// spellings. Each is a separate key whose previous day is absent, so each starts its own run.
// After the empty string, a space and a tab come the no-break space, the em space, the ideographic
// space and the byte order mark. They are escapes because written raw they read as a plain space.
const WHITE_SPACE = ["", " ", "\t", "\u{A0}", "\u{2003}", "\u{3000}", "\u{FEFF}"];
function spellingsOfFarStart(count) {
  const [year, month, day] = FAR_START.split("-");
  const keys = [];
  for (let i = 0; keys.length < count; i++) {
    const space = (place) => WHITE_SPACE[Math.floor(i / WHITE_SPACE.length ** place) % WHITE_SPACE.length];
    const key = `${space(5)}${year}${space(4)}-${space(3)}${month}${space(2)}-${space(1)}${day}${space(0)}`;
    if (key !== FAR_START) keys.push(key);
  }
  return keys;
}

test("@R7 many spellings of one far-out date that all run into the stuck key cost one pass, not one walk each", () => {
  const spellings = spellingsOfFarStart(20_000);
  const before = addDays(FAR_START, -1);
  assert.equal(new Set(spellings).size, 20_000, "precondition: 20,000 distinct keys");
  assert.ok(spellings.every((key) => !isDateKey(key)), "precondition: every spelling fails isDateKey");
  assert.ok(spellings.every((key) => addDays(key, 1) === FAR_STUCK), "precondition: every spelling's next day is the stuck key");
  assert.ok(spellings.every((key) => addDays(key, -1) === before), "precondition: every spelling has the same previous day");
  assert.ok(!spellings.includes(before), "precondition: that previous day is absent, so every spelling starts a run");

  assert.equal(streakInChild("bestStreak", [...spellings, FAR_STUCK]), 0);
});

test("@R6 @R7 keys that fail isDateKey do not count, so a streak counts only valid days", () => {
  assert.equal(streakInChild("bestStreak", ["2026-10-06", "2026-10-07", "2026-10-08", FAR_START, FAR_STUCK]), 3);

  // Going back from 0001-01-10 leaves the valid range after 10 days and then reaches the cycle below year 0001.
  const history = [];
  for (let key = "0001-01-10"; history.length < 400; key = addDays(key, -1)) history.push(key);
  assert.equal(history.filter(isDateKey).length, 10, "precondition: 10 valid days");
  assert.equal(streakInChild("currentStreak", history, "0001-01-10"), 10, "currentStreak");
  assert.equal(streakInChild("bestStreak", history), 10, "bestStreak");
});

test("@R9 ticking a day in the last week of the year", () => {
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

test("@R9 days outside the year, bad dates and bad indexes change nothing", () => {
  const rows = [
    [0, "2025-10-07"],
    [1, "2026-10-09"],
    [2, "2026-02-30"],
    [1, "2026-1-5"],
    [1, "not a date"],
    [1, undefined],
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

test("@R9 any day of the last 12 months can be ticked, even before the habit's history", () => {
  const rows = [
    [0, "2026-10-01", false],
    [1, YEAR_START, true],
    [2, "2026-01-15", true],
  ];
  for (const [index, date, nowContains] of rows) {
    const input = sampleHabits();
    const result = toggleDay(input, index, date, TODAY);
    const label = `index ${index} date ${date}`;
    assert.equal(result[index].done.includes(date), nowContains, label);
    assert.ok(isAscendingUnique(result[index].done), label);
    result.forEach((habit, position) => {
      if (position !== index) assert.deepEqual(habit, input[position], `${label} other ${position}`);
    });
  }
});

test("@R9 both ends of the year are editable and ticking twice restores the habit", () => {
  for (const date of [YEAR_START, TODAY]) {
    const input = sampleHabits();
    const once = toggleDay(input, 2, date, TODAY);
    const twice = toggleDay(once, 2, date, TODAY);
    assert.notDeepEqual(once[2].done, input[2].done, date);
    assert.deepEqual(twice, input, date);
  }
});

test("@R9 @R18 on 29 February the year starts on 28 February and holds 367 days", () => {
  const leapDay = "2028-02-29";
  const input = [{ name: "A", done: [] }];
  assert.deepEqual(toggleDay(input, 0, "2027-02-28", leapDay)[0].done, ["2027-02-28"]);
  assert.deepEqual(toggleDay(input, 0, "2027-02-27", leapDay), input);
  assert.deepEqual(toggleDay(input, 0, "2028-03-01", leapDay), input);
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
      assert.deepEqual([cell.done, cell.count], [null, null], `${today} future ${cell.key}`);
    }
    assert.ok(cells.filter((cell) => !cell.future).every((cell) => cell.key <= today), today);

    const todays = cells.filter((cell) => cell.today);
    assert.equal(todays.length, 1, today);
    assert.equal(todays[0].key, today, today);

    for (const cell of cells.filter((c) => !c.future)) {
      assert.deepEqual([cell.done, cell.count, cell.total], [[], 0, 0], `${today} ${cell.key}`);
    }
    for (const cell of cells) assert.equal("level" in cell, false, `${today} ${cell.key} has no level`);
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
    done: [true, true, false],
    count: 2,
    total: 3,
  });
  assert.deepEqual(cells[11 * 7 + 4], {
    key: "2026-10-09",
    column: 12,
    row: 5,
    today: false,
    future: true,
    done: null,
    count: null,
    total: 3,
  });
});

test("@R10 a fourth habit counts in total and in done", () => {
  const habits = [...sampleHabits(), { name: "Drink water", done: [] }];
  const byKey = new Map(heatmapCells(habits, TODAY).map((cell) => [cell.key, cell]));
  const rows = [
    ["2026-07-20", 3],
    ["2026-10-06", 3],
    ["2026-10-08", 2],
    ["2026-07-21", 1],
    ["2026-08-12", 0],
  ];
  for (const [key, count] of rows) {
    const cell = byKey.get(key);
    assert.deepEqual([cell.count, cell.total], [count, 4], key);
    assert.equal(cell.done.length, 4, `${key} done has one value per habit`);
    assert.equal(cell.done[3], false, `${key} the fourth habit is not done`);
    assert.equal(cell.done.filter(Boolean).length, count, `${key} count is the number of true values`);
  }
});

test("@R10 @R19 a cell's done is doneFlags of its day", () => {
  const habits = sampleHabits();
  for (const cell of heatmapCells(habits, TODAY).filter((c) => !c.future)) {
    assert.deepEqual(cell.done, doneFlags(habits, cell.key), cell.key);
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

test("@R18 the same date last year, and the year's day count", () => {
  const rows = [
    ["2026-10-10", "2025-10-10", 366],
    ["2026-01-01", "2025-01-01", 366],
    ["2027-03-01", "2026-03-01", 366],
    ["2028-03-01", "2027-03-01", 367],
    ["2028-02-29", "2027-02-28", 367],
  ];
  for (const [today, start, days] of rows) {
    assert.equal(yearStart(today), start, today);
    let length = 1;
    for (let key = start; key < today; key = addDays(key, 1)) length++;
    assert.equal(length, days, `${today} days from ${start}`);
  }
});

const SAMPLE_DAYS = {
  A: ["2026-10-07", "2026-10-08", "2026-10-08"],
  B: [],
  C: ["2026-10-08"],
};
const abc = () => Object.entries(SAMPLE_DAYS).map(([name, done]) => ({ name, done: [...done] }));

test("@R19 which habits are done on a day, one boolean per habit in list order", () => {
  const habits = abc();
  assert.deepEqual(doneFlags(habits, "2026-10-08"), [true, false, true]);
  assert.deepEqual(doneFlags(habits, "2026-10-07"), [true, false, false]);
  assert.deepEqual(doneFlags(habits, "2026-10-09"), [false, false, false]);
  assert.deepEqual(abc(), habits, "habits unchanged");
});

test("@R19 no habits gives an empty list, and every call returns a new array", () => {
  assert.deepEqual(doneFlags([], "2026-10-08"), []);
  const habits = abc();
  assert.notEqual(doneFlags(habits, "2026-10-08"), doneFlags(habits, "2026-10-08"));
});

const pad2 = (number) => String(number).padStart(2, "0");
const MONTH_LENGTHS_2025_10_TO_2026_10 = [31, 30, 31, 31, 30, 31, 30, 31, 28, 31, 31, 30, 31];
const tally = (months) =>
  months.flatMap((month) => month.days).reduce((counts, { kind }) => ({ ...counts, [kind]: counts[kind] + 1 }), {
    open: 0,
    closed: 0,
    empty: 0,
  });

test("@R20 the year of the goldens", () => {
  const months = yearMonths("2026-10-10");
  assert.equal(months.length, 13);
  assert.deepEqual(
    months.map((month) => month.key),
    ["2026-10-01", "2026-09-01", "2026-08-01", "2026-07-01", "2026-06-01", "2026-05-01", "2026-04-01",
      "2026-03-01", "2026-02-01", "2026-01-01", "2025-12-01", "2025-11-01", "2025-10-01"],
  );
  assert.deepEqual(months.map((month) => month.days.length), MONTH_LENGTHS_2025_10_TO_2026_10);

  for (const month of months) {
    assert.equal(month.title, monthTitle(month.key), month.key);
    assert.equal(month.lead, weekdayIndex(month.key), `${month.key} lead`);
    month.days.forEach((day, position) => {
      assert.equal(day.day, position + 1, `${month.key} day number`);
      assert.equal(day.key, `${month.key.slice(0, 8)}${pad2(day.day)}`, `${month.key} day key`);
    });
  }
  assert.deepEqual(
    months.map((month) => [month.title, month.lead]).filter((_, position) => [0, 1, 2, 3, 12].includes(position)),
    [["October 2026", 3], ["September 2026", 1], ["August 2026", 5], ["July 2026", 2], ["October 2025", 2]],
  );
  assert.equal(months.reduce((sum, month) => sum + month.lead, 0), 39);

  const october = months[0].days.map((day) => day.kind);
  assert.deepEqual(october.slice(0, 10), Array(10).fill("open"));
  assert.deepEqual(october.slice(10), Array(21).fill("closed"));
  const oldOctober = months[12].days.map((day) => day.kind);
  assert.deepEqual(oldOctober.slice(0, 9), Array(9).fill("empty"));
  assert.deepEqual(oldOctober.slice(9), Array(22).fill("open"));
  assert.ok(months.slice(1, 12).every((month) => month.days.every((day) => day.kind === "open")));
  assert.deepEqual(tally(months), { open: 366, closed: 21, empty: 9 });
});

test("@R20 the year on other days", () => {
  const rows = [
    ["2026-11-01", "November 2026", "November 2025", { open: 366, closed: 29, empty: 0 }],
    ["2026-10-31", "October 2026", "October 2025", { open: 366, closed: 0, empty: 30 }],
    ["2028-02-29", "February 2028", "February 2027", { open: 367, closed: 0, empty: 27 }],
    ["2027-01-01", "January 2027", "January 2026", { open: 366, closed: 30, empty: 0 }],
  ];
  for (const [today, first, last, counts] of rows) {
    const months = yearMonths(today);
    assert.equal(months.length, 13, today);
    assert.equal(months[0].title, first, today);
    assert.equal(months[12].title, last, today);
    assert.deepEqual(tally(months), counts, today);
  }
  const leap = yearMonths("2028-02-29");
  assert.deepEqual(leap[0].days.map((day) => day.kind).slice(28), ["open"], "29 February 2028 is the last day and open");
  assert.deepEqual(leap[12].days.map((day) => day.kind).slice(26), ["empty", "open"], "27 February 2027 empty, 28 open");
});

test("@R20 every call returns new objects", () => {
  const first = yearMonths(TODAY);
  const second = yearMonths(TODAY);
  assert.deepEqual(first, second);
  assert.notEqual(first, second);
  assert.notEqual(first[0].days, second[0].days);
});

// A call that never ends would block this file's process for good, and its growing array would exhaust the process's
// memory, so each row runs yearMonths in a worker with a heap limit and a timer. A worker stopped by either fails its
// row, not the suite. The timer is many times what the 920-key row needs, so only a call that runs on reaches it.
// The worker's source is a string, so the test needs no second file, and it reaches the ES module through import().
const YEAR_MONTHS_HEAP_MB = 256;
const YEAR_MONTHS_TIMER_MS = 5_000;
const YEAR_MONTHS_WORKER = `
  const { parentPort, workerData } = require("node:worker_threads");
  import(workerData.habitsUrl).then(({ yearMonths }) => {
    parentPort.postMessage(workerData.keys.map((key) => {
      try {
        return { key, months: yearMonths(key).length };
      } catch (error) {
        return { key, threw: String(error) };
      }
    }));
  });
`;

/** `{ ended: true, results }` with one `{ key, months }` or `{ key, threw }` per key, or `{ ended: false, why }`. */
function yearMonthsInWorker(keys) {
  return new Promise((resolve) => {
    const worker = new Worker(YEAR_MONTHS_WORKER, {
      eval: true,
      workerData: { habitsUrl: new URL("../src/habits.js", import.meta.url).href, keys },
      resourceLimits: { maxOldGenerationSizeMb: YEAR_MONTHS_HEAP_MB },
    });
    let results = null;
    let stoppedBy = null;
    const timer = setTimeout(() => {
      stoppedBy = `stopped by the timer at ${YEAR_MONTHS_TIMER_MS} ms`;
      worker.terminate();
    }, YEAR_MONTHS_TIMER_MS);
    worker.on("message", (message) => {
      results = message;
    });
    worker.on("error", (error) => {
      stoppedBy = error.code === "ERR_WORKER_OUT_OF_MEMORY" ? `stopped by the heap limit of ${YEAR_MONTHS_HEAP_MB} MB` : `failed, ${error}`;
    });
    worker.on("exit", (code) => {
      clearTimeout(timer);
      if (stoppedBy !== null || code !== 0 || results === null) {
        resolve({ ended: false, why: stoppedBy ?? `exit code ${code}, ${results === null ? "nothing posted" : "a result posted"}` });
      } else {
        resolve({ ended: true, results });
      }
    });
  });
}

// Every day of October, November and December of the years 10000 to 10009, written as localDateKey writes them.
function farQuarterKeys() {
  const keys = [];
  for (let year = 10000; year <= 10009; year++) {
    for (const [month, length] of [[10, 31], [11, 30], [12, 31]]) {
      for (let day = 1; day <= length; day++) keys.push(`${year}-${pad2(month)}-${pad2(day)}`);
    }
  }
  return keys;
}

const OUTCOMES = {
  "it returned 13 months": ({ months }) => months === 13,
  "it returned at most 13 months": ({ months }) => months <= 13,
  "it returned at most 13 months for each key": ({ months }) => months <= 13,
  "it returned at most 13 months or threw": ({ months, threw }) => threw !== undefined || months <= 13,
};

test("@R20 yearMonths ends for every key and returns at most 13 months", async (t) => {
  const farKeys = farQuarterKeys();
  assert.equal(new Set(farKeys).size, 920, "precondition: 920 distinct keys");
  assert.ok(farKeys.every((key) => !isDateKey(key)), "precondition: every one of them fails isDateKey");

  const one = (today, outcome) => [today, [today], outcome];
  const rows = [
    one("2026-10-10", "it returned 13 months"),
    one("0001-01-01", "it returned 13 months"),
    one("9999-12-31", "it returned 13 months"),
    one("10000-10-01", "it returned at most 13 months"),
    one("10000-10-15", "it returned at most 13 months"),
    one("10000-12-31", "it returned at most 13 months"),
    one("10005-11-20", "it returned at most 13 months"),
    one("10009-10-01", "it returned at most 13 months"),
    one("10009-12-31", "it returned at most 13 months"),
    ["every day of October, November and December of the years 10000 to 10009 (920 keys)", farKeys,
      "it returned at most 13 months for each key"],
    one("10000-01-05", "it returned at most 13 months or threw"),
    one("10010-10-15", "it returned at most 13 months or threw"),
    one("100000-10-15", "it returned at most 13 months or threw"),
  ];
  for (const [today, keys, outcome] of rows) {
    await t.test(`${today}, ${outcome}`, async () => {
      const run = await yearMonthsInWorker(keys);
      assert.ok(run.ended, `did not end, ${run.why}`);
      assert.equal(run.results.length, keys.length, "one result per key");
      const broken = run.results.filter((result) => !OUTCOMES[outcome](result));
      assert.deepEqual(broken, [], `${broken.length} of ${keys.length} keys break "${outcome}"`);
    });
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

// Counts the steps a call takes through string iterators, which Array.from and for...of both use. Each
// step reads one code point, and a walk to the end takes one more step to find the end, so the count
// shows whether the length check stops early or walks the whole name.
function iteratorSteps(run) {
  const native = String.prototype[Symbol.iterator];
  let steps = 0;
  String.prototype[Symbol.iterator] = function () {
    const iterator = native.call(this);
    return {
      next: () => {
        steps++;
        return iterator.next();
      },
    };
  };
  try {
    return { result: run(), steps };
  } finally {
    String.prototype[Symbol.iterator] = native;
  }
}

test("@R13 the length check reads at most 41 code points, so a huge stored name costs no more than a short one", () => {
  assert.equal(iteratorSteps(() => Array.from("abc")).steps, 4, "precondition: the counter sees 3 code points and the end");
  const huge = {
    "5,000,000 CJK units": "一".repeat(5_000_000),
    "5,000,000 emoji units": "\u{1F4DA}".repeat(2_500_000),
    "41 lone surrogates": "\uD800".repeat(41),
  };
  for (const [label, name] of Object.entries(huge)) {
    const { result, steps } = iteratorSteps(() => validateName(name, EXISTING_NAMES));
    assert.deepEqual(result, { ok: false, error: "too-long" }, label);
    assert.ok(steps <= MAX_NAME_LENGTH + 1, `${label}: ${steps} iterator steps`);
  }
  assert.deepEqual(validateName("\uD800".repeat(40), []), { ok: true, name: "\uD800".repeat(40) }, "40 lone surrogates");
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
