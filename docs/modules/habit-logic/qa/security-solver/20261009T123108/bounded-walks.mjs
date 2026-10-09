// Security solver probe (SEC-01): the inputs that hung in the audit, against the code in src/. Each call
// runs in a child Node process capped at 5 s with SIGKILL, so a hang is measured, reported and killed.
// It writes no file.
import { spawnSync } from "node:child_process";

const root = new URL("../../../../../../", import.meta.url);
const habitsUrl = new URL("src/habits.js", root).href;
const datesUrl = new URL("src/dates.js", root).href;
console.log(`node ${process.version} ${process.platform}, habits.js from src/`);

function inChild(label, body) {
  const program = `
    import * as habits from ${JSON.stringify(habitsUrl)};
    import * as dates from ${JSON.stringify(datesUrl)};
    const started = performance.now();
    const value = (() => { ${body} })();
    process.stdout.write(JSON.stringify({ value, ms: Math.round(performance.now() - started) }));
  `;
  const started = Date.now();
  const result = spawnSync(process.execPath, ["--input-type=module", "--eval", program], {
    encoding: "utf8",
    timeout: 5_000,
    killSignal: "SIGKILL",
  });
  const outcome =
    result.error?.code === "ETIMEDOUT"
      ? `HUNG: no result within 5 s, child pid ${result.pid} killed (signal ${result.signal})`
      : `returned ${result.stdout.trim()} (child pid ${result.pid}, exit ${result.status}${result.stderr ? `, stderr ${result.stderr.trim().split("\n").at(-1)}` : ""})`;
  console.log(`${label}: ${outcome}, wall ${Date.now() - started} ms`);
}

const S = JSON.stringify("24660873954866-12-02");
const T = JSON.stringify("24660873954866-12-04");
const chain = `const done = []; for (let k = "0000-01-03", i = 0; i < 30; i++, k = dates.addDays(k, -1)) done.push(k);`;
const backFrom2026 = `const done = []; for (let k = "2026-10-08", i = 0; i < 800000; i++, k = dates.addDays(k, -1)) done.push(k);`;

inChild("control: bestStreak([\"2026-10-08\"])", `return habits.bestStreak(["2026-10-08"]);`);
inChild(`bestStreak([${S}, ${T}])`, `return habits.bestStreak([${S}, ${T}]);`);
inChild(`bestStreak(three valid keys plus ${S} and ${T})`,
  `return habits.bestStreak(["2026-10-06", "2026-10-07", "2026-10-08", ${S}, ${T}]);`);
inChild(`currentStreak(30 steps back from 0000-01-03, a 12-key cycle, "0000-01-03")`,
  `${chain} return [habits.currentStreak(done, "0000-01-03"), new Set(done).size];`);
inChild(`bestStreak(the same 12-key cycle)`, `${chain} return habits.bestStreak(done);`);
inChild(`currentStreak(every day back from 2026-10-08 for 800,000 days, "2026-10-08")`,
  `${backFrom2026} return [habits.currentStreak(done, "2026-10-08"), new Set(done).size];`);
inChild(`bestStreak(the same 800,000 keys)`, `${backFrom2026} return habits.bestStreak(done);`);
inChild(`same 800,000 keys filtered by isDateKey first (what the decoder would keep)`,
  `${backFrom2026} const kept = done.filter(dates.isDateKey); return [habits.currentStreak(kept, "2026-10-08"), habits.bestStreak(kept), kept.length];`);
