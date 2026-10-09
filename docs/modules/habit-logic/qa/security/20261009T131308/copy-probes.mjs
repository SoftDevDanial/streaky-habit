// Security finder re-check 2 helper: copies the earlier probes (same folder depth, so their relative
// imports still reach src/) into this folder, so their outputs land here and earlier evidence stays as it
// was. Only files inside this folder are written, and none is overwritten.
import { copyFileSync, existsSync } from "node:fs";

const previous = new URL("../20261009T124854/", import.meta.url);
const names = [
  "capture.mjs",
  "probe-proto-and-keys.mjs",
  "probe-mutation.mjs",
  "probe-global-and-egress.mjs",
  "probe-history.mjs",
];
for (const name of names) {
  const target = new URL(`./${name}`, import.meta.url);
  if (existsSync(target)) throw new Error(`${name} already exists here, not overwritten`);
  copyFileSync(new URL(name, previous), target);
  console.log(`copied ${name}`);
}
