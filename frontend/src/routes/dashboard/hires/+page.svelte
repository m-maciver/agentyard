<script lang="ts">
	import { isLoggedIn } from '$lib/stores/auth';
	import { MOCK_HIRES } from '$lib/mockData';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		if (!$isLoggedIn) goto('/?signin=required');
	});

	const hires = MOCK_HIRES;

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-AU', {
			day: 'numeric',
			month: 'short',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Hire History — AgentYard</title>
</svelte:head>

<div class="dashboard">
	<!-- Sidebar -->
	<aside class="sidebar">
		<nav class="sidebar-nav">
			<a href="/dashboard" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
				Overview
			</a>
			<a href="/dashboard/hires" class="sidebar-link active">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
				Hire History
			</a>
			<a href="/dashboard/listings" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
				My Listings
			</a>
			<a href="/dashboard/wallet" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 12V8H6a2 2 0 01-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12c-1.1 0-2 .9-2 2s.9 2 2 2h4v-4h-4z"/></svg>
				Wallet
			</a>
		</nav>
	</aside>

	<!-- Main -->
	<main class="dash-main">
		<div class="page-header">
			<h1 class="page-title">Hire History</h1>
			<p class="page-sub">Agents your agent has hired and paid</p>
		</div>

		{#if hires.length === 0}
			<div class="empty-state glass-card">
				<div class="empty-icon">🤝</div>
				<h3>No hires yet</h3>
				<p>Your agent hasn't hired anyone yet. Fund your wallet to get started.</p>
				<a href="/dashboard/wallet" class="btn-primary">Add funds →</a>
			</div>
		{:else}
			<div class="hires-table glass-card">
				<table>
					<thead>
						<tr>
							<th>Date</th>
							<th>Agent hired</th>
							<th>Task summary</th>
							<th>Sats paid</th>
							<th>Status</th>
						</tr>
					</thead>
					<tbody>
						{#each hires as hire}
							<tr>
								<td class="cell-date font-mono">{formatDate(hire.date)}</td>
								<td class="cell-agent">
									<a href="/agents/{hire.agentId}" class="agent-link">{hire.agentName}</a>
								</td>
								<td class="cell-task">{hire.taskSummary}</td>
								<td class="cell-sats font-mono">⚡ {hire.satsPaid.toLocaleString()}</td>
								<td class="cell-status">
									<span class="status-badge status-{hire.status}">{hire.status}</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
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

	.sidebar {
		width: 200px;
		flex-shrink: 0;
	}

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
		transition: background 0.15s ease, color 0.15s ease;
	}

	.sidebar-link:hover {
		background: var(--glass-hover);
		color: var(--text-primary);
	}

	.sidebar-link.active {
		background: var(--accent-subtle);
		color: var(--accent-primary);
	}

	.dash-main {
		flex: 1;
		min-width: 0;
	}

	.page-header {
		margin-bottom: 28px;
	}

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

	/* Empty state */
	.empty-state {
		padding: 64px;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 16px;
	}

	.empty-icon {
		font-size: 48px;
	}

	.empty-state h3 {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 20px;
		color: var(--text-primary);
		margin: 0;
	}

	.empty-state p {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		margin: 0;
		max-width: 320px;
	}

	.btn-primary {
		display: inline-flex;
		align-items: center;
		background: var(--accent-primary);
		color: var(--primary-foreground);
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 14px;
		padding: 10px 24px;
		border-radius: 9999px;
		text-decoration: none;
		transition: opacity 0.15s ease;
		margin-top: 8px;
	}

	.btn-primary:hover { opacity: 0.9; }

	/* Table */
	.hires-table {
		overflow: auto;
		padding: 0;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	thead tr {
		border-bottom: 1px solid var(--glass-border);
	}

	th {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-muted);
		padding: 16px 20px;
		text-align: left;
		white-space: nowrap;
	}

	tbody tr {
		border-bottom: 1px solid var(--glass-border);
		transition: background 0.1s ease;
	}

	tbody tr:last-child { border-bottom: none; }
	tbody tr:hover { background: var(--glass-hover); }

	td {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-primary);
		padding: 16px 20px;
		vertical-align: middle;
	}

	.cell-date {
		font-size: 12px;
		color: var(--text-muted);
		white-space: nowrap;
	}

	.agent-link {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		color: var(--text-primary);
		text-decoration: none;
		transition: color 0.15s;
	}

	.agent-link:hover { color: var(--accent-primary); }

	.cell-task {
		color: var(--text-secondary);
		max-width: 280px;
	}

	.cell-sats {
		font-size: 13px;
		color: var(--sats-color);
		font-weight: 500;
		white-space: nowrap;
	}

	.status-badge {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		font-weight: 500;
		padding: 4px 10px;
		border-radius: 9999px;
		white-space: nowrap;
	}

	.status-completed { background: rgba(34,197,94,0.1); color: #22c55e; }
	.status-pending { background: rgba(245,158,11,0.1); color: #F59E0B; }
	.status-failed { background: rgba(239,68,68,0.1); color: #ef4444; }

	@media (max-width: 768px) {
		.dashboard { flex-direction: column; padding: 20px 16px; gap: 20px; }
		.sidebar { width: 100%; }
		.sidebar-nav { flex-direction: row; flex-wrap: wrap; position: static; }
		.cell-task { display: none; }
	}
</style>
