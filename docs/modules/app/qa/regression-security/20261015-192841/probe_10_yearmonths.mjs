// Security finder (read-only), regression 2026-10-15, HEAD ddf43f6. CS-01, the year 10000 residual (1.0 SEC-05).
// Calls the real src/habits.js `yearMonths`, `yearStart` and `toggleDay` with today keys a device clock in the year
// 10000 or later gives (`localDateKey` writes a five or six digit year). Each `yearMonths` call runs in its own worker
// with a heap cap and a time budget, so a call that never returns is reported, not waited on.
// Outcomes: "returned" (with the months), "threw" (with the message), "out-of-memory" (the worker hit its heap cap,
// so memory grew without bound), "timed-out" (terminated after the budget). Prints JSON lines to stdout only.
// Run: timeout 300 node probe_10_yearmonths.mjs
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";

const SRC = new URL("../../../../../../src/", import.meta.url);
const HEAP_MB = 256;
const BUDGET_MS = 20000;

if (!isMainThread) {
  const { yearMonths } = await import(new URL("habits.js", SRC));
  const started = performance.now();
  try {
    const months = yearMonths(workerData.today);
    const open = months.flatMap((m) => m.days.filter((d) => d.kind === "open").map((d) => d.key));
    parentPort.postMessage({
      outcome: "returned",
      ms: Math.round(performance.now() - started),
      months: months.length,
      firstMonth: months[0]?.key,
      lastMonth: months.at(-1)?.key,
      openDays: open.length,
      openSample: open.slice(0, 3).concat(open.length > 3 ? ["...", ...open.slice(-2)] : []),
      open,
    });
  } catch (error) {
    parentPort.postMessage({ outcome: "threw", ms: Math.round(performance.now() - started), error: `${error.name}: ${error.message}` });
  }
} else {
  const { yearStart, toggleDay } = await import(new URL("habits.js", SRC));
  const { isDateKey } = await import(new URL("dates.js", SRC));
  const todays = [
    ["control", "2026-10-10"],
    ["control", "9999-10-15"],
    ["control", "9999-12-31"],
    ["year 10000, January (CS-01's date)", "10000-01-05"],
    ["year 10000, September", "10000-09-30"],
    ["year 10000, October", "10000-10-01"],
    ["year 10000, mid October", "10000-10-15"],
    ["year 10000, December", "10000-12-31"],
    ["year 10009, November", "10009-11-30"],
    ["year 10010, October", "10010-10-15"],
    ["year 10015, November", "10015-11-20"],
    ["year 99999, December", "99999-12-31"],
    ["year 100000, October", "100000-10-15"],
  ];
  const run = (today) =>
    new Promise((resolve) => {
      const started = performance.now();
      const worker = new Worker(new URL(import.meta.url), {
        workerData: { today },
        resourceLimits: { maxOldGenerationSizeMb: HEAP_MB, maxYoungGenerationSizeMb: 16 },
      });
      let settled = false;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        worker.terminate().then(() => resolve({ ...result, wallMs: Math.round(performance.now() - started) }));
      };
      const timer = setTimeout(() => finish({ outcome: "timed-out", budgetMs: BUDGET_MS }), BUDGET_MS);
      worker.on("message", finish);
      worker.on("error", (error) =>
        finish({ outcome: error.code === "ERR_WORKER_OUT_OF_MEMORY" ? "out-of-memory" : "worker-error", error: `${error.code ?? error.name}: ${error.message}`, heapCapMb: HEAP_MB }),
      );
    });
  console.log(JSON.stringify({ probe: "yearMonths at far clocks", node: process.version, heapCapMb: HEAP_MB, budgetMs: BUDGET_MS }));
  for (const [label, today] of todays) {
    const result = await run(today);
    const habit = [{ name: "Read", done: [] }];
    const doneToday = toggleDay(habit, 0, today, today)[0].done.length === 1;
    let acceptedOpen = null;
    if (result.outcome === "returned") {
      acceptedOpen = result.open.filter((key) => toggleDay(habit, 0, key, today)[0].done.length === 1);
    }
    const { open, ...shown } = result;
    console.log(
      JSON.stringify({
        label,
        today,
        isDateKeyToday: isDateKey(today),
        yearStart: yearStart(today),
        doneTodayAccepted: doneToday,
        yearMonths: shown,
        openDaysToggleDayAccepts: acceptedOpen === null ? null : { count: acceptedOpen.length, sample: acceptedOpen.slice(0, 3) },
      }),
    );
  }
  // habit-logic O1: the text comparison accepts a four digit key in the year 1000 for a five digit today. Offered by no control.
  const habit = [{ name: "Read", done: [] }];
  for (const [today, key] of [["10000-01-05", "1000-06-01"], ["10000-10-15", "1000-06-01"], ["10000-10-15", "9999-12-31"], ["10000-01-01", "9999-12-31"]]) {
    console.log(JSON.stringify({ toggleDay: { today, key, accepted: toggleDay(habit, 0, key, today)[0].done.length === 1, keyIsDateKey: isDateKey(key) } }));
  }
}
