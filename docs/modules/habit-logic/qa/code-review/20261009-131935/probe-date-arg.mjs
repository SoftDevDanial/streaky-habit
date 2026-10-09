// WR-02 check: which Date arguments let the purity test's before-and-after getTime() comparison see a write?
// The test uses new Date(2026, 9, 8, 12), which is exactly 12:00:00.000 local time.
// Run under MUTANT=date-arg-partial (setMilliseconds, setSeconds and setMinutes to 0) and
// MUTANT=date-arg-sethours (setHours(0, 0, 0, 0)), and with no mutant as the control.
import { localDateKey } from "../../../../../../src/dates.js";

const candidates = {
  "the test's Date, 12:00:00.000": () => new Date(2026, 9, 8, 12),
  "12:34:56.789": () => new Date(2026, 9, 8, 12, 34, 56, 789),
  "00:00:00.001": () => new Date(2026, 9, 8, 0, 0, 0, 1),
};

for (const [label, make] of Object.entries(candidates)) {
  const date = Object.freeze(make());
  const before = date.getTime();
  const key = localDateKey(date);
  console.log(`${label}: key ${key}, getTime changed ${date.getTime() !== before}`);
}
