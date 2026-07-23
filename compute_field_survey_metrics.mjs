import { readFileSync, writeFileSync } from 'fs';
import xlsx from 'xlsx';

// Merge per-zone occupancy survey metrics into field-surveys.geojson + the two
// off-street yards, and pre-compute the per-area dashboard stat blocks the Field
// Surveys story step shows as the reader zooms between neighbourhoods.
//
// Four source workbooks, one per surveyed area, all with a "United Data" sheet — a
// license-plate occupancy log where each row is one vehicle seen in one zone at one
// hour. The license plate reconstructs each vehicle's duration and a zone's
// turnover; the zone number joins 1:1 to the survey paths' `zone` property. Formal
// (striped) capacity comes from the geojson `space` field, so occupancy/turnover
// are measured against the legal supply already on the map.
//   • Garegin Nzhdeh   — Garegin Nzhdeh St - Analysis (zones 25–59, 7:00–23:00)
//                         off-street log labelled "Off-street" → GNOFF yard
//   • Gai Avenue       — Mega Mall - Analysis (zones 60–69, 7:00–22:00)
//                         off-street log labelled "P" (Palace lot) → Palace yard
//   • Komitas          — Parking Survey Sheet v5  (zones 70–122, 7:00–23:00)
//                         off-street log labelled "Off street city" → KomitasCity yard
//   • Shiraz/Hasratyan — Shiraz, Hasratyan - Analysis (zones 123–156, 7:00–23:00)
//                         off-street log labelled "Shiraz off-street" → ShirazYard010

const GEOJSON_PATH = 'app/static/data/wgs84/field-surveys.geojson';
const YARDS_PATH = 'app/static/data/wgs84/field-survey-yards.geojson';

// Each source's United Data sheet, the area it feeds, and the off-street log label
// that maps to that area's yard. Areas render outer→inner in the dashboard order.
// Malatia-Sebastia (Sebastia/Raffi) uses the SebastiaYard006 polygon for its
// "Off-street" log (101 spaces, see KML_YARDS in convert_field_surveys.mjs).
const SOURCES = [
	{ area: 'malatia', file: 'Field Surveys/Malatia Sebastia - Analysis.xlsx', offLabel: 'Off-street', yard: 'SebastiaYard006' },
	{ area: 'kentron', file: 'Field Surveys/Kentron - Analysis.xlsx', offLabel: 'Off-street', yard: 'NalbandyanYard001' },
	{ area: 'garegin', file: 'Field Surveys/Garegin Nzhdeh St - Analysis.xlsx', offLabel: 'Off-street', yard: 'GNOFF' },
	{ area: 'mega', file: 'Field Surveys/Mega Mall - Analysis.xlsx', offLabel: 'P', yard: 'Palace' },
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
		} else if (typeof zone === 'string' && zone.trim().toLowerCase() === offLabel.toLowerCase()) {
			key = offLabel; // the off-street yard log (label may vary in case, e.g. "P"/"p")
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

	const wh = [...windowHours];
	return {
		plateHours, hourPlates, obs, window: windowHours.size,
		// survey-window edges (first/last observed hour) for the 1-hour boundary rule
		firstHour: wh.length ? Math.min(...wh) : null,
		lastHour: wh.length ? Math.max(...wh) : null,
	};
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

	// Surveyed zones with a known formal capacity. We summarise occupancy at the
	// PEAK hour (the only figure parking policy cares about) and weight by capacity
	// so a 60-space corridor counts 20× a 3-space stub — unlike a plain mean of
	// per-zone percentages, which lets tiny empty zones drag the headline down.
	const surveyed = fs.filter(f => f.properties.peak_occupancy != null && (f.properties.space || 0) > 0);
	const peakSum = surveyed.reduce((s, f) => s + f.properties.peak_occupancy, 0);
	const capSum = surveyed.reduce((s, f) => s + f.properties.space, 0);
	const peakPct = (f) => (f.properties.peak_occupancy / f.properties.space) * 100;
	// 85% is the classic Shoup target: above it, drivers start cruising for a spot.
	const over85 = surveyed.filter(f => peakPct(f) >= 85).length;
	const overCap = surveyed.filter(f => peakPct(f) > 100).length;

	const white = fs.filter(f => f.properties.regulation === 'white').reduce((s, f) => s + (f.properties.space || 0), 0);
	const blue = fs.filter(f => f.properties.regulation === 'blue').reduce((s, f) => s + (f.properties.space || 0), 0);

	const retainedSpaces = fs.filter(f => f.properties.retained === 'retained').reduce((s, f) => s + (f.properties.space || 0), 0);
	const removedSpaces = fs.filter(f => f.properties.retained === 'removed').reduce((s, f) => s + (f.properties.space || 0), 0);
	const retainedPaths = fs.filter(f => f.properties.retained === 'retained').length;
	const totalRetSpaces = retainedSpaces + removedSpaces;

	const yardSpaces = areaKey === 'all'
		? yards.features.reduce((s, y) => s + (y.properties.space || 0), 0)
		: (yardByArea[areaKey]?.space || 0);
	const yardLabel = {
		malatia: 'SebastiaYard006',
		kentron: 'NalbandyanYard001',
		garegin: 'GNOFF Yard',
		mega: 'Palace Yard',
		komitas: 'KomitasCity Yard',
		shiraz: 'ShirazYard010 Yard',
	}[areaKey] || 'Off-Street Yards';

	return {
		occupancy: [
			{ value: capSum ? round((peakSum / capSum) * 100) : 0, label: 'Peak Occupancy % (cap-weighted)', color: '#2ecc71' },
			{ value: surveyed.length ? round((over85 / surveyed.length) * 100) : 0, label: '% Zones Over 85% (Peak)', color: '#ffa600' },
			{ value: overCap, label: 'Zones Over Capacity', color: '#ff1f44' },
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
		displacement: computeDisplacement(fs.filter(f => f.properties.retained === 'removed')).stats,
	};
}

// --- Displacement snapshot (the §6 "where do the removed cars go" check) ---
// When BRT removes a corridor's on-street parking, the cars parked there at the
// busy hour have to land somewhere. The honest test is: do the streets *around*
// the corridor have room to absorb them?
//
// "Around the corridor" = the parking-lines inventory already tags every segment
// with an `impact` of corridor / buffer / yard. By construction buffer + yard are
// the band within ~100 m of the corridor, so we use those tags directly instead
// of recomputing distances.
//
// We scope the absorbers to the corridor the removals actually sit on, by name.
// Every parking-line name is prefixed with its corridor street (KomitasGriboedov003,
// KomitasYard001…) and the removed survey zones share that prefix (Komitas008,
// Komitas046…) — so the set of leading words on the removed zones IS the corridor
// namespace. Matching buffer/yard names by that prefix keeps only the genuinely
// nearby capacity instead of the whole study-area inventory. (No hardcoded street:
// the prefix is derived from whatever zones are flagged removed — so a per-area call
// with no removals simply yields an empty, zeroed block.)
//
// Those buffer/yard streets were never occupancy-surveyed, so we only know their
// *total* capacity — the result is a best-case "is there even enough room in
// principle" (gross capacity, not spare).
//
//   removed demand  = Σ peak_occupancy over the field-survey 'removed' zones
//                     (real cars needing a new spot at the busy hour)
//   removed supply  = Σ space over those same zones (marked spaces lost)
//   absorbing room  = Σ space over buffer/yard parking-lines on the same corridor
const PARKING_LINES_PATH = 'app/static/data/wgs84/parking-lines.geojson';
const linesGeo = JSON.parse(readFileSync(PARKING_LINES_PATH, 'utf8'));
const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
const leadWord = (n) => (String(n || '').match(/^[A-Za-z]+/) || [''])[0];

// True single-hour peak: the most cars standing in the removed zones at one clock-
// hour (max over hours of Σ vehicles present), NOT the sum of each zone's own peak
// hour — those peaks fall at different times, so summing them overstates what's ever
// displaced at once (147 summed vs 93 real). Grouped by area so multiple corridors
// each contribute their own local peak hour. Reads the hourly presence sets that
// parseUnitedData already built (sources[area].hourPlates: zone → hour → Set(plates)).
function peakHourDemand(removedZones) {
	const byArea = {};
	for (const f of removedZones) (byArea[f.properties.area] ??= []).push(f.properties.zone);
	let total = 0;
	for (const [area, zones] of Object.entries(byArea)) {
		const src = sources[area];
		if (!src) continue;
		const hours = new Set();
		for (const z of zones) { const zh = src.hourPlates.get(z); if (zh) for (const h of zh.keys()) hours.add(h); }
		let areaMax = 0;
		for (const h of hours) {
			let sum = 0;
			for (const z of zones) sum += src.hourPlates.get(z)?.get(h)?.size || 0;
			if (sum > areaMax) areaMax = sum;
		}
		total += areaMax;
	}
	return total;
}

// --- "Is this absorber on a surveyed street, and near the area?" geometry (metres) ---
// A buffer/yard parking-line that sits on a surveyed street is ALREADY represented by
// the survey layers (green if retained, hidden if removed), so counting it again as
// unsurveyed absorbing capacity would double-count the removed parking (the Zone 21 /
// SebastiaVantyan001 case). We flag each buffer/yard line two ways:
//   • distance to the nearest survey path — ≤ SURVEY_NEAR ⇒ surveyed (exclude);
//   • distance to the affected area's overall survey FOOTPRINT (the bounding box of its
//     survey paths) — within AREA_MAX ⇒ near enough to absorb that area's displacement.
// Gating on the area footprint (not a single street) lets a lot sitting behind the
// surveyed blocks still count, while keeping genuinely distant lots out.
const SURVEY_NEAR = 20, AREA_MAX = 100;
const LAT0 = 40.18, MX = Math.cos((LAT0 * Math.PI) / 180) * 111320, MY = 110540;
const toXY = ([lng, lat]) => [lng * MX, lat * MY];
function ptSeg(p, a, b) {
	const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
	let t = L ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L : 0;
	t = t < 0 ? 0 : t > 1 ? 1 : t;
	return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
}
// Distance from point p to an axis-aligned bbox (0 if inside).
function ptBox(p, b) {
	const dx = Math.max(b.x0 - p[0], 0, p[0] - b.x1);
	const dy = Math.max(b.y0 - p[1], 0, p[1] - b.y1);
	return Math.hypot(dx, dy);
}
// Survey-path segments + bounding box grouped by area, in metres.
const surveySegsByArea = {};
const surveyBoxByArea = {};
for (const f of geojson.features) {
	const pts = f.geometry.coordinates.map(toXY);
	const segs = (surveySegsByArea[f.properties.area] ??= []);
	for (let i = 1; i < pts.length; i++) segs.push([pts[i - 1], pts[i]]);
	const b = (surveyBoxByArea[f.properties.area] ??= { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity });
	for (const [x, y] of pts) { b.x0 = Math.min(b.x0, x); b.y0 = Math.min(b.y0, y); b.x1 = Math.max(b.x1, x); b.y1 = Math.max(b.y1, y); }
}
// For each buffer/yard parking-line: min distance to every area's survey paths (global
// min, for the surveyed-street exclusion) and to every area's survey footprint bbox.
const bufferYard = linesGeo.features.filter(f => f.properties.impact === 'buffer' || f.properties.impact === 'yard');
const absorberDist = new Map();
for (const f of bufferYard) {
	const cs = f.geometry.type === 'LineString' ? f.geometry.coordinates : f.geometry.coordinates.flat();
	const pts = cs.map(toXY);
	const byArea = {}; const boxByArea = {}; let global = Infinity;
	for (const [area, segs] of Object.entries(surveySegsByArea)) {
		let m = Infinity;
		for (const s of segs) for (const p of pts) { const d = ptSeg(p, s[0], s[1]); if (d < m) m = d; }
		byArea[area] = m; if (m < global) global = m;
		let mb = Infinity;
		for (const p of pts) { const d = ptBox(p, surveyBoxByArea[area]); if (d < mb) mb = d; }
		boxByArea[area] = mb;
	}
	absorberDist.set(f, { byArea, boxByArea, global });
}
const sumSpace = (arr) => arr.reduce((s, f) => s + num(f.properties.space), 0);

// --- Off-street yard POLYGONS (parking-areas.geojson) as unsurveyed off-street absorbers ---
// The off-street lots drawn in the regulation steps (KomitasYard*, RaffiYard*, …), 265 of
// them, capacity in each feature's description ("Space: N"). The six that were occupancy-
// surveyed (the field-survey-yards: KomitasCity etc.) are EXCLUDED — they carry their own
// measured occupancy and are shown but not counted, like the green on-street survivors.
// Each remaining lot is gated to an area by distance from its polygon to that area's survey
// footprint bbox (≤ AREA_MAX), the same rule as the unsurveyed on-street absorbers.
const AREAS_PATH = 'app/static/data/wgs84/parking-areas.geojson';
const areasGeo = JSON.parse(readFileSync(AREAS_PATH, 'utf8'));
const SURVEYED_YARDS = new Set(['KomitasCity', 'ShirazYard010', 'GNOFF', 'Palace', 'SebastiaYard006', 'NalbandyanYard001']);
const areaSpace = (p) => { const s = (p.description && (p.description.value || p.description)) || ''; const m = String(s).match(/Space:?\s*(\d+)/i); return m ? +m[1] : 0; };
const offYardPolys = [];
for (const f of areasGeo.features) {
	if (SURVEYED_YARDS.has(f.properties.name)) continue;        // surveyed → shown, not counted
	const space = areaSpace(f.properties);
	if (!space) continue;
	const ring = f.geometry.type === 'Polygon' ? f.geometry.coordinates.flat() : f.geometry.coordinates.flat(2);
	const pts = ring.map(toXY);
	const boxByArea = {};
	for (const [area, b] of Object.entries(surveyBoxByArea)) {
		let mb = Infinity;
		for (const p of pts) { const d = ptBox(p, b); if (d < mb) mb = d; }
		boxByArea[area] = mb;
	}
	offYardPolys.push({ name: f.properties.name, space, boxByArea });
}

// Returns { stats, raw } for a set of removed survey zones. Absorbing capacity counts
// ONLY parking we have NOT already surveyed — surveyed parking has its own measured
// occupancy, so counting it as free room to absorb displaced cars would double-count.
//   GREEN  surveyed survivors — retained survey zones; SHOWN on the map for context but
//          EXCLUDED from the absorbing math (they already carry their own occupancy).
//   YELLOW unsurveyed nearby  — buffer/yard parking-lines within AREA_MAX of the area's
//          survey footprint AND not coincident with any surveyed street → counts.
//   OFF-STREET — the affected area(s)' off-street yard lot(s) → counts.
// Yellow + off-street are gross capacity (best-case); only these feed Nearby On-Street,
// Nearby Off-Street and % Cars Absorbed.
function computeDisplacement(removedZones) {
	const removedSupply = sumSpace(removedZones);
	const removedDemand = peakHourDemand(removedZones);
	const removedAreas = [...new Set(removedZones.map(f => f.properties.area))];

	const retainedSurveyed = geojson.features.filter(f => removedAreas.includes(f.properties.area) && f.properties.retained === 'retained');
	const greenCapacity = sumSpace(retainedSurveyed);

	const yellow = removedZones.length ? bufferYard.filter(f => {
		const d = absorberDist.get(f);
		if (d.global <= SURVEY_NEAR) return false;                 // on a surveyed street → already represented
		return removedAreas.some(a => (d.boxByArea[a] ?? Infinity) <= AREA_MAX);
	}) : [];
	const yellowCapacity = sumSpace(yellow);

	// Only the UNSURVEYED nearby parking counts toward absorbing capacity; the green
	// retained survey zones AND the surveyed off-street yards are shown but excluded
	// (they have their own occupancy).
	const onStreetCapacity = yellowCapacity;
	const offYards = removedZones.length
		? offYardPolys.filter(y => removedAreas.some(a => (y.boxByArea[a] ?? Infinity) <= AREA_MAX))
		: [];
	const offStreetCapacity = offYards.reduce((s, y) => s + y.space, 0);
	const surveyedYardCapacity = removedAreas.reduce((s, a) => s + num(yardByArea[a]?.space), 0); // shown, not counted
	const absorbCapacity = onStreetCapacity + offStreetCapacity;
	const netDemand = absorbCapacity - removedDemand;
	// Two absorption rates: on-street alone, and the total nearby supply (on-street + yards).
	const absorbedOnStreet = removedDemand ? round(Math.min(1, onStreetCapacity / removedDemand) * 100) : null;
	const absorbed = removedDemand ? round(Math.min(1, absorbCapacity / removedDemand) * 100) : null;
	const raw = {
		removed_zones: removedZones.length,
		removed_supply: removedSupply,
		removed_demand: removedDemand,
		absorb_capacity: absorbCapacity,        // counted = yellow on-street + off-street (green excluded)
		absorb_onstreet: onStreetCapacity,      // unsurveyed nearby on-street only
		absorb_green_surveyed: greenCapacity,   // retained survey zones — shown but NOT counted
		absorb_yellow_unsurveyed: yellowCapacity, // unsurveyed buffer/yard nearby
		absorb_offstreet: offStreetCapacity,    // unsurveyed off-street yard polygons (counted)
		absorb_offstreet_surveyed: surveyedYardCapacity, // surveyed yards — shown, NOT counted
		net_vs_demand: netDemand,
		net_vs_supply: absorbCapacity - removedSupply,
		absorbed_onstreet: absorbedOnStreet,
		absorbed,
		basis: 'gross capacity of UNSURVEYED parking only; green=retained survey zones shown but excluded (own occupancy); yellow=unsurveyed on-street buffer/yard >20m from any survey path & within 100m of the area survey footprint (bbox); purple=unsurveyed off-street yard polygons; surveyed yards shown but excluded',
	};
	const stats = [
		{ value: removedDemand, label: 'Cars Displaced (Peak Hour)', color: '#EF5350' },
		{ value: removedSupply, label: 'Spaces Removed', color: '#b0455a' },
		{ value: onStreetCapacity, label: 'Nearby On-Street', color: '#ffd60a' },
		{ value: offStreetCapacity, label: 'Nearby Off-Street', color: '#7c4dff' },
		{ value: absorbedOnStreet == null ? 0 : absorbedOnStreet, label: '% Absorbed On-Street', color: '#ffd60a' },
		{ value: absorbed == null ? 0 : absorbed, label: '% Absorbed Total', color: '#00e5ff' },
	];
	return { stats, raw };
}

const areaStats = {
	all: statsForArea('all'),
	malatia: statsForArea('malatia'),
	kentron: statsForArea('kentron'),
	garegin: statsForArea('garegin'),
	mega: statsForArea('mega'),
	komitas: statsForArea('komitas'),
	shiraz: statsForArea('shiraz'),
};
geojson.areaStats = areaStats;
geojson.displacement = computeDisplacement(geojson.features.filter(f => f.properties.retained === 'removed')).raw;

// --- Demand profile (#3 stay-length split + #4 hourly accumulation curve) ---
// Both read the per-zone presence structures parseUnitedData already built. The
// hourly VAP is Σ vehicles present each clock-hour; the stay split bins each plate by
// how many hours it was seen. Four data-driven duration bins (the web app's split):
//   ≤1h short visit · 2–4h errand/shopper · 5–8h worker · >8h all-day/overnight.
// The 2–4h vs 5–8h cut separates two behaviours the old "commuter 2–8h" band
// conflated (errand turnover vs all-day interception). avg_duration_h is total hours
// present per vehicle. durationBlock also exposes the legacy three-way split
// (visitor=short, commuter=errand+worker, long=all-day) so the .docx report
// generators that read this geojson keep working unchanged.
//
// Approved 1-hour boundary rule (matches the report): a single-sweep stay seen ONLY
// in the survey window's first or last hour is most likely an overnight vehicle
// clipped by the daytime window (07:00–24:00), not a genuine ≤1h visit — so it is
// reclassified from 'short' into 'allday' (overnight). This lifts the 8h+ band from
// the raw ~2% to ~7% and trims ≤1h ~68%→~63%. A single-sweep stay in the interior
// of the window is a real short visit and stays in 'short'.
// Per-area profiles ride in areaStats (the stats board reads them by viewport area);
// per-zone profiles go in geojson.zoneProfiles, keyed "area:zone", for click popups.
function stayBin(hoursSet, firstHour, lastHour) {
	const dur = hoursSet.size;
	if (dur < 2) {
		const h = [...hoursSet][0];
		return (h === firstHour || h === lastHour) ? 'allday' : 'short';
	}
	return dur <= 4 ? 'errand' : dur <= 8 ? 'worker' : 'allday';
}

function durationTotals() { return { short: 0, errand: 0, worker: 0, allday: 0, durSum: 0, n: 0 }; }
function addStay(t, hoursSet, firstHour, lastHour) {
	t.durSum += hoursSet.size; t.n++;
	t[stayBin(hoursSet, firstHour, lastHour)]++;
}
function durationBlock(t) {
	const tot = t.short + t.errand + t.worker + t.allday || 1;
	const pct = (x) => round((x / tot) * 100);
	return {
		// four data-driven bins
		short: t.short, errand: t.errand, worker: t.worker, allday: t.allday,
		shortPct: pct(t.short), errandPct: pct(t.errand),
		workerPct: pct(t.worker), alldayPct: pct(t.allday),
		// legacy three-way split, for the .docx report generators
		visitor: t.short, commuter: t.errand + t.worker, long: t.allday,
		visitorPct: pct(t.short), commuterPct: pct(t.errand + t.worker), longPct: pct(t.allday),
		avg: round(t.durSum / (t.n || 1), 1),
	};
}

// One area's profile: VAP merged by hour across its zones (across all areas for
// 'all'), duration counts summed. Uses each zone's own source for the hourly sets.
function areaProfile(areaKey) {
	const feats = areaKey === 'all' ? geojson.features : geojson.features.filter(f => f.properties.area === areaKey);
	const byArea = {};
	for (const f of feats) (byArea[f.properties.area] ??= []).push(f.properties.zone);
	const vapMap = new Map();
	const t = durationTotals();
	for (const [area, zones] of Object.entries(byArea)) {
		const src = sources[area];
		if (!src) continue;
		for (const z of zones) {
			const hp = src.hourPlates.get(z);
			if (hp) for (const [h, plates] of hp) vapMap.set(h, (vapMap.get(h) || 0) + plates.size);
			const ph = src.plateHours.get(z);
			if (ph) for (const hours of ph.values()) addStay(t, hours, src.firstHour, src.lastHour);
		}
	}
	const vap = [...vapMap.entries()].sort((a, b) => a[0] - b[0]);  // [[hour, vehicles], …]
	return { vap, duration: durationBlock(t) };
}

// One zone's profile, for the click popup.
function zoneProfile(area, zone) {
	const src = sources[area];
	if (!src) return null;
	const hp = src.hourPlates.get(zone), ph = src.plateHours.get(zone);
	if (!hp && !ph) return null;
	const vap = hp ? [...hp.entries()].sort((a, b) => a[0] - b[0]).map(([h, p]) => [h, p.size]) : [];
	const t = durationTotals();
	if (ph) for (const hours of ph.values()) addStay(t, hours, src.firstHour, src.lastHour);
	const dur = durationBlock(t);
	return { vap, stay: { short: dur.short, errand: dur.errand, worker: dur.worker, allday: dur.allday }, avg: dur.avg };
}

for (const k of Object.keys(areaStats)) areaStats[k].profile = areaProfile(k);

const zoneProfiles = {};
for (const f of geojson.features) {
	const p = zoneProfile(f.properties.area, f.properties.zone);
	if (p) zoneProfiles[`${f.properties.area}:${f.properties.zone}`] = p;
}
geojson.zoneProfiles = zoneProfiles;

writeFileSync(GEOJSON_PATH, JSON.stringify(geojson));
writeFileSync(YARDS_PATH, JSON.stringify(yards));

// --- Report ---
console.log(`Survey paths: ${geojson.features.length}  matched to survey data: ${matched}`);
if (missing.length) console.log(`No survey rows for zones: ${missing.join(', ')}`);
for (const area of ['malatia', 'kentron', 'garegin', 'mega', 'komitas', 'shiraz', 'all']) {
	const o = areaStats[area].occupancy;
	console.log(`[${area}] peak occ ${o[0].value}%  over-85 ${o[1].value}%  over-cap ${o[2].value}`);
}
for (const y of yards.features) {
	console.log(`Yard ${y.properties.name}: cap ${y.properties.space}  occupancy ${y.properties.occupancy_pct}%  (${y.properties.unique_vehicles} vehicles)`);
}
console.log(`Windows — komitas: ${sources.komitas.window}h, shiraz: ${sources.shiraz.window}h`);

// --- Basis check: per-zone peaks vs one shared clock hour ---
// The headline occupancy above sums each zone's OWN busiest hour, which is the right
// figure for "how hard is this kerb worked" but counts cars that were never present at
// the same moment. Displacement instead uses a single clock hour (peakHourDemand), the
// right figure for "how many cars need re-homing at once". Both are legitimate; they are
// not comparable, and the two sit side by side on the deck's per-area table. Printing
// them together keeps the gap visible rather than leaving it to be rediscovered.
console.log('Occupancy basis — sum of per-zone peaks vs single shared hour:');
let totCap = 0, totSummed = 0, totShared = 0;
for (const area of ['malatia', 'kentron', 'garegin', 'mega', 'komitas', 'shiraz']) {
	const zones = geojson.features.filter(f => f.properties.area === area
		&& f.properties.peak_occupancy != null && (f.properties.space || 0) > 0);
	const cap = zones.reduce((s, f) => s + f.properties.space, 0);
	const summed = zones.reduce((s, f) => s + f.properties.peak_occupancy, 0);
	const shared = peakHourDemand(zones);
	// which clock hour carries that shared peak — areas do not share one city-wide hour
	const src = sources[area];
	let bestHour = null, bestN = -1;
	if (src) {
		const hours = new Set();
		for (const z of zones) { const zh = src.hourPlates.get(z.properties.zone); if (zh) for (const h of zh.keys()) hours.add(h); }
		for (const h of [...hours].sort((a, b) => a - b)) {
			let n = 0;
			for (const z of zones) n += src.hourPlates.get(z.properties.zone)?.get(h)?.size || 0;
			if (n > bestN) { bestN = n; bestHour = h; }
		}
	}
	totCap += cap; totSummed += summed; totShared += shared;
	const pct = (v) => (cap ? Math.round((v / cap) * 100) : 0);
	console.log(`  ${area.padEnd(8)} cap ${String(cap).padStart(4)} | summed peaks ${String(summed).padStart(4)} = ${String(pct(summed)).padStart(3)}%`
		+ ` | single hour ${String(shared).padStart(4)} = ${String(pct(shared)).padStart(3)}% at ${String(bestHour).padStart(2)}:00`);
}
console.log(`  ${'ALL'.padEnd(8)} cap ${String(totCap).padStart(4)} | summed peaks ${String(totSummed).padStart(4)} = ${Math.round(100 * totSummed / totCap)}%`
	+ ` | single hour ${String(totShared).padStart(4)} = ${Math.round(100 * totShared / totCap)}% (each area at its own peak hour)`);
const d = geojson.displacement;
console.log(`Displacement: ${d.removed_zones} removed zones lose ${d.removed_supply} spaces / ${d.removed_demand} cars at peak hour; ` +
	`counted capacity ${d.absorb_capacity} (yellow on-street ${d.absorb_onstreet} + off-street ${d.absorb_offstreet}; green ${d.absorb_green_surveyed} shown but excluded) → ` +
	`net vs demand ${d.net_vs_demand >= 0 ? '+' : ''}${d.net_vs_demand}, vs supply ${d.net_vs_supply >= 0 ? '+' : ''}${d.net_vs_supply} (${d.absorbed}% absorbed)`);
const ap = areaStats.all.profile;
console.log(`Profile [all]: VAP ${ap.vap.length} hours (peak ${Math.max(...ap.vap.map(p => p[1]))}); ` +
	`stay split ${ap.duration.shortPct}% ≤1h / ${ap.duration.errandPct}% 2–4h / ${ap.duration.workerPct}% 5–8h / ${ap.duration.alldayPct}% >8h, avg ${ap.duration.avg}h; ` +
	`zoneProfiles: ${Object.keys(zoneProfiles).length}`);
console.log(`Written ${GEOJSON_PATH} and ${YARDS_PATH}`);
