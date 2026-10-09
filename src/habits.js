/**
 * Week strip, streak and habit-list rules.
 * Why: the app needs these as pure functions of habit data and a passed-in day, so they can be
 * proved without a browser or a clock. Input: valid habits and date keys. Output: new values only,
 * the arguments are never changed.
 */
import { addDays, dayParts } from "./dates.js";

/** @typedef {import("./dates.js").DateKey} DateKey */
/** @typedef {{ name: string, done: DateKey[] }} Habit  done ascending, no duplicates */
/**
 * @typedef {{ key: DateKey, column: number, row: number, today: boolean, future: boolean,
 *             count: number | null, total: number, level: 0 | 1 | 2 | 3 | 4 | null }} HeatCell
 */
/** @typedef {{ column: number, month: string }} MonthLabel */

export const MAX_HABITS = 12;
export const MAX_NAME_LENGTH = 40;

const WEEK_LENGTH = 7;
const HEATMAP_WEEKS = 12;
const MONDAY = "Mon";
const PREVIOUS_DAY = -1;
const NEXT_DAY = 1;

/** Habits are rebuilt as literals, never spread, so a key from stored data cannot reach the prototype. */
function copyHabit(habit) {
  return { name: habit.name, done: [...habit.done] };
}

/** One run counter for both streaks, so current and best count a run the same way. `step` is 1 or -1. */
function runLength(days, from, step) {
  let length = 0;
  for (let key = from; days.has(key); key = addDays(key, step)) length++;
  return length;
}

/**
 * The seven days of the strip, so the strip and the editable range are one definition.
 * @param {DateKey} todayKey
 * @returns {DateKey[]} oldest first, today last
 */
export function weekWindow(todayKey) {
  return Array.from({ length: WEEK_LENGTH }, (_, position) => addDays(todayKey, position + 1 - WEEK_LENGTH));
}

/**
 * Counting starts at yesterday while today is open, so a streak does not break until today is over.
 * Days after `todayKey` are never reached because the count only moves backwards.
 * @param {readonly DateKey[]} done any order, duplicates allowed
 * @param {DateKey} todayKey
 * @returns {number}
 */
export function currentStreak(done, todayKey) {
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
  const firstDay = addDays(todayKey, 1 - WEEK_LENGTH);
  return days.has(firstDay) && days.has(addDays(firstDay, PREVIOUS_DAY));
}

/** Toggle through a Set so the stored array comes out ascending and without duplicates. */
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
 * The Monday that starts each heatmap column, oldest first. dates.js offers weekday names and no
 * index, so the Monday is found in the 7-day strip that ends on `todayKey`, which holds exactly one.
 */
function columnMondays(todayKey) {
  const currentMonday = weekWindow(todayKey).find((key) => dayParts(key).weekday === MONDAY);
  return Array.from({ length: HEATMAP_WEEKS }, (_, column) =>
    addDays(currentMonday, (column + 1 - HEATMAP_WEEKS) * WEEK_LENGTH),
  );
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
    Array.from({ length: WEEK_LENGTH }, (_, rowIndex) => {
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
 * Labels the first column of each month by its Monday, so a month that starts mid-column and has
 * no Monday of its own in the grid gets no label.
 * @param {DateKey} todayKey
 * @returns {MonthLabel[]}
 */
export function monthLabels(todayKey) {
  const months = columnMondays(todayKey).map((monday) => dayParts(monday).month);
  return months.flatMap((month, columnIndex) =>
    columnIndex === 0 || month !== months[columnIndex - 1] ? [{ column: columnIndex + 1, month }] : [],
  );
}
