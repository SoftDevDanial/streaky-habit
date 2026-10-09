// WR-15. Nothing is written. Compares the working tree's currentStreak and bestStreak (the size bound in
// runLength removed) with the same two functions at the commit before the change (the bound still there,
// read with `git show` and loaded in memory from data: URLs). runLength is used by these two only.
//   1. valid input, seeded random histories over the whole valid range (the reviewer's generators)
//   2. the edges of the valid range: a full run to 9999-12-31 and from 0001-01-01
//   3. input holding keys that fail isDateKey (the stuck key, 49 white-space spellings, the 12-key cycle
//      below year 0001, 400 days back from 0001-01-10): streakDays removes them first, so the old bound
//      was never the thing that ended these walks, and the results must be equal here too
//   control: the old source with the bound set to `length < 1` must differ from the working tree, so the
//      comparison is able to fail
// Run it under run-capped.mjs so a walk that never ends is killed at the cap instead of hanging.
// Usage, from the project root: node <this folder>/run-capped.mjs 120 - <this folder>/bound-differential.mjs <old rev>
import { execFileSync } from "node:child_process";

const root = new URL("../../../../../../", import.meta.url);
const oldRev = process.argv[2] ?? "fa7838d";
const git = (...args) => execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });

async function atRevision(rev, edit = (text) => text) {
  const datesUrl = `data:text/javascript;base64,${Buffer.from(git("show", `${rev}:src/dates.js`)).toString("base64")}`;
  const habitsText = edit(git("show", `${rev}:src/habits.js`)).replace('"./dates.js"', JSON.stringify(datesUrl));
  const habitsUrl = `data:text/javascript;base64,${Buffer.from(habitsText).toString("base64")}`;
  return { habits: await import(habitsUrl), dates: await import(datesUrl) };
}

const head = {
  habits: await import(new URL("src/habits.js", root).href),
  dates: await import(new URL("src/dates.js", root).href),
};
const before = await atRevision(oldRev);
const BOUND = "length < days.size && ";
const sabotaged = await atRevision(oldRev, (text) => {
  if (!text.includes(BOUND)) throw new Error(`the bound text is not in ${oldRev}`);
  return text.replace(BOUND, "length < 1 && ");
});

// ---- seeded random input, same generators as the reviewer's probe-differential.mjs
let seed = 0x5eed2026;
const random = () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const int = (low, high) => low + Math.floor(random() * (high - low + 1));
const MIN_DAY = -719162; // 0001-01-01
const MAX_DAY = 2932896; // 9999-12-31
const keyOfDay = (day) => new Date(day * 86400000).toISOString().slice(0, 10);
const todayDay = () => (random() < 0.3 ? int(18000, 22000) : int(MIN_DAY + 200, MAX_DAY - 200));

function doneNear(today, size) {
  const done = [];
  const mode = int(0, 3);
  for (let i = 0; i < size; i++) {
    let day;
    if (mode === 0) day = today - int(0, 40) + int(0, 3);
    else if (mode === 1) day = today - i;
    else if (mode === 2) day = today - 1 - i;
    else day = today - int(0, 2000);
    if (random() < 0.15 && i > 0) continue;
    done.push(keyOfDay(Math.max(MIN_DAY, Math.min(MAX_DAY, day))));
  }
  if (random() < 0.3) done.push(...done.slice(0, int(0, 5)));
  if (random() < 0.5) done.sort(() => random() - 0.5);
  return done;
}

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const rows = [];
function compare(label, cases) {
  let against = 0;
  let againstSabotaged = 0;
  const examples = [];
  for (const { done, today } of cases) {
    const now = [head.habits.currentStreak(done, today), head.habits.bestStreak(done)];
    const old = [before.habits.currentStreak(done, today), before.habits.bestStreak(done)];
    const wrong = [sabotaged.habits.currentStreak(done, today), sabotaged.habits.bestStreak(done)];
    if (!same(now, old)) {
      against++;
      if (examples.length < 2) examples.push({ done: JSON.stringify(done).slice(0, 120), now, old });
    }
    if (!same(now, wrong)) againstSabotaged++;
  }
  rows.push({ label, count: cases.length, against, againstSabotaged, examples });
}

// 1. valid input
compare("valid, runs ending today or yesterday, random order, duplicates", Array.from({ length: 30000 }, () => {
  const today = todayDay();
  return { done: doneNear(today, int(0, 50)), today: keyOfDay(today) };
}));
compare("valid, any distance from today (runs older than the strip)", Array.from({ length: 30000 }, () => {
  const today = todayDay();
  return { done: doneNear(todayDay(), int(0, 50)), today: keyOfDay(today) };
}));

// 2. the edges of the valid range
compare("valid, a full run along the top and bottom edge of the range", [
  { done: Array.from({ length: 400 }, (_, k) => keyOfDay(MAX_DAY - k)), today: keyOfDay(MAX_DAY) },
  { done: Array.from({ length: 400 }, (_, k) => keyOfDay(MIN_DAY + k)), today: keyOfDay(MIN_DAY + 399) },
  { done: Array.from({ length: 400 }, (_, k) => keyOfDay(MIN_DAY + k)), today: keyOfDay(MIN_DAY) },
  { done: Array.from({ length: 400 }, (_, k) => keyOfDay(MAX_DAY - k)), today: keyOfDay(MAX_DAY - 399) },
]);

// 3. keys that fail isDateKey
const FAR_START = "24660873954866-12-02";
const FAR_STUCK = "24660873954866-12-04";
const cycle = ["0000-01-03"];
while (cycle.length < 12) cycle.push(head.dates.addDays(cycle.at(-1), -1));
const spellings = [];
for (const space of ["", " ", "\t", "\u{A0}", "\u{2003}", "\u{3000}", "\u{FEFF}"]) {
  for (const other of ["", " ", "\t"]) spellings.push(`${space}24660873954866${other}-12-02`);
}
const back400 = [];
for (let key = "0001-01-10"; back400.length < 400; key = head.dates.addDays(key, -1)) back400.push(key);
const withInvalid = [
  { done: [FAR_START, FAR_STUCK], today: "2026-10-08" },
  { done: [FAR_START, FAR_STUCK, "2026-10-06", "2026-10-07", "2026-10-08"], today: "2026-10-08" },
  { done: [...spellings, FAR_STUCK], today: "2026-10-08" },
  { done: cycle, today: cycle[0] },
  { done: back400, today: "0001-01-10" },
  { done: [...back400, FAR_START, FAR_STUCK, ...spellings], today: "0001-01-10" },
];
for (let i = 0; i < 2000; i++) {
  const today = todayDay();
  withInvalid.push({ done: [...doneNear(today, int(0, 20)), FAR_START, FAR_STUCK, ...spellings.slice(0, int(0, spellings.length))], today: keyOfDay(today) });
}
compare("with keys that fail isDateKey (stuck key, spellings, cycle, below 0001)", withInvalid);

console.log(`pid ${process.pid}, working tree against ${oldRev}; the control is ${oldRev} with the bound set to \`length < 1\``);
let total = 0;
let mismatches = 0;
for (const { label, count, against, againstSabotaged, examples } of rows) {
  total += count;
  mismatches += against;
  console.log(`${label.padEnd(72)} cases ${String(count).padStart(6)}  differ from ${oldRev}: ${against}  differ from the control: ${againstSabotaged}`);
  for (const example of examples) console.log("   EXAMPLE", JSON.stringify(example));
}
console.log(`total ${total} cases (each runs currentStreak and bestStreak), ${mismatches} differ from ${oldRev}`);
