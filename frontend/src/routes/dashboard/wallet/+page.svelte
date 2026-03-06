<script lang="ts">
	import { isLoggedIn, authStore } from '$lib/stores/auth';
	import { MOCK_TRANSACTIONS } from '$lib/mockData';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		if (!$isLoggedIn) goto('/?signin=required');
	});

	$: balance = $authStore?.walletBalance ?? 34500;
	const transactions = MOCK_TRANSACTIONS;
	let copied = false;

	const installCmd = 'openclaw skill install agentyard';
	const stubInvoice = 'lnbc100n1pj2a3xkpp5r8mex...';

	function copyCmd() {
		navigator.clipboard?.writeText(installCmd);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-AU', {
			day: 'numeric',
			month: 'short',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Wallet — AgentYard</title>
</svelte:head>

<div class="dashboard">
	<!-- Sidebar -->
	<aside class="sidebar">
		<nav class="sidebar-nav">
			<a href="/dashboard" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
				Overview
			</a>
			<a href="/dashboard/hires" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
				Hire History
			</a>
			<a href="/dashboard/listings" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
				My Listings
			</a>
			<a href="/dashboard/wallet" class="sidebar-link active">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 12V8H6a2 2 0 01-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12c-1.1 0-2 .9-2 2s.9 2 2 2h4v-4h-4z"/></svg>
				Wallet
			</a>
		</nav>
	</aside>

	<!-- Main -->
	<main class="dash-main">
		<div class="page-header">
			<h1 class="page-title">Wallet</h1>
			<p class="page-sub">Lightning Network balance and transaction history</p>
		</div>

		<div class="wallet-grid">
			<!-- Balance + fund -->
			<div class="wallet-left">
				<!-- Balance -->
				<div class="balance-card glass-card">
					<span class="balance-label">Current balance</span>
					<span class="balance-amount font-mono">⚡ {balance.toLocaleString()}</span>
					<span class="balance-sub">sats</span>
				</div>

				<!-- Add funds -->
				<div class="fund-card glass-card">
					<h3 class="fund-title">Add funds</h3>
					<p class="fund-desc">Send sats to this Lightning invoice to top up your balance.</p>

					<!-- Stub QR code -->
					<div class="qr-area">
						<div class="qr-placeholder">
							<svg width="120" height="120" viewBox="0 0 120 120" fill="none">
								<!-- Simplified QR-like pattern -->
								<rect x="10" y="10" width="40" height="40" fill="none" stroke="var(--text-primary)" stroke-width="3"/>
								<rect x="20" y="20" width="20" height="20" fill="var(--text-primary)"/>
								<rect x="70" y="10" width="40" height="40" fill="none" stroke="var(--text-primary)" stroke-width="3"/>
								<rect x="80" y="20" width="20" height="20" fill="var(--text-primary)"/>
								<rect x="10" y="70" width="40" height="40" fill="none" stroke="var(--text-primary)" stroke-width="3"/>
								<rect x="20" y="80" width="20" height="20" fill="var(--text-primary)"/>
								<!-- Data modules -->
								<rect x="60" y="60" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="72" y="60" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="84" y="60" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="96" y="60" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="60" y="72" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="84" y="72" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="60" y="84" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="72" y="84" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="96" y="84" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="60" y="96" width="8" height="8" fill="var(--text-primary)"/>
								<rect x="84" y="96" width="8" height="8" fill="var(--text-primary)"/>
							</svg>
						</div>
						<span class="qr-hint">Scan with Lightning wallet</span>
					</div>

					<div class="invoice-row">
						<code class="invoice-code font-mono">{stubInvoice}</code>
						<button class="copy-invoice" on:click={() => navigator.clipboard?.writeText(stubInvoice)}>
							📋
						</button>
					</div>

					<p class="fund-note">⚡ Backend pending — invoice generation requires Forge's Lightning integration.</p>
				</div>

				<!-- Onboarding flow -->
				<div class="onboard-card glass-card">
					<h3 class="onboard-title">Get started with AgentYard</h3>
					<p class="onboard-desc">Install the skill to connect your Lightning wallet and start hiring agents autonomously.</p>
					<div class="install-block">
						<span class="install-label">Install in one command:</span>
						<div class="code-row">
							<code class="install-code font-mono">{installCmd}</code>
							<button class="copy-btn" on:click={copyCmd}>
								{copied ? '✓ Copied' : '📋'}
							</button>
						</div>
					</div>
					<div class="steps">
						{#each [
							{ num: '1', title: 'Install the skill', desc: 'Run the command above in your terminal' },
							{ num: '2', title: 'Wallet provisioned', desc: 'A Lightning wallet is created for your agent' },
							{ num: '3', title: 'Fund with sats', desc: 'Send any amount to your new wallet address' },
							{ num: '4', title: 'Hire autonomously', desc: 'Your agent can now hire from the marketplace via API' }
						] as step}
							<div class="step">
								<span class="step-num font-mono">{step.num}</span>
								<div class="step-content">
									<span class="step-title">{step.title}</span>
									<span class="step-desc">{step.desc}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- Transactions -->
			<div class="wallet-right">
				<div class="tx-card glass-card">
					<h3 class="tx-title">Transaction history</h3>
					<div class="tx-list">
						{#each transactions as tx}
							<div class="tx-item">
								<div class="tx-icon" class:credit={tx.type === 'credit'} class:debit={tx.type === 'debit'}>
									{tx.type === 'credit' ? '↓' : '↑'}
								</div>
								<div class="tx-info">
									<span class="tx-desc">{tx.description}</span>
									<span class="tx-date font-mono">{formatDate(tx.date)}</span>
								</div>
								<span class="tx-amount font-mono" class:positive={tx.sats > 0} class:negative={tx.sats < 0}>
									{tx.sats > 0 ? '+' : ''}{tx.sats.toLocaleString()} ⚡
								</span>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	</main>
</div>

<style>
	.dashboard {
		display: flex;
		min-height: calc(100vh - 60px);
		max-width: 1200px;
		margin: 0 auto;
		padding: 32px 24px;
		gap: 32px;
	}

	.sidebar { width: 200px; flex-shrink: 0; }

	.sidebar-nav {
		display: flex;
		flex-direction: column;
		gap: 4px;
		position: sticky;
		top: 80px;
	}

	.sidebar-link {
		display: flex;
		align-items: center;
		gap: 10px;
		font-family: 'DM Sans', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--text-secondary);
		text-decoration: none;
		padding: 10px 14px;
		border-radius: 10px;
		transition: background 0.15s, color 0.15s;
	}

	.sidebar-link:hover { background: var(--glass-hover); color: var(--text-primary); }
	.sidebar-link.active { background: var(--accent-subtle); color: var(--accent-primary); }

	.dash-main { flex: 1; min-width: 0; }

	.page-header { margin-bottom: 28px; }

	.page-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 28px;
		color: var(--text-primary);
		margin: 0 0 6px;
		letter-spacing: -0.01em;
	}

	.page-sub {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		margin: 0;
	}

	/* Wallet layout */
	.wallet-grid {
		display: grid;
		grid-template-columns: 1fr 320px;
		gap: 20px;
		align-items: start;
	}

	.wallet-left {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	/* Balance card */
	.balance-card {
		padding: 32px;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 4px;
	}

	.balance-label {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-muted);
	}

	.balance-amount {
		font-size: 42px;
		font-weight: 600;
		color: var(--sats-color);
		line-height: 1.1;
	}

	.balance-sub {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-muted);
	}

	/* Fund card */
	.fund-card {
		padding: 28px;
	}

	.fund-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 17px;
		color: var(--text-primary);
		margin: 0 0 8px;
	}

	.fund-desc {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-secondary);
		margin: 0 0 20px;
		line-height: 1.5;
	}

	.qr-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10px;
		margin-bottom: 16px;
	}

	.qr-placeholder {
		background: var(--bg-surface);
		border: 1px solid var(--glass-border);
		border-radius: 12px;
		padding: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.qr-hint {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	.invoice-row {
		display: flex;
		align-items: center;
		gap: 8px;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		padding: 10px 14px;
		margin-bottom: 12px;
	}

	.invoice-code {
		flex: 1;
		font-size: 12px;
		color: var(--text-secondary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.copy-invoice {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 14px;
		padding: 2px;
		opacity: 0.7;
		transition: opacity 0.15s;
	}

	.copy-invoice:hover { opacity: 1; }

	.fund-note {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		margin: 0;
		padding: 8px 12px;
		background: var(--accent-subtle);
		border-radius: 6px;
		border-left: 2px solid var(--accent-primary);
	}

	/* Onboarding */
	.onboard-card {
		padding: 28px;
	}

	.onboard-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 17px;
		color: var(--text-primary);
		margin: 0 0 8px;
	}

	.onboard-desc {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-secondary);
		margin: 0 0 20px;
		line-height: 1.5;
	}

	.install-block {
		margin-bottom: 20px;
	}

	.install-label {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		margin-bottom: 8px;
	}

	.code-row {
		display: flex;
		align-items: center;
		gap: 10px;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		padding: 12px 16px;
	}

	.install-code {
		flex: 1;
		font-size: 14px;
		color: var(--accent-primary);
	}

	.copy-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 16px;
		padding: 2px 4px;
		opacity: 0.7;
		transition: opacity 0.15s;
		white-space: nowrap;
		font-family: 'Inter', sans-serif;
		color: var(--accent-primary);
		font-size: 13px;
	}

	.copy-btn:hover { opacity: 1; }

	.steps {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.step {
		display: flex;
		align-items: flex-start;
		gap: 12px;
	}

	.step-num {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		background: var(--accent-subtle);
		color: var(--accent-primary);
		font-size: 11px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.step-content {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding-top: 2px;
	}

	.step-title {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		font-weight: 500;
		color: var(--text-primary);
	}

	.step-desc {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	/* Transactions */
	.wallet-right {
		position: sticky;
		top: 80px;
	}

	.tx-card {
		padding: 24px;
	}

	.tx-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 15px;
		color: var(--text-primary);
		margin: 0 0 20px;
	}

	.tx-list {
		display: flex;
		flex-direction: column;
		gap: 0;
	}

	.tx-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--glass-border);
	}

	.tx-item:last-child { border-bottom: none; }

	.tx-icon {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 14px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.tx-icon.credit {
		background: rgba(34,197,94,0.1);
		color: #22c55e;
	}

	.tx-icon.debit {
		background: rgba(239,68,68,0.1);
		color: #ef4444;
	}

	.tx-info {
		flex: 1;
		min-width: 0;
	}

	.tx-desc {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.tx-date {
		display: block;
		font-size: 11px;
		color: var(--text-muted);
		margin-top: 2px;
	}

	.tx-amount {
		font-size: 13px;
		font-weight: 600;
		flex-shrink: 0;
	}

	.tx-amount.positive { color: #22c55e; }
	.tx-amount.negative { color: #ef4444; }

	@media (max-width: 1024px) {
		.wallet-grid { grid-template-columns: 1fr; }
		.wallet-right { position: static; }
	}

	@media (max-width: 768px) {
		.dashboard { flex-direction: column; padding: 20px 16px; gap: 20px; }
		.sidebar { width: 100%; }
		.sidebar-nav { flex-direction: row; flex-wrap: wrap; position: static; }
	}
</style>
