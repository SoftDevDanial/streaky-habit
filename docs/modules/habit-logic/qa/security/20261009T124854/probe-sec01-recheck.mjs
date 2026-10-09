// Security re-check of SEC-01 at HEAD. Part A reruns the first audit's hanging inputs. Part B asks whether
// the size bound only turns one endless walk into many long ones: many out-of-domain run starts that all
// walk into one stuck key make bestStreak do about n squared steps. Every call runs in a child Node process
// capped with SIGKILL, so a hang is measured, reported and cleaned up.
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { addDays, isDateKey } from "../../../../../../src/dates.js";

const lines = [];
const output = new URL("./probe-sec01-recheck.txt", import.meta.url);
const log = (...parts) => {
  lines.push(parts.join(" "));
  console.log(parts.join(" "));
  writeFileSync(output, lines.join("\n") + "\n");
};
const habitsUrl = new URL("../../../../../../src/habits.js", import.meta.url).href;
const datesUrl = new URL("../../../../../../src/dates.js", import.meta.url).href;
const pids = [];
log(`node ${process.version} ${process.platform}`);

function inChild(label, body, capMs = 5_000) {
  const program = `
    import * as habits from ${JSON.stringify(habitsUrl)};
    import * as dates from ${JSON.stringify(datesUrl)};
    const started = performance.now();
    const value = (() => { ${body} })();
    process.stdout.write(JSON.stringify({ value, ms: Math.round(performance.now() - started) }));
  `;
  const started = Date.now();
  const result = spawnSync(process.execPath, ["--input-type=module", "--eval", program], {
    encoding: "utf8",
    timeout: capMs,
    killSignal: "SIGKILL",
    maxBuffer: 16 * 1024 * 1024,
  });
  pids.push(`${result.pid}${result.error?.code === "ETIMEDOUT" ? " (killed at cap)" : ""}`);
  const elapsed = Date.now() - started;
  const outcome = result.error?.code === "ETIMEDOUT"
    ? `HUNG: no result within ${capMs / 1000} s, child pid ${result.pid} killed (signal ${result.signal})`
    : `returned ${result.stdout.trim()} (child pid ${result.pid}, exit ${result.status}${result.stderr ? `, stderr ${result.stderr.trim().split("\n").at(-1)}` : ""})`;
  log(`${label}: ${outcome}, wall ${elapsed} ms`);
}

log("\n## A. The first audit's hanging inputs, at HEAD");
inChild('bestStreak(["24660873954866-12-02", "24660873954866-12-04"])',
  'return habits.bestStreak(["24660873954866-12-02", "24660873954866-12-04"]);');
inChild("bestStreak(three valid keys plus the two stuck keys)",
  'return habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", "24660873954866-12-02", "24660873954866-12-04"]);');
inChild('currentStreak(year-0 chain of 30 steps back from 0000-01-03, "0000-01-03")',
  `const done = []; for (let k = "0000-01-03", i = 0; i < 30; i++, k = dates.addDays(k, -1)) done.push(k);
   return habits.currentStreak(done, "0000-01-03");`);
inChild('currentStreak(every day back from 2026-10-08 for 800,000 days, "2026-10-08")',
  `const done = []; for (let k = "2026-10-08", i = 0; i < 800000; i++, k = dates.addDays(k, -1)) done.push(k);
   return habits.currentStreak(done, "2026-10-08");`, 30_000);

log("\n## B. Many run starts that walk into one stuck key");
const STUCK = "24660873954866-12-04";
const START = "24660873954866-12-02";
// parseKey reads each part with Number(), which ignores white space around the digits, so one date has
// many spellings. Each spelling is a distinct key in the Set and a distinct run start. Only characters
// that JSON.stringify writes as one code unit are used, so the stored size stays small.
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
const probeSet = spellings(20_000);
log(`precondition: addDays(STUCK, 1) === STUCK: ${addDays(STUCK, 1) === STUCK}`);
log(`precondition: all 20,000 spellings distinct: ${new Set(probeSet).size === 20_000}; all fail isDateKey: ${probeSet.every((k) => !isDateKey(k))}; all have next day STUCK: ${probeSet.every((k) => addDays(k, 1) === STUCK)}; all have previous day ${JSON.stringify(addDays(START, -1))}: ${probeSet.every((k) => addDays(k, -1) === addDays(START, -1))}`);
for (const n of [20_000, 90_000]) {
  const json = JSON.stringify({ version: 1, habits: [{ name: "Planted", done: [...spellings(n), STUCK] }] });
  log(`stored value with ${n} spellings plus STUCK: ${json.length.toLocaleString("en-US")} UTF-16 code units, ${Buffer.byteLength(json, "utf8").toLocaleString("en-US")} UTF-8 bytes`);
}

for (const n of [500, 1_000, 2_000, 4_000]) {
  inChild(`bestStreak(${n} spellings + STUCK)`,
    `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
     return habits.bestStreak([...spellings(${n}), ${JSON.stringify(STUCK)}]);`, 60_000);
}
inChild("bestStreak(20,000 spellings + STUCK), about 0.5 million code units stored",
  `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
   return habits.bestStreak([...spellings(20000), ${JSON.stringify(STUCK)}]);`, 60_000);
inChild("currentStreak(20,000 spellings + STUCK, 2026-10-08) (one walk only)",
  `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
   return habits.currentStreak([...spellings(20000), ${JSON.stringify(STUCK)}], "2026-10-08");`, 20_000);
inChild("control: the same 20,000 spellings filtered by isDateKey first (what the app decoder accepts)",
  `const WHITE = ${JSON.stringify(WHITE)}; const START = ${JSON.stringify(START)}; ${spellings.toString()};
   const done = [...spellings(20000), START, ${JSON.stringify(STUCK)}].filter(dates.isDateKey);
   return [done.length, habits.bestStreak(done)];`, 20_000);

log("\n## C. Two fix shapes, measured in this process on 90,000 spellings plus STUCK");
const PREVIOUS_DAY = -1;
const NEXT_DAY = 1;
function bestVisitOnce(done) {
  const days = new Set(done);
  const seen = new Set();
  let best = 0;
  for (const key of days) {
    if (days.has(addDays(key, PREVIOUS_DAY))) continue;
    let length = 0;
    for (let day = key; days.has(day) && !seen.has(day); day = addDays(day, NEXT_DAY)) {
      seen.add(day);
      length++;
    }
    best = Math.max(best, length);
  }
  return best;
}
function bestValidOnly(done) {
  const days = new Set(done.filter(isDateKey));
  let best = 0;
  for (const key of days) {
    if (days.has(addDays(key, PREVIOUS_DAY))) continue;
    let length = 0;
    for (let day = key; days.has(day); day = addDays(day, NEXT_DAY)) length++;
    best = Math.max(best, length);
  }
  return best;
}
const big = [...spellings(90_000), STUCK];
for (const [label, fn] of [["visit each key once", bestVisitOnce], ["drop keys that fail isDateKey", bestValidOnly]]) {
  const started = performance.now();
  const value = fn(big);
  log(`${label}: result ${value} in ${Math.round(performance.now() - started)} ms; three valid keys plus the two stuck keys give ${fn(["2026-10-06", "2026-10-07", "2026-10-08", START, STUCK])} (HEAD gives 5)`);
}

log(`\nchild pids: ${pids.join(", ")}`);
