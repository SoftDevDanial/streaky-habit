// Security solver probe (SEC-01, round 2): the re-check's inputs against three versions of habits.js,
// 59c6ee5 (no bound), eb2003b (size bound only) and src/ (valid keys only, plus the bound). Each call runs
// in a child Node process capped at 8 s with SIGKILL. An earlier version is passed to the child on stdin
// as a data: URL, so nothing is copied to disk. It writes no file. Usage: node sec01-attack.mjs
import { execFileSync, spawnSync } from "node:child_process";

const root = new URL("../../../../../../", import.meta.url);
const datesUrl = new URL("src/dates.js", root).href;
const CAP_MS = 8_000;

function versionUrl(rev) {
  if (rev === "src") return new URL("src/habits.js", root).href;
  const source = execFileSync("git", ["show", `${rev}:src/habits.js`], { cwd: root, encoding: "utf8" });
  const text = source.replace('from "./dates.js"', `from ${JSON.stringify(datesUrl)}`);
  return `data:text/javascript;base64,${Buffer.from(text).toString("base64")}`;
}

// The same spelling scheme as the regression test: white space that Number() ignores, around each part.
const SETUP = `
  const FAR_START = "24660873954866-12-02";
  const FAR_STUCK = "24660873954866-12-04";
  const WHITE_SPACE = ["", " ", "\\t", "\\u00A0", "\\u2003", "\\u3000", "\\uFEFF"];
  function spellings(count) {
    const [year, month, day] = FAR_START.split("-");
    const keys = [];
    for (let i = 0; keys.length < count; i++) {
      const space = (place) => WHITE_SPACE[Math.floor(i / WHITE_SPACE.length ** place) % WHITE_SPACE.length];
      const key = space(5) + year + space(4) + "-" + space(3) + month + space(2) + "-" + space(1) + day + space(0);
      if (key !== FAR_START) keys.push(key);
    }
    return keys;
  }
  const back = (from, count) => { const keys = []; for (let k = from; keys.length < count; k = dates.addDays(k, -1)) keys.push(k); return keys; };
`;

function inChild(rev, url, label, body) {
  const program = `
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    const habits = await import(JSON.parse(Buffer.concat(chunks).toString("utf8")));
    const dates = await import(${JSON.stringify(datesUrl)});
    ${SETUP}
    const started = performance.now();
    const value = (() => { ${body} })();
    process.stdout.write(JSON.stringify({ value, ms: Math.round(performance.now() - started) }));
  `;
  const started = Date.now();
  const result = spawnSync(process.execPath, ["--input-type=module", "--eval", program], {
    input: JSON.stringify(url),
    encoding: "utf8",
    timeout: CAP_MS,
    killSignal: "SIGKILL",
  });
  const outcome =
    result.error?.code === "ETIMEDOUT"
      ? `HUNG: no result within ${CAP_MS / 1000} s, child pid ${result.pid} killed (signal ${result.signal})`
      : `returned ${result.stdout.trim()} (child pid ${result.pid}, exit ${result.status}${result.stderr ? `, stderr ${result.stderr.trim().split("\n").at(-1)}` : ""})`;
  console.log(`  ${rev.padEnd(7)} ${label}: ${outcome}, wall ${Date.now() - started} ms`);
}

console.log(`node ${process.version} ${process.platform}`);
const versions = ["59c6ee5", "eb2003b", "src"].map((rev) => [rev, versionUrl(rev)]);
const CASES = [
  ["bestStreak(20,000 spellings + FAR_STUCK)", "return habits.bestStreak([...spellings(20000), FAR_STUCK]);"],
  ["bestStreak(three valid keys + FAR_START + FAR_STUCK)", 'return habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", FAR_START, FAR_STUCK]);'],
  ["currentStreak(400 days back from 0001-01-10, \"0001-01-10\")", 'return habits.currentStreak(back("0001-01-10", 400), "0001-01-10");'],
  ["bestStreak(400 days back from 0001-01-10)", 'return habits.bestStreak(back("0001-01-10", 400));'],
  ["currentStreak(800,000 days back from 2026-10-08, \"2026-10-08\")", 'return habits.currentStreak(back("2026-10-08", 800000), "2026-10-08");'],
  ["bestStreak(the same 800,000 keys)", 'return habits.bestStreak(back("2026-10-08", 800000));'],
];
for (const [label, body] of CASES) {
  console.log(label);
  for (const [rev, url] of versions) inChild(rev, url, label, body);
}

console.log("bestStreak(90,000 spellings + FAR_STUCK), about 3 MB stored, the quota-sized attack");
inChild("src", versions[2][1], "bestStreak(90,000 spellings + FAR_STUCK)", "return habits.bestStreak([...spellings(90000), FAR_STUCK]);");

console.log("Cost of the filter on valid input: 400,000 consecutive valid days, median of 3 runs in one child");
const timing = `
  const keys = back("2026-10-08", 400000);
  const median = (run) => { const t = []; let v; for (let i = 0; i < 3; i++) { const s = performance.now(); v = run(); t.push(performance.now() - s); } t.sort((a, b) => a - b); return v + " in " + Math.round(t[1]) + " ms"; };
  return { bestStreak: median(() => habits.bestStreak(keys)), currentStreak: median(() => habits.currentStreak(keys, "2026-10-08")) };
`;
for (const [rev, url] of versions.slice(1)) inChild(rev, url, "400,000 valid days", timing);
