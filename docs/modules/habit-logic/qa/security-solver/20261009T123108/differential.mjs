// Security solver probe: the code before the fixes (59c6ee5, read from git into memory) against the fixed
// code in src/, on the same inputs. A fix that changes any result for a valid input fails here.
// Usage: node differential.mjs streaks|names [control]. It writes no file and copies nothing to disk.
// With "control", the fixed code is replaced by an in-memory copy with a planted off-by-one, which must
// show mismatches, so a clean run is known to be able to fail.
// Inputs come from a seeded generator, so a rerun sees the same cases.
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { isDeepStrictEqual } from "node:util";
import { addDays, isDateKey } from "../../../../../../src/dates.js";

const BEFORE = "59c6ee5";
const root = new URL("../../../../../../", import.meta.url);
const datesUrl = new URL("src/dates.js", root).href;
const IMPORT = 'from "./dates.js"';
const CONTROL_EDITS = {
  streaks: ["length < days.size &&", "length < days.size - 1 &&"],
  names: ["if (++count > limit) return true;", "if (++count >= limit) return true;"],
};

function importSource(source, label) {
  if (source.split(IMPORT).length !== 2) throw new Error(`expected one import of ./dates.js in ${label}`);
  const text = source.replace(IMPORT, `from ${JSON.stringify(datesUrl)}`);
  return import(`data:text/javascript;base64,${Buffer.from(text).toString("base64")}`);
}

function plant(source, [from, to]) {
  if (source.split(from).length !== 2) throw new Error(`control: expected exactly one "${from}" in src/habits.js`);
  return source.replace(from, to);
}

const section = process.argv[2];
const control = process.argv[3] === "control";
const old = await importSource(execFileSync("git", ["show", `${BEFORE}:src/habits.js`], { cwd: root, encoding: "utf8" }), BEFORE);
const fixedSource = readFileSync(new URL("src/habits.js", root), "utf8");
const fixed = await importSource(control ? plant(fixedSource, CONTROL_EDITS[section]) : fixedSource, "src/habits.js");

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
const mismatches = [];
function compare(label, run) {
  cases++;
  const before = run(old);
  const after = run(fixed);
  if (isDeepStrictEqual(before, after)) return;
  mismatchCount++;
  if (mismatches.length < 10) mismatches.push({ label, before, after });
}

console.log(
  `node ${process.version} ${process.platform}, section ${section}, old habits.js from git ${BEFORE}, ` +
    `new habits.js from src/${control ? ` with the planted control edit ${JSON.stringify(CONTROL_EDITS[section])}` : ""}`,
);
let invalidKeys = 0;

if (section === "streaks") {
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
    invalidKeys += keys.filter((key) => !isDateKey(key)).length;
    const today = keyAt(Math.min(SPAN, Math.max(0, pick([centre, centre + between(-3, 300), between(0, SPAN)]))));
    const member = keys.length ? pick(keys) : today;
    for (const day of [today, member, addDays(member, 1)].filter(isDateKey)) {
      compare(`currentStreak #${i} today ${day}`, (m) => m.currentStreak(keys, day));
    }
    compare(`bestStreak #${i}`, (m) => m.bestStreak(keys));
  }

  // The ends of the valid range, where one more step leaves it.
  const atStart = Array.from({ length: 500 }, (_, i) => keyAt(i));
  const atEnd = Array.from({ length: 500 }, (_, i) => keyAt(SPAN - i));
  for (const [label, keys] of [["first 500 days", atStart], ["last 500 days", atEnd], ["both ends", [...atStart, ...atEnd]]]) {
    compare(`bestStreak ${label}`, (m) => m.bestStreak(keys));
    for (const day of [FIRST, "0001-01-02", LAST, "9999-12-30", keyAt(499), keyAt(SPAN - 499)]) {
      compare(`currentStreak ${label} today ${day}`, (m) => m.currentStreak(keys, day));
    }
  }

  // A long unbroken history: 100,000 consecutive days up to 2026-10-08.
  const long = Array.from({ length: 100000 }, (_, i) => addDays("2026-10-08", -i));
  compare("bestStreak 100,000 days", (m) => m.bestStreak(long));
  compare("currentStreak 100,000 days", (m) => m.currentStreak(long, "2026-10-08"));

  // The sample's habits on every day of 2026 and 2027.
  const { default: sample } = await import(new URL("docs/design/sample-history.json", root), { with: { type: "json" } });
  for (const habit of sample.habits) {
    compare(`bestStreak ${habit.name}`, (m) => m.bestStreak(habit.done));
    for (let day = "2026-01-01"; day <= "2027-12-31"; day = addDays(day, 1)) {
      compare(`currentStreak ${habit.name} ${day}`, (m) => m.currentStreak(habit.done, day));
    }
  }
} else if (section === "names") {
  // Pieces that stress the code-point count and the trim: ASCII, white space that trim removes, CJK,
  // a combining mark, astral emoji, lone high and low surrogates (which pair up when adjacent), a
  // zero-width space trim keeps, and capitals whose lower case changes length.
  const PIECES = ["a", "Z", " ", "\t", "\n", " ", " ", "﻿", "一", "é", "\u{1F4DA}",
    "\uD800", "\uDC00", "​", "İ", "."];
  const word = (count) => Array.from({ length: count }, () => pick(PIECES)).join("");

  for (let i = 0; i < 50000; i++) {
    const raw = word(between(0, 60));
    const names = Array.from({ length: between(0, 4) }, () => word(between(0, 45)));
    if (random() < 0.3) names.push(pick([raw, raw.trim(), raw.toUpperCase(), raw.toLowerCase()]));
    compare(`random #${i}`, (m) => m.validateName(raw, names));
  }

  // Every piece alone, 35 to 45 times, with and without padding and as an existing name.
  for (const piece of [...PIECES, "𐀀", "\uDC00\uD800"]) {
    for (let count = 35; count <= 45; count++) {
      const raw = piece.repeat(count);
      for (const [label, text] of [["bare", raw], ["padded", `  ${raw} `], ["prefixed", `x${raw}`]]) {
        compare(`${JSON.stringify(piece)} x${count} ${label}`, (m) => m.validateName(text, []));
        compare(`${JSON.stringify(piece)} x${count} ${label} as existing`, (m) => m.validateName(text, [text.trim()]));
      }
    }
  }

  // Lone surrogates at the 40 and 41 code-point edge, alone and mixed with pairs.
  for (const raw of ["\uD800".repeat(40), "\uD800".repeat(41), "\uDC00".repeat(40), "\uDC00".repeat(41),
    "𐀀".repeat(20) + "\uD800".repeat(20), "𐀀".repeat(20) + "\uD800".repeat(21),
    "\uDC00\uD800".repeat(20), "\uDC00\uD800".repeat(20) + "\uDC00", "\uD800".repeat(39) + "𐀀",
    "\uD800".repeat(40) + "\uDC00"]) {
    compare(`lone surrogates ${raw.length} units`, (m) => m.validateName(raw, []));
  }

  // Oversized names, about the storage quota: same result, with the fixed code's time and heap.
  const gc = globalThis.gc ?? (() => {});
  const oversized = {
    "ASCII x": "x".repeat(5e6),
    "CJK": "一".repeat(5e6),
    "astral emoji": "\u{1F4DA}".repeat(2.5e6),
    "lone high surrogates": "\uD800".repeat(5e6),
  };
  for (const [label, name] of Object.entries(oversized)) {
    compare(`5,000,000 units ${label}`, (m) => m.validateName(name, ["Read 20 pages"]));
    const heap = {};
    for (const [version, module] of [["before", old], ["after", fixed]]) {
      gc();
      gc();
      const startHeap = process.memoryUsage().heapUsed;
      const started = performance.now();
      const result = module.validateName(name, ["Read 20 pages"]);
      const ms = performance.now() - started;
      heap[version] = `${result.ok ? "ok" : result.error} in ${ms.toFixed(3)} ms, heap +${((process.memoryUsage().heapUsed - startHeap) / 1048576).toFixed(2)} MiB`;
    }
    console.log(`${label}: before ${heap.before} | after ${heap.after}`);
  }
} else {
  throw new Error("usage: node differential.mjs streaks|names");
}

if (section === "streaks") console.log(`generated history keys that fail isDateKey: ${invalidKeys}`);
console.log(
  `${cases} cases compared, ${mismatchCount} mismatches${mismatchCount ? `, the first ${mismatches.length}: ${JSON.stringify(mismatches).slice(0, 1500)}` : ""}`,
);
