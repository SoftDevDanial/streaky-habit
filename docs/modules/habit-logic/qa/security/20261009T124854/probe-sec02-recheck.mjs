// Security re-check of SEC-02 at HEAD. Compares validateName at HEAD with the 59c6ee5 version (loaded from
// git into memory as a data: URL, src/ untouched) on 5,000,000-unit names for time and heap, spot-checks
// that the count is unchanged, and probes the residual for non-string input the solver stated.
// Run with: node --expose-gc probe-sec02-recheck.mjs
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import * as head from "../../../../../../src/habits.js";

const lines = [];
const output = new URL("./probe-sec02-recheck.txt", import.meta.url);
const log = (...parts) => {
  lines.push(parts.join(" "));
  console.log(parts.join(" "));
  writeFileSync(output, lines.join("\n") + "\n");
};
const gc = globalThis.gc ?? (() => {});
const root = new URL("../../../../../../", import.meta.url);
const pids = [];

const show = spawnSync("git", ["show", "59c6ee5:src/habits.js"], { cwd: root, encoding: "utf8", timeout: 30_000, killSignal: "SIGKILL" });
pids.push(show.pid);
if (show.status !== 0) throw new Error(`git show failed: ${show.stderr}`);
const datesUrl = new URL("src/dates.js", root).href;
const oldSource = show.stdout.replace('from "./dates.js"', `from ${JSON.stringify(datesUrl)}`);
const old = await import(`data:text/javascript,${encodeURIComponent(oldSource)}`);
log(`node ${process.version} ${process.platform}, gc exposed ${typeof globalThis.gc === "function"}`);
log(`59c6ee5 habits.js loaded in memory (git show pid ${show.pid}), uses Array.from: ${oldSource.includes("Array.from(name)")}; HEAD uses longerThan`);

log("\n## Time and heap growth across one validateName call, no collection between before and after");
const names = {
  "ASCII x 5,000,000": "x".repeat(5_000_000),
  "CJK 5,000,000 units": "一".repeat(5_000_000),
  "emoji 5,000,000 units": "\u{1F4DA}".repeat(2_500_000),
  "41 lone surrogates": "\uD800".repeat(41),
};
for (const [label, name] of Object.entries(names)) {
  const row = [];
  for (const [version, module] of [["59c6ee5", old], ["HEAD", head]]) {
    gc();
    gc();
    const before = process.memoryUsage().heapUsed;
    const started = performance.now();
    const result = module.validateName(name, ["Read 20 pages"]);
    const ms = performance.now() - started;
    const grown = (process.memoryUsage().heapUsed - before) / 1048576;
    row.push(`${version} ${ms.toFixed(3)} ms, heap +${grown.toFixed(2)} MiB, ${result.ok ? "ok" : result.error}`);
  }
  log(`${label}: ${row.join(" | ")}`);
}

log("\n## Same result as 59c6ee5 on edge strings");
const edges = ["", "   ", "a".repeat(40), "a".repeat(41), "\uD800".repeat(40), "\uD800".repeat(41), "𐀀".repeat(40),
  "𐀀".repeat(41), "\uDC00\uD800".repeat(20), "\uDC00\uD800".repeat(21), "é".repeat(20), "é".repeat(21),
  ` ${"b".repeat(40)} `, "​".repeat(40), "​".repeat(41)];
let mismatches = 0;
for (const name of edges) {
  if (JSON.stringify(old.validateName(name, [])) !== JSON.stringify(head.validateName(name, []))) mismatches++;
}
log(`${edges.length} edge strings, ${mismatches} mismatches`);

log("\n## Non-string raw (outside the contract raw: string; app readable rule 4 type-checks first)");
const cases = {
  "trim() returns { length: 50 }": { trim: () => ({ length: 50 }) },
  "trim() returns an array of 41 letters": { trim: () => Array(41).fill("a") },
  "trim() returns a number": { trim: () => 42 },
};
for (const [label, raw] of Object.entries(cases)) {
  const row = [];
  for (const [version, module] of [["59c6ee5", old], ["HEAD", head]]) {
    try {
      row.push(`${version} ${JSON.stringify(module.validateName(raw, []))}`);
    } catch (error) {
      row.push(`${version} throws ${error.constructor.name}`);
    }
  }
  log(`${label}: ${row.join(" | ")}`);
}
// An endless iterable from trim(): the old Array.from never returns, so both run in capped children.
for (const [version, url] of [["59c6ee5", `data:text/javascript,${encodeURIComponent(oldSource)}`], ["HEAD", new URL("src/habits.js", root).href]]) {
  const program = `
    const { validateName } = await import(${JSON.stringify(url)});
    const raw = { trim: () => ({ *[Symbol.iterator]() { for (;;) yield "a"; } }) };
    process.stdout.write(JSON.stringify(validateName(raw, [])));
  `;
  const result = spawnSync(process.execPath, ["--input-type=module", "--max-old-space-size=256", "--eval", program], {
    encoding: "utf8", timeout: 5_000, killSignal: "SIGKILL",
  });
  pids.push(`${result.pid}${result.error?.code === "ETIMEDOUT" ? " (killed at cap)" : ""}`);
  const outcome = result.error?.code === "ETIMEDOUT"
    ? `no result within 5 s, child pid ${result.pid} killed`
    : `exit ${result.status}, ${result.stdout.trim() || result.stderr.trim().split("\n").filter(Boolean).at(-1)}`;
  log(`trim() returns an endless iterable, ${version}: ${outcome} (child pid ${result.pid})`);
}

log(`\nchild pids: ${pids.join(", ")}`);
