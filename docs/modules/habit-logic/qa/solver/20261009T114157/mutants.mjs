// Mutants for mutate.mjs. Each one is a deliberate defect that a fixed test must turn red.
// edits: [source file, exact text to find, replacement]. A replaced function keeps its old body
// under an unused name, so the mirror still parses.

const LOCALE_SHORT = `export function shortDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return \`\${date.toLocaleDateString(undefined, { weekday: "short" })} \${d} \${date.toLocaleDateString(undefined, { month: "short" })}\`;
}
function unusedShortDate(key) {`;

const LOCALE_LONG = `export function longDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return \`\${date.toLocaleDateString(undefined, { weekday: "long" })} \${d} \${date.toLocaleDateString(undefined, { month: "long" })}\`;
}
function unusedLongDate(key) {`;

const INTL_LONG = `const WEEKDAY_FORMAT = new Intl.DateTimeFormat(undefined, { weekday: "long" });
export function longDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  return \`\${WEEKDAY_FORMAT.format(new Date(y, m - 1, d))} \${d} \${MONTHS[m - 1]}\`;
}
function unusedLongDate(key) {`;

const LOCALE_EDITS = [
  ["dates.js", "export function shortDate(key) {", LOCALE_SHORT],
  ["dates.js", "export function longDate(key) {", LOCALE_LONG],
];

export const MUTANTS = {
  "locale-toLocaleDateString": {
    about: "WR-01: shortDate and longDate read the default locale through toLocaleDateString(undefined, ...)",
    testFile: "dates.test.js",
    edits: LOCALE_EDITS,
  },
  "locale-toLocaleDateString-old-test": {
    about: "WR-01 control: the same mutant against the tests as they were at 09c5047",
    testsFrom: "09c5047",
    testFile: "dates.test.js",
    edits: LOCALE_EDITS,
  },
  "locale-Intl-at-load": {
    about: "WR-01: longDate uses an Intl.DateTimeFormat built with the default locale when dates.js loads",
    testFile: "dates.test.js",
    edits: [["dates.js", "export function longDate(key) {", INTL_LONG]],
  },
  "localDateKey-mutates": {
    about: "WR-02: localDateKey sets the caller's Date to local midnight before reading it",
    testFile: "purity.test.js",
    edits: [["dates.js", "export function localDateKey(date) {", "export function localDateKey(date) {\n  date.setHours(0, 0, 0, 0);"]],
  },
  "localDateKey-mutates-old-test": {
    about: "WR-02 control: the same mutant against the tests as they were at 73fb59b",
    testsFrom: "73fb59b",
    testFile: "purity.test.js",
    edits: [["dates.js", "export function localDateKey(date) {", "export function localDateKey(date) {\n  date.setHours(0, 0, 0, 0);"]],
  },
  "strip-5-days-before-WR-04": {
    about: "WR-04 control: the strip shrunk to 5 days in the code before the fix (one WEEK_LENGTH for strip and heatmap)",
    srcFrom: "6275858",
    testsFrom: "6275858",
    testFile: "habits.test.js",
    edits: [["habits.js", "const WEEK_LENGTH = 7;", "const WEEK_LENGTH = 5;"]],
  },
  "strip-5-days-after-WR-04": {
    about: "WR-04: the strip shrunk to 5 days in the fixed code (STRIP_DAYS apart from DAYS_PER_WEEK)",
    testFile: "habits.test.js",
    edits: [["habits.js", "const STRIP_DAYS = 7;", "const STRIP_DAYS = 5;"]],
  },
  "toggledHabit-no-sort": {
    about: "WR-09: toggledHabit without the sort, to confirm the sort (not the Set) gives the ascending order its comment claims",
    testFile: "habits.test.js",
    edits: [["habits.js", "done: [...days].sort() }", "done: [...days] }"]],
  },
  "trim-plain-spaces-only": {
    about: "WR-10 (a): validateName strips plain spaces only, so the escaped no-break, em space and BOM test must go red",
    testFile: "habits.test.js",
    edits: [["habits.js", "const name = raw.trim();", 'const name = raw.split(" ").filter(Boolean).join(" ");']],
  },
  "strip-labels-wrong-weekday": {
    about: "WR-10 (c): shortDate shifts the weekday by one, so the strip title's Fri 2 Oct and Thu 8 Oct must be asserted",
    testFile: "sample-history.test.js",
    edits: [["dates.js", "return joinLabel(dayParts(key));", "const parts = dayParts(addDays(key, 1)); return joinLabel({ ...parts, day: dayParts(key).day });"]],
  },
  "strip-labels-wrong-weekday-old-test": {
    about: "WR-10 (c) control: the same mutant against the tests as they were at c0099bb",
    testsFrom: "c0099bb",
    testFile: "sample-history.test.js",
    edits: [["dates.js", "return joinLabel(dayParts(key));", "const parts = dayParts(addDays(key, 1)); return joinLabel({ ...parts, day: dayParts(key).day });"]],
  },
};
