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
		description: 'The parking survey was structured around three major corridors spanning north-south and east-west through the city, capturing the diversity of parking conditions.',
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
		description: 'Parking zones are color-coded to indicate regulation level. White zones are free, red and blue zones are paid, respectively Zona A and Zone B, and black zones are dedicated to Taxi drivers only.',
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
		description: 'Parallel parking dominates Yerevan\'s streets. Angled parking (90° and 45°) appears in pockets and set-back areas.',
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
		description: 'Only a fraction of on-street parking spaces have formal signage. The majority of parking in Yerevan is informal — drivers park where convention allows, not where signs direct.',
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
		description: 'Visible ground marking explicitly formalizes parking boundaries. Notice how specific locations carry strict lane paints against generic areas.',
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
		description: 'The geography of parking: on-street edges, deep structural pockets off the traffic flow, and setback spaces reserved in building curtilages.',
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
		description: 'Together, these lots account for the bulk of off-street capacity in the surveyed area. The study corridors and their buffer zones are shown for context — drag the slider to change how many of the largest lots are pinned, or toggle between residential yards and commercial lots.',
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
		subtitle: 'Survey paths across four areas — zoom in to compare',
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
		// Merged Field Surveys step. The renamed "(Zone NN)" survey paths span four
		// areas — Garegin Nzhdeh (zones 25–59), Mega Mall (60–69), Komitas (70–122) and
		// Shiraz/Hasratyan (123–156) — each with its off-street yard (GNOFF / Palace /
		// KomitasCity / ShirazYard010). They can be viewed through three lenses,
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
						{ label: '≤90% — within capacity', color: '#2ecc71' },
						{ label: '~95% — at capacity', color: '#ff8a8a' },
						{ label: '~105% — over capacity', color: '#ff4d4d' },
						{ label: '110%+ — chronic overflow', color: '#ff1f44' },
						{ label: 'Dashed purple outline — off-street yard', color: '#7c4dff' },
					],
				},
				stats: [
					{ value: 55, label: 'Mean Occupancy %', color: '#2ecc71' },
					{ value: 10, label: 'Zones Over Capacity', color: '#ff1f44' },
					{ value: 63, label: 'Zones Under 50% (slack)', color: '#cddc39' },
					{ value: 24, label: 'Parked Off-Carriageway %', color: '#00e5ff' },
				],
			},
			{
				id: 'paidfree',
				label: 'Paid / Free',
				colorMode: 'field-surveys',
				staticKey: {
					title: 'Parking Regulation',
					items: [
						{ label: 'White — Free', color: '#ffffff' },
						{ label: 'Blue — Paid', color: '#42a5f5' },
						{ label: 'Yard — Off-street', color: '#7c4dff' },
					],
				},
				stats: [
					{ value: 126, label: 'Survey Paths', color: '#00e5ff' },
					{ value: 1133, label: 'White Spaces', color: '#ffffff' },
					{ value: 276, label: 'Blue Spaces', color: '#42a5f5' },
					{ value: 266, label: 'Off-Street Yards', color: '#7c4dff' },
				],
			},
			{
				id: 'retained',
				label: 'Retained / Removed',
				// Rendered as a standalone switch bar below the lens segment, not a lens.
				// When on, it hides the paths removed by the BRT redesign from whichever
				// lens (avg occupancy / paid-free) is active; the survivors keep their
				// lens colouring. Its stats/key describe the retained network.
				isSwitch: true,
				staticKey: {
					title: 'Retained network — avg occupancy',
					items: [
						{ label: '≤90% — within capacity', color: '#2ecc71' },
						{ label: '~95% — at capacity', color: '#ff8a8a' },
						{ label: '~105% — over capacity', color: '#ff4d4d' },
						{ label: '110%+ — chronic overflow', color: '#ff1f44' },
						{ label: 'Dashed purple outline — off-street yard', color: '#7c4dff' },
					],
				},
				stats: [
					{ value: 1301, label: 'Retained Spaces', color: '#4CAF50' },
					{ value: 108, label: 'Removed Spaces', color: '#EF5350' },
					{ value: 92, label: '% Spaces Retained', color: '#4CAF50' },
					{ value: 112, label: 'Retained Paths', color: '#00e5ff' },
				],
			},
		],
	},
];
