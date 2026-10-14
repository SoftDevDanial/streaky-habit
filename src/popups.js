/**
 * The popups' own parts (spec R33, R36 to R38, R40, Contracts "Files"): opening a dialog in the top layer, telling its
 * backdrop from its box, P3's grid and legend, P1's head and ticks, P2's head and year, the `is-open` marks and the
 * phone scroll of rule 4.
 * Why: the five dialogs open, focus and close one way, so app.js keeps only which popups are open, for what, and who
 * opened them. Input: dialogs, habits, heatmap cells and date keys, never a clock or storage. Output: changes to the
 * dialogs and their day buttons. It registers no event listener. Data reaches the DOM only through textContent and
 * setAttribute (R24).
 */
import { longDate } from "./dates.js";
import { bestStreak, currentStreak, doneFlags } from "./habits.js";
import { DAY_BUTTON, dayUnit, drawHabitYear, drawLegend, drawOverview, drawRing, element, flagChange, icon, ringSvg } from "./calendar.js";
import { renderStats } from "./view.js";

/** Below 768 px P1 is a bottom sheet over its host (system.css breakpoint), where rule 4 applies. */
const PHONE_SHEET = "(max-width: 767px)";

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

/**
 * P2 for `habit` (R33, R34), its name, its Current and Best for today in a row's stats markup (R6), and its year of
 * beads. Drawn as P2 opens (`animate` false) and after every edit while it is open, where what changed pops or bumps.
 */
export function renderHabitYear(habit, todayKey, animate) {
  const { habitYear } = dialogs();
  habitYear.querySelector("#yr-title").textContent = habit.name;
  renderStats(habitYear.querySelector("p.yr-stats"), currentStreak(habit.done, todayKey), bestStreak(habit.done), animate);
  drawHabitYear(habitYear.querySelector("div.months"), habit.done, todayKey, animate);
}

/** P3's weeks, newest first, and its legend (R38), drawn the way the band draws them. */
export function renderOverviewPopup(cells, todayKey, habitCount, animate) {
  const { overview } = dialogs();
  drawOverview(overview.querySelector("div.ovg-rows"), cells, todayKey, { newestFirst: true, animate });
  drawLegend(overview.querySelector("div.sheet-body > div.legend"), habitCount);
}

/**
 * P1's list for `habits`, one tick per habit in list order, or the "No habits yet." line (CG-12). Built as P1 opens,
 * because no habit can be added or deleted while it is open. `renderDayEditor` fills the ticks.
 */
export function buildDayList(habits) {
  const items = habits.length === 0 ? [element("li", "day-empty", {}, "No habits yet.")] : habits.map((habit, index) => createTick(habit.name, index + 1));
  dialogs().day.querySelector("ul.day-list").replaceChildren(...items);
}

/** The tick markup of the spec's Contracts. Position N gives the stats id ts-N. */
function createTick(name, position) {
  const box = element("span", "tbox");
  box.append(icon("i-check"));
  const button = element("button", "tick", { type: "button", "aria-label": name, "aria-describedby": `ts-${position}` });
  button.append(box, element("span", "tname", {}, name), element("span", "tstat", { id: `ts-${position}` }));
  const item = element("li");
  item.append(button);
  return item;
}

/**
 * P1 for `dayKey` (R36, R37): the mini ring, the long date, "<count> of <total> habits" and each tick's state and
 * numbers. The ticks are updated in place, so a ticked button stays the same element with its focus, and only what
 * changed pops when `animate` is set (R32).
 */
export function renderDayEditor(dayKey, habits, todayKey, animate) {
  const { day } = dialogs();
  const flags = doneFlags(habits, dayKey);
  const mini = day.querySelector("div.day-mini");
  if (!mini.firstElementChild) mini.append(ringSvg());
  const ringChanged = drawRing(mini.firstElementChild, flags);
  flagChange(mini, "pop", animate && ringChanged);
  day.querySelector("#day-title").textContent = longDate(dayKey);
  day.querySelector("#day-sub").textContent = `${flags.filter(Boolean).length} of ${flags.length} habits`;
  day.querySelectorAll("ul.day-list button.tick").forEach((button, index) => {
    const before = button.getAttribute("aria-pressed");
    const pressed = String(flags[index]);
    button.setAttribute("aria-pressed", pressed);
    button.classList.toggle("on", flags[index]);
    flagChange(button, "pop", animate && before !== null && before !== pressed);
    const { done } = habits[index];
    renderTickStats(button.querySelector(":scope > span.tstat"), currentStreak(done, todayKey), bestStreak(done));
  });
}

/** A tick's numbers are the habit's for today, not as of the chosen day (day-editor.md). No Best when it is 0. */
function renderTickStats(stat, current, best) {
  const parts = [current > 0 ? element("span", "tcur", {}, `Current ${current} ${dayUnit(current)}`) : element("span", "tcur none", {}, "No streak yet")];
  if (best > 0) parts.push(element("span", "", {}, `Best ${best}`));
  stat.replaceChildren(...parts);
}

/** P1's first focus (rule 1): the first tick, or Close when there is no habit (CG-12). */
export function dayEditorFocus() {
  const { day } = dialogs();
  return day.querySelector("ul.day-list button.tick") ?? closeButtonOf(day);
}

/** The position of the habit whose tick holds `target`, or -1. A tick's habit is its place in P1's list. */
export function tickIndexOf(target) {
  const button = target.closest("button.tick");
  return button ? Array.from(dialogs().day.querySelectorAll("ul.day-list button.tick")).indexOf(button) : -1;
}

/** Every day button for `dayKey` in the band, P3 and P4 shows that P1 is open for it (R36). Null clears them all. */
export function markOpenDay(dayKey) {
  for (const button of document.querySelectorAll(DAY_BUTTON)) button.classList.toggle("is-open", button.getAttribute("data-key") === dayKey);
}

/**
 * Rule 4: on a phone P1 is a bottom sheet over P3 or P4, so the host's body scrolls until the chosen day lies between
 * the host's head and P1's top edge. Run after P1 is shown, so its height is known.
 */
export function keepDayInSight(dayButton) {
  const host = dayButton.closest("dialog");
  if (!host || !window.matchMedia(PHONE_SHEET).matches) return;
  const body = host.querySelector(".sheet-body");
  const headBottom = host.querySelector(".sheet-head").getBoundingClientRect().bottom;
  // The dialog element, not its box: the box is still sliding up (the `sheet` animation), the dialog is where it rests.
  const sheetTop = dialogs().day.getBoundingClientRect().top;
  const { top, bottom } = dayButton.getBoundingClientRect();
  if (bottom > sheetTop) body.scrollTop += Math.ceil(bottom - sheetTop);
  else if (top < headBottom) body.scrollTop -= Math.ceil(headBottom - top);
}
