// Security probe of habit-logic v1.1.0 (security finder, read-only, 2026-10-15). Run from this folder:
//   timeout 300 node probe-v110.mjs
// Prints its results. Writes nothing. Loads src/dates.js and src/habits.js from the project root.
// Parts: 1 source scan of both files (R16 tables, plus regular expressions), 2 runtime traps on clock, random,
// network, timers and globals while every export runs, 3 frozen and proxied inputs for every export (no write),
// 4 toggleDay range fuzz against the rule written independently here, 5 index edge values, 6 doneFlags reads
// each done list once per habit, 7 yearMonths ends and gives 13 months on edge days, and fails fast on a five-digit
// year, 8 prototype integrity with parsed __proto__ keys, 9 cost of the year views with a planted quota-size list.
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../../../../../..");
const say = (...a) => console.log(...a);

// ---------- 1. source scan
say("== 1. source scan");
const CLOCK = { "Date.now": /\bDate\s*\.\s*now\b/, "new Date no arg": /\bnew\s+Date\b(?!\s*\(\s*[^\s)])/, "Date()": /(?<!\bnew\s+|[.\w$])Date\s*\(/,
  "performance.now": /\bperformance\s*\.\s*now\b/, "Math.random": /\bMath\s*\.\s*random\b/, "Temporal.Now": /\bTemporal\s*\.\s*Now\b/ };
const BANNED = /\b(document|window|self|globalThis|navigator|process|localStorage|sessionStorage|indexedDB|caches|fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|setTimeout|setInterval|setImmediate|queueMicrotask|requestAnimationFrame|crypto|Intl|toLocale\w*|eval|Reflect|Proxy|postMessage)\b|\bimport\s*\(|\bFunction\s*\(/g;
for (const file of ["dates.js", "habits.js"]) {
  const text = readFileSync(path.join(root, "src", file), "utf8");
  const code = text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
  const clockHits = Object.entries(CLOCK).filter(([, re]) => re.test(text) || re.test(code)).map(([k]) => k);
  const banned = [...new Set([...code.matchAll(BANNED)].map((m) => m[0]))];
  const regexes = [...code.matchAll(/\/(?![*/])(?:\\.|\[[^\]]*\]|[^/\n\\])+\/[dgimsuyv]*(?=\s*[;,.)])/g)].map((m) => m[0]);
  const imports = [...code.matchAll(/^\s*import\b[^;]*from\s*["']([^"']+)["']/gm)].map((m) => m[1]);
  const objectCopies = [...code.matchAll(/Object\.assign|\{\s*\.\.\./g)].map((m) => m[0]);
  say(file, JSON.stringify({ bytes: text.length, clockHits, banned, regexes, imports, objectCopies }));
}

// ---------- 2. runtime traps
say("== 2. runtime traps while every export runs");
const calls = [];
const RealDate = Date;
globalThis.Date = new Proxy(RealDate, {
  construct(t, args) { if (args.length === 0) calls.push("new Date()"); return Reflect.construct(t, args); },
  apply() { calls.push("Date()"); return RealDate(); },
  get(t, p) { if (p === "now") { return () => { calls.push("Date.now"); return RealDate.now(); }; } return Reflect.get(t, p); },
});
for (const name of ["fetch", "setTimeout", "setInterval", "setImmediate", "queueMicrotask"]) {
  const real = globalThis[name];
  globalThis[name] = (...a) => { calls.push(name); return real?.(...a); };
}
const realRandom = Math.random;
Math.random = () => { calls.push("Math.random"); return realRandom(); };
const realPerfNow = performance.now.bind(performance);
const globalsBefore = new Set(Object.getOwnPropertyNames(globalThis));
const dates = await import(pathToFileURL(path.join(root, "src", "dates.js")).href);
const habits = await import(pathToFileURL(path.join(root, "src", "habits.js")).href);
const sample = [
  { name: "Read 20 pages", done: ["2025-10-10", "2026-09-22", "2026-10-09", "2026-10-10"] },
  { name: "Stretch", done: ["2026-10-08", "2026-10-09"] },
];
const T = "2026-10-10";
const exerciseAll = () => {
  dates.localDateKey(new RealDate(2026, 9, 10)); dates.isDateKey(T); dates.addDays(T, 1); dates.dayParts(T); dates.shortDate(T);
  dates.longDate(T); dates.weekdayIndex(T); dates.yearDate(T); dates.monthTitle(T);
  habits.currentStreak(sample[0].done, T); habits.bestStreak(sample[0].done); habits.toggleDay(sample, 0, "2026-01-01", T);
  habits.heatmapCells(sample, T); habits.monthLabels(T); habits.yearStart(T); habits.doneFlags(sample, T); habits.yearMonths(T);
  habits.validateName(" x ", ["y"]); habits.addHabit(sample, "New"); habits.deleteHabit(sample, 1);
};
for (let i = 0; i < 3; i++) exerciseAll();
Math.random = realRandom;
globalThis.Date = RealDate;
const globalsAdded = Object.getOwnPropertyNames(globalThis).filter((k) => !globalsBefore.has(k));
say("calls recorded:", JSON.stringify(calls), "globals added:", JSON.stringify(globalsAdded), "exports:", JSON.stringify([...Object.keys(dates), ...Object.keys(habits)]));

// ---------- 3. no write to any argument
say("== 3. frozen and proxied inputs");
const writes = [];
const watch = (value, where) => {
  if (value === null || typeof value !== "object") return value;
  const inner = Array.isArray(value) ? value.map((v, i) => watch(v, `${where}[${i}]`)) : Object.fromEntries(Object.entries(value).map(([k, v]) => [k, watch(v, `${where}.${k}`)]));
  Object.freeze(inner);
  return new Proxy(inner, {
    set(t, p) { writes.push(`${where}.${String(p)} set`); return false; },
    defineProperty(t, p) { writes.push(`${where}.${String(p)} define`); return false; },
    deleteProperty(t, p) { writes.push(`${where}.${String(p)} delete`); return false; },
    setPrototypeOf() { writes.push(`${where} setPrototypeOf`); return false; },
  });
};
const thrown = [];
const run = (label, fn) => { try { fn(); } catch (e) { thrown.push(`${label}: ${e.name} ${e.message}`); } };
const w = () => watch(structuredClone(sample), "habits");
run("toggleDay", () => habits.toggleDay(w(), 0, "2026-09-01", T));
run("toggleDay outside", () => habits.toggleDay(w(), 0, "2020-01-01", T));
run("doneFlags", () => habits.doneFlags(w(), "2026-10-10"));
run("heatmapCells", () => habits.heatmapCells(w(), T));
run("yearMonths", () => habits.yearMonths(T));
run("yearStart", () => habits.yearStart(T));
run("addHabit", () => habits.addHabit(w(), "Fresh"));
run("deleteHabit", () => habits.deleteHabit(w(), 0));
run("currentStreak", () => habits.currentStreak(watch([...sample[0].done], "done"), T));
run("bestStreak", () => habits.bestStreak(watch([...sample[0].done], "done")));
run("validateName", () => habits.validateName("x", watch(["a", "b"], "names")));
const shared = habits.toggleDay(sample, 0, "2026-09-01", T);
say("writes:", JSON.stringify(writes), "throws:", JSON.stringify(thrown),
  "result shares an input object:", shared.some((h, i) => h === sample[i] || h.done === sample[i].done));

// ---------- 4. toggleDay range fuzz against an independent rule
say("== 4. toggleDay range fuzz");
const isLeap = (y) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
const daysIn = (y, m) => [31, isLeap(y) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1];
const validKey = (k) => typeof k === "string" && /^\d{4}-\d{2}-\d{2}$/.test(k) && (() => { const [y, m, d] = k.split("-").map(Number); return y >= 1 && m >= 1 && m <= 12 && d >= 1 && d <= daysIn(y, m); })();
const sameDateLastYear = (k) => { const [y, m, d] = k.split("-").map(Number); const dd = m === 2 && d === 29 ? 28 : d; return `${String(y - 1).padStart(4, "0")}-${String(m).padStart(2, "0")}-${String(dd).padStart(2, "0")}`; };
let seed = 12345;
const rnd = (n) => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed % n; };
const pad = (n, w2) => String(n).padStart(w2, "0");
const todays = ["2026-10-10", "2028-02-29", "2027-03-01", "2026-01-01", "0002-01-01", "9999-12-31", "2026-12-31"];
let checked = 0, wrong = [];
for (const today of todays) {
  const start = sameDateLastYear(today);
  for (let i = 0; i < 6000; i++) {
    let key;
    const pick = rnd(6);
    if (pick === 0) key = `${pad(Number(today.slice(0, 4)) - rnd(3), 4)}-${pad(1 + rnd(12), 2)}-${pad(1 + rnd(31), 2)}`;
    else if (pick === 1) key = habits.yearStart(today);
    else if (pick === 2) key = dates.addDays(start, -1 + rnd(3));
    else if (pick === 3) key = dates.addDays(today, -1 + rnd(3));
    else if (pick === 4) key = [" " + today, today + "\n", today.replace("-", "/"), "", null, 20261010, "2026-1-1", "0000-01-01", "10000-01-01", "2026-02-29", "２" + today.slice(1)][rnd(11)];
    else key = `${pad(1 + rnd(9999), 4)}-${pad(rnd(14), 2)}-${pad(rnd(33), 2)}`;
    const before = [{ name: "A", done: ["2026-10-10"] }, { name: "B", done: [] }];
    const after = habits.toggleDay(before, 1, key, today);
    const changed = JSON.stringify(after) !== JSON.stringify(before);
    const allowed = validKey(key) && key >= start && key <= today;
    checked++;
    if (changed !== allowed || JSON.stringify(after[0]) !== JSON.stringify(before[0])) wrong.push([today, key, changed, allowed]);
  }
}
say("cases:", checked, "disagreements with the rule:", JSON.stringify(wrong.slice(0, 10)), "count", wrong.length);

// ---------- 5. index edge values
say("== 5. index edge values");
const edge = {};
for (const [label, index] of [["'0'", "0"], ["0.5", 0.5], ["-0", -0], ["NaN", NaN], ["-1", -1], ["2", 2], ["1e300", 1e300], ["true", true], ["null", null], ["undefined", undefined], ["[0]", [0]]]) {
  const t = habits.toggleDay(sample, index, "2026-09-01", T).map((h) => h.done.includes("2026-09-01"));
  const d = habits.deleteHabit(sample, index).map((h) => h.name);
  edge[label] = { toggled: t, afterDelete: d };
}
say(JSON.stringify(edge));

// ---------- 6. doneFlags reads each done list once
say("== 6. doneFlags reads per call");
const reads = { includes: 0, iterate: 0, index: 0 };
const counted = (list) => new Proxy(list, { get(t, p, r) {
  if (p === "includes") reads.includes++;
  else if (p === Symbol.iterator) reads.iterate++;
  else if (typeof p === "string" && /^\d+$/.test(p)) reads.index++;
  return Reflect.get(t, p, r); } });
const twelve = Array.from({ length: 12 }, (_, i) => ({ name: `H${i}`, done: counted(["2026-10-01", "2026-10-02"]) }));
habits.doneFlags(twelve, "2026-10-05");
say("one call, 12 habits:", JSON.stringify(reads));
for (const k of Object.keys(reads)) reads[k] = 0;
habits.heatmapCells(twelve, T);
say("heatmapCells, 12 habits:", JSON.stringify(reads), "(84 cells, 83 not future)");

// ---------- 7. yearMonths termination and shape
say("== 7. yearMonths");
const ym = {};
const days = ["0001-01-01", "0002-02-28", "1999-12-31", "2000-02-29", "2001-03-01", "2026-10-10", "2028-02-29", "2100-02-28", "2100-03-01", "2400-02-29", "9999-12-31"];
for (const d of days) {
  const t0 = realPerfNow();
  const months = habits.yearMonths(d);
  const open = months.flatMap((m) => m.days).filter((x) => x.kind === "open").length;
  ym[d] = { months: months.length, open, first: months[0].key, last: months.at(-1).key, ms: Math.round(realPerfNow() - t0) };
}
say(JSON.stringify(ym));
for (const bad of ["10000-01-05", "99999-12-31"]) {
  const t0 = realPerfNow();
  try { const m = habits.yearMonths(bad); say(bad, "returned", m.length, "months"); }
  catch (e) { say(bad, "throws", e.name, e.message, `${Math.round(realPerfNow() - t0)} ms`); }
  try { say(bad, "yearStart", habits.yearStart(bad), "toggleDay 1000-06-01 changes:", JSON.stringify(habits.toggleDay(sample, 1, "1000-06-01", bad)[1].done)); }
  catch (e) { say(bad, "yearStart/toggleDay throws", e.name); }
}
let allDays = 0, badShape = [];
for (let k = "2024-01-01"; k <= "2028-12-31"; k = dates.addDays(k, 1)) {
  const months = habits.yearMonths(k);
  const open = months.flatMap((m) => m.days).filter((x) => x.kind === "open").length;
  const expectOpen = (() => { let n = 0; for (let x = habits.yearStart(k); x <= k; x = dates.addDays(x, 1)) n++; return n; })();
  if (months.length !== 13 || open !== expectOpen) badShape.push(k);
  allDays++;
}
say("every day 2024-01-01 to 2028-12-31:", allDays, "days, wrong shape:", JSON.stringify(badShape));

// ---------- 8. prototype integrity
say("== 8. prototype integrity");
const parsed = JSON.parse('[{"name":"A","done":["2026-10-10"],"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":2}},"extra":3}]');
const out = [habits.toggleDay(parsed, 0, "2026-10-09", T), habits.addHabit(parsed, "B").habits, habits.deleteHabit(parsed, 5)];
say("own keys of results:", JSON.stringify(out.map((list) => list.map((h) => Object.keys(h).sort().join(",")))),
  "prototypes plain:", out.every((list) => list.every((h) => Object.getPrototypeOf(h) === Object.prototype)),
  "({}).polluted:", String(({}).polluted), "Object.prototype keys:", Object.getOwnPropertyNames(Object.prototype).length);

// ---------- 9. cost with a planted quota-size list
say("== 9. cost, one habit with 395,000 valid days from 1000-01-01, and 12 x 32,900");
const build = (count, per) => { const list = []; let k = "1000-01-01"; for (let h = 0; h < count; h++) { const done = []; for (let i = 0; i < per; i++) { done.push(k); k = dates.addDays(k, 1); } list.push({ name: `H${h}`, done }); } return list; };
for (const [count, per] of [[1, 395000], [12, 32900]]) {
  const list = build(count, per);
  let t0 = realPerfNow(); habits.heatmapCells(list, T); const band = realPerfNow() - t0;
  t0 = realPerfNow(); for (const m of habits.yearMonths(T)) for (const d of m.days) if (d.kind === "open") habits.doneFlags(list, d.key); const p4 = realPerfNow() - t0;
  t0 = realPerfNow(); for (const h of list) { habits.currentStreak(h.done, T); habits.bestStreak(h.done); } const streaks = realPerfNow() - t0;
  t0 = realPerfNow(); habits.toggleDay(list, 0, "2026-01-15", T); const toggle = realPerfNow() - t0;
  say(`${count} x ${per}: band ${band.toFixed(0)} ms, P4 doneFlags x366 ${p4.toFixed(0)} ms, streaks of every habit ${streaks.toFixed(0)} ms, toggleDay ${toggle.toFixed(0)} ms`);
}
