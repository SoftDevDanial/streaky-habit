// Security solver helper (SEC-03), loaded with --import before a purity test file. It changes what the
// test's source scan READS for src/dates.js and src/habits.js, so the scan can be run on a mutant
// without copying or editing any file. The modules the test imports still load unchanged.
//   SCAN_SRC_DIR  read both files from this directory instead (an auditor mirror's src/)
//   SCAN_EDIT     JSON [file, from, to]: replace the one occurrence of `from` in that file's text
// Each served read is reported on stderr, so a run shows the hook took effect.
import fs from "node:fs";
import { syncBuiltinESMExports } from "node:module";
import { pathToFileURL } from "node:url";

const native = fs.readFileSync;
const SOURCE_FILE = /\/src\/(dates|habits)\.js$/;
const directory = process.env.SCAN_SRC_DIR;
const edit = process.env.SCAN_EDIT ? JSON.parse(process.env.SCAN_EDIT) : null;

fs.readFileSync = function readFileSync(path, ...rest) {
  const file = path instanceof URL ? path.href.match(SOURCE_FILE)?.[0].slice("/src/".length) : undefined;
  if (!file) return native.call(this, path, ...rest);
  if (directory) {
    process.stderr.write(`scan-hook: ${file} read from ${directory}\n`);
    return native.call(this, new URL(file, pathToFileURL(`${directory}/`)), ...rest);
  }
  const text = native.call(this, path, ...rest);
  if (!edit || edit[0] !== file) return text;
  const count = text.split(edit[1]).length - 1;
  if (count !== 1) throw new Error(`scan-hook: expected one ${JSON.stringify(edit[1])} in ${file}, found ${count}`);
  process.stderr.write(`scan-hook: ${file} served with the edit\n`);
  return text.replace(edit[1], edit[2]);
};
syncBuiltinESMExports();
