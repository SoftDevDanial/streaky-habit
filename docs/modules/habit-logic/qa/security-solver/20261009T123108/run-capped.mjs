// Security solver helper: runs one command with a 120 s cap and prints its output with the child's pid,
// so every run in this folder is bounded and accounted for. It writes no file.
// Usage: node run-capped.mjs <cwd> <program> [args...]   ("node" means this Node binary)
import { spawnSync } from "node:child_process";

const [cwd, program, ...args] = process.argv.slice(2);
const executable = program === "node" ? process.execPath : program;
const started = Date.now();
const result = spawnSync(executable, args, {
  cwd,
  encoding: "utf8",
  timeout: 120_000,
  killSignal: "SIGKILL",
  maxBuffer: 64 * 1024 * 1024,
});
process.stdout.write(
  [
    `command: ${program} ${args.join(" ")}`,
    `runner: node ${process.version} on ${process.platform}, runner pid ${process.pid}`,
    `child pid: ${result.pid} exit: ${result.status} signal: ${result.signal} error: ${result.error?.code ?? "none"}`,
    `elapsed_ms: ${Date.now() - started}`,
    "--- stdout",
    result.stdout ?? "",
    "--- stderr",
    result.stderr ?? "",
  ].join("\n"),
);
