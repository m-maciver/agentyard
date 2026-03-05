<script lang="ts">
	import { formatSats } from '$lib/utils/format';

	export let sats: number | null = null;
	export let label: string = sats !== null ? `Pay ${formatSats(sats)} sats` : 'Pay with Lightning';
	export let loading: boolean = false;
	export let success: boolean = false;
	export let disabled: boolean = false;
	export let fullWidth: boolean = false;
	export let onClick: (() => void) | (() => Promise<void>) = () => {};

	$: resolvedLabel = success ? 'Paid ✓' : label;
</script>

<button
	class="lightning-btn"
	class:full-width={fullWidth}
	class:loading
	class:success
	{disabled}
	on:click={onClick}
	type="button"
>
	{#if loading}
		<span class="spinner" aria-label="Loading..."></span>
	{:else if success}
		<span class="btn-content">{resolvedLabel}</span>
	{:else}
		<span class="btn-content">
			<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
				<path d="M9 2L3 9h5l-1 5 7-8H9l1-4z"/>
			</svg>
			{resolvedLabel}
		</span>
	{/if}
</button>

<style>
	.lightning-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		background: var(--primary);
		color: var(--primary-foreground);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 15px;
		padding: 12px 24px;
		border-radius: 8px;
		border: none;
		cursor: pointer;
		transition: all 150ms ease-out;
		white-space: nowrap;
	}

	.lightning-btn.full-width {
		width: 100%;
	}

	.lightning-btn:hover:not(:disabled):not(.loading):not(.success) {
		background: #c97612;
	}

	.lightning-btn:active:not(:disabled) {
		transform: scale(0.97);
		background: #b56910;
	}

	.lightning-btn.loading {
		background: var(--muted);
		color: var(--muted-foreground);
		cursor: default;
	}

	.lightning-btn.success {
		background: rgba(34, 197, 94, 0.15);
		border: 1px solid var(--success);
		color: var(--success);
	}

	.lightning-btn:disabled:not(.loading) {
		background: var(--muted);
		color: var(--muted-foreground);
		cursor: not-allowed;
		opacity: 0.6;
	}

	.btn-content {
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}

	.spinner {
		display: inline-block;
		width: 16px;
		height: 16px;
		border: 2px solid var(--muted-foreground);
		border-top-color: transparent;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
