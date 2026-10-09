// Two follow-up checks for WR-11 and Observation 1. Nothing is imported from the test and nothing is written.
// 1. The import rule counts `import` words in withoutComments(habits.js). With a second import hidden under a
//    "/*" inside a line comment (mutants-extra2.mjs), the current stripper still counts 1 and the one-pass
//    stripper counts 2. The visible second import counts 2 under both.
// 2. The widened Date.now pattern suggested in Observation 1 against its spellings and near misses. The
//    current pattern, /Date\s*\.\s*now\b/, has no boundary before "Date" either, so an identifier that ends in
//    Date followed by .now matches under both. That is an existing harmless false positive, not a change.
import fs from "node:fs";
import vm from "node:vm";
import { EXTRA_MUTANTS_2 } from "./mutants-extra2.mjs";
import { applyEdits } from "./edits.mjs";

const root = new URL("../../../../../../", import.meta.url);
const read = (path) => fs.readFileSync(new URL(path, root), "utf8");
const testText = read("tests/purity.test.js");
const { withoutComments } = vm.runInNewContext(`${testText.match(/^const withoutComments = .*;$/m)[0]}\n({ withoutComments })`);

const STRING_OR_COMMENT =
  /("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`)|\/\*[\s\S]*?\*\/|\/\/.*$/gm;
const single = (text) => text.replace(STRING_OR_COMMENT, (match, quoted) => quoted ?? "");
const importWords = (code) => (code.match(/\bimport\b/g) ?? []).length;

const habits = read("src/habits.js");
console.log(`real habits.js: import words current ${importWords(withoutComments(habits))}, one-pass ${importWords(single(habits))}`);
for (const [name, mutant] of Object.entries(EXTRA_MUTANTS_2)) {
  const text = applyEdits(habits, mutant.edits, name);
  console.log(`${name}: import words current ${importWords(withoutComments(text))}, one-pass ${importWords(single(text))}`);
}

console.log("");
const current = /Date\s*\.\s*now\b/;
const widened = /Date\s*(?:\?\.|\.|\[\s*["'`])\s*now\b/;
const rows = [
  ["Date.now()", true],
  ["Date . now()", true],
  ["Date?.now()", true],
  ['Date["now"]()', true],
  ["Date['now']()", true],
  ["Date[`now`]()", true],
  ["Date.nowhere", false],
  ["Date.UTC(2026, 0, 1)", false],
  ["new Date(key)", false],
];
for (const [text, expected] of rows) {
  const got = widened.test(text);
  console.log(`${got === expected ? "ok  " : "FAIL"} ${text.padEnd(24)} widened ${got}, current ${current.test(text)}`);
}
