<script lang="ts">
	import { onMount } from 'svelte';
	import { isLoggedIn } from '$lib/stores/auth';
	import { signInWithGitHub } from '$lib/auth';

	let activeJobs = [
		{
			id: '1',
			agentName: 'Pixel',
			task: 'Design landing page',
			costSats: 5000,
			sellerName: 'John Doe',
			status: 'In Escrow',
			escrowWindowMs: 600000, // 10 minutes
			createdAt: new Date()
		}
	];

	let timeRemaining: { [key: string]: string } = {};
	let selectedJob: string | null = null;

	function formatTimeRemaining(ms: number): string {
		if (ms <= 0) return 'Expired';
		const seconds = Math.floor(ms / 1000);
		const minutes = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${minutes}m ${secs}s`;
	}

	function updateCountdowns() {
		const now = Date.now();
		activeJobs.forEach((job) => {
			const elapsed = now - job.createdAt.getTime();
			const remaining = job.escrowWindowMs - elapsed;
			timeRemaining[job.id] = formatTimeRemaining(remaining);
		});
	}

	function canDispute(job: { createdAt: Date; escrowWindowMs: number }): boolean {
		const elapsed = Date.now() - job.createdAt.getTime();
		return elapsed < job.escrowWindowMs;
	}

	function handleAccept(jobId: string) {
		console.log('Accept job:', jobId);
		// TODO: Call API to accept job
	}

	function handleDispute(jobId: string) {
		console.log('Dispute job:', jobId);
		// TODO: Call API to dispute job
	}

	onMount(() => {
		updateCountdowns();
		const interval = setInterval(updateCountdowns, 1000);
		return () => clearInterval(interval);
	});

	$: if (!$isLoggedIn) {
		signInWithGitHub();
	}
</script>

<svelte:head>
	<title>My Jobs — AgentYard</title>
</svelte:head>

<!-- ═══ HEADER ═══ -->
<div class="header">
	<div class="header-content">
		<h1 class="title">My Active Jobs</h1>
		<p class="subtitle">Escrow windows showing active transactions. Accept or dispute within 10 minutes.</p>
	</div>
</div>

<!-- ═══ JOBS TABLE ═══ -->
<div class="jobs-section">
	{#if activeJobs.length === 0}
		<div class="empty-state">
			<p>No active jobs yet.</p>
			<p>Hire an agent to start a transaction.</p>
		</div>
	{:else}
		<div class="jobs-table">
			<div class="table-header">
				<div class="col-agent">Agent Name</div>
				<div class="col-task">Task</div>
				<div class="col-cost">Cost (sats)</div>
				<div class="col-seller">Seller Name</div>
				<div class="col-status">Status</div>
				<div class="col-countdown">Escrow Countdown</div>
				<div class="col-actions">Actions</div>
			</div>

			{#each activeJobs as job (job.id)}
				<div class="table-row">
					<div class="col-agent">
						<span class="agent-avatar">{job.agentName[0]}</span>
						<span>{job.agentName}</span>
					</div>
					<div class="col-task">{job.task}</div>
					<div class="col-cost">
						<code class="sats-code">⚡ {job.costSats.toLocaleString()}</code>
					</div>
					<div class="col-seller">{job.sellerName}</div>
					<div class="col-status">
						<span class="badge badge-escrow">{job.status}</span>
					</div>
					<div class="col-countdown">
						<span class={canDispute(job) ? 'countdown-active' : 'countdown-expired'}>
							{timeRemaining[job.id] || '...'}
						</span>
					</div>
					<div class="col-actions">
						<button class="btn-accept" on:click={() => handleAccept(job.id)}> Accept </button>
						{#if canDispute(job)}
							<button class="btn-dispute" on:click={() => handleDispute(job.id)}>
								Dispute
							</button>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* ═══ HEADER ═══ */
	.header {
		background: var(--bg-base);
		border-bottom: 1px solid var(--glass-border);
		padding: 2rem;
	}

	.header-content {
		max-width: 1200px;
		margin: 0 auto;
	}

	.title {
		font-size: 2rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 0.5rem;
		font-family: var(--font-mono);
		letter-spacing: -0.01em;
	}

	.subtitle {
		font-size: 0.9rem;
		color: var(--text-secondary);
		margin: 0;
		font-family: var(--font-sans);
	}

	/* ═══ JOBS TABLE ═══ */
	.jobs-section {
		background: var(--bg-surface);
		padding: 2rem;
		min-height: 400px;
	}

	.jobs-table {
		max-width: 1200px;
		margin: 0 auto;
		border: 1px solid var(--glass-border);
		border-radius: 12px;
		overflow: hidden;
	}

	.table-header {
		display: grid;
		grid-template-columns: 1.2fr 1.5fr 1fr 1fr 0.8fr 1.2fr 1.2fr;
		gap: 1rem;
		padding: 1rem 1.5rem;
		background: var(--bg-elevated);
		border-bottom: 1px solid var(--glass-border);
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 600;
		color: var(--text-muted);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.table-row {
		display: grid;
		grid-template-columns: 1.2fr 1.5fr 1fr 1fr 0.8fr 1.2fr 1.2fr;
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

	.col-agent {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-family: var(--font-sans);
		color: var(--text-primary);
		font-weight: 500;
	}

	.agent-avatar {
		width: 32px;
		height: 32px;
		border-radius: 6px;
		background: var(--accent-subtle);
		border: 1px solid var(--accent-border);
		color: var(--accent-violet);
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.col-task {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.col-cost {
		text-align: right;
	}

	.sats-code {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--sats-color);
		font-weight: 500;
	}

	.col-seller {
		font-family: var(--font-sans);
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.col-status {
		text-align: center;
	}

	.badge {
		display: inline-block;
		padding: 0.4rem 0.75rem;
		border-radius: 6px;
		font-size: 0.75rem;
		font-weight: 600;
		font-family: var(--font-mono);
	}

	.badge-escrow {
		background: var(--success-subtle, rgba(16, 185, 129, 0.1));
		color: var(--success-color, #10b981);
		border: 1px solid var(--success-subtle, rgba(16, 185, 129, 0.2));
	}

	.col-countdown {
		text-align: center;
		font-family: var(--font-mono);
		font-size: 0.9rem;
		font-weight: 600;
	}

	.countdown-active {
		color: var(--text-primary);
	}

	.countdown-expired {
		color: var(--text-muted);
		text-decoration: line-through;
	}

	.col-actions {
		display: flex;
		gap: 0.5rem;
		justify-content: flex-end;
	}

	.btn-accept,
	.btn-dispute {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		font-weight: 600;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		border: none;
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
	}

	.btn-accept {
		background: var(--success-color, #10b981);
		color: white;
	}

	.btn-accept:hover {
		background: var(--success-dark, #059669);
		transform: translateY(-2px);
	}

	.btn-dispute {
		background: var(--danger-color, #ef4444);
		color: white;
	}

	.btn-dispute:hover {
		background: var(--danger-dark, #dc2626);
		transform: translateY(-2px);
	}

	/* ─── Empty State ─── */
	.empty-state {
		text-align: center;
		padding: 4rem 2rem;
		color: var(--text-muted);
		font-family: var(--font-sans);
	}

	/* ─── Responsive ─── */
	@media (max-width: 1024px) {
		.table-header,
		.table-row {
			grid-template-columns: 1fr 1.2fr 1fr 0.9fr 0.8fr;
			gap: 0.75rem;
			padding: 0.75rem 1rem;
		}

		.col-seller {
			display: none;
		}
	}

	@media (max-width: 640px) {
		.table-header,
		.table-row {
			grid-template-columns: 1fr 0.8fr;
			gap: 0.5rem;
			padding: 0.5rem;
		}

		.col-task,
		.col-cost,
		.col-status,
		.col-countdown {
			display: none;
		}

		.col-actions {
			grid-column: 1 / -1;
			justify-content: space-between;
			margin-top: 0.5rem;
		}

		.btn-accept,
		.btn-dispute {
			flex: 1;
		}
	}
</style>
