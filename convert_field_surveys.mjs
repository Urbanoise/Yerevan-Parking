import { readFileSync, writeFileSync } from 'fs';
import XLSX from 'xlsx';

// Extract only the renamed survey paths — those whose name contains "(Zone NN)" —
// from the Field Surveys KML (unzipped from "Field Surveys.kmz" via `unzip -p
// "Field Surveys.kmz" doc.kml > "Field Surveys.kml"`).
const kml = readFileSync('Field Surveys/Field Surveys.kml', 'utf8');

// Post-BRT retain/remove decision per zone comes from the "RetainedRemoved" sheet
// of the survey workbook (columns: Zone | Retained/Removed). Build a zone → flag
// lookup so each survey path can be colored by whether it survives the BRT redesign.
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

// Both <gx:CascadingStyle kml:id="X"> (managed styles) and classic <Style id="X">
// blocks may hold the LineStyle color. Index both by id.
const styleColor = {};
for (const m of kml.matchAll(/<gx:CascadingStyle kml:id="([^"]+)">([\s\S]*?)<\/gx:CascadingStyle>/g)) {
	const lc = m[2].match(/<LineStyle>[\s\S]*?<color>([0-9a-fA-F]{8})<\/color>/);
	if (lc) styleColor[m[1]] = lc[1];
}
for (const m of kml.matchAll(/<Style id="([^"]+)">([\s\S]*?)<\/Style>/g)) {
	const lc = m[2].match(/<LineStyle>[\s\S]*?<color>([0-9a-fA-F]{8})<\/color>/);
	if (lc) styleColor[m[1]] = lc[1];
}
// <StyleMap id="X"> ... <key>normal</key><styleUrl>#X_normal</styleUrl>
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
	// Inline LineStyle on the placemark wins over the referenced style.
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

for (const pm of placemarkMatches) {
	const content = pm[1];
	const name = extractText(content, 'name');
	if (!name) continue;

	const zoneMatch = name.match(/\(\s*Zone\s+(\d+)\s*\)/i);
	if (!zoneMatch) continue; // only keep the renamed "(Zone NN)" paths

	const coordStr = extractText(content, 'coordinates');
	if (!coordStr) continue;
	const coordinates = parseCoordinates(coordStr);
	if (coordinates.length < 2) continue;

	const descRaw = extractCDATA(content, 'description');

	const spaceStr = descField(descRaw, 'Space');
	const props = {
		name: name.trim(),
		zone: parseInt(zoneMatch[1], 10),
		space: spaceStr ? parseInt(spaceStr, 10) || 0 : 0,
		regulation: resolveRegulation(content),
		method: descField(descRaw, 'Method'),
		marking: descField(descRaw, 'Marking'),
		signage: descField(descRaw, 'Signage'),
		location: descField(descRaw, 'Location'),
		// Post-BRT retain/remove decision (from the RetainedRemoved sheet, keyed by zone).
		retained: retainedByZone[parseInt(zoneMatch[1], 10)] ?? null,
	};

	features.push({
		type: 'Feature',
		geometry: { type: 'LineString', coordinates },
		properties: props,
	});
}

const geojson = { type: 'FeatureCollection', features };

const totalSpaces = features.reduce((s, f) => s + (f.properties.space || 0), 0);
const regCounts = features.reduce((acc, f) => {
	acc[f.properties.regulation] = (acc[f.properties.regulation] || 0) + 1;
	return acc;
}, {});
console.log(`Field survey (Zone) paths: ${features.length}`);
console.log(`Total spaces: ${totalSpaces}`);
console.log(`Regulation breakdown: ${JSON.stringify(regCounts)}`);
console.log(`Zones: ${features.map(f => f.properties.zone).sort((a, b) => a - b).join(', ')}`);

writeFileSync('app/static/data/wgs84/field-surveys.geojson', JSON.stringify(geojson));
console.log('Written to app/static/data/wgs84/field-surveys.geojson');
