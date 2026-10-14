/**
 * The composition root (spec Contracts, Files): boots the page from the saved habits and today's date, and wires
 * the events. Why: the one place that joins habit-logic (the rules), storage.js (persistence) and the view modules
 * (the DOM), so none of them imports another's job. index.html loads this module and nothing else. It exports nothing.
 * State is the habits array and the shown day. Every change goes through a habit-logic function, then a save, then a
 * synchronous render inside the handler that caused it (spec Invariants).
 */
import { localDateKey } from "./dates.js";
import { MAX_HABITS, doneFlags, heatmapCells, toggleDay } from "./habits.js";
import { loadHabits, saveHabits } from "./storage.js";
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

/** Every edit takes this path, so each saves once and then shows the new habits everywhere at once (R16, R32). */
function edit(habits) {
  state.habits = habits;
  saveHabits(habits);
  render(true);
}

/**
 * Done today ticks or unticks today (R31). The button is updated in place by the render, and focus is never moved,
 * so a keyboard user stays on it.
 */
function onPageClick(event) {
  const index = view.doneTodayIndexOf(event.target);
  if (index >= 0) edit(toggleDay(state.habits, index, state.todayKey, state.todayKey));
}

function boot() {
  state.habits = loadHabits().habits;
  state.todayKey = readToday();
  view.renderDate(state.todayKey);
  render(false);
  const { page, frame } = view.containers();
  page.addEventListener("click", onPageClick);
  frame.addEventListener("scroll", view.renderFrameFades);
  window.addEventListener("resize", view.renderFrameFades);
}

boot();
