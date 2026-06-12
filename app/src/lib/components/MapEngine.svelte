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
		map.setLayoutProperty('field-surveys-lines', 'visibility', fsReg ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-occupancy-glow', 'visibility', fsOcc ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-occupancy', 'visibility', fsOcc ? 'visible' : 'none');
		map.setLayoutProperty('field-surveys-hit', 'visibility', showFS ? 'visible' : 'none');
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
		// as the survey paths; in paid/free keep its off-street purple.
		map.setPaintProperty('field-survey-yard-fill', 'fill-color', fsOcc ? OCCUPANCY_COLOR : '#7c4dff');
		map.setPaintProperty('field-survey-yard-fill', 'fill-opacity', fsOcc ? 0.55 : 0.35);
		// Keep the off-street purple (#7c4dff, same as other indexes) on the border in
		// the occupancy lens — dashed there so the shaded yard still reads as an
		// off-street facility (not an on-street path); solid purple otherwise.
		map.setPaintProperty('field-survey-yard-outline', 'line-color', '#7c4dff');
		map.setPaintProperty('field-survey-yard-outline', 'line-width', fsOcc ? 3 : 2);
		map.setPaintProperty('field-survey-yard-outline', 'line-dasharray', fsOcc ? [2, 1.5] : [1]);

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
			
			geojsonData.set({
				lines: linesData.features,
				areas: areasData.features
			});

			// Shared popup builder for parking features
			function cap(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''; }
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
