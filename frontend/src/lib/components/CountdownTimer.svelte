<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	export let createdAt: string;
	export let windowMinutes: number = 10;
	export let onExpire: (() => void) | undefined = undefined;

	let remaining = '';
	let isExpired = false;
	let interval: NodeJS.Timeout | undefined;

	function updateCountdown() {
		const now = new Date();
		const created = new Date(createdAt);
		const expiresAt = new Date(created.getTime() + windowMinutes * 60 * 1000);
		const diff = expiresAt.getTime() - now.getTime();

		if (diff <= 0) {
			remaining = '0:00';
			isExpired = true;
			if (onExpire) onExpire();
			if (interval) clearInterval(interval);
		} else {
			const mins = Math.floor(diff / 60000);
			const secs = Math.floor((diff % 60000) / 1000);
			remaining = `${mins}:${secs.toString().padStart(2, '0')}`;
			isExpired = false;
		}
	}

	onMount(() => {
		updateCountdown();
		interval = setInterval(updateCountdown, 1000);
	});

	onDestroy(() => {
		if (interval) clearInterval(interval);
	});
</script>

<div class="countdown-timer" class:expired={isExpired}>
	<svg width="48" height="48" viewBox="0 0 48 48" class="timer-icon">
		<circle cx="24" cy="24" r="22" fill="none" stroke="currentColor" stroke-width="2" opacity="0.2" />
		<circle
			cx="24"
			cy="24"
			r="22"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			stroke-dasharray={2 * Math.PI * 22}
			stroke-dashoffset={2 * Math.PI * 22 * (1 - (1 - (parseInt(remaining.split(':')[0] || '0') * 60 + parseInt(remaining.split(':')[1] || '0')) / (windowMinutes * 60)))}
			stroke-linecap="round"
			class:running={!isExpired}
		/>
	</svg>
	<div class="timer-display font-mono">{remaining}</div>
	<div class="timer-label">until auto-accept</div>
</div>

<style>
	.countdown-timer {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		padding: 16px 0;
	}

	.timer-icon {
		color: #f7931a;
		width: 48px;
		height: 48px;
	}

	.timer-icon circle:last-child.running {
		animation: spin-reverse 600ms linear infinite;
	}

	@keyframes spin-reverse {
		0% {
			transform: rotate(0deg);
			transform-origin: 50% 50%;
		}
		100% {
			transform: rotate(-360deg);
			transform-origin: 50% 50%;
		}
	}

	.timer-display {
		font-size: 24px;
		font-weight: 700;
		color: #f7931a;
		letter-spacing: 0.05em;
	}

	.timer-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.countdown-timer.expired .timer-display {
		color: #ef4444;
	}

	.countdown-timer.expired .timer-icon {
		color: #ef4444;
		opacity: 0.5;
	}
</style>
