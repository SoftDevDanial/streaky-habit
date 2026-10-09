/**
 * The composition root: boots the page from the saved habits and today's date, and wires the events.
 * Why: the one place that joins habit-logic (rules), storage.js (persistence) and view.js (DOM), so none
 * of those three knows about the others. Index.html loads this module and nothing else; it exports nothing.
 * State is the habits array plus the day the page shows. Every change goes through a habit-logic
 * function, then a save, then a synchronous render inside the handler that caused it.
 */
import { localDateKey } from "./dates.js";
import { MAX_HABITS, addHabit, toggleDay } from "./habits.js";
import { loadHabits, saveHabits } from "./storage.js";
import * as view from "./view.js";

/** The only clock read in the app, so tests move time with Playwright's clock alone (spec Invariants). */
function readToday() {
  return localDateKey(new Date());
}

const state = { habits: [], todayKey: "" };

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

function onListClick(event) {
  const dayButton = event.target.closest("button.day");
  if (dayButton) tick(dayButton);
}

function rejectName(error) {
  // "limit" cannot come from a real submit (the field and Add are disabled at 12), but addHabit can
  // return it, and there is no name message for it.
  if (error === "limit") {
    view.setAddLimit(true);
    return;
  }
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

function boot() {
  state.habits = loadHabits().habits;
  state.todayKey = readToday();
  view.renderHeader(state.todayKey);
  renderHabits();
  const { list, addForm } = view.containers();
  list.addEventListener("click", onListClick);
  addForm.addEventListener("submit", submitName);
}

boot();
