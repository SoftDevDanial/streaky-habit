/**
 * The popups' own parts (spec R38, R40, Contracts "Files"): opening a dialog in the top layer, telling its backdrop
 * from its box, and P3's grid and legend.
 * Why: the five dialogs open, focus and close one way, so app.js keeps only which popups are open and who opened
 * them. Input: dialogs, heatmap cells and `todayKey`, never a clock or storage. Output: changes to the dialogs.
 * It registers no event listener.
 */
import { drawLegend, drawOverview } from "./calendar.js";

const $ = (selector) => document.querySelector(selector);

/** The five dialogs of the skeleton (R1), by what each shows. Their selectors live here only. */
export const dialogs = () => ({
  overview: $("dialog.dlg-ov"),
  allHabits: $("dialog.dlg-all"),
  habitYear: $("dialog.dlg-year"),
  day: $("dialog.dlg-day"),
  remove: $("dialog.dlg-del"),
});

/** Each popup but M1 has one Close, the only `icon-btn` inside it. */
export const closeButtonOf = (dialog) => dialog.querySelector("button.icon-btn");

/**
 * Opens `dialog` with showModal (R40), so it stacks over what is open and everything under it is inert, with its
 * body at the top and focus on `focusTarget` (rule 1). Focus is set by hand because the native choice differs.
 */
export function showPopup(dialog, focusTarget) {
  dialog.showModal();
  const body = dialog.querySelector(".sheet-body");
  if (body) body.scrollTop = 0;
  focusTarget.focus();
}

/**
 * True when a pointer event on `dialog` lies on its backdrop. A press on ::backdrop is dispatched to the dialog
 * element itself, so the point must also lie outside the dialog's box (`div.dlg-box`).
 */
export function onBackdrop(dialog, event) {
  if (event.target !== dialog) return false;
  const box = dialog.querySelector(":scope > .dlg-box").getBoundingClientRect();
  return event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom;
}

/** P3's weeks, newest first, and its legend (R38), drawn the way the band draws them. */
export function renderOverviewPopup(cells, todayKey, habitCount, animate) {
  const { overview } = dialogs();
  drawOverview(overview.querySelector("div.ovg-rows"), cells, todayKey, { newestFirst: true, animate });
  drawLegend(overview.querySelector("div.sheet-body > div.legend"), habitCount);
}
