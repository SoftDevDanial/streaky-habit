import { readFileSync } from "node:fs";
import { addDays } from "../../src/dates.js";

// Converts the v1.1.0 design sample (docs/design/sample-history.json, read-only) into habits of
// the Habit shape. `file` is a path or URL. In each `done` string, character i is "1" when the
// habit was done on addDays(from, i). The 1.0 fixture needs no conversion, it already holds arrays.
export function sampleHabits(file) {
  const { from, habits } = JSON.parse(readFileSync(file, "utf8"));
  return habits.map(({ name, done }) => ({
    name,
    done: [...done].flatMap((flag, i) => (flag === "1" ? [addDays(from, i)] : [])),
  }));
}
