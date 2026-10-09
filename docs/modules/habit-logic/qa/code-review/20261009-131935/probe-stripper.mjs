// Observation (a): tests/purity.test.js `withoutComments` strips `//` and `/*` inside string literals.
// Takes withoutComments and the scan table straight from the test file text (nothing is imported from the
// test, nothing is written), runs them over the real sources and over the scan mutants of mutants.mjs and
// mutants-extra.mjs, and compares three things:
//   current    the stripper as it is in the test
//   guard      the auditor's proposed guard regex, asserted on the text
//   single     a one-pass stripper that consumes string literals and comments in source order
import fs from "node:fs";
import vm from "node:vm";
import { MUTANTS } from "./mutants.mjs";
import { EXTRA_MUTANTS } from "./mutants-extra.mjs";
import { applyEdits } from "./edits.mjs";

const root = new URL("../../../../../../", import.meta.url);
const read = (path) => fs.readFileSync(new URL(path, root), "utf8");

const testText = read("tests/purity.test.js");
const pick = (pattern) => testText.match(pattern)[0];
const { withoutComments, BANNED_IN_CODE } = vm.runInNewContext(
  [
    pick(/^const withoutComments = .*;$/m),
    pick(/^const BANNED_IN_CODE = \{[\s\S]*?^\};$/m),
    "({ withoutComments, BANNED_IN_CODE })",
  ].join("\n"),
);

const GUARD = /(["'`])[^"'`\n]*?(?:\/\/|\/\*)[^"'`\n]*?\1/;
const STRING_OR_COMMENT =
  /("(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`)|\/\*[\s\S]*?\*\/|\/\/.*$/gm;
const single = (text) => text.replace(STRING_OR_COMMENT, (match, quoted) => quoted ?? "");

const hits = (code) =>
  Object.entries(BANNED_IN_CODE)
    .filter(([, pattern]) => pattern.test(code))
    .map(([rule]) => rule);

const real = { "dates.js": read("src/dates.js"), "habits.js": read("src/habits.js") };

console.log("withoutComments source line:", pick(/^const withoutComments = .*;$/m));
console.log("");
console.log("REAL SOURCES");
for (const [name, text] of Object.entries(real)) {
  console.log(
    `${name}: current hits [${hits(withoutComments(text))}] | single hits [${hits(single(text))}] | ` +
      `guard matches ${GUARD.test(text)} | single output equals current output ${single(text) === withoutComments(text)}`,
  );
}

console.log("");
console.log("SCAN MUTANTS (src/habits.js text with planted lines, never executed)");
const all = { ...MUTANTS, ...EXTRA_MUTANTS };
for (const name of Object.keys(all).filter((key) => all[key].kind === "scan")) {
  const mutant = all[name];
  const text = applyEdits(real[mutant.file], mutant.edits, name);
  console.log(
    `${name}: current hits [${hits(withoutComments(text))}] | single hits [${hits(single(text))}] | guard matches ${GUARD.test(text)}`,
  );
}

console.log("");
console.log("SINGLE-PASS STRIPPER, small checks");
const checks = [
  ["line comment removed", "a(); // b()\nc();", "a(); \nc();"],
  ["block comment removed", "a(); /* b() */ c();", "a();  c();"],
  ["url in a string kept", 'x("https://h/p"); fetch(y);', 'x("https://h/p"); fetch(y);'],
  ["slash-star in a string kept", 'x("*/*"); z();', 'x("*/*"); z();'],
  ["slash-star in a line comment removed with the comment", "// src/*\nfetch(y);", "\nfetch(y);"],
  ["escaped quote", 'x("a\\"//b"); q();', 'x("a\\"//b"); q();'],
  ["regex literal of the module untouched", "const K = /^\\d{4}-\\d{2}-\\d{2}$/;", "const K = /^\\d{4}-\\d{2}-\\d{2}$/;"],
  ["template literal kept", "const t = `a//b ${c}`;", "const t = `a//b ${c}`;"],
];
for (const [label, input, expected] of checks) {
  const got = single(input);
  console.log(`${got === expected ? "ok  " : "FAIL"} ${label}${got === expected ? "" : ` got ${JSON.stringify(got)}`}`);
}
