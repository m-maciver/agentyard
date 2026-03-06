<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getAgent, type Agent } from '$lib/api/agents';
	import { MOCK_AGENTS, type MockAgent } from '$lib/mockData';
	import { isLoggedIn } from '$lib/stores/auth';
	import { initials } from '$lib/utils/format';

	let agent: MockAgent | null = null;
	let loading = true;
	let error: string | null = null;

	$: agentId = $page.params.id;

	async function loadAgent() {
		loading = true;
		error = null;
		try {
			const result = await getAgent(agentId);
			agent = result as MockAgent;
		} catch {
			const found = MOCK_AGENTS.find((a) => a.id === agentId) ?? null;
			if (found) {
				agent = found;
			} else {
				error = 'Agent not found';
			}
		} finally {
			loading = false;
		}
	}

	$: reputationStars = agent ? (agent.reputationStars ?? parseFloat((agent.reputation_score / 20).toFixed(1))) : 0;

	function renderStarsFull(score: number): { full: number; empty: number } {
		return { full: Math.round(score), empty: 5 - Math.round(score) };
	}

	onMount(loadAgent);
</script>

<svelte:head>
	<title>{agent?.name ?? 'Agent'} — AgentYard</title>
</svelte:head>

{#if loading}
	<div class="loading-wrap">
		<div class="loading-content">
			<div class="skeleton" style="width:80px;height:80px;border-radius:16px;"></div>
			<div>
				<div class="skeleton" style="width:200px;height:28px;"></div>
				<div class="skeleton" style="width:140px;height:16px;margin-top:10px;"></div>
			</div>
		</div>
	</div>
{:else if error || !agent}
	<div class="error-wrap">
		<h2>Agent not found</h2>
		<p>{error ?? 'This agent may no longer be active.'}</p>
		<a href="/" class="btn-ghost">← Back to marketplace</a>
	</div>
{:else}
	<!-- Hero -->
	<section class="agent-hero">
		<div class="hero-bg"></div>
		<div class="hero-inner">
			<a href="/" class="breadcrumb">← Marketplace</a>
			<div class="hero-content">
				<div class="agent-avatar-lg">
					{agent.name[0]}
				</div>
				<div class="hero-info">
					<div class="name-row">
						<h1 class="agent-name">{agent.name}</h1>
						{#if agent.is_verified}
							<span class="verified-tag">✓ Verified</span>
						{/if}
						{#if agent.githubUsername}
							<span class="github-handle">{agent.githubUsername}</span>
						{/if}
					</div>

					{#if agent.tags && agent.tags.length > 0}
						<div class="tag-row">
							{#each agent.tags as tag}
								<span class="tag-pill">{tag}</span>
							{/each}
						</div>
					{/if}

					<div class="hero-stats">
						<div class="hero-stat">
							<span class="stat-val font-mono">{agent.jobs_completed}</span>
							<span class="stat-lbl">jobs</span>
						</div>
						<div class="stat-sep"></div>
						<div class="hero-stat">
							<span class="stat-val font-mono">{reputationStars.toFixed(1)}</span>
							<span class="stat-lbl">★ rating</span>
						</div>
						<div class="stat-sep"></div>
						<div class="hero-stat">
							<span class="stat-val font-mono">
								{agent.jobs_disputed > 0 ? ((agent.jobs_won / agent.jobs_disputed) * 100).toFixed(0) : '100'}%
							</span>
							<span class="stat-lbl">dispute win</span>
						</div>
						<div class="stat-sep"></div>
						<div class="hero-stat">
							<span class="stat-val font-mono">~4.2m</span>
							<span class="stat-lbl">avg delivery</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Content -->
	<div class="content-wrap">
		<div class="content-grid">
			<!-- Left (2/3) -->
			<div class="left-col">
				<!-- About -->
				<section class="content-section glass-card">
					<h2 class="section-title">About this agent</h2>
					<blockquote class="soul-block">
						{#each agent.soul_excerpt.split('\n\n') as para}
							<p>{para}</p>
						{/each}
					</blockquote>
				</section>

				<!-- Capabilities -->
				{#if agent.skills_config && Object.keys(agent.skills_config).length > 0}
					<section class="content-section glass-card">
						<h2 class="section-title">Capabilities</h2>
						<div class="cap-chips">
							{#each Object.entries(agent.skills_config) as [, v]}
								{#if Array.isArray(v)}
									{#each v as item}
										<span class="cap-chip">{item}</span>
									{/each}
								{/if}
							{/each}
						</div>
					</section>
				{/if}

				<!-- Sample work -->
				{#if agent.sample_outputs.length > 0}
					<section class="content-section glass-card">
						<h2 class="section-title">Example tasks</h2>
						<div class="sample-list">
							{#each agent.sample_outputs as sample, i}
								<div class="sample-item">
									<span class="sample-num font-mono">0{i + 1}</span>
									<p class="sample-text">{sample}</p>
								</div>
							{/each}
						</div>
					</section>
				{/if}

				<!-- Recent jobs -->
				<section class="content-section glass-card">
					<h2 class="section-title">Recent job history</h2>
					<div class="job-history">
						{#each Array(5) as _, i}
							<div class="job-item">
								<div class="job-item-left">
									<div class="job-avatar">A</div>
									<div>
										<span class="job-client">Anonymous client</span>
										<span class="job-task">Completed task successfully · {i + 1}d ago</span>
									</div>
								</div>
								<span class="job-result success">✓ Completed</span>
							</div>
						{/each}
					</div>
				</section>
			</div>

			<!-- Right (1/3) — sticky hire card -->
			<aside class="hire-panel">
				<div class="hire-panel-inner glass-card">
					<div class="price-row">
						<span class="price font-mono">⚡ {agent.price_per_task_sats.toLocaleString()}</span>
						<span class="price-unit">sats / job</span>
					</div>

					<div class="rating-row">
						<div class="stars">
							{#each Array(5) as _, i}
								<span class="star" class:filled={i < Math.round(reputationStars)}>★</span>
							{/each}
						</div>
						<span class="rating-text">{reputationStars.toFixed(1)} / 5.0 · {agent.jobs_completed} jobs</span>
					</div>

					<div class="panel-stats">
						<div class="panel-stat">
							<span class="panel-stat-label">Total jobs</span>
							<span class="panel-stat-value font-mono">{agent.jobs_completed}</span>
						</div>
						<div class="panel-stat">
							<span class="panel-stat-label">Avg delivery</span>
							<span class="panel-stat-value font-mono">~4.2 min</span>
						</div>
						<div class="panel-stat">
							<span class="panel-stat-label">Max job size</span>
							<span class="panel-stat-value font-mono">{(agent.max_job_sats / 1000).toFixed(0)}k sats</span>
						</div>
					</div>

					<div class="panel-divider"></div>

					{#if $isLoggedIn}
						<button class="hire-cta-btn" on:click={() => alert('Hire flow coming — backend in progress!')}>
							⚡ Hire {agent.name}
						</button>
					{:else}
						<a href="/auth/github" class="hire-cta-btn hire-cta-github">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
								<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
							</svg>
							Sign in with GitHub to hire
						</a>
					{/if}

					<p class="panel-hint">Payment via Lightning Network · Instant settlement · Funds held in escrow until delivery</p>
				</div>
			</aside>
		</div>
	</div>
{/if}

<style>
	.loading-wrap, .error-wrap {
		max-width: 960px;
		margin: 80px auto;
		padding: 0 24px;
	}

	.loading-content {
		display: flex;
		align-items: center;
		gap: 24px;
	}

	.error-wrap h2 {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 28px;
		color: var(--text-primary);
		margin: 0 0 12px;
	}

	.error-wrap p {
		color: var(--text-secondary);
		margin: 0 0 24px;
	}

	/* Hero */
	.agent-hero {
		position: relative;
		overflow: hidden;
		background: var(--bg-base);
		border-bottom: 1px solid var(--glass-border);
		padding: 60px 24px;
	}

	.hero-inner {
		max-width: 1100px;
		margin: 0 auto;
		position: relative;
		z-index: 1;
	}

	.breadcrumb {
		display: inline-block;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--accent-primary);
		text-decoration: none;
		margin-bottom: 28px;
		transition: opacity 0.15s;
	}

	.breadcrumb:hover { opacity: 0.8; }

	.hero-content {
		display: flex;
		gap: 28px;
		align-items: flex-start;
	}

	.agent-avatar-lg {
		width: 80px;
		height: 80px;
		border-radius: 20px;
		background: var(--accent-subtle);
		border: 1px solid var(--accent-glow);
		color: var(--accent-primary);
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 36px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.hero-info {
		flex: 1;
	}

	.name-row {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
		margin-bottom: 12px;
	}

	.agent-name {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 32px;
		color: var(--text-primary);
		margin: 0;
		letter-spacing: -0.01em;
	}

	.verified-tag {
		background: rgba(34, 197, 94, 0.12);
		color: #22c55e;
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		font-weight: 600;
		padding: 4px 12px;
		border-radius: 9999px;
	}

	.github-handle {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-muted);
	}

	.tag-row {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 20px;
	}

	.tag-pill {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		padding: 4px 12px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 9999px;
		color: var(--text-secondary);
	}

	.hero-stats {
		display: flex;
		align-items: center;
		gap: 24px;
		flex-wrap: wrap;
	}

	.hero-stat {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.stat-val {
		font-size: 20px;
		font-weight: 600;
		color: var(--text-primary);
	}

	.stat-lbl {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.stat-sep {
		width: 1px;
		height: 30px;
		background: var(--glass-border);
	}

	/* Content */
	.content-wrap {
		max-width: 1100px;
		margin: 0 auto;
		padding: 48px 24px 80px;
	}

	.content-grid {
		display: grid;
		grid-template-columns: 1fr 300px;
		gap: 32px;
		align-items: start;
	}

	.left-col {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.content-section {
		padding: 28px;
	}

	.section-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 14px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		margin: 0 0 20px;
	}

	.soul-block {
		border-left: 2px solid var(--accent-primary);
		padding-left: 16px;
		margin: 0;
	}

	.soul-block p {
		font-family: 'Inter', sans-serif;
		font-size: 15px;
		color: var(--text-primary);
		line-height: 1.7;
		margin: 0 0 12px;
	}

	.soul-block p:last-child { margin-bottom: 0; }

	.cap-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.cap-chip {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		padding: 5px 12px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 6px;
		color: var(--text-secondary);
	}

	.sample-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.sample-item {
		display: flex;
		align-items: center;
		gap: 14px;
		padding: 12px 16px;
		background: var(--bg-elevated);
		border-radius: 10px;
	}

	.sample-num {
		font-size: 11px;
		color: var(--accent-primary);
		font-weight: 500;
		flex-shrink: 0;
	}

	.sample-text {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		margin: 0;
	}

	/* Job history */
	.job-history {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.job-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--glass-border);
	}

	.job-item:last-child { border-bottom: none; }

	.job-item-left {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.job-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--bg-elevated);
		color: var(--text-muted);
		font-family: 'DM Sans', sans-serif;
		font-size: 12px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.job-client {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-primary);
		font-weight: 500;
	}

	.job-task {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		margin-top: 1px;
	}

	.job-result {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		padding: 3px 10px;
		border-radius: 9999px;
		font-weight: 500;
		flex-shrink: 0;
	}

	.job-result.success {
		background: rgba(34, 197, 94, 0.1);
		color: #22c55e;
	}

	/* Hire panel */
	.hire-panel {
		position: sticky;
		top: 80px;
	}

	.hire-panel-inner {
		padding: 28px;
	}

	.price-row {
		display: flex;
		align-items: baseline;
		gap: 8px;
		margin-bottom: 16px;
	}

	.price {
		font-size: 24px;
		font-weight: 600;
		color: var(--sats-color);
	}

	.price-unit {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-muted);
	}

	.rating-row {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 20px;
	}

	.stars {
		display: flex;
		gap: 2px;
	}

	.star {
		font-size: 14px;
		color: var(--text-muted);
	}

	.star.filled {
		color: var(--sats-color);
	}

	.rating-text {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-secondary);
	}

	.panel-stats {
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-bottom: 20px;
	}

	.panel-stat {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.panel-stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-muted);
	}

	.panel-stat-value {
		font-size: 14px;
		color: var(--text-primary);
		font-weight: 500;
	}

	.panel-divider {
		height: 1px;
		background: var(--glass-border);
		margin-bottom: 20px;
	}

	.hire-cta-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		width: 100%;
		background: var(--accent-primary);
		color: var(--primary-foreground);
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 15px;
		padding: 14px;
		border: none;
		border-radius: 12px;
		cursor: pointer;
		text-decoration: none;
		transition: opacity 0.15s ease, transform 0.1s ease;
		margin-bottom: 12px;
	}

	.hire-cta-btn:hover {
		opacity: 0.9;
		transform: translateY(-1px);
	}

	.hire-cta-github {
		background: #24292e;
	}

	:root.light .hire-cta-github {
		background: #1a1a2e;
	}

	.panel-hint {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		text-align: center;
		margin: 0;
		line-height: 1.5;
	}

	/* Responsive */
	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
		}
		.hire-panel {
			position: static;
			order: -1;
		}
		.hero-content {
			flex-direction: column;
		}
		.hero-stats {
			gap: 16px;
		}
		.stat-sep { display: none; }
		.hero-stats {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 16px;
		}
	}
</style>
