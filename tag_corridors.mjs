// Tags every supply feature with the corridor it sits on, so the app and the report
// scripts share one definition instead of each re-deriving it.
//
// Membership is by geometry, not by name: a feature belongs to a corridor if its
// midpoint falls inside that corridor's boundary polygon, falling back to "any vertex
// inside" for features that straddle the edge (Isahakyan01 and the Tamantsiner pair on
// Corridor 01 both need the fallback). Features inside no polygon get corridor: null —
// currently just Nalbandyan016, which is tagged impact=corridor but lies wholly outside
// every boundary, and is excluded from the published on-corridor totals for that reason.
//
// Additive and idempotent: it only writes the `corridor` property, so re-running after a
// fresh KML export re-derives the tag without disturbing anything else.
import { readFileSync, writeFileSync } from 'fs';

const DIR = 'app/static/data/wgs84/';
const rd = n => JSON.parse(readFileSync(DIR + n, 'utf8'));
const bounds = rd('corridor-boundaries.geojson');

function inRing(pt, ring) {
	let inside = false;
	for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
		const [xi, yi] = ring[i], [xj, yj] = ring[j];
		if ((yi > pt[1]) !== (yj > pt[1]) && pt[0] < ((xj - xi) * (pt[1] - yi)) / (yj - yi) + xi) inside = !inside;
	}
	return inside;
}
const inPoly = (pt, g) => (g.type === 'Polygon' ? [g.coordinates] : g.coordinates)
	.some(p => inRing(pt, p[0]) && !p.slice(1).some(h => inRing(pt, h)));

function verts(g) {
	switch (g.type) {
		case 'Point': return [g.coordinates];
		case 'LineString': case 'MultiPoint': return g.coordinates;
		case 'MultiLineString': case 'Polygon': return g.coordinates.flat();
		case 'MultiPolygon': return g.coordinates.flat(2);
		default: return [];
	}
}

function corridorOf(geometry) {
	const vs = verts(geometry);
	if (!vs.length) return null;
	const mid = vs[Math.floor(vs.length / 2)];
	for (const b of bounds.features) if (inPoly(mid, b.geometry)) return b.properties.name;
	for (const v of vs) for (const b of bounds.features) if (inPoly(v, b.geometry)) return b.properties.name;
	return null;
}

// sensitivity-zones carries no corridor of its own but is drawn on the retention step,
// so it needs the same tag to be filterable alongside the supply layers. landmarks are
// deliberately left untagged: they are city context (malls, venues), not corridor supply.
for (const file of ['parking-lines.geojson', 'parking-areas.geojson', 'field-surveys.geojson', 'sensitivity-zones.geojson']) {
	const geo = rd(file);
	const counts = {};
	for (const f of geo.features) {
		const c = corridorOf(f.geometry);
		f.properties.corridor = c;
		counts[c ?? 'none'] = (counts[c ?? 'none'] || 0) + 1;
	}
	writeFileSync(DIR + file, JSON.stringify(geo));
	console.log(`${file.padEnd(26)} ${geo.features.length} features → ${JSON.stringify(counts)}`);
}
