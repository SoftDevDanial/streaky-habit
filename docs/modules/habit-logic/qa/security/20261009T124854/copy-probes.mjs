// Security finder re-check helper: copies the first audit's probes (same folder depth, so their relative
// imports still reach src/) into this folder, so their outputs land here and the first audit's evidence
// stays as it was. Only files inside this folder are written.
import { copyFileSync, existsSync } from "node:fs";

const first = new URL("../20261009T115752/", import.meta.url);
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
  copyFileSync(new URL(name, first), target);
  console.log(`copied ${name}`);
}
