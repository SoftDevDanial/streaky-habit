// Security probe: global state, clock, randomness, locale and network reach at run time. Traps are installed
// on globalThis BEFORE the modules load, every export is then called, and the traps and the global object
// are compared. Positive controls prove each trap records a call. No real request is ever made.
import { writeFileSync } from "node:fs";

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
let failures = 0;
const check = (label, ok) => {
  if (!ok) failures++;
  log(ok ? "PASS" : "FAIL", label);
};

const calls = [];
const record = (name) => calls.push(name);

// Network: every global that can send a request.
for (const name of ["fetch", "XMLHttpRequest", "WebSocket", "EventSource", "Request"]) {
  globalThis[name] = new Proxy(function () {}, {
    apply() { record(name); throw new Error(`${name} blocked by probe`); },
    construct() { record(name); throw new Error(`${name} blocked by probe`); },
  });
}
if (globalThis.navigator) {
  try {
    Object.defineProperty(globalThis.navigator, "sendBeacon", { value: () => { record("sendBeacon"); return false; }, configurable: true });
  } catch { /* navigator is not extensible here */ }
}
// Clock and randomness.
const RealDate = Date;
class TrappedDate extends RealDate {
  constructor(...args) {
    if (args.length === 0) record("new Date()");
    super(...args);
  }
  static now() { record("Date.now"); return RealDate.now(); }
}
globalThis.Date = new Proxy(TrappedDate, { apply() { record("Date() call"); return RealDate(); } });
const realNow = performance.now.bind(performance);
performance.now = () => { record("performance.now"); return realNow(); };
const realRandom = Math.random;
Math.random = () => { record("Math.random"); return realRandom(); };
// Timers.
for (const name of ["setTimeout", "setInterval", "setImmediate", "queueMicrotask"]) {
  const real = globalThis[name];
  globalThis[name] = (...args) => { record(name); return real(...args); };
}
// Locale.
const realIntl = Intl;
globalThis.Intl = new Proxy(realIntl, { get(target, key) { record(`Intl.${String(key)}`); return Reflect.get(target, key); } });
for (const [owner, names] of [
  [RealDate.prototype, ["toLocaleString", "toLocaleDateString", "toLocaleTimeString"]],
  [String.prototype, ["toLocaleLowerCase", "toLocaleUpperCase", "localeCompare"]],
  [Number.prototype, ["toLocaleString"]],
]) {
  for (const name of names) {
    const real = owner[name];
    owner[name] = function (...args) { record(name); return real.apply(this, args); };
  }
}

// Positive controls, then reset.
try { fetch("https://probe.invalid/"); } catch { /* expected */ }
new Date();
Date.now();
Math.random();
"x".toLocaleUpperCase();
void Intl.DateTimeFormat;
check(`controls: every trap fires (${calls.join(", ")})`,
  ["fetch", "new Date()", "Date.now", "Math.random", "toLocaleUpperCase", "Intl.DateTimeFormat"].every((n) => calls.includes(n)));
calls.length = 0;

const globalsBefore = new Set(Reflect.ownKeys(globalThis).map(String));
const envBefore = JSON.stringify(process.env);

const dates = await import("../../../../../../src/dates.js");
const habits = await import("../../../../../../src/habits.js");
const { default: sample } = await import("../../../../../../docs/design/sample-history.json", { with: { type: "json" } });

const TODAY = "2026-10-08";
const results = [];
for (let round = 0; round < 3; round++) {
  const list = structuredClone(sample.habits);
  results.push(JSON.stringify([
    dates.localDateKey(new RealDate(2026, 9, 8, 12)),
    ["2026-10-08", "2026-02-29", "x".repeat(1e5), null, {}].map(dates.isDateKey),
    dates.addDays(TODAY, -77), dates.dayParts(TODAY), dates.shortDate(TODAY), dates.longDate(TODAY), dates.weekdayIndex(TODAY),
    habits.weekWindow(TODAY),
    list.map((h) => [habits.currentStreak(h.done, TODAY), habits.bestStreak(h.done), habits.runContinues(h.done, TODAY)]),
    habits.toggleDay(list, 1, TODAY, TODAY), habits.heatmapCells(list, TODAY), habits.heatLevel(2, 3),
    habits.monthLabels(TODAY), habits.validateName("  Drink water ", list.map((h) => h.name)),
    habits.addHabit(list, "Drink water"), habits.deleteHabit(list, 0),
  ]));
}
check(`no network, clock, random, timer or locale call during import and ${results.length} rounds of every export (calls: ${calls.length ? calls.join(", ") : "none"})`, calls.length === 0);
check("three rounds give identical results", results.every((r) => r === results[0]));

const added = [...new Set(Reflect.ownKeys(globalThis).map(String))].filter((k) => !globalsBefore.has(k));
check(`no new property on globalThis (added: ${added.length ? added.join(", ") : "none"})`, added.length === 0);
check("process.env unchanged (TZ, LANG and the rest)", JSON.stringify(process.env) === envBefore);

// Legacy RegExp statics are the one realm-wide value a call can change.
dates.isDateKey("2026-10-08");
log(`note: RegExp.lastMatch after isDateKey("2026-10-08") = ${JSON.stringify(RegExp.lastMatch)}; after a failing string it keeps the last matched key (see probe-strings.txt)`);

log(`\nfailures: ${failures}`);
const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-global-and-egress.txt", import.meta.url), text);
process.stdout.write(text);
