<script>
	import { onMount } from 'svelte';

	let { step } = $props();

	let statEls = $state([]);

	onMount(async () => {
		if (!step.stats?.length) return;
		const { gsap } = await import('gsap');

		// Animate stat counters when component mounts
		const observer = new IntersectionObserver((entries) => {
			entries.forEach(entry => {
				if (entry.isIntersecting) {
					const el = entry.target;
					const target = parseInt(el.dataset.target, 10);
					gsap.fromTo(el, { innerText: 0 }, {
						innerText: target,
						duration: 1.5,
						ease: 'power2.out',
						snap: { innerText: 1 },
						onUpdate() {
							el.textContent = Math.round(parseFloat(el.innerText)).toLocaleString();
						}
					});
					observer.unobserve(el);
				}
			});
		}, { threshold: 0.5 });

		// Wait for DOM
		requestAnimationFrame(() => {
			const els = document.querySelectorAll(`[data-step="${step.index}"] .stat-number`);
			els.forEach(el => observer.observe(el));
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
		</div>
	{:else}
		<div class="card-content">
			<h2 class="card-title">{step.title}</h2>
			{#if step.subtitle}
				<p class="card-subtitle">{step.subtitle}</p>
			{/if}

			{#if step.stats?.length}
				<div class="stats-grid">
					{#each step.stats as stat}
						<div class="stat-item">
							<span class="stat-number" data-target={stat.value} style="color: {stat.color}">0</span>
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
	}

	.story-card.intro {
		width: 420px;
		text-align: center;
		padding: 48px 36px;
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
