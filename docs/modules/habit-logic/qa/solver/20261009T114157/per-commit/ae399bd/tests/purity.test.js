import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import sample from "../docs/design/sample-history.json" with { type: "json" };
import * as dates from "../src/dates.js";
import * as habits from "../src/habits.js";

const readSource = (name) => readFileSync(new URL(`../src/${name}`, import.meta.url), "utf8");

// Two plain regular expressions are enough here: these files hold only label tables and date logic,
// with no string or regular expression literal that contains // or /*.
const withoutComments = (text) => text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

function deepFreeze(value) {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value).forEach(deepFreeze);
  }
  return value;
}

const SOURCES = { "dates.js": readSource("dates.js"), "habits.js": readSource("habits.js") };

test("@R16 the source has no clock read, even in a comment", () => {
  for (const [name, text] of Object.entries(SOURCES)) {
    assert.ok(!text.includes("Date.now("), `${name} Date.now(`);
    assert.doesNotMatch(text, /new\s+Date\s*\(\s*\)/, `${name} new Date()`);
  }
});

test("@R16 the code has no DOM, storage, global or locale access", () => {
  for (const [name, text] of Object.entries(SOURCES)) {
    const code = withoutComments(text);
    assert.doesNotMatch(code, /\b(document|window|localStorage|globalThis|Intl)\b/, name);
    assert.doesNotMatch(code, /\btoLocale\w*/, name);
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
  assert.deepEqual(Object.keys(dates).sort(), ["addDays", "dayParts", "isDateKey", "localDateKey", "longDate", "shortDate"]);
  assert.deepEqual(Object.keys(habits).sort(), [
    "MAX_HABITS",
    "MAX_NAME_LENGTH",
    "addHabit",
    "bestStreak",
    "currentStreak",
    "deleteHabit",
    "heatLevel",
    "heatmapCells",
    "monthLabels",
    "runContinues",
    "toggleDay",
    "validateName",
    "weekWindow",
  ]);
});

const TODAY = "2026-10-08";

// One call per exported function. The test below fails when an export has no entry here.
function callsWith(frozenHabits) {
  const frozenDone = frozenHabits[0].done;
  const frozenNames = deepFreeze(frozenHabits.map((habit) => habit.name));
  return {
    // A freeze does not stop a Date's setters, so the Date's value is compared before and after.
    localDateKey: () => {
      const date = Object.freeze(new Date(2026, 9, 8, 12));
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
    weekWindow: () => habits.weekWindow(TODAY),
    currentStreak: () => habits.currentStreak(frozenDone, TODAY),
    bestStreak: () => habits.bestStreak(frozenDone),
    runContinues: () => habits.runContinues(frozenDone, TODAY),
    toggleDay: () => [
      habits.toggleDay(frozenHabits, 1, TODAY, TODAY),
      habits.toggleDay(frozenHabits, 0, TODAY, TODAY),
      habits.toggleDay(frozenHabits, 0, "2026-10-01", TODAY),
      habits.toggleDay(frozenHabits, 7, TODAY, TODAY),
    ],
    heatmapCells: () => habits.heatmapCells(frozenHabits, TODAY),
    heatLevel: () => habits.heatLevel(2, 3),
    monthLabels: () => habits.monthLabels(TODAY),
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
