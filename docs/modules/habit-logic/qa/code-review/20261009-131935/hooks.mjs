// Module-loader hook: serves src/<file> with the mutant's edits applied, in memory. Each edit must match
// exactly once, so a mutant that does not apply fails loudly instead of passing as a clean run.
import { applyEdits } from "./edits.mjs";

let target = { file: "", edits: [] };

export function initialize(data) {
  target = data;
}

export async function load(url, context, nextLoad) {
  const result = await nextLoad(url, context);
  if (target.file === "" || !url.endsWith(`/src/${target.file}`)) return result;
  const text = Buffer.from(result.source).toString("utf8");
  return { ...result, source: applyEdits(text, target.edits, url), shortCircuit: true };
}
