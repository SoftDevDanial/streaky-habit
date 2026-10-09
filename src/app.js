/**
 * The composition root: boots the page from the saved habits and today's date, and wires the events.
 * Why: the one place that joins habit-logic (rules), storage.js (persistence) and view.js (DOM), so
 * storage.js and view.js never import each other. Index.html loads this module and nothing else; it exports nothing.
 * State is the habits array plus the day the page shows. Every change goes through a habit-logic
 * function, then a save, then a synchronous render inside the handler that caused it.
 */
import { localDateKey } from "./dates.js";
import { MAX_HABITS, addHabit, deleteHabit, toggleDay } from "./habits.js";
import { loadHabits, saveHabits } from "./storage.js";
import * as view from "./view.js";

/** The only clock read in the app, so tests move time with Playwright's clock alone (spec Invariants). */
function readToday() {
  return localDateKey(new Date());
}

/** Half the 60 second promise ("within a minute"), so one late timer still keeps it. */
const ROLLOVER_CHECK_MS = 30000;

const state = { habits: [], todayKey: "" };

// The delete dialog is one element reused for every habit, so what it is about lives here while it is open.
let pendingDelete = null; // index of the habit the open dialog asks about
let pressedOutside = false; // whether the current mouse press began on the backdrop

/** Everything that depends on the habit list: the rows, the heatmap counts and the add form's limit. */
function renderHabits() {
  view.renderList(state.habits, state.todayKey);
  view.renderHeatmap(state.habits, state.todayKey);
  view.setAddLimit(state.habits.length >= MAX_HABITS);
}

/** Updates the button that was pressed instead of replacing it, so its transition runs and it keeps focus. */
function tick(dayButton) {
  const index = view.habitIndexOf(dayButton);
  state.habits = toggleDay(state.habits, index, dayButton.getAttribute("data-date"), state.todayKey);
  saveHabits(state.habits);
  view.syncHabit(index, state.habits[index], state.todayKey);
  view.renderHeatmap(state.habits, state.todayKey);
}

function askToDelete(deleteButton) {
  pendingDelete = view.habitIndexOf(deleteButton);
  view.openDeleteDialog(state.habits[pendingDelete].name);
}

function removeHabit(index) {
  state.habits = deleteHabit(state.habits, index);
  saveHabits(state.habits);
  renderHabits();
  if (index < state.habits.length) view.focusDeleteButton(index);
  else view.focusNameField();
}

/**
 * Runs once for Cancel, Esc, a backdrop click and Delete habit alike; only the dialog's returnValue tells
 * them apart. Focus is put back by hand: some browsers do not focus a button on click, so the native
 * return to "the element that opened the dialog" cannot be relied on.
 */
function onDialogClose(event) {
  if (pendingDelete === null) return;
  const index = pendingDelete;
  pendingDelete = null;
  if (event.currentTarget.returnValue === "delete") removeHabit(index);
  else view.focusDeleteButton(index);
}

const isOutside = (event, box) =>
  event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom;

/**
 * A click on ::backdrop is dispatched to the dialog element, and so is a click on the dialog's own
 * padding, so the target alone cannot tell them apart: the point must lie outside the box. The press is
 * checked as well, so a text selection that starts in the box and ends on the backdrop keeps it open (CG-6).
 */
function onDialogPointerDown(event) {
  const dialog = event.currentTarget;
  pressedOutside = event.target === dialog && isOutside(event, dialog.getBoundingClientRect());
}

function onDialogClick(event) {
  const dialog = event.currentTarget;
  const releasedOutside = event.target === dialog && isOutside(event, dialog.getBoundingClientRect());
  if (pressedOutside && releasedOutside) dialog.close("cancel");
  pressedOutside = false;
}

function onListClick(event) {
  const dayButton = event.target.closest("button.day");
  if (dayButton) tick(dayButton);
  const deleteButton = event.target.closest(".habit-head .icon-btn");
  if (deleteButton) askToDelete(deleteButton);
}

/** `error` is never "limit": at 12 habits the field and Add are disabled (`setAddLimit`), so no submit reaches addHabit. */
function rejectName(error) {
  view.showNameError(error);
  view.focusNameField();
}

function submitName(event) {
  event.preventDefault();
  const result = addHabit(state.habits, view.nameFieldValue());
  if (!result.ok) {
    rejectName(result.error);
    return;
  }
  state.habits = result.habits;
  saveHabits(state.habits);
  view.clearNameError();
  view.clearNameField();
  renderHabits();
}

/**
 * Moves the page to a new local day once the device clock says so, never before. Rows, buttons and
 * heat cells are updated in place, so focus stays on the same button position and the add form
 * (text, message, invalid state) is not touched.
 */
function checkDay() {
  const today = readToday();
  if (today === state.todayKey) return;
  state.todayKey = today;
  view.renderHeader(today);
  view.syncHabits(state.habits, today);
  view.renderHeatmap(state.habits, today);
}

/** The note's button disappears with the note, so focus goes to the field (it has no effect while the field is disabled). */
function onMainColumnClick(event) {
  if (!event.target.closest(".note .icon-btn")) return;
  view.removeNote();
  view.focusNameField();
}

function boot() {
  const { habits, reset } = loadHabits();
  state.habits = habits;
  state.todayKey = readToday();
  view.renderHeader(state.todayKey);
  renderHabits();
  if (reset) view.showNote();
  const { list, mainColumn, addForm, dialog } = view.containers();
  mainColumn.addEventListener("click", onMainColumnClick);
  list.addEventListener("click", onListClick);
  addForm.addEventListener("submit", submitName);
  dialog.addEventListener("close", onDialogClose);
  dialog.addEventListener("pointerdown", onDialogPointerDown);
  dialog.addEventListener("click", onDialogClick);
  setInterval(checkDay, ROLLOVER_CHECK_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") checkDay();
  });
}

boot();
