// Differential check: the module against independent reference implementations built on UTC
// millisecond maths (safe, UTC has no DST), over every todayKey from 2023-01-01 to 2030-12-31
// and seeded random histories. Usage: node probe-differential.mjs <project root>
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const root = resolve(process.argv[2]);
const H = await import(pathToFileURL(resolve(root, "src/habits.js")).href);
const DAY = 86_400_000;
const pad = (n, w) => String(n).padStart(w, "0");
const key = (ms) => { const d = new Date(ms); return `${pad(d.getUTCFullYear(), 4)}-${pad(d.getUTCMonth() + 1, 2)}-${pad(d.getUTCDate(), 2)}`; };
const ms = (k) => { const [y, m, d] = k.split("-").map(Number); return Date.UTC(y, m - 1, d); };
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
let seed = 12345;
const rand = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);

function refCurrent(done, today) {
  const s = new Set(done); let t = ms(today); if (!s.has(today)) t -= DAY;
  let n = 0; while (s.has(key(t))) { n++; t -= DAY; } return n;
}
function refBest(done) {
  const sorted = [...new Set(done)].sort(); let best = 0, run = 0, prev = null;
  for (const k of sorted) { run = prev !== null && ms(k) - ms(prev) === DAY ? run + 1 : 1; best = Math.max(best, run); prev = k; }
  return best;
}
const refRun = (done, today) => { const s = new Set(done); return s.has(key(ms(today) - 6 * DAY)) && s.has(key(ms(today) - 7 * DAY)); };
function refLevel(c, t) { if (c === 0 || t === 0) return 0; if (c === t) return 4; const r = c / t; return r <= 1/3 + 1e-12 ? 1 : r <= 2/3 + 1e-12 ? 2 : 3; }
function refCells(habits, today) {
  const t = ms(today); const dow = (new Date(t).getUTCDay() + 6) % 7; const monday = t - dow * DAY; const first = monday - 77 * DAY;
  const out = [];
  for (let i = 0; i < 84; i++) {
    const k = key(first + i * DAY); const future = k > today;
    const count = future ? null : habits.filter((h) => h.done.includes(k)).length;
    out.push({ key: k, column: Math.floor(i / 7) + 1, row: (i % 7) + 1, today: k === today, future, count, total: habits.length, level: future ? null : refLevel(count, habits.length) });
  }
  return out;
}
function refLabels(today) {
  const cells = refCells([], today); const out = []; let prev = -1;
  for (let c = 0; c < 12; c++) { const m = new Date(ms(cells[c * 7].key)).getUTCMonth(); if (m !== prev) out.push({ column: c + 1, month: MONTHS[m] }); prev = m; }
  return out;
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let checked = 0, mismatches = [];
for (let t = Date.UTC(2023, 0, 1); t <= Date.UTC(2030, 11, 31); t += DAY) {
  const today = key(t);
  const habits = Array.from({ length: 1 + Math.floor(rand() * 12) }, (_, h) => ({
    name: `H${h}`,
    done: [...new Set(Array.from({ length: Math.floor(rand() * 120) }, () => key(t - Math.floor(rand() * 200 - 10) * DAY)))].sort(),
  }));
  for (const h of habits) {
    if (H.currentStreak(h.done, today) !== refCurrent(h.done, today)) mismatches.push(["currentStreak", today, h.name]);
    if (H.bestStreak(h.done) !== refBest(h.done)) mismatches.push(["bestStreak", today, h.name]);
    if (H.runContinues(h.done, today) !== refRun(h.done, today)) mismatches.push(["runContinues", today, h.name]);
  }
  if (!same(H.heatmapCells(habits, today), refCells(habits, today))) mismatches.push(["heatmapCells", today]);
  if (!same(H.monthLabels(today), refLabels(today))) mismatches.push(["monthLabels", today]);
  checked++;
}
for (let total = 0; total <= 12; total++) for (let c = 0; c <= total; c++) if (H.heatLevel(c, total) !== refLevel(c, total)) mismatches.push(["heatLevel", c, total]);
console.log("todayKeys checked:", checked, "mismatches:", mismatches.length, JSON.stringify(mismatches.slice(0, 10)));
