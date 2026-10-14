/**
 * The composition root (spec Contracts, Files): boots the page from the saved habits and today's date, and wires
 * the events. Why: the one place that joins habit-logic (the rules), storage.js (persistence) and the view modules
 * (the DOM), so none of them imports another's job. index.html loads this module and nothing else. It exports nothing.
 * State is the habits array and the shown day. Every change goes through a habit-logic function, then a save, then a
 * synchronous render inside the handler that caused it (spec Invariants).
 */
import { localDateKey } from "./dates.js";
import { MAX_HABITS, doneFlags, heatmapCells } from "./habits.js";
import { loadHabits } from "./storage.js";
import * as view from "./view.js";

/** The only clock read in the app, so tests move time with Playwright's clock alone (spec Invariants). */
function readToday() {
  return localDateKey(new Date());
}

const state = { habits: [], todayKey: "" };

/**
 * Draws every view of the habits for the shown day. `animate` is true when the render answers an edit, so what
 * the edit changed pops or bumps once (R32), and false at boot, where nothing moves (R23).
 */
function render(animate) {
  const { habits, todayKey } = state;
  view.renderOverviewButton(doneFlags(habits, todayKey), animate);
  view.renderBand(heatmapCells(habits, todayKey), todayKey, habits.length, animate);
  view.renderRows(habits, todayKey, animate);
  view.renderComposerLimit(habits.length >= MAX_HABITS);
  view.renderFrameFades();
}

function boot() {
  state.habits = loadHabits().habits;
  state.todayKey = readToday();
  view.renderDate(state.todayKey);
  render(false);
  view.containers().frame.addEventListener("scroll", view.renderFrameFades);
  window.addEventListener("resize", view.renderFrameFades);
}

boot();
