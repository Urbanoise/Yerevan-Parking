<script>
	import 'maplibre-gl/dist/maplibre-gl.css';
	import MapEngine from '$lib/components/MapEngine.svelte';
	import StoryScroller from '$lib/components/StoryScroller.svelte';
	import Legend from '$lib/components/Legend.svelte';
	import NavDots from '$lib/components/NavDots.svelte';
	import { isLoaded } from '$lib/stores/storyStore.js';
	import { dataLoaded } from '$lib/stores/mapStore.js';
	import { onMount } from 'svelte';

	onMount(() => {
		isLoaded.set(true);
	});
</script>

<svelte:head>
	<title>Yerevan Parking Supply</title>
	<meta name="description" content="Interactive map of parking supply across Yerevan, Armenia" />
</svelte:head>

<div class="app-wrapper">
	<MapEngine />
	<StoryScroller />
	<Legend />
	<NavDots />

	{#if !$dataLoaded}
		<div class="loading-overlay">
			<div class="loading-spinner"></div>
			<p>Loading map data...</p>
		</div>
	{/if}
</div>

<style>
	:global(*) {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}

	:global(body) {
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
		background: #0a0a14;
		color: #e0e0e0;
		overflow-x: hidden;
		-webkit-font-smoothing: antialiased;
	}

	:global(::-webkit-scrollbar) {
		width: 6px;
	}

	:global(::-webkit-scrollbar-track) {
		background: transparent;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: rgba(255, 255, 255, 0.15);
		border-radius: 3px;
	}

	.app-wrapper {
		position: relative;
		width: 100%;
		min-height: 100vh;
	}

	.loading-overlay {
		position: fixed;
		inset: 0;
		z-index: 100;
		background: #0a0a14;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 16px;
		color: rgba(255, 255, 255, 0.6);
		font-size: 0.9rem;
	}

	.loading-spinner {
		width: 36px;
		height: 36px;
		border: 3px solid rgba(255, 255, 255, 0.1);
		border-top-color: #00CED1;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
