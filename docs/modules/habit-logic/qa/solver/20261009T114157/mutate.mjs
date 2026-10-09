// Solver verification for the habit-logic code-review findings (2026-10-09). Not shipped, not a test.
// Builds one mirror per mutant under ./mirrors/<name>/ (src and tests copied from the working tree or
// from a commit, the sample copied read-only from docs/design), applies one text mutation to a source
// file, runs one test file of the mirror with node --test and prints the verdict of every test.
// Usage, from the project root: node docs/modules/habit-logic/qa/solver/20261009T114157/mutate.mjs <mutant>...
import { execFileSync, spawnSync } from "node:child_process";
import { cpSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { MUTANTS } from "./mutants.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const root = process.cwd();

function gitShow(commit, path) {
  return execFileSync("git", ["show", `${commit}:${path}`], { cwd: root, encoding: "utf8" });
}

for (const name of process.argv.slice(2)) {
  const mutant = MUTANTS[name];
  if (!mutant) throw new Error(`unknown mutant ${name}`);
  const mirror = join(here, "mirrors", name);
  mkdirSync(join(mirror, "src"), { recursive: true });
  mkdirSync(join(mirror, "tests"), { recursive: true });
  mkdirSync(join(mirror, "docs", "design"), { recursive: true });
  for (const file of ["dates.js", "habits.js"]) {
    const text = mutant.srcFrom ? gitShow(mutant.srcFrom, `src/${file}`) : readFileSync(join(root, "src", file), "utf8");
    writeFileSync(join(mirror, "src", file), text);
  }
  for (const file of ["dates.test.js", "habits.test.js", "purity.test.js", "sample-history.test.js"]) {
    const text = mutant.testsFrom
      ? gitShow(mutant.testsFrom, `tests/${file}`)
      : readFileSync(join(root, "tests", file), "utf8");
    writeFileSync(join(mirror, "tests", file), text);
  }
  cpSync(join(root, "docs", "design", "sample-history.json"), join(mirror, "docs", "design", "sample-history.json"));

  for (const [file, find, replace] of mutant.edits) {
    const path = join(mirror, "src", file);
    const text = readFileSync(path, "utf8");
    if (!text.includes(find)) throw new Error(`${name}: mutation target not found in ${file}`);
    writeFileSync(path, text.replace(find, replace));
  }

  const run = spawnSync(process.execPath, ["--test", join(mirror, "tests", mutant.testFile)], {
    encoding: "utf8",
    timeout: 120_000,
  });
  const verdicts = run.stdout.split("\n").filter((line) => /^(✔|✖) /.test(line)).map((line) => line.replace(/ \([\d.]+ms\)$/, ""));
  const summary = run.stdout.split("\n").filter((line) => /^ℹ (tests|pass|fail) /.test(line));
  console.log(`== ${name}: ${mutant.about}`);
  console.log(`   tests from ${mutant.testsFrom ?? "the working tree"}, file ${mutant.testFile}, exit ${run.status}`);
  for (const line of [...verdicts, ...summary]) console.log(`   ${line}`);
}
