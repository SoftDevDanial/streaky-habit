// Scan mutants for the import rule, same format as mutants.mjs. Text only, never executed.
// The first extra import sits in plain sight (control). The second is hidden from tests/purity.test.js by
// a "/*" inside a line comment above it.
const IMPORT_LINE = 'import { addDays, dayParts, isDateKey, weekdayIndex } from "./dates.js";\n';

export const EXTRA_MUTANTS_2 = {
  "scan-s5-control-second-import-visible": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: IMPORT_LINE, to: `${IMPORT_LINE}import { send } from "./net.js";\n` }],
  },
  "scan-s5-second-import-hidden": {
    kind: "scan",
    file: "habits.js",
    edits: [{ from: IMPORT_LINE, to: `${IMPORT_LINE}// every file under src/*\nimport { send } from "./net.js";\n` }],
  },
};
