import { readFileSync, writeFileSync } from 'fs';
import XLSX from 'xlsx';

// Extract the renamed survey paths — those whose name contains "(Zone NN)" — from
// the Field Surveys KML. The survey now spans two areas:
//   • Komitas      — zones 70–122  (Parking Survey Sheet v5)
//   • Shiraz/Hasratyan — zones 123–156 (Shiraz, Hasratyan - Analysis)
// Each path is tagged with an `area` so the Field Surveys story step can resolve
// per-area dashboard numbers as the reader zooms between the two neighbourhoods.
//
// The KML is the "Field Surveys 05062026.kmz" unzipped to a plain .kml:
//   unzip -p "Field Surveys 05062026.kmz" doc.kml > "Field Surveys 05062026.kml"
const KML_PATH = 'Field Surveys/Field Surveys 05062026.kml';
const kml = readFileSync(KML_PATH, 'utf8');

// Zone → area split. Komitas is the original survey (70–122); the new Shiraz/
// Hasratyan corridor adds 123–156.
const SHIRAZ_MIN = 123;
const SHIRAZ_MAX = 156;
const areaOfZone = (z) => (z >= SHIRAZ_MIN && z <= SHIRAZ_MAX ? 'shiraz' : 'komitas');

// Post-BRT retain/remove decision per zone comes from the "RetainedRemoved" sheet
// of the Komitas survey workbook (columns: Zone | Retained/Removed). Build a zone →
// flag lookup so each survey path can be colored by whether it survives the BRT
// redesign. The Shiraz/Hasratyan zones are outside every BRT corridor, so nothing
// there is removed — they default to "retained" (see below).
const wb = XLSX.readFile('Field Surveys/Parking Survey Sheet v5.xlsx');
const retainedRows = XLSX.utils.sheet_to_json(wb.Sheets['RetainedRemoved'], { header: 1, blankrows: false });
const retainedByZone = {};
for (const row of retainedRows.slice(1)) {
	const zone = Number(row[0]);
	const flag = String(row[1] ?? '').trim().toLowerCase();
	if (Number.isFinite(zone) && (flag === 'retained' || flag === 'removed')) {
		retainedByZone[zone] = flag;
	}
}

function extractText(xml, tag) {
	const m = xml.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`));
	return m ? m[1].trim() : null;
}

function extractCDATA(xml, tag) {
	const m = xml.match(new RegExp(`<${tag}[^>]*><!\\[CDATA\\[([\\s\\S]*?)\\]\\]></${tag}>`));
	if (m) return m[1].trim();
	return extractText(xml, tag);
}

function parseCoordinates(coordStr) {
	return coordStr.trim().split(/\s+/).filter(Boolean).map(pt => {
		const [lng, lat] = pt.split(',').map(Number);
		return [lng, lat];
	});
}

// Pull a "Label: Value" field out of the HTML description, stripping HTML
// entities/whitespace noise (e.g. "&nbsp; No" -> "no").
function descField(html, label) {
	if (!html) return null;
	const m = html.match(new RegExp(`${label}:\\s*([^<]+)`, 'i'));
	if (!m) return null;
	const cleaned = m[1]
		.replace(/&nbsp;/gi, ' ')
		.replace(/\s+/g, ' ')
		.trim()
		.toLowerCase();
	return cleaned || null;
}

// --- Resolve parking regulation from each path's KML line color ---
// The survey paths carry no "Regulation" text field, but the line color the
// surveyor assigned in Google Earth encodes it (white = free, blue = paid Zone B,
// etc.). Build style lookups so each placemark's styleUrl can be resolved to a hex.
const styleColor = {};
for (const m of kml.matchAll(/<gx:CascadingStyle kml:id="([^"]+)">([\s\S]*?)<\/gx:CascadingStyle>/g)) {
	const lc = m[2].match(/<LineStyle>[\s\S]*?<color>([0-9a-fA-F]{8})<\/color>/);
	if (lc) styleColor[m[1]] = lc[1];
}
for (const m of kml.matchAll(/<Style id="([^"]+)">([\s\S]*?)<\/Style>/g)) {
	const lc = m[2].match(/<LineStyle>[\s\S]*?<color>([0-9a-fA-F]{8})<\/color>/);
	if (lc) styleColor[m[1]] = lc[1];
}
const styleMapNormal = {};
for (const m of kml.matchAll(/<StyleMap id="([^"]+)">([\s\S]*?)<\/StyleMap>/g)) {
	const norm = m[2].match(/<key>normal<\/key>\s*<styleUrl>#([^<]+)<\/styleUrl>/);
	if (norm) styleMapNormal[m[1]] = norm[1];
}

// KML color is aabbggrr; convert to #RRGGBB.
function kmlColorToHex(c) {
	if (!c) return null;
	return ('#' + c.slice(6, 8) + c.slice(4, 6) + c.slice(2, 4)).toUpperCase();
}

// Map a resolved line color to the app's Parking Regulation buckets.
const REGULATION_BY_HEX = {
	'#FFFFFF': 'white', // free
	'#42A5F5': 'blue',  // paid Zone B
	'#EF5350': 'red',   // paid Zone A
	'#888888': 'black', // taxi
};

function resolveRegulation(placemarkXml) {
	const inline = placemarkXml.match(/<LineStyle>[\s\S]*?<color>([0-9a-fA-F]{8})<\/color>/);
	let hex = inline ? kmlColorToHex(inline[1]) : null;
	if (!hex) {
		const su = placemarkXml.match(/<styleUrl>#([^<]+)<\/styleUrl>/);
		if (su) {
			const normalId = styleMapNormal[su[1]] || su[1];
			hex = kmlColorToHex(styleColor[normalId]);
		}
	}
	return REGULATION_BY_HEX[hex] || 'white';
}

const features = [];
const placemarkMatches = [...kml.matchAll(/<Placemark[^>]*>([\s\S]*?)<\/Placemark>/g)];

// Capture the ShirazYard010 off-street lot polygon while sweeping the placemarks —
// it is the Shiraz/Hasratyan counterpart to the KomitasCity yard.
let shirazYardCoords = null;

for (const pm of placemarkMatches) {
	const content = pm[1];
	const name = extractText(content, 'name');
	if (!name) continue;

	if (/^ShirazYard010\s*$/.test(name.trim())) {
		const cs = extractText(content, 'coordinates');
		if (cs) shirazYardCoords = parseCoordinates(cs);
	}

	const zoneMatch = name.match(/\(\s*Zone\s+(\d+)\s*\)/i);
	if (!zoneMatch) continue; // only keep the renamed "(Zone NN)" paths

	const coordStr = extractText(content, 'coordinates');
	if (!coordStr) continue;
	const coordinates = parseCoordinates(coordStr);
	if (coordinates.length < 2) continue;

	const descRaw = extractCDATA(content, 'description');
	const spaceStr = descField(descRaw, 'Space');
	const zone = parseInt(zoneMatch[1], 10);
	const area = areaOfZone(zone);

	// Komitas keeps the surveyed RetainedRemoved decision; Shiraz/Hasratyan sits
	// outside every BRT corridor, so all of its on-street parking is retained.
	const retained = area === 'shiraz' ? 'retained' : (retainedByZone[zone] ?? null);

	const props = {
		name: name.trim(),
		zone,
		area,
		space: spaceStr ? parseInt(spaceStr, 10) || 0 : 0,
		regulation: resolveRegulation(content),
		method: descField(descRaw, 'Method'),
		marking: descField(descRaw, 'Marking'),
		signage: descField(descRaw, 'Signage'),
		location: descField(descRaw, 'Location'),
		retained,
	};

	features.push({
		type: 'Feature',
		geometry: { type: 'LineString', coordinates },
		properties: props,
	});
}

const geojson = { type: 'FeatureCollection', features };

// --- Off-street yards shown alongside the survey paths ---
// One per area: KomitasCity (123 spaces) and ShirazYard010 (71 spaces). KomitasCity
// geometry comes from the existing parking-areas inventory; ShirazYard010 from the
// survey KML polygon captured above. compute_field_survey_metrics.mjs stamps each
// yard with its measured occupancy afterwards.
const SHIRAZ_YARD_SPACES = 71;
const areasGeo = JSON.parse(readFileSync('app/static/data/wgs84/parking-areas.geojson', 'utf8'));
const komitasCity = areasGeo.features.find(f => (f.properties.name || '') === 'KomitasCity');

const yardFeatures = [];
if (komitasCity) {
	const html = komitasCity.properties.description?.value || '';
	const m = html.match(/Space:\s*(\d+)/i);
	yardFeatures.push({
		type: 'Feature',
		geometry: komitasCity.geometry,
		properties: { name: 'KomitasCity', area: 'komitas', space: m ? parseInt(m[1], 10) : 123 },
	});
} else {
	console.warn('WARNING: KomitasCity not found in parking-areas.geojson');
}
if (shirazYardCoords) {
	yardFeatures.push({
		type: 'Feature',
		geometry: { type: 'Polygon', coordinates: [shirazYardCoords] },
		properties: { name: 'ShirazYard010', area: 'shiraz', space: SHIRAZ_YARD_SPACES },
	});
} else {
	console.warn('WARNING: ShirazYard010 polygon not found in KML');
}
const yardsGeojson = { type: 'FeatureCollection', features: yardFeatures };

// --- Report ---
const byArea = (a) => features.filter(f => f.properties.area === a);
for (const area of ['komitas', 'shiraz']) {
	const fs = byArea(area);
	const totalSpaces = fs.reduce((s, f) => s + (f.properties.space || 0), 0);
	const regCounts = fs.reduce((acc, f) => { acc[f.properties.regulation] = (acc[f.properties.regulation] || 0) + 1; return acc; }, {});
	console.log(`[${area}] paths: ${fs.length}  spaces: ${totalSpaces}  regulation: ${JSON.stringify(regCounts)}`);
}
console.log(`Total survey paths: ${features.length}`);
console.log(`Yards: ${yardFeatures.map(f => `${f.properties.name}(${f.properties.space})`).join(', ')}`);

writeFileSync('app/static/data/wgs84/field-surveys.geojson', JSON.stringify(geojson));
writeFileSync('app/static/data/wgs84/field-survey-yards.geojson', JSON.stringify(yardsGeojson));
console.log('Written field-surveys.geojson and field-survey-yards.geojson');
