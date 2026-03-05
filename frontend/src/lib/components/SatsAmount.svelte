<script lang="ts">
	import { formatSats, satsToUsd } from '$lib/utils/format';

	export let amount: number;
	export let showUsd: boolean = false;
	export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
	export let color: string = 'var(--foreground)';
	export let prefix: string = '⚡ ';

	const sizeClass = {
		sm: 'text-sm',
		md: 'text-base',
		lg: 'text-xl',
		xl: 'text-2xl font-bold'
	};
</script>

<span class="inline-flex items-baseline gap-2">
	<span
		class="font-mono {sizeClass[size]}"
		style="font-family: 'JetBrains Mono', monospace; color: {color};"
	>
		{prefix}{formatSats(amount)} sats
	</span>
	{#if showUsd}
		<span
			class="font-body text-sm"
			style="color: var(--muted-foreground); font-family: 'Inter', sans-serif;"
		>
			≈ {satsToUsd(amount)}
		</span>
	{/if}
</span>
