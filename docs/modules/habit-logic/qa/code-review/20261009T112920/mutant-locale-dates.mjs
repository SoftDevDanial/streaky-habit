// Mutant of src/dates.js labels: reads the runtime locale. Used only to test whether the R4 locale test can go red.
export function longDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return `${date.toLocaleDateString(undefined, { weekday: "long" })} ${d} ${date.toLocaleDateString(undefined, { month: "long" })}`;
}
export function shortDate(key) {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return `${date.toLocaleDateString(undefined, { weekday: "short" })} ${d} ${date.toLocaleDateString(undefined, { month: "short" })}`;
}
