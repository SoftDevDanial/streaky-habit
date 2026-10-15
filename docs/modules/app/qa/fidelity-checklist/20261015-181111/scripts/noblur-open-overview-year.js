// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs it as the body of an async function after load. It opens P4, the state of the overview-year.html
// golden, from the band's Year from 1024 px and from P3's Year below (app qa.md, Fidelity gate). It throws when the
// state is not reached.
const fail = (why) => { throw new Error(`fidelity: open-overview-year.js ${why}`); };
if (navigator.clipboard && typeof Clipboard === "function" && Function.prototype.toString.call(Clipboard.prototype.writeText).includes("[native code]")) {
  fail("found no clipboard stand-in, so it clicks nothing");
}
const press = (selector) => {
  const node = document.querySelector(selector);
  if (!node) fail(`found no ${selector}`);
  node.click(); // detail 0, so neither guard of R13 and R14 holds it
};
const wide = matchMedia("(min-width: 1024px)").matches;
if (wide) {
  press("section.band button.btn-all");
} else {
  press("button.ov-btn");
  if (!document.querySelector("dialog.dlg-ov")?.open) fail("did not open P3");
  press("dialog.dlg-ov button.btn-all");
}
const all = document.querySelector("dialog.dlg-all");
if (!all?.open) fail("did not open P4");
if (wide && document.querySelectorAll("dialog[open]").length !== 1) fail("left another dialog open with P4");
if (!wide && document.querySelectorAll("dialog[open]").length !== 2) fail("left a dialog other than P3 and P4 open");
if (all.querySelector("div.sheet-body").scrollTop !== 0) fail("left P4 scrolled");
// The golden draws no focus, and focus moved by script without a pointer gesture matches :focus-visible in Chromium.
