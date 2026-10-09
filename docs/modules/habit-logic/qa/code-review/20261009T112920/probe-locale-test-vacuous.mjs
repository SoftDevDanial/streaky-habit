// Runs the exact child-process program of the "@R4 labels do not follow the runtime locale" test
// against a mutant that reads the runtime locale, with LANG and LC_ALL set to de_DE.UTF-8.
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const mutantUrl = pathToFileURL(resolve(process.argv[2])).href;
const program = `
  const { longDate, shortDate } = await import(${JSON.stringify(mutantUrl)});
  process.stdout.write(JSON.stringify([longDate("2026-10-08"), shortDate("2026-10-06"), Intl.DateTimeFormat().resolvedOptions().locale]));
`;
const output = execFileSync(process.execPath, ["--input-type=module", "--eval", program], {
  env: { ...process.env, LANG: "de_DE.UTF-8", LC_ALL: "de_DE.UTF-8" },
  encoding: "utf8",
  timeout: 15_000,
});
const [long, short, locale] = JSON.parse(output);
console.log("platform", process.platform, "node", process.version);
console.log("child default locale under LANG=de_DE.UTF-8:", locale);
console.log("mutant longDate:", JSON.stringify(long), "mutant shortDate:", JSON.stringify(short));
console.log("test assertion would PASS on the mutant:", long === "Thursday 8 October" && short === "Tue 6 Oct");
console.log("what a German device gets from the same mutant code:", new Date(2026, 9, 8).toLocaleDateString("de-DE", { weekday: "long" }));
