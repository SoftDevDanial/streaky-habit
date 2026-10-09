// Security probe: checks the scan patterns proposed in SEC-03 against the real source (must find nothing),
// against each mirror (must find the planted read or call) and against short synthetic lines (allowed
// constructions with arguments must not hit). Comment stripping is the same as in tests/purity.test.js.
import { readFileSync, writeFileSync } from "node:fs";

const withoutComments = (text) => text.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

// Whole text, comments included (as the current clock check reads it).
const CLOCK_PATTERNS = {
  "current: Date.now(": (text) => text.includes("Date.now("),
  "current: new Date()": (text) => /new\s+Date\s*\(\s*\)/.test(text),
  "proposed: argument-less new Date, with or without ()": (text) => /\bnew\s+Date\b(?!\s*\(\s*[^\s)])/.test(text),
  "proposed: Date called as a function": (text) => /(?<!\bnew\s+|[.\w$])Date\s*\(/.test(text),
  "proposed: performance.now or Math.random": (text) => /\bperformance\s*\.\s*now\b|\bMath\s*\.\s*random\b/.test(text),
};
// Code only, comments removed.
const CODE_WORDS = /\b(fetch|XMLHttpRequest|WebSocket|EventSource|navigator|sendBeacon|sessionStorage|indexedDB|caches|setTimeout|setInterval|setImmediate|queueMicrotask|requestAnimationFrame|self|process)\b/;

const lines = [];

const samples = {
  "synthetic `new Date(2026, 9, 8)` (allowed, must not hit)": "const d = new Date(2026, 9, 8);",
  "synthetic `new Date(key)` (allowed, must not hit)": "const d = new Date(key);",
  "synthetic `Date.UTC(2026, 0, 1)` (allowed, must not hit)": "const ms = Date.UTC(2026, 0, 1);",
  "synthetic `new Date;` (must hit)": "const d = new Date;",
  "synthetic `new Date( )` (must hit)": "const d = new Date( );",
  "synthetic `Date()` (must hit)": "const s = Date();",
};
for (const [label, text] of Object.entries(samples)) {
  const hits = Object.entries(CLOCK_PATTERNS).filter(([name, test]) => name.startsWith("proposed") && test(text)).map(([name]) => name);
  lines.push(`${label}: ${hits.length ? hits.join("; ") : "no hit"}`);
}

const sources = { "real src": new URL("../../../../../../src/", import.meta.url) };
for (const name of ["baseline-unchanged", "control-clock-new-Date-with-parens", "clock-new-Date-without-parens",
  "clock-Date-called-as-function", "egress-fetch-and-sessionStorage"]) {
  sources[`mirror ${name}`] = new URL(`./mirrors/${name}/src/`, import.meta.url);
}
for (const [label, dir] of Object.entries(sources)) {
  const hits = [];
  for (const file of ["dates.js", "habits.js"]) {
    const text = readFileSync(new URL(file, dir), "utf8");
    for (const [name, test] of Object.entries(CLOCK_PATTERNS)) if (test(text)) hits.push(`${file} ${name}`);
    const word = withoutComments(text).match(CODE_WORDS);
    if (word) hits.push(`${file} proposed code word "${word[1]}"`);
  }
  lines.push(`${label}: ${hits.length ? hits.join("; ") : "no hit"}`);
}

const text = lines.join("\n") + "\n";
writeFileSync(new URL("./probe-scan-patterns.txt", import.meta.url), text);
process.stdout.write(text);
