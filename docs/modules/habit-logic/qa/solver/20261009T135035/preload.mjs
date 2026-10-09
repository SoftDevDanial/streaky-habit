// Loaded with --import by run-capped.mjs. Same mechanism as the reviewer's preload (module mutants through
// the loader hook, scan mutants through fs.readFileSync), with the solver's mutants added to the reviewer's
// tables. hooks.mjs and edits.mjs are the reviewer's files, imported from their folder, not copied.
import fs from "node:fs";
import { register, syncBuiltinESMExports } from "node:module";
import { MUTANTS } from "../../code-review/20261009-131935/mutants.mjs";
import { EXTRA_MUTANTS } from "../../code-review/20261009-131935/mutants-extra.mjs";
import { EXTRA_MUTANTS_2 } from "../../code-review/20261009-131935/mutants-extra2.mjs";
import { applyEdits } from "../../code-review/20261009-131935/edits.mjs";
import { SOLVER_MUTANTS } from "./mutants.mjs";

const mutant = { ...MUTANTS, ...EXTRA_MUTANTS, ...EXTRA_MUTANTS_2, ...SOLVER_MUTANTS }[process.env.MUTANT];
if (mutant === undefined) throw new Error(`unknown mutant ${process.env.MUTANT}`);

if (mutant.kind === "module") {
  register("../../code-review/20261009-131935/hooks.mjs", import.meta.url, {
    data: { file: mutant.file, edits: mutant.edits },
  });
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
