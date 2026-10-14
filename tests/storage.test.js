// Unit tests of src/storage.js (app spec, Storage contract and the readable rule, CG-4), the pure exports and, with a
// stand-in localStorage, what loadHabits and saveHabits report (R16, R41).
// Why here and not only in the browser: the browser can see what decodeState keeps only through a later
// save, and cannot see at all whether it returned the parsed objects themselves (threat T2).
import test from "node:test";
import assert from "node:assert/strict";
import { STORAGE_KEY, decodeState, encodeState, loadHabits, saveHabits } from "../src/storage.js";
import { sampleHabits } from "./fixtures/sample.js";

const state = (habits) => JSON.stringify({ version: 1, habits });
const habit = (name, done = []) => ({ name, done });
const named = (count) => Array.from({ length: count }, (_, index) => habit(`H${index + 1}`));

test("@R16 the storage key is streaks.state", () => {
  assert.equal(STORAGE_KEY, "streaks.state");
});

test("@R17 nothing saved is absent, not unreadable", () => {
  assert.deepEqual(decodeState(null), { status: "absent" });
});

// raw text, why it is unreadable. Every row must come back as exactly { status: "unreadable" }.
const UNREADABLE = [
  ["the empty string", ""],
  ["not JSON", "{"],
  ["JSON null", "null"],
  ["an array", "[]"],
  ["a number", "1"],
  ["wrong version", '{"version":2,"habits":[]}'],
  ["version as text", '{"version":"1","habits":[]}'],
  ["no version", '{"habits":[]}'],
  ["habits is not an array", '{"version":1,"habits":{}}'],
  ["13 habits", state(named(13))],
  ["a habit that is null", state([null])],
  ["a habit that is an array", state([[]])],
  ["an empty name", state([habit("")])],
  ["an untrimmed name", state([habit(" Read")])],
  ["41 characters", state([habit("Read twenty pages before bed every night.")])],
  ["a name that is not text", state([{ name: 5, done: [] }])],
  ["no done list", state([{ name: "Read" }])],
  ["done is not a list", state([{ name: "Read", done: "2026-10-08" }])],
  ["an impossible date", state([habit("Read", ["2026-02-30"])])],
  ["a date with a time", state([habit("Read", ["2026-10-08T00:00"])])],
  ["a number among the dates", state([habit("Read", ["2026-10-08", 20261008])])],
  // The three rows below are the holes a survivor of "only done[0]" and "only the previous name" would leave.
  ["a good date, then another good one, then an impossible one", state([habit("Read", ["2026-10-08", "2026-10-07", "2026-02-30"])])],
  ["an impossible date in the second habit", state([habit("A", ["2026-10-08"]), habit("B", ["2026-10-08", "2026-02-30"])])],
  ["a duplicate name that is not next to its twin", state([habit("A"), habit("B"), habit("a")])],
];

for (const [why, raw] of UNREADABLE) {
  test(`@R17 unreadable: ${why}`, () => {
    assert.deepEqual(decodeState(raw), { status: "unreadable" });
  });
}

test("@R17 an empty list and exactly 12 habits are readable", () => {
  assert.deepEqual(decodeState(state([])), { status: "ok", habits: [] });
  const twelve = decodeState(state(named(12)));
  assert.equal(twelve.status, "ok");
  assert.equal(twelve.habits.length, 12);
});

test("@R17 days come back sorted ascending and without duplicates, whatever order they were saved in", () => {
  const messy = ["2026-10-08", "2026-10-05", "2026-10-08", "2026-10-07", "2026-10-05"];
  const result = decodeState(state([habit("Read", messy), habit("Stretch", ["2026-10-02"])]));
  assert.deepEqual(result, {
    status: "ok",
    habits: [habit("Read", ["2026-10-05", "2026-10-07", "2026-10-08"]), habit("Stretch", ["2026-10-02"])],
  });
});

test("@R17 a day far after today is kept (a clock or time zone change can create one)", () => {
  const result = decodeState(state([habit("Read", ["2999-01-01", "2026-10-08"])]));
  assert.deepEqual(result.habits[0].done, ["2026-10-08", "2999-01-01"]);
});

test("@R17 @T2 habits are rebuilt as { name, done }: extra properties and a __proto__ key go nowhere", () => {
  const raw = '{"version":1,"theme":"dark","habits":[{"name":"Read","done":[],"color":"red","__proto__":{"polluted":true}}]}';
  const result = decodeState(raw);
  assert.equal(result.status, "ok");
  const [first] = result.habits;
  assert.deepEqual(Object.getOwnPropertyNames(first), ["name", "done"]);
  assert.equal(Object.getPrototypeOf(first), Object.prototype);
  assert.equal(({}).polluted, undefined);
  assert.equal(first.polluted, undefined);
});

test("@R17 @T2 the result is made of new objects, never the parsed ones", () => {
  const realParse = JSON.parse;
  let parsed;
  JSON.parse = (text) => (parsed = realParse(text));
  let result;
  try {
    result = decodeState(state([habit("Read", ["2026-10-08"]), habit("Stretch")]));
  } finally {
    JSON.parse = realParse;
  }
  assert.equal(result.status, "ok");
  result.habits.forEach((made, index) => {
    assert.notEqual(made, parsed.habits[index]);
    assert.notEqual(made.done, parsed.habits[index].done);
  });
});

test("@R16 encodeState writes compact JSON with version 1 and only name and done", () => {
  const text = encodeState([{ name: "Read 20 pages", done: ["2026-10-03", "2026-10-04"], color: "red" }]);
  assert.equal(text, '{"version":1,"habits":[{"name":"Read 20 pages","done":["2026-10-03","2026-10-04"]}]}');
});

test("@R16 @R17 what encodeState writes decodeState reads back unchanged", () => {
  const habits = [habit("Read 20 pages", ["2026-10-03", "2026-10-04"]), habit("Stretch 10 minutes")];
  assert.deepEqual(decodeState(encodeState(habits)), { status: "ok", habits });
  assert.deepEqual(decodeState(encodeState([])), { status: "ok", habits: [] });
});

// qa.md, "saveHabits reports whether the write worked, and loadHabits whether the read did" (R16, R41, SW1 to SW4).
// Node has no localStorage, so each case puts a stand-in on globalThis and removes it afterwards, whatever happens.

const SAMPLE_HABITS = sampleHabits(new URL("../docs/design/sample-history.json", import.meta.url)).slice(0, 3);

/**
 * A stand-in store. `saved` is what getItem returns for the key. `failWith`, when given, is thrown by setItem
 * instead of storing. `writes` records every setItem call, `held` what was stored.
 */
function standIn({ saved = null, failWith } = {}) {
  const writes = [];
  const held = new Map();
  const storage = {
    getItem: (key) => (key === STORAGE_KEY ? saved : null),
    setItem: (key, value) => {
      writes.push([key, value]);
      if (failWith !== undefined) throw failWith;
      held.set(key, value);
    },
  };
  return { storage, writes, held };
}

/** Runs `body` with globalThis.localStorage defined by `descriptor`, then takes it away again. */
function withLocalStorage(descriptor, body) {
  const before = Object.getOwnPropertyDescriptor(globalThis, "localStorage");
  Object.defineProperty(globalThis, "localStorage", { configurable: true, ...descriptor });
  try {
    return body();
  } finally {
    if (before) Object.defineProperty(globalThis, "localStorage", before);
    else delete globalThis.localStorage;
  }
}

test("@R16 @R41 saveHabits returns true when setItem returns, and the store holds encodeState(habits)", () => {
  const { storage, held } = standIn();
  const result = withLocalStorage({ value: storage }, () => saveHabits(SAMPLE_HABITS));
  assert.equal(result, true);
  assert.equal(held.get(STORAGE_KEY), encodeState(SAMPLE_HABITS));
});

test("@R16 @R41 saveHabits returns false when setItem throws something that is not an Error, and never reads it", () => {
  const read = [];
  const thrown = {};
  for (const property of ["name", "code", "message"]) {
    Object.defineProperty(thrown, property, { get: () => read.push(property) });
  }
  const { storage } = standIn({ failWith: thrown });
  let result;
  assert.doesNotThrow(() => {
    result = withLocalStorage({ value: storage }, () => saveHabits(SAMPLE_HABITS));
  });
  assert.equal(result, false);
  assert.deepEqual(read, [], "the app read the error it caught");
});

test("@R16 @R41 with a localStorage getter that throws, saveHabits returns false and loadHabits reports the failed read", () => {
  const denied = {
    get: () => {
      throw new Error("test denied");
    },
  };
  assert.equal(withLocalStorage(denied, () => saveHabits(SAMPLE_HABITS)), false);
  assert.deepEqual(withLocalStorage(denied, () => loadHabits()), { habits: [], reset: false, saveFailed: true });
});

test("@R16 @R41 nothing saved loads empty with no failure and writes nothing", () => {
  const { storage, writes } = standIn({ saved: null });
  assert.deepEqual(withLocalStorage({ value: storage }, () => loadHabits()), { habits: [], reset: false, saveFailed: false });
  assert.deepEqual(writes, []);
});

test("@R16 @R41 unreadable saved text whose reset save fails gives reset and saveFailed", () => {
  const { storage } = standIn({ saved: "{", failWith: new Error("test quota") });
  assert.deepEqual(withLocalStorage({ value: storage }, () => loadHabits()), { habits: [], reset: true, saveFailed: true });
});

test("@R16 @R41 unreadable saved text is reset to the empty state, and the reset save works", () => {
  const { storage, held } = standIn({ saved: "{" });
  assert.deepEqual(withLocalStorage({ value: storage }, () => loadHabits()), { habits: [], reset: true, saveFailed: false });
  assert.equal(held.get(STORAGE_KEY), '{"version":1,"habits":[]}');
});

test("@R16 @R41 readable saved text loads the habits with no reset and no failure, and writes nothing", () => {
  const { storage, writes } = standIn({ saved: encodeState(SAMPLE_HABITS) });
  assert.deepEqual(withLocalStorage({ value: storage }, () => loadHabits()), {
    habits: SAMPLE_HABITS,
    reset: false,
    saveFailed: false,
  });
  assert.deepEqual(writes, []);
});
