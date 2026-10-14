/**
 * K1, the main screen. The header date, the Overview button, the band, the banners (the save warning and the note
 * after a reset), the rows and their numbers, the list frame's fades and scroll, the composer's states, its name
 * errors and its 12-habit state, and focus after a delete (spec R3 to R6, R10 to R12, R15, R17, R35, R38, R41).
 * Why: one module owns K1's markup and selectors, so app.js never builds or looks up an element of K1 itself.
 * Input: habits, heatmap cells and `todayKey` (never a clock), and `animate`, true when a render answers an edit
 * (R32). Output: changes to the page. Data reaches the DOM only through textContent and setAttribute (R24).
 * It stores nothing and registers no event listener.
 */
import { longDate } from "./dates.js";
import { bestStreak, currentStreak } from "./habits.js";
import { dayUnit, drawLegend, drawOverview, drawRing, element, flagChange, icon, ringSvg, svgElement } from "./calendar.js";

const LIMIT_NOTE = "You track 12 habits, the most this app holds. Delete one to add another.";
const SAVE_WARNING = "Your habits are not being saved on this device. Changes will be lost when you close this tab.";
const RESET_NOTE = "Your saved habits could not be read, so the list was reset.";
/** The message of each name error `addHabit` gives (R11). */
const NAME_ERRORS = {
  empty: "Name the habit first.",
  "too-long": "Keep it to 40 characters or fewer.",
  duplicate: "You already track this habit.",
};

const $ = (selector) => document.querySelector(selector);
const rowsOf = () => Array.from(document.querySelectorAll("ul.rows > li.row"));

export function renderDate(todayKey) {
  const date = $("header.top > time.date");
  date.setAttribute("datetime", todayKey);
  date.textContent = longDate(todayKey);
}

/** Today's ring and count on the Overview button (R38), which pops its ring when an edit changes today. */
export function renderOverviewButton(todayFlags, animate) {
  const button = $("button.ov-btn");
  const done = todayFlags.filter(Boolean).length;
  button.setAttribute("aria-label", `Overview, today ${done} of ${todayFlags.length} habits done`);
  const holder = button.querySelector(":scope > span.ov-ring");
  if (!holder.firstElementChild) holder.append(ringSvg());
  const changed = drawRing(holder.firstElementChild, todayFlags);
  flagChange(holder, "pop", animate && changed);
}

export function renderBand(cells, todayKey, habitCount, animate) {
  drawOverview($("section.band div.ovg-cols"), cells, todayKey, { newestFirst: false, animate });
  drawLegend($("section.band div.legend"), habitCount);
}

/**
 * One row per habit, or the empty list (R3, R5). The rows are built again only when the habits themselves change
 * (an add or a delete). Otherwise each row is updated in place, so a pressed Done today stays the same element
 * with its focus (R31) and only what changed animates (R32).
 */
export function renderRows(habits, todayKey, animate) {
  const list = $("ul.rows");
  if (habits.length === 0) {
    if (!list.querySelector(":scope > li.empty")) list.replaceChildren(emptyList());
    return;
  }
  const shown = rowsOf().map((row) => row.querySelector(":scope > div.r-head > h3").textContent);
  const same = shown.length === habits.length && habits.every((habit, index) => habit.name === shown[index]);
  if (!same) list.replaceChildren(...habits.map((habit, index) => createRow(habit.name, index + 1)));
  rowsOf().forEach((row, index) => syncRow(row, habits[index].done, todayKey, animate));
}

function emptyList() {
  const art = svgElement("svg", { viewBox: "0 0 120 120", "aria-hidden": "true" });
  art.append(
    svgElement("circle", { class: "e-orbit", cx: "60", cy: "60", r: "50" }),
    svgElement("circle", { class: "e-core", cx: "60", cy: "60", r: "18" }),
  );
  const words = element("div");
  words.append(element("p", "lead", {}, "No habits yet."), element("p", "line", {}, "Add one you want to do every day."));
  const empty = element("li", "empty");
  empty.append(art, words);
  return empty;
}

/** The habit-row markup of the spec's Contracts. Position N gives the ids rn-N and rs-N. */
function createRow(name, position) {
  const bin = element("button", "btn-bin", { type: "button", "aria-haspopup": "dialog", "aria-label": `Delete "${name}"` });
  bin.append(icon("i-trash", "ph"));
  const head = element("div", "r-head");
  head.append(element("h3", "r-name", { id: `rn-${position}` }, name), bin);
  const year = element("button", "btn-year", { type: "button", "aria-haspopup": "dialog", "aria-label": `Year view, ${name}` }, "Year");
  const dot = element("span", "dot");
  dot.append(icon("i-check"));
  const done = element("button", "btn-done", { type: "button", "aria-label": `Done today, ${name}`, "aria-describedby": `rs-${position}` });
  done.append(dot, "Done today");
  const row = element("li", "row");
  row.append(head, element("p", "stats", { id: `rs-${position}` }), year, done);
  return row;
}

function syncRow(row, done, todayKey, animate) {
  renderStats(row.querySelector(":scope > p.stats"), currentStreak(done, todayKey), bestStreak(done), animate);
  const button = row.querySelector(":scope > button.btn-done");
  const before = button.getAttribute("aria-pressed");
  const pressed = String(done.includes(todayKey));
  button.setAttribute("aria-pressed", pressed);
  flagChange(button, "pop", animate && before !== null && before !== pressed);
}

/**
 * Current and Best (R6) into a row's `p.stats` (and P2's `p.yr-stats`). A value whose text changed is replaced by
 * a new element, which carries `bump` when `animate` is set, so the rise plays (R32) and plays again on the next
 * change because the element is new. An unchanged value keeps its element and loses `bump`. Filling an empty
 * `stats` animates nothing. When Best is 0 its block is not drawn.
 */
export function renderStats(stats, current, best, animate) {
  const bump = animate && stats.firstElementChild !== null;
  const currentStat = stats.querySelector(":scope > .stat.cur") ?? stats.appendChild(statBlock("cur", "Current"));
  const currentValue = current > 0 ? valueOf(current, dayUnit(current)) : element("span", "none", {}, "No streak yet");
  setValue(currentStat, currentValue, bump);
  const bestStat = stats.querySelector(":scope > .stat.best");
  if (best === 0) {
    bestStat?.remove();
    return;
  }
  setValue(bestStat ?? stats.appendChild(statBlock("best", "Best")), valueOf(best), bump);
}

function statBlock(kind, label) {
  const stat = element("span", `stat ${kind}`);
  stat.append(element("span", "lbl", {}, label));
  return stat;
}

function valueOf(number, unit = "") {
  const value = element("span", "val");
  value.append(element("b", "num", {}, String(number)));
  if (unit) value.append(element("span", "unit", {}, unit));
  return value;
}

/** Puts `next` after the stat's label unless the value shown there already reads the same. */
function setValue(stat, next, bump) {
  const shown = stat.children[1];
  if (shown && shown.classList.contains(next.className) && shown.textContent === next.textContent) {
    shown.classList.remove("bump");
    return;
  }
  if (bump) next.classList.add("bump");
  if (shown) shown.replaceWith(next);
  else stat.append(next);
}

/**
 * At 12 habits the composer closes and says why (R12), and below 12 it opens again. It writes only when the state
 * changes, so the note is not written again into the live region `#nh-msg` by every render. Below 12 a name error
 * is left as it is.
 */
export function renderComposerLimit(full) {
  const form = $("form.composer");
  if (form.classList.contains("is-full") === full) return;
  form.classList.toggle("is-full", full);
  const field = $("#nh");
  field.disabled = full;
  $("#add-btn").disabled = full;
  if (full) {
    field.removeAttribute("aria-invalid");
    setMessage("field-msg note", LIMIT_NOTE);
  } else {
    setMessage("field-msg", "");
  }
}

/** The text in the field exactly as typed. `addHabit` trims it, and a rejected name leaves it as it is (R11). */
export const composerText = () => $("#nh").value;

/**
 * A rejected name (R11) shows its one message above the field, marks the field invalid and puts focus on it. The
 * app sets that focus because a click on Add leaves focus on no element in WebKit (spec Invariants, engine note).
 */
export function showNameError(error) {
  setMessage("field-msg err", NAME_ERRORS[error]);
  const field = $("#nh");
  field.setAttribute("aria-invalid", "true");
  field.focus();
}

/** Typing clears a name error at once (R11, rule 7). The 12-habit note is no error and stays. */
export function clearNameError() {
  if (!$("#nh-msg").classList.contains("err")) return;
  setMessage("field-msg", "");
  $("#nh").removeAttribute("aria-invalid");
}

/** After an add the field empties and any name error clears (R10). */
export function emptyComposer() {
  $("#nh").value = "";
  clearNameError();
}

/** The line above the field (spec Contracts, Message line), shown exactly when it holds a text. */
function setMessage(className, text) {
  const message = $("#nh-msg");
  message.className = className;
  message.textContent = text;
  message.hidden = text === "";
}

/** The fades show which edges of the list frame have more rows behind them (R5). */
export function renderFrameFades() {
  const frame = $("div.frame");
  const wrap = frame.parentElement;
  wrap.classList.toggle("more-above", frame.scrollTop > 0);
  wrap.classList.toggle("more-below", frame.scrollTop + frame.clientHeight < frame.scrollHeight);
}

/**
 * After an add the frame scrolls to its end, so the new last row lies fully in its visible part (R10, CG-15, as F2
 * does). The fades follow at once, because the frame's `scroll` event comes only after this handler (R5).
 */
export function showLastRow() {
  const frame = $("div.frame");
  frame.scrollTop = frame.scrollHeight;
  renderFrameFades();
}

/**
 * The save warning (R41) shows while the latest save failed, as the first banner. It is inserted only when saving
 * turns to failing and removed only when it turns to working, so the live region is left alone while saves keep
 * failing (SW7).
 */
export function renderSaveWarning(failing) {
  const banners = $("div.banners");
  const warning = banners.querySelector(":scope > div.banner.warn");
  if (failing === (warning !== null)) return;
  if (failing) banners.prepend(banner("warn", SAVE_WARNING));
  else warning.remove();
}

/** The note after unreadable saved data was reset (R17), drawn once at boot, below the warning when both show. */
export function showResetNote() {
  const dismiss = element("button", "icon-btn", { type: "button", "aria-label": "Dismiss note" });
  dismiss.append(icon("i-x", "ph"));
  const note = banner("note", RESET_NOTE);
  note.append(dismiss);
  $("div.banners").append(note);
}

/** A banner of the spec's Contracts, `div.banner.<kind>` with the role status, holding `text` in a `p`. */
function banner(kind, text) {
  const node = element("div", `banner ${kind}`, { role: "status" });
  node.append(element("p", "", {}, text));
  return node;
}

/** The note's Dismiss that holds `target`, or null. */
export const dismissOf = (target) => target.closest("div.banner.note > button.icon-btn");

/**
 * Dismiss removes the note, changes nothing else, and puts focus on the field (R17, rule 7). The app sets that focus
 * because a click leaves focus on no element in WebKit (spec Invariants, engine note).
 */
export function dismissNote() {
  $("div.banners > div.banner.note").remove();
  $("#nh").focus();
}

/** The elements app.js listens on. Their selectors live here only. */
export const containers = () => ({ page: $("div.app"), frame: $("div.frame"), composer: $("form.composer"), field: $("#nh") });

/**
 * The position of the habit whose row holds `control`. Rows carry no index attribute (spec Events and focus), so a
 * row's habit is its place in the list.
 */
export const habitIndexOf = (control) => rowsOf().indexOf(control.closest("li.row"));

/** The position of the habit whose Done today holds `target`, or -1. */
export function doneTodayIndexOf(target) {
  const button = target.closest("button.btn-done");
  return button ? habitIndexOf(button) : -1;
}

/** A row's bin that holds `target`, or null. */
export const binOf = (target) => target.closest("button.btn-bin");

/**
 * Rule 3 (R15, CG-18). After a delete, focus goes to the bin of the row now at the deleted `position`, or to its Year
 * when the delete came from P2 (`fromYear`), else to that control of the row above, else to the field. When that row
 * lies outside the frame's visible part the frame scrolls it into view, as F2 does, and the fades follow at once,
 * because the frame's `scroll` event comes only after this handler (R5).
 */
export function focusAfterDelete(position, fromYear) {
  const rows = rowsOf();
  const row = rows[position] ?? rows[position - 1];
  if (!row) {
    $("#nh").focus();
    return;
  }
  row.querySelector(fromYear ? ":scope > button.btn-year" : ":scope > div.r-head > button.btn-bin").focus({ preventScroll: true });
  row.scrollIntoView({ block: "nearest" });
  renderFrameFades();
}

export const overviewButtonOf = (target) => target.closest("button.ov-btn");

/** The Year named "Year view, all habits" that holds `target`, or null. It is the same control in the band and in P3. */
export const allHabitsButtonOf = (target) => target.closest("button.btn-all");

/** A row's Year that holds `target`, or null. */
export const yearButtonOf = (target) => target.closest("button.btn-year");
