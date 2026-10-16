/**
 * The rings and the day grids (spec R33 to R35, R38, R39, R42, Contracts "Files").
 * Why: a day must read the same wherever it shows (system.md principle 1), so every ring (the band, P3, P4, P1's
 * mini ring, the Overview button) and every legend is drawn here from habit-logic's cells and done flags, and so are
 * the months of the year views, P2's beads with their threads and P4's day buttons. A new day lays the grids out
 * again, so this module also finds a day's control again by its date (R19).
 * Input: cells, habits, flags and date keys, never a clock or storage. Output: new elements, and changes to the
 * containers it is given. It registers no event listener. As the lowest DOM module it also owns the two element
 * factories the other view modules share. Data reaches the DOM only through textContent and setAttribute (R24).
 */
import { dayParts, shortDate, yearDate } from "./dates.js";
import { doneFlags, monthLabels, yearMonths } from "./habits.js";
import { arcPath, legendCounts } from "./ring.js";

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const RING_CENTRE = "20";
const SEGMENT_RADIUS = "15";
const TODAY_RADIUS = "19.2";
const CORE_RADIUS = "11.5";
const WEEKDAY_LETTERS = ["M", "T", "W", "T", "F", "S", "S"];
const DAYS_PER_WEEK = 7;

/** A day cell that opens P1, in the band, P3 and P4 (spec Contracts, Day cell). */
export const DAY_BUTTON = "button.hc";

/** The day button a click landed on, or null. */
export const dayButtonOf = (target) => target.closest(DAY_BUTTON);

/** A habit's open day in P2, which ticks it (spec Contracts, Bead). */
const BEAD = "button.yc";

/** The bead a click landed on, or null. */
export const beadOf = (target) => target.closest(BEAD);

/** A control for one day, which a new day replaces when it lays its grid out again. */
const DAY_CONTROL = `${DAY_BUTTON}, ${BEAD}`;

/** The grids a new day lays out again, the band's, P3's, and the months of P2 and P4. Each keeps its own element. */
const DAY_GRID = "div.ovg-cols, div.ovg-rows, div.months";

/**
 * Where `control` sits when it is a day button or a bead, its grid and its date, so that `dayControlAt` finds the
 * control for the same day once a new day has laid that grid out again (R19). Null for any other control, and for
 * no control, because a new day leaves every other control in place.
 */
export function dayPlace(control) {
  if (!control?.matches(DAY_CONTROL)) return null;
  return { control, grid: control.closest(DAY_GRID), key: control.getAttribute("data-key") };
}

/**
 * The control a `dayPlace` names. The same element while it is still in the page, else the control for the same date
 * in the same grid (in P2, the same habit), else null when the new day left that date out.
 */
export function dayControlAt({ control, grid, key }) {
  if (control.isConnected) return control;
  return Array.from(grid.querySelectorAll(DAY_CONTROL)).find((day) => day.getAttribute("data-key") === key) ?? null;
}

/** An HTML element with its class, attributes and text. An empty class or text is left unset. */
export function element(tag, className = "", attributes = {}, text = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  if (text) node.textContent = text;
  return node;
}

/** Made with createElementNS, because an svg made by createElement is an HTML element and draws nothing. */
export function svgElement(tag, attributes = {}) {
  const node = document.createElementNS(SVG_NAMESPACE, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  return node;
}

/** An empty ring, for `drawRing` to fill. */
export function ringSvg() {
  return svgElement("svg", { viewBox: "0 0 40 40", "aria-hidden": "true" });
}

/**
 * Adds `className` when `changed`, else removes it, so only what an edit changed carries the class (R32).
 */
export function flagChange(node, className, changed) {
  if (changed && node.classList.contains(className)) {
    node.classList.remove(className);
    // Looks like a wasted read, but it is not: the layout read applies the removal, so the class added back below
    // starts its animation again when the same element changes twice in a row (R23).
    node.getBoundingClientRect();
  }
  node.classList.toggle(className, changed);
}

const drawnRings = new WeakMap(); // ring svg -> a key of what it shows

/**
 * Draws a ring (R42) into `svg`, or leaves it alone when it already shows the same thing.
 * @param {SVGSVGElement} svg
 * @param {boolean[]} flags one per habit in list order (habit-logic `doneFlags`), empty when there is no habit
 * @param {{ today?: boolean, day?: number }} options the today circle, and the number of a day cell
 * @returns {boolean} true when it redrew a ring drawn before, so the caller can pop it. A first drawing gives
 *   false, so nothing moves on load or in a grid just built (R23)
 */
export function drawRing(svg, flags, { today = false, day } = {}) {
  const shows = `${today}|${flags.map(Number).join("")}|${day ?? ""}`;
  const before = drawnRings.get(svg);
  if (before === shows) return false;
  drawnRings.set(svg, shows);
  svg.replaceChildren(...ringParts(flags, today, day));
  return before !== undefined;
}

function ringParts(flags, today, day) {
  const full = flags.length > 0 && flags.every(Boolean);
  const parts = [];
  if (today) parts.push(circle("c-today", TODAY_RADIUS));
  parts.push(...segments(flags));
  if (full) parts.push(circle("c-core", CORE_RADIUS));
  if (day !== undefined) parts.push(dayNumber(day, full ? "c-num on" : "c-num"));
  return parts;
}

/** SVG text on the baseline at the ring's centre, dropped .352em, so the figures centre by their ink (rule 6). */
function dayNumber(day, className) {
  const text = svgElement("text", { class: className, x: RING_CENTRE, y: RING_CENTRE, dy: ".352em" });
  text.textContent = String(day);
  return text;
}

/** No habit or one habit is one whole circle, two or more are arcs (R42). */
function segments(flags) {
  if (flags.length < 2) return [circle(flags[0] ? "seg on" : "seg", SEGMENT_RADIUS)];
  return flags.map((on, index) => svgElement("path", { class: on ? "seg on" : "seg", d: arcPath(index, flags.length) }));
}

function circle(className, radius) {
  return svgElement("circle", { class: className, cx: RING_CENTRE, cy: RING_CENTRE, r: radius });
}

const drawnLegends = new WeakMap(); // legend -> the number of habits it was drawn for

/** "None", a ring for each count of `legendCounts`, then "All" (R42). Redrawn only when the number of habits changes. */
export function drawLegend(legend, habitCount) {
  if (drawnLegends.get(legend) === habitCount) return;
  drawnLegends.set(legend, habitCount);
  const rings = legendCounts(habitCount).map((count) => {
    const svg = ringSvg();
    drawRing(svg, Array.from({ length: habitCount }, (_, index) => index < count));
    return svg;
  });
  legend.replaceChildren(element("span", "", {}, "None"), ...rings, element("span", "", {}, "All"));
}

const laidOutFor = new WeakMap(); // a day grid (the band's, P3's or P4's) -> the today key it was laid out for

/**
 * The 12 weeks of `heatmapCells`, as the band's columns (`newestFirst` false, R35) or P3's rows (true, R38).
 * The layout depends on the day alone, so it is built again only for a new day. Every other render renames and
 * redraws the day buttons in place, so a button keeps its focus and a changed day pops when `animate` is set (R32).
 * @param {HTMLElement} grid div.ovg-cols or div.ovg-rows
 * @param {import("./habits.js").HeatCell[]} cells
 * @param {string} todayKey
 * @param {{ newestFirst: boolean, animate: boolean }} options
 */
export function drawOverview(grid, cells, todayKey, { newestFirst, animate }) {
  if (laidOutFor.get(grid) !== todayKey) {
    laidOutFor.set(grid, todayKey);
    layOutWeeks(grid, cells, todayKey, newestFirst);
  }
  const cellOf = new Map(cells.map((cell) => [cell.key, cell]));
  for (const button of grid.querySelectorAll(DAY_BUTTON)) {
    const cell = cellOf.get(button.getAttribute("data-key"));
    syncDayButton(button, shortDate(cell.key), cell.done, cell.today, animate);
  }
}

/**
 * P4, the year of all habits (R39): the months of `yearMonths`, newest first, each open day a day button named with
 * its year ("Fri 10 Oct 2025, 3 of 3 habits", P4 holds two Octobers). Laid out again only for a new day, and every
 * other render renames and redraws the day buttons in place, as `drawOverview` does (R32).
 * @param {HTMLElement} months P4's div.months
 * @param {readonly import("./habits.js").Habit[]} habits
 * @param {string} todayKey
 * @param {boolean} animate
 */
export function drawAllHabitsYear(months, habits, todayKey, animate) {
  if (laidOutFor.get(months) !== todayKey) {
    laidOutFor.set(months, todayKey);
    const openCell = (day) => dayButton(day.key, day.key === todayKey);
    layOutMonths(months, todayKey, { idPrefix: "amo", cellClass: "hc", openCell, closedCell: closedDayCell });
  }
  for (const button of months.querySelectorAll(DAY_BUTTON)) {
    const key = button.getAttribute("data-key");
    syncDayButton(button, yearDate(key), doneFlags(habits, key), key === todayKey, animate);
  }
}

/**
 * A day button's name, "<date>, <count> of <total> habits", and its ring with the day's number (R35, R38, R39). The
 * button pops when `animate` is set and its ring changed (R32).
 */
function syncDayButton(button, dateText, flags, today, animate) {
  button.setAttribute("aria-label", `${dateText}, ${flags.filter(Boolean).length} of ${flags.length} habits`);
  const day = dayParts(button.getAttribute("data-key")).day;
  const changed = drawRing(button.firstElementChild, flags, { today, day });
  flagChange(button, "pop", animate && changed);
}

function layOutWeeks(grid, cells, todayKey, newestFirst) {
  const weeks = Array.from({ length: cells.length / DAYS_PER_WEEK }, (_, week) =>
    cells.slice(week * DAYS_PER_WEEK, (week + 1) * DAYS_PER_WEEK),
  );
  const months = weekMonths(weeks, todayKey, newestFirst);
  const order = weeks.map((_, week) => (newestFirst ? weeks.length - 1 - week : week));
  grid.replaceChildren(
    element("div", "", { "aria-hidden": "true" }),
    ...WEEKDAY_LETTERS.map((letter) => element("div", "og-wd", { "aria-hidden": "true" }, letter)),
    ...order.flatMap((week) => [element("div", "og-mo", { "aria-hidden": "true" }, months[week]), ...weeks[week].map(dayCell)]),
  );
}

/**
 * The month over each week, oldest first. Both grids name the first week of each month (habit-logic
 * `monthLabels`). P3 also names its top row, the newest week, so its first row always says the month (CG-16).
 */
function weekMonths(weeks, todayKey, newestFirst) {
  const months = weeks.map(() => "");
  for (const { column, month } of monthLabels(todayKey)) months[column - 1] = month;
  const newest = weeks.length - 1;
  if (newestFirst) months[newest] = dayParts(weeks[newest][0].key).month;
  return months;
}

/** A day after today is an empty cell, any other day a button that opens it (named and drawn by `drawOverview`). */
function dayCell(cell) {
  if (cell.future) return element("span", "hc", { "aria-hidden": "true" });
  return dayButton(cell.key, cell.today);
}

/** The day cell of the spec's Contracts, which opens P1 for its day. `syncDayButton` names it and draws its ring. */
function dayButton(key, today) {
  const button = element("button", "hc", { type: "button", "data-key": key, "aria-haspopup": "dialog" });
  if (today) button.setAttribute("aria-current", "date");
  button.append(ringSvg());
  return button;
}

/** A P4 day after today, its number alone in the ring's place and not a control (R39). */
function closedDayCell(day) {
  const svg = ringSvg();
  svg.append(dayNumber(day.day, "c-num dim"));
  const cell = element("span", "hc closed", { "aria-hidden": "true" });
  cell.append(svg);
  return cell;
}

/**
 * The months of `yearMonths(todayKey)`, newest first, as both year views draw them (R33, R39). Each is a
 * `section.month` labelled by its `h3`, whose `div.mgrid` holds the weekday letters, the empty lead cells before the
 * 1st, then one cell per day. A day before the year starts is blank, after today it is `closedCell`, between it is
 * `openCell`.
 * @param {HTMLElement} container div.months
 * @param {string} todayKey
 * @param {{ idPrefix: string, cellClass: string, openCell: Function, closedCell: Function }} cells the id prefix of the
 *   month headings, the class every cell carries, and the two cell makers, each given a habit-logic `YearDay`
 */
function layOutMonths(container, todayKey, { idPrefix, cellClass, openCell, closedCell }) {
  const blankCell = () => element("span", `${cellClass} blank`, { "aria-hidden": "true" });
  const cellOf = { open: openCell, closed: closedCell, empty: blankCell };
  container.replaceChildren(
    ...yearMonths(todayKey).map((month) => {
      const id = monthId(idPrefix, month.key);
      const grid = element("div", "mgrid", { role: "group", "aria-labelledby": id });
      grid.append(
        ...WEEKDAY_LETTERS.map((letter) => element("span", "mwd", { "aria-hidden": "true" }, letter)),
        ...Array.from({ length: month.lead }, () => element("span", `${cellClass} lead`, { "aria-hidden": "true" })),
        ...month.days.map((day) => cellOf[day.kind](day)),
      );
      const section = element("section", "month", { "aria-labelledby": id });
      section.append(element("h3", "", { id }, month.title), grid);
      return section;
    }),
  );
}

/** "mo-2026-9" for September 2026, the month without a leading zero, as the goldens write it. */
function monthId(prefix, monthKey) {
  const [year, month] = monthKey.split("-");
  return `${prefix}-${year}-${Number(month)}`;
}

const laidOutYears = new WeakMap(); // P2's div.months -> { todayKey, beads }, the bead buttons oldest first

/**
 * P2's months for one habit (R33, R34). The layout depends on the day alone, so it is built again only for a new
 * day. Every other render, the next habit's included, updates the beads in place, so a ticked bead stays the same
 * element with its focus, and a bead whose done state changed pops when `animate` is set (R32).
 * @param {HTMLElement} months P2's div.months
 * @param {readonly string[]} done the habit's done date keys
 * @param {string} todayKey
 * @param {boolean} animate
 */
export function drawHabitYear(months, done, todayKey, animate) {
  let laidOut = laidOutYears.get(months);
  if (laidOut?.todayKey !== todayKey) {
    layOutMonths(months, todayKey, { idPrefix: "mo", cellClass: "yc", openCell: beadButton, closedCell: closedBead });
    // Date keys sort as text in calendar order.
    const beads = Array.from(months.querySelectorAll(BEAD)).sort((a, b) => (a.dataset.key < b.dataset.key ? -1 : 1));
    laidOut = { todayKey, beads };
    laidOutYears.set(months, laidOut);
  }
  const doneDays = new Set(done);
  const flags = laidOut.beads.map((button) => doneDays.has(button.dataset.key));
  // The open days run without a gap from yearStart to today, so a bead's neighbours in this list are the day before
  // and the day after. Past either end the flag is undefined, so the oldest day and today join nothing outside (R34).
  laidOut.beads.forEach((button, index) => {
    const on = flags[index];
    const left = on && flags[index - 1] === true;
    const right = on && flags[index + 1] === true;
    syncBead(button, { on, left, right, today: button.dataset.key === todayKey }, animate);
  });
}

/** An open day of P2, named the same whatever its state, which `aria-pressed` carries (system.md, Accessible names). */
function beadButton(day) {
  const button = element("button", "yc", { type: "button", "data-key": day.key, "aria-label": `Mark ${yearDate(day.key)} as done` });
  button.append(beadFace(day.day));
  return button;
}

/** A day after today, its number alone and not a control. */
function closedBead(day) {
  const cell = element("span", "yc closed", { "aria-hidden": "true" });
  cell.append(beadFace(day.day));
  return cell;
}

/** The bead with its number as SVG text, so the figures centre by their ink as a ring's do (rule 6). */
function beadFace(dayNumber) {
  const number = svgElement("text", { x: "50%", y: "50%", dy: ".352em" });
  number.textContent = String(dayNumber);
  const svg = svgElement("svg", { "aria-hidden": "true" });
  svg.append(number);
  const face = element("span", "bead");
  face.append(svg);
  return face;
}

/**
 * A bead's state (R34). Pressed and `on` when done, `l` and `r` for the thread to a done neighbour, `today` with
 * `aria-current`. It pops only when its own done state changed, as f2 draws it, so a neighbour whose thread changed
 * keeps its bead still.
 */
function syncBead(button, { on, left, right, today }, animate) {
  const before = button.getAttribute("aria-pressed");
  const pressed = String(on);
  button.setAttribute("aria-pressed", pressed);
  button.classList.toggle("on", on);
  button.classList.toggle("l", left);
  button.classList.toggle("r", right);
  button.classList.toggle("today", today);
  if (today) button.setAttribute("aria-current", "date");
  flagChange(button, "pop", animate && before !== null && before !== pressed);
}
