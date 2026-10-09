// Observation (c): the WHITE_SPACE constant in tests/habits.test.js holds raw invisible characters.
// 1. Lists every invisible or look-alike space character (Zs, Zl, Zp and Cf categories, except U+0020)
//    in src/ and tests/, by file and line, so the scope of the pattern is known.
// 2. Evaluates WHITE_SPACE from the file text and shows each entry as code points, whether Number() treats
//    it as white space (the property the test relies on), and how it looks once every non-ASCII
//    character is shown as a plain space, which is what a reader without a hex view sees.
import fs from "node:fs";
import vm from "node:vm";

const root = new URL("../../../../../../", import.meta.url);
const files = ["src/dates.js", "src/habits.js", "tests/dates.test.js", "tests/habits.test.js", "tests/purity.test.js", "tests/sample-history.test.js"];
const invisible = /[\p{Zs}\p{Zl}\p{Zp}\p{Cf}]/gu;
const code = (char) => `U+${char.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`;

console.log("INVISIBLE OR LOOK-ALIKE SPACE CHARACTERS (everything but U+0020), by file and line");
for (const file of files) {
  const lines = fs.readFileSync(new URL(file, root), "utf8").split(/\r?\n/);
  lines.forEach((line, index) => {
    const found = [...line.matchAll(invisible)].map((match) => match[0]).filter((char) => char !== " ");
    if (found.length > 0) console.log(`${file}:${index + 1}: ${found.map(code).join(" ")}`);
  });
}

console.log("");
const text = fs.readFileSync(new URL("tests/habits.test.js", root), "utf8");
const line = text.match(/^const WHITE_SPACE = .*;$/m)[0];
const entries = vm.runInNewContext(line.replace(/^const WHITE_SPACE = /, "").replace(/;$/, ""));
console.log(`WHITE_SPACE has ${entries.length} entries, ${new Set(entries).size} distinct`);
for (const entry of entries) {
  const points = [...entry].map(code).join(" ") || "(empty)";
  const asSeen = entry.replace(/[^\x00-\x7f]/g, " ");
  console.log(`  ${points.padEnd(8)} Number(entry + "12") === 12: ${Number(`${entry}12`) === 12}   Number(entry + "") is 0 for empty: ${entry === "" ? Number(entry) === 0 : "n/a"}   seen without a hex view: ${JSON.stringify(asSeen)}`);
}
console.log(`entries that look like a plain space or are empty without a hex view: ${entries.filter((entry) => /^[ ]*$/.test(entry.replace(/[^\x00-\x7f]/g, " "))).length} of ${entries.length}`);
