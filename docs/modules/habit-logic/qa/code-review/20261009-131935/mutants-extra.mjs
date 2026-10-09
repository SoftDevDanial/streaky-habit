// More mutants, same format as mutants.mjs.
const WEEKDAY_LINE = "  return { weekday: WEEKDAYS[weekdayIndex(key)], day, month: MONTHS[month - 1] };";
const MAX_LINE = "export const MAX_NAME_LENGTH = 40;\n";
const BOUND_LOOP = "for (let key = from; length < days.size && days.has(key); key = addDays(key, step)) length++;";
const BOUND_COUNTER =
  "for (let key = from; days.has(key); key = addDays(key, step)) {\n    if (length >= days.size) {\n      globalThis.__boundHits = (globalThis.__boundHits ?? 0) + 1;\n      break;\n    }\n    length++;\n  }";

export const EXTRA_MUTANTS = {
  // These change only the weekday name and only on a non-English default locale, so every test that runs
  // under this machine's own English locale stays green. Only the R4 locale test can tell them apart.
  "locale-weekday-toLocaleDateString": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: WEEKDAY_LINE,
        to: '  return { weekday: new Date(parseKey(key).year, month - 1, day).toLocaleDateString(undefined, { weekday: "long" }), day, month: MONTHS[month - 1] };',
      },
    ],
  },
  "locale-weekday-Intl": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: WEEKDAY_LINE,
        to: '  return { weekday: new Intl.DateTimeFormat(undefined, { weekday: "long" }).format(new Date(parseKey(key).year, month - 1, day)), day, month: MONTHS[month - 1] };',
      },
    ],
  },
  // Not covered by the German default the locale test installs: Number.prototype.toLocaleString.
  "locale-number-toLocaleString": {
    kind: "module",
    file: "dates.js",
    edits: [
      {
        from: "  return `${weekday} ${day} ${month}`;",
        to: "  return `${weekday} ${day.toLocaleString()} ${month}`;",
      },
    ],
  },
  // Scan mutants (text only, never executed). The planted lines hold no quote that contains // or /*, so the
  // auditor's guard regex has nothing to match. Only the comment holds the marker.
  "scan-s3b-slash-star-in-line-comment": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: MAX_LINE, to: `${MAX_LINE}// every file under src/*\nlocalStorage.setItem("streaks", "x");\n` }],
  },
  "scan-s3c-slash-star-in-line-comment-network": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: MAX_LINE, to: `${MAX_LINE}// every file under src/*\nnavigator.sendBeacon(endpoint, body);\n` }],
  },
  // Control for bound-counter: with the isDateKey filter also disabled, the size bound is the only thing
  // that ends a walk on a stuck key, so the counter must fire. If it does, the counter works and the
  // filter is what keeps the bound idle.
  "bound-counter-no-filter": {
    kind: "module",
    file: "habits.js",
    edits: [
      { from: BOUND_LOOP, to: BOUND_COUNTER },
      { from: "done.filter(isDateKey)", to: "done.filter(Boolean)" },
    ],
  },
};
