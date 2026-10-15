// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs it as the body of an async function after load. It opens P2 for "Read 20 pages" from the row's
// Year, the state of the year-view.html golden (app qa.md, Fidelity gate). It throws when the state is not reached.
const fail = (why) => { throw new Error(`fidelity: open-year-view.js ${why}`); };
if (navigator.clipboard && typeof Clipboard === "function" && Function.prototype.toString.call(Clipboard.prototype.writeText).includes("[native code]")) {
  fail("found no clipboard stand-in, so it clicks nothing");
}
const press = (selector) => {
  const node = document.querySelector(selector);
  if (!node) fail(`found no ${selector}`);
  node.click(); // detail 0, so neither guard of R13 and R14 holds it
};
press('button.btn-year[aria-label="Year view, Read 20 pages"]');
const year = document.querySelector("dialog.dlg-year");
if (!year?.open) fail("did not open P2");
if (document.querySelector("#yr-title").textContent !== "Read 20 pages") fail("opened P2 for another habit");
if (document.querySelectorAll("dialog[open]").length !== 1) fail("left another dialog open with P2");
if (year.querySelector("div.sheet-body").scrollTop !== 0) fail("left P2 scrolled");
// The golden draws no focus, and focus moved by script without a pointer gesture matches :focus-visible in Chromium.
