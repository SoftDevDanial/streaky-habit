// WR-13. Nothing is written. Evaluates the WHITE_SPACE line of `git show <rev>:tests/habits.test.js` (raw
// characters) and of the working tree's tests/habits.test.js (escapes), and compares the two arrays entry by
// entry as code points. Also checks that the new line is ASCII only, and that every entry is still treated
// as white space by Number(), the property the test relies on.
// Usage, from the project root: node docs/modules/habit-logic/qa/solver/<ts>/whitespace-equality.mjs <old rev>
import fs from "node:fs";
import vm from "node:vm";
import { execFileSync } from "node:child_process";

const root = new URL("../../../../../../", import.meta.url);
const oldRev = process.argv[2] ?? "fa7838d";
const oldText = execFileSync("git", ["show", `${oldRev}:tests/habits.test.js`], { cwd: root, encoding: "utf8" });
const newText = fs.readFileSync(new URL("tests/habits.test.js", root), "utf8");

const lineOf = (text) => text.match(/^const WHITE_SPACE = .*;$/m)[0];
const evaluate = (line) => vm.runInNewContext(line.replace(/^const WHITE_SPACE = /, "").replace(/;$/, ""));
const points = (entry) => [...entry].map((char) => "U+" + char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")).join(" ") || "(empty)";

const oldLine = lineOf(oldText);
const newLine = lineOf(newText);
const before = evaluate(oldLine);
const after = evaluate(newLine);

console.log(`pid ${process.pid}, old line from ${oldRev}, new line from the working tree`);
console.log(`old line has ${[...oldLine].filter((char) => char.codePointAt(0) > 127).length} non-ASCII characters`);
console.log(`new line has ${[...newLine].filter((char) => char.codePointAt(0) > 127).length} non-ASCII characters: ${newLine}`);
console.log(`entries old ${before.length}, new ${after.length}, identical array ${JSON.stringify(before) === JSON.stringify(after)}`);
for (let i = 0; i < after.length; i++) {
  console.log(`  [${i}] old ${points(before[i]).padEnd(8)} new ${points(after[i]).padEnd(8)} same ${before[i] === after[i]}  Number(entry + "12") === 12: ${Number(`${after[i]}12`) === 12}`);
}
console.log(`new array has ${new Set(after).size} distinct entries`);
const naive = [...newText.matchAll(/^.*[^\x00-\x7f].*$/gm)].length;
console.log(`lines of tests/habits.test.js with any non-ASCII character: ${naive}`);
