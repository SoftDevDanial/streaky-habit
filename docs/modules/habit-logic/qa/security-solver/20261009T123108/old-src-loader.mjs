// Security solver helper: when OLD_SRC_REV is set, every import of src/habits.js loads that revision's
// text from git instead, in memory, so the current tests can be run against the code before a fix without
// changing src/. Passed as NODE_OPTIONS="--import=<this file's URL>", so the test runner's children and
// the tests' own child processes load it too. Each served import is reported on stderr.
import { execFileSync } from "node:child_process";
import { registerHooks } from "node:module";

const rev = process.env.OLD_SRC_REV;
const root = new URL("../../../../../../", import.meta.url);
const target = new URL("src/habits.js", root).href.toLowerCase();
const source = rev ? execFileSync("git", ["show", `${rev}:src/habits.js`], { cwd: root, encoding: "utf8" }) : null;

registerHooks({
  load(url, context, nextLoad) {
    if (!source || url.toLowerCase() !== target) return nextLoad(url, context);
    process.stderr.write(`old-src-loader: src/habits.js served from ${rev} in pid ${process.pid}\n`);
    return { format: "module", source, shortCircuit: true };
  },
});
