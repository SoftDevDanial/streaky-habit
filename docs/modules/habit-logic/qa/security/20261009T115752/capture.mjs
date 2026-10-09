// Security finder helper: runs one command with a 120 s cap and writes its output next to this script.
// Usage: node capture.mjs <output-name> <cwd> <command> [args...]   ("node" means this Node binary)
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";

const [outName, cwd, program, ...args] = process.argv.slice(2);
const executable = program === "node" ? process.execPath : program;
const started = Date.now();
const result = spawnSync(executable, args, {
  cwd,
  encoding: "utf8",
  timeout: 120_000,
  killSignal: "SIGKILL",
  maxBuffer: 64 * 1024 * 1024,
});
const text = [
  `command: ${program} ${args.join(" ")}`,
  `cwd: ${cwd}`,
  `runner: node ${process.version} on ${process.platform}`,
  `child pid: ${result.pid} exit: ${result.status} signal: ${result.signal} error: ${result.error?.code ?? "none"}`,
  `elapsed_ms: ${Date.now() - started}`,
  "--- stdout",
  result.stdout ?? "",
  "--- stderr",
  result.stderr ?? "",
].join("\n");
writeFileSync(new URL(`./${outName}`, import.meta.url), text);
process.stdout.write(text.length > 6000 ? `${text.slice(0, 1500)}\n[...]\n${text.slice(-4000)}` : text);
