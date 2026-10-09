// Security solver probe (SEC-04): the purity scan before and after the fix, on the re-check's mirrors and on
// further mutants. OLD is tests/purity.test.js as of b48d716 (the re-check mirrors hold byte-identical
// copies, CR aside). NEW is tests/purity.test.js in the working tree. Each run is one purity test file in a
// child Node process capped at 60 s. Mutants are served to the scan by ../20261009T123108/scan-hook.mjs,
// so nothing is copied or changed on disk. It writes no file. Usage: node scan-mutants.mjs
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = new URL("../../../../../../", import.meta.url);
const HOOK = new URL("../20261009T123108/scan-hook.mjs", import.meta.url).href; // --import takes a URL
const mirrors = new URL("docs/modules/habit-logic/qa/security/20261009T124854/mirrors/", root);
const mirror = (name, part) => fileURLToPath(new URL(`${name}/${part}`, mirrors));
const NEW_TEST = fileURLToPath(new URL("tests/purity.test.js", root));
const OLD_TEST = (name = "baseline-unchanged") => mirror(name, "tests/purity.test.js");

function scan(testFile, env) {
  const result = spawnSync(process.execPath, ["--import", HOOK, "--test-reporter=spec", testFile], {
    cwd: fileURLToPath(root),
    env: { ...process.env, ...env },
    encoding: "utf8",
    timeout: 60_000,
    killSignal: "SIGKILL",
  });
  if (result.error) return `ERROR ${result.error.code} (child pid ${result.pid})`;
  const lines = result.stdout.split(/\r?\n/);
  const count = (label) => lines.find((line) => line.startsWith(`ℹ ${label} `))?.split(" ")[2];
  const served = result.stderr.split(/\r?\n/).filter((line) => line.startsWith("scan-hook:")).length;
  // A run whose counts cannot be read did not run its tests, so it is never reported as green.
  if (count("pass") === undefined || count("fail") === undefined) {
    return `BROKEN: no test counts (child pid ${result.pid}, exit ${result.status}), stderr: ${result.stderr.trim().split(/\r?\n/).slice(-3).join(" / ")}`;
  }
  const failed = lines.filter((line) => line.startsWith("✖ @")).map((line) => line.replace(/ \([\d.]+ms\)$/, ""));
  const messages = lines.filter((line) => /^\s+AssertionError/.test(line)).map((line) => line.trim().replace(/^AssertionError \[ERR_ASSERTION\]: /, ""));
  const verdict = Number(count("fail")) > 0 ? "RED" : "GREEN";
  const detail = failed.length ? ` | failed: ${[...new Set(failed)].map((title, i) => `${title} [${messages[i] ?? "?"}]`).join("; ")}` : "";
  return `${verdict} ${count("pass")} pass ${count("fail")} fail (child pid ${result.pid}, exit ${result.status}, hook served ${served} reads)${detail}`;
}

console.log(`node ${process.version} ${process.platform}, typeof Temporal = ${typeof globalThis.Temporal}`);

console.log("\n## The re-check's mirrors (src/ read from the mirror)");
for (const name of ["baseline-unchanged", "hunt-Temporal-Now", "hunt-Reflect-construct-Date"]) {
  console.log(name);
  console.log(`  OLD: ${scan(OLD_TEST(name), {})}`);
  console.log(`  NEW: ${scan(NEW_TEST, { SCAN_SRC_DIR: mirror(name, "src") })}`);
}

const ANCHOR = "const NEXT_DAY = 1;";
const insert = (line) => JSON.stringify(["habits.js", ANCHOR, `${ANCHOR}\n${line}`]);
const MUTANTS = {
  "Temporal.Now.plainDateISO()": "const today = Temporal.Now.plainDateISO().toString();",
  "Temporal.Now.instant()": "const now = Temporal.Now.instant();",
  "Temporal . Now with spaces": "const zone = Temporal . Now . timeZoneId();",
  "eval building new Date": 'const now = eval("new " + "Da" + "te");',
  "eval passed as a value": "const run = eval;",
  "new Function building Date.now()": 'const read = new Function("return Da" + "te.now()");',
  "Function() building Date.now()": 'const read = Function("return Da" + "te.now()");',
};
const ALLOWED = {
  "Temporal.PlainDate arithmetic": "const next = Temporal.PlainDate.from(key).add({ days: 1 });",
  "Temporal.PlainDate weekday": 'const weekday = Temporal.PlainDate.from("2026-10-08").dayOfWeek;',
  "Temporal.PlainDate difference": 'const span = Temporal.PlainDate.from("2026-10-01").until("2026-10-08").days;',
  "a typeof check for functions": 'const callable = (value) => typeof value === "function";',
  "an identifier that ends in Function": "const result = toggleFunction(1);",
  "a comment that names eval and Function(": "// eval and Function( are words a comment may use",
};
const NOT_CAUGHT = {
  "Reflect.construct(Date, [])": "const now = Reflect.construct(Date, []);",
  "an aliased constructor": "const Clock = Date; const now = new Clock();",
  "new (Date)()": "const now = new (Date)();",
};

for (const [title, cases] of [
  ["Mutants, one line added to habits.js after the NEXT_DAY constant (must be RED under NEW)", MUTANTS],
  ["Allowed lines, added the same way (must stay GREEN)", ALLOWED],
  ["Deliberate evasions outside this fix (recorded, not claimed)", NOT_CAUGHT],
]) {
  console.log(`\n## ${title}`);
  for (const [label, line] of Object.entries(cases)) {
    console.log(`${label}: ${line}`);
    console.log(`  OLD: ${scan(OLD_TEST(), { SCAN_EDIT: insert(line) })}`);
    console.log(`  NEW: ${scan(NEW_TEST, { SCAN_EDIT: insert(line) })}`);
  }
}

console.log("\n## The real source, no hook edit");
console.log(`  NEW: ${scan(NEW_TEST, {})}`);
