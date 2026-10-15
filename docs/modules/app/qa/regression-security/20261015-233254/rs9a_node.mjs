// Re-check of task 9a in Node (security finder, read-only, 2026-10-15).
// Run: timeout 900 node rs9a_node.mjs <part>   part = diff | sweep
//   diff   yearMonths at a6f7e18 (old/habits.js with old/dates.js, from git show) against the committed src/habits.js,
//          deep-equal for every day 1999-01-01 to 2101-12-31 and the first day of every month 0001 to 9999.
//   sweep  the committed yearMonths, each call in a worker with a 512 MB heap cap and a 600 s timer, over keys written
//          as localDateKey writes them: every day of 10000 to 10200, of 99990 to 100010 and of 275750 to 275760, and
//          the 15th of March and of October of every year 10000 to 275760. Counts returns by length, throws by message,
//          and the slowest call.
import { Worker } from "node:worker_threads";
import { isDeepStrictEqual } from "node:util";
import { pathToFileURL } from "node:url";

const NEW_URL = pathToFileURL("{workspace}/examples/streaks/src/habits.js").href;
const OLD_URL = new URL("./old/habits.js", import.meta.url).href;

const pad = (n, w) => String(n).padStart(w, "0");
const key = (y, m, d) => `${pad(y, 4)}-${pad(m, 2)}-${pad(d, 2)}`;
const leap = (y) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
const dim = (y, m) => (m === 2 && leap(y) ? 29 : [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]);
function* everyDay(y0, y1) {
  for (let y = y0; y <= y1; y++) for (let m = 1; m <= 12; m++) for (let d = 1; d <= dim(y, m); d++) yield key(y, m, d);
}

async function diff() {
  const oldMod = await import(OLD_URL);
  const newMod = await import(NEW_URL);
  const sets = {
    "every day 1999-01-01 to 2101-12-31": [...everyDay(1999, 2101)],
    "first day of every month 0001 to 9999": (() => {
      const out = [];
      for (let y = 1; y <= 9999; y++) for (let m = 1; m <= 12; m++) out.push(key(y, m, 1));
      return out;
    })(),
  };
  for (const [name, keys] of Object.entries(sets)) {
    const t0 = Date.now();
    let differences = 0;
    let notThirteen = 0;
    for (const k of keys) {
      const a = oldMod.yearMonths(k);
      const b = newMod.yearMonths(k);
      if (!isDeepStrictEqual(a, b)) differences++;
      if (b.length !== 13) notThirteen++;
    }
    console.log(JSON.stringify({ part: "diff", set: name, keys: keys.length, differences, newNotThirteen: notThirteen, seconds: (Date.now() - t0) / 1000 }));
  }
}

const SWEEP_WORKER = `
  const { parentPort, workerData } = require("node:worker_threads");
  import(workerData.url).then(({ yearMonths }) => {
    const pad = (n, w) => String(n).padStart(w, "0");
    const key = (y, m, d) => pad(y, 4) + "-" + pad(m, 2) + "-" + pad(d, 2);
    const leap = (y) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
    const dim = (y, m) => (m === 2 && leap(y) ? 29 : [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]);
    const keys = [];
    for (const [y0, y1] of workerData.dayRanges)
      for (let y = y0; y <= y1; y++) for (let m = 1; m <= 12; m++) for (let d = 1; d <= dim(y, m); d++) keys.push(key(y, m, d));
    for (let y = workerData.midFrom; y <= workerData.midTo; y++) { keys.push(key(y, 3, 15)); keys.push(key(y, 10, 15)); }
    const lengths = {}, throws = {};
    let slowest = { ms: 0, key: null }, maxLength = 0;
    for (const k of keys) {
      const t = performance.now();
      try {
        const n = yearMonths(k).length;
        lengths[n] = (lengths[n] || 0) + 1;
        if (n > maxLength) maxLength = n;
      } catch (e) {
        const m = String(e).slice(0, 80);
        throws[m] = (throws[m] || 0) + 1;
      }
      const ms = performance.now() - t;
      if (ms > slowest.ms) slowest = { ms: Math.round(ms * 100) / 100, key: k };
    }
    parentPort.postMessage({ keys: keys.length, lengths, maxLength, throws, slowest });
  });
`;

function sweep() {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const worker = new Worker(SWEEP_WORKER, {
      eval: true,
      workerData: { url: NEW_URL, dayRanges: [[10000, 10200], [99990, 100010], [275750, 275760]], midFrom: 10000, midTo: 275760 },
      resourceLimits: { maxOldGenerationSizeMb: 512 },
    });
    let result = null;
    let why = null;
    const timer = setTimeout(() => { why = "stopped by the timer at 600 s"; worker.terminate(); }, 600_000);
    worker.on("message", (m) => { result = m; });
    worker.on("error", (e) => { why = e.code === "ERR_WORKER_OUT_OF_MEMORY" ? "stopped by the heap cap" : String(e); });
    worker.on("exit", (code) => {
      clearTimeout(timer);
      console.log(JSON.stringify({ part: "sweep", ended: why === null && code === 0 && result !== null, why, exitCode: code, seconds: (Date.now() - t0) / 1000, ...result }));
      resolve();
    });
  });
}

const part = process.argv[2];
if (part === "diff") await diff();
else if (part === "sweep") await sweep();
else console.log("usage: node rs9a_node.mjs diff|sweep");
