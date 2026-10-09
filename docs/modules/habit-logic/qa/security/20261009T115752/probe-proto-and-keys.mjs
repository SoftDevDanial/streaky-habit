// Security probe: prototype pollution and unknown-key carry-over through habit objects whose keys come
// from parsed storage. Includes negative controls (spread, Object.assign) that show the checks can fail.
import { writeFileSync } from "node:fs";
import * as dates from "../../../../../../src/dates.js";
import * as habits from "../../../../../../src/habits.js";

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
let failures = 0;
const check = (label, ok) => {
  if (!ok) failures++;
  log(ok ? "PASS" : "FAIL", label);
};

const TODAY = "2026-10-08";
const objectProtoBefore = Object.getOwnPropertyNames(Object.prototype).sort().join(",");
const arrayProtoBefore = Object.getOwnPropertyNames(Array.prototype).sort().join(",");
const functionProtoBefore = Object.getOwnPropertyNames(Function.prototype).sort().join(",");

// Shape an attacker on the same origin could plant in localStorage.
const hostileJson = `[
  {"name":"Read","done":["2026-10-07","2026-10-08"],
   "__proto__":{"polluted":"yes","isAdmin":true},
   "constructor":{"prototype":{"polluted2":"yes"}},
   "prototype":{"polluted3":"yes"},
   "extra":"carried?"},
  {"name":"__proto__","done":["2026-10-06"]},
  {"name":"constructor","done":[]},
  {"name":"prototype","done":["__proto__","constructor","prototype","toString","2026-10-08"]}
]`;
const parsed = JSON.parse(hostileJson);
log("input: parsed[0] own keys =", JSON.stringify(Object.keys(parsed[0])));
log("input: parsed[0] prototype is Object.prototype =", Object.getPrototypeOf(parsed[0]) === Object.prototype);

// Negative controls: the two copy styles the threat model forbids, so the checks below are not vacuous.
const spread = { ...parsed[0] };
const assigned = Object.assign({}, parsed[0]);
log("control: spread own keys =", JSON.stringify(Object.keys(spread)), "(carries __proto__, constructor, prototype, extra)");
log("control: Object.assign swaps prototype =", Object.getPrototypeOf(assigned) !== Object.prototype,
  "and assigned.polluted =", assigned.polluted, "assigned.isAdmin =", assigned.isAdmin);

function checkHabitShape(label, habit) {
  const keys = Object.getOwnPropertyNames(habit).sort();
  check(`${label}: own keys exactly done,name (got ${JSON.stringify(keys)})`, JSON.stringify(keys) === '["done","name"]');
  check(`${label}: prototype is Object.prototype`, Object.getPrototypeOf(habit) === Object.prototype);
  check(`${label}: no inherited polluted/isAdmin`, habit.polluted === undefined && habit.isAdmin === undefined);
  check(`${label}: done is a plain array`, Array.isArray(habit.done) && Object.getPrototypeOf(habit.done) === Array.prototype);
}

const results = {
  "toggleDay in window": habits.toggleDay(parsed, 0, TODAY, TODAY),
  "toggleDay outside window": habits.toggleDay(parsed, 1, "2026-10-01", TODAY),
  "toggleDay index 3": habits.toggleDay(parsed, 3, "2026-10-07", TODAY),
  "deleteHabit 3": habits.deleteHabit(parsed, 3),
  "deleteHabit none": habits.deleteHabit(parsed, 99),
};
for (const [label, list] of Object.entries(results)) {
  list.forEach((habit, position) => checkHabitShape(`${label} [${position}]`, habit));
}

const added = habits.addHabit(parsed, "Walk");
check("addHabit ok", added.ok === true);
added.habits.forEach((habit, position) => checkHabitShape(`addHabit [${position}]`, habit));

// Names that are prototype words are just names.
for (const name of ["__proto__", "constructor", "prototype", "hasOwnProperty", "toString", "valueOf"]) {
  const result = habits.validateName(name, []);
  check(`validateName("${name}") is ok with the same name`, result.ok === true && result.name === name);
  const dup = habits.validateName(name.toUpperCase(), [name]);
  check(`validateName duplicate of "${name}" is caught`, dup.ok === false && dup.error === "duplicate");
  const add = habits.addHabit([], name);
  check(`addHabit("${name}") gives a plain { name, done }`, add.ok && Object.getPrototypeOf(add.habits[0]) === Object.prototype
    && Object.getOwnPropertyNames(add.habits[0]).sort().join() === "done,name" && add.habits[0].name === name);
}

// Prototype words as done entries (decoder bypass, defence in depth): counted through a Map, never an object.
const cells = habits.heatmapCells(parsed, TODAY);
check("heatmapCells returns 84 cells", cells.length === 84);
const cellKeys = "column,count,future,key,level,row,today,total";
check("every cell has exactly the contract keys and Object.prototype",
  cells.every((cell) => Object.getOwnPropertyNames(cell).sort().join() === cellKeys && Object.getPrototypeOf(cell) === Object.prototype));
check("today cell counts 2 (Read and prototype habit both have 2026-10-08)", cells.find((c) => c.today).count === 2);
log("bestStreak(prototype-word done) =", habits.bestStreak(parsed[3].done),
  "currentStreak =", habits.currentStreak(parsed[3].done, TODAY), "runContinues =", habits.runContinues(parsed[3].done, TODAY));

// Habits with a null prototype are copied into ordinary objects.
const nullProto = Object.assign(Object.create(null), { name: "Null", done: ["2026-10-08"] });
checkHabitShape("toggleDay of a null-prototype habit", habits.toggleDay([nullProto], 0, "2026-10-07", TODAY)[0]);

// isDateKey never coerces an object, so a hostile toString or getter never runs.
let coerced = 0;
const sneaky = { toString() { coerced++; return "2026-10-08"; }, valueOf() { coerced++; return 1; },
  [Symbol.toPrimitive]() { coerced++; return "2026-10-08"; } };
check("isDateKey(object with toString) is false", dates.isDateKey(sneaky) === false);
check("isDateKey never coerced the object", coerced === 0);
const proxy = new Proxy({}, { get() { coerced++; return () => "2026-10-08"; } });
check("isDateKey(proxy) is false and never touched it", dates.isDateKey(proxy) === false && coerced === 0);

// Global prototypes are unchanged and nothing leaked onto a fresh object.
check("Object.prototype own names unchanged", Object.getOwnPropertyNames(Object.prototype).sort().join(",") === objectProtoBefore);
check("Array.prototype own names unchanged", Object.getOwnPropertyNames(Array.prototype).sort().join(",") === arrayProtoBefore);
check("Function.prototype own names unchanged", Object.getOwnPropertyNames(Function.prototype).sort().join(",") === functionProtoBefore);
check("({}).polluted, isAdmin, polluted2, polluted3 all undefined",
  [{}.polluted, {}.isAdmin, {}.polluted2, {}.polluted3].every((v) => v === undefined));

log(`\nfailures: ${failures}`);
const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-proto-and-keys.txt", import.meta.url), text);
process.stdout.write(text);
