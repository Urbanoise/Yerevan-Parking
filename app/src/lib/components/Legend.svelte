<script>
	import { currentStep } from '$lib/stores/storyStore.js';
	import { STORY_STEPS } from '$lib/config/story.js';

	let legendLayers = $derived(STORY_STEPS[$currentStep]?.legendLayers ?? []);
	let legendVisible = $derived(STORY_STEPS[$currentStep]?.legendVisible ?? false);
</script>

{#if legendVisible && legendLayers.length > 0}
	<div class="legend-panel">
		<div class="legend-title">Legend</div>
		{#each legendLayers as layer}
			<div class="legend-item">
				<span class="legend-swatch" style="background-color: {layer.color}"></span>
				<span class="legend-label">{layer.label}</span>
			</div>
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
		min-width: 160px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
	}

	.legend-title {
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.8px;
		color: rgba(255, 255, 255, 0.4);
		margin-bottom: 10px;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 3px 0;
	}

	.legend-swatch {
		width: 12px;
		height: 12px;
		border-radius: 3px;
		flex-shrink: 0;
	}

	.legend-label {
		font-size: 0.8rem;
		color: rgba(255, 255, 255, 0.75);
	}
</style>
