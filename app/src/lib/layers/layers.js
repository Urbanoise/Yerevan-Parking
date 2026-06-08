// Invisible wide hit area for clicking parking lines
export const PARKING_LINES_HIT = {
	id: 'parking-lines-hit',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': 'transparent',
		'line-width': 16,
		'line-opacity': 0
	},
	layout: {
		visibility: 'none'
	}
};

// Parking lines — on-street segments
export const PARKING_LINES = {
	id: 'parking-lines',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': '#42a5f5',
		'line-width': 3,
		'line-opacity': 0.85
	},
	layout: {
		visibility: 'none'
	}
};

// Method-colored lines
export const PARKING_LINES_METHOD = {
	id: 'parking-lines-method',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'method'],
			'parallel', '#4CAF50',
			'90', '#FF9800',
			'45', '#E91E63',
			'#4CAF50'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Signage-colored lines
export const PARKING_LINES_SIGNAGE = {
	id: 'parking-lines-signage',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'signage'],
			'yes', '#4CAF50',
			'no', '#EF5350',
			'#888888'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Marking-colored lines
export const PARKING_LINES_MARKING = {
	id: 'parking-lines-marking',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'marking'],
			'yes', '#4CAF50',
			/* default / no */ '#EF5350'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Location-colored lines
export const PARKING_LINES_LOCATION = {
	id: 'parking-lines-location',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'location'],
			'on-street', '#42a5f5',
			'pocket', '#ab47bc',
			'set-back', '#ffaa00',
			'#42a5f5'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Color-zone-colored lines
export const PARKING_LINES_COLOR = {
	id: 'parking-lines-color',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'color'],
			'white', '#ffffff',
			'red', '#EF5350',
			'blue', '#42a5f5',
			'black', '#888888',
			'#666666'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Impact-colored lines
export const PARKING_LINES_IMPACT = {
	id: 'parking-lines-impact',
	type: 'line',
	source: 'parking-lines',
	paint: {
		'line-color': [
			'match',
			['get', 'impact'],
			'corridor', '#ffaa00',
			'buffer', '#00aa00',
			'yard', '#55aaff',
			'#888888'
		],
		'line-width': 3.5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

// Parking areas — off-street fill
export const PARKING_AREAS_FILL = {
	id: 'parking-areas-fill',
	type: 'fill',
	source: 'parking-areas',
	paint: {
		'fill-color': '#7c4dff',
		'fill-opacity': 0.35
	},
	layout: {
		visibility: 'none'
	}
};

// Impact-colored areas
export const PARKING_AREAS_FILL_IMPACT = {
	id: 'parking-areas-fill-impact',
	type: 'fill',
	source: 'parking-areas',
	paint: {
		'fill-color': [
			'match',
			['get', 'impact'],
			'corridor', '#ffaa00',
			'buffer', '#00aa00',
			'yard', '#55aaff',
			'#7c4dff'
		],
		'fill-opacity': 0.35
	},
	layout: {
		visibility: 'none'
	}
};

// Parking areas — outline
export const PARKING_AREAS_OUTLINE = {
	id: 'parking-areas-outline',
	type: 'line',
	source: 'parking-areas',
	paint: {
		'line-color': '#7c4dff',
		'line-width': 1.5,
		'line-opacity': 0.6
	},
	layout: {
		visibility: 'none'
	}
};

// Corridor routes
export const CORRIDORS_LINE = {
	id: 'corridors-line',
	type: 'line',
	source: 'corridors',
	paint: {
		'line-color': [
			'match',
			['get', 'name'],
			'Corridor 01', '#ffaa00',
			'Corridor 02', '#55aaff',
			'Corridor 03', '#00aa00',
			'#ffffff'
		],
		'line-width': 5,
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none',
		'line-cap': 'round',
		'line-join': 'round'
	}
};

// Corridor boundaries
export const CORRIDOR_BOUNDARIES_FILL = {
	id: 'corridor-boundaries-fill',
	type: 'fill',
	source: 'corridor-boundaries',
	paint: {
		'fill-color': '#ff0000',
		'fill-opacity': 0.06
	},
	layout: {
		visibility: 'none'
	}
};

export const CORRIDOR_BOUNDARIES_OUTLINE = {
	id: 'corridor-boundaries-outline',
	type: 'line',
	source: 'corridor-boundaries',
	paint: {
		'line-color': '#ff0000',
		'line-width': 2,
		'line-opacity': 0.4,
		'line-dasharray': [4, 3]
	},
	layout: {
		visibility: 'none'
	}
};

// Landmarks
export const LANDMARKS_POINTS = {
	id: 'landmarks-points',
	type: 'circle',
	source: 'landmarks',
	paint: {
		'circle-color': '#FFC107',
		'circle-radius': 8,
		'circle-stroke-color': '#fff',
		'circle-stroke-width': 2,
		'circle-opacity': 0.9
	},
	layout: {
		visibility: 'none'
	}
};

export const LANDMARKS_LABELS = {
	id: 'landmarks-labels',
	type: 'symbol',
	source: 'landmarks',
	layout: {
		'text-field': ['get', 'name'],
		'text-size': 12,
		'text-offset': [0, 1.5],
		'text-anchor': 'top',
		'text-font': ['Open Sans Regular', 'Arial Unicode MS Regular'],
		visibility: 'none'
	},
	paint: {
		'text-color': '#FFC107',
		'text-halo-color': 'rgba(0,0,0,0.8)',
		'text-halo-width': 1.5
	}
};

// Post-BRT individual parking bays (kz folder)
export const NEW_DESIGN_KZ = {
	id: 'new-design-kz',
	type: 'line',
	source: 'new-design-parking',
	filter: ['==', ['get', 'folder'], 'kz'],
	paint: {
		'line-color': '#9C0072',
		'line-width': 1.8,
		'line-opacity': 0.75
	},
	layout: { visibility: 'none' }
};

// Post-BRT corridor street segments (Corridor 1 & 2), width ∝ space count
export const NEW_DESIGN_CORRIDORS = {
	id: 'new-design-corridors',
	type: 'line',
	source: 'new-design-parking',
	filter: ['in', ['get', 'folder'], ['literal', ['Corridor 1', 'Corridor 2']]],
	paint: {
		'line-color': [
			'match', ['get', 'folder'],
			'Corridor 1', '#F9A825',
			'Corridor 2', '#0288D1',
			'#aaaaaa'
		],
		'line-width': ['interpolate', ['linear'], ['coalesce', ['get', 'spaces'], 1], 1, 3, 50, 10],
		'line-opacity': 0.9
	},
	layout: {
		visibility: 'none',
		'line-cap': 'round',
		'line-join': 'round'
	}
};

// Invisible hit area for corridor segment clicks
export const NEW_DESIGN_HIT = {
	id: 'new-design-hit',
	type: 'line',
	source: 'new-design-parking',
	filter: ['in', ['get', 'folder'], ['literal', ['Corridor 1', 'Corridor 2']]],
	paint: {
		'line-color': 'transparent',
		'line-width': 16,
		'line-opacity': 0
	},
	layout: { visibility: 'none' }
};

// Sensitivity zones — colored by parking demand level
export const SENSITIVITY_ZONES = {
	id: 'sensitivity-zones',
	type: 'line',
	source: 'sensitivity-zones',
	paint: {
		'line-color': [
			'match', ['get', 'sensitivity'],
			'No Parking', '#9e9e9e',
			'Low',        '#66bb6a',
			'Moderate',   '#ffee58',
			'Medium',     '#f57c00',
			'High',       '#d32f2f',
			'#aaaaaa'
		],
		'line-width': 6,
		'line-opacity': 0.85
	},
	layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' }
};

// Field Surveys — renamed "(Zone NN)" survey paths across all four surveyed areas,
// colored by parking regulation (same palette as the Parking Regulation step).
export const FIELD_SURVEYS_LINES = {
	id: 'field-surveys-lines',
	type: 'line',
	source: 'field-surveys',
	paint: {
		'line-color': [
			'match', ['get', 'regulation'],
			'white', '#ffffff',
			'red', '#EF5350',
			'blue', '#42a5f5',
			'black', '#888888',
			'#ffffff'
		],
		'line-width': 4,
		'line-opacity': 0.9
	},
	layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' }
};

// Occupancy ramp shared by the glow + line layers below. ~85–90% is the healthy
// "sweet spot" for on-street parking (full enough to be efficient, with just
// enough turnover to find a space), so everything up to 90% stays green; above
// 90% it grades green → yellow → orange → red as the street oversaturates and
// vehicles spill onto footpaths/setbacks. On the dark CARTO basemap all anchors
// stay bright so severity pops. Past 90% it goes straight to red shades (no
// yellow/orange) — light red just over the line, deepening to intense red as the
// street oversaturates. The 90→94 band is kept tight so the green→red blend
// doesn't muddy. occupancy_pct comes from compute_field_survey_metrics.mjs.
// occupancy_pct is now a full-day AVERAGE (mean vehicles present ÷ legal spaces),
// so the real range is ~30–113%: most zones have daily slack, a couple sit over
// 100% (chronic overflow). The ramp stays green up to the 90% sweet-spot top,
// then grades straight to red across 90→115% where the over-capacity zones live.
export const OCCUPANCY_COLOR = [
	'interpolate', ['linear'], ['coalesce', ['get', 'occupancy_pct'], 0],
	0, '#2ecc71',     // empty → green
	90, '#2ecc71',    // top of the sweet spot — still green
	94, '#ff8a8a',    // just over — light red
	103, '#ff4d4d',   // over capacity
	113, '#ff1f44',   // chronic overflow — vivid red (the busiest zone)
	140, '#d50000'    // headroom for re-runs — intense red
];
const OCCUPANCY_WIDTH = [
	'interpolate', ['linear'], ['coalesce', ['get', 'occupancy_pct'], 0],
	30, 3,
	70, 4,
	95, 5.5,
	115, 7.5
];

// Soft blurred halo beneath the occupancy lines — makes oversaturated streets
// glow on the dark basemap and draws the eye to the hotspots.
export const FIELD_SURVEYS_OCCUPANCY_GLOW = {
	id: 'field-surveys-occupancy-glow',
	type: 'line',
	source: 'field-surveys',
	paint: {
		'line-color': OCCUPANCY_COLOR,
		'line-width': ['*', OCCUPANCY_WIDTH, 2.4],
		'line-blur': 8,
		'line-opacity': [
			// Only the over-capacity zones glow, scaling in above 95%.
			'interpolate', ['linear'], ['coalesce', ['get', 'occupancy_pct'], 0],
			95, 0,
			105, 0.4,
			113, 0.65
		]
	},
	layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' }
};

export const FIELD_SURVEYS_OCCUPANCY = {
	id: 'field-surveys-occupancy',
	type: 'line',
	source: 'field-surveys',
	paint: {
		'line-color': OCCUPANCY_COLOR,
		'line-width': OCCUPANCY_WIDTH,
		'line-opacity': 0.95
	},
	layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' }
};

// Invisible wide hit area for clicking field-survey paths
export const FIELD_SURVEYS_HIT = {
	id: 'field-surveys-hit',
	type: 'line',
	source: 'field-surveys',
	paint: {
		'line-color': 'transparent',
		'line-width': 16,
		'line-opacity': 0
	},
	layout: { visibility: 'none' }
};

// Off-street yards shown alongside the Field Surveys paths — one per area:
// KomitasCity (123), ShirazYard010 (71), GNOFF (40, Garegin Nzhdeh) and Palace
// (32, Mega Mall). Geometry, capacity and measured occupancy come from the
// dedicated field-survey-yards.geojson (built by convert/compute). Uses the same
// purple as off-street areas in the Parking Regulation step (#7c4dff).
export const FIELD_SURVEY_YARD_FILL = {
	id: 'field-survey-yard-fill',
	type: 'fill',
	source: 'field-survey-yards',
	paint: {
		'fill-color': '#7c4dff',
		'fill-opacity': 0.35
	},
	layout: { visibility: 'none' }
};

export const FIELD_SURVEY_YARD_OUTLINE = {
	id: 'field-survey-yard-outline',
	type: 'line',
	source: 'field-survey-yards',
	paint: {
		'line-color': '#7c4dff',
		'line-width': 2,
		'line-opacity': 0.9
	},
	layout: { visibility: 'none', 'line-join': 'round' }
};

export const ALL_LAYERS = [
	PARKING_AREAS_FILL,
	PARKING_AREAS_FILL_IMPACT,
	PARKING_AREAS_OUTLINE,
	PARKING_LINES,
	PARKING_LINES_METHOD,
	PARKING_LINES_SIGNAGE,
	PARKING_LINES_MARKING,
	PARKING_LINES_LOCATION,
	PARKING_LINES_COLOR,
	PARKING_LINES_IMPACT,
	PARKING_LINES_HIT,
	CORRIDOR_BOUNDARIES_FILL,
	CORRIDOR_BOUNDARIES_OUTLINE,
	CORRIDORS_LINE,
	LANDMARKS_POINTS,
	LANDMARKS_LABELS,
	NEW_DESIGN_KZ,
	NEW_DESIGN_CORRIDORS,
	NEW_DESIGN_HIT,
	SENSITIVITY_ZONES,
	FIELD_SURVEYS_LINES,
	FIELD_SURVEYS_OCCUPANCY_GLOW,
	FIELD_SURVEYS_OCCUPANCY,
	FIELD_SURVEYS_HIT,
	FIELD_SURVEY_YARD_FILL,
	FIELD_SURVEY_YARD_OUTLINE,
];
