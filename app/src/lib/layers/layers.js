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
];
