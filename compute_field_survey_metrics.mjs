import { readFileSync, writeFileSync } from 'fs';
import xlsx from 'xlsx';

// Merge per-zone occupancy survey metrics into field-surveys.geojson + the two
// off-street yards, and pre-compute the per-area dashboard stat blocks the Field
// Surveys story step shows as the reader zooms between neighbourhoods.
//
// Two source workbooks, one per surveyed area, both with a "United Data" sheet — a
// license-plate occupancy log where each row is one vehicle seen in one zone at one
// hour. The license plate reconstructs each vehicle's duration and a zone's
// turnover; the zone number joins 1:1 to the survey paths' `zone` property. Formal
// (striped) capacity comes from the geojson `space` field, so occupancy/turnover
// are measured against the legal supply already on the map.
//   • Komitas          — Parking Survey Sheet v5  (zones 70–122, 7:00–23:00)
//                         off-street log labelled "Off street city" → KomitasCity yard
//   • Shiraz/Hasratyan — Shiraz, Hasratyan - Analysis (zones 123–156, 7:00–24:00)
//                         off-street log labelled "Shiraz off-street" → ShirazYard010

const GEOJSON_PATH = 'app/static/data/wgs84/field-surveys.geojson';
const YARDS_PATH = 'app/static/data/wgs84/field-survey-yards.geojson';

// Each source's United Data sheet, the area it feeds, and the off-street log label
// that maps to that area's yard.
const SOURCES = [
	{ area: 'komitas', file: 'Field Surveys/Parking Survey Sheet v5.xlsx', offLabel: 'Off street city', yard: 'KomitasCity' },
	{ area: 'shiraz', file: 'Field Surveys/Shiraz, Hasratyan - Analysis.xlsx', offLabel: 'Shiraz off-street', yard: 'ShirazYard010' },
];

const firstWord = (v) => (v == null ? '' : String(v).trim().split(/\s+/)[0]);
const round = (n, d = 0) => { const m = 10 ** d; return Math.round(n * m) / m; };

// A "parking event" is one contiguous run of hours a plate is present (a gap of >1
// hour means the space was vacated and re-used). Turnover counts these events.
function countEvents(hourSet) {
	const hs = [...hourSet].sort((a, b) => a - b);
	let events = hs.length ? 1 : 0;
	for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) events++;
	return events;
}

// Parse one workbook's United Data into per-zone presence/turnover structures plus
// a per-zone observation tally (total / illegal / off-carriageway). `offLabel` rows
// are collected separately as the area's off-street yard. Returns the survey window
// (distinct hours observed) so occupancy is averaged over the right denominator.
function parseUnitedData(file, offLabel) {
	const ws = xlsx.readFile(file).Sheets['United Data'];
	const matrix = xlsx.utils.sheet_to_json(ws, { header: 1, blankrows: false });
	const dataRows = matrix.slice(2); // drop the two header rows

	// keyed by zone number (or the offLabel string for the yard)
	const plateHours = new Map();   // key -> plate -> Set(hours)
	const hourPlates = new Map();   // key -> hour -> Set(plates)
	const obs = new Map();          // key -> { total, illegal, offstreet }
	const windowHours = new Set();  // distinct on-street survey hours

	for (const r of dataRows) {
		const time = r[0];
		let zone = r[1];
		let plate = r[2];
		const location = r[4];
		const legal = r[6];
		if (typeof time !== 'number') continue;

		let key;
		if (typeof zone === 'number') {
			key = zone;
			windowHours.add(time);
		} else if (typeof zone === 'string' && zone.trim() === offLabel) {
			key = offLabel; // the off-street yard log
		} else {
			continue; // stray / unrelated rows
		}

		plate = plate == null ? '' : String(plate).trim().toLowerCase();
		if (!plate || plate === '-' || plate === 'none') continue;

		if (!plateHours.has(key)) plateHours.set(key, new Map());
		if (!hourPlates.has(key)) hourPlates.set(key, new Map());
		if (!obs.has(key)) obs.set(key, { total: 0, illegal: 0, offstreet: 0 });

		const ph = plateHours.get(key);
		if (!ph.has(plate)) ph.set(plate, new Set());
		ph.get(plate).add(time);

		const hp = hourPlates.get(key);
		if (!hp.has(time)) hp.set(time, new Set());
		hp.get(time).add(plate);

		const o = obs.get(key);
		o.total += 1;
		if (firstWord(legal) === 'I') o.illegal += 1;
		// Location OS = On-Street (on the carriageway); FP/SB = footpath/setback overflow.
		if (firstWord(location) !== 'OS') o.offstreet += 1;
	}

	return { plateHours, hourPlates, obs, window: windowHours.size };
}

const sources = {};
for (const s of SOURCES) sources[s.area] = { ...s, ...parseUnitedData(s.file, s.offLabel) };

// Compute the occupancy/turnover/duration metrics for one survey key (zone number
// or yard label) against a given formal capacity, using its source's window.
function metricsFor(src, key, cap) {
	const ph = src.plateHours.get(key);
	if (!ph) return null;
	let events = 0, durationSum = 0;
	for (const hours of ph.values()) { events += countEvents(hours); durationSum += hours.size; }
	let peak = 0, peakHour = null;
	for (const [hour, plates] of src.hourPlates.get(key)) {
		if (plates.size > peak) { peak = plates.size; peakHour = hour; }
	}
	const o = src.obs.get(key);
	// Average occupancy = mean vehicles present across the window, as a share of
	// legal (striped) capacity. durationSum is total vehicle-hours; ÷ window gives
	// average vehicles present, ÷ capacity the occupancy. >100% = chronic overflow.
	const avgPresent = durationSum / src.window;
	return {
		unique_vehicles: ph.size,
		parking_events: events,
		peak_occupancy: peak,
		peak_hour: peakHour,
		occupancy_pct: cap ? round((avgPresent / cap) * 100) : null,
		turnover: cap ? round(events / cap, 1) : null,
		avg_duration_h: round(durationSum / ph.size, 1),
		illegal_share: round((o.illegal / o.total) * 100, 1),
		offstreet_share: round((o.offstreet / o.total) * 100, 1),
		_obs: o,
	};
}

// --- Stamp the on-street survey paths ---
const geojson = JSON.parse(readFileSync(GEOJSON_PATH, 'utf8'));
let matched = 0;
const missing = [];
for (const f of geojson.features) {
	const src = sources[f.properties.area];
	const m = src && metricsFor(src, f.properties.zone, f.properties.space || 0);
	if (!m) { missing.push(f.properties.zone); continue; }
	matched++;
	delete m._obs;
	Object.assign(f.properties, m);
}

// --- Stamp the off-street yards ---
const yards = JSON.parse(readFileSync(YARDS_PATH, 'utf8'));
for (const y of yards.features) {
	const src = sources[y.properties.area];
	if (!src) continue;
	const m = metricsFor(src, src.offLabel, y.properties.space || 0);
	if (!m) continue;
	delete m._obs;
	Object.assign(y.properties, m);
}
const yardByArea = {};
for (const y of yards.features) yardByArea[y.properties.area] = y.properties;

// --- Per-area dashboard stat blocks (occupancy / paidfree / retained) ---
// One block per area plus a combined "all" view shown when zoomed out far enough to
// see both neighbourhoods. Labels/colors mirror the Field Surveys story cards.
const mean = (arr) => (arr.length ? arr.reduce((s, x) => s + x, 0) / arr.length : 0);

function statsForArea(areaKey) {
	const fs = areaKey === 'all'
		? geojson.features
		: geojson.features.filter(f => f.properties.area === areaKey);
	const occ = fs.map(f => f.properties.occupancy_pct).filter(v => v != null);

	// Off-carriageway share, volume-weighted across the area's zones (matches the
	// share a reader would get from the raw observation counts).
	let offObs = 0, totObs = 0;
	for (const f of fs) {
		const src = sources[f.properties.area];
		const o = src?.obs.get(f.properties.zone);
		if (o) { offObs += o.offstreet; totObs += o.total; }
	}

	const white = fs.filter(f => f.properties.regulation === 'white').reduce((s, f) => s + (f.properties.space || 0), 0);
	const blue = fs.filter(f => f.properties.regulation === 'blue').reduce((s, f) => s + (f.properties.space || 0), 0);

	const retainedSpaces = fs.filter(f => f.properties.retained === 'retained').reduce((s, f) => s + (f.properties.space || 0), 0);
	const removedSpaces = fs.filter(f => f.properties.retained === 'removed').reduce((s, f) => s + (f.properties.space || 0), 0);
	const retainedPaths = fs.filter(f => f.properties.retained === 'retained').length;
	const totalRetSpaces = retainedSpaces + removedSpaces;

	const yardSpaces = areaKey === 'all'
		? yards.features.reduce((s, y) => s + (y.properties.space || 0), 0)
		: (yardByArea[areaKey]?.space || 0);
	const yardLabel = areaKey === 'shiraz' ? 'ShirazYard010 Yard'
		: areaKey === 'komitas' ? 'KomitasCity Yard'
		: 'Off-Street Yards';

	return {
		occupancy: [
			{ value: round(mean(occ)), label: 'Mean Occupancy %', color: '#2ecc71' },
			{ value: occ.filter(v => v > 100).length, label: 'Zones Over Capacity', color: '#ff1f44' },
			{ value: occ.filter(v => v < 50).length, label: 'Zones Under 50% (slack)', color: '#cddc39' },
			{ value: totObs ? round((offObs / totObs) * 100) : 0, label: 'Parked Off-Carriageway %', color: '#00e5ff' },
		],
		paidfree: [
			{ value: fs.length, label: 'Survey Paths', color: '#00e5ff' },
			{ value: white, label: 'White Spaces', color: '#ffffff' },
			{ value: blue, label: 'Blue Spaces', color: '#42a5f5' },
			{ value: yardSpaces, label: yardLabel, color: '#7c4dff' },
		],
		retained: [
			{ value: retainedSpaces, label: 'Retained Spaces', color: '#4CAF50' },
			{ value: removedSpaces, label: 'Removed Spaces', color: '#EF5350' },
			{ value: totalRetSpaces ? round((retainedSpaces / totalRetSpaces) * 100) : 0, label: '% Spaces Retained', color: '#4CAF50' },
			{ value: retainedPaths, label: 'Retained Paths', color: '#00e5ff' },
		],
	};
}

const areaStats = { all: statsForArea('all'), komitas: statsForArea('komitas'), shiraz: statsForArea('shiraz') };
geojson.areaStats = areaStats;

writeFileSync(GEOJSON_PATH, JSON.stringify(geojson));
writeFileSync(YARDS_PATH, JSON.stringify(yards));

// --- Report ---
console.log(`Survey paths: ${geojson.features.length}  matched to survey data: ${matched}`);
if (missing.length) console.log(`No survey rows for zones: ${missing.join(', ')}`);
for (const area of ['komitas', 'shiraz', 'all']) {
	const o = areaStats[area].occupancy;
	console.log(`[${area}] mean occ ${o[0].value}%  over-cap ${o[1].value}  under-50 ${o[2].value}  off-carriageway ${o[3].value}%`);
}
for (const y of yards.features) {
	console.log(`Yard ${y.properties.name}: cap ${y.properties.space}  occupancy ${y.properties.occupancy_pct}%  (${y.properties.unique_vehicles} vehicles)`);
}
console.log(`Windows — komitas: ${sources.komitas.window}h, shiraz: ${sources.shiraz.window}h`);
console.log(`Written ${GEOJSON_PATH} and ${YARDS_PATH}`);
