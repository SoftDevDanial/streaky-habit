/**
 * Week strip, streaks, heatmap and habit-list rules.
 * Why: the app needs these as pure functions of habit data and a passed-in day, so they can be
 * proved without a browser or a clock. Input: valid habits and date keys. Output: new values only,
 * the arguments are never changed.
 */
import { addDays, dayParts, weekdayIndex, localDateKey } from "./dates.js";

/** @typedef {import("./dates.js").DateKey} DateKey */
/** @typedef {{ name: string, done: DateKey[] }} Habit  done ascending, no duplicates */
/**
 * @typedef {{ key: DateKey, column: number, row: number, today: boolean, future: boolean,
 *             count: number | null, total: number, level: 0 | 1 | 2 | 3 | 4 | null }} HeatCell
 */
/** @typedef {{ column: number, month: string }} MonthLabel */
/** @typedef {{ ok: true, name: string } | { ok: false, error: "empty" | "too-long" | "duplicate" }} NameCheck */
/**
 * @typedef {{ ok: true, habits: Habit[] } | { ok: false, error: "limit" | "empty" | "too-long" | "duplicate" }} AddResult
 */

export const MAX_HABITS = 12;
export const MAX_NAME_LENGTH = 40;

// Both 7, kept apart: the strip's width is a design choice, the week's length is a calendar fact.
const STRIP_DAYS = 7;
const DAYS_PER_WEEK = 7;
const HEATMAP_WEEKS = 12;
const PREVIOUS_DAY = -1;
const NEXT_DAY = 1;

/** Rebuilt from the two known fields, so no extra key from stored data is carried into new state. */
function copyHabit(habit) {
  return { name: habit.name, done: [...habit.done] };
}

/**
 * One run counter for both streaks, so current and best count a run the same way. `step` is 1 or -1.
 * A run never holds more days than the set, so the walk stops there. Outside the valid date range
 * `addDays` can return a key it already returned, and an unbounded walk would never end.
 */
function runLength(days, from, step) {
  let length = 0;
  for (let key = from; length < days.size && days.has(key); key = addDays(key, step)) length++;
  return length;
}

/**
 * The seven days of the strip. Every rule tied to the strip's span reads it from here, so they move together.
 * @param {DateKey} todayKey
 * @returns {DateKey[]} oldest first, today last
 */
export function weekWindow(todayKey) {
  return Array.from({ length: STRIP_DAYS }, (_, position) => addDays(todayKey, position + 1 - STRIP_DAYS));
}

/**
 * Counting starts at yesterday while today is open, so a streak does not break until today is over.
 * Days after `todayKey` are never reached because the count only moves backwards.
 * @param {readonly DateKey[]} done any order, duplicates allowed
 * @param {DateKey} todayKey
 * @returns {number}
 */
export function currentStreak(done, todayKey = localDateKey(new Date(Date()))) {
  const days = new Set(done);
  const start = days.has(todayKey) ? todayKey : addDays(todayKey, PREVIOUS_DAY);
  return runLength(days, start, PREVIOUS_DAY);
}

/**
 * Longest run over the whole history, entries after today included. Each run is measured once,
 * from its first day, so the cost stays linear.
 * @param {readonly DateKey[]} done any order, duplicates allowed
 * @returns {number} 0 when `done` is empty
 */
export function bestStreak(done) {
  const days = new Set(done);
  let best = 0;
  for (const key of days) {
    if (!days.has(addDays(key, PREVIOUS_DAY))) best = Math.max(best, runLength(days, key, NEXT_DAY));
  }
  return best;
}

/**
 * True when a run reaches into the strip from the left, which the strip draws as a thread running
 * off its edge.
 * @param {readonly DateKey[]} done
 * @param {DateKey} todayKey
 * @returns {boolean}
 */
export function runContinues(done, todayKey) {
  const days = new Set(done);
  const firstDay = weekWindow(todayKey)[0];
  return days.has(firstDay) && days.has(addDays(firstDay, PREVIOUS_DAY));
}

/**
 * The Set drops duplicates and the sort restores ascending order, so the stored array keeps the
 * Habit invariant.
 */
function toggledHabit(habit, dateKey) {
  const days = new Set(habit.done);
  if (days.has(dateKey)) days.delete(dateKey);
  else days.add(dateKey);
  return { name: habit.name, done: [...days].sort() };
}

/**
 * Enforces "only the last 7 days can be changed" where the data changes, not in the screen.
 * A date outside the strip or an index that is no habit changes nothing and still returns a new array.
 * @param {readonly Habit[]} habits
 * @param {number} index
 * @param {DateKey} dateKey
 * @param {DateKey} todayKey
 * @returns {Habit[]}
 */
export function toggleDay(habits, index, dateKey, todayKey) {
  const editable = weekWindow(todayKey).includes(dateKey);
  return habits.map((habit, position) =>
    editable && position === index ? toggledHabit(habit, dateKey) : copyHabit(habit),
  );
}

/**
 * Integer comparisons only, so a boundary such as 1 of 3 cannot flip on floating-point rounding.
 * Both thirds are inclusive, as the goldens require.
 * @param {number} count habits done that day
 * @param {number} total habits in the list
 * @returns {0 | 1 | 2 | 3 | 4}
 */
export function heatLevel(count, total) {
  if (count === 0 || total === 0) return 0;
  if (count === total) return 4;
  if (3 * count <= total) return 1;
  if (3 * count <= 2 * total) return 2;
  return 3;
}

/**
 * The Monday that starts each heatmap column, oldest first. Monday is weekday 0, so going back by
 * the index lands on it.
 */
function columnMondays(todayKey) {
  const currentMonday = addDays(todayKey, -weekdayIndex(todayKey));
  return Array.from({ length: HEATMAP_WEEKS }, (_, column) =>
    addDays(currentMonday, (column + 1 - HEATMAP_WEEKS) * DAYS_PER_WEEK),
  );
}

/** Date keys are fixed width, so the "YYYY-MM" prefix names the calendar month. */
function calendarMonth(key) {
  return key.slice(0, "YYYY-MM".length);
}

/** Habits done per day, built once so the 84 cells do not each scan every habit. */
function doneCountsByDay(habits) {
  const counts = new Map();
  for (const habit of habits) {
    for (const key of new Set(habit.done)) counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return counts;
}

/**
 * The 12-week grid in the order the screen lays it out. Future days carry null so the screen can
 * leave them blank instead of drawing a level 0 that never happened.
 * @param {readonly Habit[]} habits
 * @param {DateKey} todayKey
 * @returns {HeatCell[]} 84 cells, column-major, row 1 is Monday
 */
export function heatmapCells(habits, todayKey) {
  const counts = doneCountsByDay(habits);
  const total = habits.length;
  return columnMondays(todayKey).flatMap((monday, columnIndex) =>
    Array.from({ length: DAYS_PER_WEEK }, (_, rowIndex) => {
      const key = addDays(monday, rowIndex);
      const future = key > todayKey; // date keys sort as text in calendar order
      const count = future ? null : (counts.get(key) ?? 0);
      return {
        key,
        column: columnIndex + 1,
        row: rowIndex + 1,
        today: key === todayKey,
        future,
        count,
        total,
        level: future ? null : heatLevel(count, total),
      };
    }),
  );
}

/**
 * A month is labelled on the first column whose Monday is in it, so a month whose days all fall
 * after the last Monday of the grid gets no label.
 * @param {DateKey} todayKey
 * @returns {MonthLabel[]}
 */
export function monthLabels(todayKey) {
  const mondays = columnMondays(todayKey);
  return mondays.flatMap((monday, columnIndex) =>
    columnIndex === 0 || calendarMonth(monday) !== calendarMonth(mondays[columnIndex - 1])
      ? [{ column: columnIndex + 1, month: dayParts(monday).month }]
      : [],
  );
}

/**
 * True when `text` has more than `limit` code points. It stops reading at `limit + 1`, so a name planted
 * in storage at quota size costs no more than a short one. The string iterator yields the same code
 * points as `Array.from`, a lone surrogate counting as one.
 */
function longerThan(text, limit) {
  let count = 0;
  for (const _ of text) if (++count > limit) return true;
  return false;
}

/**
 * Trim first, then empty, too long, duplicate, so a name that is only spaces is "empty" and an
 * over-long copy of an existing name is "too-long". Length counts code points (CG-8): UTF-16
 * units would count one emoji as two, and grapheme counting needs Intl.
 * @param {string} raw text as typed
 * @param {readonly string[]} existingNames
 * @returns {NameCheck}
 */
export function validateName(raw, existingNames) {
  const name = raw.trim();
  if (name === "") return { ok: false, error: "empty" };
  if (longerThan(name, MAX_NAME_LENGTH)) return { ok: false, error: "too-long" };
  const lowered = name.toLowerCase();
  if (existingNames.some((existing) => existing.toLowerCase() === lowered)) {
    return { ok: false, error: "duplicate" };
  }
  return { ok: true, name };
}

/**
 * The limit is checked before the name, so a full list never reports a name problem.
 * New habits go to the bottom.
 * @param {readonly Habit[]} habits
 * @param {string} raw text as typed
 * @returns {AddResult}
 */
export function addHabit(habits, raw) {
  if (habits.length >= MAX_HABITS) return { ok: false, error: "limit" };
  const check = validateName(raw, habits.map((habit) => habit.name));
  if (!check.ok) return check;
  return { ok: true, habits: [...habits.map(copyHabit), { name: check.name, done: [] }] };
}

/**
 * An index that is no habit removes nothing, because no position equals it.
 * @param {readonly Habit[]} habits
 * @param {number} index
 * @returns {Habit[]}
 */
export function deleteHabit(habits, index) {
  return habits.filter((_, position) => position !== index).map(copyHabit);
}
