/**
 * Date keys and English date labels.
 * Why: every other function speaks in `YYYY-MM-DD` local calendar days, so the calendar arithmetic
 * and the label tables live here, free of clocks, time zones and locales.
 * Input: valid date keys (only `isDateKey` accepts arbitrary values). Output: new strings and objects.
 */

/** @typedef {string} DateKey  "YYYY-MM-DD", a local calendar day */

const KEY_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const ABBREVIATION_LENGTH = 3;
const THURSDAY_INDEX = 3;

function pad(number, width) {
  return String(number).padStart(width, "0");
}

function formatKey(year, month, day) {
  return `${pad(year, 4)}-${pad(month, 2)}-${pad(day, 2)}`;
}

function parseKey(key) {
  const [year, month, day] = key.split("-").map(Number);
  return { year, month, day };
}

function isLeapYear(year) {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}

function daysInMonth(year, month) {
  return month === 2 && isLeapYear(year) ? 29 : DAYS_IN_MONTH[month - 1];
}

/**
 * Whole days since 1970-01-01 for a proleptic Gregorian date (Hinnant's days_from_civil).
 * Why integers and not a Date: Date.UTC maps years 0 to 99 into the 1900s, and any Date maths
 * invites local-time steps that a DST change turns into 23 or 25 hour days.
 */
function daysFromCivil(year, month, day) {
  const shiftedYear = month <= 2 ? year - 1 : year;
  const era = Math.floor(shiftedYear / 400);
  const yearOfEra = shiftedYear - era * 400;
  const dayOfYear = Math.floor((153 * (month + (month > 2 ? -3 : 9)) + 2) / 5) + day - 1;
  const dayOfEra = yearOfEra * 365 + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100) + dayOfYear;
  return era * 146097 + dayOfEra - 719468;
}

/** Inverse of `daysFromCivil` (Hinnant's civil_from_days). */
function civilFromDays(daysSinceEpoch) {
  const shifted = daysSinceEpoch + 719468;
  const era = Math.floor(shifted / 146097);
  const dayOfEra = shifted - era * 146097;
  const yearOfEra = Math.floor(
    (dayOfEra - Math.floor(dayOfEra / 1460) + Math.floor(dayOfEra / 36524) - Math.floor(dayOfEra / 146096)) / 365,
  );
  const dayOfYear = dayOfEra - (365 * yearOfEra + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100));
  const monthIndex = Math.floor((5 * dayOfYear + 2) / 153);
  const month = monthIndex < 10 ? monthIndex + 3 : monthIndex - 9;
  const year = yearOfEra + era * 400 + (month <= 2 ? 1 : 0);
  return { year, month, day: dayOfYear - Math.floor((153 * monthIndex + 2) / 5) + 1 };
}

/**
 * The local calendar day of an instant. Local getters on purpose: the UTC date is the wrong day
 * for anyone whose offset moves the instant across midnight.
 * @param {Date} date
 * @returns {DateKey}
 */
export function localDateKey(date) {
  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());
}

/**
 * Strict check for text that comes from storage. The pattern is anchored and linear, so a hostile
 * string cannot cause backtracking.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isDateKey(value) {
  if (typeof value !== "string" || !KEY_PATTERN.test(value)) return false;
  const { year, month, day } = parseKey(value);
  return year >= 1 && month >= 1 && month <= 12 && day >= 1 && day <= daysInMonth(year, month);
}

/**
 * The key `days` calendar days after `key` (negative goes back), the same in every time zone.
 * @param {DateKey} key
 * @param {number} days
 * @returns {DateKey}
 */
export function addDays(key, days) {
  const { year, month, day } = parseKey(key);
  const next = civilFromDays(daysFromCivil(year, month, day) + days);
  return formatKey(next.year, next.month, next.day);
}

/** Full English names for a key. 1970-01-01 was a Thursday, which anchors the Monday-first index. */
function namesOf(key) {
  const { year, month, day } = parseKey(key);
  const weekdayIndex = (((daysFromCivil(year, month, day) + THURSDAY_INDEX) % 7) + 7) % 7;
  return { weekday: WEEKDAYS[weekdayIndex], day, month: MONTHS[month - 1] };
}

function joinLabel({ weekday, day, month }) {
  return `${weekday} ${day} ${month}`;
}

/**
 * Fixed-table parts, so labels never follow the device language.
 * @param {DateKey} key
 * @returns {{ weekday: string, day: number, month: string }} three-letter weekday and month
 */
export function dayParts(key) {
  const { weekday, day, month } = namesOf(key);
  return {
    weekday: weekday.slice(0, ABBREVIATION_LENGTH),
    day,
    month: month.slice(0, ABBREVIATION_LENGTH),
  };
}

/**
 * @param {DateKey} key
 * @returns {string} for example "Tue 6 Oct"
 */
export function shortDate(key) {
  return joinLabel(dayParts(key));
}

/**
 * @param {DateKey} key
 * @returns {string} for example "Thursday 8 October"
 */
const WEEKDAY_FORMAT = new Intl.DateTimeFormat(undefined, { weekday: "long" });
export function longDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  return `${WEEKDAY_FORMAT.format(new Date(y, m - 1, d))} ${d} ${MONTHS[m - 1]}`;
}
function unusedLongDate(key) {
  return joinLabel(namesOf(key));
}
