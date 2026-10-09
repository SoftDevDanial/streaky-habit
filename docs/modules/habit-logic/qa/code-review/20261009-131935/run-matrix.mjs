// Runs every mutant of the mutation table once, from the project root, each child capped at 120 s, and
// prints one line per run: scope, mutant, child pid, exit code, pass/fail counts and the failing tests.
// The children are run one after the other. Writes no file. A mutant whose edit does not match exactly
// once throws inside the child and shows up as an exit code 1 with a "mutant edit matched" error.
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = fileURLToPath(new URL("../../../../../../", import.meta.url));
const preload = pathToFileURL(fileURLToPath(new URL("./preload.mjs", import.meta.url))).href;
const FULL = ["--test", "tests/**/*.test.js"];

const rows = [
  ["-", "full suite", FULL],
  // WR-02 and bound: mutants that must survive or must be killed
  ["bound-removed", "full suite", FULL],
  ["bound-zero", "full suite", FULL],
  ["date-arg-partial", "full suite", FULL],
  ["date-arg-sethours", "full suite", FULL],
  // WR-04, WR-05
  ["strip-5", "full suite", FULL],
  ["month-year-only", "full suite", FULL],
  ["sunday-first", "full suite", FULL],
  ["runcontinues-second-day", "full suite", FULL],
  // SEC-01, SEC-02
  ["current-unfiltered", "full suite", FULL],
  ["best-unfiltered", "full suite", FULL],
  ["filter-useless", "full suite", FULL],
  ["longer-than-ge", "full suite", FULL],
  ["name-length-array", "full suite", FULL],
  // WR-10
  ["trim-plain-space-only", "full suite", FULL],
  // WR-01: only the weekday name changes, and only on a non-English default locale
  ["locale-weekday-toLocaleDateString", "dates.test.js", ["--test", "tests/dates.test.js"]],
  ["locale-weekday-Intl", "dates.test.js", ["--test", "tests/dates.test.js"]],
  ["locale-number-toLocaleString", "dates.test.js", ["--test", "tests/dates.test.js"]],
  // purity scan (text only, never executed)
  ["scan-control", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s1-url-string-same-line", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s2-slash-star-in-string", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s3-slash-star-in-line-comment", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s3b-slash-star-in-line-comment", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s3c-slash-star-in-line-comment-network", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s5-control-second-import-visible", "purity.test.js", ["--test", "tests/purity.test.js"]],
  ["scan-s5-second-import-hidden", "purity.test.js", ["--test", "tests/purity.test.js"]],
];

for (const [mutant, scope, args] of rows) {
  const env = { ...process.env };
  if (mutant !== "-") {
    env.MUTANT = mutant;
    env.NODE_OPTIONS = `--import ${preload}`;
  }
  const run = spawnSync(process.execPath, args, { cwd: root, env, encoding: "utf8", timeout: 120_000, killSignal: "SIGKILL", maxBuffer: 256 * 1024 * 1024 });
  const out = run.stdout ?? "";
  const count = (name) => (out.match(new RegExp(`^ℹ ${name} (\\d+)`, "m")) ?? [])[1] ?? "?";
  const failed = [...new Set(out.split("\n").filter((line) => /^\s*✖/.test(line) && !/failing tests/.test(line)).map((line) => line.trim().replace(/\s*\([\d.]+ms\)$/, "")))];
  const broken = (run.stderr ?? "").includes("mutant edit matched") ? " BROKEN MUTANT EDIT" : "";
  console.log(`${mutant.padEnd(44)} ${scope.padEnd(14)} pid ${String(run.pid).padStart(5)} exit ${run.status} pass ${count("pass")} fail ${count("fail")}${broken}${failed.length ? `\n    red: ${failed.join(" | ")}` : ""}`);
}
