// Security re-check: cost of the two SEC-01 fix shapes on valid input (400,000 consecutive days, quota
// size) against HEAD's bestStreak and currentStreak, plus a check of the SEC-04 pattern on the real source
// and the Temporal mirror. Read-only on src/ and tests/.
import { readFileSync, writeFileSync } from "node:fs";
import { addDays, isDateKey } from "../../../../../../src/dates.js";
import { bestStreak, currentStreak } from "../../../../../../src/habits.js";

const lines = [`node ${process.version} ${process.platform}`];
const TODAY = "2026-10-08";
const done = [];
for (let key = TODAY, i = 0; i < 400_000; i++, key = addDays(key, -1)) done.unshift(key);
const shuffled = [...done].reverse();

function timed(run) {
  const samples = [];
  let value;
  for (let i = 0; i < 3; i++) {
    const started = performance.now();
    value = run();
    samples.push(performance.now() - started);
  }
  return `${value} in ${samples.sort((a, b) => a - b)[1].toFixed(0)} ms`;
}
function bestVisitOnce(keys) {
  const days = new Set(keys);
  const seen = new Set();
  let best = 0;
  for (const key of days) {
    if (days.has(addDays(key, -1))) continue;
    let length = 0;
    for (let day = key; days.has(day) && !seen.has(day); day = addDays(day, 1)) {
      seen.add(day);
      length++;
    }
    best = Math.max(best, length);
  }
  return best;
}
function bestValidOnly(keys) {
  const days = new Set(keys.filter(isDateKey));
  let best = 0;
  for (const key of days) {
    if (days.has(addDays(key, -1))) continue;
    let length = 0;
    for (let day = key; days.has(day); day = addDays(day, 1)) length++;
    best = Math.max(best, length);
  }
  return best;
}
function currentValidOnly(keys, today) {
  const days = new Set(keys.filter(isDateKey));
  let length = 0;
  for (let day = days.has(today) ? today : addDays(today, -1); days.has(day); day = addDays(day, -1)) length++;
  return length;
}

lines.push("\n## 400,000 consecutive valid days, median of 3");
lines.push(`HEAD bestStreak: ${timed(() => bestStreak(done))}; shuffled: ${timed(() => bestStreak(shuffled))}`);
lines.push(`shape (b) visit each key once: ${timed(() => bestVisitOnce(done))}; shuffled: ${timed(() => bestVisitOnce(shuffled))}`);
lines.push(`shape (a) drop keys that fail isDateKey: ${timed(() => bestValidOnly(done))}; shuffled: ${timed(() => bestValidOnly(shuffled))}`);
lines.push(`HEAD currentStreak: ${timed(() => currentStreak(done, TODAY))}; shape (a) currentStreak: ${timed(() => currentValidOnly(done, TODAY))}`);
lines.push(`isDateKey over the 400,000 keys alone: ${timed(() => done.filter(isDateKey).length)}`);

lines.push("\n## SEC-04 pattern /\\bTemporal\\s*\\.\\s*Now\\b/");
const pattern = /\bTemporal\s*\.\s*Now\b/;
const root = new URL("../../../../../../", import.meta.url);
for (const [label, url] of [
  ["HEAD src/dates.js", new URL("src/dates.js", root)],
  ["HEAD src/habits.js", new URL("src/habits.js", root)],
  ["mirror hunt-Temporal-Now src/habits.js", new URL("./mirrors/hunt-Temporal-Now/src/habits.js", import.meta.url)],
]) {
  lines.push(`${label}: ${pattern.test(readFileSync(url, "utf8")) ? "hit" : "no hit"}`);
}
lines.push(`"Temporal.PlainDate.from(key).add({ days: 1 })": ${pattern.test("Temporal.PlainDate.from(key).add({ days: 1 })") ? "hit" : "no hit"}`);

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-fix-shapes.txt", import.meta.url), text);
process.stdout.write(text);
