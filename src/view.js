/**
 * K1, the main screen: the header date, the Overview button, the band, the rows and their numbers, the list
 * frame's fades and the composer's 12-habit state (spec R3 to R6, R12, R35, R38).
 * Why: one module owns K1's markup and selectors, so app.js never builds or looks up an element of K1 itself.
 * Input: habits, heatmap cells and `todayKey` (never a clock), and `animate`, true when a render answers an edit
 * (R32). Output: changes to the page. Data reaches the DOM only through textContent and setAttribute (R24).
 * It stores nothing and registers no event listener.
 */
import { longDate } from "./dates.js";
import { bestStreak, currentStreak } from "./habits.js";
import { dayUnit, drawLegend, drawOverview, drawRing, element, flagChange, icon, ringSvg, svgElement } from "./calendar.js";

const LIMIT_NOTE = "You track 12 habits, the most this app holds. Delete one to add another.";

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
 * At 12 habits the composer closes and says why (R12). Below 12 that state is undone, and a message that is not
 * the 12-habit note (a name error) is left as it is.
 */
export function renderComposerLimit(full) {
  const form = $("form.composer");
  const field = $("#nh");
  const message = $("#nh-msg");
  if (full) {
    form.classList.add("is-full");
    field.removeAttribute("aria-invalid");
    message.className = "field-msg note";
    message.textContent = LIMIT_NOTE;
    message.hidden = false;
  } else if (form.classList.contains("is-full")) {
    form.classList.remove("is-full");
    message.className = "field-msg";
    message.textContent = "";
    message.hidden = true;
  }
  field.disabled = full;
  $("#add-btn").disabled = full;
}

/** The fades show which edges of the list frame have more rows behind them (R5). */
export function renderFrameFades() {
  const frame = $("div.frame");
  const wrap = frame.parentElement;
  wrap.classList.toggle("more-above", frame.scrollTop > 0);
  wrap.classList.toggle("more-below", frame.scrollTop + frame.clientHeight < frame.scrollHeight);
}

/** The elements app.js listens on. Their selectors live here only. */
export const containers = () => ({ page: $("div.app"), frame: $("div.frame") });

/**
 * The position of the habit whose Done today holds `target`, or -1. Rows carry no index attribute (spec Events and
 * focus), so a row's habit is its place in the list.
 */
export function doneTodayIndexOf(target) {
  const button = target.closest("button.btn-done");
  return button ? rowsOf().indexOf(button.closest("li.row")) : -1;
}

export const overviewButtonOf = (target) => target.closest("button.ov-btn");
