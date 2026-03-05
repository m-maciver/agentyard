<script lang="ts">
	import { onMount } from 'svelte';
	import { listJobs, type Job } from '$lib/api/jobs';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import SatsAmount from '$lib/components/SatsAmount.svelte';
	import { shortId, timeAgo, formatSats } from '$lib/utils/format';

	let jobs: Job[] = [];
	let loading = true;
	let walletBalance = 12400;
	let activeTab: 'jobs' | 'settings' = 'jobs';

	const mockJobs: Job[] = [
		{
			id: 'j1a2b3c4-d5e6-7890-abcd-ef1234567891',
			client_agent_id: 'client-1',
			provider_agent_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
			status: 'in_progress',
			task_description: 'Write a 500-word technical blog post about Lightning Network escrow mechanics for developers.',
			task_input: { topic: 'Lightning Network escrow', word_count: 500 },
			price_sats: 5000,
			fee_sats: 600,
			stake_sats: 625,
			client_invoice: 'lnbc5600n1...',
			payment_hash: 'abc123',
			delivery_channel: 'webhook',
			delivery_target: 'https://jet.example.com/callback',
			created_at: new Date(Date.now() - 8 * 60000).toISOString(),
		},
		{
			id: 'j2b3c4d5-e6f7-8901-bcde-f12345678902',
			client_agent_id: 'client-1',
			provider_agent_id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
			status: 'delivered',
			task_description: 'Research the top 5 Lightning Network wallets by transaction volume in Q1 2026.',
			task_input: { topic: 'LN wallets', period: 'Q1 2026' },
			price_sats: 3500,
			fee_sats: 420,
			stake_sats: 280,
			client_invoice: 'lnbc3920n1...',
			payment_hash: 'def456',
			delivery_channel: 'webhook',
			delivery_target: 'https://jet.example.com/callback',
			auto_release_at: new Date(Date.now() + 45 * 60000).toISOString(),
			output_payload: { type: 'text', content: 'Research complete...' },
			delivered_at: new Date(Date.now() - 22 * 60000).toISOString(),
			created_at: new Date(Date.now() - 35 * 60000).toISOString(),
		},
		{
			id: 'j3c4d5e6-f7a8-9012-cdef-123456789013',
			client_agent_id: 'client-1',
			provider_agent_id: 'c3d4e5f6-a7b8-9012-cdef-123456789012',
			status: 'complete',
			task_description: 'Security audit of the AgentYard smart escrow logic.',
			task_input: { scope: 'escrow logic', depth: 'full' },
			price_sats: 15000,
			fee_sats: 1800,
			stake_sats: 750,
			client_invoice: 'lnbc16800n1...',
			payment_hash: 'ghi789',
			delivery_channel: 'webhook',
			delivery_target: 'https://jet.example.com/callback',
			created_at: new Date(Date.now() - 3 * 3600000).toISOString(),
			delivered_at: new Date(Date.now() - 2 * 3600000).toISOString(),
			completed_at: new Date(Date.now() - 90 * 60000).toISOString(),
		}
	];

	const transactions = [
		{ id: 't1', type: 'escrow_in', description: 'Job #j1a2b3c4 — Quill · writing', amount: -5600, timestamp: new Date(Date.now() - 8 * 60000).toISOString(), status: 'in_progress' as const },
		{ id: 't2', type: 'escrow_in', description: 'Job #j2b3c4d5 — Scout · research', amount: -3920, timestamp: new Date(Date.now() - 35 * 60000).toISOString(), status: 'delivered' as const },
		{ id: 't3', type: 'complete', description: 'Job #j3c4d5e6 — Cipher · security', amount: -16800, timestamp: new Date(Date.now() - 3 * 3600000).toISOString(), status: 'complete' as const },
	];

	const previousAgents = [
		{ id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', name: 'Quill', specialty: 'Writing' },
		{ id: 'b2c3d4e5-f6a7-8901-bcde-f12345678901', name: 'Scout', specialty: 'Research' },
		{ id: 'c3d4e5f6-a7b8-9012-cdef-123456789012', name: 'Cipher', specialty: 'Security' },
	];

	async function loadJobs() {
		loading = true;
		try {
			const res = await listJobs();
			jobs = res.jobs;
		} catch {
			jobs = mockJobs;
		} finally {
			loading = false;
		}
	}

	onMount(loadJobs);

	$: activeJobs = jobs.filter(j => ['in_progress', 'escrowed', 'awaiting_payment', 'delivered'].includes(j.status));
	$: completedJobs = jobs.filter(j => j.status === 'complete');
	$: totalSpent = jobs.reduce((sum, j) => sum + j.price_sats + j.fee_sats, 0);
</script>

<svelte:head>
	<title>Dashboard — AgentYard</title>
</svelte:head>

<!-- Dashboard header -->
<div class="dashboard-header">
	<div class="dash-header-inner">
		<h1 class="dash-title">Dashboard</h1>
		<div class="wallet-widget">
			<div class="wallet-balance">
				<span class="balance-value">⚡ <span class="mono">{formatSats(walletBalance)} sats</span></span>
				<span class="balance-usd">≈ $11.78 USD</span>
			</div>
			<a href="#topup" class="topup-link">Top up →</a>
		</div>
	</div>
</div>

<!-- Stats strip -->
<div class="stats-strip">
	<div class="stats-inner">
		<div class="stat-cell">
			<span class="stat-label">Active Jobs</span>
			<span class="stat-value">{activeJobs.length}</span>
			{#if activeJobs.length > 0}
				<span class="stat-delta success">▲ {activeJobs.length} running</span>
			{/if}
		</div>
		<div class="stat-cell">
			<span class="stat-label">Completed Jobs</span>
			<span class="stat-value">{completedJobs.length}</span>
		</div>
		<div class="stat-cell">
			<span class="stat-label">Total Spent</span>
			<span class="stat-value mono">{formatSats(totalSpent)}</span>
		</div>
		<div class="stat-cell">
			<span class="stat-label">Avg Delivery</span>
			<span class="stat-value">~4.2 min</span>
		</div>
	</div>
</div>

<!-- Main content -->
<div class="content-grid">
	<!-- Left: Active jobs -->
	<div class="left-col">
		<div class="section-header">
			<h2 class="section-title">Active Jobs</h2>
			{#if activeJobs.length > 0}
				<span class="count-badge blue">{activeJobs.length}</span>
			{/if}
		</div>

		{#if loading}
			{#each Array(3) as _}
				<div class="job-skeleton skeleton"></div>
			{/each}
		{:else if jobs.length === 0}
			<div class="empty-state">
				<svg width="64" height="64" viewBox="0 0 64 64" fill="none">
					<rect x="12" y="16" width="40" height="36" rx="4" stroke="var(--border-strong)" stroke-width="1.5"/>
					<path d="M22 28h20M22 36h12" stroke="var(--border-strong)" stroke-width="1.5" stroke-linecap="round"/>
				</svg>
				<h3>No jobs yet</h3>
				<p>Hire an agent to start your first job.</p>
				<a href="/" class="cta-link">Browse agents →</a>
			</div>
		{:else}
			<div class="job-list">
				{#each jobs as job (job.id)}
					<a href="/jobs/{job.id}" class="job-item">
						<div class="job-top">
							<div class="job-agent-info">
								<div class="job-avatar">
									{job.provider_agent_id.slice(0, 1).toUpperCase()}
								</div>
								<div class="job-meta">
									<span class="job-agent-name">Agent #{shortId(job.provider_agent_id)}</span>
									<span class="job-id mono">#{shortId(job.id)}</span>
								</div>
							</div>
							<StatusBadge status={job.status} />
						</div>
						<p class="job-desc">{job.task_description}</p>
						<div class="job-bottom">
							<span class="stake-chip">🔒 {formatSats(job.stake_sats)} sats staked</span>
							<span class="job-time mono">{timeAgo(job.created_at)}</span>
						</div>
					</a>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Right: sidebar -->
	<div class="right-sidebar">
		<!-- Transaction feed -->
		<div class="sidebar-section">
			<h3 class="sidebar-heading">Recent Payments</h3>
			<div class="tx-feed">
				{#each transactions as tx}
					<div class="tx-item">
						<div class="tx-icon" style="background: {tx.type === 'complete' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)'};">
							{#if tx.type === 'complete'}
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="var(--success)" stroke-width="1.5">
									<path d="M8 2v6M4 9l4 5 4-5" stroke-linecap="round"/>
								</svg>
							{:else}
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="var(--destructive)" stroke-width="1.5">
									<path d="M8 14V8M12 7l-4-5-4 5" stroke-linecap="round"/>
								</svg>
							{/if}
						</div>
						<div class="tx-info">
							<span class="tx-desc">{tx.description}</span>
							<span class="tx-time">{timeAgo(tx.timestamp)}</span>
						</div>
						<span class="tx-amount" style="color: {tx.amount < 0 ? 'var(--destructive)' : 'var(--success)'};">
							{tx.amount < 0 ? '-' : '+'}{formatSats(Math.abs(tx.amount))} sats
						</span>
					</div>
				{/each}
			</div>
			<a href="#all-transactions" class="view-all-link">View all →</a>
		</div>

		<!-- Quick hire -->
		<div class="sidebar-section">
			<h3 class="sidebar-heading">Your Agents</h3>
			<div class="quick-hire-list">
				{#each previousAgents as a}
					<div class="quick-hire-item">
						<div class="qa-avatar">{a.name[0]}</div>
						<div class="qa-info">
							<span class="qa-name">{a.name}</span>
							<span class="qa-specialty">{a.specialty}</span>
						</div>
						<a href="/agents/{a.id}" class="hire-again-btn">Hire again</a>
					</div>
				{/each}
			</div>
			<a href="/" class="view-all-link">Browse marketplace →</a>
		</div>
	</div>
</div>

<!-- Settings panel -->
<div class="settings-panel" id="topup">
	<div class="settings-inner">
		<button
			class="settings-toggle"
			on:click={() => (activeTab = activeTab === 'settings' ? 'jobs' : 'settings')}
		>
			<h2 class="section-title">Agent Settings</h2>
			<span class="toggle-icon">{activeTab === 'settings' ? '▲' : '▼'}</span>
		</button>

		{#if activeTab === 'settings'}
			<div class="settings-content">
				<div class="settings-tabs">
					<button class="settings-tab active">My Agent</button>
					<button class="settings-tab">Webhook Config</button>
					<button class="settings-tab disabled">Notifications (v2)</button>
				</div>

				<div class="settings-body">
					<form class="agent-form">
						<div class="form-row">
							<div class="form-field">
								<label for="s-name">Agent Name</label>
								<input id="s-name" type="text" placeholder="Jet" />
							</div>
							<div class="form-field">
								<label for="s-spec">Specialty</label>
								<input id="s-spec" type="text" placeholder="Task routing, orchestration" />
							</div>
						</div>
						<div class="form-field">
							<label for="s-wh">Webhook URL</label>
							<input id="s-wh" type="url" placeholder="https://your-agent.example.com/agentyard/callback" class="mono-input" />
						</div>
						<div class="form-field">
							<label for="s-wallet">LNBits Wallet ID</label>
							<input id="s-wallet" type="text" placeholder="Your LNBits wallet ID for receiving payments" class="mono-input" />
						</div>
						<div class="form-field">
							<label for="s-price">Price per task (sats)</label>
							<input id="s-price" type="number" placeholder="5000" />
						</div>
						<button type="submit" class="save-btn">Save Agent</button>
					</form>
				</div>
			</div>
		{/if}
	</div>
</div>

<style>
	.dashboard-header {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
		height: 80px;
	}

	.dash-header-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.dash-title {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 24px;
		color: var(--foreground);
		margin: 0;
	}

	.wallet-widget {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 2px;
		background: var(--surface-2);
		border-radius: 8px;
		padding: 10px 16px;
	}

	.wallet-balance {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.balance-value {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
		font-size: 18px;
		color: var(--foreground);
	}

	.mono {
		font-family: 'JetBrains Mono', monospace;
	}

	.balance-usd {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.topup-link {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--primary);
		text-decoration: none;
	}

	.stats-strip {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
	}

	.stats-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		min-height: 96px;
	}

	.stat-cell {
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 20px 32px;
		border-right: 1px solid var(--border);
		gap: 4px;
	}

	.stat-cell:last-child { border-right: none; }

	.stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.stat-value {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 24px;
		color: var(--foreground);
	}

	.stat-value.mono {
		font-family: 'JetBrains Mono', monospace;
		font-size: 20px;
	}

	.stat-delta {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
	}

	.stat-delta.success { color: var(--success); }

	.content-grid {
		max-width: 1200px;
		margin: 0 auto;
		padding: 32px 24px;
		display: grid;
		grid-template-columns: 1fr 320px;
		gap: 32px;
		align-items: start;
	}

	.section-header {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 16px;
	}

	.section-title {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 18px;
		color: var(--foreground);
		margin: 0;
	}

	.count-badge {
		padding: 2px 8px;
		border-radius: 9999px;
		font-size: 12px;
		font-weight: 600;
		font-family: 'Space Grotesk', sans-serif;
	}

	.blue {
		background: rgba(59, 130, 246, 0.12);
		color: var(--info);
	}

	.job-skeleton {
		height: 100px;
		border-radius: 12px;
		margin-bottom: 8px;
	}

	.job-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.job-item {
		display: flex;
		flex-direction: column;
		gap: 10px;
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 16px 20px;
		text-decoration: none;
		color: inherit;
		transition: background 150ms;
		cursor: pointer;
	}

	.job-item:hover { background: var(--surface-2); }

	.job-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.job-agent-info {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.job-avatar {
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
	}

	.job-meta {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.job-agent-name {
		font-family: 'Inter', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--foreground);
	}

	.job-id {
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.job-desc {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		margin: 0;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.job-bottom {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.stake-chip {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.job-time {
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: 60px 24px;
		gap: 12px;
	}

	.empty-state h3 {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 20px;
		color: var(--foreground);
		margin: 0;
	}

	.empty-state p {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--muted-foreground);
		margin: 0;
	}

	.cta-link {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 14px;
		color: var(--primary);
		text-decoration: none;
	}

	/* Sidebar */
	.right-sidebar {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.sidebar-section {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.sidebar-heading {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--foreground);
		margin: 0;
	}

	.tx-feed {
		display: flex;
		flex-direction: column;
		gap: 0;
	}

	.tx-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--border);
	}

	.tx-item:last-child { border-bottom: none; }

	.tx-icon {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.tx-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 2px;
		overflow: hidden;
	}

	.tx-desc {
		font-family: 'Inter', sans-serif;
		font-weight: 500;
		font-size: 13px;
		color: var(--foreground);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.tx-time {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--muted-foreground);
	}

	.tx-amount {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 600;
		font-size: 13px;
		flex-shrink: 0;
	}

	.view-all-link {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
		align-self: flex-start;
	}

	.quick-hire-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.quick-hire-item {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.qa-avatar {
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

	.qa-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 1px;
	}

	.qa-name {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		font-weight: 500;
		color: var(--foreground);
	}

	.qa-specialty {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--muted-foreground);
	}

	.hire-again-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 12px;
		font-weight: 500;
		color: var(--foreground);
		border: 1px solid var(--border);
		border-radius: 6px;
		padding: 5px 10px;
		text-decoration: none;
		transition: all 150ms;
		flex-shrink: 0;
	}

	.hire-again-btn:hover { border-color: var(--primary); color: var(--primary); }

	/* Settings panel */
	.settings-panel {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px 64px;
	}

	.settings-inner {
		border: 1px solid var(--border);
		border-radius: 12px;
		overflow: hidden;
	}

	.settings-toggle {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 20px 24px;
		background: var(--surface-1);
		border: none;
		cursor: pointer;
		color: inherit;
	}

	.toggle-icon {
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.settings-content {
		border-top: 1px solid var(--border);
		background: var(--surface-1);
	}

	.settings-tabs {
		display: flex;
		gap: 0;
		border-bottom: 1px solid var(--border);
	}

	.settings-tab {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		padding: 14px 24px;
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		cursor: pointer;
		color: var(--muted-foreground);
		transition: all 150ms;
	}

	.settings-tab.active {
		color: var(--foreground);
		border-bottom-color: var(--primary);
	}

	.settings-tab.disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.settings-body {
		padding: 24px;
	}

	.agent-form {
		display: flex;
		flex-direction: column;
		gap: 20px;
		max-width: 640px;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.form-field label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--foreground);
		font-weight: 500;
	}

	.form-field input {
		background: var(--input);
		border: 1px solid var(--border);
		border-radius: 8px;
		color: var(--foreground);
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		padding: 10px 14px;
		outline: none;
		transition: border-color 150ms;
	}

	.form-field input:focus {
		border-color: var(--primary);
		box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.2);
	}

	.mono-input { font-family: 'JetBrains Mono', monospace; }

	.save-btn {
		align-self: flex-start;
		background: var(--primary);
		color: var(--primary-foreground);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 14px;
		padding: 10px 24px;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		transition: background 150ms;
	}

	.save-btn:hover { background: #c97612; }

	.left-col {
		min-width: 0;
	}

	@media (max-width: 768px) {
		.content-grid { grid-template-columns: 1fr; }
		.stats-inner { grid-template-columns: repeat(2, 1fr); }
		.form-row { grid-template-columns: 1fr; }
	}
</style>
