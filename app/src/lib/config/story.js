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
					{ id: 'white', label: 'White (8,082)', color: '#ffffff', activeByDefault: true },
					{ id: 'red', label: 'Red (386)', color: '#EF5350', activeByDefault: true },
					{ id: 'blue', label: 'Blue (625)', color: '#42a5f5', activeByDefault: true },
					{ id: 'black', label: 'Taxi (75)', color: '#888888', activeByDefault: true },
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
			{ value: 8082, label: 'Free Parking Spaces', color: '#ffffff' },
			{ value: 386, label: 'Red Spaces', color: '#EF5350' },
			{ value: 625, label: 'Blue Spaces', color: '#42a5f5' },
			{ value: 75, label: 'Taxi Spaces', color: '#888888' },
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
		title: 'Busiest Streets',
		subtitle: 'Where parking supply concentrates',
		center: [44.497, 40.17],
		zoom: 13.5,
		pitch: 40,
		bearing: 15,
		showLines: true,
		showAreas: true,
		showCorridors: false,
		showLandmarks: false,
		colorMode: 'default',
		legendVisible: true,
		legendLayers: [
			{ id: 'on-street', label: 'On-Street Parking', color: '#42a5f5', layerId: 'parking-lines' },
			{ id: 'off-street', label: 'Off-Street / Yards', color: '#7c4dff', layerId: 'parking-areas-fill' },
		],
		topStreets: [
			{ name: 'Arshakunyac', spaces: 1012, type: 'yard' },
			{ name: 'Komitas', spaces: 871, type: 'yard' },
			{ name: 'Bagratunyac', spaces: 695, type: 'yard' },
			{ name: 'Komitas', spaces: 507, type: 'street' },
			{ name: 'Rubinyan', spaces: 485, type: 'street' },
			{ name: 'Shiraz', spaces: 446, type: 'yard' },
			{ name: 'Sebastia', spaces: 442, type: 'yard' },
		],
		description: 'Arshakunyac Avenue leads with over 1,000 yard-parking spaces. Komitas Avenue has the highest combined supply — 507 on-street plus 871 in courtyards.',
	},
	{
		index: 8,
		title: 'Key Landmarks',
		subtitle: 'Major destinations with parking impact',
		center: [44.51, 40.19],
		zoom: 13,
		pitch: 25,
		bearing: 0,
		showLines: true,
		showAreas: true,
		showCorridors: false,
		showLandmarks: true,
		colorMode: 'default',
		legendVisible: true,
		legendLayers: [
			{ id: 'on-street', label: 'On-Street Parking', color: '#42a5f5', layerId: 'parking-lines' },
			{ id: 'off-street', label: 'Off-Street / Yards', color: '#7c4dff', layerId: 'parking-areas-fill' },
			{ id: 'landmarks', label: 'Landmarks', color: '#FFC107', layerId: 'landmarks-points' },
		],
		description: 'Major malls and institutions — Mega Mall, Yerevan City Mall, the Sport/Concert Complex — generate significant parking demand, each with their own off-street facilities.',
	},
];
