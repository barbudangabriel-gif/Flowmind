// utils/date.js
import { isNyseHolidayNY } from './nyseHoliday';

export function isThirdFridayNY(iso) {
 const d = new Date(iso + 'T00:00:00');
 const wd = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'short' })
 .format(d);
 const day = +new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', day: '2-digit' })
 .format(d);
 return wd === 'Fri' && day >= 15 && day <= 21;
}

// Markăm OPEX pe vineri; dacă e holiday, marcăm joia dinainte.
export function isMonthlyOpexNY(iso) {
 if (isThirdFridayNY(iso) && !isNyseHolidayNY(iso)) return true;
 
 // Thursday-before if Friday holiday
 const d = new Date(iso + 'T00:00:00');
 if (isThirdFridayNY(iso) && isNyseHolidayNY(iso)) {
 // Check if the day before (Thursday) should be marked
 const thu = new Date(d);
 thu.setDate(thu.getDate() - 1);
 const thuIso = thu.toISOString().slice(0, 10);
 const thuw = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'short' }).format(thu);
 const thuday = +new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', day: '2-digit' }).format(thu);
 
 // Thu between 14-20 is the "observed" OPEX trading day
 if (thuw === 'Thu' && thuday >= 14 && thuday <= 20) {
 return iso === thuIso; // mark only that Thursday date
 }
 }
 return false;
}