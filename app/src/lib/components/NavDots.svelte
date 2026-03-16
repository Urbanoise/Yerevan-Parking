<script>
	import { currentStep } from '$lib/stores/storyStore.js';
	import { STORY_STEPS } from '$lib/config/story.js';
</script>

<div class="nav-dots">
	{#each STORY_STEPS as step, i}
		<button
			class="nav-dot"
			class:active={$currentStep === i}
			title={step.title}
			onclick={() => {
				const el = document.querySelector(`[data-step="${i}"]`);
				if (el) el.scrollIntoView({ behavior: 'smooth' });
			}}
		>
			<span class="dot-indicator"></span>
		</button>
	{/each}
</div>

<style>
	.nav-dots {
		position: fixed;
		right: 16px;
		top: 50%;
		transform: translateY(-50%);
		z-index: 30;
		display: flex;
		flex-direction: column;
		gap: 10px;
		align-items: center;
	}

	.nav-dot {
		background: none;
		border: none;
		padding: 4px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.dot-indicator {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.25);
		transition: all 0.3s ease;
	}

	.nav-dot.active .dot-indicator {
		background: #00CED1;
		width: 10px;
		height: 10px;
		box-shadow: 0 0 8px rgba(0, 206, 209, 0.5);
	}

	.nav-dot:hover .dot-indicator {
		background: rgba(255, 255, 255, 0.5);
	}

	.nav-dot.active:hover .dot-indicator {
		background: #00CED1;
	}
</style>
