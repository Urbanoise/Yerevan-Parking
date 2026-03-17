<script>
	import { onMount } from 'svelte';
	import { mapInstance, dataLoaded, activeFilter, showAreas, showLines, activeLegendFilters } from '$lib/stores/mapStore.js';
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

		// Areas
		const showA = s.showAreas ?? false;
		map.setLayoutProperty('parking-areas-fill', 'visibility', showA ? 'visible' : 'none');
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
		const active = filters === null
			? (step.legendLayers ? new Set(step.legendLayers.map(l => l.id)) : new Set())
			: filters;

		// 1. Reset all filters if filters are null (switching steps or "show all")
		if (filters === null) {
			map.setFilter('parking-lines-method', null);
			map.setFilter('parking-lines-signage', null);
			map.setFilter('corridors-line', null);
			map.setFilter('corridor-boundaries-fill', null);
			map.setFilter('corridor-boundaries-outline', null);
		}

		// 2. Handle Corridor Mode (Check this before default colorMode because it has colorMode: 'default' but special layers)
		if (step.showCorridors) {
			const idToName = { 'corridor-1': 'Corridor 01', 'corridor-2': 'Corridor 02', 'corridor-3': 'Corridor 03' };
			const selected = step.legendLayers
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

		// 3. Handle Method/Signage modes
		if (colorMode === 'method') {
			const idToMethod = { 'parallel': 'parallel', 'angle-90': '90', 'angle-45': '45' };
			const selected = step.legendLayers
				.filter(l => active.has(l.id))
				.map(l => idToMethod[l.id])
				.filter(Boolean);
			map.setFilter('parking-lines-method', selected.length === 0 ? ['==', ['get', 'method'], '__none__'] : ['in', ['get', 'method'], ['literal', selected]]);
			return;
		}

		if (colorMode === 'signage') {
			const idToSignage = { 'signed': 'yes', 'unsigned': 'no' };
			const selected = step.legendLayers
				.filter(l => active.has(l.id))
				.map(l => idToSignage[l.id])
				.filter(Boolean);
			map.setFilter('parking-lines-signage', selected.length === 0 ? ['==', ['get', 'signage'], '__none__'] : ['in', ['get', 'signage'], ['literal', selected]]);
			return;
		}

		// 4. Handle Default Mode (Direct visibility toggles)
		if (colorMode === 'default' && step.legendLayers) {
			for (const layer of step.legendLayers) {
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

			// Popups for parking lines
			map.on('click', 'parking-lines', (e) => {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `
					<div style="font-weight:600;color:#42a5f5;margin-bottom:4px">${p.name}</div>
					${p.spaces > 0 ? `<div>Spaces: <strong>${p.spaces}</strong></div>` : ''}
					${p.method !== 'unknown' ? `<div>Method: ${p.method}</div>` : ''}
					${p.location !== 'unknown' ? `<div>Location: ${p.location}</div>` : ''}
					${p.signage !== 'unknown' ? `<div>Signage: ${p.signage}</div>` : ''}
				`;
				new maplibregl.default.Popup({ closeButton: true, maxWidth: '240px' })
					.setLngLat(e.lngLat)
					.setDOMContent(el)
					.addTo(map);
			});

			// Popups for parking areas
			map.on('click', 'parking-areas-fill', (e) => {
				if (!e.features?.length) return;
				const p = e.features[0].properties;
				const el = document.createElement('div');
				el.className = 'map-popup';
				el.innerHTML = `
					<div style="font-weight:600;color:#7c4dff;margin-bottom:4px">${p.name}</div>
					${p.spaces > 0 ? `<div>Spaces: <strong>${p.spaces}</strong></div>` : ''}
				`;
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
			for (const layerId of ['parking-lines', 'parking-lines-method', 'parking-lines-signage', 'parking-areas-fill', 'landmarks-points']) {
				map.on('mouseenter', layerId, () => { map.getCanvas().style.cursor = 'pointer'; });
				map.on('mouseleave', layerId, () => { map.getCanvas().style.cursor = ''; });
			}

			// Line hover highlight
			let hoveredLineId = null;
			for (const layerId of ['parking-lines', 'parking-lines-method', 'parking-lines-signage']) {
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
