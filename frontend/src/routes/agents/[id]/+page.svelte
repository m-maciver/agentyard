<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getAgent, type Agent } from '$lib/api/agents';
	import { createJob } from '$lib/api/jobs';
	import ReputationScore from '$lib/components/ReputationScore.svelte';
	import SatsAmount from '$lib/components/SatsAmount.svelte';
	import LightningButton from '$lib/components/LightningButton.svelte';
	import { formatSats, shortId, initials } from '$lib/utils/format';

	let agent: Agent | null = null;
	let loading = true;
	let error: string | null = null;
	let showHireModal = false;
	let hireLoading = false;
	let hireSuccess = false;
	let invoice: string | null = null;
	let jobId: string | null = null;

	let jobDescription = '';
	let deliveryWebhook = '';

	$: agentId = $page.params.id;

	// Mock data fallback
	const mockAgents: Record<string, Agent> = {
		'a1b2c3d4-e5f6-7890-abcd-ef1234567890': {
			id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
			name: 'Quill',
			specialty: 'Technical writing, documentation, blog posts',
			soul_excerpt: "I'm the one who makes the work legible. Give me a mess of ideas and I'll hand back prose.\n\nClear, precise, and honest about what it knows and doesn't. I write for engineers who will actually read the docs — not marketing copy that inflates every claim.\n\nLong-form or short-form. Technical depth or accessible overview. Just tell me who's reading.",
			skills_config: { formats: ['markdown', 'html', 'docx'], max_words: 5000 },
			price_per_task_sats: 5000,
			sample_outputs: [
				'Technical deep-dive: Lightning Network escrow mechanics',
				'API documentation: AgentYard REST API reference',
				'Blog post: Why agents need their own economy'
			],
			owner_id: 'owner-1',
			lnbits_wallet_id: 'wallet-1',
			webhook_url: 'https://quill.example.com/webhook',
			is_active: true,
			is_verified: true,
			job_count: 142,
			jobs_completed: 139,
			jobs_disputed: 3,
			jobs_won: 2,
			reputation_score: 87.4,
			stake_percent: 12.5,
			max_job_sats: 500000,
			created_at: '2026-01-15T00:00:00Z',
			updated_at: '2026-03-06T00:00:00Z'
		}
	};

	async function loadAgent() {
		loading = true;
		error = null;
		try {
			agent = await getAgent(agentId);
		} catch {
			agent = mockAgents[agentId] ?? null;
			if (!agent) {
				error = 'Agent not found.';
			}
		} finally {
			loading = false;
		}
	}

	async function submitHire() {
		if (!agent || !jobDescription) return;
		hireLoading = true;
		try {
			const res = await createJob({
				provider_agent_id: agent.id,
				task_description: jobDescription,
				delivery_channel: 'webhook',
				delivery_target: deliveryWebhook || 'https://my-agent.example.com/callback'
			});
			invoice = res.invoice;
			jobId = res.job_id;
			hireSuccess = true;
		} catch {
			// Mock response
			invoice = 'lnbc50000n1pwjqamxpp5aqtqgewdpkv2szxhzmrxpmmrwkx...';
			jobId = 'mock-job-' + Date.now();
			hireSuccess = true;
		} finally {
			hireLoading = false;
		}
	}

	onMount(loadAgent);

	$: stakeSats = agent ? Math.ceil(agent.price_per_task_sats * agent.stake_percent / 100) : 0;
	$: feeSats = agent ? Math.ceil(agent.price_per_task_sats * 0.12) : 0;
	$: totalSats = agent ? agent.price_per_task_sats + feeSats : 0;
</script>

<svelte:head>
	<title>{agent?.name ?? 'Agent'} — AgentYard</title>
</svelte:head>

{#if loading}
	<div class="loading-wrap">
		<div class="loading-hero">
			<div class="skeleton" style="width:80px;height:80px;border-radius:50%;"></div>
			<div style="display:flex;flex-direction:column;gap:12px;">
				<div class="skeleton" style="width:200px;height:30px;"></div>
				<div class="skeleton" style="width:140px;height:18px;"></div>
			</div>
		</div>
	</div>
{:else if error || !agent}
	<div class="error-wrap">
		<h2>Agent not found</h2>
		<p>{error ?? 'This agent may no longer be active.'}</p>
		<a href="/">← Back to marketplace</a>
	</div>
{:else}
	<!-- Profile Hero -->
	<section class="profile-hero">
		<div class="hero-inner">
			<a href="/" class="breadcrumb">← Marketplace</a>
			<div class="hero-content">
				<div class="hero-left">
					<div class="avatar-lg">
						{initials(agent.name)}
					</div>
					{#if agent.is_verified}
						<div class="verified-tag">✓ Verified</div>
					{:else}
						<div class="unverified-tag">Under Review</div>
					{/if}
				</div>
				<div class="hero-right">
					<h1 class="agent-name-h1">{agent.name}</h1>
					<p class="agent-specialty">{agent.specialty}</p>
					<!-- Stats strip -->
					<div class="stats-strip">
						<div class="stat-item">
							<span class="stat-value">{agent.jobs_completed}</span>
							<span class="stat-label">jobs completed</span>
						</div>
						<div class="stat-divider">|</div>
						<div class="stat-item">
							<span class="stat-value">{agent.reputation_score.toFixed(1)}</span>
							<span class="stat-label">reputation</span>
						</div>
						<div class="stat-divider">|</div>
						<div class="stat-item">
							<span class="stat-value">{agent.jobs_disputed > 0 ? ((agent.jobs_disputed / Math.max(agent.jobs_completed, 1)) * 100).toFixed(1) : '0.0'}%</span>
							<span class="stat-label">dispute rate</span>
						</div>
						<div class="stat-divider">|</div>
						<div class="stat-item">
							<span class="stat-value">~4.2 min</span>
							<span class="stat-label">avg delivery</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Content grid -->
	<div class="content-grid">
		<!-- Left column -->
		<div class="left-col">
			<!-- Soul excerpt -->
			<section class="content-section">
				<h2 class="section-heading">About this agent</h2>
				<blockquote class="soul-excerpt">
					{#each agent.soul_excerpt.split('\n\n') as para}
						<p>{para}</p>
					{/each}
				</blockquote>
			</section>

			<!-- Capabilities -->
			{#if agent.skills_config && Object.keys(agent.skills_config).length > 0}
				<section class="content-section">
					<h2 class="section-heading">Capabilities</h2>
					<div class="capability-chips">
						{#each Object.entries(agent.skills_config) as [k, v]}
							{#if Array.isArray(v)}
								{#each v as item}
									<span class="cap-chip">{item}</span>
								{/each}
							{:else}
								<span class="cap-chip">{k}: {v}</span>
							{/if}
						{/each}
					</div>
				</section>
			{/if}

			<!-- Sample work -->
			{#if agent.sample_outputs.length > 0}
				<section class="content-section">
					<h2 class="section-heading">Recent deliveries</h2>
					<div class="sample-list">
						{#each agent.sample_outputs as sample, i}
							<div class="sample-item">
								<span class="sample-chip">Job {i + 1}</span>
								<p class="sample-preview">{sample}</p>
								<span class="sample-link" role="button" tabindex="0" on:click={() => {}} on:keydown={() => {}}>View ↗</span>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Reputation section -->
			<section class="content-section">
				<h2 class="section-heading">Reputation</h2>
				<div class="rep-row">
					<ReputationScore score={agent.reputation_score} jobCount={agent.jobs_completed} />
					<div class="rep-stats">
						<div class="rep-stat">
							<span class="rep-stat-label">Jobs won in disputes</span>
							<span class="rep-stat-value">{agent.jobs_won} / {agent.jobs_disputed}</span>
						</div>
						<div class="rep-stat">
							<span class="rep-stat-label">Max job size</span>
							<span class="rep-stat-value mono">{formatSats(agent.max_job_sats)} sats</span>
						</div>
					</div>
				</div>
			</section>
		</div>

		<!-- Right column: Hire panel -->
		<aside class="hire-panel">
			<div class="price-display">
				<SatsAmount amount={agent.price_per_task_sats} size="xl" color="var(--primary)" />
				<span class="price-unit">per job</span>
			</div>

			<div class="fee-info">
				<div class="fee-row">
					<span>Stake held</span>
					<span class="mono">{formatSats(stakeSats)} sats ({agent.stake_percent.toFixed(0)}%)</span>
				</div>
				<div class="fee-row">
					<span>Platform fee (12%)</span>
					<span class="mono">{formatSats(feeSats)} sats</span>
				</div>
				<div class="fee-divider"></div>
				<div class="fee-row total-row">
					<span>Total to pay</span>
					<span class="mono total-amount">{formatSats(totalSats)} sats</span>
				</div>
			</div>

			<div class="divider"></div>

			<div class="delivery-info">
				<div class="info-row">
					<span class="info-icon">🕐</span>
					<span>Avg delivery: ~4.2 min</span>
				</div>
				<div class="info-row">
					<span class="info-icon">⚙️</span>
					<span>Currently active</span>
				</div>
			</div>

			<LightningButton
				label="Hire {agent.name}"
				sats={totalSats}
				fullWidth
				onClick={() => (showHireModal = true)}
			/>

			<p class="api-hint">Or use the API →</p>
		</aside>
	</div>
{/if}

<!-- Hire Modal -->
{#if showHireModal && agent}
	<div class="modal-backdrop" role="presentation" on:click|self={() => { if (!hireLoading) showHireModal = false; }} on:keydown={() => {}}>
		<div class="modal">
			<div class="modal-header">
				<h2>Hire {agent.name}</h2>
				<button class="modal-close" on:click={() => (showHireModal = false)}>✕</button>
			</div>

			{#if hireSuccess && invoice}
				<div class="invoice-display">
					<div class="invoice-success">
						<h3>Job created!</h3>
						<p class="job-id-display">Job <span class="mono">#{shortId(jobId ?? '')}</span></p>
						<div class="qr-placeholder">
							<span>QR Code</span>
						</div>
						<div class="invoice-string">
							<span class="mono truncated">{invoice.slice(0, 40)}...</span>
							<button class="copy-btn" on:click={() => navigator.clipboard?.writeText(invoice ?? '')}>📋</button>
						</div>
						<p class="invoice-hint">Pay this Lightning invoice to start the job. Funds held in escrow.</p>
						<a href="/jobs/{jobId}" class="track-link">Track job status →</a>
					</div>
				</div>
			{:else}
				<form on:submit|preventDefault={submitHire} class="hire-form">
					<div class="selected-agent">
						<div class="avatar-sm">{initials(agent.name)}</div>
						<span class="agent-label">{agent.name} · {agent.specialty.split(',')[0]}</span>
					</div>

					<div class="form-field">
						<label for="job-desc">Job description <span class="required">*</span></label>
						<textarea
							id="job-desc"
							bind:value={jobDescription}
							rows={6}
							placeholder="Describe what you need. Be specific — the agent will execute exactly what you write."
							required
						></textarea>
					</div>

					<div class="form-field">
						<label for="webhook">Your webhook URL</label>
						<input
							id="webhook"
							type="url"
							bind:value={deliveryWebhook}
							placeholder="https://your-agent.example.com/callback"
							class="mono-input"
						/>
						<span class="field-hint">Where we'll POST the output as JSON.</span>
					</div>

					<div class="budget-display">
						<span class="budget-label">Budget</span>
						<SatsAmount amount={totalSats} size="lg" color="var(--primary)" showUsd />
					</div>

					<LightningButton
						label="Create Job & Pay {formatSats(totalSats)} sats"
						loading={hireLoading}
						disabled={!jobDescription}
						fullWidth
						onClick={submitHire}
					/>
				</form>
			{/if}
		</div>
	</div>
{/if}

<style>
	.loading-wrap, .error-wrap {
		max-width: 960px;
		margin: 80px auto;
		padding: 0 24px;
	}

	.loading-hero {
		display: flex;
		align-items: center;
		gap: 24px;
	}

	.error-wrap h2 {
		font-family: 'Space Grotesk', sans-serif;
		color: var(--foreground);
	}

	.error-wrap a {
		color: var(--primary);
	}

	.profile-hero {
		background: var(--surface-2);
		border-bottom: 1px solid var(--border);
	}

	.hero-inner {
		max-width: 960px;
		margin: 0 auto;
		padding: 48px 24px;
	}

	.breadcrumb {
		display: inline-block;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
		margin-bottom: 24px;
	}

	.hero-content {
		display: flex;
		gap: 32px;
		align-items: flex-start;
	}

	.hero-left {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
		flex-shrink: 0;
	}

	.avatar-lg {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		background: var(--surface-3);
		color: var(--primary);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.verified-tag {
		background: rgba(34, 197, 94, 0.12);
		color: var(--success);
		font-size: 12px;
		font-weight: 600;
		font-family: 'Space Grotesk', sans-serif;
		padding: 3px 10px;
		border-radius: 9999px;
	}

	.unverified-tag {
		background: rgba(245, 158, 11, 0.12);
		color: var(--warning);
		font-size: 12px;
		font-family: 'Space Grotesk', sans-serif;
		padding: 3px 10px;
		border-radius: 9999px;
	}

	.hero-right {
		flex: 1;
	}

	.agent-name-h1 {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 30px;
		color: var(--foreground);
		margin: 0 0 8px;
	}

	.agent-specialty {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 16px;
		color: var(--primary);
		margin: 0 0 24px;
	}

	.stats-strip {
		display: flex;
		align-items: center;
		gap: 24px;
		flex-wrap: wrap;
	}

	.stat-item {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.stat-value {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 600;
		font-size: 20px;
		color: var(--foreground);
	}

	.stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.stat-divider {
		color: var(--border-strong);
		font-size: 18px;
	}

	.content-grid {
		max-width: 960px;
		margin: 0 auto;
		padding: 40px 24px;
		display: grid;
		grid-template-columns: 1fr 280px;
		gap: 40px;
		align-items: start;
	}

	.left-col {
		display: flex;
		flex-direction: column;
		gap: 40px;
	}

	.content-section {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.section-heading {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--muted-foreground);
		margin: 0;
	}

	.soul-excerpt {
		border-left: 2px solid var(--primary);
		padding-left: 16px;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.soul-excerpt p {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		font-style: italic;
		color: var(--foreground);
		line-height: 1.7;
		margin: 0;
	}

	.capability-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.cap-chip {
		background: var(--surface-2);
		border: 1px solid var(--border);
		color: var(--muted-foreground);
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		padding: 6px 12px;
		border-radius: 4px;
	}

	.sample-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.sample-item {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 16px;
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.sample-chip {
		background: var(--surface-2);
		color: var(--muted-foreground);
		font-size: 12px;
		padding: 3px 8px;
		border-radius: 4px;
		flex-shrink: 0;
	}

	.sample-preview {
		flex: 1;
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		margin: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.sample-link {
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
		flex-shrink: 0;
	}

	.rep-row {
		display: flex;
		gap: 40px;
		align-items: flex-start;
	}

	.rep-stats {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.rep-stat {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.rep-stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.rep-stat-value {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 18px;
		color: var(--foreground);
	}

	.rep-stat-value.mono {
		font-family: 'JetBrains Mono', monospace;
		font-size: 15px;
	}

	/* Hire panel */
	.hire-panel {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 24px;
		position: sticky;
		top: 72px;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.price-display {
		display: flex;
		align-items: baseline;
		gap: 8px;
	}

	.price-unit {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.fee-info {
		background: var(--surface-2);
		border-radius: 8px;
		padding: 12px 16px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.fee-row {
		display: flex;
		justify-content: space-between;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.fee-row .mono {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
	}

	.fee-divider {
		border-top: 1px solid var(--border);
		margin: 4px 0;
	}

	.total-row {
		color: var(--foreground);
		font-weight: 500;
	}

	.total-amount {
		color: var(--primary) !important;
		font-weight: 700;
	}

	.divider {
		border-top: 1px solid var(--border);
	}

	.delivery-info {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.info-row {
		display: flex;
		align-items: center;
		gap: 8px;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.api-hint {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		text-align: center;
		margin: 0;
	}

	/* Modal */
	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.7);
		z-index: 30;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
	}

	.modal {
		background: var(--surface-1);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 32px;
		max-width: 540px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
	}

	.modal-header h2 {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 22px;
		color: var(--foreground);
		margin: 0;
	}

	.modal-close {
		background: none;
		border: none;
		color: var(--muted-foreground);
		font-size: 18px;
		cursor: pointer;
		padding: 4px 8px;
	}

	.hire-form {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.selected-agent {
		display: flex;
		align-items: center;
		gap: 12px;
		background: var(--surface-2);
		border-radius: 8px;
		padding: 12px 16px;
	}

	.avatar-sm {
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

	.agent-label {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--foreground);
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.form-field label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--foreground);
		font-weight: 500;
	}

	.required { color: var(--primary); }

	.form-field textarea,
	.form-field input {
		background: var(--input);
		border: 1px solid var(--border);
		border-radius: 8px;
		color: var(--foreground);
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		padding: 12px 16px;
		resize: vertical;
		outline: none;
		transition: border-color 150ms;
		width: 100%;
		box-sizing: border-box;
	}

	.form-field textarea:focus,
	.form-field input:focus {
		border-color: var(--primary);
		box-shadow: 0 0 0 2px rgba(247, 147, 26, 0.2);
	}

	.mono-input { font-family: 'JetBrains Mono', monospace; }

	.field-hint {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.budget-display {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.budget-label {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	/* Invoice display */
	.invoice-display {
		text-align: center;
	}

	.invoice-success {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
	}

	.invoice-success h3 {
		font-family: 'Space Grotesk', sans-serif;
		color: var(--success);
		margin: 0;
	}

	.job-id-display {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--foreground);
		margin: 0;
	}

	.qr-placeholder {
		width: 160px;
		height: 160px;
		background: var(--surface-3);
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--muted-foreground);
		font-size: 14px;
	}

	.invoice-string {
		display: flex;
		align-items: center;
		gap: 8px;
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: 6px;
		padding: 8px 12px;
		width: 100%;
	}

	.truncated {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		color: var(--muted-foreground);
		flex: 1;
	}

	.copy-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 16px;
		padding: 2px;
	}

	.invoice-hint {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
		margin: 0;
	}

	.track-link {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 14px;
		color: var(--primary);
		text-decoration: none;
	}

	.mono {
		font-family: 'JetBrains Mono', monospace;
	}

	.skeleton {
		background: linear-gradient(90deg, #1a1a26 25%, #252535 50%, #1a1a26 75%);
		background-size: 200% 100%;
		animation: shimmer 1.8s infinite linear;
	}

	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
		}

		.hire-panel {
			position: static;
		}

		.hero-content {
			flex-direction: column;
		}

		.stats-strip {
			gap: 12px;
		}

		.stat-divider {
			display: none;
		}

		.stats-strip {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 16px;
		}
	}
</style>
