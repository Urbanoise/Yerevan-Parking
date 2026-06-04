<script>
	import { currentStep } from '$lib/stores/storyStore.js';
	import { activeLegendFilters, topLotsCount, topLotsCategories, showCurrentParking, showSensitivityZones, fieldSurveyMode } from '$lib/stores/mapStore.js';
	import { STORY_STEPS } from '$lib/config/story.js';

	let stepConfig = $derived(STORY_STEPS[$currentStep] || {});
	let legendLayers = $derived(stepConfig.legendLayers || []);
	let legendGroups = $derived(stepConfig.legendGroups || []);
	let allLayers = $derived([...legendLayers, ...(legendGroups.flatMap(g => g.layers))]);
	let legendVisible = $derived(stepConfig.legendVisible ?? false);
	let topSlider = $derived(stepConfig.topSlider ?? false);
	let topSliderOptions = $derived(stepConfig.topSliderOptions ?? [10, 20, 30, 50]);
	let topSliderIndex = $derived(Math.max(0, topSliderOptions.indexOf($topLotsCount)));

	let topCategoryFilter = $derived(stepConfig.topCategoryFilter ?? false);
	let topCategories = $derived(stepConfig.topCategories ?? []);
	let showCurrentToggle = $derived(stepConfig.showCurrentToggle ?? false);
	let showSensitivityToggle = $derived(stepConfig.showSensitivityToggle ?? false);
	// Field-survey lens toggle: a 3-way mode selector (occupancy / paid-free /
	// retained). The active mode supplies the static key shown below the toggle.
	let fieldModes = $derived(stepConfig.fieldModes ?? null);
	let activeFieldMode = $derived(fieldModes ? (fieldModes.find(m => m.id === $fieldSurveyMode) || fieldModes[0]) : null);
	let staticKey = $derived(activeFieldMode ? activeFieldMode.staticKey : (stepConfig.staticKey ?? null));

	function onTopSliderInput(e) {
		const idx = Number(e.target.value);
		topLotsCount.set(topSliderOptions[idx]);
	}

	function toggleCategory(id) {
		topLotsCategories.update((current) => {
			const next = new Set(current);
			if (next.has(id)) {
				if (next.size === 1) return next; // keep at least one active
				next.delete(id);
			} else {
				next.add(id);
			}
			return next;
		});
	}

	// Reset filters whenever the step changes
	$effect(() => {
		const stepId = $currentStep;
		const step = STORY_STEPS.find(s => s.index === stepId);
		if (step) {
			const activeLayers = [...(step.legendLayers || []), ...(step.legendGroups?.flatMap(g => g.layers) || [])];
			if (activeLayers.some(l => l.activeByDefault !== undefined)) {
				const defaults = activeLayers.filter(l => l.activeByDefault !== false).map(l => l.id);
				activeLegendFilters.set(new Set(defaults));
			} else {
				activeLegendFilters.set(null);
			}
			if (!step.showSensitivityToggle) {
				showSensitivityZones.set(false);
			}
			// Reset the field-survey lens to the step's default when entering it.
			if (step.fieldModes) {
				fieldSurveyMode.set(step.defaultFieldMode ?? step.fieldModes[0].id);
			}
		} else {
			activeLegendFilters.set(null);
			showSensitivityZones.set(false);
		}
	});

	function toggle(id) {
		activeLegendFilters.update((current) => {
			// Start from a full set if null
			const all = new Set(allLayers.map((l) => l.id));
			const active = current === null ? new Set(all) : new Set(current);

			if (active.has(id)) {
				active.delete(id);
			} else {
				active.add(id);
			}

			// If everything is active again, collapse back to null (no filter)
			if (active.size === all.size) return null;
			return active;
		});
	}

	function isActive(id) {
		return $activeLegendFilters === null || $activeLegendFilters.has(id);
	}
</script>

{#if (legendVisible && allLayers.length > 0) || topSlider || topCategoryFilter || showCurrentToggle || showSensitivityToggle || staticKey || fieldModes}
	<div class="legend-panel">
		{#if fieldModes}
			<div class="legend-title">View <span class="legend-hint">switch lens</span></div>
			<div class="mode-toggle">
				{#each fieldModes as mode}
					<button
						class="mode-btn"
						class:active={$fieldSurveyMode === mode.id}
						onclick={() => fieldSurveyMode.set(mode.id)}
						aria-pressed={$fieldSurveyMode === mode.id}
					>{mode.label}</button>
				{/each}
			</div>
		{/if}

		{#if staticKey}
			<div class="legend-title">{staticKey.title}</div>
			{#each staticKey.items as item}
				<div class="legend-item legend-item--static">
					<span class="legend-swatch" style="background-color: {item.color}"></span>
					<span class="legend-label">{item.label}</span>
				</div>
			{/each}
		{/if}

		{#if legendVisible && allLayers.length > 0}
			<div class="legend-title">Legend <span class="legend-hint">click to filter</span></div>
			{#if legendLayers.length > 0}
				{#each legendLayers as layer}
					<button
						class="legend-item"
						class:inactive={!isActive(layer.id)}
						onclick={() => toggle(layer.id)}
						title={isActive(layer.id) ? `Hide ${layer.label}` : `Show ${layer.label}`}
					>
						<span class="legend-swatch" style="background-color: {layer.color}"></span>
						<span class="legend-label">{layer.label}</span>
					</button>
				{/each}
			{/if}

			{#each legendGroups as group}
				<div class="legend-group-title">{group.title}</div>
				{#each group.layers as layer}
					<button
						class="legend-item"
						class:inactive={!isActive(layer.id)}
						onclick={() => toggle(layer.id)}
						title={isActive(layer.id) ? `Hide ${layer.label}` : `Show ${layer.label}`}
					>
						<span class="legend-swatch" style="background-color: {layer.color}"></span>
						<span class="legend-label">{layer.label}</span>
					</button>
				{/each}
			{/each}
		{/if}

		{#if topCategoryFilter}
			<div class="legend-title">Lot type <span class="legend-hint">click to filter</span></div>
			{#each topCategories as cat}
				<button
					class="legend-item"
					class:inactive={!$topLotsCategories.has(cat.id)}
					onclick={() => toggleCategory(cat.id)}
					title={$topLotsCategories.has(cat.id) ? `Hide ${cat.label}` : `Show ${cat.label}`}
				>
					<span class="legend-swatch" style="background-color: {cat.color}"></span>
					<span class="legend-label">{cat.label}</span>
				</button>
			{/each}
		{/if}

		{#if showCurrentToggle}
			<div class="legend-divider"></div>
			<div class="current-toggle-row">
				<span class="legend-label">Current parking</span>
				<button
					class="legend-toggle-switch"
					class:on={$showCurrentParking}
					onclick={() => showCurrentParking.update(v => !v)}
					aria-pressed={$showCurrentParking}
					aria-label="Toggle current parking overlay"
				>
					<span class="legend-toggle-thumb"></span>
				</button>
			</div>
		{/if}

		{#if showSensitivityToggle}
			<div class="legend-divider"></div>
			<div class="current-toggle-row">
				<span class="legend-label">Sensitivity zones</span>
				<button
					class="legend-toggle-switch"
					class:on={$showSensitivityZones}
					onclick={() => showSensitivityZones.update(v => !v)}
					aria-pressed={$showSensitivityZones}
					aria-label="Toggle sensitivity zones"
				>
					<span class="legend-toggle-thumb"></span>
				</button>
			</div>
			{#if $showSensitivityZones}
				<div class="sensitivity-key">
					{#each [['No Parking','#9e9e9e'],['Low','#66bb6a'],['Moderate','#ffee58'],['Medium','#f57c00'],['High','#d32f2f']] as [label, color]}
						<div class="sensitivity-item">
							<span class="sensitivity-swatch" style="background:{color}"></span>
							<span class="sensitivity-label">{label}</span>
						</div>
					{/each}
				</div>
			{/if}
		{/if}

		{#if topSlider}
			<div class="legend-title legend-title-sub">Show top <span class="top-count">{$topLotsCount}</span> yards</div>
			<input
				class="top-slider"
				type="range"
				min="0"
				max={topSliderOptions.length - 1}
				step="1"
				value={topSliderIndex}
				oninput={onTopSliderInput}
			/>
			<div class="top-ticks">
				{#each topSliderOptions as opt}
					<span class:active={opt === $topLotsCount}>{opt}</span>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	.mode-toggle {
		display: flex;
		gap: 4px;
		margin-bottom: 14px;
		padding: 3px;
		background: rgba(255, 255, 255, 0.06);
		border-radius: 9px;
	}

	.mode-btn {
		flex: 1;
		padding: 6px 8px;
		background: none;
		border: none;
		border-radius: 6px;
		color: rgba(255, 255, 255, 0.55);
		font-family: 'Inter', sans-serif;
		font-size: 0.72rem;
		font-weight: 500;
		line-height: 1.2;
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}

	.mode-btn:hover {
		color: rgba(255, 255, 255, 0.85);
	}

	.mode-btn.active {
		background: #00CED1;
		color: #06121a;
		font-weight: 600;
	}

	.sensitivity-key {
		margin-top: 8px;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.sensitivity-item {
		display: flex;
		align-items: center;
		gap: 7px;
	}

	.sensitivity-swatch {
		width: 18px;
		height: 4px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.sensitivity-label {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.65);
	}

	.legend-divider {
		height: 1px;
		background: rgba(255, 255, 255, 0.08);
		margin: 10px -16px;
	}

	.current-toggle-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		padding: 2px 0;
	}

	.legend-toggle-switch {
		position: relative;
		width: 34px;
		height: 19px;
		background: rgba(255, 255, 255, 0.15);
		border: none;
		border-radius: 10px;
		cursor: pointer;
		padding: 0;
		flex-shrink: 0;
		transition: background 0.2s ease;
	}

	.legend-toggle-switch.on {
		background: #42a5f5;
	}

	.legend-toggle-thumb {
		position: absolute;
		top: 2.5px;
		left: 2.5px;
		width: 14px;
		height: 14px;
		background: #fff;
		border-radius: 50%;
		transition: transform 0.2s ease;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
	}

	.legend-toggle-switch.on .legend-toggle-thumb {
		transform: translateX(15px);
	}
	.legend-panel {
		position: fixed;
		bottom: 24px;
		right: 16px;
		z-index: 20;
		background: rgba(10, 10, 20, 0.88);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 12px;
		backdrop-filter: blur(16px);
		padding: 14px 16px;
		min-width: 180px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
	}

	.legend-title {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.8px;
		color: rgba(255, 255, 255, 0.4);
		margin-bottom: 10px;
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.legend-hint {
		font-size: 0.6rem;
		text-transform: none;
		letter-spacing: 0;
		color: rgba(255, 255, 255, 0.22);
		font-style: italic;
	}

	.legend-group-title {
		font-size: 0.65rem;
		color: rgba(255, 255, 255, 0.5);
		text-transform: uppercase;
		margin-top: 14px;
		margin-bottom: 6px;
		font-weight: 500;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 5px 6px;
		margin: 0 -6px;
		width: calc(100% + 12px);
		background: none;
		border: none;
		border-radius: 7px;
		cursor: pointer;
		transition: background 0.15s, opacity 0.2s;
		text-align: left;
	}

	.legend-item:hover {
		background: rgba(255, 255, 255, 0.07);
	}

	.legend-item--static {
		cursor: default;
	}

	.legend-item--static:hover {
		background: none;
	}

	.legend-item.inactive {
		opacity: 0.35;
	}

	.legend-item.inactive .legend-swatch {
		filter: grayscale(1);
	}

	.legend-swatch {
		width: 12px;
		height: 12px;
		border-radius: 3px;
		flex-shrink: 0;
		transition: filter 0.2s;
	}

	.legend-label {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.75);
	}

	.legend-title-sub {
		margin-top: 12px;
	}

	.top-count {
		color: #00e5ff;
		font-weight: 700;
		font-size: 0.78rem;
		margin-left: 4px;
	}

	.top-slider {
		-webkit-appearance: none;
		appearance: none;
		width: 100%;
		height: 4px;
		background: rgba(255, 255, 255, 0.15);
		border-radius: 2px;
		outline: none;
		margin: 4px 0 6px;
		cursor: pointer;
	}

	.top-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: #00e5ff;
		border: 2px solid #fff;
		box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.25);
		cursor: pointer;
	}

	.top-slider::-moz-range-thumb {
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: #00e5ff;
		border: 2px solid #fff;
		box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.25);
		cursor: pointer;
	}

	.top-ticks {
		display: flex;
		justify-content: space-between;
		font-size: 0.7rem;
		color: rgba(255, 255, 255, 0.4);
		font-variant-numeric: tabular-nums;
	}

	.top-ticks span {
		transition: color 0.15s;
	}

	.top-ticks span.active {
		color: #00e5ff;
		font-weight: 700;
	}
</style>
