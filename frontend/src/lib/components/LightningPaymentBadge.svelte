<script lang="ts">
	import { onMount } from 'svelte';

	/** 'escrowed' = payment locked, 'released' = payment sent to provider */
	export let status: 'escrowed' | 'released' = 'escrowed';

	let mounted = false;

	onMount(() => {
		// Tiny delay so the CSS transition fires visibly
		requestAnimationFrame(() => {
			setTimeout(() => { mounted = true; }, 40);
		});
	});
</script>

<div
	class="lightning-badge"
	class:released={status === 'released'}
	class:mounted
	aria-label={status === 'released' ? 'Payment released' : 'Payment locked in escrow'}
>
	<span class="bolt">⚡</span>

	{#if status === 'released'}
		<span class="badge-text">Payment released</span>
	{:else}
		<span class="badge-text">Payment locked in escrow</span>
		<span class="sep">•</span>
		<span class="stub-label">Lightning stub mode</span>
	{/if}
</div>

<style>
	/* ── Enter animation ── */
	@keyframes badge-glow-amber {
		0%   { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
		25%  { box-shadow: 0 0 0 5px rgba(245, 158, 11, 0.28); }
		100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
	}

	@keyframes badge-glow-green {
		0%   { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
		25%  { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.3); }
		100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
	}

	@keyframes bolt-zap {
		0%   { transform: scale(1) rotate(0deg); }
		20%  { transform: scale(1.35) rotate(-8deg); }
		45%  { transform: scale(0.9)  rotate(4deg); }
		70%  { transform: scale(1.1)  rotate(-3deg); }
		100% { transform: scale(1)    rotate(0deg); }
	}

	/* ── Base ── */
	.lightning-badge {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 5px 13px;
		border-radius: 9999px;
		font-family: -apple-system, 'Inter', system-ui, sans-serif;
		font-size: 12px;
		font-weight: 500;
		line-height: 1.4;
		letter-spacing: 0.01em;

		/* Amber/Bitcoin default */
		background: rgba(245, 158, 11, 0.10);
		border: 1px solid rgba(245, 158, 11, 0.28);
		color: #f59e0b;

		/* Enter transition */
		opacity: 0;
		transform: translateY(5px) scale(0.97);
		transition: opacity 0.28s ease, transform 0.28s ease;
	}

	.lightning-badge.mounted {
		opacity: 1;
		transform: translateY(0) scale(1);
		animation: badge-glow-amber 1.4s ease-out forwards;
	}

	/* ── Released variant ── */
	.lightning-badge.released {
		background: rgba(34, 197, 94, 0.10);
		border-color: rgba(34, 197, 94, 0.28);
		color: #22c55e;
	}

	.lightning-badge.released.mounted {
		animation: badge-glow-green 1.4s ease-out forwards;
	}

	/* ── Parts ── */
	.bolt {
		display: inline-block;
		font-size: 14px;
		line-height: 1;
		flex-shrink: 0;
	}

	.lightning-badge.mounted .bolt {
		animation: bolt-zap 0.55s ease-out;
	}

	.badge-text {
		white-space: nowrap;
	}

	.sep {
		opacity: 0.45;
		font-size: 10px;
	}

	.stub-label {
		opacity: 0.65;
		font-size: 11px;
		letter-spacing: 0.02em;
		white-space: nowrap;
	}
</style>
