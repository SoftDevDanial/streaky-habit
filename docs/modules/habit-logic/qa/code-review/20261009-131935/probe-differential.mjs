// Differential check: current src/ (HEAD) against the same exports at three older commits, on valid input.
//   09c5047  the first build, before the WR-01 to WR-10 solver round
//   59c6ee5  after the solver round, before the security fixes
//   eb2003b  after the first security round (bound and name length), before streakDays
// The old sources are read with `git show` and loaded in memory from data: URLs, so nothing is written.
// Valid input must give identical results. Two controls prove the comparison can fail:
//   control 1: keys that fail isDateKey, where streakDays is meant to change the answer (eb2003b only,
//              because 09c5047 and 59c6ee5 have no size bound and never return on those keys)
//   control 2: a bestStreak with one deliberately wrong result
import { execFileSync } from "node:child_process";

const root = new URL("../../../../../../", import.meta.url);
const git = (...args) => execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });

async function atRevision(rev) {
  const datesUrl = `data:text/javascript;base64,${Buffer.from(git("show", `${rev}:src/dates.js`)).toString("base64")}`;
  const habitsText = git("show", `${rev}:src/habits.js`).replace('"./dates.js"', JSON.stringify(datesUrl));
  const habitsUrl = `data:text/javascript;base64,${Buffer.from(habitsText).toString("base64")}`;
  return { rev, dates: await import(datesUrl), habits: await import(habitsUrl) };
}

const head = {
  rev: "HEAD",
  dates: await import(new URL("src/dates.js", root).href),
  habits: await import(new URL("src/habits.js", root).href),
};
const olds = [await atRevision("09c5047"), await atRevision("59c6ee5"), await atRevision("eb2003b")];

// ---- seeded random input
let seed = 0x5eed2026;
const random = () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const int = (low, high) => low + Math.floor(random() * (high - low + 1));
const pick = (list) => list[int(0, list.length - 1)];

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
    else if (mode === 1) day = today - i; // a run ending today
    else if (mode === 2) day = today - 1 - i; // a run ending yesterday
    else day = today - int(0, 2000);
    if (random() < 0.15 && i > 0) continue; // a gap
    done.push(keyOfDay(Math.max(MIN_DAY, Math.min(MAX_DAY, day))));
  }
  if (random() < 0.3) done.push(...done.slice(0, int(0, 5))); // duplicates
  if (random() < 0.5) done.sort(() => random() - 0.5); // any order
  return done;
}

const habitsNear = (today) =>
  Array.from({ length: int(0, 12) }, (_, i) => {
    const done = [...new Set(doneNear(today, int(0, 30)))].sort();
    return { name: `Habit ${i}`, done };
  });

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const results = [];
function compare(label, make, call) {
  const mismatches = Object.fromEntries(olds.map((v) => [v.rev, 0]));
  const examples = [];
  const cases = make();
  for (const input of cases) {
    const expected = call(head, input);
    for (const old of olds) {
      let actual;
      try {
        actual = call(old, input);
      } catch (error) {
        actual = `THROW ${error.message}`;
      }
      if (!same(expected, actual)) {
        mismatches[old.rev]++;
        if (examples.length < 2) examples.push({ rev: old.rev, input: JSON.stringify(input).slice(0, 160), head: JSON.stringify(expected).slice(0, 60), old: JSON.stringify(actual).slice(0, 60) });
      }
    }
  }
  results.push({ label, cases: cases.length, mismatches, examples });
}

// ---- valid input
compare("currentStreak", () => Array.from({ length: 20000 }, () => { const t = todayDay(); return { done: doneNear(t, int(0, 50)), today: keyOfDay(t) }; }), (v, i) => v.habits.currentStreak(i.done, i.today));
compare("bestStreak", () => Array.from({ length: 20000 }, () => doneNear(todayDay(), int(0, 50))), (v, i) => v.habits.bestStreak(i));
compare("runContinues", () => Array.from({ length: 20000 }, () => { const t = todayDay(); return { done: doneNear(t, int(0, 50)), today: keyOfDay(t) }; }), (v, i) => v.habits.runContinues(i.done, i.today));
compare("toggleDay", () => Array.from({ length: 10000 }, () => { const t = todayDay(); return { habits: habitsNear(t), index: int(-1, 13), key: keyOfDay(t - int(-2, 9)), today: keyOfDay(t) }; }), (v, i) => v.habits.toggleDay(i.habits, i.index, i.key, i.today));
compare("weekWindow", () => Array.from({ length: 5000 }, () => keyOfDay(todayDay())), (v, i) => v.habits.weekWindow(i));
compare("heatmapCells (every day 1995 to 2035)", () => { const out = []; for (let d = Date.UTC(1995, 0, 1) / 86400000; d <= Date.UTC(2035, 11, 31) / 86400000; d++) out.push({ habits: habitsNear(d), today: keyOfDay(d) }); return out; }, (v, i) => v.habits.heatmapCells(i.habits, i.today));
compare("monthLabels (every day 1995 to 2035)", () => { const out = []; for (let d = Date.UTC(1995, 0, 1) / 86400000; d <= Date.UTC(2035, 11, 31) / 86400000; d++) out.push(keyOfDay(d)); return out; }, (v, i) => v.habits.monthLabels(i));
compare("heatmapCells and monthLabels (random days over the valid range)", () => Array.from({ length: 4000 }, () => { const t = todayDay(); return { habits: habitsNear(t), today: keyOfDay(t) }; }), (v, i) => [v.habits.heatmapCells(i.habits, i.today), v.habits.monthLabels(i.today)]);
compare("heatLevel", () => Array.from({ length: 5000 }, () => { const total = int(0, 14); return [int(0, total), total]; }), (v, [c, t]) => v.habits.heatLevel(c, t));
compare("addDays", () => Array.from({ length: 30000 }, () => ({ key: keyOfDay(int(MIN_DAY + 5000, MAX_DAY - 5000)), days: int(-4000, 4000) })), (v, i) => v.dates.addDays(i.key, i.days));
compare("dayParts, shortDate, longDate", () => Array.from({ length: 30000 }, () => keyOfDay(int(MIN_DAY, MAX_DAY))), (v, k) => [v.dates.dayParts(k), v.dates.shortDate(k), v.dates.longDate(k)]);
compare("isDateKey (valid keys, near misses, hostile text)", () => {
  const out = [];
  for (let i = 0; i < 20000; i++) {
    const key = keyOfDay(int(MIN_DAY, MAX_DAY));
    out.push(key, key.replace(/-(\d\d)$/, "-$1x"), ` ${key}`, key.slice(0, 8) + String(int(28, 33)), "9".repeat(int(1, 30)), "");
  }
  return out;
}, (v, k) => v.dates.isDateKey(k));

// ---- names
const pieces = ["a", "b", "Z", "é", "É", "ß", "ẞ", "İ", " ", "  ", "\t", " ", " ", "　", "﻿", "​", "一", "字", "\u{1F4DA}", "\u{1F600}", "\uD800", "\uDC00", "é", "0", "1", "-"];
const randomName = () => {
  const target = pick([0, 1, 5, 38, 39, 40, 40, 41, 41, 42, 45, 80]);
  let text = "";
  for (let i = 0; i < target; i++) text += pick(pieces);
  if (random() < 0.4) text = pick(["  ", " ", "﻿ ", "\t"]) + text + pick(["", " ", "　"]);
  return text;
};
const existing = ["Read 20 pages", "Stretch 10 minutes", "İ", "É", "ß", "Habit 1"];
compare("validateName", () => Array.from({ length: 40000 }, () => ({ raw: randomName(), existing: random() < 0.3 ? [...existing, randomName().trim()] : existing })), (v, i) => v.habits.validateName(i.raw, i.existing));
compare("addHabit", () => Array.from({ length: 8000 }, () => { const habits = habitsNear(20000).slice(0, int(0, 13)); return { habits: habits.length >= 12 && random() < 0.5 ? habits.slice(0, 11) : habits, raw: random() < 0.5 ? randomName() : pick(["Drink water", "habit 1", "  Read 20 pages  ", "x".repeat(41)]) }; }), (v, i) => v.habits.addHabit(i.habits, i.raw));
compare("deleteHabit", () => Array.from({ length: 5000 }, () => ({ habits: habitsNear(20000), index: int(-2, 14) })), (v, i) => v.habits.deleteHabit(i.habits, i.index));

// ---- weekdayIndex against an independent reference (the Sunday-first UTC weekday), HEAD only
let weekdayMismatches = 0;
let weekdayCases = 0;
for (let d = MIN_DAY; d <= MAX_DAY; d += 1) {
  const reference = (new Date(d * 86400000).getUTCDay() + 6) % 7;
  if (head.dates.weekdayIndex(keyOfDay(d)) !== reference) weekdayMismatches++;
  weekdayCases++;
}

// ---- controls
const FAR_START = "24660873954866-12-02";
const FAR_STUCK = "24660873954866-12-04";
const control = [["2026-10-06", "2026-10-07", "2026-10-08", FAR_START, FAR_STUCK]];
for (let i = 0; i < 200; i++) control.push([...doneNear(20000, int(0, 20)), FAR_START, FAR_STUCK]);
const bound = olds[2];
const controlMismatches = control.filter(
  (done) => !same([head.habits.bestStreak(done), head.habits.currentStreak(done, "2026-10-08")], [bound.habits.bestStreak(done), bound.habits.currentStreak(done, "2026-10-08")]),
).length;
const wrongBest = (done) => head.habits.bestStreak(done) + (done.length === 7 ? 1 : 0);
const sabotageInputs = Array.from({ length: 3000 }, () => doneNear(20000, int(0, 12)));
const sabotageMismatches = sabotageInputs.filter((done) => !same(head.habits.bestStreak(done), wrongBest(done))).length;

console.log(`pid ${process.pid}`);
console.log("VALID INPUT, HEAD against 09c5047 / 59c6ee5 / eb2003b (mismatch counts)");
for (const { label, cases, mismatches, examples } of results) {
  console.log(`${label.padEnd(66)} cases ${String(cases).padStart(6)}  mismatches ${Object.values(mismatches).join(" / ")}`);
  for (const example of examples) console.log("   EXAMPLE", JSON.stringify(example));
}
console.log(`weekdayIndex against the UTC weekday, every day 0001-01-01 to 9999-12-31: ${weekdayCases} cases, ${weekdayMismatches} mismatches`);
console.log("");
console.log("CONTROL 1, histories with two keys that fail isDateKey (streakDays should change the answer), HEAD against eb2003b");
console.log(`cases ${control.length}, differing: ${controlMismatches}`);
console.log("CONTROL 2, a deliberately wrong bestStreak (7 entries gives +1) must be seen");
console.log(`cases ${sabotageInputs.length}, mismatches ${sabotageMismatches}`);
