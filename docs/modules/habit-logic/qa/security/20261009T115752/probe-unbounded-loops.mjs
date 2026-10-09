// Security probe: do the streak walks terminate on keys outside the isDateKey domain? Each risky call runs
// in a child Node process with a 5 s cap and SIGKILL, so a hang is measured, reported and cleaned up.
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { addDays, isDateKey } from "../../../../../../src/dates.js";

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
const habitsUrl = new URL("../../../../../../src/habits.js", import.meta.url).href;
const datesUrl = new URL("../../../../../../src/dates.js", import.meta.url).href;
log(`node ${process.version} ${process.platform}`);

function inChild(label, body) {
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
    timeout: 5_000,
    killSignal: "SIGKILL",
  });
  const elapsed = Date.now() - started;
  const outcome = result.error?.code === "ETIMEDOUT"
    ? `HUNG: no result within 5 s, child pid ${result.pid} killed (signal ${result.signal})`
    : `returned ${result.stdout.trim()} (child pid ${result.pid}, exit ${result.status}${result.stderr ? `, stderr ${result.stderr.trim().split("\n").at(-1)}` : ""})`;
  log(`${label}: ${outcome}, wall ${elapsed} ms`);
}

// 1a. A day count of 2^53: past it, adding one day can round back to the same number.
const far = addDays("1970-01-01", 2 ** 53);
log(`\n## 1a. Two-way fixed point at 2^53 days (bestStreak skips it, because its predecessor is itself)`);
log(`K = addDays("1970-01-01", 2 ** 53) = "${far}"; addDays(K, 1) === K: ${addDays(far, 1) === far}; addDays(K, -1) === K: ${addDays(far, -1) === far}; isDateKey(K): ${isDateKey(far)}`);
inChild("control: bestStreak([\"2026-10-08\"])", `return habits.bestStreak(["2026-10-08"]);`);
inChild(`bestStreak(["${far}"])`, `return habits.bestStreak([${JSON.stringify(far)}]);`);

// 1b. Search near 2^53 for a run start whose forward walk ends in a fixed point it can never leave.
log(`\n## 1b. A start key whose next day is a forward fixed point (search near 2^53 days)`);
let start = null;
for (let offset = -40; offset <= 40 && !start; offset++) {
  const candidate = addDays("1970-01-01", 2 ** 53 + offset);
  const next = addDays(candidate, 1);
  if (next !== candidate && addDays(next, 1) === next && addDays(candidate, -1) !== candidate && addDays(candidate, -1) !== next) {
    start = candidate;
  }
}
const stuck = addDays(start, 1);
log(`S = "${start}", addDays(S, -1) = "${addDays(start, -1)}" (not in the set, so S starts a run)`);
log(`addDays(S, 1) = T = "${stuck}", addDays(T, 1) === T: ${addDays(stuck, 1) === stuck}; isDateKey(S): ${isDateKey(start)}, isDateKey(T): ${isDateKey(stuck)}`);
inChild(`bestStreak(["${start}", "${stuck}"])`, `return habits.bestStreak([${JSON.stringify(start)}, ${JSON.stringify(stuck)}]);`);
inChild(`bestStreak(sample-like valid keys plus S and T)`,
  `return habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", ${JSON.stringify(start)}, ${JSON.stringify(stuck)}]);`);
inChild(`currentStreak, runContinues, heatmapCells, toggleDay with S and T in done (no walk reaches them)`,
  `const h = [{ name: "A", done: ["2026-10-07", ${JSON.stringify(start)}, ${JSON.stringify(stuck)}] }];
   return [habits.currentStreak(h[0].done, "2026-10-08"), habits.runContinues(h[0].done, "2026-10-08"),
     habits.heatmapCells(h, "2026-10-08").length, habits.toggleDay(h, 0, "2026-10-08", "2026-10-08")[0].done.length];`);

// 2. Year 0 and before: formatKey writes year -1 as "00-1", which parseKey reads back as year 0, month 1,
// day 12, so walking backwards from 0000-01-01 enters a 12-key cycle.
log("\n## 2. Backward cycle below year 0001");
const chain = [];
for (let key = "0000-01-03", i = 0; i < 30; i++, key = addDays(key, -1)) chain.push(key);
log(`backward from 0000-01-03: ${chain.slice(0, 18).join(" ")} ...`);
log(`isDateKey of each chain key: ${[...new Set(chain)].map((k) => `${k}=${isDateKey(k)}`).join(" ")}`);
inChild(`currentStreak(chain keys, "0000-01-03")`,
  `const done = []; for (let k = "0000-01-03", i = 0; i < 30; i++, k = dates.addDays(k, -1)) done.push(k);
   return habits.currentStreak(done, "0000-01-03");`);
inChild(`currentStreak(every day back from 2026-10-08 for 800,000 days, "2026-10-08") (how the first history probe hung)`,
  `const done = []; for (let k = "2026-10-08", i = 0; i < 800000; i++, k = dates.addDays(k, -1)) done.push(k);
   return habits.currentStreak(done, "2026-10-08");`);
inChild(`same 800,000 keys filtered by isDateKey first (what the decoder would keep)`,
  `const done = []; for (let k = "2026-10-08", i = 0; i < 800000; i++, k = dates.addDays(k, -1)) done.push(k);
   return [habits.currentStreak(done.filter(dates.isDateKey), "2026-10-08"), done.filter(dates.isDateKey).length];`);

// 3. The fix shape: bound each walk by the number of distinct days, a run can never be longer.
log("\n## 3. A bounded walk (length < days.size) terminates on the same inputs");
function boundedRunLength(days, from, step) {
  let length = 0;
  for (let key = from; length < days.size && days.has(key); key = addDays(key, step)) length++;
  return length;
}
function boundedBest(done) {
  const days = new Set(done);
  let best = 0;
  for (const key of days) if (!days.has(addDays(key, -1))) best = Math.max(best, boundedRunLength(days, key, 1));
  return best;
}
log(`boundedBest(["${start}", "${stuck}"]) = ${boundedBest([start, stuck])}`);
{
  const days = new Set(chain);
  log(`bounded current walk over the year-0 chain = ${boundedRunLength(days, "0000-01-03", -1)} (set size ${days.size})`);
}

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-unbounded-loops.txt", import.meta.url), text);
process.stdout.write(text);
