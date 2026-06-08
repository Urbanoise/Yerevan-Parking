import { readFileSync, writeFileSync } from 'fs';
import XLSX from 'xlsx';

// Extract the renamed survey paths — those whose name contains "(Zone NN)" — from
// the Field Surveys KML. The survey now spans four areas:
//   • Garegin Nzhdeh   — zones 25–59   (Garegin Nzhdeh St - Analysis)
//   • Mega Mall        — zones 60–69   (Mega Mall - Analysis)
//   • Komitas          — zones 70–122  (Parking Survey Sheet v5)
//   • Shiraz/Hasratyan — zones 123–156 (Shiraz, Hasratyan - Analysis)
// Each path is tagged with an `area` so the Field Surveys story step can resolve
// per-area dashboard numbers as the reader zooms between the neighbourhoods.
//
// The KML is the "Field Surveys 08062026.kmz" unzipped to a plain .kml:
//   unzip -p "Field Surveys 08062026.kmz" doc.kml > "Field Surveys 08062026.kml"
const KML_PATH = 'Field Surveys/Field Surveys 08062026.kml';
const kml = readFileSync(KML_PATH, 'utf8');

// Zone → area split. Each surveyed neighbourhood owns a contiguous zone range.
const areaOfZone = (z) =>
	z <= 59 ? 'garegin' :
	z <= 69 ? 'mega' :
	z <= 122 ? 'komitas' :
	'shiraz';

// Post-BRT retain/remove decision per zone comes from the "RetainedRemoved" sheet
// of the Komitas survey workbook (columns: Zone | Retained/Removed). Build a zone →
// flag lookup so each survey path can be colored by whether it survives the BRT
// redesign. Only Komitas overlaps the BRT corridors; the Garegin, Mega Mall and
// Shiraz/Hasratyan zones sit outside every corridor, so nothing there is removed —
// they default to "retained" (see below).
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

// Off-street lot polygons captured straight from the KML, one per non-Komitas area.
// Each yard is the off-street counterpart to that area's on-street zones; the survey
// workbook's off-street occupancy log keys to it in compute_field_survey_metrics.mjs.
//   • ShirazYard010 — Shiraz/Hasratyan (71 spaces, capacity from KML)
//   • GNOFF         — Garegin Nzhdeh off-street (40 spaces)
//   • Palace        — Mega Mall, the "P" off-street log (32 spaces)
// `match` is the exact KML placemark name; `space` overrides any KML capacity so the
// figures stay aligned with the survey team's agreed lot sizes.
const KML_YARDS = [
	{ name: 'ShirazYard010', area: 'shiraz', match: 'ShirazYard010', space: 71 },
	{ name: 'GNOFF', area: 'garegin', match: 'GNOFF', space: 40 },
	{ name: 'Palace', area: 'mega', match: 'Palace', space: 32 },
];
const kmlYardCoords = {}; // yard name -> ring coordinates

for (const pm of placemarkMatches) {
	const content = pm[1];
	const name = extractText(content, 'name');
	if (!name) continue;

	const yardDef = KML_YARDS.find(y => y.match === name.trim());
	if (yardDef && /<Polygon>/.test(content)) {
		const cs = extractText(content, 'coordinates');
		if (cs) kmlYardCoords[yardDef.name] = parseCoordinates(cs);
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

	// Komitas keeps the surveyed RetainedRemoved decision; the other areas sit
	// outside every BRT corridor, so all of their on-street parking is retained.
	const retained = area === 'komitas' ? (retainedByZone[zone] ?? null) : 'retained';

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
// One per area. KomitasCity (123 spaces) geometry comes from the existing parking-
// areas inventory; the other three (ShirazYard010, GNOFF, Palace) from the survey
// KML polygons captured above. compute_field_survey_metrics.mjs stamps each yard
// with its measured occupancy afterwards.
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
for (const y of KML_YARDS) {
	const ring = kmlYardCoords[y.name];
	if (ring) {
		yardFeatures.push({
			type: 'Feature',
			geometry: { type: 'Polygon', coordinates: [ring] },
			properties: { name: y.name, area: y.area, space: y.space },
		});
	} else {
		console.warn(`WARNING: ${y.name} polygon ("${y.match}") not found in KML`);
	}
}
const yardsGeojson = { type: 'FeatureCollection', features: yardFeatures };

// --- Report ---
const byArea = (a) => features.filter(f => f.properties.area === a);
for (const area of ['garegin', 'mega', 'komitas', 'shiraz']) {
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
