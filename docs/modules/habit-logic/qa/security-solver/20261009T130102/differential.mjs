// Security solver probe (SEC-01, round 2): an earlier habits.js (read from git into memory) against the
// code in src/, on valid input only. A fix that changes any result for a valid input fails here.
// Usage: node differential.mjs <rev> [control]. It writes no file and copies nothing to disk.
// With "control", src/habits.js is replaced by an in-memory copy with the walk bound planted one short,
// which must show mismatches, so a clean run is known to be able to fail.
// Inputs come from a seeded generator, so a rerun sees the same cases. The generator is the round 1 one.
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";
import { addDays, isDateKey } from "../../../../../../src/dates.js";

const root = new URL("../../../../../../", import.meta.url);
const datesUrl = new URL("src/dates.js", root).href;
const IMPORT = 'from "./dates.js"';
const CONTROL_EDIT = ["length < days.size &&", "length < days.size - 1 &&"];

function importSource(source, label) {
  if (source.split(IMPORT).length !== 2) throw new Error(`expected one import of ./dates.js in ${label}`);
  const text = source.replace(IMPORT, `from ${JSON.stringify(datesUrl)}`);
  return import(`data:text/javascript;base64,${Buffer.from(text).toString("base64")}`);
}

const [rev, mode] = process.argv.slice(2);
if (!rev) throw new Error("usage: node differential.mjs <rev> [control]");
const control = mode === "control";
const old = await importSource(execFileSync("git", ["show", `${rev}:src/habits.js`], { cwd: root, encoding: "utf8" }), rev);
let fixedSource = readFileSync(new URL("src/habits.js", root), "utf8");
if (control) {
  if (fixedSource.split(CONTROL_EDIT[0]).length !== 2) throw new Error("control: expected the bound once in src/habits.js");
  fixedSource = fixedSource.replace(...CONTROL_EDIT);
}
const fixed = await importSource(fixedSource, "src/habits.js");

let seed = 20261009;
const random = () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const between = (low, high) => low + Math.floor(random() * (high - low + 1));
const pick = (list) => list[Math.floor(random() * list.length)];

let cases = 0;
let mismatchCount = 0;
let invalidKeys = 0;
const mismatches = [];
function compare(label, keys, run) {
  cases++;
  invalidKeys += keys.filter((key) => !isDateKey(key)).length;
  const before = run(old);
  const after = run(fixed);
  if (isDeepStrictEqual(before, after)) return;
  mismatchCount++;
  if (mismatches.length < 10) mismatches.push({ label, before, after });
}

console.log(
  `node ${process.version} ${process.platform}, habits.js from git ${rev} against src/` +
    `${control ? ` with the planted control edit ${JSON.stringify(CONTROL_EDIT)}` : ""}`,
);

const FIRST = "0001-01-01";
const LAST = "9999-12-31";
const SPAN = 3652058; // days from 0001-01-01 to 9999-12-31
const keyAt = (offset) => addDays(FIRST, offset);

// Runs of 1 to 40 days with gaps, duplicates and shuffled order, around a random day or a range edge.
function history() {
  const centre = pick([between(0, SPAN), between(0, 60), between(SPAN - 60, SPAN), between(738000, 740500)]);
  const keys = [];
  let day = centre;
  for (let run = between(0, 6); run > 0; run--) {
    for (let length = between(1, 40); length > 0 && day <= SPAN; length--) keys.push(keyAt(day++));
    day += between(1, 4);
  }
  for (let extra = between(0, 3); extra > 0 && keys.length; extra--) keys.push(pick(keys));
  for (let i = keys.length - 1; i > 0; i--) {
    const j = between(0, i);
    [keys[i], keys[j]] = [keys[j], keys[i]];
  }
  return { keys, centre };
}

for (let i = 0; i < 20000; i++) {
  const { keys, centre } = history();
  const today = keyAt(Math.min(SPAN, Math.max(0, pick([centre, centre + between(-3, 300), between(0, SPAN)]))));
  const member = keys.length ? pick(keys) : today;
  for (const day of [today, member, addDays(member, 1)].filter(isDateKey)) {
    compare(`currentStreak #${i} today ${day}`, keys, (m) => m.currentStreak(keys, day));
  }
  compare(`bestStreak #${i}`, keys, (m) => m.bestStreak(keys));
}

// The ends of the valid range, where one more step leaves it.
const atStart = Array.from({ length: 500 }, (_, i) => keyAt(i));
const atEnd = Array.from({ length: 500 }, (_, i) => keyAt(SPAN - i));
for (const [label, keys] of [["first 500 days", atStart], ["last 500 days", atEnd], ["both ends", [...atStart, ...atEnd]]]) {
  compare(`bestStreak ${label}`, keys, (m) => m.bestStreak(keys));
  for (const day of [FIRST, "0001-01-02", LAST, "9999-12-30", keyAt(499), keyAt(SPAN - 499)]) {
    compare(`currentStreak ${label} today ${day}`, keys, (m) => m.currentStreak(keys, day));
  }
}

// A long unbroken history: 100,000 consecutive days up to 2026-10-08.
const long = Array.from({ length: 100000 }, (_, i) => addDays("2026-10-08", -i));
compare("bestStreak 100,000 days", long, (m) => m.bestStreak(long));
compare("currentStreak 100,000 days", long, (m) => m.currentStreak(long, "2026-10-08"));

// The sample's habits on every day of 2026 and 2027.
const { default: sample } = await import(new URL("docs/design/sample-history.json", root), { with: { type: "json" } });
for (const habit of sample.habits) {
  compare(`bestStreak ${habit.name}`, habit.done, (m) => m.bestStreak(habit.done));
  for (let day = "2026-01-01"; day <= "2027-12-31"; day = addDays(day, 1)) {
    compare(`currentStreak ${habit.name} ${day}`, habit.done, (m) => m.currentStreak(habit.done, day));
  }
}

console.log(`input keys that fail isDateKey: ${invalidKeys}`);
console.log(
  `${cases} cases compared, ${mismatchCount} mismatches${mismatchCount ? `, the first ${mismatches.length}: ${JSON.stringify(mismatches).slice(0, 1200)}` : ""}`,
);
