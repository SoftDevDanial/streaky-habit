// Shows that storage.js decodeState/encodeState are pure and importable under Node, so the sort,
// de-duplication, strictness and literal-rebuild contract items can be unit tested without a browser.
// usage: node decode-unit.mjs <project root>
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const root = resolve(process.argv[2]);
const { decodeState, encodeState } = await import(pathToFileURL(resolve(root, "src/storage.js")).href);

const show = (label, value) => console.log(label.padEnd(44), JSON.stringify(value));

show("unsorted + duplicate days", decodeState('{"version":1,"habits":[{"name":"A","done":["2026-10-08","2026-10-07","2026-10-08"]}]}'));
show("mixed good and impossible date", decodeState('{"version":1,"habits":[{"name":"A","done":["2026-10-08","2026-02-30"]}]}'));
show("A, B, a (non-adjacent duplicate)", decodeState('{"version":1,"habits":[{"name":"A","done":[]},{"name":"B","done":[]},{"name":"a","done":[]}]}'));
const parsedProto = decodeState('{"version":1,"habits":[{"name":"A","done":[],"__proto__":{"polluted":true},"extra":1}]}');
show("__proto__ and extra key", parsedProto);
const habit = parsedProto.habits[0];
console.log("rebuilt literal, own keys only:".padEnd(44), Object.keys(habit).join(","), "| polluted?", habit.polluted, ({}).polluted);
show("encodeState drops extra props", JSON.parse(encodeState([{ name: "A", done: ["2026-10-08"], extra: 1 }])));
