/**
 * The geometry of a ring and of the legend (spec R42, Ring contract).
 * A ring shows one segment per habit on a 40 unit box, so the view modules draw every ring of the band, P3, P4,
 * P1 and the Overview button from these two functions. Pure, with no page access and no clock, so the unit tests
 * prove the arcs character for character against the goldens' own path data.
 */

const CENTRE = 20;
const RADIUS = 15;
const MAX_GAP_DEGREES = 22;
const GAP_SHARE_OF_STEP = 0.3;

const twoDecimals = (value) => Math.round(value * 100) / 100;

/** "x y" of the point `degrees` clockwise from 12 o'clock on the ring, each rounded to 2 decimals. */
function pointAt(degrees) {
  const radians = (degrees * Math.PI) / 180;
  return `${twoDecimals(CENTRE + RADIUS * Math.sin(radians))} ${twoDecimals(CENTRE - RADIUS * Math.cos(radians))}`;
}

/**
 * The path data of segment `i` (0 to n - 1) of a ring of `n` habits, `n` 2 or more. Segments run clockwise from
 * 12 o'clock with a gap between neighbours, so each habit's arc reads on its own.
 * For example arcPath(0, 3) is "M22.86 5.28A15 15 0 0 1 34.18 24.88".
 */
export function arcPath(i, n) {
  const step = 360 / n;
  const gap = Math.min(MAX_GAP_DEGREES, GAP_SHARE_OF_STEP * step);
  const largeArc = step - gap > 180 ? 1 : 0;
  return `M${pointAt(i * step + gap / 2)}A${RADIUS} ${RADIUS} 0 ${largeArc} 1 ${pointAt((i + 1) * step - gap / 2)}`;
}

/**
 * How many segments are on in each legend ring for `n` habits, between "None" and "All". The distinct values of
 * none, a third, two thirds and all, in that order, so [0] for 0 habits and [0, 4, 8, 12] for 12.
 */
export function legendCounts(n) {
  return [...new Set([0, Math.ceil(n / 3), Math.ceil((2 * n) / 3), n])];
}
