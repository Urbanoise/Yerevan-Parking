export const STORY_STEPS = [
	{
		index: 0,
		title: 'Yerevan Parking Supply',
		subtitle: 'A spatial inventory of on-street and off-street parking across the city',
		isIntro: true,
		center: [44.5036, 40.1735],
		zoom: 11.8,
		pitch: 0,
		bearing: 0,
		showLines: false,
		showAreas: false,
		showCorridors: false,
		showLandmarks: false,
		legendVisible: false,
	},
	{
		index: 1,
		title: 'Study Corridors',
		subtitle: 'Three primary routes of analysis',
		center: [44.505, 40.165],
		zoom: 12.8,
		pitch: 20,
		bearing: 0,
		showLines: false,
		showAreas: false,
		showCorridors: true,
		showLandmarks: false,
		colorMode: 'default',
		legendVisible: true,
		legendLayers: [
			{ id: 'corridor-1', label: 'Corridor 01', color: '#ffaa00' },
			{ id: 'corridor-2', label: 'Corridor 02', color: '#55aaff' },
			{ id: 'corridor-3', label: 'Corridor 03', color: '#00aa00' },
		],
	},
	{
		index: 2,
		title: 'Parking Regulation',
		subtitle: 'Parking zones by color',
		center: [44.505, 40.175],
		zoom: 13.5,
		pitch: 35,
		bearing: 0,
		showLines: true,
		showAreas: true,
		showCorridors: false,
		showLandmarks: false,
		colorMode: 'color',
		legendVisible: true,
		legendGroups: [
			{
				title: 'Regulation Zones',
				layers: [
					{ id: 'white', label: 'White', color: '#ffffff', activeByDefault: true },
					{ id: 'red', label: 'Red', color: '#EF5350', activeByDefault: true },
					{ id: 'blue', label: 'Blue', color: '#42a5f5', activeByDefault: true },
					{ id: 'black', label: 'Taxi', color: '#888888', activeByDefault: true },
				]
			},
			{
				title: 'Impact Area',
				layers: [
					{ id: 'corridor', label: 'Corridor', color: '#ffaa00', activeByDefault: true },
					{ id: 'buffer', label: 'Buffer', color: '#00aa00', activeByDefault: false },
					{ id: 'yard', label: 'Yard', color: '#55aaff', activeByDefault: false },
				]
			}
		],
		stats: [
			{ value: 6144, label: 'Free Parking Spaces', color: '#ffffff' },
			{ value: 260, label: 'Red Spaces', color: '#EF5350' },
			{ value: 534, label: 'Blue Spaces', color: '#42a5f5' },
			{ value: 67, label: 'Taxi Spaces', color: '#888888' },
		],
	},
	{
		index: 3,
		title: 'Parking Methods',
		subtitle: 'How vehicles are arranged',
		center: [44.513, 40.175],
		zoom: 14.5,
		pitch: 35,
		bearing: 10,
		showLines: true,
		showAreas: true,
		colorMode: 'method',
		legendVisible: true,
		legendGroups: [
			{
				title: 'Parking Methods',
				layers: [
					{ id: 'parallel', label: 'Parallel', color: '#4CAF50', activeByDefault: true },
					{ id: '90', label: '90-Degree', color: '#FF9800', activeByDefault: true },
					{ id: '45', label: '45-Degree', color: '#E91E63', activeByDefault: true },
				]
			},
			{
				title: 'Impact Area',
				layers: [
					{ id: 'corridor', label: 'Corridor', color: '#ffaa00', activeByDefault: true },
					{ id: 'buffer', label: 'Buffer', color: '#00aa00', activeByDefault: false },
					{ id: 'yard', label: 'Yard', color: '#55aaff', activeByDefault: false },
				]
			}
		],
	},
	{
		index: 4,
		title: 'Parking Signage',
		subtitle: 'Is there a parking sign?',
		center: [44.512, 40.177],
		zoom: 14.2,
		pitch: 35,
		bearing: -5,
		showLines: true,
		showAreas: true,
		colorMode: 'signage',
		legendVisible: true,
		legendGroups: [
			{
				title: 'Signage Coverage',
				layers: [
					{ id: 'yes', label: 'Yes', color: '#4CAF50', activeByDefault: true },
					{ id: 'no', label: 'No', color: '#EF5350', activeByDefault: true },
				]
			},
			{
				title: 'Impact Area',
				layers: [
					{ id: 'corridor', label: 'Corridor', color: '#ffaa00', activeByDefault: true },
					{ id: 'buffer', label: 'Buffer', color: '#00aa00', activeByDefault: false },
					{ id: 'yard', label: 'Yard', color: '#55aaff', activeByDefault: false },
				]
			}
		],
	},
	{
		index: 5,
		title: 'Parking Marking',
		subtitle: 'Is there a pavement marking?',
		center: [44.502, 40.174],
		zoom: 14,
		pitch: 20,
		bearing: 15,
		showLines: true,
		showAreas: true,
		colorMode: 'marking',
		legendVisible: true,
		legendGroups: [
			{
				title: 'Marking Presence',
				layers: [
					{ id: 'yes', label: 'Marked', color: '#4CAF50', activeByDefault: true },
					{ id: 'no', label: 'Unmarked', color: '#EF5350', activeByDefault: true },
				]
			},
			{
				title: 'Impact Area',
				layers: [
					{ id: 'corridor', label: 'Corridor', color: '#ffaa00', activeByDefault: true },
					{ id: 'buffer', label: 'Buffer', color: '#00aa00', activeByDefault: false },
					{ id: 'yard', label: 'Yard', color: '#55aaff', activeByDefault: false },
				]
			}
		],
	},
	{
		index: 6,
		title: 'Parking Location',
		subtitle: 'Physical boundaries and zones',
		center: [44.505, 40.180],
		zoom: 14,
		pitch: 45,
		bearing: -10,
		showLines: true,
		showAreas: true,
		colorMode: 'location',
		legendVisible: true,
		legendGroups: [
			{
				title: 'Physical Location',
				layers: [
					{ id: 'on-street', label: 'On-Street', color: '#42a5f5', activeByDefault: true },
					{ id: 'pocket', label: 'Pocket', color: '#ab47bc', activeByDefault: true },
					{ id: 'set-back', label: 'Set-back', color: '#ffaa00', activeByDefault: true },
				]
			},
			{
				title: 'Impact Area',
				layers: [
					{ id: 'corridor', label: 'Corridor', color: '#ffaa00', activeByDefault: true },
					{ id: 'buffer', label: 'Buffer', color: '#00aa00', activeByDefault: false },
					{ id: 'yard', label: 'Yard', color: '#55aaff', activeByDefault: false },
				]
			}
		],
	},
	{
		index: 7,
		title: 'Top Off-Street Lots',
		subtitle: 'The 20 largest yards by capacity',
		center: [44.5036, 40.1735],
		zoom: 12.4,
		pitch: 0,
		bearing: 0,
		showLines: false,
		showAreas: false,
		showCorridors: true,
		showLandmarks: false,
		colorMode: 'top',
		legendVisible: false,
		legendLayers: [
			{ id: 'corridor-1', label: 'Corridor 01', color: '#ffaa00' },
			{ id: 'corridor-2', label: 'Corridor 02', color: '#55aaff' },
			{ id: 'corridor-3', label: 'Corridor 03', color: '#00aa00' },
		],
		topSlider: true,
		topSliderOptions: [10, 20, 30, 50],
		topCategoryFilter: true,
		topCategories: [
			{ id: 'yard', label: 'Yards (residential)', color: '#00e5ff' },
			{ id: 'commercial', label: 'Commercial (Mall / City)', color: '#ff4dd2' },
		],
	},
	{
		index: 8,
		title: 'Post-BRT Parking Index',
		subtitle: 'Spaces retained after BRT corridor introduction',
		center: [44.505, 40.178],
		zoom: 12.4,
		pitch: 0,
		bearing: 0,
		showLines: false,
		showAreas: false,
		showCorridors: false,
		showLandmarks: false,
		showNewDesign: true,
		showCurrentToggle: true,
		showSensitivityToggle: true,
		colorMode: 'new-design',
		legendVisible: true,
		legendLayers: [
			{ id: 'new-c1', label: 'Corridor 01', color: '#F9A825' },
			{ id: 'new-c2', label: 'Corridor 02', color: '#0288D1' },
		],
		stats: [
			{ value: 1012, label: 'Total Retained', color: '#4CAF50' },
			{ value: 522, label: 'Corridor 01', color: '#F9A825' },
			{ value: 490, label: 'Corridor 02', color: '#0288D1' },
		],
		comparison: { current: 7005, retained: 1012 },
	},
	{
		index: 9,
		title: 'Field Surveys',
		subtitle: 'Survey paths across six areas — zoom in to compare',
		center: [44.516, 40.178],
		zoom: 11.6,
		pitch: 0,
		bearing: 0,
		showLines: false,
		showAreas: false,
		showCorridors: false,
		showLandmarks: false,
		showFieldSurveys: true,
		legendVisible: false,
		// Merged Field Surveys step. The renamed "(Zone NN)" survey paths span six
		// areas — Malatia-Sebastia (zones 2–24), Garegin Nzhdeh (25–59), Gai Avenue
		// (60–69), Komitas (70–122), Shiraz/Hasratyan (123–156) and Kentron (lettered
		// "(Zone K01)" tags) — each with its off-street yard (SebastiaYard006 / GNOFF /
		// Palace / KomitasCity / ShirazYard010 / NalbandyanYard001). Three lenses,
		// switched with a toggle in the legend panel: average daily occupancy, parking
		// regulation (paid/free), and the post-BRT retain/remove decision. Each mode
		// carries its own colorMode, static key, stats and description; defaultFieldMode
		// sets the initial view. The stats below are fallbacks — live dashboard numbers
		// are viewport-aware and resolved from the areaStats embedded in
		// field-surveys.geojson as the reader zooms between areas.
		fieldSurveyToggle: true,
		defaultFieldMode: 'occupancy',
		fieldModes: [
			{
				id: 'occupancy',
				label: 'Avg Occupancy',
				colorMode: 'field-occupancy',
				staticKey: {
					title: 'Avg occupancy (% of capacity)',
					items: [
						{ label: '≤85% — within capacity', color: '#2ecc71' },
						{ label: '86–100% — at capacity', color: '#ff8a8a' },
						{ label: '>100% — over capacity', color: '#ff4d4d' },
						{ label: 'Dashed purple outline — off-street yard', color: '#7c4dff' },
					],
				},
				stats: [
					{ value: 93, label: 'Peak Occupancy % (cap-weighted)', color: '#2ecc71' },
					{ value: 69, label: '% Zones Over 85% (Peak)', color: '#ffa600' },
					{ value: 116, label: 'Zones Over Capacity', color: '#ff1f44' },
				],
			},
			{
				id: 'displacement',
				label: 'Displacement',
				// Its own map view: surviving SURVEYED parking (green = retained survey zones)
				// plus the UNSURVEYED nearby capacity (yellow = buffer/yard parking-lines >20 m
				// from any survey path & within 150 m) and the off-street yards. Surveyed streets
				// that are removed are dropped, not re-counted as absorbers. The stat panel
				// carries the numbers; fallback stats mirror the 'all' block.
				colorMode: 'field-displacement',
				staticKey: {
					title: 'Parking displacement',
					items: [
						{ label: 'Surviving surveyed parking', color: '#2ecc71' },
						{ label: 'Unsurveyed on-street', color: '#ffd60a' },
						{ label: 'Off-street yard', color: '#7c4dff' },
					],
				},
				stats: [
					{ value: 908, label: 'Cars Displaced (Peak Hour)', color: '#EF5350' },
					{ value: 1643, label: 'Spaces Removed', color: '#b0455a' },
					{ value: 391, label: 'Nearby On-Street', color: '#ffd60a' },
					{ value: 1935, label: 'Nearby Off-Street', color: '#7c4dff' },
					{ value: 43, label: '% Absorbed On-Street', color: '#ffd60a' },
					{ value: 100, label: '% Absorbed Total', color: '#00e5ff' },
				],
			},
		],
	},
];
