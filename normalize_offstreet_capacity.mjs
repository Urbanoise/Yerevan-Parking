// Resolves off-street capacity into a numeric `space` property on every
// parking-areas feature, so the app and the report scripts stop re-parsing the raw
// Google Earth description HTML (and disagreeing when they do).
//
// Three things this settles:
//
//  1. Format drift. Capacity is written as "Space: 123", "Space: 101<br>" and
//     "space : 16" — a lowercase key with a space before the colon. The app's own
//     regex required "Space:" exactly and silently scored that last one 0.
//  2. Two features carry a `space` field that contradicts their description.
//     Per client decision the description wins for both, so they are pinned here
//     rather than left to whichever parser runs last.
//  3. NalbandyanPavstocByuzand is withdrawn from the inventory at client direction.
//     It is flagged, not deleted — parking-areas.geojson is hand-maintained source,
//     so the exclusion stays visible and reversible.
import { readFileSync, writeFileSync } from 'fs';

const PATH = 'app/static/data/wgs84/parking-areas.geojson';

// name → capacity to use instead of whatever the description parses to
const OVERRIDES = { SebastiaYard003: 30, SebastiaYard006: 101 };
// withdrawn from the published inventory; still present in the file, flagged excluded
const EXCLUDED = new Set(['NalbandyanPavstocByuzand']);

const geo = JSON.parse(readFileSync(PATH, 'utf8'));

function parseCapacity(props) {
	const d = props.description;
	const html = typeof d === 'string' ? d : d?.value || '';
	// tolerant: any case, optional whitespace either side of the colon, colon optional
	const m = html.replace(/&nbsp;/g, ' ').match(/space\s*:?\s*(\d+)/i);
	return m ? Number(m[1]) : 0;
}

let total = 0, excludedTotal = 0, unparsed = [], pinned = [];
for (const f of geo.features) {
	const p = f.properties;
	const parsed = parseCapacity(p);
	const capacity = OVERRIDES[p.name] ?? parsed;
	// report against the value the file carried before, which is what actually changes
	if (OVERRIDES[p.name] != null) pinned.push(`${p.name} ${p.space ?? '—'}→${capacity}`);
	if (!capacity) unparsed.push(p.name);

	p.space = capacity;
	if (EXCLUDED.has(p.name)) {
		p.excluded = 'withdrawn from inventory';
		excludedTotal += capacity;
	} else {
		delete p.excluded;
		total += capacity;
	}
}

const counted = geo.features.filter(f => !f.properties.excluded);
const byCorridor = {};
for (const f of counted) {
	const c = f.properties.corridor ?? 'none';
	byCorridor[c] = (byCorridor[c] || 0) + f.properties.space;
}

writeFileSync(PATH, JSON.stringify(geo));

console.log(`overrides pinned:       ${pinned.join(', ')}`);
console.log(`excluded:               ${EXCLUDED.size} facility / ${excludedTotal} spaces (${[...EXCLUDED].join(', ')})`);
if (unparsed.length) console.warn(`WARNING: ${unparsed.length} facilities with no capacity: ${unparsed.join(', ')}`);
console.log(`counted:                ${counted.length} facilities / ${total} spaces`);
console.log(`by corridor:            ${JSON.stringify(byCorridor)}`);
const c12 = (byCorridor['Corridor 01'] || 0) + (byCorridor['Corridor 02'] || 0);
const n12 = counted.filter(f => ['Corridor 01', 'Corridor 02'].includes(f.properties.corridor)).length;
console.log(`C1+C2:                  ${n12} facilities / ${c12} spaces`);
console.log(`Written to ${PATH}`);
