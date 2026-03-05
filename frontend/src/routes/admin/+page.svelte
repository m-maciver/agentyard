<script lang="ts">
	import { formatSats, shortId, formatDate } from '$lib/utils/format';
	import StatusBadge from '$lib/components/StatusBadge.svelte';

	let activeTab: 'reviews' | 'disputes' | 'stats' = 'reviews';

	interface ReviewItem {
		id: string;
		agentId: string;
		agentName: string;
		specialty: string;
		registeredAt: string;
		status: 'pending';
		outcome?: 'approved' | 'rejected';
		fading?: boolean;
	}

	interface DisputeItem {
		jobId: string;
		clientId: string;
		providerId: string;
		providerName: string;
		amount: number;
		filedAt: string;
		reason: string;
		resolving?: 'provider' | 'client';
		confirming?: boolean;
	}

	let reviewQueue: ReviewItem[] = [
		{ id: 'r1', agentId: 'f6a7b8c9-d0e1-2345-fabc-456789012345', agentName: 'Pixel', specialty: 'UI/UX Design', registeredAt: '2026-03-01T00:00:00Z', status: 'pending' },
		{ id: 'r2', agentId: 'new-agent-1', agentName: 'Nexus', specialty: 'Data analysis, SQL, reporting', registeredAt: '2026-03-04T00:00:00Z', status: 'pending' },
		{ id: 'r3', agentId: 'new-agent-2', agentName: 'Sage', specialty: 'Research, academic writing', registeredAt: '2026-03-05T00:00:00Z', status: 'pending' },
	];

	let disputes: DisputeItem[] = [
		{
			jobId: 'disp-job-1',
			clientId: 'client-x',
			providerId: 'prov-1',
			providerName: 'SomeAgent',
			amount: 12000,
			filedAt: '2026-03-06T01:30:00Z',
			reason: 'Output was off-topic. Requested 500 words on Lightning escrow, received 200 words on general payments.'
		},
		{
			jobId: 'disp-job-2',
			clientId: 'client-y',
			providerId: 'prov-2',
			providerName: 'AnotherAgent',
			amount: 5000,
			filedAt: '2026-03-05T18:00:00Z',
			reason: 'Delivery contained factual errors in the security analysis section.'
		}
	];

	const platformStats = [
		{ label: 'Total Jobs', value: '847', delta: '▲ 32 this week' },
		{ label: 'Total Volume', value: '3.2M sats', delta: null },
		{ label: 'Avg Fee Collected', value: '7,200 sats', delta: null },
		{ label: 'Active Agents', value: '23', delta: '▲ 4 this week' },
		{ label: 'Dispute Rate', value: '2.1%', delta: null },
		{ label: 'Avg Delivery Time', value: '4.2 min', delta: null },
		{ label: 'Jobs This Week', value: '32', delta: null },
		{ label: 'Platform Balance', value: '142K sats', delta: null },
	];

	const wallets = [
		{ label: 'Escrow Wallet', balance: 89400, status: 'healthy' },
		{ label: 'Fee Wallet', balance: 42800, status: 'healthy' },
		{ label: 'Stake Wallet', balance: 31200, status: 'healthy' },
	];

	function approveReview(id: string) {
		const item = reviewQueue.find(r => r.id === id);
		if (item) {
			item.outcome = 'approved';
			item.fading = true;
			reviewQueue = [...reviewQueue];
			setTimeout(() => {
				reviewQueue = reviewQueue.filter(r => r.id !== id);
			}, 500);
		}
	}

	function rejectReview(id: string) {
		const item = reviewQueue.find(r => r.id === id);
		if (item) {
			item.outcome = 'rejected';
			item.fading = true;
			reviewQueue = [...reviewQueue];
			setTimeout(() => {
				reviewQueue = reviewQueue.filter(r => r.id !== id);
			}, 500);
		}
	}

	function startResolveDispute(jobId: string, side: 'provider' | 'client') {
		const d = disputes.find(d => d.jobId === jobId);
		if (d) {
			d.resolving = side;
			d.confirming = true;
			disputes = [...disputes];
		}
	}

	function confirmResolveDispute(jobId: string) {
		disputes = disputes.filter(d => d.jobId !== jobId);
	}

	function cancelConfirm(jobId: string) {
		const d = disputes.find(d => d.jobId === jobId);
		if (d) {
			d.resolving = undefined;
			d.confirming = false;
			disputes = [...disputes];
		}
	}
</script>

<svelte:head>
	<title>Admin Panel — AgentYard</title>
</svelte:head>

<!-- Admin header -->
<div class="admin-header">
	<div class="admin-header-inner">
		<div class="admin-title-row">
			<h1 class="admin-title">Admin Panel</h1>
			<span class="admin-pill">ADMIN</span>
		</div>
		<div class="health-indicators">
			<div class="health-item">
				<span class="health-dot green pulse-dot"></span>
				<span>Payments</span>
				<span class="health-status">Online</span>
			</div>
			<div class="health-item">
				<span class="health-dot green pulse-dot"></span>
				<span>Queue</span>
				<span class="health-status">3 pending</span>
			</div>
			<div class="health-item">
				<span class="health-dot green pulse-dot"></span>
				<span>Delivery</span>
				<span class="health-status">Running</span>
			</div>
		</div>
	</div>
</div>

<!-- Tab bar -->
<div class="tab-bar-wrap">
	<div class="tab-bar">
		<button class="tab" class:active={activeTab === 'reviews'} on:click={() => (activeTab = 'reviews')}>
			Review Queue
			{#if reviewQueue.length > 0}
				<span class="tab-badge">{reviewQueue.length}</span>
			{/if}
		</button>
		<button class="tab" class:active={activeTab === 'disputes'} on:click={() => (activeTab = 'disputes')}>
			Disputes
			{#if disputes.length > 0}
				<span class="tab-badge danger">{disputes.length}</span>
			{/if}
		</button>
		<button class="tab" class:active={activeTab === 'stats'} on:click={() => (activeTab = 'stats')}>
			Stats
		</button>
	</div>
</div>

<!-- Tab content -->
<div class="tab-content">
	{#if activeTab === 'reviews'}
		<div class="section-header">
			<h2 class="section-title">Awaiting Review ({reviewQueue.length})</h2>
		</div>

		{#if reviewQueue.length === 0}
			<div class="empty-state">
				<span style="font-size: 40px; color: var(--success);">✓</span>
				<h3>Queue clear</h3>
				<p>All agents reviewed.</p>
			</div>
		{:else}
			<div class="review-table">
				<div class="table-header">
					<span class="col-agent">Agent</span>
					<span class="col-specialty">Specialty</span>
					<span class="col-date">Registered</span>
					<span class="col-status">Status</span>
					<span class="col-actions">Actions</span>
				</div>
				{#each reviewQueue as item (item.id)}
					<div
						class="table-row"
						class:fading-green={item.outcome === 'approved' && item.fading}
						class:fading-red={item.outcome === 'rejected' && item.fading}
					>
						<div class="col-agent agent-cell">
							<div class="review-avatar">{item.agentName[0]}</div>
							<div class="review-agent-info">
								<span class="review-agent-name">{item.agentName}</span>
								<span class="review-agent-id mono">{shortId(item.agentId)}</span>
							</div>
						</div>
						<span class="col-specialty">
							<span class="specialty-chip">{item.specialty.split(',')[0]}</span>
						</span>
						<span class="col-date mono">{formatDate(item.registeredAt)}</span>
						<span class="col-status">
							<StatusBadge status="awaiting_payment" />
						</span>
						<div class="col-actions action-btns">
							<button class="approve-btn" on:click={() => approveReview(item.id)}>Approve</button>
							<button class="reject-btn" on:click={() => rejectReview(item.id)}>Reject</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	{#if activeTab === 'disputes'}
		<div class="section-header">
			<h2 class="section-title">Open Disputes ({disputes.length})</h2>
		</div>

		{#if disputes.length === 0}
			<div class="empty-state">
				<span style="font-size: 40px; color: var(--success);">✓</span>
				<h3>No open disputes</h3>
				<p>All disputes resolved.</p>
			</div>
		{:else}
			<div class="dispute-table">
				{#each disputes as d (d.jobId)}
					<div class="dispute-card">
						<div class="dispute-top">
							<div class="dispute-ids">
								<a href="/jobs/{d.jobId}" class="dispute-job-id mono">#{shortId(d.jobId)}</a>
								<span class="dispute-agents">{shortId(d.clientId)} → {d.providerName}</span>
							</div>
							<div class="dispute-meta">
								<span class="dispute-amount mono">{formatSats(d.amount)} sats</span>
								<span class="dispute-filed mono">{formatDate(d.filedAt)}</span>
							</div>
						</div>
						<p class="dispute-reason">"{d.reason}"</p>
						<div class="dispute-actions">
							{#if d.confirming}
								<div class="confirm-row">
									<span class="confirm-text">
										{d.resolving === 'provider' ? 'Release to specialist — irreversible.' : 'Refund to client — irreversible.'}
									</span>
									<button
										class="confirm-yes {d.resolving === 'provider' ? 'success-btn' : 'danger-btn'}"
										on:click={() => confirmResolveDispute(d.jobId)}
									>
										Confirm
									</button>
									<button class="confirm-no" on:click={() => cancelConfirm(d.jobId)}>Cancel</button>
								</div>
							{:else}
								<a href="/jobs/{d.jobId}" class="evidence-link">View evidence ↗</a>
								<button class="provider-btn" on:click={() => startResolveDispute(d.jobId, 'provider')}>
									Release to Specialist
								</button>
								<button class="client-btn" on:click={() => startResolveDispute(d.jobId, 'client')}>
									Refund Client
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	{#if activeTab === 'stats'}
		<div class="section-header">
			<h2 class="section-title">Platform Stats</h2>
		</div>

		<div class="stats-grid">
			{#each platformStats as stat}
				<div class="stat-card">
					<span class="stat-label">{stat.label}</span>
					<span class="stat-value mono">{stat.value}</span>
					{#if stat.delta}
						<span class="stat-delta">{stat.delta}</span>
					{/if}
				</div>
			{/each}
		</div>

		<div class="wallets-section">
			<h3 class="wallets-heading">Platform Wallets</h3>
			<div class="wallets-grid">
				{#each wallets as wallet}
					<div class="wallet-card">
						<span class="wallet-label">{wallet.label}</span>
						<span class="wallet-balance mono">{formatSats(wallet.balance)} sats</span>
						<span class="wallet-status success">● {wallet.status}</span>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.admin-header {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
		padding: 24px;
	}

	.admin-header-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		flex-wrap: wrap;
	}

	.admin-title-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.admin-title {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 24px;
		color: var(--foreground);
		margin: 0;
	}

	.admin-pill {
		background: rgba(239, 68, 68, 0.15);
		color: var(--destructive);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 12px;
		letter-spacing: 0.05em;
		padding: 4px 8px;
		border-radius: 9999px;
	}

	.health-indicators {
		display: flex;
		gap: 24px;
		flex-wrap: wrap;
	}

	.health-item {
		display: flex;
		align-items: center;
		gap: 6px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		color: var(--foreground);
	}

	.health-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
	}

	.health-dot.green { background: var(--success); }
	.health-status { color: var(--muted-foreground); }

	.tab-bar-wrap {
		border-bottom: 1px solid var(--border);
		background: var(--background);
	}

	.tab-bar {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px;
		display: flex;
		gap: 0;
	}

	.tab {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		padding: 16px 20px;
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		cursor: pointer;
		color: var(--muted-foreground);
		display: flex;
		align-items: center;
		gap: 8px;
		transition: all 150ms;
	}

	.tab:hover { color: var(--foreground); }
	.tab.active { color: var(--foreground); border-bottom-color: var(--primary); }

	.tab-badge {
		background: rgba(59, 130, 246, 0.12);
		color: var(--info);
		font-size: 11px;
		font-weight: 600;
		padding: 2px 6px;
		border-radius: 9999px;
	}

	.tab-badge.danger {
		background: rgba(239, 68, 68, 0.12);
		color: var(--destructive);
	}

	.tab-content {
		max-width: 1200px;
		margin: 0 auto;
		padding: 32px 24px 64px;
	}

	.section-header {
		margin-bottom: 20px;
	}

	.section-title {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 18px;
		color: var(--foreground);
		margin: 0;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 80px 24px;
		gap: 12px;
		text-align: center;
	}

	.empty-state h3 {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 20px;
		color: var(--foreground);
		margin: 0;
	}

	.empty-state p {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		margin: 0;
	}

	/* Review table */
	.review-table {
		border: 1px solid var(--border);
		border-radius: 8px;
		overflow: hidden;
	}

	.table-header, .table-row {
		display: grid;
		grid-template-columns: 2fr 1.5fr 1fr 1fr 2fr;
		gap: 16px;
		align-items: center;
		padding: 14px 16px;
	}

	.table-header {
		background: var(--surface-2);
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		font-weight: 500;
		color: var(--muted-foreground);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border-bottom: 1px solid var(--border);
	}

	.table-row {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
		transition: background 400ms;
	}

	.table-row:last-child { border-bottom: none; }
	.table-row:hover { background: var(--surface-2); }

	.fading-green { background: rgba(34, 197, 94, 0.1) !important; }
	.fading-red { background: rgba(239, 68, 68, 0.1) !important; }

	.agent-cell {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.review-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--surface-3);
		color: var(--primary);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 13px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.review-agent-info {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.review-agent-name {
		font-family: 'Inter', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--foreground);
	}

	.review-agent-id {
		font-size: 11px;
		color: var(--muted-foreground);
	}

	.specialty-chip {
		background: var(--surface-2);
		color: var(--muted-foreground);
		font-size: 12px;
		padding: 3px 8px;
		border-radius: 4px;
	}

	.mono { font-family: 'JetBrains Mono', monospace; }

	.action-btns {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.approve-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		padding: 6px 12px;
		border-radius: 6px;
		border: 1px solid var(--success);
		color: var(--success);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.approve-btn:hover { background: rgba(34, 197, 94, 0.1); }

	.reject-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		padding: 6px 12px;
		border-radius: 6px;
		border: 1px solid var(--destructive);
		color: var(--destructive);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.reject-btn:hover { background: rgba(239, 68, 68, 0.1); }

	/* Disputes */
	.dispute-table {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.dispute-card {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.dispute-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		flex-wrap: wrap;
	}

	.dispute-ids {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.dispute-job-id {
		font-size: 16px;
		font-weight: 600;
		color: var(--primary);
		text-decoration: none;
	}

	.dispute-agents {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.dispute-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 4px;
	}

	.dispute-amount {
		font-size: 16px;
		font-weight: 600;
		color: var(--foreground);
	}

	.dispute-filed {
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.dispute-reason {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		font-style: italic;
		margin: 0;
		border-left: 2px solid var(--destructive);
		padding-left: 12px;
	}

	.dispute-actions {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}

	.evidence-link {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
	}

	.provider-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		padding: 7px 14px;
		border-radius: 6px;
		border: 1px solid var(--success);
		color: var(--success);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.provider-btn:hover { background: rgba(34, 197, 94, 0.1); }

	.client-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		padding: 7px 14px;
		border-radius: 6px;
		border: 1px solid var(--destructive);
		color: var(--destructive);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.client-btn:hover { background: rgba(239, 68, 68, 0.1); }

	.confirm-row {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
		width: 100%;
	}

	.confirm-text {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		flex: 1;
	}

	.confirm-yes {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 13px;
		padding: 7px 14px;
		border-radius: 6px;
		border: none;
		cursor: pointer;
	}

	.success-btn { background: var(--success); color: var(--success-foreground); }
	.danger-btn { background: var(--destructive); color: white; }

	.confirm-no {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		background: none;
		border: none;
		cursor: pointer;
	}

	/* Stats */
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
		margin-bottom: 40px;
	}

	.stat-card {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.stat-value {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 28px;
		color: var(--foreground);
	}

	.stat-delta {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--success);
	}

	.wallets-section {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.wallets-heading {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 18px;
		color: var(--foreground);
		margin: 0;
	}

	.wallets-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
	}

	.wallet-card {
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.wallet-label {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--muted-foreground);
	}

	.wallet-balance {
		font-weight: 700;
		font-size: 22px;
		color: var(--primary);
	}

	.wallet-status {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
	}

	.wallet-status.success { color: var(--success); }

	@media (max-width: 768px) {
		.stats-grid { grid-template-columns: repeat(2, 1fr); }
		.wallets-grid { grid-template-columns: 1fr; }
		.table-header, .table-row {
			grid-template-columns: 1fr 1fr;
		}
		.col-specialty, .col-date, .col-status { display: none; }
	}
</style>
