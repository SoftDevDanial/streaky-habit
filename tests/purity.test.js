import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import sample from "./fixtures/sample-history-v1.0.0.json" with { type: "json" };
import * as dates from "../src/dates.js";
import * as habits from "../src/habits.js";

const readSource = (name) => readFileSync(new URL(`../src/${name}`, import.meta.url), "utf8");

// One pass in source order, so a // or /* inside a string is not read as a comment, which would hide the
// code after it, and a quote inside a comment is not read as a string. Limit: a quote inside a regular
// expression literal is read as the start of a string.
const STRING_OR_COMMENT = /("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`)|\/\*[\s\S]*?\*\/|\/\/.*$/gm;
const withoutComments = (text) => text.replace(STRING_OR_COMMENT, (match, quoted) => quoted ?? "");

function deepFreeze(value) {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value).forEach(deepFreeze);
  }
  return value;
}

const SOURCES = { "dates.js": readSource("dates.js"), "habits.js": readSource("habits.js") };

// Matched on the whole text, so a comment must not spell one either, and on the code alone, which also
// finds a read that a comment splits, such as `new Date(/* today */)`. `new Date` with an argument,
// `Date.UTC` and `Temporal.PlainDate` arithmetic stay allowed, because they read no clock.
const CLOCK_AND_RANDOM_READS = {
  "Date.now": /Date\s*\.\s*now\b/,
  "new Date without an argument": /new\s+Date\b(?!\s*\(\s*[^\s)])/,
  "Date called as a function": /(?<![.\w$]|\bnew\s+)Date\s*\(/,
  "Temporal.Now": /\bTemporal\s*\.\s*Now\b/,
  "performance.now": /\bperformance\s*\.\s*now\b/,
  "Math.random": /\bMath\s*\.\s*random\b/,
};

// Matched on the code only, as whole words, so a comment may still say "the week window". Code built
// from a string at run time is banned too: a clock read spelled inside the string passes every pattern.
const BANNED_IN_CODE = {
  "DOM or global object": /\b(document|window|self|globalThis|navigator|process)\b/,
  storage: /\b(localStorage|sessionStorage|indexedDB|caches)\b/,
  network: /\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon)\b/,
  "dynamic import": /\bimport\s*\(/,
  "code built from a string": /\beval\b|\bFunction\s*\(/,
  timer: /\b(setTimeout|setInterval|setImmediate|queueMicrotask|requestAnimationFrame)\b/,
  "random source": /\bcrypto\b/,
  locale: /\bIntl\b|\btoLocale\w*/,
};

function assertNoClockRead(name, text) {
  for (const [form, source] of [["text", text], ["code", withoutComments(text)]]) {
    for (const [read, pattern] of Object.entries(CLOCK_AND_RANDOM_READS)) {
      assert.doesNotMatch(source, pattern, `${name} ${form}: ${read}`);
    }
  }
}

test("@R16 the source has no clock or random read, even in a comment", () => {
  for (const [name, text] of Object.entries(SOURCES)) assertNoClockRead(name, text);
});

/**
 * A Date that throws on every read of the device clock and builds any date it is given. While it stands in for
 * `globalThis.Date`, a clock read inside a function body throws, an aliased one (`const Clock = Date`) included, which
 * the source scan above cannot see and two calls in the same millisecond cannot tell apart.
 */
class ClockReadDate extends Date {
  constructor(...args) {
    if (args.length === 0) throw new Error("a clock read, new Date() with no argument");
    super(...args);
  }

  static now() {
    throw new Error("a clock read, Date.now()");
  }
}

test("@R20 @R16 yearMonths reads no clock, so two calls with one key give equal results", () => {
  const realDate = globalThis.Date;
  globalThis.Date = ClockReadDate;
  let first;
  let second;
  try {
    first = habits.yearMonths(TODAY);
    second = habits.yearMonths(TODAY);
  } finally {
    globalThis.Date = realDate;
  }
  assert.deepEqual(first, second);
});

test("@R16 the code has no DOM, storage, network, timer, global or locale access and builds no code from strings", () => {
  for (const [name, text] of Object.entries(SOURCES)) {
    const code = withoutComments(text);
    for (const [access, pattern] of Object.entries(BANNED_IN_CODE)) {
      assert.doesNotMatch(code, pattern, `${name}: ${access}`);
    }
  }
});

test("@R16 habits.js imports only ./dates.js and dates.js imports nothing", () => {
  const habitsCode = withoutComments(SOURCES["habits.js"]);
  const datesCode = withoutComments(SOURCES["dates.js"]);

  assert.equal(habitsCode.match(/\bimport\b/g).length, 1, "one import keyword in habits.js");
  const specifiers = [...habitsCode.matchAll(/^import\s[^;]*?from\s*["']([^"']+)["']/gm)].map((match) => match[1]);
  assert.deepEqual(specifiers, ["./dates.js"]);

  assert.doesNotMatch(datesCode, /\bimport\b/, "dates.js import");
  for (const code of [habitsCode, datesCode]) assert.doesNotMatch(code, /\brequire\s*\(/);
});

test("@R16 only the contracted names are exported", () => {
  assert.deepEqual(Object.keys(dates).sort(), [
    "addDays",
    "dayParts",
    "isDateKey",
    "localDateKey",
    "longDate",
    "monthTitle",
    "shortDate",
    "weekdayIndex",
    "yearDate",
  ]);
  assert.deepEqual(Object.keys(habits).sort(), [
    "MAX_HABITS",
    "MAX_NAME_LENGTH",
    "addHabit",
    "bestStreak",
    "currentStreak",
    "deleteHabit",
    "doneFlags",
    "heatmapCells",
    "monthLabels",
    "toggleDay",
    "validateName",
    "yearMonths",
    "yearStart",
  ]);
});

const TODAY = "2026-10-08";

// One call per exported function. The test below fails when an export has no entry here.
function callsWith(frozenHabits) {
  const frozenDone = frozenHabits[0].done;
  const frozenNames = deepFreeze(frozenHabits.map((habit) => habit.name));
  return {
    // A freeze does not stop a Date's setters, so the Date's value is compared before and after. Minutes,
    // seconds and milliseconds are not zero, so a setter that resets any one of them changes the value.
    localDateKey: () => {
      const date = Object.freeze(new Date(2026, 9, 8, 12, 34, 56, 789));
      const before = date.getTime();
      const key = dates.localDateKey(date);
      assert.equal(date.getTime(), before, "localDateKey left its Date unchanged");
      return key;
    },
    isDateKey: () => [dates.isDateKey(TODAY), dates.isDateKey(deepFreeze({}))],
    addDays: () => dates.addDays(TODAY, -6),
    dayParts: () => dates.dayParts(TODAY),
    shortDate: () => dates.shortDate(TODAY),
    longDate: () => dates.longDate(TODAY),
    weekdayIndex: () => dates.weekdayIndex(TODAY),
    yearDate: () => dates.yearDate(TODAY),
    monthTitle: () => dates.monthTitle(TODAY),
    currentStreak: () => habits.currentStreak(frozenDone, TODAY),
    bestStreak: () => habits.bestStreak(frozenDone),
    toggleDay: () => [
      habits.toggleDay(frozenHabits, 1, TODAY, TODAY),
      habits.toggleDay(frozenHabits, 0, TODAY, TODAY),
      habits.toggleDay(frozenHabits, 0, "2026-10-01", TODAY),
      habits.toggleDay(frozenHabits, 0, "2025-10-07", TODAY),
      habits.toggleDay(frozenHabits, 7, TODAY, TODAY),
    ],
    heatmapCells: () => habits.heatmapCells(frozenHabits, TODAY),
    monthLabels: () => habits.monthLabels(TODAY),
    yearStart: () => habits.yearStart(TODAY),
    doneFlags: () => habits.doneFlags(frozenHabits, TODAY),
    yearMonths: () => habits.yearMonths(TODAY),
    validateName: () => [
      habits.validateName("Drink water", frozenNames),
      habits.validateName("read 20 pages", frozenNames),
    ],
    addHabit: () => [
      habits.addHabit(frozenHabits, "Drink water"),
      habits.addHabit(frozenHabits, "read 20 pages"),
    ],
    deleteHabit: () => [habits.deleteHabit(frozenHabits, 0), habits.deleteHabit(frozenHabits, 9)],
  };
}

// A result that holds an input object is frozen. Finding nothing frozen proves every result is new.
function frozenPartsOf(value, path = "result") {
  if (value === null || typeof value !== "object") return [];
  const own = Object.isFrozen(value) ? [path] : [];
  return own.concat(Object.entries(value).flatMap(([key, child]) => frozenPartsOf(child, `${path}.${key}`)));
}

test("@R16 no exported function writes to its arguments or returns one of them", () => {
  const frozenHabits = deepFreeze(structuredClone(sample.habits));
  const calls = callsWith(frozenHabits);

  const exportedFunctions = [...Object.entries(dates), ...Object.entries(habits)]
    .filter(([, value]) => typeof value === "function")
    .map(([name]) => name);
  assert.deepEqual(exportedFunctions.sort(), Object.keys(calls).sort(), "every exported function is called");

  for (const [name, call] of Object.entries(calls)) {
    let result;
    assert.doesNotThrow(() => {
      result = call();
    }, name);
    assert.deepEqual(frozenPartsOf(result, name), [], `${name} returns only new objects`);
  }
  assert.deepEqual(frozenHabits, sample.habits, "the frozen sample still equals the file's habits");
});
