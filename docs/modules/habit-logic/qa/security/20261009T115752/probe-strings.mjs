// Security probe: hostile and oversized strings through the two functions the storage decoder runs on
// stored text (isDateKey, validateName). Measures time scaling and the memory the length count allocates.
// Run with: node --expose-gc probe-strings.mjs
import { writeFileSync } from "node:fs";
import { isDateKey } from "../../../../../../src/dates.js";
import { validateName, MAX_NAME_LENGTH } from "../../../../../../src/habits.js";

const lines = [];
const log = (...parts) => lines.push(parts.join(" "));
const gc = globalThis.gc ?? (() => {});
log(`node ${process.version} ${process.platform}, gc exposed: ${typeof globalThis.gc === "function"}`);

function timed(run, repeats = 3) {
  const samples = [];
  let result;
  for (let i = 0; i < repeats; i++) {
    const started = performance.now();
    result = run();
    samples.push(performance.now() - started);
  }
  samples.sort((a, b) => a - b);
  return { ms: samples[Math.floor(repeats / 2)], result };
}

// ---- isDateKey: anchored fixed-width pattern, so time should not grow with length.
log("\n## isDateKey on hostile strings (median of 3, ms)");
const datePatterns = {
  "valid prefix then 8s": (n) => "2026-10-0" + "8".repeat(n),
  "digits only": (n) => "1".repeat(n),
  "valid key then newlines": (n) => "2026-10-08" + "\n".repeat(n),
  "valid key repeated": (n) => "2026-10-08".repeat(Math.ceil(n / 10)),
  "hyphens only": (n) => "-".repeat(n),
  "digits then hyphen at the end": (n) => "9".repeat(n) + "-",
  "fullwidth digits": (n) => "２".repeat(n),
};
for (const [label, make] of Object.entries(datePatterns)) {
  const row = [];
  for (const n of [1e4, 1e6, 1e7, 5e7]) {
    const text = make(n);
    const { ms, result } = timed(() => isDateKey(text));
    row.push(`n=${n.toExponential(0)} ${ms.toFixed(3)}ms ${result}`);
  }
  log(`${label}: ${row.join(" | ")}`);
}

// ---- RegExp legacy statics: does a hostile string stay referenced after isDateKey?
isDateKey("2026-10-08");
const afterValid = RegExp.input;
const big = "2026-10-08" + "x".repeat(5e6);
isDateKey(big);
log(`\nRegExp.input after isDateKey("2026-10-08") = ${JSON.stringify(afterValid)}`);
log(`RegExp.input length after isDateKey(5,000,010 char failing string) = ${RegExp.input.length} (the failing string is ${RegExp.input === big ? "" : "not "}retained)`);

// ---- validateName: time, and the memory of the code-point count it uses (Array.from(name)).
log("\n## validateName on oversized names (median of 3, ms). Storage quota is about 5 million UTF-16 code units.");
const namePatterns = {
  "ASCII x": (units) => "x".repeat(units),
  "CJK (BMP, two-byte)": (units) => "一".repeat(units),
  "astral emoji (surrogate pairs)": (units) => "\u{1F4DA}".repeat(units / 2),
  "only white space": (units) => " ".repeat(units),
  "white space around 41 letters": (units) => " ".repeat(units / 2) + "y".repeat(41) + " ".repeat(units / 2),
};
for (const [label, make] of Object.entries(namePatterns)) {
  const row = [];
  for (const units of [1e5, 1e6, 2.5e6, 5e6]) {
    const name = make(units);
    const { ms, result } = timed(() => validateName(name, ["Read 20 pages"]));
    row.push(`units=${units.toExponential(1)} ${ms.toFixed(1)}ms ${result.ok ? "ok" : result.error}`);
  }
  log(`${label}: ${row.join(" | ")}`);
}

// Memory held by the exact expression validateName uses to count code points, for a 5M unit name.
log("\n## Heap allocated by Array.from(name), the length count in validateName, for 5,000,000 UTF-16 units");
for (const [label, make] of Object.entries(namePatterns).slice(0, 3)) {
  const name = make(5e6);
  gc();
  gc();
  const before = process.memoryUsage().heapUsed;
  const held = Array.from(name);
  const after = process.memoryUsage().heapUsed;
  log(`${label}: ${held.length} code points, heap +${((after - before) / 1048576).toFixed(1)} MiB (string itself is ${((name.length * (/[^\x00-\xff]/.test(name.slice(0, 2)) ? 2 : 1)) / 1048576).toFixed(1)} MiB)`);
  held.length = 0;
}

// A bounded count, for comparison: stop at MAX_NAME_LENGTH + 1 code points.
function tooLongBounded(name) {
  let count = 0;
  for (const _ of name) if (++count > MAX_NAME_LENGTH) return true;
  return false;
}
log("\n## Comparison: a bounded code-point count that stops at 41 (median of 3, ms)");
for (const [label, make] of Object.entries(namePatterns).slice(0, 3)) {
  const name = make(5e6);
  const { ms, result } = timed(() => tooLongBounded(name));
  gc();
  const before = process.memoryUsage().heapUsed;
  tooLongBounded(name);
  const after = process.memoryUsage().heapUsed;
  log(`${label}: ${ms.toFixed(4)}ms too-long=${result}, heap +${((after - before) / 1048576).toFixed(2)} MiB`);
}

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-strings.txt", import.meta.url), text);
process.stdout.write(text);
