<script lang="ts">
	import type { Agent } from '$lib/api/agents';
	import { formatSats, formatMonthYear, initials } from '$lib/utils/format';
	import ReputationScore from './ReputationScore.svelte';

	export let agent: Agent;
	export let loading: boolean = false;
</script>

{#if loading}
	<!-- Skeleton -->
	<div class="agent-card skeleton-card">
		<div class="card-header">
			<div class="skeleton avatar-skel"></div>
			<div class="name-rep">
				<div class="skeleton name-skel"></div>
				<div class="skeleton rep-skel"></div>
			</div>
		</div>
		<div class="skeleton specialty-skel"></div>
		<div class="desc-skels">
			<div class="skeleton desc-line-1"></div>
			<div class="skeleton desc-line-2"></div>
		</div>
		<div class="stats-skels">
			<div class="skeleton stat-skel"></div>
			<div class="skeleton stat-skel"></div>
			<div class="skeleton stat-skel"></div>
		</div>
		<div class="footer-skels">
			<div class="skeleton footer-skel-l"></div>
			<div class="skeleton footer-skel-r"></div>
		</div>
	</div>
{:else}
	<a href="/agents/{agent.id}" class="agent-card" tabindex="0">
		<!-- Header: avatar + name + rep -->
		<div class="card-header">
			<div class="avatar">
				{initials(agent.name)}
			</div>
			<div class="name-rep">
				<span class="agent-name">
					{agent.name}
					{#if agent.is_verified}
						<span class="verified-badge" title="Verified agent">✓</span>
					{/if}
				</span>
				<ReputationScore score={agent.reputation_score} jobCount={agent.jobs_completed} compact />
			</div>
		</div>

		<!-- Specialty chip -->
		<div class="specialty-chip">{agent.specialty.split(',')[0].trim()}</div>

		<!-- Description -->
		<p class="description">{agent.soul_excerpt}</p>

		<!-- Stats row -->
		<div class="stats-row">
			<span class="stat">{agent.jobs_completed} jobs</span>
			<span class="divider">·</span>
			<span class="stat">Since {formatMonthYear(agent.created_at)}</span>
			<span class="divider">·</span>
			<span class="stat">from {formatSats(agent.price_per_task_sats)} sats</span>
		</div>

		<!-- Footer: stake + link -->
		<div class="card-footer">
			<span class="stake-indicator">
				🔒 {formatSats(Math.ceil(agent.price_per_task_sats * agent.stake_percent / 100))} sats staked
			</span>
			<span class="view-link">View Agent →</span>
		</div>
	</a>
{/if}

<style>
	.agent-card {
		display: flex;
		flex-direction: column;
		gap: 12px;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 24px;
		text-decoration: none;
		color: inherit;
		cursor: pointer;
		transition: border-color 150ms ease-out, transform 150ms ease-out, box-shadow 150ms ease-out;
	}

	.agent-card:hover {
		border-color: var(--primary);
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
	}

	.agent-card:focus-visible {
		outline: 2px solid var(--primary);
		outline-offset: 2px;
	}

	.agent-card:active {
		transform: translateY(0) scale(0.99);
		box-shadow: none;
	}

	.card-header {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.avatar {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: var(--surface-3);
		color: var(--primary);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.name-rep {
		display: flex;
		flex-direction: column;
		gap: 2px;
		flex: 1;
	}

	.agent-name {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--foreground);
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.verified-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 16px;
		height: 16px;
		border-radius: 50%;
		background: var(--primary);
		color: var(--primary-foreground);
		font-size: 10px;
		font-weight: 700;
	}

	.specialty-chip {
		display: inline-flex;
		align-self: flex-start;
		background: var(--muted);
		color: var(--muted-foreground);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 12px;
		padding: 4px 8px;
		border-radius: 4px;
	}

	.description {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		margin: 0;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.stats-row {
		display: flex;
		align-items: center;
		gap: 6px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		color: var(--muted-foreground);
		flex-wrap: wrap;
	}

	.divider {
		opacity: 0.4;
	}

	.card-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: 4px;
	}

	.stake-indicator {
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.view-link {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 13px;
		color: var(--primary);
	}

	/* Skeleton */
	.skeleton-card {
		cursor: default;
	}
	.skeleton-card:hover {
		border-color: var(--border);
	}
	.skeleton { border-radius: 4px; }
	.avatar-skel { width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; }
	.name-skel { width: 120px; height: 16px; }
	.rep-skel { width: 56px; height: 14px; margin-top: 4px; }
	.specialty-skel { width: 72px; height: 20px; }
	.desc-skels { display: flex; flex-direction: column; gap: 6px; }
	.desc-line-1 { width: 100%; height: 14px; }
	.desc-line-2 { width: 75%; height: 14px; }
	.stats-skels { display: flex; gap: 8px; }
	.stat-skel { width: 60px; height: 12px; }
	.footer-skels { display: flex; justify-content: space-between; }
	.footer-skel-l, .footer-skel-r { width: 80px; height: 14px; }
</style>
