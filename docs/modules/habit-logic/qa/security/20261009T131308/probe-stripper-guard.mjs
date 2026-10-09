// Security re-check 2: (1) shows what the test's comment stripper leaves of the two blind-spot mirrors,
// (2) checks a candidate guard for the assumption stated at tests/purity.test.js:10-11 (no string literal
// holding // or /*) on HEAD's source and on the mirrors, (3) lists the code points of WHITE_SPACE in
// tests/habits.test.js. Read-only on src/ and tests/.
import { readFileSync, writeFileSync } from "node:fs";

const root = new URL("../../../../../../", import.meta.url);
const withoutComments = (text) => text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
const GUARD = /(["'`])[^"'`\n]*?(?:\/\/|\/\*)[^"'`\n]*?\1/;
const lines = [];

for (const [label, url] of [
  ["HEAD src/dates.js", new URL("src/dates.js", root)],
  ["HEAD src/habits.js", new URL("src/habits.js", root)],
  ["mirror hunt-banned-after-url-string", new URL("./mirrors/hunt-banned-after-url-string/src/habits.js", import.meta.url)],
  ["mirror hunt-banned-after-mime-string", new URL("./mirrors/hunt-banned-after-mime-string/src/habits.js", import.meta.url)],
]) {
  const text = readFileSync(url, "utf8");
  const code = withoutComments(text);
  const guard = text.match(GUARD);
  lines.push(`${label}: guard ${guard ? `HIT ${JSON.stringify(guard[0])}` : "no hit"}; stripped code holds fetch ${/\bfetch\b/.test(code)}, sessionStorage ${/\bsessionStorage\b/.test(code)}; raw text holds fetch ${/\bfetch\b/.test(text)}, sessionStorage ${/\bsessionStorage\b/.test(text)}`);
}
{
  const text = readFileSync(new URL("./mirrors/hunt-banned-after-mime-string/src/habits.js", import.meta.url), "utf8");
  const start = text.indexOf('const ACCEPT = "*/*"');
  const removed = text.length - withoutComments(text).length;
  const hiddenUntil = text.indexOf("*/", start + 'const ACCEPT = "*'.length + 1);
  lines.push(`mime mirror: the "/*" inside "*/*" starts a block the stripper removes up to the next "*/", ${text.slice(start, hiddenUntil + 2).split("\n").length} lines from that string`);
  lines.push(`mime mirror: stripper removes ${removed} characters in all`);
}
{
  const test = readFileSync(new URL("tests/habits.test.js", root), "utf8");
  const line = test.split("\n").find((l) => l.startsWith("const WHITE_SPACE"));
  const points = [...line].filter((c) => c.codePointAt(0) > 0x7e || c === "\t").map((c) => `U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, "0")}`);
  lines.push(`tests/habits.test.js WHITE_SPACE line: non-ASCII or tab characters written raw: ${points.join(", ") || "none"}`);
}

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-stripper-guard.txt", import.meta.url), text);
process.stdout.write(text);
