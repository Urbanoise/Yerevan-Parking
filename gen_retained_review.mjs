// Proposes RetainedRemoved updates for Kentron and Komitas from the v2 conceptual
// design. REVIEW ONLY — writes a standalone workbook and touches neither the survey
// workbooks nor field-surveys.geojson. Approve first, then transcribe.
//
// Why only these two areas: the design KMZ lists retained parking, so "no segment
// nearby" is ambiguous between "everything removed here" and "the redesign does not
// cover this street". That ambiguity is safe to resolve only where the design actually
// reaches. Measured zone-to-nearest-segment distance puts all 58 Kentron zones and 51
// of 53 Komitas zones within 200 m, against zero of Garegin Nzhdeh, Shiraz and Gai, and
// 3 of 22 in Malatia-Sebastia — those four keep their existing flags untouched.
//
// A zone counts as retained when at least KEEP_FRACTION of its vertices lie within
// NEAR metres of a design segment. Coverage is reported per zone so borderline calls
// can be judged by eye rather than taken on trust.
import { readFileSync } from 'fs';
import XLSX from 'xlsx';

const DIR = 'app/static/data/wgs84/';
const OUT = 'Field Surveys/RetainedRemoved Review - 23072026.xlsx';
const AREAS = { kentron: 'Kentron - Analysis.xlsx', komitas: 'Parking Survey Sheet v5.xlsx' };

const NEAR = 15;            // m from a design segment to count a vertex as kept
const KEEP_FRACTION = 0.5;  // share of vertices that must be near to call it retained
const BORDERLINE = [0.2, 0.8]; // coverage in this band is flagged for human review

const surveys = JSON.parse(readFileSync(DIR + 'field-surveys.geojson', 'utf8'));
const design = JSON.parse(readFileSync(DIR + 'new-design-parking.geojson', 'utf8'));

const LAT0 = 40.18, MX = Math.cos((LAT0 * Math.PI) / 180) * 111320, MY = 110540;
const xy = ([lng, lat]) => [lng * MX, lat * MY];
function ptSeg(p, a, b) {
	const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
	let t = L ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L : 0;
	t = t < 0 ? 0 : t > 1 ? 1 : t;
	return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
}

const segments = [];
for (const f of design.features) {
	if (f.properties.spaces == null) continue;
	const pts = f.geometry.coordinates.map(xy);
	for (let i = 1; i < pts.length; i++) segments.push([pts[i - 1], pts[i]]);
}

const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const wb = XLSX.utils.book_new();
const summary = [];

for (const area of Object.keys(AREAS)) {
	const rows = [];
	for (const f of surveys.features) {
		if (f.properties.area !== area) continue;
		const pts = f.geometry.coordinates.map(xy);
		let near = 0, nearest = Infinity;
		for (const p of pts) {
			let best = Infinity;
			for (const [a, b] of segments) { const d = ptSeg(p, a, b); if (d < best) best = d; }
			if (best < nearest) nearest = best;
			if (best < NEAR) near++;
		}
		const coverage = pts.length ? near / pts.length : 0;
		const current = cap(f.properties.retained);
		const proposed = cap(coverage >= KEEP_FRACTION ? 'retained' : 'removed');
		rows.push({
			Zone: f.properties.zone,
			Name: f.properties.name,
			Spaces: Number(f.properties.space) || 0,
			'Peak occupancy': Number(f.properties.peak_occupancy) || 0,
			Current: current,
			Proposed: proposed,
			Change: current === proposed ? '' : `${current} → ${proposed}`,
			'Design coverage': Math.round(coverage * 100) / 100,
			'Nearest segment (m)': Math.round(nearest),
			Confidence: coverage > BORDERLINE[0] && coverage < BORDERLINE[1] ? 'BORDERLINE — review' : 'clear',
		});
	}
	// changed zones first, largest first — the ones worth arguing about are at the top
	rows.sort((a, b) => (b.Change ? 1 : 0) - (a.Change ? 1 : 0) || b.Spaces - a.Spaces);

	const changed = rows.filter(r => r.Change);
	const sum = (rs, k) => rs.reduce((s, r) => s + r[k], 0);
	const remNow = sum(rows.filter(r => r.Current === 'Removed'), 'Spaces');
	const remNew = sum(rows.filter(r => r.Proposed === 'Removed'), 'Spaces');
	summary.push({
		Area: area, 'Workbook to edit': AREAS[area], Zones: rows.length,
		'Zones changed': changed.length,
		'Borderline': rows.filter(r => r.Confidence !== 'clear').length,
		'Removed spaces now': remNow, 'Removed spaces proposed': remNew, 'Delta': remNew - remNow,
	});
	XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(rows), cap(area));
	console.log(`${area}: ${rows.length} zones, ${changed.length} changed, `
		+ `${rows.filter(r => r.Confidence !== 'clear').length} borderline; removed spaces ${remNow} → ${remNew}`);
}

const notes = [
	{ Note: 'REVIEW ONLY — nothing has been applied. Approve, then transcribe the Proposed column into each workbook\'s RetainedRemoved sheet and re-run convert_field_surveys.mjs + compute_field_survey_metrics.mjs.' },
	{ Note: `Proposed = Retained when >=${KEEP_FRACTION * 100}% of a zone's vertices lie within ${NEAR} m of a v2 design segment.` },
	{ Note: 'Source: Parking New Design/New Design Parking 23072026 v2.kmz via new-design-parking.geojson.' },
	{ Note: 'Only Kentron and Komitas are proposed. The design does not geometrically reach Garegin Nzhdeh, Shiraz/Hasratyan or Gai Avenue, and reaches only 3 of 22 Malatia-Sebastia zones, so those areas keep their existing flags.' },
	{ Note: 'BORDERLINE rows are partly covered by the design — a zone the design keeps in part. Decide these by eye; the 50% rule forces them one way or the other.' },
];
XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summary), 'Summary');
XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(notes), 'Notes');
XLSX.writeFile(wb, OUT);
console.log(`\nWritten ${OUT} (review only — no workbook or geojson was modified)`);
