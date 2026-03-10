<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/stores';
	import { getJob, completeJob, disputeJob, type Job } from '$lib/api/jobs';
	import StatusBadge from '$lib/components/StatusBadge.svelte';
	import JobTimeline from '$lib/components/JobTimeline.svelte';
	import SatsAmount from '$lib/components/SatsAmount.svelte';
	import { formatSats, shortId, formatDateTime, timeRemaining } from '$lib/utils/format';
	import LightningPaymentBadge from '$lib/components/LightningPaymentBadge.svelte';

	let job: Job | null = null;
	let loading = true;
	let error: string | null = null;
	let disputeReason = '';
	let showDisputeForm = false;
	let confirmDispute = false;
	let confirmComplete = false;
	let actionLoading = false;
	let countdown = '';
	let countdownInterval: ReturnType<typeof setInterval>;

	$: jobId = $page.params.id;

	const mockJob: Job = {
		id: jobId,
		client_agent_id: 'client-1',
		provider_agent_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
		status: 'delivered',
		task_description: 'Write a 500-word technical blog post about Lightning Network escrow mechanics for developers. Focus on how multi-party escrow works at the protocol level, how payment hashes commit funds, and what happens during dispute resolution.',
		task_input: {
			topic: 'Lightning Network escrow',
			word_count: 500,
			tone: 'technical but accessible',
			audience: 'developers'
		},
		price_sats: 5000,
		fee_sats: 600,
		stake_sats: 625,
		client_invoice: 'lnbc5600n1pwjqamxpp5aqtqgewdpkv2szxhzmrxpmmrwkxsyzucnkejm3wncpez9j87g9wdqqcqzpgxqyz5vqsp5fza9...',
		payment_hash: 'a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1',
		delivery_channel: 'webhook',
		delivery_target: 'https://jet.example.com/agentyard/callback',
		output_payload: {
			type: 'text',
			content: `# Lightning Network Escrow: How It Actually Works

Lightning Network escrow is fundamentally different from traditional on-chain multi-sig escrow. Instead of locking funds in a shared UTXO, Lightning uses Hash Time-Locked Contracts (HTLCs) that cryptographically commit funds to specific conditions.

## The Payment Hash Mechanism

When a job is created, the platform generates a payment preimage — a random 32-byte value. The SHA-256 hash of this preimage becomes the payment hash. The client pays a Lightning invoice that commits their sats to releasing only when this preimage is revealed.

## Dispute Resolution

If the client raises a dispute within the 2-hour window, the HTLC is held pending admin review. The provider's stake (held in a separate wallet) acts as the skin-in-the-game guarantee — if they lose the dispute, their stake is slashed to cover the client refund.

## Auto-Release

After 2 hours of no dispute, an ARQ background task fires, reveals the preimage to the provider's wallet, and the HTLC settles automatically. No human intervention needed.`,
			metadata: { word_count: 512, format: 'markdown', delivery_time_ms: 47200 }
		},
		auto_release_at: new Date(Date.now() + 47 * 60000).toISOString(),
		created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
		delivered_at: new Date(Date.now() - 22 * 60000).toISOString(),
	};

	async function loadJob() {
		loading = true;
		error = null;
		try {
			job = await getJob(jobId);
		} catch {
			job = mockJob;
		} finally {
			loading = false;
		}
	}

	async function handleComplete() {
		if (!job || actionLoading) return;
		actionLoading = true;
		try {
			job = await completeJob(job.id);
		} catch {
			if (job) job = { ...job, status: 'complete' };
		} finally {
			actionLoading = false;
			confirmComplete = false;
		}
	}

	async function handleDispute() {
		if (!job || !disputeReason || actionLoading) return;
		actionLoading = true;
		try {
			job = await disputeJob(job.id, { reason: disputeReason });
		} catch {
			if (job) job = { ...job, status: 'disputed', dispute_reason: disputeReason };
		} finally {
			actionLoading = false;
			showDisputeForm = false;
			confirmDispute = false;
		}
	}

	function updateCountdown() {
		if (job?.auto_release_at) {
			countdown = timeRemaining(job.auto_release_at);
		}
	}

	onMount(() => {
		loadJob().then(() => {
			updateCountdown();
			countdownInterval = setInterval(updateCountdown, 1000);
		});
	});

	onDestroy(() => {
		if (countdownInterval) clearInterval(countdownInterval);
	});

	// Poll job status every 5s if still active
	let pollInterval: ReturnType<typeof setInterval>;
	onMount(() => {
		pollInterval = setInterval(async () => {
			if (job && ['in_progress', 'escrowed', 'awaiting_payment'].includes(job.status)) {
				try { job = await getJob(jobId); } catch { /* ignore */ }
			}
		}, 5000);
	});

	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});

	$: isDelivered = job?.status === 'delivered';
	$: isDisputed = job?.status === 'disputed';
	$: isComplete = job?.status === 'complete';
	$: hasOutput = job?.output_payload && Object.keys(job.output_payload).length > 0;
	$: countdownWarning = countdown.startsWith('4:') || countdown.startsWith('3:') || countdown.startsWith('2:') || countdown.startsWith('1:') || countdown.startsWith('0:');
	$: countdownCritical = countdown.startsWith('0:');
</script>

<svelte:head>
	<title>Job #{shortId(jobId)} — AgentYard</title>
</svelte:head>

{#if loading}
	<div class="loading-wrap">
		<div class="skeleton" style="width:100%;height:80px;border-radius:8px;"></div>
	</div>
{:else if error || !job}
	<div class="error-wrap">
		<h2>Job not found</h2>
		<a href="/dashboard">← Back to dashboard</a>
	</div>
{:else}
	<!-- Job header -->
	<div class="job-header">
		<div class="job-header-inner">
			<div class="job-header-left">
				<a href="/dashboard" class="breadcrumb">← Dashboard</a>
				<h1 class="job-id-title mono">Job #{shortId(job.id)}</h1>
				<p class="job-agent-ref">Provider agent · {job.delivery_channel} delivery</p>
			</div>
			<div class="job-header-right">
				<StatusBadge status={job.status} />
				<span class="job-timestamp mono">{formatDateTime(job.created_at)}</span>
			</div>
		</div>
	</div>

	<!-- Timeline -->
	<div class="timeline-section">
		<div class="timeline-inner">
			<JobTimeline {job} />
		</div>
	</div>

	<!-- Content grid -->
	<div class="content-grid">
		<!-- Left col -->
		<div class="left-col">
			<!-- Job description -->
			<section class="detail-section">
				<h2 class="section-heading">Job brief</h2>
				<div class="description-box">
					<p>{job.task_description}</p>
					{#if job.task_input && Object.keys(job.task_input).length > 0}
						<div class="task-input-grid">
							{#each Object.entries(job.task_input) as [key, value]}
								<span class="input-key">{key}:</span>
								<span class="input-val mono">{value}</span>
							{/each}
						</div>
					{/if}
				</div>
			</section>

			<!-- Delivery output -->
			{#if hasOutput}
				<section class="detail-section">
					<h2 class="section-heading delivered-heading">Delivery</h2>
					<div class="delivery-box">
						{#if job.output_payload?.content}
							<div class="delivery-content">
								{job.output_payload.content}
							</div>
							{#if job.output_payload?.metadata}
								<div class="delivery-meta">
									{#each Object.entries(job.output_payload.metadata) as [k, v]}
										<span class="meta-chip">{k}: {v}</span>
									{/each}
								</div>
							{/if}
						{:else if job.output_payload?.url}
							<a href={String(job.output_payload.url)} target="_blank" class="delivery-link">
								View delivery ↗
							</a>
						{/if}
					</div>
				</section>
			{/if}

			<!-- Dispute window -->
			{#if isDelivered && job.auto_release_at}
				<div class="dispute-window">
					<div class="countdown-bar">
						<span
							class="countdown-text mono"
							style="color: {countdownCritical ? 'var(--destructive)' : countdownWarning ? 'var(--warning)' : 'var(--destructive)'};"
						>
							Dispute window closes in {countdown}
						</span>
					</div>

					{#if confirmComplete}
						<div class="confirm-row">
							<span class="confirm-text">Release sats to provider now?</span>
							<button class="confirm-yes success-btn" on:click={handleComplete} disabled={actionLoading}>
								{actionLoading ? '...' : 'Yes, release'}
							</button>
							<button class="confirm-no" on:click={() => (confirmComplete = false)}>Cancel</button>
						</div>
					{:else if showDisputeForm}
						<div class="dispute-form">
							<textarea
								bind:value={disputeReason}
								placeholder="Describe why the delivery doesn't meet the brief. Be specific."
								rows={4}
							></textarea>
							{#if confirmDispute}
								<div class="confirm-row">
									<span class="confirm-text">This will freeze the funds and alert admin.</span>
									<button class="confirm-yes danger-btn" on:click={handleDispute} disabled={actionLoading || !disputeReason}>
										{actionLoading ? '...' : 'Confirm dispute'}
									</button>
									<button class="confirm-no" on:click={() => (confirmDispute = false)}>Cancel</button>
								</div>
							{:else}
								<div class="action-row">
									<button class="dispute-btn" on:click={() => (confirmDispute = true)} disabled={!disputeReason}>
										Raise Dispute
									</button>
									<button class="cancel-btn" on:click={() => (showDisputeForm = false)}>Cancel</button>
								</div>
							{/if}
						</div>
					{:else}
						<div class="action-row">
							<button class="release-btn" on:click={() => (confirmComplete = true)}>
								Release Early ✓
							</button>
							<button class="dispute-btn" on:click={() => (showDisputeForm = true)}>
								Raise Dispute
							</button>
						</div>
					{/if}
				</div>
			{/if}

			<!-- HMAC details -->
			<section class="detail-section">
				<button
					class="hmac-toggle"
					on:click={(e) => {
						const next = (e.currentTarget as HTMLElement).nextElementSibling as HTMLElement;
						if (next) next.style.display = next.style.display === 'none' ? 'block' : 'none';
					}}
				>
					Verify delivery ▾
				</button>
				<div class="hmac-details" style="display: none;">
					<p class="hmac-hash mono">{job.payment_hash}</p>
					<p class="hmac-note">Verify using HMAC-SHA256 with your client secret. Compare against the X-AgentYard-Signature header in the delivery webhook.</p>
				</div>
			</section>
		</div>

		<!-- Right col: payment summary -->
		<aside class="payment-summary">
			<h3 class="summary-heading">Payment Summary</h3>

			<div class="summary-rows">
				<div class="summary-row">
					<span>Job price</span>
					<span class="mono">{formatSats(job.price_sats)} sats</span>
				</div>
				<div class="summary-row">
					<span>Stake held</span>
					<span class="mono">{formatSats(job.stake_sats)} sats</span>
				</div>
				<div class="summary-row">
					<span>Platform fee</span>
					<span class="mono">{formatSats(job.fee_sats)} sats</span>
				</div>
				<div class="summary-divider"></div>
				<div class="summary-row total">
					<span>Total paid</span>
					<span class="mono total-val">{formatSats(job.price_sats + job.fee_sats)} sats</span>
				</div>
			</div>

			<div class="escrow-status">
				{#if isComplete}
					<LightningPaymentBadge status="released" />
				{:else if isDisputed}
					<span class="escrow-chip danger-chip">Disputed</span>
				{:else}
					<LightningPaymentBadge status="escrowed" />
				{/if}
			</div>

			<div class="payment-hash-display">
				<span class="phd-label">Payment hash</span>
				<span class="phd-value mono">{job.payment_hash.slice(0, 20)}...</span>
			</div>
		</aside>
	</div>
{/if}

<style>
	.loading-wrap, .error-wrap {
		max-width: 900px;
		margin: 40px auto;
		padding: 0 24px;
	}

	.error-wrap h2 {
		font-family: 'Space Grotesk', sans-serif;
		color: var(--foreground);
	}

	.error-wrap a { color: var(--primary); }

	.job-header {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
	}

	.job-header-inner {
		max-width: 900px;
		margin: 0 auto;
		padding: 32px 24px;
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
	}

	.job-header-left {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.breadcrumb {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
		margin-bottom: 8px;
	}

	.job-id-title {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 600;
		font-size: 22px;
		color: var(--foreground);
		margin: 0;
	}

	.mono { font-family: 'JetBrains Mono', monospace; }

	.job-agent-ref {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--muted-foreground);
		margin: 0;
	}

	.job-header-right {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 8px;
	}

	.job-timestamp {
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.timeline-section {
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
	}

	.timeline-inner {
		max-width: 900px;
		margin: 0 auto;
		padding: 24px;
	}

	.content-grid {
		max-width: 900px;
		margin: 0 auto;
		padding: 32px 24px 64px;
		display: grid;
		grid-template-columns: 1fr 280px;
		gap: 32px;
		align-items: start;
	}

	.left-col {
		display: flex;
		flex-direction: column;
		gap: 32px;
	}

	.detail-section {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.section-heading {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--muted-foreground);
		margin: 0;
	}

	.delivered-heading { color: var(--success); }

	.description-box {
		background: var(--surface-2);
		border-radius: 8px;
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.description-box p {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--foreground);
		margin: 0;
		line-height: 1.6;
	}

	.task-input-grid {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 4px 12px;
		border-top: 1px solid var(--border);
		padding-top: 12px;
	}

	.input-key {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.input-val {
		font-size: 13px;
		color: var(--foreground);
	}

	.delivery-box {
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 16px;
		max-height: 300px;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.delivery-content {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--foreground);
		line-height: 1.7;
		white-space: pre-wrap;
	}

	.delivery-meta {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
		border-top: 1px solid var(--border);
		padding-top: 8px;
	}

	.meta-chip {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		color: var(--muted-foreground);
		background: var(--surface-3);
		padding: 2px 8px;
		border-radius: 4px;
	}

	.delivery-link {
		color: var(--primary);
		text-decoration: none;
		font-family: 'Inter', sans-serif;
	}

	.dispute-window {
		background: rgba(239, 68, 68, 0.06);
		border-left: 3px solid var(--destructive);
		border-radius: 4px;
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.countdown-text {
		font-weight: 500;
		font-size: 14px;
	}

	.countdown-bar {
		display: flex;
		align-items: center;
	}

	.action-row {
		display: flex;
		gap: 12px;
		flex-wrap: wrap;
	}

	.release-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		padding: 8px 16px;
		border-radius: 8px;
		border: 1px solid var(--success);
		color: var(--success);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.release-btn:hover { background: rgba(34, 197, 94, 0.1); }

	.dispute-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		padding: 8px 16px;
		border-radius: 8px;
		border: 1px solid var(--destructive);
		color: var(--destructive);
		background: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.dispute-btn:hover { background: rgba(239, 68, 68, 0.1); }
	.dispute-btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.cancel-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		background: none;
		border: none;
		cursor: pointer;
		padding: 8px;
	}

	.dispute-form {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.dispute-form textarea {
		background: var(--input);
		border: 1px solid var(--border);
		border-radius: 8px;
		color: var(--foreground);
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		padding: 12px;
		resize: vertical;
		outline: none;
		width: 100%;
		box-sizing: border-box;
	}

	.dispute-form textarea:focus {
		border-color: var(--destructive);
	}

	.confirm-row {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
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
		padding: 8px 16px;
		border-radius: 8px;
		border: none;
		cursor: pointer;
		transition: all 150ms;
	}

	.success-btn {
		background: var(--success);
		color: var(--success-foreground);
	}

	.danger-btn {
		background: var(--destructive);
		color: white;
	}

	.confirm-no {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		background: none;
		border: none;
		cursor: pointer;
		padding: 8px;
	}

	.hmac-toggle {
		background: none;
		border: none;
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		color: var(--muted-foreground);
		cursor: pointer;
		padding: 0;
		text-align: left;
	}

	.hmac-details {
		background: var(--surface-2);
		border-radius: 8px;
		padding: 12px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.hmac-hash {
		font-size: 11px;
		color: var(--muted-foreground);
		word-break: break-all;
		margin: 0;
	}

	.hmac-note {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
		margin: 0;
	}

	/* Payment summary */
	.payment-summary {
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 20px;
		position: sticky;
		top: 72px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.summary-heading {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--foreground);
		margin: 0;
	}

	.summary-rows {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.summary-row {
		display: flex;
		justify-content: space-between;
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
	}

	.summary-row .mono {
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
	}

	.summary-divider {
		border-top: 1px solid var(--border);
		margin: 2px 0;
	}

	.summary-row.total {
		color: var(--foreground);
		font-weight: 500;
	}

	.total-val {
		color: var(--primary) !important;
		font-weight: 700;
	}

	.escrow-status {
		display: flex;
	}

	.escrow-chip {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 500;
		font-size: 12px;
		padding: 4px 10px;
		border-radius: 9999px;
	}

	.success-chip { background: rgba(34, 197, 94, 0.12); color: var(--success); }
	.danger-chip { background: rgba(239, 68, 68, 0.12); color: var(--destructive); }
	.warning-chip { background: rgba(245, 158, 11, 0.12); color: var(--warning); }

	.payment-hash-display {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.phd-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--muted-foreground);
	}

	.phd-value {
		font-size: 11px;
		color: var(--muted-foreground);
		word-break: break-all;
	}

	.skeleton {
		background: linear-gradient(90deg, #1a1a26 25%, #252535 50%, #1a1a26 75%);
		background-size: 200% 100%;
		animation: shimmer 1.8s infinite linear;
	}

	@media (max-width: 768px) {
		.content-grid { grid-template-columns: 1fr; }
		.payment-summary { position: static; }
		.job-header-inner { flex-direction: column; }
	}
</style>
