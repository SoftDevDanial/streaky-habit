// Independent probe for the qa.md scenario "R4 Labels do not follow the runtime locale".
// ICU on Windows ignores LANG and LC_ALL, so the child makes de-DE the default of Intl.DateTimeFormat and of
// Date's toLocale* methods before it imports src/dates.js. The child reports its precondition first.
// A control child runs the same probe without the German patch, to show the patch is what makes German the default.
// Run: node <absolute path to this file>. Exits 1 on any FAIL.
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const ROOT = "{workspace}/examples/streaks";
const datesHref = pathToFileURL(`${ROOT}/src/dates.js`).href;

const patched = `
  const pick = (locales) => (locales === undefined ? "de-DE" : locales);
  const Native = Intl.DateTimeFormat;
  Intl.DateTimeFormat = function DateTimeFormat(locales, options) {
    return new Native(pick(locales), options);
  };
  Intl.DateTimeFormat.prototype = Native.prototype;
  for (const name of ["toLocaleDateString", "toLocaleString", "toLocaleTimeString"]) {
    const native = Date.prototype[name];
    Date.prototype[name] = function (locales, options) {
      return native.call(this, pick(locales), options);
    };
  }
  const thursday = new Date(2026, 9, 8);
  const precondition = [
    thursday.toLocaleDateString(undefined, { weekday: "long" }),
    new Intl.DateTimeFormat(undefined, { weekday: "long" }).format(thursday),
  ];
  const dates = await import(${JSON.stringify(datesHref)});
  process.stdout.write(JSON.stringify({ precondition, long: dates.longDate("2026-10-08"), short: dates.shortDate("2026-10-06") }));
`;

const control = `
  const thursday = new Date(2026, 9, 8);
  const precondition = [
    thursday.toLocaleDateString(undefined, { weekday: "long" }),
    new Intl.DateTimeFormat(undefined, { weekday: "long" }).format(thursday),
  ];
  process.stdout.write(JSON.stringify({ precondition }));
`;

const env = { ...process.env, LANG: "de_DE.UTF-8", LC_ALL: "de_DE.UTF-8" };
const run = (program) =>
  JSON.parse(
    execFileSync(process.execPath, ["--input-type=module", "--eval", program], {
      env,
      encoding: "utf8",
      timeout: 15_000,
    }),
  );

let failures = 0;
function row(label, actual, expected) {
  const pass = JSON.stringify(actual) === JSON.stringify(expected);
  if (!pass) failures++;
  console.log(`${pass ? "PASS" : "FAIL"} | R4 | Labels do not follow the runtime locale | ${label} | actual ${JSON.stringify(actual)} | expected ${JSON.stringify(expected)}`);
}

const control_out = run(control);
console.log(`CONTROL (no German patch) precondition ${JSON.stringify(control_out.precondition)}`);

const out = run(patched);
row("child precondition: long weekday of 8 Oct 2026 is German, via toLocaleDateString and Intl", out.precondition, ["Donnerstag", "Donnerstag"]);
row("longDate(2026-10-08) and shortDate(2026-10-06) under the German default", [out.long, out.short], ["Thursday 8 October", "Tue 6 Oct"]);
console.log(`SUMMARY scenario R4 locale failures=${failures}`);
process.exitCode = failures === 0 ? 0 : 1;
