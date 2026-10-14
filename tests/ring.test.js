// Unit tests of src/ring.js, the pure ring geometry of spec R42 (qa.md, Feature "Rings and the legend", the Node
// scenarios). The arcs must equal the goldens' own path data character for character, which only a direct call can
// compare, so these run in Node and the browser tests of task 15 check how the rings are put together.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as ring from "../src/ring.js";
import { arcPath, legendCounts } from "../src/ring.js";

const readGolden = (name) => readFileSync(new URL(`../docs/design/${name}`, import.meta.url), "utf8");

/** The d of the shared arcs "a<n>-0" to "a<n>-<n-1>" that a golden draws its rings from. */
function sharedArcs(golden, n) {
  return Array.from({ length: n }, (_, i) => {
    const found = golden.match(new RegExp(`<path id="a${n}-${i}" d="([^"]+)"/>`));
    assert.ok(found, `the golden holds a${n}-${i}`);
    return found[1];
  });
}

test("@R42 arcPath reproduces the goldens' shared arcs", () => {
  sharedArcs(readGolden("today.html"), 3).forEach((d, i) => assert.equal(arcPath(i, 3), d, `a3-${i}`));
  sharedArcs(readGolden("today-full.html"), 12).forEach((d, i) => assert.equal(arcPath(i, 12), d, `a12-${i}`));
});

// n, i, d. Computed with the arc rule of spec R42 while planning (qa.md).
const OTHER_COUNTS = [
  [2, 0, "M22.86 5.28A15 15 0 0 1 22.86 34.72"],
  [2, 1, "M17.14 34.72A15 15 0 0 1 17.14 5.28"],
  [5, 0, "M22.81 5.27A15 15 0 0 1 33.14 12.77"],
  [5, 1, "M34.88 18.12A15 15 0 0 1 30.93 30.27"],
  [5, 2, "M26.39 33.57A15 15 0 0 1 13.61 33.57"],
  [5, 3, "M9.07 30.27A15 15 0 0 1 5.12 18.12"],
  [5, 4, "M6.86 12.77A15 15 0 0 1 17.19 5.27"],
];

for (const [n, i, d] of OTHER_COUNTS) {
  test(`@R42 arcPath(${i}, ${n}) for other numbers of habits`, () => {
    assert.equal(arcPath(i, n), d);
  });
}

const LEGENDS = [
  [0, [0]],
  [1, [0, 1]],
  [2, [0, 1, 2]],
  [3, [0, 1, 2, 3]],
  [4, [0, 2, 3, 4]],
  [5, [0, 2, 4, 5]],
  [12, [0, 4, 8, 12]],
];

for (const [n, counts] of LEGENDS) {
  test(`@R42 legendCounts(${n})`, () => {
    assert.deepEqual(legendCounts(n), counts);
  });
}

test("@R42 ring.js is pure", () => {
  const text = readFileSync(new URL("../src/ring.js", import.meta.url), "utf8");
  assert.doesNotMatch(text, /^\s*import[\s{*"']/m, "an import statement");
  assert.doesNotMatch(text, /\bimport\s*\(/, "a dynamic import");
  for (const word of ["document", "window", "globalThis", "localStorage", "Date"]) {
    assert.ok(!text.includes(word), `ring.js contains "${word}"`);
  }
  assert.deepEqual(Object.keys(ring).sort(), ["arcPath", "legendCounts"]);
});
