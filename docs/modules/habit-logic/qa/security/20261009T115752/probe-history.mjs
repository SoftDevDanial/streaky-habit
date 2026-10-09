// Security probe: time and memory on large but valid histories (every key passes isDateKey), the worst a
// planted value that survives the storage decoder can carry. One quota-sized history is about 400,000 keys
// (13 JSON bytes each, about 5 MB). Sizes above that cannot come from storage and only show the scaling.
// Every size stays above year 0001: the first run of this probe went to 800,000 and 1,600,000 days, walked
// below year 0001 and hung (see probe-unbounded-loops.txt, section 2). It was killed by its 400 s cap.
// Run with: node --expose-gc probe-history.mjs
import { writeFileSync } from "node:fs";
import { addDays, isDateKey } from "../../../../../../src/dates.js";
import {
  currentStreak, bestStreak, runContinues, toggleDay, heatmapCells,
} from "../../../../../../src/habits.js";

const lines = [];
const output = new URL("./probe-history.txt", import.meta.url);
const log = (...parts) => {
  lines.push(parts.join(" "));
  console.log(parts.join(" "));
  writeFileSync(output, lines.join("\n") + "\n");
};
const gc = globalThis.gc ?? (() => {});
log(`node ${process.version} ${process.platform}`);

const TODAY = "2026-10-08";
function timed(run, repeats = 3) {
  const samples = [];
  for (let i = 0; i < repeats; i++) {
    const started = performance.now();
    run();
    samples.push(performance.now() - started);
  }
  return samples.sort((a, b) => a - b)[Math.floor(repeats / 2)];
}

// n consecutive valid days ending today, oldest first (sorted, as the decoder leaves them).
function run(n, end = TODAY) {
  const keys = new Array(n);
  let key = end;
  for (let i = n - 1; i >= 0; i--) {
    keys[i] = key;
    key = addDays(key, -1);
  }
  return keys;
}

// Deterministic shuffle (Fisher-Yates with a fixed LCG), so runs are repeatable.
function shuffled(keys) {
  const copy = [...keys];
  let seed = 12345;
  for (let i = copy.length - 1; i > 0; i--) {
    seed = (seed * 1103515245 + 12345) % 2147483648;
    const j = seed % (i + 1);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

log("\n## One habit, one unbroken run ending today (the worst case for both streak walks), median of 3, ms");
log("n | JSON size | all valid | currentStreak | bestStreak | bestStreak shuffled | runContinues | toggleDay | heatmapCells");
for (const n of [50_000, 100_000, 200_000, 400_000, 700_000]) {
  const done = run(n);
  const mixed = shuffled(done);
  const bytes = JSON.stringify(done).length;
  const valid = done.every(isDateKey);
  const habit = [{ name: "Planted", done }];
  const cur = timed(() => currentStreak(done, TODAY));
  const best = timed(() => bestStreak(done));
  const bestMixed = timed(() => bestStreak(mixed));
  const flag = timed(() => runContinues(done, TODAY));
  const toggle = timed(() => toggleDay(habit, 0, TODAY, TODAY));
  const heat = timed(() => heatmapCells(habit, TODAY));
  log(`${n} | ${(bytes / 1e6).toFixed(1)} MB | ${valid} | ${cur.toFixed(0)} | ${best.toFixed(0)} | ${bestMixed.toFixed(0)} | ${flag.toFixed(0)} | ${toggle.toFixed(0)} | ${heat.toFixed(0)}`);
}

log("\n## Results stay correct at quota size (400,000 days)");
{
  const done = run(400_000);
  log(`currentStreak = ${currentStreak(done, TODAY)}, bestStreak = ${bestStreak(done)}, first key ${done[0]}`);
}

log("\n## Quota-sized state over 12 habits: one render (12 x currentStreak, bestStreak, runContinues, plus heatmapCells) and one tick (toggleDay plus a render), median of 3");
{
  const per = Math.floor(400_000 / 12);
  const habits = Array.from({ length: 12 }, (_, i) => ({ name: `H${i}`, done: run(per) }));
  const render = () => {
    for (const habit of habits) {
      currentStreak(habit.done, TODAY);
      bestStreak(habit.done);
      runContinues(habit.done, TODAY);
    }
    heatmapCells(habits, TODAY);
  };
  log(`render: ${timed(render).toFixed(0)} ms`);
  log(`tick: ${timed(() => { toggleDay(habits, 0, TODAY, TODAY); render(); }).toFixed(0)} ms`);
}

log("\n## Duplicates (the decoder de-duplicates, this is the module alone): 1,000,000 copies of one key");
{
  const done = new Array(1_000_000).fill(TODAY);
  const toggled = toggleDay([{ name: "D", done }], 0, "2026-10-07", TODAY)[0].done;
  log(`bestStreak ${timed(() => bestStreak(done)).toFixed(0)} ms, currentStreak ${timed(() => currentStreak(done, TODAY)).toFixed(0)} ms, toggleDay ${timed(() => toggleDay([{ name: "D", done }], 0, "2026-10-07", TODAY)).toFixed(0)} ms, toggled done has ${toggled.length} keys`);
}

log("\n## Heap held by the Set one streak call builds, 400,000 keys");
{
  const done = run(400_000);
  gc();
  gc();
  const before = process.memoryUsage().heapUsed;
  const set = new Set(done);
  const after = process.memoryUsage().heapUsed;
  log(`new Set(done): +${((after - before) / 1048576).toFixed(1)} MiB for ${set.size} keys`);
}
