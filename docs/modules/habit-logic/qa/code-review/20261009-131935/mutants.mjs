// Mutants, applied in memory by preload.mjs. Nothing here touches src/ or tests/.
// kind "module": the loader serves src/<file> with the edits, so the code really runs mutated.
// kind "scan": only fs.readFileSync of src/<file> returns the edited text, so tests/purity.test.js scans
// it but nothing executes it (the egress lines below must never run).
const MAX_LINE = "export const MAX_NAME_LENGTH = 40;\n";
const FETCH = 'fetch("https://collector.invalid/streaks");\n';
const BOUND_LOOP = "for (let key = from; length < days.size && days.has(key); key = addDays(key, step)) length++;";

export const MUTANTS = {
  // ---- module mutants on src/habits.js
  "bound-removed": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "length < days.size && days.has(key)", to: "days.has(key)" }],
  },
  // Control for bound-removed: the bound set to 0 changes every result, so the edited line is live code.
  "bound-zero": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "length < days.size && days.has(key)", to: "length < 0 && days.has(key)" }],
  },
  // Same loop, with the size bound turned into a counter, so a probe can show whether it ever fires.
  "bound-counter": {
    kind: "module",
    file: "habits.js",
    edits: [
      {
        from: BOUND_LOOP,
        to: "for (let key = from; days.has(key); key = addDays(key, step)) {\n    if (length >= days.size) {\n      globalThis.__boundHits = (globalThis.__boundHits ?? 0) + 1;\n      break;\n    }\n    length++;\n  }",
      },
    ],
  },
  "strip-5": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "const STRIP_DAYS = 7;", to: "const STRIP_DAYS = 5;" }],
  },
  "month-year-only": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: 'key.slice(0, "YYYY-MM".length)', to: "key.slice(0, 4)" }],
  },
  "sunday-first": {
    kind: "module",
    file: "habits.js",
    edits: [
      {
        from: "addDays(todayKey, -weekdayIndex(todayKey))",
        to: "addDays(todayKey, -((weekdayIndex(todayKey) + 1) % 7))",
      },
    ],
  },
  "current-unfiltered": {
    kind: "module",
    file: "habits.js",
    edits: [
      {
        from: "const days = streakDays(done);\n  const start",
        to: "const days = new Set(done);\n  const start",
      },
    ],
  },
  "best-unfiltered": {
    kind: "module",
    file: "habits.js",
    edits: [
      {
        from: "const days = streakDays(done);\n  let best = 0;",
        to: "const days = new Set(done);\n  let best = 0;",
      },
    ],
  },
  "filter-useless": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "done.filter(isDateKey)", to: "done.filter(Boolean)" }],
  },
  "runcontinues-second-day": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "weekWindow(todayKey)[0]", to: "weekWindow(todayKey)[1]" }],
  },
  "trim-plain-space-only": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "const name = raw.trim();", to: "const name = raw.replace(/^ +| +$/g, '');" }],
  },
  "longer-than-ge": {
    kind: "module",
    file: "habits.js",
    edits: [{ from: "++count > limit", to: "++count >= limit" }],
  },
  "name-length-array": {
    kind: "module",
    file: "habits.js",
    edits: [
      {
        from: "if (longerThan(name, MAX_NAME_LENGTH))",
        to: "if (Array.from(name).length > MAX_NAME_LENGTH)",
      },
    ],
  },

  // ---- module mutants on src/dates.js
  "date-arg-partial": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: "  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());",
        to: "  date.setMilliseconds(0);\n  date.setSeconds(0);\n  date.setMinutes(0);\n  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());",
      },
    ],
  },
  "date-arg-sethours": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: "  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());",
        to: "  date.setHours(0, 0, 0, 0);\n  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());",
      },
    ],
  },
  "locale-longdate": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: "  return joinLabel(namesOf(key));",
        to: '  const { year, month, day } = parseKey(key);\n  return new Date(year, month - 1, day).toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });',
      },
    ],
  },
  "locale-intl-longdate": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: "  return joinLabel(namesOf(key));",
        to: '  const { year, month, day } = parseKey(key);\n  return new Intl.DateTimeFormat(undefined, { weekday: "long", day: "numeric", month: "long" }).format(new Date(year, month - 1, day));',
      },
    ],
  },

  // ---- scan mutants on src/habits.js (text only, never executed)
  "scan-control": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: MAX_LINE, to: `${MAX_LINE}${FETCH}` }],
  },
  "scan-s1-url-string-same-line": {
    kind: "scan",
    file: "habits.js",
    edits: [
      {
        from: MAX_LINE,
        to: `${MAX_LINE}const ENDPOINT = "https://collector.invalid/streaks"; fetch(ENDPOINT);\n`,
      },
    ],
  },
  "scan-s2-slash-star-in-string": {
    kind: "scan",
    file: "habits.js",
    edits: [
      {
        from: MAX_LINE,
        to: `${MAX_LINE}const MIME = "*/*"; sessionStorage.setItem("k", MIME);\n`,
      },
    ],
  },
  "scan-s3-slash-star-in-line-comment": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: MAX_LINE, to: `${MAX_LINE}// every file under src/*\n${FETCH}` }],
  },
};
