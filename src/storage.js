/**
 * The saved state: one localStorage key holding the habits.
 * Why: the saved text is untrusted (any page on the same origin can write the key), so reading it is a
 * strict check that rebuilds every habit from the two known fields, and anything else is "unreadable".
 * Input: the raw saved text, or the habits to save. Output: habits, or a status (spec Storage contract, CG-4).
 * Storage failures never reach the user (CG-5): a failed read starts empty and a failed save is ignored.
 */
import { isDateKey } from "./dates.js";
import { MAX_HABITS, validateName } from "./habits.js";

export const STORAGE_KEY = "streaks.state";
const STORAGE_VERSION = 1;

/** @typedef {import("./habits.js").Habit} Habit */

const isRecord = (value) => value !== null && typeof value === "object" && !Array.isArray(value);

/**
 * One saved habit as a new `{ name, done }` literal (never the parsed object, so a `__proto__` key or any
 * extra property goes nowhere), or null when it breaks the name rules or holds a bad date.
 * The name must already be in the form `validateName` returns: trimmed, 1 to 40 code points, unique.
 */
function readHabit(entry, earlierNames) {
  if (!isRecord(entry) || typeof entry.name !== "string" || !Array.isArray(entry.done)) return null;
  const check = validateName(entry.name, earlierNames);
  if (!check.ok || check.name !== entry.name) return null;
  if (!entry.done.every((value) => isDateKey(value))) return null;
  return { name: entry.name, done: [...new Set(entry.done)].sort() };
}

function readHabits(list) {
  if (!Array.isArray(list) || list.length > MAX_HABITS) return null;
  const habits = [];
  for (const entry of list) {
    const habit = readHabit(entry, habits.map((existing) => existing.name));
    if (habit === null) return null;
    habits.push(habit);
  }
  return habits;
}

/**
 * @param {string | null} raw what `getItem` returned
 * @returns {{ status: "absent" } | { status: "ok", habits: Habit[] } | { status: "unreadable" }}
 */
export function decodeState(raw) {
  if (raw === null) return { status: "absent" };
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { status: "unreadable" };
  }
  if (!isRecord(parsed) || parsed.version !== STORAGE_VERSION) return { status: "unreadable" };
  const habits = readHabits(parsed.habits);
  return habits === null ? { status: "unreadable" } : { status: "ok", habits };
}

/** @param {readonly Habit[]} habits */
export function encodeState(habits) {
  return JSON.stringify({
    version: STORAGE_VERSION,
    habits: habits.map((habit) => ({ name: habit.name, done: habit.done })),
  });
}

/**
 * Never throws. Unreadable saved text is replaced by the empty state at once, so "the list was reset"
 * is true on the next load too, and `reset` tells the app to say so once.
 * @returns {{ habits: Habit[], reset: boolean }}
 */
export function loadHabits() {
  // Only the storage access is guarded: a throw from decodeState is a bug and must not read as "storage
  // unusable", which would start empty without the note and let the next save overwrite the saved data.
  let raw;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch {
    return { habits: [], reset: false };
  }
  const decoded = decodeState(raw);
  if (decoded.status === "ok") return { habits: decoded.habits, reset: false };
  if (decoded.status === "absent") return { habits: [], reset: false };
  saveHabits([]);
  return { habits: [], reset: true };
}

/** @param {readonly Habit[]} habits */
export function saveHabits(habits) {
  try {
    localStorage.setItem(STORAGE_KEY, encodeState(habits));
  } catch {
    // Blocked or full storage: the change stays on screen and in memory (CG-5, an accepted residual).
  }
}
