import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { localDateKey, isDateKey, addDays, dayParts, shortDate, longDate } from "../src/dates.js";

const KUALA_LUMPUR = "Asia/Kuala_Lumpur";
const NEW_YORK = "America/New_York";

// Zone cases must build their Date inside the zone, so the zone is set and restored around the body.
function inZone(zone, run) {
  const before = process.env.TZ;
  process.env.TZ = zone;
  try {
    return run();
  } finally {
    if (before === undefined) delete process.env.TZ;
    else process.env.TZ = before;
  }
}

const pad = (number, width) => String(number).padStart(width, "0");

// An independent reference: UTC millisecond maths, safe because UTC has no DST.
function utcKey(ms) {
  const date = new Date(ms);
  return `${pad(date.getUTCFullYear(), 4)}-${pad(date.getUTCMonth() + 1, 2)}-${pad(date.getUTCDate(), 2)}`;
}

const DAY_MS = 86_400_000;

test("@R1 @R3 the zone switch is real, so the zone cases are not vacuous", () => {
  assert.equal(inZone(KUALA_LUMPUR, () => new Date(2026, 9, 8, 12).getTimezoneOffset()), -480);
  assert.equal(inZone(NEW_YORK, () => new Date(2026, 9, 8, 12).getTimezoneOffset()), 240);
  assert.equal(inZone(NEW_YORK, () => new Date(2026, 11, 8, 12).getTimezoneOffset()), 300);
});

test("@R1 the local calendar day of an instant", () => {
  const rows = [
    [KUALA_LUMPUR, () => new Date(2026, 9, 8, 0, 0, 0, 0), "2026-10-08"],
    [KUALA_LUMPUR, () => new Date(2026, 9, 8, 23, 59, 59, 999), "2026-10-08"],
    [KUALA_LUMPUR, () => new Date(2027, 0, 1), "2027-01-01"],
    [KUALA_LUMPUR, () => new Date("2026-10-07T16:30:00Z"), "2026-10-08"],
    [NEW_YORK, () => new Date(2026, 2, 8, 3, 30), "2026-03-08"],
    [NEW_YORK, () => new Date(2026, 10, 1, 1, 30), "2026-11-01"],
  ];
  for (const [zone, makeDate, key] of rows) {
    assert.equal(
      inZone(zone, () => localDateKey(makeDate())),
      key,
      `${zone} ${key}`,
    );
  }
});

test("@R1 the UTC date is not used: 00:30 local in Kuala Lumpur is still the day before in UTC", () => {
  const instant = inZone(KUALA_LUMPUR, () => new Date(2026, 9, 8, 0, 30));
  assert.equal(instant.toISOString().slice(0, 10), "2026-10-07");
  assert.equal(inZone(KUALA_LUMPUR, () => localDateKey(instant)), "2026-10-08");
});

test("@R1 month and day are zero padded and the year has 4 digits", () => {
  assert.equal(inZone(KUALA_LUMPUR, () => localDateKey(new Date(2026, 0, 5))), "2026-01-05");
  assert.equal(inZone(KUALA_LUMPUR, () => localDateKey(new Date(2026, 11, 31))), "2026-12-31");
});

test("@R2 valid and invalid date keys", () => {
  const rows = [
    ["2026-10-08", true],
    ["2028-02-29", true],
    ["2000-02-29", true],
    ["2026-12-31", true],
    ["0001-01-01", true],
    ["2026-02-29", false],
    ["2100-02-29", false],
    ["2026-13-01", false],
    ["2026-00-10", false],
    ["2026-04-31", false],
    ["2026-1-1", false],
    ["2026-10-08T00:00", false],
    [" 2026-10-08", false],
    ["2026-10-08 ", false],
    ["2026-10-08\n", false],
    ["2026-10-00", false],
    ["2026-10-32", false],
    ["0000-01-01", false],
    ["", false],
    ["２０２６-10-08", false],
    [20261008, false],
    [null, false],
    [undefined, false],
    [{}, false],
    [[], false],
    [new String("2026-10-08"), false],
  ];
  for (const [value, expected] of rows) {
    assert.equal(isDateKey(value), expected, `isDateKey(${JSON.stringify(value)})`);
  }
});

test("@R2 agrees with a calendar reference for every year-month-day combination 1900 to 2100", () => {
  for (let year = 1900; year <= 2100; year++) {
    for (let month = 1; month <= 12; month++) {
      for (let day = 0; day <= 32; day++) {
        const key = `${pad(year, 4)}-${pad(month, 2)}-${pad(day, 2)}`;
        const real = day >= 1 && new Date(Date.UTC(year, month - 1, day)).getUTCDate() === day;
        assert.equal(isDateKey(key), real, key);
      }
    }
  }
});

test("@R2 a long hostile string is rejected quickly", () => {
  const started = performance.now();
  assert.equal(isDateKey("2026-10-0" + "8".repeat(1_000_000)), false);
  assert.equal(isDateKey("1".repeat(1_000_000)), false);
  assert.ok(performance.now() - started < 1000);
});

test("@R3 calendar arithmetic that ignores the time zone", () => {
  const rows = [
    [KUALA_LUMPUR, "2026-10-08", -6, "2026-10-02"],
    [KUALA_LUMPUR, "2026-12-31", 1, "2027-01-01"],
    [KUALA_LUMPUR, "2028-02-28", 1, "2028-02-29"],
    [KUALA_LUMPUR, "2026-02-28", 1, "2026-03-01"],
    [KUALA_LUMPUR, "2026-07-20", 83, "2026-10-11"],
    [KUALA_LUMPUR, "2026-10-05", -77, "2026-07-20"],
    [NEW_YORK, "2026-03-07", 1, "2026-03-08"],
    [NEW_YORK, "2026-03-08", 1, "2026-03-09"],
    [NEW_YORK, "2026-11-01", 1, "2026-11-02"],
    [NEW_YORK, "2026-11-02", -1, "2026-11-01"],
    [NEW_YORK, "2026-03-09", -2, "2026-03-07"],
  ];
  for (const [zone, key, days, expected] of rows) {
    assert.equal(
      inZone(zone, () => addDays(key, days)),
      expected,
      `${zone} ${key} ${days}`,
    );
  }
});

test("@R3 century and year edges", () => {
  assert.equal(addDays("2000-02-28", 1), "2000-02-29");
  assert.equal(addDays("2100-02-28", 1), "2100-03-01");
  assert.equal(addDays("2026-01-01", -1), "2025-12-31");
  assert.equal(addDays("2026-10-08", 0), "2026-10-08");
  assert.equal(addDays("0001-01-01", 1), "0001-01-02");
  assert.equal(addDays("2026-10-08", 366), "2027-10-09");
});

test("@R3 agrees with UTC reference maths for every day 1900 to 2100 in both zones", () => {
  for (const zone of [KUALA_LUMPUR, NEW_YORK]) {
    inZone(zone, () => {
      for (let ms = Date.UTC(1900, 0, 1); ms <= Date.UTC(2100, 11, 31); ms += DAY_MS) {
        const key = utcKey(ms);
        assert.equal(addDays(key, 1), utcKey(ms + DAY_MS), `${zone} ${key} +1`);
        assert.equal(addDays(key, -1), utcKey(ms - DAY_MS), `${zone} ${key} -1`);
        assert.equal(addDays(key, 400), utcKey(ms + 400 * DAY_MS), `${zone} ${key} +400`);
      }
    });
  }
});

test("@R4 short weekday, day and month for every weekday", () => {
  const rows = [
    ["2026-10-05", "Mon", 5, "Oct", "Mon 5 Oct"],
    ["2026-10-06", "Tue", 6, "Oct", "Tue 6 Oct"],
    ["2026-10-07", "Wed", 7, "Oct", "Wed 7 Oct"],
    ["2026-10-08", "Thu", 8, "Oct", "Thu 8 Oct"],
    ["2026-10-09", "Fri", 9, "Oct", "Fri 9 Oct"],
    ["2026-10-10", "Sat", 10, "Oct", "Sat 10 Oct"],
    ["2026-10-11", "Sun", 11, "Oct", "Sun 11 Oct"],
    ["2026-07-20", "Mon", 20, "Jul", "Mon 20 Jul"],
    ["2026-08-01", "Sat", 1, "Aug", "Sat 1 Aug"],
  ];
  for (const [key, weekday, day, month, short] of rows) {
    assert.deepEqual(dayParts(key), { weekday, day, month }, key);
    assert.equal(shortDate(key), short, key);
  }
});

test("@R4 short and long month names for every month", () => {
  const rows = [
    ["2026-01-15", "Jan", "Thursday 15 January"],
    ["2026-02-15", "Feb", "Sunday 15 February"],
    ["2026-03-15", "Mar", "Sunday 15 March"],
    ["2026-04-15", "Apr", "Wednesday 15 April"],
    ["2026-05-15", "May", "Friday 15 May"],
    ["2026-06-15", "Jun", "Monday 15 June"],
    ["2026-07-15", "Jul", "Wednesday 15 July"],
    ["2026-08-15", "Aug", "Saturday 15 August"],
    ["2026-09-15", "Sep", "Tuesday 15 September"],
    ["2026-10-15", "Oct", "Thursday 15 October"],
    ["2026-11-15", "Nov", "Sunday 15 November"],
    ["2026-12-15", "Dec", "Tuesday 15 December"],
    ["2026-10-08", "Oct", "Thursday 8 October"],
    ["2027-01-01", "Jan", "Friday 1 January"],
  ];
  for (const [key, month, long] of rows) {
    assert.equal(dayParts(key).month, month, key);
    assert.equal(longDate(key), long, key);
  }
});

test("@R4 weekday names agree with a UTC reference for every day 1900 to 2100", () => {
  const names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  for (let ms = Date.UTC(1900, 0, 1); ms <= Date.UTC(2100, 11, 31); ms += DAY_MS) {
    assert.equal(dayParts(utcKey(ms)).weekday, names[new Date(ms).getUTCDay()], utcKey(ms));
  }
});

test("@R4 labels do not follow the runtime locale", () => {
  // A child process, because ICU reads LANG once at start-up and an in-process change would prove nothing.
  const datesUrl = new URL("../src/dates.js", import.meta.url).href;
  const program = `
    const { longDate, shortDate } = await import(${JSON.stringify(datesUrl)});
    process.stdout.write(JSON.stringify([longDate("2026-10-08"), shortDate("2026-10-06")]));
  `;
  const output = execFileSync(process.execPath, ["--input-type=module", "--eval", program], {
    env: { ...process.env, LANG: "de_DE.UTF-8", LC_ALL: "de_DE.UTF-8" },
    encoding: "utf8",
    timeout: 15_000,
  });
  assert.deepEqual(JSON.parse(output), ["Thursday 8 October", "Tue 6 Oct"]);
});
