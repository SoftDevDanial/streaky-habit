# Bugs found and left for a later version

Bugs that testing found after the build, that were written up instead of fixed before the seal, with why.

## The All habits window shows two months per row on a Windows desktop (v1.1.0, H-09)

**Found.** 2026-10-16, by the owner at the v1.1.0 user acceptance test. He crossed one expected line in UAT-01,
"The top row holds three months, October 2026 first", and still passed the case.
**Ledger.** v1.1.0, Needs the human H-09, findings U1 of the 2026-10-16 user test.

**What happens.** The All habits window is a 980 px dialog designed to show three months across. Three months need
922 px. With no scrollbar the dialog leaves 930 px, so three fit. Chrome on Windows draws a scrollbar inside the
window, about 10 px in the test browser, which leaves 920 px, so the grid falls to two months per row with wide
margins on both sides. Every window width from 1024 to 1920 px gives the same result. The single-habit Year window
keeps three fixed columns and is not affected.

**Why the automated checks missed it.** The pixel match against the design and the pre-run of the test script both
ran in headless Chromium, which hides scrollbars by default. The design file itself has the same 2 px shortfall, so a
pixel match could not have caught it either. A person on a Windows desktop did.

**Why it was not fixed before the seal.** The owner chose to wrap the version up. A proper fix has to work at any
scrollbar width, since Windows can draw a wider one than the test browser did, so it is a small design decision and
not only a number. It changes the approved design file, which only the design phase may do.

**The fix, next version.** Correct the design so three months fit with a scrollbar drawn (for example a narrower month
gap, a wider dialog, or room kept for the scrollbar), then run the pixel match and the browser tests with scrollbars
drawn.
