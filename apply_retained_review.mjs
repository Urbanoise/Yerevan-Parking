// Applies the approved RetainedRemoved proposals from the review workbook onto
// field-surveys.geojson, so the displacement metrics can be recomputed against the v2
// conceptual design.
//
// This writes the flags straight onto the GeoJSON rather than into the survey
// workbooks. The workbooks stay the client's own record; convert_field_surveys.mjs
// still reads them, so running that script afterwards REVERTS this change. The
// intended order when the flags are signed off for good is: update each workbook's
// RetainedRemoved sheet, then re-run convert_field_surveys.mjs. Until then this is the
// way to see what the design implies without editing the client's spreadsheets.
//
// Usage:  node apply_retained_review.mjs            (dry run — reports, writes nothing)
//         node apply_retained_review.mjs --apply    (writes field-surveys.geojson)
import { readFileSync, writeFileSync } from 'fs';
import XLSX from 'xlsx';

const GEOJSON = 'app/static/data/wgs84/field-surveys.geojson';
const REVIEW = 'Field Surveys/RetainedRemoved Review - 23072026.xlsx';
const SHEETS = ['Kentron', 'Komitas'];   // the only areas the v2 design geometrically reaches
const apply = process.argv.includes('--apply');

const geo = JSON.parse(readFileSync(GEOJSON, 'utf8'));
const wb = XLSX.readFile(REVIEW);

const proposed = {};
for (const sheet of SHEETS) {
	if (!wb.Sheets[sheet]) throw new Error(`review workbook has no "${sheet}" sheet`);
	for (const row of XLSX.utils.sheet_to_json(wb.Sheets[sheet])) {
		const flag = String(row.Proposed || '').toLowerCase();
		if (flag !== 'retained' && flag !== 'removed') throw new Error(`${sheet} zone ${row.Zone}: bad flag "${row.Proposed}"`);
		proposed[`${sheet.toLowerCase()}:${row.Zone}`] = flag;
	}
}

const sum = (fs_, k) => fs_.reduce((s, f) => s + (Number(f.properties[k]) || 0), 0);
const removedBefore = geo.features.filter(f => f.properties.retained === 'removed');

let matched = 0, changed = 0;
const unmatched = new Set(Object.keys(proposed));
for (const f of geo.features) {
	const key = `${f.properties.area}:${f.properties.zone}`;
	const flag = proposed[key];
	if (!flag) continue;
	matched++;
	unmatched.delete(key);
	if (f.properties.retained !== flag) { f.properties.retained = flag; changed++; }
}

const removedAfter = geo.features.filter(f => f.properties.retained === 'removed');
console.log(`review rows ${Object.keys(proposed).length} | matched to zones ${matched} | flags changed ${changed}`);
if (unmatched.size) console.warn(`WARNING: ${unmatched.size} review rows matched no survey zone: ${[...unmatched].join(', ')}`);
console.log(`removed zones  ${removedBefore.length} → ${removedAfter.length}`);
console.log(`removed spaces ${sum(removedBefore, 'space')} → ${sum(removedAfter, 'space')}`);

if (!apply) {
	console.log('\nDRY RUN — nothing written. Re-run with --apply to write.');
} else {
	writeFileSync(GEOJSON, JSON.stringify(geo));
	console.log(`\nWritten ${GEOJSON}. Now run: node compute_field_survey_metrics.mjs`);
}
