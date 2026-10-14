/**
 * The composition root (spec Contracts, Files): boots the page from the saved habits and today's date, and wires
 * the events. Why: the one place that joins habit-logic (the rules), storage.js (persistence) and the view modules
 * (the DOM), so none of them imports another's job. index.html loads this module and nothing else. It exports nothing.
 * State is the habits array, the shown day and the open popups with their openers. Every change goes through a
 * habit-logic function, then a save, then a synchronous render inside the handler that caused it (spec Invariants).
 */
import { beadOf, dayButtonOf } from "./calendar.js";
import { localDateKey } from "./dates.js";
import { MAX_HABITS, addHabit, deleteHabit, doneFlags, heatmapCells, toggleDay } from "./habits.js";
import * as popups from "./popups.js";
import { loadHabits, saveHabits } from "./storage.js";
import * as view from "./view.js";

/** For this long after a mouse or touch click inside a popup, in event time, the layers beneath it ignore clicks (R14). */
const TAP_THROUGH_MS = 500;

/** The only clock read in the app, so tests move time with Playwright's clock alone (spec Invariants). */
function readToday() {
  return localDateKey(new Date());
}

/**
 * `day` is the date P1 is open for, `year` the position of the habit P2 is open for, `remove` what M1 is open for
 * (the habit's position, whether M1 came from P2, and the box of the control that opened it), each null while its
 * popup is closed. A position stays right while its popup is open, because popups are modal and nothing adds or
 * deletes behind them.
 */
const state = { habits: [], todayKey: "", day: null, year: null, remove: null };

/**
 * Each open popup and the control that opened it, so closing it puts focus back there (rule 1). A Map keeps the order
 * the popups opened in, so its keys are the stack, bottom first (R40).
 */
const openers = new Map();

/** Whether the current press began on a popup's backdrop (R40). */
let pressStartedOnBackdrop = false;

/** The event time of the latest mouse or touch click inside a popup, and the layers that lay beneath that popup (R14). */
let lastPopupPress = null;

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
 * M1 for the habit at `index` (R13), over K1 from its row's bin or over P2 from P2's Delete habit, with focus on
 * Cancel. The opener's box is kept for the guard of Delete habit (`isStrayPress`).
 */
function openDelete(opener, index) {
  const { remove, habitYear } = popups.dialogs();
  state.remove = { index, fromYear: habitYear.contains(opener), openerBox: opener.getBoundingClientRect() };
  popups.renderDeleteTitle(state.habits[index].name);
  openPopup(remove, opener, popups.closeButtonOf(remove));
}

/**
 * The guard of Delete habit (R13, CG-10). M1 opens under the pointer, so the second click of a double click or double
 * tap, slow or fast, lands where the first one opened M1. A mouse or touch click (`detail` above 0) is ignored when
 * its point lies in the opener's box or when it is a second click by the browser's count. A keyboard click (`detail`
 * 0) always acts, and nothing depends on time.
 */
function isStrayPress(event, box) {
  if (event.detail === 0) return false;
  const inBox = event.clientX >= box.left && event.clientX <= box.right && event.clientY >= box.top && event.clientY <= box.bottom;
  return event.detail > 1 || inBox;
}

/**
 * Delete habit (R15). The habit and its history go through `deleteHabit` and `edit` (one save, R32), M1 closes, and
 * P2 too when M1 came from it. Focus then goes by rule 3 (CG-18), so neither close returns it to an opener.
 */
function deleteFromM1() {
  const { index, fromYear } = state.remove;
  const { remove, habitYear } = popups.dialogs();
  closeWithoutReturn(remove);
  if (fromYear) closeWithoutReturn(habitYear);
  edit(deleteHabit(state.habits, index));
  view.focusAfterDelete(index, fromYear);
}

/** Closes `dialog` with no opener left for `onPopupClose` to focus, because the caller sets focus itself. */
function closeWithoutReturn(dialog) {
  openers.delete(dialog);
  dialog.close();
}

/**
 * Done today ticks or unticks today (R31). The button is updated in place by the render, and focus is never moved,
 * so a keyboard user stays on it. A row's bin opens M1, the Overview button opens P3, the band's Year opens P4, a
 * row's Year opens P2, a band day opens P1.
 */
function onPageClick(event) {
  const index = view.doneTodayIndexOf(event.target);
  if (index >= 0) {
    edit(toggleDay(state.habits, index, state.todayKey, state.todayKey));
    return;
  }
  const bin = view.binOf(event.target);
  if (bin) {
    openDelete(bin, view.habitIndexOf(bin));
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

/**
 * Add or Enter in the composer (R10, R11). An accepted name goes through `edit`, so it saves once and shows
 * everywhere (R32), and then the frame shows the new last row (CG-15). Focus stays where the user left it. A
 * rejected name shows its message and moves focus to the field. At 12 habits R12 disables the field and Add, so
 * the form cannot be submitted and every refusal here is a name error. The page never navigates.
 */
function onComposerSubmit(event) {
  event.preventDefault();
  const result = addHabit(state.habits, view.composerText());
  if (!result.ok) {
    view.showNameError(result.error);
    return;
  }
  view.emptyComposer();
  edit(result.habits);
  view.showLastRow();
}

function onPopupPointerDown(event) {
  pressStartedOnBackdrop = popups.onBackdrop(event.currentTarget, event);
}

/**
 * Close (or M1's Cancel) closes its popup, and so does a click whose press and release both land on the backdrop. A
 * click inside the box, or a drag from the box to the backdrop, closes nothing (R40). Inside the box M1's Delete habit
 * deletes unless the guard holds the click (R13), P2's Delete habit opens M1 over P2, P3's Year opens P4 over P3, a
 * day button opens P1 over this popup, a tick in P1 ticks or unticks P1's day for its habit (R37), and a bead in P2
 * its day for P2's habit (R34), with focus left where it is.
 */
function onPopupClick(event) {
  const dialog = event.currentTarget;
  const pressedOnBackdrop = pressStartedOnBackdrop;
  pressStartedOnBackdrop = false;
  if (popups.closeButtonOf(dialog).contains(event.target) || (pressedOnBackdrop && popups.onBackdrop(dialog, event))) {
    dialog.close();
    return;
  }
  if (popups.confirmDeleteOf(event.target)) {
    if (!isStrayPress(event, state.remove.openerBox)) deleteFromM1();
    return;
  }
  const yearDelete = popups.yearDeleteOf(event.target);
  if (yearDelete) {
    openDelete(yearDelete, state.year);
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

/** The layers beneath `popup`, the page and then the popups that opened before it and are still open, bottom first. */
function layersBeneath(popup) {
  const stack = [...openers.keys()];
  return [view.containers().page, ...stack.slice(0, Math.max(0, stack.indexOf(popup)))];
}

/**
 * The tap-through guard (R14, CG-11). A click that closes a popup sends the second click of the same gesture to the
 * layer behind it. So for TAP_THROUGH_MS after a mouse or touch click inside a popup (its backdrop included), measured
 * in `event.timeStamp`, a click on the page or on a popup that lay beneath it is cancelled. Clicks in that popup, and
 * in popups opened after it, are never held, and a keyboard click (`detail` 0) starts no window.
 */
function guardTapThrough(event) {
  const layer = event.currentTarget;
  const held = lastPopupPress && event.timeStamp - lastPopupPress.at < TAP_THROUGH_MS && lastPopupPress.beneath.includes(layer);
  if (held) {
    event.preventDefault();
    // Immediate, because a click on a backdrop targets the dialog itself, where its own click listener would still run.
    event.stopImmediatePropagation();
    return;
  }
  if (layer.localName === "dialog" && event.detail > 0) lastPopupPress = { at: event.timeStamp, beneath: layersBeneath(layer) };
}

/**
 * Every way out of a popup ends here (Close, Cancel, Esc, the backdrop, a delete). Focus goes back to its opener by
 * hand, because a clicked button never took focus in WebKit, so the native return has nothing to return to (R40).
 */
function onPopupClose(event) {
  const dialog = event.currentTarget;
  const { day, habitYear, remove } = popups.dialogs();
  if (dialog === day) {
    state.day = null;
    popups.markOpenDay(null);
    popups.clearDayRoom();
  }
  if (dialog === habitYear) state.year = null;
  if (dialog === remove) state.remove = null;
  const opener = openers.get(dialog);
  openers.delete(dialog);
  opener?.focus();
}

function boot() {
  state.habits = loadHabits().habits;
  state.todayKey = readToday();
  view.renderDate(state.todayKey);
  render(false);
  const { page, frame, composer, field } = view.containers();
  // The guard listens in the capture phase and first, so a held click reaches no other listener (R14).
  page.addEventListener("click", guardTapThrough, true);
  page.addEventListener("click", onPageClick);
  composer.addEventListener("submit", onComposerSubmit);
  field.addEventListener("input", view.clearNameError);
  frame.addEventListener("scroll", view.renderFrameFades);
  window.addEventListener("resize", view.renderFrameFades);
  for (const dialog of Object.values(popups.dialogs())) {
    dialog.addEventListener("click", guardTapThrough, true);
    dialog.addEventListener("pointerdown", onPopupPointerDown);
    dialog.addEventListener("click", onPopupClick);
    dialog.addEventListener("close", onPopupClose);
  }
}

boot();
