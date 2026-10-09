// Runs one node command from the project root with a hard time cap, optionally under a mutant.
// Usage: node run-capped.mjs <seconds> <MUTANT name or -> <node arguments...>
// Prints the child's pid and exit state, then the test summary lines and the failing test names, or the
// whole stdout when the child is not a test run. Writes no file. The mutants live in mutants.mjs and are
// applied in memory by preload.mjs, so src/ and tests/ are never touched.
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const [seconds, mutant, ...nodeArguments] = process.argv.slice(2);
const root = fileURLToPath(new URL("../../../../../../", import.meta.url));
const preload = pathToFileURL(fileURLToPath(new URL("./preload.mjs", import.meta.url))).href;

const env = { ...process.env };
if (mutant !== "-") {
  env.MUTANT = mutant;
  env.NODE_OPTIONS = `--import ${preload}`;
}

const started = Date.now();
const run = spawnSync(process.execPath, nodeArguments, {
  cwd: root,
  env,
  encoding: "utf8",
  timeout: Number(seconds) * 1000,
  killSignal: "SIGKILL",
  maxBuffer: 256 * 1024 * 1024,
});
const elapsed = Date.now() - started;

console.log(`root ${root}`);
console.log(`PID ${run.pid} mutant ${mutant} exit ${run.status} signal ${run.signal} ${run.error ? `error ${run.error.code}` : ""} ${elapsed} ms`);
const out = run.stdout ?? "";
const summary = out.split("\n").filter((line) => /^ℹ (tests|pass|fail|cancelled|skipped) /.test(line));
if (summary.length > 0) {
  console.log(summary.join("\n"));
  const failed = [...new Set(out.split("\n").filter((line) => /^\s*✖/.test(line)).map((line) => line.trim()))];
  console.log(failed.length === 0 ? "FAILED: none" : `FAILED:\n${failed.join("\n")}`);
} else {
  console.log(out.trimEnd());
}
if ((run.stderr ?? "").trim() !== "") console.log(`STDERR:\n${run.stderr.trimEnd().slice(0, 3000)}`);
