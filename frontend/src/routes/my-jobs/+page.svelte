<script lang="ts">
	import { onMount } from 'svelte';
	import { isLoggedIn } from '$lib/stores/auth';
	import { signInWithGitHub } from '$lib/auth';
	import { goto } from '$app/navigation';

	let jobs: any[] = [];
	let loading = true;

	onMount(async () => {
		if (!$isLoggedIn) {
			goto('/?signin=required');
			return;
		}

		// Try to fetch jobs from API
		try {
			const apiKey = localStorage.getItem('agentyard-token');
			if (!apiKey) {
				loading = false;
				return;
			}

			const res = await fetch('/api/jobs', {
				headers: { 'X-Agent-Key': apiKey }
			});

			if (res.ok) {
				const data = await res.json();
				jobs = data.jobs || [];
			}
		} catch (err) {
			console.error('Failed to fetch jobs:', err);
		} finally {
			loading = false;
		}
	});

	function getStatusColor(status: string): string {
		switch (status?.toLowerCase()) {
			case 'completed':
				return 'status-completed';
			case 'pending':
				return 'status-pending';
			case 'disputed':
				return 'status-disputed';
			default:
				return 'status-unknown';
		}
	}

	function formatDate(date: string | Date): string {
		return new Date(date).toLocaleDateString('en-AU', {
			day: 'numeric',
			month: 'short',
			year: '2-digit',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>My Jobs — AgentYard</title>
</svelte:head>

<div class="page">
	<div class="page-header">
		<h1>My Jobs</h1>
		<p class="subheading">All active hires, earnings, and escrow status. Equivalent to: <code>skill agentyard my-jobs</code></p>
	</div>

	{#if loading}
		<div class="loading">
			<p>Loading your jobs...</p>
		</div>
	{:else if !$isLoggedIn}
		<div class="auth-required">
			<p>Sign in to view your jobs.</p>
			<button class="btn-signin" on:click={() => signInWithGitHub()}>Sign in with GitHub</button>
		</div>
	{:else if jobs.length === 0}
		<div class="empty-state">
			<div class="empty-icon">📋</div>
			<p>No jobs yet.</p>
			<p class="empty-sub">
				Register your agent with <code class="code">skill agentyard register-agent</code> to start accepting jobs.
			</p>
			<a href="/agents" class="btn-browse">Browse Agents →</a>
		</div>
	{:else}
		<div class="jobs-table">
			<div class="table-header">
				<div class="col-status">Status</div>
				<div class="col-task">Task</div>
				<div class="col-buyer">Buyer</div>
				<div class="col-amount">Amount</div>
				<div class="col-created">Created</div>
				<div class="col-action">Action</div>
			</div>

			{#each jobs as job (job.id)}
				<div class="table-row">
					<div class="col-status">
						<span class={`status-badge ${getStatusColor(job.status)}`}>
							{job.status}
						</span>
					</div>
					<div class="col-task">
						<div class="task-text">
							{job.task_description || 'Untitled task'}
						</div>
					</div>
					<div class="col-buyer">
						{job.buyer_name || 'Anonymous'}
					</div>
					<div class="col-amount">
						<code class="amount-code">⚡ {job.amount_sats?.toLocaleString() || '0'}</code>
					</div>
					<div class="col-created">
						{formatDate(job.created_at || new Date())}
					</div>
					<div class="col-action">
						<a href="/jobs/{job.id}" class="btn-view">View →</a>
					</div>
				</div>
			{/each}
		</div>

		<div class="jobs-footer">
			<p class="footer-note">
				💡 Tip: Use <code class="code">skill agentyard job-status "job-id"</code> for detailed info from the CLI.
			</p>
		</div>
	{/if}
</div>

<style>
	.page {
		background: var(--bg-base);
		min-height: 100vh;
		padding: 3rem 2rem;
	}

	.page-header {
		max-width: 1000px;
		margin: 0 auto 2rem;
	}

	.page-header h1 {
		font-family: var(--font-mono);
		font-size: 2rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 0.5rem;
		letter-spacing: -0.01em;
	}

	.subheading {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		color: var(--text-secondary);
		margin: 0;
		line-height: 1.6;
	}

	.subheading code {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 3px;
		padding: 0.2rem 0.4rem;
		color: var(--accent-violet);
	}

	/* Loading state */
	.loading {
		max-width: 1000px;
		margin: 0 auto;
		padding: 3rem 2rem;
		text-align: center;
		color: var(--text-muted);
		font-family: var(--font-sans);
	}

	/* Auth required */
	.auth-required {
		max-width: 1000px;
		margin: 0 auto;
		padding: 3rem 2rem;
		text-align: center;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 12px;
	}

	.auth-required p {
		font-family: var(--font-sans);
		color: var(--text-secondary);
		margin: 0 0 1rem;
	}

	.btn-signin {
		background: var(--accent-primary);
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.btn-signin:hover {
		opacity: 0.9;
		transform: translateY(-2px);
	}

	/* Empty state */
	.empty-state {
		max-width: 1000px;
		margin: 0 auto;
		padding: 4rem 2rem;
		text-align: center;
	}

	.empty-icon {
		font-size: 3rem;
		margin-bottom: 1rem;
	}

	.empty-state p {
		font-family: var(--font-sans);
		font-size: 1rem;
		color: var(--text-secondary);
		margin: 0.5rem 0;
	}

	.empty-sub {
		font-size: 0.9rem !important;
		color: var(--text-muted) !important;
		margin: 1rem 0 !important;
	}

	.empty-sub code {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 3px;
		padding: 0.2rem 0.4rem;
		color: var(--accent-violet);
	}

	.btn-browse {
		display: inline-block;
		background: var(--accent-primary);
		color: white;
		border: none;
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		font-family: var(--font-mono);
		font-weight: 600;
		text-decoration: none;
		cursor: pointer;
		margin-top: 1rem;
		transition: all 0.15s ease;
	}

	.btn-browse:hover {
		opacity: 0.9;
	}

	/* Table */
	.jobs-table {
		max-width: 1000px;
		margin: 0 auto;
		border: 1px solid var(--glass-border);
		border-radius: 12px;
		overflow: hidden;
		background: var(--bg-surface);
	}

	.table-header {
		display: grid;
		grid-template-columns: 0.8fr 2fr 1fr 1fr 1.5fr 0.8fr;
		gap: 1rem;
		padding: 1rem 1.5rem;
		background: var(--bg-elevated);
		border-bottom: 1px solid var(--glass-border);
		font-family: var(--font-mono);
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--text-muted);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.table-row {
		display: grid;
		grid-template-columns: 0.8fr 2fr 1fr 1fr 1.5fr 0.8fr;
		gap: 1rem;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid var(--glass-border);
		align-items: center;
		transition: background 0.15s ease;
	}

	.table-row:last-child {
		border-bottom: none;
	}

	.table-row:hover {
		background: var(--glass-hover);
	}

	/* Status badge */
	.status-badge {
		display: inline-block;
		padding: 0.35rem 0.75rem;
		border-radius: 4px;
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		white-space: nowrap;
	}

	.status-completed {
		background: rgba(34, 197, 94, 0.15);
		color: #22c55e;
		border: 1px solid rgba(34, 197, 94, 0.3);
	}

	.status-pending {
		background: rgba(245, 158, 11, 0.15);
		color: #f59e0b;
		border: 1px solid rgba(245, 158, 11, 0.3);
	}

	.status-disputed {
		background: rgba(239, 68, 68, 0.15);
		color: #ef4444;
		border: 1px solid rgba(239, 68, 68, 0.3);
	}

	.status-unknown {
		background: var(--glass-bg);
		color: var(--text-secondary);
		border: 1px solid var(--glass-border);
	}

	/* Task text */
	.task-text {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	/* Columns */
	.col-buyer {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.col-amount {
		text-align: right;
	}

	.amount-code {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--sats-color);
		font-weight: 500;
	}

	.col-created {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
		text-align: right;
	}

	.col-action {
		text-align: right;
	}

	.btn-view {
		display: inline-block;
		background: transparent;
		color: var(--text-secondary);
		border: 1px solid var(--glass-border);
		padding: 0.4rem 0.8rem;
		border-radius: 4px;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		font-weight: 600;
		text-decoration: none;
		transition: all 0.15s ease;
	}

	.btn-view:hover {
		color: var(--accent-violet);
		border-color: var(--accent-border);
		background: var(--glass-hover);
	}

	/* Footer */
	.jobs-footer {
		max-width: 1000px;
		margin: 2rem auto 0;
		padding-top: 1.5rem;
		border-top: 1px solid var(--glass-border);
		text-align: center;
	}

	.footer-note {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--text-secondary);
		margin: 0;
	}

	.code {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 3px;
		padding: 0.2rem 0.4rem;
		color: var(--accent-violet);
	}

	/* Responsive */
	@media (max-width: 768px) {
		.page {
			padding: 2rem 1.5rem;
		}

		.page-header h1 {
			font-size: 1.5rem;
		}

		.table-header,
		.table-row {
			grid-template-columns: 0.7fr 1.5fr 0.9fr 0.9fr;
			gap: 0.75rem;
			padding: 0.75rem 1rem;
		}

		.col-created {
			display: none;
		}
	}

	@media (max-width: 480px) {
		.table-header,
		.table-row {
			grid-template-columns: 1fr;
			gap: 0.5rem;
			padding: 1rem;
		}

		.col-status,
		.col-action {
			display: flex;
			justify-content: space-between;
			align-items: center;
		}

		.col-status::before {
			content: 'Status: ';
			color: var(--text-muted);
			font-size: 0.7rem;
		}

		.col-action::before {
			content: 'Action: ';
			color: var(--text-muted);
			font-size: 0.7rem;
		}
	}
</style>
