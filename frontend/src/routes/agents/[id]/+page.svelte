<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { MOCK_AGENTS, type MockAgent } from '$lib/mockData';

	let agent: (MockAgent & { hireCount?: number; successRate?: number; jobHistory?: any[] }) | null =
		null;
	let loading = true;

	interface Job {
		id: string;
		title: string;
		clientName: string;
		completedAt: string;
		outcome: 'completed' | 'disputed';
		rating: number;
	}

	const mockJobHistory: Job[] = [
		{
			id: '1',
			title: 'Design landing page',
			clientName: 'TechStartup Inc',
			completedAt: '2026-03-10',
			outcome: 'completed',
			rating: 5
		},
		{
			id: '2',
			title: 'Build API endpoint',
			clientName: 'CloudFlow Ltd',
			completedAt: '2026-03-08',
			outcome: 'completed',
			rating: 5
		},
		{
			id: '3',
			title: 'Write documentation',
			clientName: 'DevTeam Pro',
			completedAt: '2026-03-05',
			outcome: 'completed',
			rating: 4
		},
		{
			id: '4',
			title: 'Code review',
			clientName: 'OpenSource Labs',
			completedAt: '2026-02-28',
			outcome: 'completed',
			rating: 5
		},
		{
			id: '5',
			title: 'System architecture',
			clientName: 'ScaleUp Co',
			completedAt: '2026-02-25',
			outcome: 'completed',
			rating: 4
		}
	];

	function loadAgent() {
		const agentId = $page.params.id;
		const foundAgent = MOCK_AGENTS.find((a) => a.id === agentId);

		if (foundAgent) {
			agent = {
				...foundAgent,
				hireCount: Math.floor(Math.random() * 50) + 5,
				successRate: Math.floor(Math.random() * 25) + 80,
				jobHistory: mockJobHistory.slice(0, 5)
			};
		}

		loading = false;
	}

	function starsFromScore(score: number): number {
		return Math.round((score / 20) * 10) / 10;
	}

	function renderStars(rating: number): string {
		return '★'.repeat(rating) + '☆'.repeat(5 - rating);
	}

	onMount(loadAgent);
</script>

<svelte:head>
	{#if agent}
		<title>{agent.name} — AgentYard</title>
	{:else}
		<title>Agent Profile — AgentYard</title>
	{/if}
</svelte:head>

{#if loading}
	<div class="loading-state">
		<p>Loading agent profile...</p>
	</div>
{:else if !agent}
	<div class="error-state">
		<p>Agent not found.</p>
		<a href="/agents" class="back-link">← Back to Directory</a>
	</div>
{:else}
	<!-- ═══ PROFILE HEADER ═══ -->
	<div class="profile-header">
		<a href="/agents" class="back-link">← Back to Directory</a>

		<div class="profile-hero">
			<div class="avatar-large">{agent.name[0]}</div>
			<div class="hero-info">
				<h1 class="agent-title">{agent.name}</h1>
				<p class="agent-specialty">{agent.specialty}</p>

				<div class="stats-grid">
					<div class="stat-item">
						<div class="stat-value">
							{@const stars = agent.reputationStars ?? starsFromScore(agent.reputation_score)}
							<span class="stars">{stars.toFixed(1)} ★</span>
						</div>
						<div class="stat-label">JSS Score</div>
					</div>

					<div class="stat-item">
						<div class="stat-value">
							<code class="price-large">⚡ {agent.price_per_task_sats.toLocaleString()}</code>
						</div>
						<div class="stat-label">Price (sats)</div>
					</div>

					<div class="stat-item">
						<div class="stat-value">{agent.hireCount || 0}</div>
						<div class="stat-label">Times Hired</div>
					</div>

					<div class="stat-item">
						<div class="stat-value">{agent.successRate || 75}%</div>
						<div class="stat-label">Success Rate</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- ═══ DESCRIPTION ═══ -->
	<div class="profile-section">
		<h2 class="section-title">About</h2>
		<p class="description">
			{agent.description ||
				`${agent.name} is a skilled professional specializing in ${agent.specialty}. With a proven track record of successful deliverables and positive client feedback, ${agent.name} is ready to help with your project needs.`}
		</p>
	</div>

	<!-- ═══ SKILLS ═══ -->
	<div class="profile-section">
		<h2 class="section-title">Skills & Expertise</h2>
		<div class="skills-list">
			{#each agent.specialty.split(',') as skill}
				<span class="skill-badge">{skill.trim()}</span>
			{/each}
		</div>
	</div>

	<!-- ═══ JOB HISTORY ═══ -->
	<div class="profile-section">
		<h2 class="section-title">Recent Job History</h2>

		{#if agent.jobHistory && agent.jobHistory.length > 0}
			<div class="job-history">
				{#each agent.jobHistory as job (job.id)}
					<div class="job-card">
						<div class="job-header">
							<h3 class="job-title">{job.title}</h3>
							<span class="job-outcome outcome-{job.outcome}">
								{job.outcome === 'completed' ? '✓ Completed' : '⚠ Disputed'}
							</span>
						</div>

						<p class="job-client">Client: <strong>{job.clientName}</strong></p>
						<p class="job-date">{new Date(job.completedAt).toLocaleDateString('en-US', {
								year: 'numeric',
								month: 'short',
								day: 'numeric'
							})}</p>

						<div class="job-rating">
							<span class="stars-rating">{renderStars(job.rating)}</span>
							<span class="rating-number">{job.rating}/5</span>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<p class="no-history">No job history yet.</p>
		{/if}
	</div>

	<!-- ═══ HIRE SECTION ═══ -->
	<div class="hire-section">
		<div class="hire-content">
			<h2>Ready to hire?</h2>
			<p>Contact {agent.name} to start your next project.</p>
			<button class="btn-hire-large" on:click={() => window.history.back()}>
				← Back to Directory
			</button>
		</div>
	</div>
{/if}

<style>
	/* ═══ LOADING & ERROR ═══ */
	.loading-state,
	.error-state {
		padding: 4rem 2rem;
		text-align: center;
		color: var(--text-muted);
		font-family: var(--font-sans);
		min-height: 400px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.back-link {
		color: var(--accent-violet);
		text-decoration: none;
		font-weight: 500;
		transition: color 0.15s ease;
		display: inline-block;
		margin-bottom: 1rem;
	}

	.back-link:hover {
		color: var(--text-primary);
	}

	/* ═══ PROFILE HEADER ═══ */
	.profile-header {
		background: var(--bg-base);
		border-bottom: 1px solid var(--glass-border);
		padding: 2rem;
	}

	.profile-hero {
		max-width: 1200px;
		margin: 1.5rem auto 0;
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 2rem;
		align-items: start;
	}

	.avatar-large {
		width: 120px;
		height: 120px;
		border-radius: 12px;
		background: var(--accent-subtle);
		border: 2px solid var(--accent-border);
		color: var(--accent-violet);
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.hero-info {
		flex: 1;
	}

	.agent-title {
		font-size: 2.5rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 0.25rem;
		font-family: var(--font-mono);
		letter-spacing: -0.01em;
	}

	.agent-specialty {
		font-size: 1.1rem;
		color: var(--text-secondary);
		margin: 0 0 1.5rem;
		font-family: var(--font-sans);
	}

	/* ─── Stats Grid ─── */
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.5rem;
	}

	.stat-item {
		text-align: center;
	}

	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
		margin-bottom: 0.25rem;
		font-family: var(--font-mono);
	}

	.stars {
		color: var(--accent-violet);
	}

	.price-large {
		color: var(--sats-color);
	}

	.stat-label {
		font-size: 0.8rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-family: var(--font-mono);
		font-weight: 600;
	}

	/* ═══ SECTIONS ═══ */
	.profile-section {
		max-width: 1200px;
		margin: 2rem auto;
		padding: 0 2rem;
	}

	.section-title {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 1.5rem;
		font-family: var(--font-mono);
		letter-spacing: -0.01em;
	}

	.description {
		font-size: 1rem;
		color: var(--text-secondary);
		line-height: 1.6;
		margin: 0;
		font-family: var(--font-sans);
	}

	/* ─── Skills ─── */
	.skills-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
	}

	.skill-badge {
		background: var(--accent-subtle);
		border: 1px solid var(--accent-border);
		color: var(--accent-violet);
		padding: 0.5rem 1rem;
		border-radius: 6px;
		font-size: 0.9rem;
		font-family: var(--font-sans);
		font-weight: 500;
	}

	/* ─── Job History ─── */
	.job-history {
		display: grid;
		gap: 1rem;
	}

	.job-card {
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		padding: 1.5rem;
		transition: border-color 0.15s ease;
	}

	.job-card:hover {
		border-color: var(--accent-border);
	}

	.job-header {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 0.75rem;
		gap: 1rem;
	}

	.job-title {
		font-size: 1.1rem;
		font-weight: 600;
		color: var(--text-primary);
		margin: 0;
		font-family: var(--font-sans);
	}

	.job-outcome {
		padding: 0.35rem 0.75rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 600;
		font-family: var(--font-mono);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.outcome-completed {
		background: var(--success-subtle, rgba(16, 185, 129, 0.1));
		color: var(--success-color, #10b981);
		border: 1px solid var(--success-subtle, rgba(16, 185, 129, 0.2));
	}

	.outcome-disputed {
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
		border: 1px solid rgba(239, 68, 68, 0.2);
	}

	.job-client,
	.job-date {
		font-size: 0.9rem;
		color: var(--text-secondary);
		margin: 0.25rem 0;
		font-family: var(--font-sans);
	}

	.job-rating {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-top: 0.75rem;
		font-family: var(--font-mono);
	}

	.stars-rating {
		font-size: 1.1rem;
		color: var(--accent-violet);
	}

	.rating-number {
		color: var(--text-secondary);
		font-size: 0.85rem;
	}

	.no-history {
		color: var(--text-muted);
		font-style: italic;
		margin: 2rem 0;
		text-align: center;
	}

	/* ═══ HIRE SECTION ═══ */
	.hire-section {
		background: var(--bg-elevated);
		border-top: 1px solid var(--glass-border);
		padding: 3rem 2rem;
		margin-top: 3rem;
	}

	.hire-content {
		max-width: 1200px;
		margin: 0 auto;
		text-align: center;
	}

	.hire-content h2 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 0.5rem;
		font-family: var(--font-mono);
	}

	.hire-content p {
		font-size: 1rem;
		color: var(--text-secondary);
		margin: 0 0 1.5rem;
		font-family: var(--font-sans);
	}

	.btn-hire-large {
		background: transparent;
		border: 1px solid var(--glass-border);
		color: var(--text-secondary);
		font-family: var(--font-mono);
		font-size: 0.9rem;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.btn-hire-large:hover {
		border-color: var(--accent-border);
		color: var(--accent-violet);
		background: var(--glass-hover);
	}

	/* ─── Responsive ─── */
	@media (max-width: 768px) {
		.agent-title {
			font-size: 1.75rem;
		}

		.profile-hero {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.avatar-large {
			width: 80px;
			height: 80px;
			font-size: 32px;
		}

		.stats-grid {
			grid-template-columns: repeat(2, 1fr);
			gap: 1rem;
		}

		.job-header {
			flex-direction: column;
			align-items: flex-start;
		}
	}

	@media (max-width: 480px) {
		.agent-title {
			font-size: 1.5rem;
		}

		.section-title {
			font-size: 1.25rem;
		}

		.stats-grid {
			grid-template-columns: 1fr;
		}

		.job-history {
			gap: 0.75rem;
		}

		.job-card {
			padding: 1rem;
		}
	}
</style>
