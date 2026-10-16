/**
 * Streaks, the editable year, the 12-week overview and habit-list rules.
 * Why: the app needs these as pure functions of habit data and a passed-in day, so they can be
 * proved without a browser or a clock. Input: valid habits and date keys. Output: new values only,
 * the arguments are never changed.
 */
import { addDays, dayParts, isDateKey, monthTitle, weekdayIndex } from "./dates.js";

/** @typedef {import("./dates.js").DateKey} DateKey */
/** @typedef {{ name: string, done: DateKey[] }} Habit  done ascending, no duplicates */
/**
 * @typedef {{ key: DateKey, column: number, row: number, today: boolean, future: boolean,
 *             done: boolean[] | null, count: number | null, total: number }} HeatCell
 */
/** @typedef {{ column: number, month: string }} MonthLabel */
/** @typedef {{ key: DateKey, day: number, kind: "open" | "closed" | "empty" }} YearDay */
/** @typedef {{ key: DateKey, title: string, lead: 0 | 1 | 2 | 3 | 4 | 5 | 6, days: YearDay[] }} YearMonth */
/** @typedef {{ ok: true, name: string } | { ok: false, error: "empty" | "too-long" | "duplicate" }} NameCheck */
/**
 * @typedef {{ ok: true, habits: Habit[] } | { ok: false, error: "limit" | "empty" | "too-long" | "duplicate" }} AddResult
 */

export const MAX_HABITS = 12;
export const MAX_NAME_LENGTH = 40;

const DAYS_PER_WEEK = 7;
const YEAR_WIDTH = "YYYY".length;
const MONTH_PREFIX_WIDTH = "YYYY-MM".length;
const LEAP_DAY = "-02-29";
const DAY_BEFORE_LEAP_DAY = "-02-28";
const HEATMAP_WEEKS = 12;
const YEAR_VIEW_MONTHS = 13;
const PREVIOUS_DAY = -1;
const NEXT_DAY = 1;

/** Rebuilt from the two known fields, so no extra key from stored data is carried into new state. */
function copyHabit(habit) {
  return { name: habit.name, done: [...habit.done] };
}

/**
 * The days a streak may count: only keys that pass `isDateKey`. Each valid day has one spelling, and
 * inside the valid range `addDays` never repeats a key, so every run is walked once, ends at its first
 * day not in the set, and the total work stays linear. This filter is the only thing that ends the
 * walks: outside the range `addDays` can return a key it already returned, and many spellings of one
 * far-out date could each start such a walk.
 */
function streakDays(done) {
  return new Set(done.filter(isDateKey));
}

/**
 * One run counter for both streaks, so current and best count a run the same way. `step` is 1 or -1.
 * `days` must come from `streakDays`: that is why this walk needs no bound of its own.
 */
function runLength(days, from, step) {
  let length = 0;
  for (let key = from; days.has(key); key = addDays(key, step)) length++;
  return length;
}

/**
 * Counting starts at yesterday while today is open, so a streak does not break until today is over.
 * Days after `todayKey` are never reached because the count only moves backwards.
 * @param {readonly DateKey[]} done any order, duplicates allowed, keys that fail `isDateKey` ignored
 * @param {DateKey} todayKey
 * @returns {number}
 */
export function currentStreak(done, todayKey) {
  const days = streakDays(done);
  const start = days.has(todayKey) ? todayKey : addDays(todayKey, PREVIOUS_DAY);
  return runLength(days, start, PREVIOUS_DAY);
}

/**
 * Longest run over the whole history, entries after today included. Each run is measured once,
 * from its first day, so the cost stays linear.
 * @param {readonly DateKey[]} done any order, duplicates allowed, keys that fail `isDateKey` ignored
 * @returns {number} 0 when `done` holds no valid key
 */
export function bestStreak(done) {
  const days = streakDays(done);
  let best = 0;
  for (const key of days) {
    if (!days.has(addDays(key, PREVIOUS_DAY))) best = Math.max(best, runLength(days, key, NEXT_DAY));
  }
  return best;
}

/**
 * The first day of the editable year, "today back to the same date last year". 29 February is the
 * one date whose twin may not exist (two years in a row are never both leap), and it falls back to
 * 28 February (CG-13). The key's year part is fixed width, so the text is rebuilt, not recounted.
 * @param {DateKey} todayKey
 * @returns {DateKey}
 */
export function yearStart(todayKey) {
  const previousYear = String(Number(todayKey.slice(0, YEAR_WIDTH)) - 1).padStart(YEAR_WIDTH, "0");
  const monthAndDay = todayKey.slice(YEAR_WIDTH);
  return `${previousYear}${monthAndDay === LEAP_DAY ? DAY_BEFORE_LEAP_DAY : monthAndDay}`;
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
 * Enforces "only the year from `yearStart(todayKey)` to today can be changed" where the data
 * changes, not in the screen. A date outside it, a string that is not a real day or an index that is
 * no habit changes nothing and still returns a new array. Date keys sort as text in calendar order,
 * and `isDateKey` runs first so only well-formed keys are compared.
 * @param {readonly Habit[]} habits
 * @param {number} index
 * @param {DateKey} dateKey
 * @param {DateKey} todayKey
 * @returns {Habit[]}
 */
export function toggleDay(habits, index, dateKey, todayKey) {
  const editable = isDateKey(dateKey) && dateKey >= yearStart(todayKey) && dateKey <= todayKey;
  return habits.map((habit, position) =>
    editable && position === index ? toggledHabit(habit, dateKey) : copyHabit(habit),
  );
}

/**
 * The one answer to "which habits are done on this day", so the overview cells, the rings and the
 * day editor cannot disagree. One `includes` per habit, so a call reads each `done` once.
 * @param {readonly Habit[]} habits
 * @param {DateKey} dateKey
 * @returns {boolean[]} one value per habit, in list order
 */
export function doneFlags(habits, dateKey) {
  return habits.map((habit) => habit.done.includes(dateKey));
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
  return key.slice(0, MONTH_PREFIX_WIDTH);
}

/**
 * The 12-week grid in the order the screen lays it out. Future days carry null so the screen can
 * leave them blank instead of drawing an empty ring for a day that has not happened.
 * @param {readonly Habit[]} habits
 * @param {DateKey} todayKey
 * @returns {HeatCell[]} 84 cells, column-major, row 1 is Monday
 */
export function heatmapCells(habits, todayKey) {
  const total = habits.length;
  return columnMondays(todayKey).flatMap((monday, columnIndex) =>
    Array.from({ length: DAYS_PER_WEEK }, (_, rowIndex) => {
      const key = addDays(monday, rowIndex);
      const future = key > todayKey; // date keys sort as text in calendar order
      const done = future ? null : doneFlags(habits, key);
      return {
        key,
        column: columnIndex + 1,
        row: rowIndex + 1,
        today: key === todayKey,
        future,
        done,
        count: done === null ? null : done.filter(Boolean).length,
        total,
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

/** The first day of the month `key` is in. */
function monthStart(key) {
  return `${calendarMonth(key)}-01`;
}

/** "empty" before the year starts, "closed" after today, "open" between, so one list draws blanks, locked and tappable cells. */
function dayKind(key, firstDay, todayKey) {
  if (key < firstDay) return "empty";
  return key > todayKey ? "closed" : "open";
}

function yearMonth(start, firstDay, todayKey) {
  const days = [];
  for (let key = start; calendarMonth(key) === calendarMonth(start); key = addDays(key, 1)) {
    days.push({ key, day: dayParts(key).day, kind: dayKind(key, firstDay, todayKey) });
  }
  return { key: start, title: monthTitle(start), lead: weekdayIndex(start), days };
}

/**
 * The calendar of both year views, newest month first, from today's month back to the month of
 * `yearStart`. For a key that passes `isDateKey` that is 13 months, because the start is the same month
 * one year earlier. The walk also stops after 13 months, because a key from a clock past the year 9999 can
 * give `yearStart` a month the walk never writes, and the walk would then never end (R20, SEC-R01).
 * @param {DateKey} todayKey
 * @returns {YearMonth[]} 13 months for a key that passes `isDateKey`, never more than 13
 */
export function yearMonths(todayKey) {
  const firstDay = yearStart(todayKey);
  const months = [];
  let start = monthStart(todayKey);
  for (;;) {
    months.push(yearMonth(start, firstDay, todayKey));
    if (calendarMonth(start) === calendarMonth(firstDay) || months.length === YEAR_VIEW_MONTHS) return months;
    start = monthStart(addDays(start, -1));
  }
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
