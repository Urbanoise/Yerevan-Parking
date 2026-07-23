import { readFileSync, writeFileSync } from 'fs';
import { inflateRawSync } from 'zlib';

// Latest conceptual design. Google Earth now exports .kmz (a zip holding doc.kml);
// a bare .kml path still works, so older exports can be re-run by changing this line.
const SOURCE = 'Parking New Design/New Design Parking 23072026 v2.kmz';

// --- minimal KMZ (zip) reader -------------------------------------------------
// A KMZ is a zip with one doc.kml inside. Rather than take a dependency for it, we
// walk the central directory and inflate the entry ourselves. Only the two methods
// Google Earth emits are handled: 0 (stored) and 8 (deflate).
function readKmz(buf) {
	const eocd = buf.lastIndexOf(Buffer.from('PK\x05\x06', 'binary'));
	if (eocd < 0) throw new Error('not a zip: no end-of-central-directory record');
	let p = buf.readUInt32LE(eocd + 16); // offset of first central-directory entry
	const count = buf.readUInt16LE(eocd + 10);
	for (let i = 0; i < count; i++) {
		const nameLen = buf.readUInt16LE(p + 28);
		const extraLen = buf.readUInt16LE(p + 30);
		const commentLen = buf.readUInt16LE(p + 32);
		const name = buf.toString('utf8', p + 46, p + 46 + nameLen);
		const method = buf.readUInt16LE(p + 10);
		const compSize = buf.readUInt32LE(p + 20);
		const localOff = buf.readUInt32LE(p + 42);
		if (name.toLowerCase().endsWith('.kml')) {
			// the local header repeats the name/extra lengths, and they can differ
			const lNameLen = buf.readUInt16LE(localOff + 26);
			const lExtraLen = buf.readUInt16LE(localOff + 28);
			const start = localOff + 30 + lNameLen + lExtraLen;
			const raw = buf.subarray(start, start + compSize);
			return (method === 0 ? raw : inflateRawSync(raw)).toString('utf8');
		}
		p += 46 + nameLen + extraLen + commentLen;
	}
	throw new Error('no .kml entry inside ' + SOURCE);
}

const kml = SOURCE.toLowerCase().endsWith('.kmz')
	? readKmz(readFileSync(SOURCE))
	: readFileSync(SOURCE, 'utf8');

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

// --- Reconciliation to the signed-off retained totals ---------------------------
// The KMZ runs slightly above the agreed retained totals (Final Presentation/
// Retention Numbers.xlsx, and everything published off it). Per client instruction the
// gap is closed by shaving one space off each of the largest paths, working down from
// the top, until the folder hits its target.
//
// Driven by TARGET, not by a path count: the design has been re-exported twice (908 →
// 913 → 872 on Corridor 1) and a hardcoded "top 39" silently stops reconciling the
// moment the source moves. Deriving the count from the target keeps the published
// totals stable across re-exports, and the guard below fires if a future export drifts
// so far that shaving one space per path can no longer close the gap.
//
// Ordering is spaces DESC then name ASC. The name tiebreak matters: when the cut falls
// inside a run of equal-sized paths, only some of them are decremented, and without a
// deterministic tiebreak which ones would drift with KMZ placemark order.
const TARGET = { 'Corridor 1': 869, 'Corridor 2': 351 };
for (const [folder, target] of Object.entries(TARGET)) {
	const rows = features
		.filter(f => f.properties.folder === folder && f.properties.spaces != null)
		.sort((a, b) => b.properties.spaces - a.properties.spaces
			|| String(a.properties.name).localeCompare(String(b.properties.name)));
	const before = rows.reduce((s, f) => s + f.properties.spaces, 0);
	const gap = before - target;
	if (gap < 0) {
		console.warn(`WARNING: ${folder} KMZ total ${before} is BELOW target ${target} — left untouched; `
			+ `shaving cannot add spaces, so confirm which number is current.`);
		continue;
	}
	if (gap > rows.length) {
		console.warn(`WARNING: ${folder} needs ${gap} spaces removed but has only ${rows.length} paths — `
			+ `left untouched rather than shaving some paths twice.`);
		continue;
	}
	for (const f of rows.slice(0, gap)) f.properties.spaces -= 1;
	console.log(`reconcile ${folder}: ${before} → ${target} (1 space off each of the top ${gap} paths)`);
}

const geojson = { type: 'FeatureCollection', features };

// Stats
const kzFeatures = features.filter(f => f.properties.folder === 'kz');
const c1Features = features.filter(f => f.properties.folder === 'Corridor 1');
const c2Features = features.filter(f => f.properties.folder === 'Corridor 2');
const c1Total = c1Features.reduce((s, f) => s + (f.properties.spaces || 0), 0);
const c2Total = c2Features.reduce((s, f) => s + (f.properties.spaces || 0), 0);

console.log(`source: ${SOURCE}`);
console.log(`kz features: ${kzFeatures.length}`);
console.log(`Corridor 1 segments: ${c1Features.length}, total spaces: ${c1Total}`);
console.log(`Corridor 2 segments: ${c2Features.length}, total spaces: ${c2Total}`);
console.log(`Grand total spaces (corridors): ${c1Total + c2Total}`);
console.log(`Total features: ${features.length}`);

// Every corridor placemark must carry a parseable space count — a silent null would
// quietly shrink the retained total that the app and the reports both quote.
const missing = [...c1Features, ...c2Features].filter(f => f.properties.spaces == null);
if (missing.length) console.warn(`WARNING: ${missing.length} corridor segments with no space count:`,
	missing.map(f => f.properties.name).join(', '));

writeFileSync('app/static/data/wgs84/new-design-parking.geojson', JSON.stringify(geojson));
console.log('Written to app/static/data/wgs84/new-design-parking.geojson');
