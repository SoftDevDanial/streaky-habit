/**
 * The composition root: boots the page from the saved habits and today's date, and wires the events.
 * Why: the one place that joins habit-logic (rules), storage.js (persistence) and view.js (DOM), so none
 * of those three knows about the others. Index.html loads this module and nothing else; it exports nothing.
 * State is the habits array plus the day the page shows. Every change goes through a habit-logic
 * function, then a save, then a synchronous render inside the handler that caused it.
 */
import { localDateKey } from "./dates.js";
import { MAX_HABITS } from "./habits.js";
import { loadHabits } from "./storage.js";
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

function boot() {
  state.habits = loadHabits().habits;
  state.todayKey = readToday();
  view.renderHeader(state.todayKey);
  renderHabits();
}

boot();
