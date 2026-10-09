// Solver mutants for the 2026-10-09 re-check batch, same format as the reviewer's mutants.mjs. Applied in
// memory by preload.mjs, so src/ and tests/ are never written. Each edit must match exactly once.
// WR-14: one mutant per Date setter, so each of minutes, seconds and milliseconds is proved on its own.
const RETURN_LINE = "  return formatKey(date.getFullYear(), date.getMonth() + 1, date.getDate());";

const writeToArgument = (setter) => ({
  kind: "module",
  file: "dates.js",
  edits: [{ from: RETURN_LINE, to: `  date.${setter};\n${RETURN_LINE}` }],
});

export const SOLVER_MUTANTS = {
  "date-arg-minutes-only": writeToArgument("setMinutes(0)"),
  "date-arg-seconds-only": writeToArgument("setSeconds(0)"),
  "date-arg-milliseconds-only": writeToArgument("setMilliseconds(0)"),
};
