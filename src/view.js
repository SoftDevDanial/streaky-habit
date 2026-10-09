/**
 * Everything the user sees: builds the page's DOM from the habits and the shown day, and updates it.
 * Why: one module owns the markup of the golden designs, so app.js never builds or styles an element.
 * Input: habits and `todayKey` (never read from a clock here). Output: changes to the page.
 * Data reaches the DOM only through textContent and setAttribute, never as markup (spec R24).
 * It stores nothing and registers no event listener.
 */
import { dayParts, longDate, shortDate } from "./dates.js";
import { bestStreak, currentStreak, heatmapCells, monthLabels, runContinues, weekWindow } from "./habits.js";

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

const NAME_ERRORS = {
  empty: "Name the habit first.",
  "too-long": "Keep it to 40 characters or fewer.",
  duplicate: "You already track this habit.",
};
const LIMIT_NOTE = "You track 12 habits, the most this app holds. Delete one to add another.";
const RESET_NOTE = "Your saved habits could not be read, so the list was reset.";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function element(tag, className, attributes = {}) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  return node;
}

/**
 * Created with createElementNS: an svg made by createElement is an HTML element and does not render.
 * @param {string} symbolId a symbol of the sprite in index.html
 */
function icon(symbolId) {
  const svg = document.createElementNS(SVG_NAMESPACE, "svg");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  const use = document.createElementNS(SVG_NAMESPACE, "use");
  use.setAttribute("href", `#${symbolId}`);
  svg.append(use);
  return svg;
}

/**
 * Only writes a changed text. Replacing a text node with an identical one still makes screen readers
 * repeat the whole live region, so a tick must not touch the lines that did not change.
 */
function setText(node, text) {
  if (node.textContent !== text) node.textContent = text;
}

// ---------------------------------------------------------------------------------------------
// Header, list and rows

export function renderHeader(todayKey) {
  const time = $(".date time");
  time.setAttribute("datetime", todayKey);
  setText(time, longDate(todayKey));
}

function createDayButton() {
  const label = element("span", "day-label", { "aria-hidden": "true" });
  label.append(element("span", "wd"), element("span", "dm"));
  const bead = element("span", "bead");
  bead.append(icon("i-check"));
  const slot = element("span", "slot", { "aria-hidden": "true" });
  slot.append(bead);
  const button = element("button", "day", { type: "button" });
  button.append(label, slot);
  return button;
}

/** The row for one habit; its name, streak line and beads are filled by `fillRow` and `syncProgress`. */
function createRow(position, todayKey) {
  const nameId = `h${position + 1}-name`;
  const head = element("div", "habit-head");
  const deleteButton = element("button", "icon-btn", { type: "button" });
  deleteButton.append(icon("i-trash"));
  head.append(element("h3", "habit-name", { id: nameId }), deleteButton);
  const streak = element("p", "streak", { "aria-live": "polite" });
  streak.append(element("span", "cur"));
  const strip = element("div", "strip", { role: "group", "aria-labelledby": nameId });
  strip.append(...weekWindow(todayKey).map(createDayButton));
  const row = element("li", "habit");
  row.append(head, streak, strip);
  return row;
}

function fillRow(row, habit) {
  row.querySelector(".habit-name").textContent = habit.name;
  row.querySelector(".icon-btn").setAttribute("aria-label", `Delete ${habit.name}`);
}

function streakLabel(current) {
  if (current === 0) return "No streak yet";
  return current === 1 ? "1 day" : `${current} days`;
}

function syncStreak(streak, done, todayKey) {
  const current = currentStreak(done, todayKey);
  const best = bestStreak(done);
  const currentNode = streak.querySelector(".cur");
  currentNode.className = current === 0 ? "cur none" : "cur";
  setText(currentNode, streakLabel(current));
  let bestNode = streak.querySelector(".best");
  if (best === 0) {
    bestNode?.remove();
    return;
  }
  if (!bestNode) {
    bestNode = element("span", "best");
    streak.append(bestNode);
  }
  setText(bestNode, `Best ${best}`);
}

/**
 * Sets the button for `key` in place, so the same element (and its focus and transitions) lives on
 * when a tick or a new day changes what it shows.
 */
function syncDay(button, key, isDone, isToday) {
  const { weekday, day } = dayParts(key);
  button.setAttribute("data-date", key);
  button.setAttribute("aria-pressed", String(isDone));
  button.setAttribute("aria-label", `Mark ${shortDate(key)} as done`);
  if (isToday) button.setAttribute("aria-current", "date");
  else button.removeAttribute("aria-current");
  setText(button.querySelector(".wd"), weekday);
  setText(button.querySelector(".dm"), String(day));
}

function syncStrip(strip, done, todayKey) {
  const doneDays = new Set(done);
  const days = weekWindow(todayKey);
  strip.querySelectorAll(".day").forEach((button, position) => {
    syncDay(button, days[position], doneDays.has(days[position]), days[position] === todayKey);
  });
  strip.toggleAttribute("data-run-continues", runContinues(done, todayKey));
}

function syncProgress(row, habit, todayKey) {
  syncStreak(row.querySelector(".streak"), habit.done, todayKey);
  syncStrip(row.querySelector(".strip"), habit.done, todayKey);
}

function emptyMessage() {
  const message = element("p", "empty");
  const lead = element("strong");
  lead.textContent = "No habits yet.";
  message.append(lead, " Add one you want to do every day.");
  return message;
}

/** Replaces the list (or the empty message) with fresh rows, for a first load, an add or a delete. */
export function renderList(habits, todayKey) {
  const section = $('section[aria-labelledby="habits-title"]');
  section.querySelectorAll(":scope > .empty, :scope > .habits").forEach((node) => node.remove());
  if (habits.length === 0) {
    section.append(emptyMessage());
    return;
  }
  const list = element("ul", "habits");
  habits.forEach((habit, position) => {
    const row = createRow(position, todayKey);
    fillRow(row, habit);
    syncProgress(row, habit, todayKey);
    list.append(row);
  });
  section.append(list);
}

/** After a tick: updates one existing row in place. */
export function syncHabit(index, habit, todayKey) {
  syncProgress($$(".habits > .habit")[index], habit, todayKey);
}

/** A habit's index is its row's place in the list: rows carry no index attribute (spec Events and focus). */
export function habitIndexOf(node) {
  return $$(".habits > .habit").indexOf(node.closest(".habit"));
}

// ---------------------------------------------------------------------------------------------
// Heatmap

function renderMonths(todayKey) {
  $(".months").replaceChildren(
    ...monthLabels(todayKey).map(({ column, month }) => {
      const label = element("span");
      label.style.gridColumn = String(column);
      label.textContent = month;
      return label;
    }),
  );
}

function fillCell(node, cell) {
  node.setAttribute("data-date", cell.key);
  if (cell.future) {
    node.className = "hc future";
    node.setAttribute("aria-hidden", "true");
    for (const name of ["role", "aria-label", "aria-current"]) node.removeAttribute(name);
    return;
  }
  node.className = `hc l${cell.level}${cell.today ? " today" : ""}`;
  node.removeAttribute("aria-hidden");
  node.setAttribute("role", "img");
  node.setAttribute("aria-label", `${shortDate(cell.key)}, ${cell.count} of ${cell.total} habits`);
  if (cell.today) node.setAttribute("aria-current", "date");
  else node.removeAttribute("aria-current");
}

/**
 * The 84 cells are created once and then set in place, so a changed level plays the dot's size
 * transition and an unchanged cell is left alone.
 */
export function renderHeatmap(habits, todayKey) {
  renderMonths(todayKey);
  const grid = $(".cells");
  const cells = heatmapCells(habits, todayKey);
  while (grid.children.length < cells.length) grid.append(element("span"));
  cells.forEach((cell, position) => fillCell(grid.children[position], cell));
}

// ---------------------------------------------------------------------------------------------
// Add form

function resetMessage() {
  const message = $("#new-habit-msg");
  message.className = "field-msg field-error";
  message.textContent = "";
  $("#new-habit").removeAttribute("aria-invalid");
}

/** @param {"empty" | "too-long" | "duplicate"} error */
export function showNameError(error) {
  resetMessage();
  $("#new-habit-msg").textContent = NAME_ERRORS[error];
  $("#new-habit").setAttribute("aria-invalid", "true");
}

export function clearNameError() {
  resetMessage();
}

export const nameFieldValue = () => $("#new-habit").value;

export function clearNameField() {
  $("#new-habit").value = "";
}

/** Has no effect while the field is disabled. */
export function focusNameField() {
  $("#new-habit").focus();
}

/** At the limit the field and Add are disabled and the message line holds the note; below it the note goes. */
export function setAddLimit(full) {
  $("#new-habit").disabled = full;
  $(".add .btn").disabled = full;
  const message = $("#new-habit-msg");
  if (full) {
    resetMessage();
    message.className = "field-msg field-note";
    message.textContent = LIMIT_NOTE;
  } else if (message.classList.contains("field-note")) {
    resetMessage();
  }
}

// ---------------------------------------------------------------------------------------------
// Note shown after unreadable saved data

export function showNote() {
  const dismiss = element("button", "icon-btn", { type: "button", "aria-label": "Dismiss note" });
  dismiss.append(icon("i-x"));
  const text = element("p", "note-text");
  text.textContent = RESET_NOTE;
  const note = element("div", "note", { role: "status" });
  note.append(text, dismiss);
  $(".col-main").prepend(note);
}

export function removeNote() {
  $(".note")?.remove();
}

// ---------------------------------------------------------------------------------------------
// Delete dialog

/** `returnValue` is reset because it persists between openings: a later Esc would repeat the last "delete". */
export function openDeleteDialog(habitName) {
  const dialog = $(".dialog");
  dialog.returnValue = "";
  $("#del-title").textContent = `Delete "${habitName}"?`;
  dialog.showModal();
}

export function focusDeleteButton(index) {
  $$(".habits > .habit")[index].querySelector(".icon-btn").focus();
}

// ---------------------------------------------------------------------------------------------
// Where app.js listens

export const containers = () => ({
  list: $('section[aria-labelledby="habits-title"]'),
  mainColumn: $(".col-main"),
  addForm: $(".add"),
  dialog: $(".dialog"),
});
