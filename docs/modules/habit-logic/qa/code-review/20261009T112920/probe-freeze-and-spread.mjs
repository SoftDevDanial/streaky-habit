// 1. Does a frozen Date throw when a callee writes to it (the R16 frozen-input claim)?
// 2. Does object spread let a "__proto__" key from stored data reach the prototype (the copyHabit comment's claim)?
"use strict";
const date = Object.freeze(new Date(2026, 9, 8, 12));
const before = date.getTime();
let threw = false;
try { date.setDate(1); } catch { threw = true; }
console.log("frozen Date: setDate threw =", threw, "| value changed =", date.getTime() !== before);

const stored = JSON.parse('{"name":"A","done":[],"__proto__":{"polluted":true}}');
const spread = { ...stored };
console.log("spread: prototype is Object.prototype =", Object.getPrototypeOf(spread) === Object.prototype,
  "| own __proto__ key kept =", Object.hasOwn(spread, "__proto__"), "| ({}).polluted =", ({}).polluted);
const assigned = Object.assign({}, stored);
console.log("Object.assign: prototype is Object.prototype =", Object.getPrototypeOf(assigned) === Object.prototype,
  "| assigned.polluted =", assigned.polluted);
