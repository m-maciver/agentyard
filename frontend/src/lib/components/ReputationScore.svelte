<script lang="ts">
	export let score: number; // 0–100
	export let jobCount: number = 0;
	export let compact: boolean = false;

	// Convert 0-100 score to 0-5 star scale
	$: starScore = (score / 100) * 5;
	$: fullStars = Math.floor(starScore);
	$: partialFill = (starScore - fullStars) * 100;
	$: emptyStars = 5 - Math.ceil(starScore);

	$: scoreColor = score >= 90
		? 'var(--success)'
		: score >= 70
		? 'var(--foreground)'
		: score >= 40
		? 'var(--warning)'
		: 'var(--destructive)';

	$: percentile = score >= 95 ? 'Top 2%' : score >= 90 ? 'Top 5%' : score >= 80 ? 'Top 8%' : score >= 70 ? 'Top 15%' : null;
</script>

{#if compact}
	<!-- Compact: star + number, used in cards -->
	<span class="inline-flex items-center gap-1">
		<span style="color: var(--primary); font-size: 14px;">★</span>
		<span
			class="font-mono font-semibold"
			style="font-family: 'JetBrains Mono', monospace; font-size: 15px; color: var(--foreground);"
		>
			{(starScore).toFixed(1)}
		</span>
		{#if jobCount > 0}
			<span
				style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--muted-foreground);"
			>
				({jobCount})
			</span>
		{/if}
	</span>
{:else}
	<!-- Full: large score + star row + job count + optional percentile -->
	<div class="flex flex-col items-start gap-2">
		<span
			class="font-display font-bold"
			style="font-family: 'Space Grotesk', sans-serif; font-size: 48px; line-height: 1; color: {scoreColor};"
		>
			{score.toFixed(1)}
		</span>
		<div class="flex items-center gap-1">
			{#each Array(fullStars) as _}
				<span style="color: var(--primary); font-size: 20px;">★</span>
			{/each}
			{#if partialFill > 0 && fullStars < 5}
				<span style="position: relative; font-size: 20px; color: var(--border-strong);">
					★
					<span
						style="position: absolute; left: 0; top: 0; overflow: hidden; width: {partialFill}%; color: var(--primary);"
					>★</span>
				</span>
			{/if}
			{#each Array(emptyStars) as _}
				<span style="color: var(--border-strong); font-size: 20px;">★</span>
			{/each}
		</div>
		<span style="font-family: 'Inter', sans-serif; font-size: 14px; color: var(--muted-foreground);">
			{jobCount} jobs completed
		</span>
		{#if percentile}
			<span
				class="inline-flex items-center rounded-full px-2.5 py-1"
				style="background: rgba(247,147,26,0.12); color: var(--primary); font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 500;"
			>
				{percentile}
			</span>
		{/if}
	</div>
{/if}
