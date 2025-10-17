// utils/nyseHoliday.js
const tz = 'America/New_York';
const dISO = (d) =>
 new Intl.DateTimeFormat('en-CA', { timeZone: tz, dateStyle: 'short' })
 .format(d)
 .replace(/\//g, '-');

function nthDowOfMonth(year, month0, dow, n) {
 // month0: 0..11, dow: 0=Sun..6=Sat, n>=1
 const d = new Date(Date.UTC(year, month0, 1));
 const add = (7 + dow - d.getUTCDay()) % 7;
 d.setUTCDate(1 + add + 7 * (n - 1));
 return d;
}

function lastDowOfMonth(year, month0, dow) {
 const d = new Date(Date.UTC(year, month0 + 1, 0)); // last day
 const sub = (7 + d.getUTCDay() - dow) % 7;
 d.setUTCDate(d.getUTCDate() - sub);
 return d;
}

// Meeus/Jones/Butcher – Easter Sunday (Gregorian), then Good Friday = -2 days
function easterSundayUTC(year) {
 const a = year % 19, b = Math.floor(year / 100), c = year % 100;
 const d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25);
 const g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30;
 const i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7;
 const m = Math.floor((a + 11 * h + 22 * l) / 451);
 const month = Math.floor((h + l - 7 * m + 114) / 31) - 1; // 0=Jan
 const day = ((h + l - 7 * m + 114) % 31) + 1;
 return new Date(Date.UTC(year, month, day));
}

export function isNyseHolidayNY(iso) {
 // iso: 'YYYY-MM-DD' interpreted in New York
 const d = new Date(iso + 'T12:00:00'); // noon avoids DST edgecases
 const y = d.getUTCFullYear();

 // Fixed-date with observed rules (Mon if Sun, Fri if Sat)
 const observe = (month0, day) => {
 const base = new Date(Date.UTC(y, month0, day));
 const wd = base.getUTCDay();
 if (wd === 0) base.setUTCDate(day + 1); // Sunday -> Monday
 else if (wd === 6) base.setUTCDate(day - 1); // Saturday -> Friday
 return dISO(base);
 };

 const set = new Set();

 // New Year's Day
 set.add(observe(0, 1));
 // Martin Luther King Jr. Day – 3rd Monday in Jan
 set.add(dISO(nthDowOfMonth(y, 0, 1, 3)));
 // Presidents' Day – 3rd Monday in Feb
 set.add(dISO(nthDowOfMonth(y, 1, 1, 3)));
 // Good Friday – 2 days before Easter
 const gf = easterSundayUTC(y); 
 gf.setUTCDate(gf.getUTCDate() - 2);
 set.add(dISO(gf));
 // Memorial Day – last Monday in May
 set.add(dISO(lastDowOfMonth(y, 4, 1)));
 // Juneteenth – June 19 (observed)
 set.add(observe(5, 19));
 // Independence Day – July 4 (observed)
 set.add(observe(6, 4));
 // Labor Day – 1st Monday in Sep
 set.add(dISO(nthDowOfMonth(y, 8, 1, 1)));
 // Thanksgiving – 4th Thursday in Nov
 set.add(dISO(nthDowOfMonth(y, 10, 4, 4)));
 // Christmas – Dec 25 (observed)
 set.add(observe(11, 25));

 return set.has(iso);
}