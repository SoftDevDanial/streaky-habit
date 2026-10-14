/**
 * The composition root (spec Contracts, Files): boots the page from the saved habits and today's date, and wires
 * the events. Why: the one place that joins habit-logic (the rules), storage.js (persistence) and the view modules
 * (the DOM), so none of them imports another's job. index.html loads this module and nothing else. It exports nothing.
 * State is the habits array, the shown day and the open popups with their openers. Every change goes through a
 * habit-logic function, then a save, then a synchronous render inside the handler that caused it (spec Invariants).
 */
import { beadOf, dayButtonOf } from "./calendar.js";
import { localDateKey } from "./dates.js";
import { MAX_HABITS, doneFlags, heatmapCells, toggleDay } from "./habits.js";
import * as popups from "./popups.js";
import { loadHabits, saveHabits } from "./storage.js";
import * as view from "./view.js";

/** The only clock read in the app, so tests move time with Playwright's clock alone (spec Invariants). */
function readToday() {
  return localDateKey(new Date());
}

/**
 * `day` is the date P1 is open for, `year` the position of the habit P2 is open for, each null while its popup is
 * closed. A position stays right while P2 is open, because P2 is modal and nothing adds or deletes behind it.
 */
const state = { habits: [], todayKey: "", day: null, year: null };

/** Each open popup and the control that opened it, so closing it puts focus back there (rule 1). */
const openers = new Map();

/** Whether the current press began on a popup's backdrop (R40). */
let pressStartedOnBackdrop = false;

/**
 * Draws every view of the habits for the shown day, the open popups included. `animate` is true when the render
 * answers an edit, so what the edit changed pops or bumps once (R32), and false at boot, where nothing moves (R23).
 */
function render(animate) {
  const { habits, todayKey } = state;
  const cells = heatmapCells(habits, todayKey);
  view.renderOverviewButton(doneFlags(habits, todayKey), animate);
  view.renderBand(cells, todayKey, habits.length, animate);
  const open = popups.dialogs();
  if (open.overview.open) popups.renderOverviewPopup(cells, todayKey, habits.length, animate);
  if (open.allHabits.open) popups.renderAllHabitsYear(habits, todayKey, animate);
  if (open.day.open) popups.renderDayEditor(state.day, habits, todayKey, animate);
  if (open.habitYear.open) popups.renderHabitYear(habits[state.year], todayKey, animate);
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

function openPopup(dialog, opener, focusTarget) {
  openers.set(dialog, opener);
  popups.showPopup(dialog, focusTarget);
}

/** P3, the 12 weeks on a phone (R38), drawn fresh as it opens. */
function openOverview(opener) {
  const { overview } = popups.dialogs();
  popups.renderOverviewPopup(heatmapCells(state.habits, state.todayKey), state.todayKey, state.habits.length, false);
  openPopup(overview, opener, popups.closeButtonOf(overview));
}

/** P4, the year of all habits (R39), from the band's Year (over K1) or P3's Year (over P3), drawn fresh as it opens. */
function openAllHabits(opener) {
  const { allHabits } = popups.dialogs();
  popups.renderAllHabitsYear(state.habits, state.todayKey, false);
  openPopup(allHabits, opener, popups.closeButtonOf(allHabits));
}

/** P1 for the day of `dayButton` (R36), over K1, P3 or P4, which marks that day open everywhere it shows. */
function openDay(dayButton) {
  state.day = dayButton.getAttribute("data-key");
  popups.buildDayList(state.habits);
  popups.renderDayEditor(state.day, state.habits, state.todayKey, false);
  popups.markOpenDay(state.day);
  openPopup(popups.dialogs().day, dayButton, popups.dayEditorFocus());
  popups.keepDayInSight(dayButton);
}

/** P2, the year of the habit whose row holds `yearButton` (R33). */
function openYear(yearButton) {
  state.year = view.habitIndexOf(yearButton);
  popups.renderHabitYear(state.habits[state.year], state.todayKey, false);
  const { habitYear } = popups.dialogs();
  openPopup(habitYear, yearButton, popups.closeButtonOf(habitYear));
}

/**
 * Done today ticks or unticks today (R31). The button is updated in place by the render, and focus is never moved,
 * so a keyboard user stays on it. The Overview button opens P3, the band's Year opens P4, a row's Year opens P2, a
 * band day opens P1.
 */
function onPageClick(event) {
  const index = view.doneTodayIndexOf(event.target);
  if (index >= 0) {
    edit(toggleDay(state.habits, index, state.todayKey, state.todayKey));
    return;
  }
  const overviewButton = view.overviewButtonOf(event.target);
  if (overviewButton) {
    openOverview(overviewButton);
    return;
  }
  const allHabitsButton = view.allHabitsButtonOf(event.target);
  if (allHabitsButton) {
    openAllHabits(allHabitsButton);
    return;
  }
  const yearButton = view.yearButtonOf(event.target);
  if (yearButton) {
    openYear(yearButton);
    return;
  }
  const dayButton = dayButtonOf(event.target);
  if (dayButton) openDay(dayButton);
}

function onPopupPointerDown(event) {
  pressStartedOnBackdrop = popups.onBackdrop(event.currentTarget, event);
}

/**
 * Close closes its popup, and so does a click whose press and release both land on the backdrop. A click inside the
 * box, or a drag from the box to the backdrop, closes nothing (R40). Inside the box P3's Year opens P4 over P3, a day
 * button opens P1 over this popup, a tick in P1 ticks or unticks P1's day for its habit (R37), and a bead in P2 its
 * day for P2's habit (R34), with focus left where it is.
 */
function onPopupClick(event) {
  const dialog = event.currentTarget;
  const pressedOnBackdrop = pressStartedOnBackdrop;
  pressStartedOnBackdrop = false;
  const close = popups.closeButtonOf(dialog);
  if ((close && close.contains(event.target)) || (pressedOnBackdrop && popups.onBackdrop(dialog, event))) {
    dialog.close();
    return;
  }
  const allHabitsButton = view.allHabitsButtonOf(event.target);
  if (allHabitsButton) {
    openAllHabits(allHabitsButton);
    return;
  }
  const dayButton = dayButtonOf(event.target);
  if (dayButton) {
    openDay(dayButton);
    return;
  }
  const tickIndex = popups.tickIndexOf(event.target);
  if (tickIndex >= 0) {
    edit(toggleDay(state.habits, tickIndex, state.day, state.todayKey));
    return;
  }
  const bead = beadOf(event.target);
  if (bead) edit(toggleDay(state.habits, state.year, bead.getAttribute("data-key"), state.todayKey));
}

/**
 * Every way out of a popup ends here (Close, Esc, the backdrop). Focus goes back to its opener by hand, because a
 * clicked button never took focus in WebKit, so the native return has nothing to return to (R40).
 */
function onPopupClose(event) {
  const dialog = event.currentTarget;
  const { day, habitYear } = popups.dialogs();
  if (dialog === day) {
    state.day = null;
    popups.markOpenDay(null);
    popups.clearDayRoom();
  }
  if (dialog === habitYear) state.year = null;
  const opener = openers.get(dialog);
  openers.delete(dialog);
  opener?.focus();
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
  for (const dialog of Object.values(popups.dialogs())) {
    dialog.addEventListener("pointerdown", onPopupPointerDown);
    dialog.addEventListener("click", onPopupClick);
    dialog.addEventListener("close", onPopupClose);
  }
}

boot();
