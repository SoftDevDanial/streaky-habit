// WR-11. Nothing is written. Takes the OLD stripper from `git show <rev>:tests/purity.test.js` and the NEW one
// from the working tree's tests/purity.test.js (both evaluated from the file text, nothing imported from a
// test), then reports:
//   1. byte equality of old and new output on the two real sources (the ruling asks for the same output)
//   2. the reviewer's eight small checks of a string-aware stripper, run against the NEW stripper
//   3. BANNED_IN_CODE and the import-word count on the real sources and on the reviewer's scan mutants,
//      old stripper against new, so the rows show where the hole was and that it is closed
//   4. the reviewer's guard regex against the two comment-shaped mutants, for the record
// Usage, from the project root: node docs/modules/habit-logic/qa/solver/<ts>/stripper-equality.mjs <old rev>
import fs from "node:fs";
import vm from "node:vm";
import { execFileSync } from "node:child_process";
import { MUTANTS } from "../../code-review/20261009-131935/mutants.mjs";
import { EXTRA_MUTANTS } from "../../code-review/20261009-131935/mutants-extra.mjs";
import { EXTRA_MUTANTS_2 } from "../../code-review/20261009-131935/mutants-extra2.mjs";
import { applyEdits } from "../../code-review/20261009-131935/edits.mjs";

const root = new URL("../../../../../../", import.meta.url);
const oldRev = process.argv[2] ?? "fa7838d";
const read = (path) => fs.readFileSync(new URL(path, root), "utf8");
const git = (...args) => execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });

const oldTest = git("show", `${oldRev}:tests/purity.test.js`);
const newTest = read("tests/purity.test.js");
const pick = (text, pattern) => text.match(pattern)?.[0];

function strippers(testText) {
  const parts = [
    pick(testText, /^const STRING_OR_COMMENT = .*;$/m),
    pick(testText, /^const withoutComments = .*;$/m),
    pick(testText, /^const BANNED_IN_CODE = \{[\s\S]*?^\};$/m),
    "({ withoutComments, BANNED_IN_CODE })",
  ].filter(Boolean);
  return vm.runInNewContext(parts.join("\n"));
}
const oldSide = strippers(oldTest);
const newSide = strippers(newTest);

console.log(`pid ${process.pid}, old stripper from ${oldRev}, new stripper from the working tree`);
console.log("old line:", pick(oldTest, /^const withoutComments = .*;$/m));
console.log("new line:", pick(newTest, /^const withoutComments = .*;$/m));
console.log("new regex:", pick(newTest, /^const STRING_OR_COMMENT = .*;$/m));

console.log("\n1. REAL SOURCES, old output against new output");
const real = { "dates.js": read("src/dates.js"), "habits.js": read("src/habits.js") };
for (const [name, text] of Object.entries(real)) {
  const before = oldSide.withoutComments(text);
  const after = newSide.withoutComments(text);
  console.log(`${name}: ${text.length} chars in, ${before.length} out (old), ${after.length} out (new), identical ${before === after}`);
}

console.log("\n2. SMALL CHECKS of the new stripper");
const checks = [
  ["line comment removed", "a(); // b()\nc();", "a(); \nc();"],
  ["block comment removed", "a(); /* b() */ c();", "a();  c();"],
  ["url in a string kept", 'x("https://h/p"); fetch(y);', 'x("https://h/p"); fetch(y);'],
  ["slash-star in a string kept", 'x("*/*"); z();', 'x("*/*"); z();'],
  ["slash-star in a line comment removed with the comment", "// src/*\nfetch(y);", "\nfetch(y);"],
  ["escaped quote", 'x("a\\"//b"); q();', 'x("a\\"//b"); q();'],
  ["regex literal of the module untouched", "const K = /^\\d{4}-\\d{2}-\\d{2}$/;", "const K = /^\\d{4}-\\d{2}-\\d{2}$/;"],
  ["template literal kept", "const t = `a//b ${c}`;", "const t = `a//b ${c}`;"],
  ["apostrophe inside a line comment does not open a string", "// the strip's width\nfetch(y);", "\nfetch(y);"],
  ["apostrophe inside a block comment does not open a string", "/* the strip's width */ fetch(y);", " fetch(y);"],
  ["CRLF line ending kept", "a(); // b\r\nc();", "a(); \r\nc();"],
];
let failed = 0;
for (const [label, input, expected] of checks) {
  const got = newSide.withoutComments(input);
  const ok = got === expected;
  if (!ok) failed++;
  console.log(`${ok ? "ok  " : "FAIL"} ${label}${ok ? "" : ` got ${JSON.stringify(got)}`}`);
}
console.log(`${checks.length - failed} of ${checks.length} ok`);

console.log("\n3. SCAN TABLE AND IMPORT WORDS, old stripper against new stripper");
const hits = (side, code) => Object.entries(side.BANNED_IN_CODE).filter(([, pattern]) => pattern.test(code)).map(([rule]) => rule);
const importWords = (code) => (code.match(/\bimport\b/g) ?? []).length;
const GUARD = /(["'`])[^"'`\n]*?(?:\/\/|\/\*)[^"'`\n]*?\1/;
const all = { ...MUTANTS, ...EXTRA_MUTANTS, ...EXTRA_MUTANTS_2 };
const rows = [["real habits.js", real["habits.js"]], ["real dates.js", real["dates.js"]]];
for (const name of Object.keys(all).filter((key) => all[key].kind === "scan")) {
  rows.push([name, applyEdits(real[all[name].file], all[name].edits, name)]);
}
for (const [label, text] of rows) {
  const before = oldSide.withoutComments(text);
  const after = newSide.withoutComments(text);
  console.log(
    `${label.padEnd(46)} banned hits old [${hits(oldSide, before)}] new [${hits(newSide, after)}] | import words old ${importWords(before)} new ${importWords(after)} | guard regex matches ${GUARD.test(text)}`,
  );
}
