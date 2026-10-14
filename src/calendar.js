/**
 * The rings and the day grids (spec R35, R38, R42, Contracts "Files").
 * Why: a day must read the same wherever it shows (system.md principle 1), so every ring (the band, P3, P4, P1's
 * mini ring, the Overview button) and every legend is drawn here from habit-logic's cells and done flags.
 * Input: cells, flags and date keys, never a clock or storage. Output: new elements, and changes to the containers
 * it is given. It registers no event listener. As the lowest DOM module it also owns the two element factories the
 * other view modules share. Data reaches the DOM only through textContent and setAttribute (R24).
 */
import { dayParts, shortDate } from "./dates.js";
import { monthLabels } from "./habits.js";
import { arcPath, legendCounts } from "./ring.js";

const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const RING_CENTRE = "20";
const SEGMENT_RADIUS = "15";
const TODAY_RADIUS = "19.2";
const CORE_RADIUS = "11.5";
const WEEKDAY_LETTERS = ["M", "T", "W", "T", "F", "S", "S"];
const DAYS_PER_WEEK = 7;

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
  if (day !== undefined) parts.push(dayNumber(day, full));
  return parts;
}

/** SVG text on the baseline at the ring's centre, dropped .352em, so the figures centre by their ink (rule 6). */
function dayNumber(day, onCore) {
  const text = svgElement("text", { class: onCore ? "c-num on" : "c-num", x: RING_CENTRE, y: RING_CENTRE, dy: ".352em" });
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

const laidOutFor = new WeakMap(); // overview grid -> the today key its weeks were laid out for

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
  for (const button of grid.querySelectorAll("button.hc")) {
    const cell = cellOf.get(button.getAttribute("data-key"));
    button.setAttribute("aria-label", `${shortDate(cell.key)}, ${cell.count} of ${cell.total} habits`);
    const changed = drawRing(button.firstElementChild, cell.done, { today: cell.today, day: dayParts(cell.key).day });
    flagChange(button, "pop", animate && changed);
  }
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
  const button = element("button", "hc", { type: "button", "data-key": cell.key, "aria-haspopup": "dialog" });
  if (cell.today) button.setAttribute("aria-current", "date");
  button.append(ringSvg());
  return button;
}
