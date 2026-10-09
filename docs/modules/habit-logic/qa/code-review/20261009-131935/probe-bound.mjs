// Is the `length < days.size` bound in runLength ever the thing that ends a walk?
// Run under MUTANT=bound-counter (bound turned into a counter, same behaviour) and under
// MUTANT=bound-counter-no-filter (control: isDateKey filter off, so the counter must fire).
// Drives only exported functions: currentStreak and bestStreak.
import { currentStreak, bestStreak } from "../../../../../../src/habits.js";
import { addDays, isDateKey } from "../../../../../../src/dates.js";

let seed = 20261009;
const random = () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const keyOfDay = (day) => new Date(day * 86400000).toISOString().slice(0, 10);
const MIN_DAY = -719162; // 0001-01-01
const MAX_DAY = 2932896; // 9999-12-31

const FAR_START = "24660873954866-12-02";
const FAR_STUCK = "24660873954866-12-04";
const cycle = ["0000-01-03"];
while (cycle.length < 12) cycle.push(addDays(cycle.at(-1), -1));
const spellings = [];
for (const space of ["", " ", "\t", " ", " ", "　", "﻿"]) {
  for (const other of ["", " ", "\t"]) spellings.push(`${space}24660873954866${other}-12-0${2}`);
}

const histories = [];
// valid histories across the whole valid range, including both ends
for (let i = 0; i < 3000; i++) {
  const centre = i < 100 ? (i % 2 === 0 ? MIN_DAY + (i % 7) : MAX_DAY - (i % 7)) : Math.floor(MIN_DAY + random() * (MAX_DAY - MIN_DAY));
  const size = Math.floor(random() * 40);
  const done = [];
  for (let k = 0; k < size; k++) {
    const day = centre + Math.floor(random() * 30) - 25;
    if (day >= MIN_DAY && day <= MAX_DAY) done.push(keyOfDay(day));
  }
  histories.push({ done, today: keyOfDay(Math.max(MIN_DAY, Math.min(MAX_DAY, centre))) });
}
// a full run along the top and bottom edge of the valid range
histories.push({ done: Array.from({ length: 400 }, (_, k) => keyOfDay(MAX_DAY - k)), today: keyOfDay(MAX_DAY) });
histories.push({ done: Array.from({ length: 400 }, (_, k) => keyOfDay(MIN_DAY + k)), today: keyOfDay(MIN_DAY + 399) });
// keys that fail isDateKey
histories.push({ done: [FAR_START, FAR_STUCK], today: "2026-10-08" });
histories.push({ done: [FAR_START, FAR_STUCK, "2026-10-06", "2026-10-07", "2026-10-08"], today: "2026-10-08" });
histories.push({ done: [...spellings, FAR_STUCK], today: "2026-10-08" });
histories.push({ done: cycle, today: cycle[0] });
histories.push({ done: Array.from({ length: 400 }, (_, k) => addDays("0001-01-10", -k)), today: "0001-01-10" });

let calls = 0;
let invalidKeysSeen = 0;
for (const { done, today } of histories) {
  invalidKeysSeen += done.filter((key) => !isDateKey(key)).length;
  currentStreak(done, today);
  bestStreak(done);
  calls += 2;
}
console.log(`pid ${process.pid}: ${histories.length} histories, ${calls} streak calls, ${invalidKeysSeen} keys that fail isDateKey went in`);
console.log(`size bound fired ${globalThis.__boundHits ?? 0} times`);
