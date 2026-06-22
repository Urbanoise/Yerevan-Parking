<script>
	import { onMount, untrack } from 'svelte';
	import { mapInstance, dataLoaded, activeFilter, showAreas, showLines, activeLegendFilters, geojsonData, topLotsCount, topLotsCategories, showCurrentParking, showSensitivityZones, fieldSurveyMode, fieldSurveyRetained, fieldSurveyArea, fieldSurveyStats } from '$lib/stores/mapStore.js';
	import { currentStep } from '$lib/stores/storyStore.js';
	import { ALL_LAYERS, OCCUPANCY_COLOR } from '$lib/layers/layers.js';
	import { STORY_STEPS } from '$lib/config/story.js';

	const MAX_TOP_LOTS = 50;

	// Field Surveys viewport→area detection. The step shows all surveyed areas at
	// once; once the reader zooms past FS_AREA_ZOOM the dashboard settles on whichever
	// neighbourhood centroid is nearest, otherwise it reports the combined ('all') view.
	const FS_AREA_ZOOM = 13.3;
	const FS_AREA_CENTROIDS = {
		malatia: [44.4528, 40.1742],
		kentron: [44.5195, 40.1818],
		garegin: [44.4854, 40.1510],
		mega: [44.5677, 40.1978],
		komitas: [44.5173, 40.2066],
		shiraz: [44.4649, 40.1956],
	};

	let mapContainer;
	let map = null;
	let topMarkers = [];
	let currentStepIdx = 0;
	// The Displacement-lens absorber filter — matches the unsurveyed nearby parking-lines
	// tagged with `_absorber` at load (buffer/yard, >20 m from any survey path, within
	// 150 m of the area). Set once, reused to make those yellow lines clickable via the
	// shared parking-lines hit layer.
	let dispAbsorberFilter = null;

	function updateFieldSurveyArea() {
		const s = STORY_STEPS[currentStepIdx];
		if (!map || !s?.showFieldSurveys) return;
		const z = map.getZoom();
		if (z < FS_AREA_ZOOM) { fieldSurveyArea.set('all'); return; }
		const c = map.getCenter();
		let best = 'all', bestDist = Infinity;
		for (const [area, [lng, lat]] of Object.entries(FS_AREA_CENTROIDS)) {
			const d = (c.lng - lng) ** 2 + (c.lat - lat) ** 2;
			if (d < bestDist) { bestDist = d; best = area; }
		}
		fieldSurveyArea.set(best);
	}

	function applyStepVisibility(step, moveCamera = true) {
		if (!map || !$dataLoaded) return;

		const s = STORY_STEPS[step];
		if (!s) return;

		// Lines
		const showL = s.showLines ?? false;
		// Steps with a field-survey toggle resolve their colorMode from the active lens
		// (occupancy / paid-free); the retained/removed switch is a filter, not a lens,
		// so it's excluded here. Other steps use the step's static colorMode.
		const activeLens = s.fieldModes?.find(m => m.id === $fieldSurveyMode && !m.isSwitch)
			?? s.fieldModes?.find(m => !m.isSwitch);
		const colorMode = activeLens ? activeLens.colorMode : (s.colorMode ?? 'default');

		map.setLayoutProperty('parking-lines', 'visibility',
			showL && colorMode === 'default' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-method', 'visibility',
			showL && colorMode === 'method' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-signage', 'visibility',
			showL && colorMode === 'signage' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-marking', 'visibility',
			showL && colorMode === 'marking' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-location', 'visibility',
			showL && colorMode === 'location' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-color', 'visibility',
			showL && colorMode === 'color' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-impact', 'visibility',
			showL && colorMode === 'impact' ? 'visible' : 'none');
		map.setLayoutProperty('parking-lines-hit', 'visibility',
			showL ? 'visible' : 'none');

		// Areas
		const showA = s.showAreas ?? false;
		map.setLayoutProperty('parking-areas-fill', 'visibility', showA && colorMode !== 'impact' ? 'visible' : 'none');
		map.setLayoutProperty('parking-areas-fill-impact', 'visibility', showA && colorMode === 'impact' ? 'visible' : 'none');
		map.setLayoutProperty('parking-areas-outline', 'visibility', showA ? 'visible' : 'none');

		// Top off-street lot markers handled in a separate effect (reacts to slider too).

		// Corridors
		const showC = s.showCorridors ?? false;
		map.setLayoutProperty('corridors-line', 'visibility', showC ? 'visible' : 'none');
		map.setLayoutProperty('corridor-boundaries-fill', 'visibility', showC ? 'visible' : 'none');
		map.setLayoutProperty('corridor-boundaries-outline', 'visibility', showC ? 'visible' : 'none');

		// Landmarks
		const showLm = s.showLandmarks ?? false;
		map.setLayoutProperty('landmarks-points', 'visibility', showLm ? 'visible' : 'none');
		map.setLayoutProperty('landmarks-labels', 'visibility', showLm ? 'visible' : 'none');

		// Post-BRT new design (kz individual bays excluded — corridors only)
		const showND = s.showNewDesign ?? false;
		map.setLayoutProperty('new-design-kz', 'visibility', 'none');
		map.setLayoutProperty('new-design-corridors', 'visibility', showND ? 'visible' : 'none');
		map.setLayoutProperty('new-design-hit', 'visibility', showND ? 'visible' : 'none');

		// Sensitivity zones — only visible when the step supports the toggle AND it is toggled on
		if (!s.showSensitivityToggle) {
			map.setLayoutProperty('sensitivity-zones', 'visibility', 'none');
		} else {
			map.setLayoutProperty('sensitivity-zones', 'visibility', $showSensitivityZones ? 'visible' : 'none');
		}

		// Field surveys — renamed "(Zone NN)" survey paths, plus the off-street yards
		const showFS = s.showFieldSurveys ?? false;
		// The survey paths are coloured through one of two lenses: average occupancy ramp
		// or parking regulation (paid/free). The retained/removed switch is independent of
		// the lens — when on it just hides the paths removed by the BRT redesign, so the
		// surviving network keeps whichever lens colouring is active.
		const fsOcc = showFS && colorMode === 'field-occupancy';
		const fsReg = showFS && colorMode === 'field-surveys';
		// Displacement lens: the surviving survey network (green) with the absorbing
		// buffer/yard streets (yellow) on top. The removed-corridor red lines are
		// intentionally not shown in this view.
		const fsDisp = showFS && colorMode === 'field-displacement';
		map.setLayoutProperty('field-surveys-lines', 'visibility', fsReg ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-occupancy-glow', 'visibility', fsOcc ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-occupancy', 'visibility', fsOcc ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-displacement-retained', 'visibility', fsDisp ? 'visible' : 'none');
		map.setLayoutProperty('displacement-absorbers', 'visibility', fsDisp ? 'visible' : 'none');
		// Unsurveyed off-street yard polygons (the counted "Nearby Off-Street" capacity), yellow.
		map.setLayoutProperty('displacement-off-yards-fill', 'visibility', fsDisp ? 'visible' : 'none');
		map.setLayoutProperty('displacement-off-yards-outline', 'visibility', fsDisp ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-displacement-removed', 'visibility', 'none');
		map.setLayoutProperty('field-surveys-hit', 'visibility', showFS ? 'visible' : 'none');
		// The yellow absorber lines come from the parking-lines source, so they need the
		// shared parking-lines hit layer to be clickable. Surface it in the Displacement
		// lens scoped to the same absorbers; elsewhere leave it to the showLines logic
		// above with no extra filter.
		map.setFilter('parking-lines-hit', fsDisp ? dispAbsorberFilter : null);
		if (fsDisp) map.setLayoutProperty('parking-lines-hit', 'visibility', 'visible');
		// Retained/removed filter: when on, keep only the paths retained after the redesign.
		const retainedOnly = (showFS && $fieldSurveyRetained) ? ['==', ['get', 'retained'], 'retained'] : null;
		map.setFilter('field-surveys-occupancy-glow', retainedOnly);
		map.setFilter('field-surveys-occupancy', retainedOnly);
		map.setFilter('field-surveys-lines', retainedOnly);
		map.setFilter('field-surveys-hit', retainedOnly);
		// All four off-street yards (KomitasCity / ShirazYard010 / GNOFF / Palace) are
		// always retained, so the removed filter never touches them — they stay visible
		// in every lens.
		map.setLayoutProperty('field-survey-yard-fill', 'visibility', showFS ? 'visible' : 'none');
		map.setLayoutProperty('field-survey-yard-outline', 'visibility', showFS ? 'visible' : 'none');
		// In the occupancy lens, color the yard by its average occupancy on the same ramp
		// as the survey paths; otherwise keep its off-street purple — including the
		// Displacement lens, where the yard is the absorbing off-street capacity and
		// reads as purple against the green retained network and yellow on-street absorbers.
		map.setPaintProperty('field-survey-yard-fill', 'fill-color', fsOcc ? OCCUPANCY_COLOR : '#7c4dff');
		map.setPaintProperty('field-survey-yard-fill', 'fill-opacity', (fsOcc || fsDisp) ? 0.55 : 0.35);
		// Keep the off-street purple (#7c4dff, same as other indexes) on the border —
		// dashed in the occupancy and Displacement lenses so the shaded yard still reads
		// as an off-street facility (not an on-street path); solid purple otherwise.
		map.setPaintProperty('field-survey-yard-outline', 'line-color', '#7c4dff');
		map.setPaintProperty('field-survey-yard-outline', 'line-width', (fsOcc || fsDisp) ? 3 : 2);
		map.setPaintProperty('field-survey-yard-outline', 'line-dasharray', (fsOcc || fsDisp) ? [2, 1.5] : [1]);

		// Camera — only fly when entering the step. Re-applying visibility for a lens
		// toggle (paid/free, retained/removed) must NOT move the camera, so a reader who
		// has zoomed into a survey location stays "locked in" there across toggles.
		if (moveCamera) {
			map.easeTo({
				center: s.center,
				zoom: s.zoom,
				pitch: s.pitch ?? 0,
				bearing: s.bearing ?? 0,
				duration: 1200,
				easing: (t) => t * (2 - t)
			});
		}
	}

	function applyLegendFilter(filters) {
		if (!map || !$dataLoaded) return;

		const step = STORY_STEPS[$currentStep];
		if (!step) return;

		const colorMode = step.colorMode ?? 'default';
		const stepLayers = [...(step.legendLayers || []), ...(step.legendGroups?.flatMap(g => g.layers) || [])];
		const active = filters === null
			? new Set(stepLayers.map(l => l.id))
			: filters;

		// 1. Reset all filters if filters are null (switching steps or "show all")
		if (filters === null) {
			map.setFilter('parking-lines-method', null);
			map.setFilter('parking-lines-signage', null);
			map.setFilter('parking-lines-marking', null);
			map.setFilter('parking-lines-location', null);
			map.setFilter('parking-lines-color', null);
			map.setFilter('parking-lines-impact', null);
			map.setFilter('parking-areas-fill', null);
			map.setFilter('parking-areas-fill-impact', null);
			map.setFilter('parking-areas-outline', null);
			map.setFilter('parking-lines-hit', null);
			map.setFilter('corridors-line', null);
			map.setFilter('corridor-boundaries-fill', null);
			map.setFilter('corridor-boundaries-outline', null);
			map.setFilter('new-design-kz', null);
			map.setFilter('new-design-corridors', null);
			map.setFilter('new-design-hit', null);
		}

		// 2. Handle Corridor Mode (Check this before default colorMode because it has colorMode: 'default' but special layers)
		if (step.showCorridors) {
			const idToName = { 'corridor-1': 'Corridor 01', 'corridor-2': 'Corridor 02', 'corridor-3': 'Corridor 03' };
			const selected = stepLayers
				.filter(l => active.has(l.id))
				.map(l => idToName[l.id])
				.filter(Boolean);
			
			const f = selected.length === 0
				? ['==', ['get', 'name'], '__none__']
				: ['in', ['get', 'name'], ['literal', selected]];
			
			map.setFilter('corridors-line', f);
			map.setFilter('corridor-boundaries-fill', f);
			map.setFilter('corridor-boundaries-outline', f);
			return; // Corridor step is handled
		}

		// Post-BRT new design legend toggles
		if (colorMode === 'new-design') {
			const showC1 = active.has('new-c1');
			const showC2 = active.has('new-c2');

			const activeFolders = [
				...(showC1 ? ['Corridor 1'] : []),
				...(showC2 ? ['Corridor 2'] : []),
			];
			const corFilter = activeFolders.length === 0
				? ['==', ['get', 'folder'], '__none__']
				: ['in', ['get', 'folder'], ['literal', activeFolders]];
			map.setFilter('new-design-corridors', corFilter);
			map.setFilter('new-design-hit', corFilter);
			map.setLayoutProperty('new-design-corridors', 'visibility', activeFolders.length > 0 ? 'visible' : 'none');
			map.setLayoutProperty('new-design-hit', 'visibility', activeFolders.length > 0 ? 'visible' : 'none');
			return;
		}

		const propertyMap = {
			'color': { 'white': 'white', 'red': 'red', 'blue': 'blue', 'black': 'black' },
			'method': { 'parallel': 'parallel', '90': '90', '45': '45' },
			'signage': { 'yes': 'yes', 'no': 'no' },
			'marking': { 'yes': 'yes', 'no': 'no' },
			'location': { 'on-street': 'on-street', 'pocket': 'pocket', 'set-back': 'set-back' }
		};

		if (propertyMap[colorMode]) {
			const idToPrimary = propertyMap[colorMode];
			const idToImpact = { 'corridor': 'corridor', 'buffer': 'buffer', 'yard': 'yard' };
			
			const selectedPrimary = stepLayers
				.filter(l => active.has(l.id) && idToPrimary[l.id])
				.map(l => idToPrimary[l.id]);
				
			const selectedImpacts = stepLayers
				.filter(l => active.has(l.id) && idToImpact[l.id])
				.map(l => idToImpact[l.id]);

			let pFilter;
			if (selectedPrimary.length === 0) {
				pFilter = ['==', ['get', colorMode], '__none__'];
			} else {
				if ((colorMode === 'signage' || colorMode === 'marking')) {
					// Logic for boolean: yes/no, where no represents unset values as well
					if (selectedPrimary.includes('yes') && selectedPrimary.includes('no')) {
						pFilter = ['!=', ['get', colorMode], '__none__'];
					} else if (selectedPrimary.includes('no')) {
						pFilter = ['!=', ['get', colorMode], 'yes'];
					} else if (selectedPrimary.includes('yes')) {
						pFilter = ['==', ['get', colorMode], 'yes'];
					}
				} else if (colorMode === 'method') {
					if (selectedPrimary.includes('parallel')) {
						const unselected = ['90', '45'].filter(id => !selectedPrimary.includes(id));
						pFilter = unselected.length > 0 ? ['!', ['in', ['get', colorMode], ['literal', unselected]]] : ['!=', ['get', colorMode], '__none__'];
					} else {
						pFilter = ['in', ['get', colorMode], ['literal', selectedPrimary]];
					}
				} else if (colorMode === 'location') {
					if (selectedPrimary.includes('on-street')) {
						const unselected = ['pocket', 'set-back'].filter(id => !selectedPrimary.includes(id));
						pFilter = unselected.length > 0 ? ['!', ['in', ['get', colorMode], ['literal', unselected]]] : ['!=', ['get', colorMode], '__none__'];
					} else {
						pFilter = ['in', ['get', colorMode], ['literal', selectedPrimary]];
					}
				} else {
					pFilter = ['in', ['get', colorMode], ['literal', selectedPrimary]];
				}
			}

			const iFilter = selectedImpacts.length === 0 ? ['==', ['get', 'impact'], '__none__'] : ['in', ['get', 'impact'], ['literal', selectedImpacts]];
			
			const hasImpactOptions = stepLayers.some(l => idToImpact[l.id]);
			const finalFilter = hasImpactOptions ? ['all', pFilter, iFilter] : pFilter;

			const targetLayer = `parking-lines-${colorMode}`;
			map.setFilter(targetLayer, finalFilter);
			map.setFilter('parking-lines-hit', finalFilter);
			
			// Handle parking-areas (implicitly white and yard, lacks marking/signage)
			if (hasImpactOptions) {
				const primaryAllowsArea = colorMode === 'color' ? selectedPrimary.includes('white') : true;
				const showAreasImplicitly = primaryAllowsArea && selectedImpacts.includes('yard');
				const areaFilter = showAreasImplicitly ? null : ['==', '1', '2']; // hidden if false
				map.setFilter('parking-areas-fill', areaFilter);
				map.setFilter('parking-areas-outline', areaFilter);
			}
			return;
		}

		if (colorMode === 'impact') {
			const selected = step.legendLayers
				.filter(l => active.has(l.id))
				.map(l => l.id);
			const iFilter = selected.length === 0 ? ['==', ['get', 'impact'], '__none__'] : ['in', ['get', 'impact'], ['literal', selected]];
			map.setFilter('parking-lines-impact', iFilter);
			map.setFilter('parking-areas-fill-impact', iFilter);
			map.setFilter('parking-areas-outline', iFilter);
			map.setFilter('parking-lines-hit', iFilter);
			return;
		}

		// 4. Handle Default Mode (Direct visibility toggles)
		if (colorMode === 'default' && stepLayers.length > 0) {
			for (const layer of stepLayers) {
				if (!layer.layerId) continue;
				const vis = active.has(layer.id) ? 'visible' : 'none';
				
				// Standard visibility toggle
				map.setLayoutProperty(layer.layerId, 'visibility', vis);

				// Paired/secondary layers
				if (layer.layerId === 'parking-lines') {
					// Ensure we don't accidentally show lines if the step itself says showLines: false
					if (!step.showLines) map.setLayoutProperty('parking-lines', 'visibility', 'none');
				}
				if (layer.layerId === 'parking-areas-fill') {
					map.setLayoutProperty('parking-areas-outline', 'visibility', step.showAreas ? vis : 'none');
				}
				if (layer.layerId === 'landmarks-points') {
					map.setLayoutProperty('landmarks-labels', 'visibility', step.showLandmarks ? vis : 'none');
				}
			}
		}
	}

	function applyCurrentParkingOverlay(stepIdx, showCurrent) {
		if (!map || !$dataLoaded) return;
		const step = STORY_STEPS[stepIdx];

		// Always restore default opacity and filter so other steps aren't affected
		map.setPaintProperty('parking-lines-color', 'line-opacity', 0.9);
		map.setFilter('parking-lines-color', null);

		if (step?.showNewDesign && showCurrent) {
			map.setFilter('parking-lines-color', ['==', ['get', 'impact'], 'corridor']);
			map.setLayoutProperty('parking-lines-color', 'visibility', 'visible');
			map.setPaintProperty('parking-lines-color', 'line-opacity', 0.45);
		} else if (step?.showNewDesign) {
			map.setLayoutProperty('parking-lines-color', 'visibility', 'none');
		}
		// Non-new-design steps: applyStepVisibility handles visibility
	}

	onMount(async () => {
		const maplibregl = await import('maplibre-gl');

		map = new maplibregl.default.Map({
			container: mapContainer,
			style: {
				version: 8,
				name: 'Dark Basemap',
				sources: {
					'carto-dark': {
						type: 'raster',
						tiles: [
							'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
							'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
							'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'
						],
						tileSize: 256,
						attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
					}
				},
				layers: [
					{
						id: 'carto-dark-layer',
						type: 'raster',
						source: 'carto-dark',
						minzoom: 0,
						maxzoom: 20
					}
				],
				glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf'
			},
			center: [44.5036, 40.1735],
			zoom: 11.8,
			pitch: 0,
			bearing: 0,
			maxZoom: 18,
			minZoom: 10
		});

		map.addControl(new maplibregl.default.NavigationControl(), 'top-right');
		mapInstance.set(map);

		map.on('load', async () => {
			// Load all data sources
			const [linesData, areasData, corridorsData, boundariesData, landmarksData, newDesignData, sensitivityData, fieldSurveysData, fieldYardsData] = await Promise.all([
				fetch('/data/wgs84/parking-lines.geojson').then(r => r.json()),
				fetch('/data/wgs84/parking-areas.geojson').then(r => r.json()),
				fetch('/data/wgs84/corridors.geojson').then(r => r.json()),
				fetch('/data/wgs84/corridor-boundaries.geojson').then(r => r.json()),
				fetch('/data/wgs84/landmarks.geojson').then(r => r.json()),
				fetch('/data/wgs84/new-design-parking.geojson').then(r => r.json()),
				fetch('/data/wgs84/sensitivity-zones.geojson').then(r => r.json()),
				fetch('/data/wgs84/field-surveys.geojson').then(r => r.json()),
				fetch('/data/wgs84/field-survey-yards.geojson').then(r => r.json()),
			]);

			// Per-area dashboard numbers travel inside the field-surveys file.
			fieldSurveyStats.set(fieldSurveysData.areaStats ?? null);
			// Per-zone demand profiles (hourly curve + stay split), keyed "area:zone",
			// for the click popups. Captured here so the popup builder can read them.
			const zoneProfiles = fieldSurveysData.zoneProfiles ?? {};

			// Parse "Space: N" from each area's HTML description into a numeric `space`
			// property (so popups and labels can read it directly), then flag the top N
			// lots by capacity for the highlight step.
			for (const f of areasData.features) {
				const html = f.properties.description?.value || '';
				const m = html.match(/Space:\s*(\d+)/i);
				f.properties.space = m ? parseInt(m[1], 10) : 0;
				// Mall/City/Tonavachar in name = commercial; everything else (mostly Yard###) = yard.
				f.properties.category = /mall|city|tonavachar/i.test(f.properties.name || '') ? 'commercial' : 'yard';
			}
			// All commercial lots pin regardless of size; yards are capped to top N by space.
			const withSpace = areasData.features.filter(f => f.properties.space > 0);
			const topYards = withSpace
				.filter(f => f.properties.category === 'yard')
				.sort((a, b) => b.properties.space - a.properties.space)
				.slice(0, MAX_TOP_LOTS);
			topYards.forEach((f, i) => {
				f.properties.top = true;
				f.properties.topRank = i + 1;
			});
			const commercials = withSpace.filter(f => f.properties.category === 'commercial');
			commercials.forEach((f) => {
				f.properties.top = true;
				f.properties.topRank = 0; // commercials ignore the slider
			});
			const topFeatures = [...topYards, ...commercials];

			// Always-on DOM markers for top lots — bbox center of the polygon as anchor.
			for (const f of topFeatures) {
				const ring = f.geometry.coordinates[0];
				let minLng = Infinity, maxLng = -Infinity, minLat = Infinity, maxLat = -Infinity;
				for (const c of ring) {
					if (c[0] < minLng) minLng = c[0];
					if (c[0] > maxLng) maxLng = c[0];
					if (c[1] < minLat) minLat = c[1];
					if (c[1] > maxLat) maxLat = c[1];
				}
				const center = [(minLng + maxLng) / 2, (minLat + maxLat) / 2];

				const el = document.createElement('div');
				el.className = `top-lot-marker top-lot-marker--${f.properties.category}`;
				el.style.display = 'none';
				el.innerHTML = `
					<div class="top-lot-pin"></div>
					<div class="top-lot-card">
						<span class="top-lot-name">${f.properties.name ?? ''}</span>
						<span class="top-lot-spaces"><strong>${f.properties.space}</strong> spaces</span>
					</div>
				`;

				const marker = new maplibregl.default.Marker({ element: el, anchor: 'bottom' })
					.setLngLat(center)
					.addTo(map);
				marker._rank = f.properties.topRank;
				marker._category = f.properties.category;
				topMarkers.push(marker);
			}

			// Tag each parking-line as a Displacement "unsurveyed nearby absorber" (yellow):
			// buffer/yard impact, >20 m from every survey path (so not already shown by the
			// survey layers), and within 100 m of some area's survey FOOTPRINT (the bbox of
			// that area's survey paths) — so a lot behind the surveyed blocks still counts,
			// while genuinely distant lots stay out. Mirrors the same test in
			// compute_field_survey_metrics.mjs so the map and the dashboard numbers agree.
			{
				const SURVEY_NEAR = 20, AREA_MAX = 100;
				const LAT0 = 40.18, MX = Math.cos((LAT0 * Math.PI) / 180) * 111320, MY = 110540;
				const toXY = ([lng, lat]) => [lng * MX, lat * MY];
				const ptSeg = (p, a, b) => {
					const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
					let t = L ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L : 0;
					t = t < 0 ? 0 : t > 1 ? 1 : t;
					return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
				};
				const ptBox = (p, b) => {
					const dx = Math.max(b.x0 - p[0], 0, p[0] - b.x1);
					const dy = Math.max(b.y0 - p[1], 0, p[1] - b.y1);
					return Math.hypot(dx, dy);
				};
				const segs = [];
				const boxes = {};
				for (const f of fieldSurveysData.features) {
					const pts = f.geometry.coordinates.map(toXY);
					for (let i = 1; i < pts.length; i++) segs.push([pts[i - 1], pts[i]]);
					const b = (boxes[f.properties.area] ??= { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity });
					for (const [x, y] of pts) { b.x0 = Math.min(b.x0, x); b.y0 = Math.min(b.y0, y); b.x1 = Math.max(b.x1, x); b.y1 = Math.max(b.y1, y); }
				}
				const boxList = Object.values(boxes);
				for (const f of linesData.features) {
					const imp = f.properties.impact;
					if (imp !== 'buffer' && imp !== 'yard') { f.properties._absorber = false; continue; }
					const cs = f.geometry.type === 'LineString' ? f.geometry.coordinates : f.geometry.coordinates.flat();
					const pts = cs.map(toXY);
					let mPath = Infinity, mBox = Infinity;
					for (const p of pts) {
						for (const s of segs) { const d = ptSeg(p, s[0], s[1]); if (d < mPath) mPath = d; }
						for (const b of boxList) { const d = ptBox(p, b); if (d < mBox) mBox = d; }
					}
					f.properties._absorber = mPath > SURVEY_NEAR && mBox <= AREA_MAX;
				}
				// Tag off-street yard POLYGONS (parking-areas) the same way: an unsurveyed lot
				// within AREA_MAX of some area footprint is a counted off-street absorber
				// (yellow). The six surveyed yards are excluded (shown green for context).
				const SURVEYED_YARDS = new Set(['KomitasCity', 'ShirazYard010', 'GNOFF', 'Palace', 'SebastiaYard006', 'NalbandyanYard001']);
				const areaSpace = (p) => { const s = (p.description && (p.description.value || p.description)) || ''; const m = String(s).match(/Space:?\s*(\d+)/i); return m ? +m[1] : 0; };
				for (const f of areasData.features) {
					if (SURVEYED_YARDS.has(f.properties.name) || !areaSpace(f.properties)) { f.properties._absorber = false; continue; }
					const ring = f.geometry.type === 'Polygon' ? f.geometry.coordinates.flat() : f.geometry.coordinates.flat(2);
					let mBox = Infinity;
					for (const c of ring) { const p = toXY(c); for (const b of boxList) { const d = ptBox(p, b); if (d < mBox) mBox = d; } }
					f.properties._absorber = mBox <= AREA_MAX;
				}
			}

			map.addSource('parking-lines', { type: 'geojson', data: linesData, generateId: true });
			map.addSource('parking-areas', { type: 'geojson', data: areasData, generateId: true });
			map.addSource('corridors', { type: 'geojson', data: corridorsData });
			map.addSource('corridor-boundaries', { type: 'geojson', data: boundariesData });
			map.addSource('landmarks', { type: 'geojson', data: landmarksData });
			map.addSource('new-design-parking', { type: 'geojson', data: newDesignData });
			map.addSource('sensitivity-zones', { type: 'geojson', data: sensitivityData });
			map.addSource('field-surveys', { type: 'geojson', data: fieldSurveysData, generateId: true });
			map.addSource('field-survey-yards', { type: 'geojson', data: fieldYardsData, generateId: true });

			// Add all layers
			for (const layer of ALL_LAYERS) {
				map.addLayer(layer);
			}

			// Yellow absorbers = the unsurveyed nearby parking-lines tagged above. Reused as
			// the parking-lines-hit filter so only those yellow lines are clickable in the
			// Displacement lens.
			dispAbsorberFilter = ['==', ['get', '_absorber'], true];
			map.setFilter('displacement-absorbers', dispAbsorberFilter);

			geojsonData.set({
				lines: linesData.features,
				areas: areasData.features
			});

			// Shared popup builder for parking features
			function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''; }
			// Mini hourly-curve + stay-length viz for a zone's click popup (built as inline
			// HTML so it lives inside the maplibre popup). Mirrors the always-on stats-board
			// profile but for the single clicked zone.
			function miniProfile(prof) {
				if (!prof) return '';
				let html = '';
				if (prof.vap?.length) {
					const max = Math.max(...prof.vap.map((x) => x[1])) || 1;
					const peakH = prof.vap.reduce((b, x) => (x[1] > b[1] ? x : b))[0];
					const bars = prof.vap.map(([h, v]) =>
						`<div title="${h}:00 — ${v} vehicles" style="flex:1;min-height:2px;height:${Math.max(2, (v / max) * 34)}px;background:${h === peakH ? '#00e5ff' : 'rgba(0,206,209,0.5)'};border-radius:2px 2px 0 0"></div>`
					).join('');
					const first = prof.vap[0][0], last = prof.vap[prof.vap.length - 1][0];
					html += `<div style="margin-top:8px;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.55">Hourly occupancy · peaks ${peakH}:00</div>
						<div style="display:flex;align-items:flex-end;gap:1px;height:36px;margin-top:4px">${bars}</div>
						<div style="display:flex;justify-content:space-between;font-size:9px;opacity:0.45;margin-top:2px"><span>${first}:00</span><span>${last}:00</span></div>`;
				}
				if (prof.stay) {
					const { short = 0, errand = 0, worker = 0, allday = 0 } = prof.stay;
					const tot = short + errand + worker + allday || 1;
					const sp = Math.round((short / tot) * 100), ep = Math.round((errand / tot) * 100),
						wp = Math.round((worker / tot) * 100), ap = 100 - sp - ep - wp;
					html += `<div style="margin-top:8px;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;opacity:0.55">Stay length · avg ${prof.avg}h</div>
						<div style="display:flex;height:8px;border-radius:4px;overflow:hidden;margin-top:4px;background:rgba(255,255,255,0.08)">
							<div style="width:${sp}%;background:#00e5ff"></div><div style="width:${ep}%;background:#ffd60a"></div><div style="width:${wp}%;background:#ff9f1c"></div><div style="width:${ap}%;background:#ff6b6b"></div>
						</div>
						<div style="font-size:9px;opacity:0.6;margin-top:4px">≤1h ${sp}% · 2–4h ${ep}% · 5–8h ${wp}% · &gt;8h ${ap}%</div>`;
				}
				return html;
			}

			function showParkingPopup(e, color, showSurveyMetrics = false) {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const rows = [];
				if (p.snippet) rows.push(`<div style="font-size:11px;opacity:0.6;margin-bottom:2px">${p.snippet}</div>`);
				if (p.space) rows.push(`<div>Spaces: <strong>${p.space}</strong></div>`);
				if (p.regulation) rows.push(`<div>Regulation: ${cap(p.regulation)}</div>`);
				if (p.method) rows.push(`<div>Method: ${cap(p.method)}</div>`);
				if (p.location) rows.push(`<div>Location: ${cap(p.location)}</div>`);
				if (p.marking) rows.push(`<div>Marking: ${cap(p.marking)}</div>`);
				if (p.signage) rows.push(`<div>Signage: ${cap(p.signage)}</div>`);
				// Survey-derived occupancy metrics — shown only on the Field Surveys and
				// Parking Occupancy steps (not in the Parking Regulation step's area popups).
				if (showSurveyMetrics && p.occupancy_pct != null && p.occupancy_pct !== '') {
					const occ = Number(p.occupancy_pct);
					const occColor = occ <= 90 ? '#2ecc71' : occ <= 102 ? '#ff8a8a' : '#ff1f44';
					rows.push(`<div>Avg occupancy: <strong style="color:${occColor}">${occ}%</strong> of capacity</div>`);
				}
				if (showSurveyMetrics && p.turnover != null && p.turnover !== '') rows.push(`<div>Turnover: ${p.turnover} vehicles/space</div>`);
				if (showSurveyMetrics && p.avg_duration_h != null && p.avg_duration_h !== '') rows.push(`<div>Avg stay: ${p.avg_duration_h} h</div>`);
				// Per-zone hourly curve + stay split (on-street survey paths only).
				if (showSurveyMetrics && p.area != null && p.zone != null) {
					rows.push(miniProfile(zoneProfiles[`${p.area}:${p.zone}`]));
				}
				if (p.administration) rows.push(`<div>Administration: ${cap(p.administration)}</div>`);
				if (p.impact) rows.push(`<div>Impact: ${cap(p.impact)}</div>`);
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `
					<div style="font-weight:600;color:${color};margin-bottom:4px">${p.name}</div>
					${rows.join('')}
				`;
				new maplibregl.default.Popup({ closeButton: true, maxWidth: '260px' })
					.setLngLat(e.lngLat)
					.setDOMContent(el)
					.addTo(map);
			}

			// Popups for parking lines (via hit layer for reliable clicking)
			map.on('click', 'parking-lines-hit', (e) => showParkingPopup(e, '#42a5f5'));

			// Popups for parking areas
			map.on('click', 'parking-areas-fill', (e) => showParkingPopup(e, '#7c4dff'));

			// Popups for field-survey paths — show the survey occupancy metrics
			map.on('click', 'field-surveys-hit', (e) => showParkingPopup(e, '#00e5ff', true));

			// Popup for the off-street yards (KomitasCity / ShirazYard010 / GNOFF / Palace) — shows occupancy analysis
			map.on('click', 'field-survey-yard-fill', (e) => showParkingPopup(e, '#7c4dff', true));

			// Popups for corridors
			map.on('click', 'corridors-line', (e) => {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `<div style="font-weight:600;color:#ffaa00;margin-bottom:4px">${p.name}</div>`;
				new maplibregl.default.Popup({ closeButton: true, maxWidth: '220px' })
					.setLngLat(e.lngLat)
					.setDOMContent(el)
					.addTo(map);
			});

			// Popups for post-BRT corridor segments
			map.on('click', 'new-design-hit', (e) => {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const color = p.folder === 'Corridor 1' ? '#F9A825' : '#0288D1';
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `
					<div style="font-weight:600;color:${color};margin-bottom:4px">${p.name}</div>
					<div>Corridor: <strong>${p.folder}</strong></div>
					${p.spaces != null ? `<div>Spaces retained: <strong>${p.spaces}</strong></div>` : ''}
				`;
				new maplibregl.default.Popup({ closeButton: true, maxWidth: '240px' })
					.setLngLat(e.lngLat)
					.setDOMContent(el)
					.addTo(map);
			});

			// Popups for landmarks
			map.on('click', 'landmarks-points', (e) => {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `
					<div style="font-weight:600;color:#FFC107;margin-bottom:4px">${p.name}</div>
					${p.note ? `<div style="font-size:12px;opacity:0.8">${p.note}</div>` : ''}
				`;
				new maplibregl.default.Popup({ closeButton: true, maxWidth: '220px' })
					.setLngLat(e.lngLat)
					.setDOMContent(el)
					.addTo(map);
			});

			// Hover cursors
			for (const layerId of ['parking-lines-hit', 'parking-areas-fill', 'landmarks-points', 'corridors-line', 'new-design-hit', 'field-surveys-hit', 'field-survey-yard-fill']) {
				map.on('mouseenter', layerId, () => { map.getCanvas().style.cursor = 'pointer'; });
				map.on('mouseleave', layerId, () => { map.getCanvas().style.cursor = ''; });
			}

			// Line hover highlight
			let hoveredLineId = null;
			for (const layerId of ['parking-lines-hit']) {
				map.on('mousemove', layerId, (e) => {
					if (e.features?.length) {
						if (hoveredLineId !== null) {
							map.setFeatureState({ source: 'parking-lines', id: hoveredLineId }, { hover: false });
						}
						hoveredLineId = e.features[0].id;
						map.setFeatureState({ source: 'parking-lines', id: hoveredLineId }, { hover: true });
					}
				});
				map.on('mouseleave', layerId, () => {
					if (hoveredLineId !== null) {
						map.setFeatureState({ source: 'parking-lines', id: hoveredLineId }, { hover: false });
						hoveredLineId = null;
					}
				});
			}

			// Re-evaluate which surveyed area the dashboard reports on after every
			// camera move (only acts while the Field Surveys step is active).
			map.on('moveend', updateFieldSurveyArea);

			dataLoaded.set(true);
			currentStepIdx = $currentStep;
			applyStepVisibility($currentStep);
			updateFieldSurveyArea();
		});

		return () => {
			if (map) map.remove();
		};
	});

	// React to step changes. applyStepVisibility() reads the field-survey lens/retained
	// stores internally; without untrack() this effect would subscribe to them and
	// re-fire (with moveCamera defaulting to true) on every toggle, flying the camera
	// back to the step's wide view. untrack() keeps this effect bound to step changes
	// only — the lens/retained toggles are handled by their own no-camera effect below.
	$effect(() => {
		const step = $currentStep;
		currentStepIdx = step;
		if (map && $dataLoaded) {
			untrack(() => {
				applyStepVisibility(step);
				// Entering a non-survey step? Reset to the combined view so the next time
				// the survey step is shown it starts on 'all' until the camera settles.
				if (!STORY_STEPS[step]?.showFieldSurveys) fieldSurveyArea.set('all');
				else updateFieldSurveyArea();
			});
		}
	});

	// React to legend filter toggles
	$effect(() => {
		const filters = $activeLegendFilters;
		if (map && $dataLoaded) {
			applyLegendFilter(filters);
		}
	});

	// React to current-parking overlay toggle (also re-runs on step change)
	$effect(() => {
		const step = $currentStep;
		const showCurrent = $showCurrentParking;
		if (map && $dataLoaded) {
			applyCurrentParkingOverlay(step, showCurrent);
		}
	});

	// Sensitivity zones visibility — only shown when the toggle is on
	$effect(() => {
		const show = $showSensitivityZones;
		if (!map || !$dataLoaded) return;
		map.setLayoutProperty('sensitivity-zones', 'visibility', show ? 'visible' : 'none');
	});

	// Field-survey coloring mode toggle (occupancy / paid-free / retained) —
	// re-apply the step so the right survey-path layer and yard styling show.
	$effect(() => {
		const mode = $fieldSurveyMode;
		const retained = $fieldSurveyRetained;
		if (map && $dataLoaded) {
			// Keep the camera where the reader left it (locked into a survey location).
			applyStepVisibility($currentStep, false);
		}
	});

	// Top-lot marker visibility — depends on the active step, the slider value,
	// and the category toggle set. Commercials ignore the slider; only yard rank is capped.
	$effect(() => {
		const step = $currentStep;
		const count = $topLotsCount;
		const cats = $topLotsCategories;
		if (!map || !$dataLoaded) return;
		const isTopStep = STORY_STEPS[step]?.colorMode === 'top';
		for (const m of topMarkers) {
			const passesRank = m._category === 'commercial' || m._rank <= count;
			const visible = isTopStep && cats.has(m._category) && passesRank;
			m.getElement().style.display = visible ? 'flex' : 'none';
		}
	});
</script>

<div class="map-container" bind:this={mapContainer}></div>

<style>
	.map-container {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
	}

	:global(.maplibregl-popup-content) {
		background: rgba(15, 15, 25, 0.92) !important;
		color: #e0e0e0 !important;
		border: 1px solid rgba(255, 255, 255, 0.12);
		border-radius: 8px !important;
		padding: 12px 14px !important;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		line-height: 1.5;
		backdrop-filter: blur(12px);
	}

	:global(.maplibregl-popup-tip) {
		border-top-color: rgba(15, 15, 25, 0.92) !important;
	}

	:global(.maplibregl-popup-close-button) {
		color: #aaa !important;
		font-size: 18px;
		padding: 2px 6px;
	}

	:global(.maplibregl-ctrl-group) {
		background: rgba(15, 15, 25, 0.8) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		backdrop-filter: blur(8px);
	}

	:global(.maplibregl-ctrl-group button) {
		filter: invert(1);
	}

	:global(.top-lot-marker) {
		--pin: #00e5ff;
		display: flex;
		align-items: flex-end;
		gap: 6px;
		font-family: 'Inter', sans-serif;
		pointer-events: none;
	}

	:global(.top-lot-marker--commercial) {
		--pin: #ff4dd2;
	}

	:global(.top-lot-pin) {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--pin);
		border: 2px solid #fff;
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--pin) 25%, transparent), 0 2px 6px rgba(0, 0, 0, 0.55);
		flex-shrink: 0;
		margin-bottom: 6px;
	}

	:global(.top-lot-card) {
		display: inline-flex;
		flex-direction: column;
		gap: 2px;
		background: rgba(10, 10, 20, 0.92);
		border: 1px solid color-mix(in srgb, var(--pin) 45%, transparent);
		border-radius: 6px;
		padding: 5px 9px;
		white-space: nowrap;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(6px);
		line-height: 1.25;
	}

	:global(.top-lot-name) {
		font-size: 11px;
		font-weight: 600;
		color: #ffffff;
		letter-spacing: 0.1px;
	}

	:global(.top-lot-spaces) {
		font-size: 11px;
		color: var(--pin);
		font-variant-numeric: tabular-nums;
	}

	:global(.top-lot-spaces strong) {
		font-size: 13px;
		font-weight: 700;
	}
</style>
