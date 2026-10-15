// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs it as the body of an async function after load. It opens P3 from the Overview button, the state of
// the overview.html golden, below 1024 px only (app qa.md, Fidelity gate). It throws when the state is not reached.
const fail = (why) => { throw new Error(`fidelity: open-overview.js ${why}`); };
if (navigator.clipboard && typeof Clipboard === "function" && Function.prototype.toString.call(Clipboard.prototype.writeText).includes("[native code]")) {
  fail("found no clipboard stand-in, so it clicks nothing");
}
const press = (selector) => {
  const node = document.querySelector(selector);
  if (!node) fail(`found no ${selector}`);
  node.click(); // detail 0, so neither guard of R13 and R14 holds it
};
press("button.ov-btn");
const overview = document.querySelector("dialog.dlg-ov");
if (!overview?.open) fail("did not open P3");
if (document.querySelectorAll("dialog[open]").length !== 1) fail("left another dialog open with P3");
if (overview.querySelector("div.sheet-body").scrollTop !== 0) fail("left P3 scrolled");
// The golden draws no focus, and focus moved by script without a pointer gesture matches :focus-visible in Chromium.
