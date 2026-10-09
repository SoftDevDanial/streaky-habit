// Independent cross-check of the qa.md Then-lines for habit-logic, driven straight against src/.
// It does not read the unit test files. Expected values are typed from docs/modules/habit-logic/qa.md.
// Run: node <absolute path to this file>. Prints one line per row, a per-scenario summary, and exits 1 on any FAIL.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const ROOT = "{workspace}/examples/streaks";
const dates = await import(pathToFileURL(`${ROOT}/src/dates.js`).href);
const habits = await import(pathToFileURL(`${ROOT}/src/habits.js`).href);
const sample = JSON.parse(readFileSync(`${ROOT}/docs/design/sample-history.json`, "utf8"));

const KL = "Asia/Kuala_Lumpur";
const NY = "America/New_York";
const T = "2026-10-08";
const DAY = 86_400_000;
const H = sample.habits;

const sorted = (v) => {
  if (Array.isArray(v)) return v.map(sorted);
  if (v !== null && typeof v === "object") {
    return Object.fromEntries(Object.keys(v).sort().map((k) => [k, sorted(v[k])]));
  }
  return v;
};
const same = (a, b) => JSON.stringify(sorted(a)) === JSON.stringify(sorted(b));

const tally = new Map();
function row(r, scenario, label, actual, expected) {
  const pass = same(actual, expected);
  if (!tally.has(scenario)) tally.set(scenario, { r, pass: 0, total: 0 });
  const t = tally.get(scenario);
  t.total++;
  if (pass) t.pass++;
  console.log(
    `${pass ? "PASS" : "FAIL"} | ${r} | ${scenario} | ${label} | actual ${JSON.stringify(actual)} | expected ${JSON.stringify(expected)}`,
  );
}

function inZone(zone, fn) {
  const before = process.env.TZ;
  process.env.TZ = zone;
  try {
    return fn();
  } finally {
    if (before === undefined) delete process.env.TZ;
    else process.env.TZ = before;
  }
}

function utcKey(ms) {
  return new Date(ms).toISOString().slice(0, 10);
}

// ---------- R1 ----------
const S1 = "R1 The local calendar day of an instant";
const r1 = [
  [KL, () => new Date(2026, 9, 8, 0, 0, 0, 0), "2026-10-08"],
  [KL, () => new Date(2026, 9, 8, 23, 59, 59, 999), "2026-10-08"],
  [KL, () => new Date(2027, 0, 1), "2027-01-01"],
  [KL, () => new Date("2026-10-07T16:30:00Z"), "2026-10-08"],
  [NY, () => new Date(2026, 2, 8, 3, 30), "2026-03-08"],
  [NY, () => new Date(2026, 10, 1, 1, 30), "2026-11-01"],
];
for (const [zone, make, key] of r1) {
  row("R1", S1, `${zone} ${key}`, inZone(zone, () => dates.localDateKey(make())), key);
}

// ---------- R2 ----------
const S2 = "R2 Valid date keys";
const r2 = [
  ["2026-10-08", true],
  ["2028-02-29", true],
  ["2000-02-29", true],
  ["2026-12-31", true],
  ["2026-02-29", false],
  ["2100-02-29", false],
  ["2026-13-01", false],
  ["2026-00-10", false],
  ["2026-04-31", false],
  ["2026-1-1", false],
  ["2026-10-08T00:00", false],
  [" 2026-10-08", false],
  ["0000-01-01", false],
  [20261008, false],
  [null, false],
  [undefined, false],
  [{}, false],
];
for (const [value, expected] of r2) {
  row("R2", S2, `isDateKey(${String(JSON.stringify(value) ?? value)})`, dates.isDateKey(value), expected);
}

// ---------- R3 ----------
const S3 = "R3 Calendar arithmetic that ignores the time zone";
const r3 = [
  [KL, "2026-10-08", -6, "2026-10-02"],
  [KL, "2026-12-31", 1, "2027-01-01"],
  [KL, "2028-02-28", 1, "2028-02-29"],
  [KL, "2026-02-28", 1, "2026-03-01"],
  [KL, "2026-07-20", 83, "2026-10-11"],
  [KL, "2026-10-05", -77, "2026-07-20"],
  [NY, "2026-03-07", 1, "2026-03-08"],
  [NY, "2026-03-08", 1, "2026-03-09"],
  [NY, "2026-11-01", 1, "2026-11-02"],
  [NY, "2026-11-02", -1, "2026-11-01"],
  [NY, "2026-03-09", -2, "2026-03-07"],
];
for (const [zone, key, days, expected] of r3) {
  row("R3", S3, `${zone} addDays(${key}, ${days})`, inZone(zone, () => dates.addDays(key, days)), expected);
}

// ---------- R4 ----------
const S4a = "R4 Short weekday, day and month for every weekday";
const r4a = [
  ["2026-10-05", "Mon", 5, "Oct", "Mon 5 Oct"],
  ["2026-10-06", "Tue", 6, "Oct", "Tue 6 Oct"],
  ["2026-10-07", "Wed", 7, "Oct", "Wed 7 Oct"],
  ["2026-10-08", "Thu", 8, "Oct", "Thu 8 Oct"],
  ["2026-10-09", "Fri", 9, "Oct", "Fri 9 Oct"],
  ["2026-10-10", "Sat", 10, "Oct", "Sat 10 Oct"],
  ["2026-10-11", "Sun", 11, "Oct", "Sun 11 Oct"],
  ["2026-07-20", "Mon", 20, "Jul", "Mon 20 Jul"],
  ["2026-08-01", "Sat", 1, "Aug", "Sat 1 Aug"],
];
for (const [key, weekday, day, month, short] of r4a) {
  row("R4", S4a, key, [dates.dayParts(key), dates.shortDate(key)], [{ weekday, day, month }, short]);
}

const S4b = "R4 Short and long month names for every month";
const r4b = [
  ["2026-01-15", "Jan", "Thursday 15 January"],
  ["2026-02-15", "Feb", "Sunday 15 February"],
  ["2026-03-15", "Mar", "Sunday 15 March"],
  ["2026-04-15", "Apr", "Wednesday 15 April"],
  ["2026-05-15", "May", "Friday 15 May"],
  ["2026-06-15", "Jun", "Monday 15 June"],
  ["2026-07-15", "Jul", "Wednesday 15 July"],
  ["2026-08-15", "Aug", "Saturday 15 August"],
  ["2026-09-15", "Sep", "Tuesday 15 September"],
  ["2026-10-15", "Oct", "Thursday 15 October"],
  ["2026-11-15", "Nov", "Sunday 15 November"],
  ["2026-12-15", "Dec", "Tuesday 15 December"],
  ["2026-10-08", "Oct", "Thursday 8 October"],
  ["2027-01-01", "Jan", "Friday 1 January"],
];
for (const [key, month, long] of r4b) {
  row("R4", S4b, key, [dates.dayParts(key).month, dates.longDate(key)], [month, long]);
}

const S4c = "R4 The weekday index, Monday first";
const r4c = [
  ["2026-10-05", 0],
  ["2026-10-06", 1],
  ["2026-10-07", 2],
  ["2026-10-08", 3],
  ["2026-10-09", 4],
  ["2026-10-10", 5],
  ["2026-10-11", 6],
  ["2026-07-20", 0],
  ["2026-08-01", 5],
];
for (const [key, index] of r4c) row("R4", S4c, key, dates.weekdayIndex(key), index);

// ---------- R5 to R8, sample on the key screen ----------
const S5 = "R5 The seven days of the strip";
const r5 = [
  ["2026-10-08", ["2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08"]],
  ["2027-01-03", ["2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-03"]],
  ["2028-03-02", ["2028-02-25", "2028-02-26", "2028-02-27", "2028-02-28", "2028-02-29", "2028-03-01", "2028-03-02"]],
];
for (const [today, days] of r5) row("R5", S5, today, habits.weekWindow(today), days);

const byName = (name) => H.find((h) => h.name === name);
const S5to8 = "R5 R6 R7 R8 The sample's strips and streaks on the key screen";
const sampleToday = [
  ["Read 20 pages", ". D D D D D D", 6, 14, false],
  ["Stretch 10 minutes", "D D . D D D .", 3, 9, true],
  ["No phone after 11pm", ". D . . D . D", 1, 4, false],
];
for (const [name, strip, current, best, run] of sampleToday) {
  const { done } = byName(name);
  const drawn = habits.weekWindow(T).map((k) => (done.includes(k) ? "D" : ".")).join(" ");
  row("R5", S5to8, `${name} strip`, drawn, strip);
  row("R6", S5to8, `${name} currentStreak`, habits.currentStreak(done, T), current);
  row("R7", S5to8, `${name} bestStreak`, habits.bestStreak(done), best);
  row("R8", S5to8, `${name} runContinues`, habits.runContinues(done, T), run);
}

const S6b = "R6 R8 The same sample one day later";
const sampleNext = [
  ["Read 20 pages", 6, false],
  ["Stretch 10 minutes", 0, true],
  ["No phone after 11pm", 1, false],
];
for (const [name, current, run] of sampleNext) {
  const { done } = byName(name);
  row("R6", S6b, `${name} currentStreak on 2026-10-09`, habits.currentStreak(done, "2026-10-09"), current);
  row("R8", S6b, `${name} runContinues on 2026-10-09`, habits.runContinues(done, "2026-10-09"), run);
}

const S6a = "R6 A streak does not break until today is over";
const r6a = [
  [[], 0],
  [["2026-10-07"], 1],
  [["2026-10-06"], 0],
  [["2026-10-09"], 0],
  [["2026-10-08", "2026-10-08"], 1],
  [["2026-09-30", "2026-10-01"], 0],
  [["2026-10-08", "2026-10-06", "2026-10-07"], 3],
  [["2026-10-07", "2026-10-08", "2026-10-09"], 2],
];
for (const [done, current] of r6a) row("R6", S6a, JSON.stringify(done), habits.currentStreak(done, T), current);

const S6dst = "R6 A streak that crosses a DST change";
row(
  "R6",
  S6dst,
  "NY zone, today 2026-03-09",
  inZone(NY, () => habits.currentStreak(["2026-03-07", "2026-03-08", "2026-03-09"], "2026-03-09")),
  3,
);

const S7 = "R7 The longest run in the whole history";
const r7 = [
  [[], 0],
  [["2026-12-30", "2026-12-31", "2027-01-01"], 3],
  [["2028-02-28", "2028-02-29", "2028-03-01"], 3],
  [["2026-02-28", "2026-03-01"], 2],
  [["2026-10-08", "2026-10-08"], 1],
  [["2026-10-01", "2026-10-03"], 1],
  [["2026-10-09", "2026-10-08", "2026-10-07"], 3],
];
for (const [done, best] of r7) row("R7", S7, JSON.stringify(done), habits.bestStreak(done), best);

// ---------- R6 and R7, keys that fail isDateKey ----------
const S67 = "R6 R7 Keys that fail isDateKey are ignored";
const FAR_START = "24660873954866-12-02";
const FAR_STUCK = "24660873954866-12-04";
row(
  "R7",
  S67,
  "bestStreak with 3 valid days plus FAR_START and FAR_STUCK",
  habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", FAR_START, FAR_STUCK]),
  3,
);
const WS = ["", " ", "\t", "\u00A0", "\u2003", "\u3000", "\uFEFF"];
const [farYear, farMonth, farDay] = FAR_START.split("-");
const spellings = [];
for (let i = 1; spellings.length < 20_000; i++) {
  const slot = (k) => WS[Math.floor(i / 7 ** k) % 7];
  spellings.push(`${slot(5)}${farYear}${slot(4)}-${slot(3)}${farMonth}${slot(2)}-${slot(1)}${farDay}${slot(0)}`);
}
row("R7", S67, "precondition: 20,000 distinct spellings", new Set(spellings).size, 20_000);
row(
  "R7",
  S67,
  "bestStreak with 20,000 spellings of FAR_START and FAR_STUCK",
  habits.bestStreak([...spellings, FAR_STUCK]),
  0,
);
const history = [];
for (let key = "0001-01-10", n = 0; n < 400; n++, key = dates.addDays(key, -1)) history.push(key);
row("R6", S67, "precondition: 10 valid keys among the 400", history.filter((k) => dates.isDateKey(k)).length, 10);
row("R6", S67, "currentStreak of the 400 keys, today 0001-01-10", habits.currentStreak(history, "0001-01-10"), 10);
row("R7", S67, "bestStreak of the 400 keys", habits.bestStreak(history), 10);

// ---------- R9 ----------
const S9a = "R9 Ticking a day inside the window";
const r9a = [
  [1, "2026-10-08", true, 4],
  [0, "2026-10-08", false, 5],
  [2, "2026-10-07", true, 3],
  [1, "2026-10-04", true, 7],
  [1, "2026-10-02", false, 3],
  [0, "2026-10-02", true, 10],
];
for (const [index, date, contains, current] of r9a) {
  const snapshot = structuredClone(H);
  const out = habits.toggleDay(H, index, date, T);
  const d = out[index].done;
  const ascending = d.every((k, i) => i === 0 || d[i - 1] < k);
  const others = out.every((h, i) => i === index || same(h, H[i]));
  row(
    "R9",
    S9a,
    `index ${index} ${date} ${contains ? "now contains" : "no longer contains"}`,
    [d.includes(date) === contains, ascending, habits.currentStreak(d, T), others, same(H, snapshot)],
    [true, true, current, true, true],
  );
}

const S9b = "R9 Days outside the window and bad indexes change nothing";
const r9b = [
  [0, "2026-10-01"],
  [1, "2026-10-09"],
  [2, "2026-07-20"],
  [3, "2026-10-08"],
  [-1, "2026-10-08"],
  [0.5, "2026-10-08"],
];
for (const [index, date] of r9b) {
  const snapshot = structuredClone(H);
  const out = habits.toggleDay(H, index, date, T);
  row("R9", S9b, `index ${index} ${date}`, [out !== H, same(out, H), same(H, snapshot)], [true, true, true]);
}

// ---------- R10 ----------
const S10 = "R10 The 12-week grid around today";
const r10 = [
  ["2026-10-08", "2026-07-20", "2026-10-11", 3],
  ["2026-10-11", "2026-07-20", "2026-10-11", 0],
  ["2026-10-05", "2026-07-20", "2026-10-11", 6],
  ["2026-10-12", "2026-07-27", "2026-10-18", 6],
  ["2027-01-07", "2026-10-19", "2027-01-10", 3],
];
for (const [today, first, last, futureCount] of r10) {
  const cells = habits.heatmapCells([], today);
  const [fy, fm, fd] = first.split("-").map(Number);
  const firstMs = Date.UTC(fy, fm - 1, fd);
  const consecutive = cells.every((c, i) => c.key === utcKey(firstMs + i * DAY));
  const layout = cells.every((c, i) => c.column === Math.floor(i / 7) + 1 && c.row === (i % 7) + 1);
  const future = cells.filter((c) => c.future);
  const futureOk = future.length === futureCount && future.every((c) => c.key > today && c.count === null && c.level === null);
  const todays = cells.filter((c) => c.today).map((c) => c.key);
  const pastZero = cells.filter((c) => !c.future).every((c) => c.count === 0 && c.total === 0 && c.level === 0);
  row(
    "R10",
    S10,
    `today ${today}`,
    [cells.length, cells[0].key, cells[0].column, cells[0].row, cells[83].key, cells[83].column, cells[83].row, consecutive, layout, future.length, futureOk, todays, pastZero],
    [84, first, 1, 1, last, 12, 7, true, true, futureCount, true, [today], true],
  );
}

const S10g = "R10 R11 The sample's heatmap equals the golden";
const golden = habits.heatmapCells(H, T);
const byKey = new Map(golden.map((c) => [c.key, c]));
const goldenKeys = Object.keys(sample.heatmapLevels);
row(
  "R10",
  S10g,
  "cell 2026-10-08 column, row, today",
  [byKey.get(T).column, byKey.get(T).row, byKey.get(T).today],
  [12, 4, true],
);
row(
  "R11",
  S10g,
  "81 golden keys, level equals file",
  [goldenKeys.length, goldenKeys.every((k) => byKey.get(k).level === sample.heatmapLevels[k])],
  [81, true],
);
row(
  "R10",
  S10g,
  "total 3 and count equals the habits done that day",
  goldenKeys.every(
    (k) => byKey.get(k).total === 3 && byKey.get(k).count === H.filter((h) => h.done.includes(k)).length,
  ),
  true,
);
row(
  "R11",
  S10g,
  "distribution of levels 0 to 4 over the 81 cells",
  [0, 1, 2, 3, 4].map((l) => goldenKeys.filter((k) => byKey.get(k).level === l).length),
  [3, 30, 28, 0, 20],
);
row(
  "R10",
  S10g,
  "2026-10-09, 10, 11 are future",
  ["2026-10-09", "2026-10-10", "2026-10-11"].map((k) => byKey.get(k).future),
  [true, true, true],
);

// ---------- R11 ----------
const S11 = "R11 Levels from the share of habits done";
const r11 = [
  [1, [0, 4]],
  [2, [0, 2, 4]],
  [3, [0, 1, 2, 4]],
  [4, [0, 1, 2, 3, 4]],
  [5, [0, 1, 2, 2, 3, 4]],
  [6, [0, 1, 1, 2, 2, 3, 4]],
  [12, [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4]],
];
for (const [total, levels] of r11) {
  row(
    "R11",
    S11,
    `total ${total}`,
    Array.from({ length: total + 1 }, (_, c) => habits.heatLevel(c, total)),
    levels,
  );
}
row("R11", "R11 No habits means level 0", "heatLevel(0, 0)", habits.heatLevel(0, 0), 0);

const S1011 = "R10 R11 A fourth habit makes level 3 appear";
const four = [...structuredClone(H), { name: "Drink water", done: [] }];
const byKey4 = new Map(habits.heatmapCells(four, T).map((c) => [c.key, c]));
for (const [key, count, level] of [
  ["2026-07-20", 3, 3],
  ["2026-10-06", 3, 3],
  ["2026-10-08", 2, 2],
  ["2026-07-21", 1, 1],
  ["2026-08-12", 0, 0],
]) {
  const c = byKey4.get(key);
  row("R10", S1011, key, [c.count, c.total, c.level], [count, 4, level]);
}

// ---------- R12 ----------
const S12 = "R12 Month labels over the first column whose Monday is in the month";
const r12 = [
  ["2026-10-08", [{ column: 1, month: "Jul" }, { column: 3, month: "Aug" }, { column: 8, month: "Sep" }, { column: 12, month: "Oct" }]],
  ["2026-10-12", [{ column: 1, month: "Jul" }, { column: 2, month: "Aug" }, { column: 7, month: "Sep" }, { column: 11, month: "Oct" }]],
  ["2027-01-07", [{ column: 1, month: "Oct" }, { column: 3, month: "Nov" }, { column: 8, month: "Dec" }, { column: 12, month: "Jan" }]],
  ["2026-03-31", [{ column: 1, month: "Jan" }, { column: 4, month: "Feb" }, { column: 8, month: "Mar" }]],
];
for (const [today, labels] of r12) row("R12", S12, today, habits.monthLabels(today), labels);

// ---------- R13 ----------
const EXISTING = ["Read 20 pages", "Stretch 10 minutes", "No phone after 11pm"];
const S13 = "R13 Name checks in the order empty, too long, duplicate";
const r13 = [
  ["", { ok: false, error: "empty" }],
  ["   ", { ok: false, error: "empty" }],
  ["Walk to the end of the street and back after dinner", { ok: false, error: "too-long" }],
  ["Read twenty pages before bed every night", { ok: true, name: "Read twenty pages before bed every night" }],
  ["Read twenty pages before bed every night.", { ok: false, error: "too-long" }],
  ["  Drink water  ", { ok: true, name: "Drink water" }],
  ["read 20 pages", { ok: false, error: "duplicate" }],
  [" STRETCH 10 MINUTES ", { ok: false, error: "duplicate" }],
];
for (const [raw, expected] of r13) row("R13", S13, JSON.stringify(raw), habits.validateName(raw, EXISTING), expected);

const LONG41 = "Read twenty pages before bed every night.";
row(
  "R13",
  "R13 Too long is checked before duplicate",
  "validateName(41 chars, existing name equal to it)",
  habits.validateName(LONG41, [LONG41]),
  { ok: false, error: "too-long" },
);

const EMOJI = String.fromCodePoint(0x1f4da);
row(
  "R13",
  "R13 Length counts code points, not UTF-16 units",
  "40 book emoji (80 UTF-16 units)",
  [EMOJI.repeat(40).length, habits.validateName(EMOJI.repeat(40), [])],
  [80, { ok: true, name: EMOJI.repeat(40) }],
);
row(
  "R13",
  "R13 Length counts code points, not UTF-16 units",
  "41 book emoji",
  habits.validateName(EMOJI.repeat(41), []),
  { ok: false, error: "too-long" },
);
row("R13", "R13 The limits are exported", "MAX_NAME_LENGTH, MAX_HABITS", [habits.MAX_NAME_LENGTH, habits.MAX_HABITS], [40, 12]);

// ---------- R14 ----------
const S14a = "R14 A new habit goes to the bottom";
const added = habits.addHabit(H, "  Drink water  ");
const snapshot14 = structuredClone(H);
row(
  "R14",
  S14a,
  "addHabit(sample, '  Drink water  ')",
  [
    added.ok,
    added.ok ? added.habits.map((h) => h.name) : null,
    added.ok ? added.habits[3] : null,
    added.ok ? same(added.habits.slice(0, 3), H) : null,
    same(H, snapshot14),
  ],
  [true, [...EXISTING, "Drink water"], { name: "Drink water", done: [] }, true, true],
);
row(
  "R14",
  "R14 A rejected name returns its error",
  "addHabit(sample, 'read 20 pages')",
  habits.addHabit(H, "read 20 pages"),
  { ok: false, error: "duplicate" },
);

const S14c = "R14 The limit of 12 habits";
const listOf = (n) => Array.from({ length: n }, (_, i) => ({ name: `Habit ${i + 1}`, done: [] }));
const eleven = habits.addHabit(listOf(11), "Habit 12");
row(
  "R14",
  S14c,
  "11 habits plus 'Habit 12'",
  [eleven.ok, eleven.ok ? eleven.habits.length : null, eleven.ok ? eleven.habits.at(-1).name : null],
  [true, 12, "Habit 12"],
);
row("R14", S14c, "12 habits plus 'Habit 13'", habits.addHabit(listOf(12), "Habit 13"), { ok: false, error: "limit" });
row("R14", S14c, "12 habits plus empty name", habits.addHabit(listOf(12), ""), { ok: false, error: "limit" });

// ---------- R15 ----------
const S15 = "R15 Deleting a habit";
for (const [index, names] of [
  [0, ["Stretch 10 minutes", "No phone after 11pm"]],
  [2, ["Read 20 pages", "Stretch 10 minutes"]],
  [3, EXISTING],
  [-1, EXISTING],
]) {
  const snapshot = structuredClone(H);
  const out = habits.deleteHabit(H, index);
  const doneKept = out.every((h) => same(h, H.find((c) => c.name === h.name)));
  row("R15", S15, `index ${index}`, [out.map((h) => h.name), doneKept, same(H, snapshot)], [names, true, true]);
}

// ---------- R16, source scan (text as it is, and code with comments removed) ----------
const srcDates = readFileSync(`${ROOT}/src/dates.js`, "utf8");
const srcHabits = readFileSync(`${ROOT}/src/habits.js`, "utf8");
const stripComments = (t) => t.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
const codeDates = stripComments(srcDates);
const codeHabits = stripComments(srcHabits);
const S16a = "R16 No clock, DOM, storage or locale access in the source";
row(
  "R16",
  S16a,
  "Date.now( and new Date() with no argument, whole file text",
  [
    srcDates.includes("Date.now("),
    srcHabits.includes("Date.now("),
    /new\s+Date\s*\(\s*\)/.test(srcDates),
    /new\s+Date\s*\(\s*\)/.test(srcHabits),
  ],
  [false, false, false, false],
);
row(
  "R16",
  S16a,
  "document, window, localStorage, globalThis, Intl and toLocale, code only",
  [
    /\b(document|window|localStorage|globalThis|Intl)\b/.test(codeDates),
    /\b(document|window|localStorage|globalThis|Intl)\b/.test(codeHabits),
    /\btoLocale\w*/.test(codeDates),
    /\btoLocale\w*/.test(codeHabits),
  ],
  [false, false, false, false],
);
const specifiers = [...codeHabits.matchAll(/^import\b[^;]*?from\s*["']([^"']+)["']/gm)].map((m) => m[1]);
row("R16", "R16 habits.js imports only ./dates.js and dates.js imports nothing", "import specifiers", [
  specifiers,
  /\bimport\b/.test(codeDates),
], [["./dates.js"], false]);

const S16b = "R16 No exported function writes to its arguments";
const deepFreeze = (v) => {
  if (v !== null && typeof v === "object" && !Object.isFrozen(v)) {
    Object.freeze(v);
    Object.values(v).forEach(deepFreeze);
  }
  return v;
};
const frozen = deepFreeze(structuredClone(H));
const frozenNames = deepFreeze(frozen.map((h) => h.name));
const fd = Object.freeze(new Date(2026, 9, 8, 12, 34, 56, 789));
const fdBefore = fd.getTime();
const calls = {
  localDateKey: () => dates.localDateKey(fd),
  isDateKey: () => dates.isDateKey(T),
  addDays: () => dates.addDays(T, -6),
  dayParts: () => dates.dayParts(T),
  shortDate: () => dates.shortDate(T),
  longDate: () => dates.longDate(T),
  weekdayIndex: () => dates.weekdayIndex(T),
  weekWindow: () => habits.weekWindow(T),
  currentStreak: () => habits.currentStreak(frozen[0].done, T),
  bestStreak: () => habits.bestStreak(frozen[0].done),
  runContinues: () => habits.runContinues(frozen[0].done, T),
  toggleDay: () => habits.toggleDay(frozen, 1, T, T),
  heatmapCells: () => habits.heatmapCells(frozen, T),
  heatLevel: () => habits.heatLevel(2, 3),
  monthLabels: () => habits.monthLabels(T),
  validateName: () => habits.validateName("Drink water", frozenNames),
  addHabit: () => habits.addHabit(frozen, "Drink water"),
  deleteHabit: () => habits.deleteHabit(frozen, 0),
};
const exported = [...Object.entries(dates), ...Object.entries(habits)]
  .filter(([, v]) => typeof v === "function")
  .map(([k]) => k)
  .sort();
row("R16", S16b, "every exported function is in the call list", exported, Object.keys(calls).sort());
const thrown = [];
for (const [name, call] of Object.entries(calls)) {
  try {
    call();
  } catch (error) {
    thrown.push(`${name}: ${error.message}`);
  }
}
row("R16", S16b, "no call throws on frozen arguments", thrown, []);
row("R16", S16b, "frozen sample still equals the file's habits", same(frozen, H), true);
row("R16", S16b, "Date passed to localDateKey keeps its getTime()", fd.getTime() === fdBefore, true);

// ---------- Summary ----------
let scenariosPassed = 0;
let scenariosFailed = 0;
let rowsPassed = 0;
let rowsTotal = 0;
for (const [name, t] of tally) {
  rowsPassed += t.pass;
  rowsTotal += t.total;
  if (t.pass === t.total) scenariosPassed++;
  else scenariosFailed++;
  console.log(`SCENARIO ${t.pass === t.total ? "PASS" : "FAIL"} | ${t.r} | ${name} | ${t.pass}/${t.total} rows`);
}
console.log(`SUMMARY scenarios_pass=${scenariosPassed} scenarios_fail=${scenariosFailed} rows_pass=${rowsPassed} rows_total=${rowsTotal}`);
process.exitCode = scenariosFailed === 0 ? 0 : 1;
