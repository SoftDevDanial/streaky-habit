// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs it as the body of an async function after load. It opens P1 for Tuesday 22 September the way the
// day-editor.html golden reaches it, from P3 below 1024 px and from the band from 1024 px (app qa.md, Fidelity gate).
// It throws when the state is not reached, so a broken script fails its capture instead of rendering a wrong state.
const fail = (why) => { throw new Error(`fidelity: open-day-editor.js ${why}`); };
if (navigator.clipboard && typeof Clipboard === "function" && Function.prototype.toString.call(Clipboard.prototype.writeText).includes("[native code]")) {
  fail("found no clipboard stand-in, so it clicks nothing");
}
const press = (selector) => {
  const node = document.querySelector(selector);
  if (!node) fail(`found no ${selector}`);
  node.click(); // detail 0, so neither guard of R13 and R14 holds it
};
const isOpen = (selector) => Boolean(document.querySelector(selector)?.open);
const wide = matchMedia("(min-width: 1024px)").matches;
if (wide) {
  press('section.band div.ovg-cols button.hc[data-key="2026-09-22"]');
} else {
  press("button.ov-btn");
  if (!isOpen("dialog.dlg-ov")) fail("did not open P3");
  press('dialog.dlg-ov div.ovg-rows button.hc[data-key="2026-09-22"]');
}
if (!isOpen("dialog.dlg-day")) fail("did not open P1");
if (document.querySelector("#day-title").textContent !== "Tuesday 22 September") fail("opened P1 for another day");
const host = wide ? "section.band div.ovg-cols" : "dialog.dlg-ov div.ovg-rows";
const marked = Array.from(document.querySelectorAll(`${host} button.hc.is-open`), (node) => node.dataset.key);
if (marked.join() !== "2026-09-22") fail(`found ${marked.join() || "no day"} marked open in ${host}`);
if (wide) {
  if (document.querySelectorAll("dialog[open]").length !== 1) fail("left another dialog open under P1");
} else {
  if (document.querySelectorAll("dialog[open]").length !== 2) fail("left a dialog other than P3 and P1 open");
  if (document.querySelector("dialog.dlg-ov div.sheet-body").scrollTop !== 0) fail("left P3 scrolled");
}
// The golden draws no focus, and focus moved by script without a pointer gesture matches :focus-visible in Chromium.
