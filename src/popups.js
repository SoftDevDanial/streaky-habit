/**
 * The popups' own parts (spec R13, R33, R36 to R40, Contracts "Files"), which are opening a dialog in the top layer,
 * telling its backdrop from its box, P3's grid and legend, P4's months and legend, P1's head and ticks, P2's head and
 * year, M1's title, the `is-open` marks, and the phone scroll of rule 4 with the room it gives P1's host.
 * Why: the five dialogs open, focus and close one way, so app.js keeps only which popups are open, for what, and who
 * opened them. Input: dialogs, habits, heatmap cells and date keys, never a clock or storage. Output: changes to the
 * dialogs and their day buttons. It registers no event listener. Data reaches the DOM only through textContent and
 * setAttribute (R24).
 */
import { longDate } from "./dates.js";
import { bestStreak, currentStreak, doneFlags } from "./habits.js";
import {
  DAY_BUTTON,
  dayUnit,
  drawAllHabitsYear,
  drawHabitYear,
  drawLegend,
  drawOverview,
  drawRing,
  element,
  flagChange,
  icon,
  ringSvg,
} from "./calendar.js";
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

/**
 * The one control that closes `dialog` and returns focus to its opener, which is Close (the only `icon-btn` inside
 * it), or Cancel in M1, which has no Close (R13, R14). It also takes focus as P2, P3, P4 and M1 open (rule 1).
 */
export const closeButtonOf = (dialog) => dialog.querySelector("button.icon-btn, div.dlg-actions > button.btn-secondary");

/** M1's Delete habit that holds `target`, or null. */
export const confirmDeleteOf = (target) => target.closest("dialog.dlg-del button.btn-danger");

/** P2's Delete habit that holds `target`, or null. */
export const yearDeleteOf = (target) => target.closest("dialog.dlg-year button.btn-del");

/**
 * What M1's title leaves out of its copy of the name, written as escapes so that this file holds no invisible
 * character. U+202A to U+202E (embeddings and overrides, and their end), U+2066 to U+2069 (isolates, and their end)
 * and the paragraph separators U+0085, U+001C to U+001E and U+2029 (SEC-06). The isolate round the name only holds
 * while the name can neither close it nor leave one open. A U+2069 or a separator inside the name closes the title's
 * isolate early, and an isolate opener with no closer takes the title's U+2069, so after a right-to-left letter the
 * closing quote and the question mark were drawn on the wrong side of the name.
 */
const TITLE_STRIPPED = /[\u{202A}-\u{202E}\u{2066}-\u{2069}\u{0085}\u{001C}-\u{001E}\u{2029}]/gu;

/**
 * M1's title for the habit `name` (R13). The name sits between U+2068 and U+2069, two invisible characters, so a
 * bidirectional override in it cannot reorder the quotes and the question mark that follow it (SEC-02), and the
 * title's copy has `TITLE_STRIPPED` taken out first. The stored name and every other place keep the name as typed.
 */
export function renderDeleteTitle(name) {
  dialogs().remove.querySelector("#del-title").textContent = `Delete "\u{2068}${name.replace(TITLE_STRIPPED, "")}\u{2069}"?`;
}

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

/** P4's months, newest first, and its legend (R39), drawn as P4 opens and after every edit while it is open (R32). */
export function renderAllHabitsYear(habits, todayKey, animate) {
  const { allHabits } = dialogs();
  drawAllHabitsYear(allHabits.querySelector("div.months"), habits, todayKey, animate);
  drawLegend(allHabits.querySelector("div.yr-tools > div.legend"), habits.length);
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

/**
 * The control that takes focus as `dialog` opens (rule 1). In P1 the first tick, or Close when it lists no habit
 * (CG-12). In the others Close, or Cancel in M1. Focus whose day a rollover took away goes here too (CG-14).
 */
export function openFocusOf(dialog) {
  return dialog.querySelector("ul.day-list button.tick") ?? closeButtonOf(dialog);
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
 * Rule 4 (R36, owner ruling H-03): on a phone P1 is a bottom sheet over its host, P3 or P4. The host's body gets room
 * below its last day as tall as P1, so any day can scroll above P1, and then scrolls until the chosen day lies between
 * the host's head and P1's top edge. When that gap is smaller than a day, the day's top meets the head instead, so it
 * shows as far as the gap allows. Run after P1 is shown, so its height is known. `clearDayRoom` undoes the room.
 */
export function keepDayInSight(dayButton) {
  const host = dayButton.closest("dialog");
  if (!host || !window.matchMedia(PHONE_SHEET).matches) return;
  const body = host.querySelector(".sheet-body");
  // The dialog element, not its box: the box is still sliding up (the `sheet` animation), the dialog is where it rests.
  const sheetTop = dialogs().day.getBoundingClientRect().top;
  // Inline, not a style rule, because P1's height depends on how many habits it lists and how long their names are.
  body.style.paddingBottom = `${Math.ceil(window.innerHeight - sheetTop)}px`;
  const headBottom = host.querySelector(".sheet-head").getBoundingClientRect().bottom;
  const { top, bottom } = dayButton.getBoundingClientRect();
  if (bottom - top > sheetTop - headBottom) body.scrollTop += top - headBottom;
  else if (bottom > sheetTop) body.scrollTop += Math.ceil(bottom - sheetTop);
  else if (top < headBottom) body.scrollTop -= Math.ceil(headBottom - top);
}

/**
 * P1 has closed, so its host loses the room `keepDayInSight` gave it (R36). The browser clamps the host's scroll to
 * the smaller range, and the focus going back to the day brings it into view where needed.
 */
export function clearDayRoom() {
  const { overview, allHabits } = dialogs();
  for (const body of [overview, allHabits].map((host) => host.querySelector(".sheet-body"))) {
    body.style.removeProperty("padding-bottom");
    // An emptied style attribute goes too, so the body's markup is the golden's again.
    if (!body.getAttribute("style")) body.removeAttribute("style");
  }
}
