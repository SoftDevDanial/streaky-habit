// Loaded with --import by run-capped.mjs, and so by every process the test run starts (NODE_OPTIONS is
// inherited by the test files and by the child processes some tests start).
import fs from "node:fs";
import { register, syncBuiltinESMExports } from "node:module";
import { MUTANTS } from "./mutants.mjs";
import { EXTRA_MUTANTS } from "./mutants-extra.mjs";
import { EXTRA_MUTANTS_2 } from "./mutants-extra2.mjs";
import { applyEdits } from "./edits.mjs";

const mutant = { ...MUTANTS, ...EXTRA_MUTANTS, ...EXTRA_MUTANTS_2 }[process.env.MUTANT];
if (mutant === undefined) throw new Error(`unknown mutant ${process.env.MUTANT}`);

if (mutant.kind === "module") {
  register("./hooks.mjs", import.meta.url, { data: { file: mutant.file, edits: mutant.edits } });
} else {
  const realRead = fs.readFileSync;
  fs.readFileSync = function (path, ...rest) {
    const content = realRead.call(this, path, ...rest);
    if (typeof content === "string" && String(path).replaceAll("\\", "/").endsWith(`/src/${mutant.file}`)) {
      return applyEdits(content, mutant.edits, String(path));
    }
    return content;
  };
  syncBuiltinESMExports();
}
