<script>
	import { onMount } from 'svelte';
	import { mapInstance, dataLoaded, activeFilter, showAreas, showLines, activeLegendFilters, geojsonData } from '$lib/stores/mapStore.js';
	import { currentStep } from '$lib/stores/storyStore.js';
	import { ALL_LAYERS } from '$lib/layers/layers.js';
	import { STORY_STEPS } from '$lib/config/story.js';

	let mapContainer;
	let map = null;

	function applyStepVisibility(step) {
		if (!map || !$dataLoaded) return;

		const s = STORY_STEPS[step];
		if (!s) return;

		// Lines
		const showL = s.showLines ?? false;
		const colorMode = s.colorMode ?? 'default';

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

		// Corridors
		const showC = s.showCorridors ?? false;
		map.setLayoutProperty('corridors-line', 'visibility', showC ? 'visible' : 'none');
		map.setLayoutProperty('corridor-boundaries-fill', 'visibility', showC ? 'visible' : 'none');
		map.setLayoutProperty('corridor-boundaries-outline', 'visibility', showC ? 'visible' : 'none');

		// Landmarks
		const showLm = s.showLandmarks ?? false;
		map.setLayoutProperty('landmarks-points', 'visibility', showLm ? 'visible' : 'none');
		map.setLayoutProperty('landmarks-labels', 'visibility', showLm ? 'visible' : 'none');

		// Camera
		map.easeTo({
			center: s.center,
			zoom: s.zoom,
			pitch: s.pitch ?? 0,
			bearing: s.bearing ?? 0,
			duration: 1200,
			easing: (t) => t * (2 - t)
		});
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
			const [linesData, areasData, corridorsData, boundariesData, landmarksData] = await Promise.all([
				fetch('/data/wgs84/parking-lines.geojson').then(r => r.json()),
				fetch('/data/wgs84/parking-areas.geojson').then(r => r.json()),
				fetch('/data/wgs84/corridors.geojson').then(r => r.json()),
				fetch('/data/wgs84/corridor-boundaries.geojson').then(r => r.json()),
				fetch('/data/wgs84/landmarks.geojson').then(r => r.json()),
			]);

			map.addSource('parking-lines', { type: 'geojson', data: linesData, generateId: true });
			map.addSource('parking-areas', { type: 'geojson', data: areasData, generateId: true });
			map.addSource('corridors', { type: 'geojson', data: corridorsData });
			map.addSource('corridor-boundaries', { type: 'geojson', data: boundariesData });
			map.addSource('landmarks', { type: 'geojson', data: landmarksData });

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
			function showParkingPopup(e, color) {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const rows = [];
				if (p.snippet) rows.push(`<div style="font-size:11px;opacity:0.6;margin-bottom:2px">${p.snippet}</div>`);
				if (p.space) rows.push(`<div>Spaces: <strong>${p.space}</strong></div>`);
				if (p.method) rows.push(`<div>Method: ${cap(p.method)}</div>`);
				if (p.location) rows.push(`<div>Location: ${cap(p.location)}</div>`);
				if (p.marking) rows.push(`<div>Marking: ${cap(p.marking)}</div>`);
				if (p.signage) rows.push(`<div>Signage: ${cap(p.signage)}</div>`);
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
			for (const layerId of ['parking-lines-hit', 'parking-areas-fill', 'landmarks-points', 'corridors-line']) {
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

			dataLoaded.set(true);
			applyStepVisibility($currentStep);
		});

		return () => {
			if (map) map.remove();
		};
	});

	// React to step changes
	$effect(() => {
		const step = $currentStep;
		if (map && $dataLoaded) {
			applyStepVisibility(step);
		}
	});

	// React to legend filter toggles
	$effect(() => {
		const filters = $activeLegendFilters;
		if (map && $dataLoaded) {
			applyLegendFilter(filters);
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
</style>
