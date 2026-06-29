# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two coupled deliverables built from the same parking-survey data:

1. **`app/`** — a SvelteKit + MapLibre scrollytelling web app that visualises Yerevan's
   on-street and off-street parking supply as a sequence of map "story steps".
2. **Report pipeline** (repo root) — Node converters that turn raw KML/KMZ/XLSX survey
   data into the app's GeoJSON, plus Python scripts that generate the client `.docx`
   reports (Output 8, Output 10, Field Surveys findings, audit memo).

The reports read the **same published GeoJSON the app serves**, so the numbers in the
documents never drift from what the dashboard shows. The GeoJSON is the single source of
truth — regenerate it first, then regenerate reports.

## Commands

The web app lives in `app/` (its own `package.json`); the data/report tooling lives at the
repo root (root `package.json` only carries `shapefile` + `xlsx` for the converters).

```bash
# Web app (run from app/)
cd app
npm install
npm run build      # production build → app/build/ (adapter-static)
npm run preview    # serve the static build on :5173  ← the user views THIS, not dev
npm run dev        # vite dev server (not the user's normal workflow)

# Data converters (run from repo ROOT, Node ESM)
node convert_field_surveys.mjs          # KML + XLSX → field-surveys.geojson + yards
node compute_field_survey_metrics.mjs   # merge occupancy/turnover metrics + areaStats
node convert_new_design.mjs             # New Design KML → new-design-parking.geojson

# Reports (run from repo root; needs python-docx + matplotlib)
python gen_field_survey_report.py       # Field Surveys findings report .docx
python gen_output8_change_plan.py       # redline change-plan for review
python apply_output8_edits.py           # apply approved edits → "...(rev).docx"
python gen_output10_figures.py          # Figures 10/11, swapped into the rev .docx
```

> **IMPORTANT — preview workflow:** the user reviews the static `app/build/` via
> `npm run preview` (port 5173), not the vite dev server. After editing anything under
> `app/src/`, run `npm run build` and tell the user to hard-refresh. Source edits do **not**
> appear without a rebuild.

There is no test suite, linter, or typechecker configured. `app/` uses JS + JSDoc with a
`jsconfig.json` (no TypeScript build).

## Web app architecture

**Stack:** Svelte 5 (runes mode, `runes: true`), SvelteKit, `adapter-static`
(`fallback: index.html`, deployed to Vercel with `outputDirectory: build`), MapLibre GL,
scrollama (scroll tracking), gsap. A single route (`app/src/routes/+page.svelte`) mounts
four components over a full-screen map.

**The story-driven pattern — everything keys off the current step:**

- **`app/src/lib/config/story.js`** — `STORY_STEPS[]` is the spine of the whole app. Each
  step is a declarative config object: camera (`center`/`zoom`/`pitch`/`bearing`), which
  layers are visible (`showLines`, `showAreas`, `showCorridors`, `showFieldSurveys`, …), a
  `colorMode` string, the `legendGroups`/`legendLayers`, and `stats` shown in the panel.
  **To change what a step shows, edit this file** — the components are generic and read it.
- **`app/src/lib/stores/storyStore.js`** — `currentStep` (the active index, set by scroll).
- **`app/src/lib/stores/mapStore.js`** — shared reactive state: the map instance, loaded
  data, and all the interactive filters (legend toggles, top-lots slider/category,
  field-survey lens/area/retained toggles). Components communicate through these stores.
- **`app/src/lib/components/MapEngine.svelte`** (~900 lines, the core) — owns the MapLibre
  map. `applyStepVisibility(step)` reads the step config and flips every layer's
  `visibility` + flies the camera. Reacts to store changes for live filtering, click
  popups, and the top-lots markers. The Field Surveys step is viewport-aware: zooming past
  `FS_AREA_ZOOM` snaps the dashboard to the nearest neighbourhood centroid
  (`FS_AREA_CENTROIDS`) and swaps in that area's pre-computed stat block.
- **`app/src/lib/layers/layers.js`** — every MapLibre layer definition. There is **one
  layer per colorMode** (e.g. `parking-lines-method`, `parking-lines-signage`,
  `parking-lines-color`); they share a GeoJSON source and `applyStepVisibility` toggles
  exactly one visible at a time. Colors here must stay in sync with the legend colors in
  `story.js`.
- **`Legend.svelte` / `StoryScroller.svelte` / `StoryStep.svelte` / `NavDots.svelte`** —
  the scroll UI and the legend/stats panel, all driven by the step config.

**Data:** GeoJSON in `app/static/data/wgs84/` (served as `/data/wgs84/*.geojson`).
`field-surveys.geojson` additionally embeds an `areaStats` block (per-area, per-lens
dashboard numbers) produced by `compute_field_survey_metrics.mjs`.

## Data pipeline & provenance

```
raw KML/KMZ/XLSX (Field Surveys/, Parking New Design/)
   │  convert_field_surveys.mjs        (extracts "(Zone NN)" survey paths, tags each with an area)
   │  compute_field_survey_metrics.mjs (joins license-plate occupancy logs → occupancy/turnover/areaStats)
   ▼
app/static/data/wgs84/*.geojson  ── served by the app AND read by the report scripts
   │  gen_*_report.py / gen_*_figures.py / apply_*_edits.py
   ▼
Field Surveys/Field Surveys Report/*.docx
```

- Survey paths are identified by a `(Zone NN)` suffix in their KML name and split into
  areas by zone-number range (Malatia-Sebastia, Garegin Nzhdeh, Gai Avenue, Komitas,
  Shiraz/Hasratyan); newer areas use lettered tags like `(Zone K01)`. The zone number/code
  joins 1:1 to the occupancy workbooks' rows. Formal (striped) capacity comes from the
  GeoJSON `space` field; paths with no `space` fall back to length ÷ 7.5 m.
- `parking-lines.geojson` / `parking-areas.geojson` (the core city supply) are committed
  static data with no converter in-repo — treat them as hand-maintained inputs (only
  `compute_offstreet_city_metrics.mjs` mutates `parking-areas.geojson`).
- `Parking_Supply.geojson` at the repo root is raw source, not consumed by the build.

## Report scripts — conventions

- Built with `python-docx`; figures with `matplotlib` (`Agg` backend). Paths inside the
  scripts are **absolute Windows paths** (`C:/Users/user/Yerevan-Parking/...`).
- **`gen_*_change_plan.py`** produces a redline *proposal* for client review; **`apply_*_edits.py`**
  applies the approved changes into a separate `...(rev).docx`, leaving the source
  untouched. Additions are red; deletions are red strikethrough. Plan → approve → apply.
- Known label quirk, do not "fix": **Output 10** = the Parking Analysis (measures) report,
  but its cover internally reads "Output 8: Parking Analysis Report" — a deliberate-to-leave
  client mislabel referenced across the scripts.

## Conventions & gotchas

- Adding/renaming a story step means editing `story.js` (config), `layers.js` (if a new
  colorMode/layer is needed), and possibly `MapEngine.svelte` (if it introduces new
  interactive state). Legend colors live in `story.js`; layer paint colors live in
  `layers.js` — keep them matched.
- Stats and analysis visuals that are always on belong in the stats panel (the StoryStep
  card), not the legend; per-zone detail belongs in click popups.
- The Field Surveys step distinguishes a **lens** (occupancy / paid-free — a `colorMode`
  swap) from the **retained/removed filter** (a cross-cutting visibility filter, not a lens).
- `.gitignore` excludes `node_modules/`, `build/`, `.svelte-kit/`, `.claude/`, the
  `poppler/` binaries, and the raw `Yerevan Shapes/` GIS extracts. The two `node_modules/`
  (root for converters, `app/` for the web app) are separate.
