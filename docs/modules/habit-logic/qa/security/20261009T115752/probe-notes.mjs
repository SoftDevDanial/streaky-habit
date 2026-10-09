// Security probe: edges recorded as observations (not findings). Name characters the rule admits, the
// key format localDateKey can produce that isDateKey rejects, and non-string input to validateName.
import { writeFileSync } from "node:fs";
import { localDateKey, isDateKey } from "../../../../../../src/dates.js";
import { validateName, addHabit } from "../../../../../../src/habits.js";

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
const show = (value) => JSON.stringify(value).replace(/[\u0080-￿]/g, (c) => `\\u${c.charCodeAt(0).toString(16).padStart(4, "0")}`);

log("## Names the rule accepts (trim, 1 to 40 code points, unique by toLowerCase)");
const existing = ["Read 20 pages", "Étude"];
const rows = [
  ["zero-width space only", "​"],
  ["word joiner and ZWNJ only", "⁠‌"],
  ["existing name plus a zero-width space", "Read 20 pages​"],
  ["existing name with Cyrillic e (homoglyph)", "Rеad 20 pages"],
  ["NFD form of an existing NFC name", "Étude"],
  ["right-to-left override", "‮egap 02 daeR"],
  ["C0 control characters", "a\u0000b\u0007c"],
  ["line break inside", "Read\n20 pages"],
  ["lone surrogate", "\uD800"],
];
for (const [label, name] of rows) log(`${label}: validateName(${show(name)}) = ${show(validateName(name, existing))}`);

log("\n## Key format: localDateKey can produce a key isDateKey rejects (device clock at year 10000 or later)");
const late = localDateKey(new Date(10000, 0, 1));
log(`localDateKey(new Date(10000, 0, 1)) = "${late}", isDateKey = ${isDateKey(late)}`);
const nine = localDateKey(new Date(9999, 11, 31));
log(`localDateKey(new Date(9999, 11, 31)) = "${nine}", isDateKey = ${isDateKey(nine)}`);

log("\n## Non-string input (the decoder type-checks first, the add form passes input.value)");
for (const raw of [null, undefined, 42, { trim: () => "x" }]) {
  try {
    log(`validateName(${show(raw)}) = ${show(validateName(raw, []))}`);
  } catch (error) {
    log(`validateName(${raw === undefined ? "undefined" : show(raw)}) throws ${error.constructor.name}`);
  }
}
try {
  log(`addHabit([{ name: 7, done: [] }], "x") = ${show(addHabit([{ name: 7, done: [] }], "x"))}`);
} catch (error) {
  log(`addHabit with a non-string stored name throws ${error.constructor.name}`);
}

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-notes.txt", import.meta.url), text);
process.stdout.write(text);
