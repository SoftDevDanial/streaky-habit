// The claim behind streakDays and runLength: inside the valid range addDays never repeats a key, and a
// walk leaves the range at the first step outside it (to a key that fails isDateKey), so no walk over
// valid keys can cycle. Checked for every day from 0001-01-01 to 9999-12-31, forward and back.
import { addDays, isDateKey } from "../../../../../../src/dates.js";

const MIN_DAY = -719162; // 0001-01-01
const MAX_DAY = 2932896; // 9999-12-31
const keyOfDay = (day) => new Date(day * 86400000).toISOString().slice(0, 10);

let forwardWrong = 0;
let backWrong = 0;
let invalidKeysInRange = 0;
for (let day = MIN_DAY; day < MAX_DAY; day++) {
  const key = keyOfDay(day);
  if (!isDateKey(key)) invalidKeysInRange++;
  if (addDays(key, 1) !== keyOfDay(day + 1)) forwardWrong++;
  if (addDays(keyOfDay(day + 1), -1) !== key) backWrong++;
}
console.log(`pid ${process.pid}: ${MAX_DAY - MIN_DAY} steps. keys in range failing isDateKey ${invalidKeysInRange}, wrong +1 ${forwardWrong}, wrong -1 ${backWrong}`);
console.log(`first step past the top:    addDays("9999-12-31", 1) = ${addDays("9999-12-31", 1)}, isDateKey ${isDateKey(addDays("9999-12-31", 1))}`);
console.log(`first step past the bottom: addDays("0001-01-01", -1) = ${addDays("0001-01-01", -1)}, isDateKey ${isDateKey(addDays("0001-01-01", -1))}`);
