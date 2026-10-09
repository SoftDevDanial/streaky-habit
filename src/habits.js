/**
 * Week strip, streak and habit-list rules.
 * Why: the app needs these as pure functions of habit data and a passed-in day, so they can be
 * proved without a browser or a clock. Input: valid habits and date keys. Output: new values only,
 * the arguments are never changed.
 */
import { addDays } from "./dates.js";

/** @typedef {import("./dates.js").DateKey} DateKey */
/** @typedef {{ name: string, done: DateKey[] }} Habit  done ascending, no duplicates */

export const MAX_HABITS = 12;
export const MAX_NAME_LENGTH = 40;

const WEEK_LENGTH = 7;
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
