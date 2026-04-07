<script>
	import { onMount } from 'svelte';
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	import { activeLegendFilters, geojsonData } from '$lib/stores/mapStore.js';
	import { currentStep } from '$lib/stores/storyStore.js';

	let { step } = $props();

	let statEls = $state([]);

	let dynamicStats = $derived.by(() => {
		// Only run dynamic calculation on steps that have legendGroups configured with an Impact Area toggle
		if (step.legendGroups && step.legendGroups[1]?.title === 'Impact Area' && $geojsonData.lines) {
			// Only apply filter restrictions when THIS step is the current step.
			// For non-current steps, treat all legends as active (null = show all).
			const activeLayers = ($currentStep === step.index) ? $activeLegendFilters : null;
			
			const primaryGroup = step.legendGroups[0];
			const primaryMode = step.colorMode; // 'color', 'method', 'signage', 'marking', 'location'
			
			const propertyMap = {
				'color': { 'white': 'white', 'red': 'red', 'blue': 'blue', 'black': 'black' },
				'method': { 'parallel': 'parallel', '90': '90', '45': '45' },
				'signage': { 'yes': 'yes', 'no': 'no' },
				'marking': { 'yes': 'yes', 'no': 'no' },
				'location': { 'on-street': 'on-street', 'pocket': 'pocket', 'set-back': 'set-back' }
			};
			const primaryMap = propertyMap[primaryMode];
			
			if (!primaryMap) return step.stats || [];

			// Determine which primary values are active
			const allowedPrimary = new Set();
			if (activeLayers === null) {
				primaryGroup.layers.forEach(l => allowedPrimary.add(primaryMap[l.id]));
			} else {
				primaryGroup.layers.forEach(l => {
					if (activeLayers.has(l.id)) allowedPrimary.add(primaryMap[l.id]);
				});
			}

			// Determine which impact values are active
			const allowedImpacts = new Set();
			if (activeLayers === null) {
				allowedImpacts.add('corridor').add('buffer').add('yard');
			} else {
				if (activeLayers.has('corridor')) allowedImpacts.add('corridor');
				if (activeLayers.has('buffer')) allowedImpacts.add('buffer');
				if (activeLayers.has('yard')) allowedImpacts.add('yard');
			}
			
			// Initialize counts for each primary layer ID
			const counts = {};
			primaryGroup.layers.forEach(l => counts[l.id] = 0);
			
			const processFeature = (f) => {
				const impact = f.properties.impact;
				const space = parseInt(f.properties.space) || 0;
				if (!allowedImpacts.has(impact)) return;
				
				let propVal = f.properties[primaryMode];
				// Force-alias undefined and minor edge cases into standard legacy buckets
				if ((primaryMode === 'signage' || primaryMode === 'marking') && propVal !== 'yes') {
					propVal = 'no';
				} else if (primaryMode === 'method' && propVal !== '90' && propVal !== '45') {
					propVal = 'parallel';
				} else if (primaryMode === 'location' && propVal !== 'pocket' && propVal !== 'set-back') {
					propVal = 'on-street';
				}

				if (allowedPrimary.has(propVal)) {
					// Identify which legend id this value corresponds to
					const matchId = primaryGroup.layers.find(l => primaryMap[l.id] === propVal)?.id;
					if (matchId) {
						counts[matchId] += space;
					}
				}
			};
			
			$geojsonData.lines.forEach(processFeature);
			
			// Process areas implicitly (they are visually 'yard' and conceptually 'white' or generic supply)
			if (allowedImpacts.has('yard')) {
				const primaryAllowsArea = primaryMode === 'color' ? allowedPrimary.has('white') : true;
				if (primaryAllowsArea) {
					// We attribute area spaces to the first primary label available, or specifically 'white' if color mode.
					const targetId = primaryMode === 'color' ? 'white' : primaryGroup.layers[0]?.id;
					
					if (targetId && (activeLayers === null || activeLayers.has(targetId))) {
						$geojsonData.areas.forEach(f => {
							let spaceStr = f.properties.description?.value || '';
							const match = spaceStr.match(/Space:\s*(\d+)/i);
							if (match && counts[targetId] !== undefined) {
								counts[targetId] += parseInt(match[1]) || 0;
							}
						});
					}
				}
			}
			
			// Format the result cleanly as expected by the frontend
			return primaryGroup.layers.map(l => ({
				id: l.id,
				value: counts[l.id],
				label: l.label.replace(/\s*\([\d,]+\)/, ''), // clean off static numbers from legend text
				color: l.color
			}));
		}
		
		return step.stats || [];
	});

	let isVisible = $state(false);
	let animatedValues = tweened((step.stats || (step.legendGroups ? step.legendGroups[0].layers : [])).map(() => 0), { duration: 1500, easing: cubicOut });

	$effect(() => {
		if (isVisible && dynamicStats.length > 0) {
			animatedValues.set(dynamicStats.map(s => s.value));
		}
	});

	onMount(() => {
		const observer = new IntersectionObserver((entries) => {
			entries.forEach(entry => {
				if (entry.isIntersecting) {
					isVisible = true;
					observer.unobserve(entry.target);
				}
			});
		}, { threshold: 0.5 });

		requestAnimationFrame(() => {
			const el = document.querySelector(`[data-step="${step.index}"]`);
			if (el) observer.observe(el);
		});

		return () => observer.disconnect();
	});
</script>

<div class="story-card" class:intro={step.isIntro} data-step={step.index}>
	{#if step.isIntro}
		<div class="intro-content">
			<h1 class="intro-title">{step.title}</h1>
			<p class="intro-subtitle">{step.subtitle}</p>
			<div class="scroll-hint">
				<span class="scroll-arrow">&#8595;</span>
				<span>Scroll to explore</span>
			</div>
			<a class="sts-brand" href="https://www.sts.com.ge" target="_blank" rel="noopener noreferrer">
				<img class="sts-logo-img" src="/sts-logo.png" alt="STS logo" />
				<span class="sts-label">created by STS</span>
			</a>
		</div>
	{:else}
		<div class="card-content">
			<h2 class="card-title">{step.title}</h2>
			{#if step.subtitle}
				<p class="card-subtitle">{step.subtitle}</p>
			{/if}

			{#if dynamicStats.length}
				<div class="stats-grid">
					{#each dynamicStats as stat, i}
						<div class="stat-item">
							<span class="stat-number" style="color: {stat.color}">{Math.round($animatedValues[i] || 0).toLocaleString()}</span>
							<span class="stat-label">{stat.label}</span>
						</div>
					{/each}
				</div>
			{/if}

			{#if step.description}
				<p class="card-description">{step.description}</p>
			{/if}

			{#if step.topStreets?.length}
				<div class="top-streets">
					<h3 class="streets-heading">Top Areas by Supply</h3>
					{#each step.topStreets as street, i}
						<div class="street-row">
							<span class="street-rank">#{i + 1}</span>
							<span class="street-name">{street.name}</span>
							<span class="street-type" class:yard={street.type === 'yard'} class:on-street={street.type === 'street'}>
								{street.type === 'yard' ? 'Yard' : 'Street'}
							</span>
							<span class="street-spaces">{street.spaces.toLocaleString()}</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.story-card {
		background: rgba(10, 10, 20, 0.88);
		border: 1px solid rgba(255, 255, 255, 0.08);
		border-radius: 16px;
		backdrop-filter: blur(16px);
		padding: 28px 24px;
		width: 340px;
		max-width: 90vw;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
		transition: opacity 0.3s ease;
		pointer-events: auto;
	}

	.story-card.intro {
		width: 420px;
		text-align: center;
		padding: 48px 36px;
	}

	.sts-brand {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
		margin-top: 28px;
		text-decoration: none;
		opacity: 0.7;
		transition: opacity 0.2s ease;
	}

	.sts-brand:hover {
		opacity: 1;
	}

	.sts-logo-img {
		width: 120px;
		height: auto;
	}

	.sts-label {
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 1.5px;
		color: rgba(255, 255, 255, 0.45);
		font-weight: 500;
	}

	.intro-title {
		font-size: 2rem;
		font-weight: 700;
		color: #00CED1;
		margin: 0 0 12px;
		line-height: 1.15;
	}

	.intro-subtitle {
		font-size: 1rem;
		color: rgba(255, 255, 255, 0.7);
		margin: 0 0 32px;
		line-height: 1.5;
	}

	.scroll-hint {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
		color: rgba(255, 255, 255, 0.4);
		font-size: 0.85rem;
	}

	.scroll-arrow {
		font-size: 1.4rem;
		animation: bounce 2s ease-in-out infinite;
	}

	@keyframes bounce {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(6px); }
	}

	.card-title {
		font-size: 1.3rem;
		font-weight: 600;
		color: #00CED1;
		margin: 0 0 4px;
	}

	.card-subtitle {
		font-size: 0.82rem;
		color: rgba(255, 255, 255, 0.5);
		margin: 0 0 18px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
		gap: 12px;
		margin-bottom: 18px;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}

	.stat-number {
		font-size: 1.6rem;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		line-height: 1.2;
	}

	.stat-label {
		font-size: 0.72rem;
		color: rgba(255, 255, 255, 0.55);
		text-transform: uppercase;
		letter-spacing: 0.3px;
		text-align: center;
	}

	.card-description {
		font-size: 0.88rem;
		color: rgba(255, 255, 255, 0.75);
		line-height: 1.6;
		margin: 0;
	}

	.top-streets {
		margin-top: 14px;
	}

	.streets-heading {
		font-size: 0.78rem;
		text-transform: uppercase;
		color: rgba(255, 255, 255, 0.45);
		letter-spacing: 0.5px;
		margin: 0 0 10px;
	}

	.street-row {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 6px 0;
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
		font-size: 0.85rem;
	}

	.street-rank {
		color: rgba(255, 255, 255, 0.3);
		font-size: 0.75rem;
		width: 22px;
	}

	.street-name {
		flex: 1;
		color: rgba(255, 255, 255, 0.85);
	}

	.street-type {
		font-size: 0.7rem;
		padding: 2px 6px;
		border-radius: 4px;
		text-transform: uppercase;
		letter-spacing: 0.3px;
	}

	.street-type.yard {
		background: rgba(124, 77, 255, 0.2);
		color: #B388FF;
	}

	.street-type.on-street {
		background: rgba(66, 165, 245, 0.2);
		color: #42a5f5;
	}

	.street-spaces {
		font-weight: 600;
		color: #00CED1;
		min-width: 40px;
		text-align: right;
	}
</style>
