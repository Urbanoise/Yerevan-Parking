<script>
	import { currentStep } from '$lib/stores/storyStore.js';
	import { activeLegendFilters } from '$lib/stores/mapStore.js';
	import { STORY_STEPS } from '$lib/config/story.js';

	let legendLayers = $derived(STORY_STEPS[$currentStep]?.legendLayers ?? []);
	let legendVisible = $derived(STORY_STEPS[$currentStep]?.legendVisible ?? false);

	// Reset filters whenever the step changes
	$effect(() => {
		$currentStep;
		activeLegendFilters.set(null);
	});

	function toggle(id) {
		activeLegendFilters.update((current) => {
			// Start from a full set if null
			const all = new Set(legendLayers.map((l) => l.id));
			const active = current === null ? new Set(all) : new Set(current);

			if (active.has(id)) {
				active.delete(id);
			} else {
				active.add(id);
			}

			// If everything is active again, collapse back to null (no filter)
			if (active.size === all.size) return null;
			// If nothing is active, keep one item active (prevent blank map)
			if (active.size === 0) { active.add(id); return active; }
			return active;
		});
	}

	function isActive(id) {
		return $activeLegendFilters === null || $activeLegendFilters.has(id);
	}
</script>

{#if legendVisible && legendLayers.length > 0}
	<div class="legend-panel">
		<div class="legend-title">Legend <span class="legend-hint">click to filter</span></div>
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
	</div>
{/if}

<style>
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
</style>
