// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs it as the body of an async function after load. It opens M1 from the bin of "Stretch 10 minutes",
// the state of the delete-dialog.html golden (app qa.md, Fidelity gate). It throws when the state is not reached.
const fail = (why) => { throw new Error(`fidelity: open-delete-dialog.js ${why}`); };
if (navigator.clipboard && typeof Clipboard === "function" && Function.prototype.toString.call(Clipboard.prototype.writeText).includes("[native code]")) {
  fail("found no clipboard stand-in, so it clicks nothing");
}
const press = (selector) => {
  const node = document.querySelector(selector);
  if (!node) fail(`found no ${selector}`);
  node.click(); // detail 0, so neither guard of R13 and R14 holds it
};
press(`button.btn-bin[aria-label='Delete "Stretch 10 minutes"']`);
const remove = document.querySelector("dialog.dlg-del");
if (!remove?.open || !remove.matches(":modal")) fail("did not open M1 as a modal");
// The title wraps the name in two invisible isolate marks (spec R13 note, SEC-02), U+2068 before it and U+2069 after.
if (document.querySelector("#del-title").textContent !== 'Delete "\u{2068}Stretch 10 minutes\u{2069}"?') fail("found another title");
if (document.querySelectorAll("dialog[open]").length !== 1) fail("left another dialog open with M1");
// The golden draws no focus, and focus moved by script without a pointer gesture matches :focus-visible in Chromium.
