// Security re-check 2 of SEC-01 at HEAD. A: the first audit's hanging inputs. B: the re-check's n squared
// input at 20,000 and 90,000 spellings. C: isDateKey, which now runs on every key at every streak call,
// on quota-sized inputs of many shapes. D: valid-input differential against eb2003b and 59c6ee5, loaded
// from git into memory. Every streak call on hostile input runs in a child capped with SIGKILL.
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { addDays, isDateKey } from "../../../../../../src/dates.js";
import * as head from "../../../../../../src/habits.js";

const lines = [];
const output = new URL("./probe-sec01-recheck2.txt", import.meta.url);
const log = (...parts) => {
  lines.push(parts.join(" "));
  console.log(parts.join(" "));
  writeFileSync(output, lines.join("\n") + "\n");
};
const root = new URL("../../../../../../", import.meta.url);
const habitsUrl = new URL("src/habits.js", root).href;
const datesUrl = new URL("src/dates.js", root).href;
const pids = [];
log(`node ${process.version} ${process.platform}`);

function inChild(label, body, capMs = 10_000) {
  const program = `
    import * as habits from ${JSON.stringify(habitsUrl)};
    import * as dates from ${JSON.stringify(datesUrl)};
    const started = performance.now();
    const value = (() => { ${body} })();
    process.stdout.write(JSON.stringify({ value, ms: Math.round(performance.now() - started) }));
  `;
  const started = Date.now();
  const result = spawnSync(process.execPath, ["--input-type=module", "--eval", program], {
    encoding: "utf8", timeout: capMs, killSignal: "SIGKILL", maxBuffer: 16 * 1024 * 1024,
  });
  pids.push(`${result.pid}${result.error?.code === "ETIMEDOUT" ? " (killed at cap)" : ""}`);
  const outcome = result.error?.code === "ETIMEDOUT"
    ? `HUNG: no result within ${capMs / 1000} s, child pid ${result.pid} killed (signal ${result.signal})`
    : `returned ${result.stdout.trim()} (child pid ${result.pid}, exit ${result.status}${result.stderr ? `, stderr ${result.stderr.trim().split("\n").at(-1)}` : ""})`;
  log(`${label}: ${outcome}, wall ${Date.now() - started} ms`);
}

log("\n## A. The first audit's hanging inputs");
inChild('bestStreak(["24660873954866-12-02", "24660873954866-12-04"])',
  'return habits.bestStreak(["24660873954866-12-02", "24660873954866-12-04"]);');
inChild("bestStreak(three valid keys plus the two stuck keys)",
  'return habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", "24660873954866-12-02", "24660873954866-12-04"]);');
inChild('currentStreak(year-0 chain of 30 steps back from 0000-01-03, "0000-01-03")',
  `const done = []; for (let k = "0000-01-03", i = 0; i < 30; i++, k = dates.addDays(k, -1)) done.push(k);
   return habits.currentStreak(done, "0000-01-03");`);
inChild('currentStreak and bestStreak over every day back from 2026-10-08 for 800,000 days',
  `const done = []; for (let k = "2026-10-08", i = 0; i < 800000; i++, k = dates.addDays(k, -1)) done.push(k);
   return [habits.currentStreak(done, "2026-10-08"), habits.bestStreak(done)];`, 30_000);

log("\n## B. Many spellings of one far-out date that run into the stuck key (the re-check's input)");
const STUCK = "24660873954866-12-04";
const START = "24660873954866-12-02";
const WHITE = ["", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ",
  " ", " ", " ", " ", " ", " ", " ", " ", "　", "﻿"];
function spellings(count) {
  const keys = [];
  const size = WHITE.length;
  for (let i = 0; keys.length < count; i++) {
    const slot = (k) => WHITE[Math.floor(i / size ** k) % size];
    const key = `${slot(5)}24660873954866${slot(4)}-${slot(3)}12${slot(2)}-${slot(1)}02${slot(0)}`;
    if (key !== START) keys.push(key);
  }
  return keys;
}
{
  const set = spellings(90_000);
  log(`precondition on 90,000 spellings: distinct ${new Set(set).size === 90_000}, all fail isDateKey ${set.every((k) => !isDateKey(k))}, all have next day STUCK ${set.every((k) => addDays(k, 1) === STUCK)}, all share one absent previous day ${set.every((k) => addDays(k, -1) === addDays(START, -1))}`);
  log(`stored value with 90,000 spellings plus STUCK: ${JSON.stringify({ version: 1, habits: [{ name: "P", done: [...set, STUCK] }] }).length.toLocaleString("en-US")} UTF-16 code units`);
}
for (const n of [4_000, 20_000, 90_000]) {
  inChild(`bestStreak(${n} spellings + STUCK)`,
    `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
     return habits.bestStreak([...spellings(${n}), ${JSON.stringify(STUCK)}]);`);
  inChild(`currentStreak(${n} spellings + STUCK, "2026-10-08")`,
    `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
     return habits.currentStreak([...spellings(${n}), ${JSON.stringify(STUCK)}], "2026-10-08");`);
}
inChild("12 habits of 7,500 spellings each (90,000 keys) plus STUCK: one render (12 x currentStreak, bestStreak, runContinues, plus heatmapCells)",
  `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
   const all = spellings(90000);
   const list = Array.from({ length: 12 }, (_, i) => ({ name: "H" + i, done: [...all.slice(i * 7500, (i + 1) * 7500), ${JSON.stringify(STUCK)}] }));
   for (const h of list) { habits.currentStreak(h.done, "2026-10-08"); habits.bestStreak(h.done); habits.runContinues(h.done, "2026-10-08"); }
   return habits.heatmapCells(list, "2026-10-08").length;`);

log("\n## C. isDateKey on quota-sized inputs (about 2.4 million UTF-16 code units each), median of 3");
function timed(run) {
  const samples = [];
  let value;
  for (let i = 0; i < 3; i++) {
    const started = performance.now();
    value = run();
    samples.push(performance.now() - started);
  }
  return { value, ms: samples.sort((a, b) => a - b)[1] };
}
const UNITS = 2_400_000;
const shapes = {
  "90,000 spellings of the far-out date": () => spellings(90_000),
  "valid keys, consecutive days": () => {
    const keys = [];
    for (let k = "2026-10-08"; keys.length < UNITS / 13; k = addDays(k, -1)) keys.push(k);
    return keys;
  },
  "pattern-shaped but invalid days (2026-02-30)": () => new Array(Math.floor(UNITS / 13)).fill("2026-02-30"),
  "keys of 100 units (valid prefix, then x)": () => new Array(UNITS / 100).fill("2026-10-08" + "x".repeat(90)),
  "keys of 10,000 units": () => new Array(UNITS / 10_000).fill("2026-10-08" + "x".repeat(9_990)),
  "one key of 2,400,000 units": () => ["2026-10-0" + "8".repeat(UNITS - 9)],
  "keys of 100 digits": () => new Array(UNITS / 100).fill("9".repeat(100)),
};
for (const [label, make] of Object.entries(shapes)) {
  const keys = make();
  const units = keys.reduce((sum, key) => sum + key.length, 0);
  const filter = timed(() => keys.filter(isDateKey).length);
  const best = timed(() => head.bestStreak(keys));
  log(`${label}: ${keys.length.toLocaleString("en-US")} keys, ${units.toLocaleString("en-US")} units; filter(isDateKey) ${filter.ms.toFixed(1)} ms (${filter.value} pass, ${(filter.ms * 1e6 / keys.length).toFixed(0)} ns per key); bestStreak ${best.ms.toFixed(1)} ms = ${best.value}`);
}
log("scaling of filter(isDateKey) on valid consecutive keys:");
for (const n of [100_000, 200_000, 400_000, 800_000]) {
  const keys = [];
  for (let k = "9999-12-31"; keys.length < n; k = addDays(k, -1)) keys.push(k);
  log(`  ${n.toLocaleString("en-US")} keys: ${timed(() => keys.filter(isDateKey).length).ms.toFixed(1)} ms`);
}

log("\n## D. Valid input, HEAD against eb2003b and 59c6ee5");
async function load(rev) {
  const show = spawnSync("git", ["show", `${rev}:src/habits.js`], { cwd: root, encoding: "utf8", timeout: 30_000, killSignal: "SIGKILL" });
  pids.push(`${show.pid} (git show ${rev})`);
  if (show.status !== 0) throw new Error(show.stderr);
  const source = show.stdout.replace('from "./dates.js"', `from ${JSON.stringify(datesUrl)}`);
  return import(`data:text/javascript,${encodeURIComponent(source)}`);
}
const versions = { "eb2003b": await load("eb2003b"), "59c6ee5": await load("59c6ee5") };
let seed = 20261009;
const random = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
const starts = ["0001-01-01", "0001-03-01", "1899-12-25", "1999-12-20", "2000-02-20", "2026-10-01", "2028-02-20", "2100-02-20", "9999-11-01"];
const cases = [];
for (let c = 0; c < 20_000; c++) {
  const begin = random() < 0.2 ? starts[Math.floor(random() * starts.length)] : addDays("2026-10-08", -Math.floor(random() * 3000));
  const length = 1 + Math.floor(random() * 120);
  const done = [];
  for (let i = 0; i < length; i++) {
    const key = addDays(begin, i);
    if (isDateKey(key) && random() < 0.8) done.push(key);
    if (random() < 0.05) done.push(key);
  }
  if (random() < 0.5) done.sort(() => random() - 0.5);
  const today = random() < 0.5 ? done[Math.floor(random() * done.length)] ?? begin : addDays(begin, Math.floor(random() * 140) - 10);
  cases.push([done, isDateKey(today) ? today : begin]);
}
{
  const { default: sample } = await import(new URL("docs/design/sample-history.json", root).href, { with: { type: "json" } });
  for (let k = "2026-01-01"; k <= "2027-12-31"; k = addDays(k, 1)) for (const h of sample.habits) cases.push([h.done, k]);
}
for (const [rev, module] of Object.entries(versions)) {
  let mismatches = 0;
  for (const [done, today] of cases) {
    if (module.currentStreak(done, today) !== head.currentStreak(done, today)) mismatches++;
    if (module.bestStreak(done) !== head.bestStreak(done)) mismatches++;
  }
  log(`HEAD against ${rev}: ${cases.length.toLocaleString("en-US")} cases (currentStreak and bestStreak each), ${mismatches} mismatches`);
}
{
  const broken = (done) => head.bestStreak(done.slice(1));
  const control = cases.filter(([done]) => done.length > 1 && broken(done) !== head.bestStreak(done)).length;
  log(`control: dropping the first key changes bestStreak in ${control.toLocaleString("en-US")} cases, so the comparison can see a difference`);
}

log(`\nchild pids: ${pids.join(", ")}`);
