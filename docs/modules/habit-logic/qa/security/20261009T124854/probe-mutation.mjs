// Security probe: input mutation and aliasing. Every array and object argument is wrapped in a Proxy that
// records any write (set, defineProperty, deleteProperty, setPrototypeOf, preventExtensions). Results are
// walked to prove no input object is returned. A positive control proves the trap records writes.
import { writeFileSync } from "node:fs";
import * as dates from "../../../../../../src/dates.js";
import * as habits from "../../../../../../src/habits.js";
import sample from "../../../../../../docs/design/sample-history.json" with { type: "json" };

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
let failures = 0;
const check = (label, ok) => {
  if (!ok) failures++;
  log(ok ? "PASS" : "FAIL", label);
};

const proxies = new WeakSet();
function watch(value, path, writes) {
  if (value === null || typeof value !== "object") return value;
  const target = Array.isArray(value)
    ? value.map((child, i) => watch(child, `${path}[${i}]`, writes))
    : Object.fromEntries(Object.entries(value).map(([key, child]) => [key, watch(child, `${path}.${key}`, writes)]));
  const record = (what) => (...args) => {
    writes.push(`${what} ${path}${args[1] !== undefined && typeof args[1] !== "object" ? `.${String(args[1])}` : ""}`);
    return Reflect[what](...args);
  };
  const proxy = new Proxy(target, {
    set: record("set"),
    defineProperty: record("defineProperty"),
    deleteProperty: record("deleteProperty"),
    setPrototypeOf: record("setPrototypeOf"),
    preventExtensions: record("preventExtensions"),
  });
  proxies.add(proxy);
  return proxy;
}

function aliasesIn(value, path = "result", seen = new Set()) {
  if (value === null || typeof value !== "object" || seen.has(value)) return [];
  seen.add(value);
  const own = proxies.has(value) ? [path] : [];
  return own.concat(Object.entries(value).flatMap(([key, child]) => aliasesIn(child, `${path}.${key}`, seen)));
}

// Positive control: a function that sorts its argument in place is caught.
{
  const writes = [];
  const arr = watch(["2026-10-08", "2026-10-01"], "control", writes);
  arr.sort();
  check(`control: an in-place sort is recorded (${writes.length} writes)`, writes.length > 0);
}

const TODAY = "2026-10-08";
const twelve = Array.from({ length: 12 }, (_, i) => ({ name: `Habit ${i + 1}`, done: ["2026-10-0" + ((i % 8) + 1)] }));
const unsorted = [{ name: "Unsorted", done: ["2026-10-05", "2026-09-01", "2026-10-05", "2026-10-08"] }];

const cases = [
  ["weekWindow", () => habits.weekWindow(TODAY)],
  ["currentStreak", (w) => habits.currentStreak(w(sample.habits[0].done), TODAY)],
  ["bestStreak", (w) => habits.bestStreak(w(sample.habits[1].done))],
  ["bestStreak unsorted dupes", (w) => habits.bestStreak(w(unsorted[0].done))],
  ["runContinues", (w) => habits.runContinues(w(sample.habits[1].done), TODAY)],
  ["toggleDay add", (w) => habits.toggleDay(w(sample.habits), 1, TODAY, TODAY)],
  ["toggleDay remove", (w) => habits.toggleDay(w(sample.habits), 0, TODAY, TODAY)],
  ["toggleDay unsorted input", (w) => habits.toggleDay(w(unsorted), 0, "2026-10-03", TODAY)],
  ["toggleDay outside window", (w) => habits.toggleDay(w(sample.habits), 0, "2026-10-01", TODAY)],
  ["toggleDay bad index 99", (w) => habits.toggleDay(w(sample.habits), 99, TODAY, TODAY)],
  ["toggleDay string index", (w) => habits.toggleDay(w(sample.habits), "0", TODAY, TODAY)],
  ["heatmapCells", (w) => habits.heatmapCells(w(sample.habits), TODAY)],
  ["heatLevel", () => habits.heatLevel(2, 3)],
  ["monthLabels", () => habits.monthLabels(TODAY)],
  ["validateName ok", (w) => habits.validateName("  Drink water ", w(sample.habits.map((h) => h.name)))],
  ["validateName duplicate", (w) => habits.validateName("READ 20 PAGES", w(sample.habits.map((h) => h.name)))],
  ["addHabit ok", (w) => habits.addHabit(w(sample.habits), "Drink water")],
  ["addHabit duplicate", (w) => habits.addHabit(w(sample.habits), "read 20 pages")],
  ["addHabit limit", (w) => habits.addHabit(w(twelve), "Thirteen")],
  ["deleteHabit 0", (w) => habits.deleteHabit(w(sample.habits), 0)],
  ["deleteHabit -1", (w) => habits.deleteHabit(w(sample.habits), -1)],
  ["isDateKey object", (w) => dates.isDateKey(w({ year: 2026 }))],
  ["isDateKey array", (w) => dates.isDateKey(w(["2026-10-08"]))],
  ["addDays", () => dates.addDays(TODAY, -6)],
  ["dayParts", () => dates.dayParts(TODAY)],
  ["shortDate", () => dates.shortDate(TODAY)],
  ["longDate", () => dates.longDate(TODAY)],
  ["weekdayIndex", () => dates.weekdayIndex(TODAY)],
];

for (const [label, call] of cases) {
  const writes = [];
  const before = JSON.stringify(sample.habits);
  const result = call((value) => watch(value, "arg", writes));
  check(`${label}: no write to any argument${writes.length ? ` (${writes.join("; ")})` : ""}`, writes.length === 0);
  const aliases = aliasesIn(result);
  check(`${label}: result holds no argument object${aliases.length ? ` (${aliases.join(", ")})` : ""}`, aliases.length === 0);
  check(`${label}: imported sample unchanged`, JSON.stringify(sample.habits) === before);
}

// The Date of localDateKey: its time value and own properties stay as they were.
{
  const date = new Date(2026, 9, 8, 12, 34, 56, 789);
  const time = date.getTime();
  const ownBefore = Reflect.ownKeys(date).length;
  const key = dates.localDateKey(date);
  check(`localDateKey leaves the Date's time value unchanged (${key})`, date.getTime() === time);
  check("localDateKey adds no own property to the Date", Reflect.ownKeys(date).length === ownBefore);
}

// Results are fresh on every call: changing one result never changes a later one (no shared module state).
{
  const w = habits.weekWindow(TODAY);
  w[0] = "tampered";
  w.push("tampered");
  check("weekWindow result is not shared between calls", habits.weekWindow(TODAY)[0] === "2026-10-02" && habits.weekWindow(TODAY).length === 7);
  const parts = dates.dayParts(TODAY);
  parts.weekday = "tampered";
  check("dayParts result is not shared", dates.dayParts(TODAY).weekday === "Thu");
  const name = habits.validateName("", []);
  name.error = "tampered";
  check("validateName failure object is not shared", habits.validateName("", []).error === "empty");
  const limit = habits.addHabit(twelve, "x");
  limit.error = "tampered";
  check("addHabit limit object is not shared", habits.addHabit(twelve, "x").error === "limit");
  const labels = habits.monthLabels(TODAY);
  labels[0].month = "tampered";
  check("monthLabels result is not shared", habits.monthLabels(TODAY)[0].month === "Jul");
  const cells = habits.heatmapCells(sample.habits, TODAY);
  cells[0].count = 999;
  check("heatmapCells result is not shared", habits.heatmapCells(sample.habits, TODAY)[0].count === 3);
}

// Exported constants cannot be reassigned through the module namespace.
{
  let threw = false;
  try {
    habits.MAX_HABITS = 1000;
  } catch {
    threw = true;
  }
  check("assigning habits.MAX_HABITS throws and the value stays 12", threw && habits.MAX_HABITS === 12);
  let threwDelete = false;
  try {
    delete habits.addHabit;
  } catch {
    threwDelete = true;
  }
  check("deleting an export throws and the export stays", threwDelete && typeof habits.addHabit === "function");
}

log(`\nfailures: ${failures}`);
const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-mutation.txt", import.meta.url), text);
process.stdout.write(text);
