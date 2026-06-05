import { readFileSync, writeFileSync } from 'fs';
import xlsx from 'xlsx';

// Same occupancy/turnover/duration analysis as compute_field_survey_metrics.mjs,
// applied to the KomitasCity off-street yard. Its license-plate occupancy log lives
// in the "Off street city" sheet of the survey workbook (Route: Komitas), one row
// per vehicle seen per hourly pass (7:00–23:00, 17 passes). Unlike the on-street
// "United Data" sheet, the hour is given once per block in column 0 as a label
// ("7 - 8") and left blank on the rows beneath it, so it is forward-filled here.

const XLSX_PATH = 'Field Surveys/Parking Survey Sheet v5.xlsx';
const GEOJSON_PATH = 'app/static/data/wgs84/parking-areas.geojson';
const SHEET = 'Off street city';
const SURVEY_WINDOW_HOURS = 17; // 7:00–23:00 inclusive
const FORMAL_CAPACITY = 123; // formal capacity of the off-street city yard (per ANALYSIS sheet)

const wb = xlsx.readFile(XLSX_PATH);
const matrix = xlsx.utils.sheet_to_json(wb.Sheets[SHEET], { header: 1, blankrows: false });
// Header/legend occupy rows 0–5 (Date/Route/Name/column-titles/legend); data from row 6.
const dataRows = matrix.slice(6);

const firstWord = (v) => (v == null ? '' : String(v).trim().split(/\s+|-/)[0].trim());

const plateHours = new Map(); // plate -> Set(hours)
const hourPlates = new Map(); // hour -> Set(plates)
const obs = { total: 0, illegal: 0, offstreet: 0 };
const byType = {};
const byMethod = {};
const byLocation = {};

let curHour = null;
for (const r of dataRows) {
	const timeLabel = r[0];
	if (timeLabel != null) {
		const m = String(timeLabel).match(/\d+/); // "7 - 8" -> 7
		if (m) curHour = parseInt(m[0], 10);
	}
	let plate = r[2];
	const vtype = r[3];
	const location = r[4];
	const method = r[5];
	const legal = r[6];
	if (curHour == null) continue;
	plate = plate == null ? '' : String(plate).trim().toLowerCase(); // same normalization as the on-street script
	if (!plate || plate === '-' || plate === 'none') continue;

	if (!plateHours.has(plate)) plateHours.set(plate, new Set());
	plateHours.get(plate).add(curHour);
	if (!hourPlates.has(curHour)) hourPlates.set(curHour, new Set());
	hourPlates.get(curHour).add(plate);

	obs.total += 1;
	if (firstWord(legal) === 'I') obs.illegal += 1;
	if (firstWord(location) !== 'OS') obs.offstreet += 1; // FP/SB = footpath/setback overflow
	const tk = firstWord(vtype), mk = firstWord(method), lk = firstWord(location);
	byType[tk] = (byType[tk] || 0) + 1;
	byMethod[mk] = (byMethod[mk] || 0) + 1;
	byLocation[lk] = (byLocation[lk] || 0) + 1;
}

function countEvents(hourSet) {
	const hs = [...hourSet].sort((a, b) => a - b);
	let events = hs.length ? 1 : 0;
	for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) events++;
	return events;
}

const round = (n, d = 0) => {
	const m = 10 ** d;
	return Math.round(n * m) / m;
};

let events = 0, durationSum = 0;
const durations = [];
for (const hours of plateHours.values()) {
	events += countEvents(hours);
	durationSum += hours.size;
	durations.push(hours.size);
}
durations.sort((a, b) => a - b);

const uniqueVehicles = plateHours.size;
let peak = 0, peakHour = null;
for (const [hour, plates] of hourPlates) {
	if (plates.size > peak) { peak = plates.size; peakHour = hour; }
}
const avgPresent = durationSum / SURVEY_WINDOW_HOURS;
const median = durations[Math.floor((durations.length - 1) / 2)];
const longTerm = (h) => durations.filter((d) => d >= h).length / uniqueVehicles;
const pct = (n) => round((n / obs.total) * 100, 1);

// Properties written onto the KomitasCity feature, matching the names/rounding the
// on-street field-survey paths carry so the existing map popup renders them identically.
const merged = {
	space: FORMAL_CAPACITY,
	unique_vehicles: uniqueVehicles,
	parking_events: events,
	peak_occupancy: peak,
	peak_hour: peakHour,
	occupancy_pct: round((avgPresent / FORMAL_CAPACITY) * 100),
	turnover: round(events / FORMAL_CAPACITY, 1),
	avg_duration_h: round(durationSum / uniqueVehicles, 1),
	illegal_share: pct(obs.illegal),
	offstreet_share: pct(obs.offstreet), // share parked off the carriageway (FP/SB) — overflow within the yard
};

// Extra descriptive metrics (not on the on-street paths; printed for the report).
const extra = {
	formal_capacity: FORMAL_CAPACITY,
	peak_occupancy_pct: round((peak / FORMAL_CAPACITY) * 100),
	median_duration_h: median,
	parked_8h_plus_pct: round(longTerm(8) * 100, 1),
	parked_12h_plus_pct: round(longTerm(12) * 100, 1),
};

// --- Merge into the KomitasCity feature in parking-areas.geojson ---
const geojson = JSON.parse(readFileSync(GEOJSON_PATH, 'utf8'));
const yard = geojson.features.find((f) => f.properties.name === 'KomitasCity');
if (!yard) throw new Error('KomitasCity feature not found in ' + GEOJSON_PATH);
Object.assign(yard.properties, merged);
writeFileSync(GEOJSON_PATH, JSON.stringify(geojson));

console.log('=== KomitasCity off-street yard — occupancy/turnover analysis ===');
console.log('merged into feature:', merged);
console.log('additional metrics:', extra);
console.log('Written to ' + GEOJSON_PATH);
console.log('\nVehicle type:', byType);
console.log('Parking method:', byMethod);
console.log('Location:', byLocation);
console.log('\nHourly occupancy (distinct plates present):');
for (let h = 7; h <= 23; h++) {
	const n = hourPlates.get(h)?.size || 0;
	const bar = '#'.repeat(Math.round((n / FORMAL_CAPACITY) * 40));
	console.log(`  ${String(h).padStart(2)}:00  ${String(n).padStart(3)}  ${round((n / FORMAL_CAPACITY) * 100)}%  ${bar}`);
}

console.log('\n--- cross-check vs ANALYSIS sheet (821 uniq, 906 events, 1.43 avg, 7.37 turnover) ---');
