import { readFileSync, writeFileSync } from 'fs';

const kml = readFileSync('Parking New Design/New Design Parking.kml', 'utf8');

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
	return coordStr.trim().split(/\s+/).map(pt => {
		const [lng, lat] = pt.split(',').map(Number);
		return [lng, lat];
	});
}

const features = [];

// Split into folders
const folderMatches = [...kml.matchAll(/<Folder>([\s\S]*?)<\/Folder>/g)];

for (const fm of folderMatches) {
	const folderContent = fm[1];
	const folderName = extractText(folderContent, 'name');

	const placemarkMatches = [...folderContent.matchAll(/<Placemark>([\s\S]*?)<\/Placemark>/g)];

	for (const pm of placemarkMatches) {
		const content = pm[1];
		const name = extractText(content, 'name');
		const descRaw = extractCDATA(content, 'description');
		const coordStr = extractText(content, 'coordinates');
		if (!coordStr) continue;

		const coordinates = parseCoordinates(coordStr);
		if (coordinates.length < 2) continue;

		const props = { folder: folderName, name };

		if (folderName === 'kz') {
			const fidMatch = descRaw?.match(/FID\s+(\d+)/);
			props.fid = fidMatch ? parseInt(fidMatch[1]) : null;
		} else {
			// Corridor 1 / Corridor 2: description is the space count
			const spaces = descRaw ? parseInt(descRaw.replace(/<[^>]+>/g, '').trim()) : null;
			props.spaces = isNaN(spaces) ? null : spaces;
		}

		features.push({
			type: 'Feature',
			geometry: { type: 'LineString', coordinates },
			properties: props
		});
	}
}

const geojson = { type: 'FeatureCollection', features };

// Stats
const kzFeatures = features.filter(f => f.properties.folder === 'kz');
const c1Features = features.filter(f => f.properties.folder === 'Corridor 1');
const c2Features = features.filter(f => f.properties.folder === 'Corridor 2');
const c1Total = c1Features.reduce((s, f) => s + (f.properties.spaces || 0), 0);
const c2Total = c2Features.reduce((s, f) => s + (f.properties.spaces || 0), 0);

console.log(`kz features: ${kzFeatures.length}`);
console.log(`Corridor 1 segments: ${c1Features.length}, total spaces: ${c1Total}`);
console.log(`Corridor 2 segments: ${c2Features.length}, total spaces: ${c2Total}`);
console.log(`Grand total spaces (corridors): ${c1Total + c2Total}`);
console.log(`Total features: ${features.length}`);

writeFileSync('app/static/data/wgs84/new-design-parking.geojson', JSON.stringify(geojson));
console.log('Written to app/static/data/wgs84/new-design-parking.geojson');
