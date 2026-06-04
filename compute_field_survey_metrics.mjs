import { readFileSync, writeFileSync } from 'fs';
import xlsx from 'xlsx';

// Merge per-zone occupancy survey metrics into field-surveys.geojson.
//
// Source: "Field Surveys/Parking Survey Sheet v5.xlsx", sheet "United Data" — a
// license-plate occupancy log where each row is one vehicle seen in one zone at
// one hour (7:00–23:00, 17 hourly passes on 2026-05-29). The license plate lets
// us reconstruct each vehicle's duration and a zone's turnover; the zone number
// joins 1:1 to the survey paths' `zone` property. Formal (striped) capacity comes
// from the geojson `space` field, so occupancy/turnover are measured against the
// legal supply already on the map.

const XLSX_PATH = 'Field Surveys/Parking Survey Sheet v5.xlsx';
const GEOJSON_PATH = 'app/static/data/wgs84/field-surveys.geojson';
const SURVEY_WINDOW_HOURS = 17; // 7:00–23:00 inclusive (17 hourly passes)

const wb = xlsx.readFile(XLSX_PATH);
const ws = wb.Sheets['United Data'];
// Header rows occupy the first two rows; data starts at row 3. Read as a matrix
// and key by position to avoid depending on the multi-line header labels.
const matrix = xlsx.utils.sheet_to_json(ws, { header: 1, blankrows: false });
const dataRows = matrix.slice(2); // drop the two header rows

// Column order in "United Data": Time, Zone, License, VehicleType, Location, Method, Legal/Illegal
const firstWord = (v) => (v == null ? '' : String(v).trim().split(/\s+/)[0]);

// zone -> plate -> Set(hours);  zone -> hour -> Set(plates)
const zonePlateHours = new Map();
const zoneHourPlates = new Map();
const zoneObs = new Map(); // zone -> { total, illegal, offstreet }

for (const r of dataRows) {
	const time = r[0];
	const zone = r[1];
	let plate = r[2];
	const location = r[4];
	const legal = r[6];
	if (typeof time !== 'number' || zone == null) continue; // skip blanks / non-hour rows
	if (typeof zone !== 'number') continue; // skip "Off street city" — handled separately, not a survey path
	plate = plate == null ? '' : String(plate).trim().toLowerCase();
	if (!plate || plate === '-' || plate === 'none') continue;

	if (!zonePlateHours.has(zone)) zonePlateHours.set(zone, new Map());
	if (!zoneHourPlates.has(zone)) zoneHourPlates.set(zone, new Map());
	if (!zoneObs.has(zone)) zoneObs.set(zone, { total: 0, illegal: 0, offstreet: 0 });

	const ph = zonePlateHours.get(zone);
	if (!ph.has(plate)) ph.set(plate, new Set());
	ph.get(plate).add(time);

	const hp = zoneHourPlates.get(zone);
	if (!hp.has(time)) hp.set(time, new Set());
	hp.get(time).add(plate);

	const o = zoneObs.get(zone);
	o.total += 1;
	if (firstWord(legal) === 'I') o.illegal += 1;
	// Location OS = On-Street (on the carriageway); FP/SB = footpath/setback overflow.
	if (firstWord(location) !== 'OS') o.offstreet += 1;
}

// A "parking event" is one contiguous run of hours a plate is present (a gap of
// >1 hour means the space was vacated and re-used). Turnover counts these events.
function countEvents(hourSet) {
	const hs = [...hourSet].sort((a, b) => a - b);
	let events = hs.length ? 1 : 0;
	for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) events++;
	return events;
}

const geojson = JSON.parse(readFileSync(GEOJSON_PATH, 'utf8'));
let matched = 0;
const missing = [];

for (const f of geojson.features) {
	const zone = f.properties.zone;
	const ph = zonePlateHours.get(zone);
	if (!ph) {
		missing.push(zone);
		continue;
	}
	matched++;
	const cap = f.properties.space || 0;
	const uniqueVehicles = ph.size;
	let events = 0;
	let durationSum = 0;
	for (const hours of ph.values()) {
		events += countEvents(hours);
		durationSum += hours.size; // hours present == hours parked
	}
	// Peak occupancy = the most vehicles present in any single hour.
	const hp = zoneHourPlates.get(zone);
	let peak = 0;
	let peakHour = null;
	for (const [hour, plates] of hp) {
		if (plates.size > peak) {
			peak = plates.size;
			peakHour = hour;
		}
	}
	const o = zoneObs.get(zone);

	const round = (n, d = 0) => {
		const m = 10 ** d;
		return Math.round(n * m) / m;
	};

	// Average occupancy = mean number of vehicles present across the survey
	// window, as a share of legal (striped) capacity. durationSum is the zone's
	// total vehicle-hours; ÷ window gives average vehicles present, ÷ capacity
	// the occupancy. Spreading each car's hours across the day means within-hour
	// turnover no longer inflates the figure (a quick-churn car counts as its 1
	// hour, not as occupying a space all day). >100% = chronic overflow: on
	// average more cars parked than legal spaces, the surplus on footpaths/setbacks.
	const avgPresent = durationSum / SURVEY_WINDOW_HOURS;

	Object.assign(f.properties, {
		unique_vehicles: uniqueVehicles,
		parking_events: events,
		peak_occupancy: peak, // most distinct plates in any one hour (throughput, kept for reference)
		peak_hour: peakHour,
		occupancy_pct: cap ? round((avgPresent / cap) * 100) : null,
		turnover: cap ? round(events / cap, 1) : null,
		avg_duration_h: round(durationSum / uniqueVehicles, 1),
		illegal_share: round((o.illegal / o.total) * 100, 1),
		offstreet_share: round((o.offstreet / o.total) * 100, 1),
	});
}

writeFileSync(GEOJSON_PATH, JSON.stringify(geojson));

// --- Report ---
const withOcc = geojson.features.filter((f) => f.properties.occupancy_pct != null);
const mean = (arr) => arr.reduce((s, x) => s + x, 0) / arr.length;
const occVals = withOcc.map((f) => f.properties.occupancy_pct);
console.log(`Survey paths: ${geojson.features.length}  matched to survey data: ${matched}`);
if (missing.length) console.log(`No survey rows for zones: ${missing.join(', ')}`);
console.log(`Mean avg-occupancy: ${round_(mean(occVals))}%   max: ${Math.max(...occVals)}%`);
console.log(`Zones over 100% (chronic overflow): ${occVals.filter((v) => v > 100).length} / ${occVals.length}`);
console.log(`Zones in the 70–100% sweet-spot band: ${occVals.filter((v) => v >= 70 && v <= 100).length} / ${occVals.length}`);
console.log(`Zones under 50% (daily slack): ${occVals.filter((v) => v < 50).length} / ${occVals.length}`);
console.log(`Mean turnover: ${round_(mean(withOcc.map((f) => f.properties.turnover)))} events/space`);
console.log(`Written to ${GEOJSON_PATH}`);

function round_(n) {
	return Math.round(n * 10) / 10;
}
