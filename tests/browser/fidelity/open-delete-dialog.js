// Candidate after-load script for the plugin fidelity harness (--candidate-after-load). Test-side only, never shipped.
// The harness runs this as the body of an async function. It opens the M1 dialog the way a tap does, checks
// that it really opened, then blurs: the golden draws no focus, and focus moved by script without a pointer
// gesture would draw the Cancel ring (focus on Cancel is proven by the browser tests, not by the pixel diff).
document.querySelector('button[aria-label="Delete Read 20 pages"]').click();
const dialog = document.querySelector("dialog.dialog");
if (!dialog.open || !dialog.matches(":modal")) throw new Error("the delete dialog did not open as a modal");
// The title wraps the name in two invisible isolate marks (spec R13 note, SEC-02): U+2068 before it, U+2069 after.
if (document.querySelector("#del-title").textContent !== 'Delete "\u{2068}Read 20 pages\u{2069}"?') throw new Error("unexpected dialog title");
document.activeElement.blur();
