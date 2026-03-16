<script>
	import { onMount } from 'svelte';
	import { currentStep } from '$lib/stores/storyStore.js';
	import { STORY_STEPS } from '$lib/config/story.js';
	import StoryStep from './StoryStep.svelte';

	let scrollerContainer;

	onMount(async () => {
		const scrollama = (await import('scrollama')).default;

		const scroller = scrollama();

		scroller
			.setup({
				step: '.scroll-step',
				offset: 0.5,
				debug: false
			})
			.onStepEnter(({ index }) => {
				currentStep.set(index);
			});

		window.addEventListener('resize', scroller.resize);

		return () => {
			scroller.destroy();
			window.removeEventListener('resize', scroller.resize);
		};
	});
</script>

<div class="story-scroller" bind:this={scrollerContainer}>
	{#each STORY_STEPS as step, i}
		<div
			class="scroll-step"
			class:active={$currentStep === i}
			data-step={i}
		>
			<StoryStep {step} />
		</div>
	{/each}
	<div class="scroll-spacer"></div>
</div>

<style>
	.story-scroller {
		position: relative;
		z-index: 10;
		pointer-events: none;
	}

	.scroll-step {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: flex-start;
		padding: 0 5vw;
		pointer-events: auto;
		opacity: 0.3;
		transition: opacity 0.4s ease;
	}

	.scroll-step.active {
		opacity: 1;
	}

	.scroll-step:first-child {
		justify-content: center;
	}

	.scroll-spacer {
		height: 40vh;
	}
</style>
