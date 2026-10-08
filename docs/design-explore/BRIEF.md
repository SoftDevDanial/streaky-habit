# Design brief: Streaks

**Phase:** design (sdlc:design, step 1 and 2) · **Date:** 2026-10-08 · **Source:** `docs/brainstorm/brainstorm.md`

## Who uses it
One person keeping a few daily habits. They open the app on their phone for a few seconds at a time,
tick today, glance at their streaks and close it. Sometimes they catch up on a day they forgot.

## The one job of the key screen
Show, in one glance, what is done today and how long each run has lasted, and make ticking a day a
single tap.

## Three feeling words
**Steady, calm, rewarding.**

## Hard constraints
- **Platform:** a static web page. Primary viewport is a phone, 390 x 844. It must also work from 360 px
  wide and look deliberate on a 1280 px desktop (a centred column is fine).
- **One theme, light.** No theme switcher (non-goal). The fidelity gate renders in the light scheme.
- **No network dependencies.** No web fonts, no CDN, no images from the internet. The app ships with zero
  dependencies and must work offline, so designs use system font stacks only. Icons are optional. If
  used, they are Phosphor Icons (MIT) SVG paths inlined into the file, never hand-drawn.
- **Accessibility:** WCAG AA text contrast, visible keyboard focus, touch targets at least 44 px (a day
  cell may be 40 px if the row cannot fit 7 x 44 at 360 px, with the gap making up the hit area),
  reduced motion respected. Done and not-done must differ by more than colour alone.
- **Real copy only.** All copy comes from the brainstorm. Sample habits: "Read 20 pages", "Stretch 10
  minutes", "No phone after 11pm". Today in the samples is Thursday 8 October 2026.

## References
The owner gave no references for this app. He dislikes generic AI-made looks (purple gradients, cream
paper with a serif and a terracotta accent, glass cards everywhere). Avoid those defaults.

## Inventory (step 2)
Everything below traces to a brainstorm capability. Nothing outside this list gets designed.

| ID | Screen or state | Traces to | Notes |
|---|---|---|---|
| S1 | **Today screen with three habits (KEY SCREEN)** | C1 C2 C3 C4 C5 | Add field, heatmap, three habits with week strips and streaks. |
| S2 | Today screen, first visit (empty) | C1 C5 C7 | No habits. Says how to start. Heatmap all level 0. |
| S3 | State: name error | C1 | Inline error under the add field (empty, too long, duplicate). |
| S4 | State: 12 habits reached | C1 | Add field and button disabled, with the note. |
| S5 | State: saved habits could not be read | C7 | Dismissible note at the top. |
| M1 | Delete confirmation | C6 | "Delete "Read 20 pages"? Its history is deleted too." |

**Key screen:** S1.

**Inventory confirmation:** confirmed by the orchestrator under the owner's delegation, 2026-10-08 (ORCH).
