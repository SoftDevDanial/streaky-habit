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

/**
 * The second click of a double click or double tap lands where the first one left the screen (spec T7): on
 * "Delete habit" when the first click opened the dialog under the pointer, and on the page behind the dialog
 * when the first click closed it. For this long, measured in browser event time (no timer, no clock read of
 * our own), "Delete habit" ignores clicks after the one that opened the dialog, and the page ignores clicks
 * after a mouse or touch click in the dialog. The CSS cannot do it: R2 locks it to the golden.
 */
const DIALOG_GUARD_MS = 500;
const withinGuard = (event, since) => event.timeStamp - since < DIALOG_GUARD_MS;

const state = { habits: [], todayKey: "" };

// The delete dialog is one element reused for every habit, so what it is about lives here while it is open.
let pendingDelete = null; // index of the habit the open dialog asks about
let dialogOpenedAt = -Infinity; // event time of the click that opened the dialog
let dialogPressedAt = -Infinity; // event time of the latest mouse or touch click inside the dialog
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

function askToDelete(deleteButton, openingClick) {
  pendingDelete = view.habitIndexOf(deleteButton);
  dialogOpenedAt = openingClick.timeStamp;
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

/**
 * Cancelling the click of a submit button cancels the submit, so the dialog stays open. Registered for the
 * capture phase so that a later listener on the button or the form cannot stop the event before this runs.
 * `detail` is 0 for a click made with the keyboard and above 0 for mouse and touch, so closing the dialog
 * with the keyboard never holds the page.
 */
function guardDialogClick(event) {
  if (event.detail > 0) dialogPressedAt = event.timeStamp;
  if (view.confirmButtonOf(event.target) && withinGuard(event, dialogOpenedAt)) event.preventDefault();
}

/**
 * Registered on the page, not the document, so a press in the dialog is never held by it. The page is inert
 * while the dialog is open, so a page click this soon after a press in the dialog is that gesture's second click.
 */
function swallowTapThrough(event) {
  if (!withinGuard(event, dialogPressedAt)) return;
  event.preventDefault();
  event.stopPropagation();
}

function onListClick(event) {
  const dayButton = view.dayButtonOf(event.target);
  if (dayButton) tick(dayButton);
  const deleteButton = view.deleteButtonOf(event.target);
  if (deleteButton) askToDelete(deleteButton, event);
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
  view.resetMessage();
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
  view.renderMonths(today);
  view.syncHabits(state.habits, today);
  view.renderHeatmap(state.habits, today);
}

/** The note's button disappears with the note, so focus goes to the field (it has no effect while the field is disabled). */
function onMainColumnClick(event) {
  if (!view.dismissButtonOf(event.target)) return;
  view.removeNote();
  view.focusNameField();
}

function boot() {
  const { habits, reset } = loadHabits();
  state.habits = habits;
  state.todayKey = readToday();
  view.renderHeader(state.todayKey);
  view.renderMonths(state.todayKey);
  renderHabits();
  if (reset) view.showNote();
  const { page, list, mainColumn, addForm, dialog } = view.containers();
  page.addEventListener("click", swallowTapThrough, true);
  mainColumn.addEventListener("click", onMainColumnClick);
  list.addEventListener("click", onListClick);
  addForm.addEventListener("submit", submitName);
  dialog.addEventListener("close", onDialogClose);
  dialog.addEventListener("pointerdown", onDialogPointerDown);
  dialog.addEventListener("click", onDialogClick);
  dialog.addEventListener("click", guardDialogClick, true);
  setInterval(checkDay, ROLLOVER_CHECK_MS);
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") checkDay();
  });
}

boot();
