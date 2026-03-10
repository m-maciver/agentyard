<script lang="ts">
	export let priceInSats: number;
	export let platformFeePercent: number = 0.12; // 12% default

	$: platformFee = Math.floor(priceInSats * platformFeePercent);
	$: sellerEarns = priceInSats - platformFee;
</script>

<div class="escrow-window glass-card">
	<div class="ew-header">
		<span class="ew-label">Escrow window</span>
		<span class="ew-badge">10 minutes</span>
	</div>
	<div class="ew-breakdown">
		<div class="ew-row">
			<span class="ew-key">You paid:</span>
			<span class="ew-val font-mono">⚡ {priceInSats.toLocaleString()} sats</span>
		</div>
		<div class="ew-row">
			<span class="ew-key">Platform fee:</span>
			<span class="ew-val font-mono">⚡ {platformFee.toLocaleString()} ({(platformFeePercent * 100).toFixed(0)}%)</span>
		</div>
		<div class="ew-row ew-row-highlight">
			<span class="ew-key">Seller earned:</span>
			<span class="ew-val font-mono">⚡ {sellerEarns.toLocaleString()}</span>
		</div>
	</div>
	<p class="ew-note">Funds held in Lightning escrow until accepted. If disputed, both parties' stakes are held for review.</p>
</div>

<style>
	.escrow-window {
		padding: 16px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 12px;
	}

	.ew-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 12px;
	}

	.ew-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-muted);
		font-weight: 600;
	}

	.ew-badge {
		background: rgba(245, 158, 11, 0.1);
		color: #f7931a;
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		font-weight: 600;
		padding: 2px 8px;
		border-radius: 6px;
	}

	.ew-breakdown {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: 12px;
	}

	.ew-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.ew-row-highlight {
		padding: 8px;
		background: rgba(124, 58, 237, 0.08);
		border-radius: 6px;
		margin: 0 -8px;
		padding-left: 8px;
		padding-right: 8px;
	}

	.ew-key {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-secondary);
	}

	.ew-val {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--sats-color);
		font-weight: 500;
	}

	.ew-note {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		margin: 0;
		line-height: 1.5;
	}
</style>
