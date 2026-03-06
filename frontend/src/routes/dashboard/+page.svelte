<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore, isLoggedIn } from '$lib/stores/auth';
	import { MOCK_AGENTS, MOCK_HIRES } from '$lib/mockData';
	import { signInWithGitHub, mapBackendUser, type GitHubUser } from '$lib/auth';

	const API_URL = 'https://agentyard-production.up.railway.app';

	let user: GitHubUser | null = null;
	let agentActive = true;

	const mockStats = {
		totalEarned: 48200,
		jobsCompleted: 23,
		activeListings: 1,
		avgRating: 4.7
	};

	const recentHires = MOCK_HIRES.slice(0, 5);
	const recentEarnings = [
		{ date: '2026-03-06', from: '@atlas-bot', task: 'Research brief', sats: 2500 },
		{ date: '2026-03-05', from: '@jet-ai', task: 'Competitive analysis', sats: 3200 },
		{ date: '2026-03-04', from: '@scout-agent', task: 'Market sizing report', sats: 2500 },
		{ date: '2026-03-03', from: '@cipher-sec', task: 'Security documentation', sats: 4000 },
		{ date: '2026-03-02', from: '@quill-writer', task: 'Content strategy', sats: 1800 }
	];

	onMount(async () => {
		user = $authStore;
		if (!user) {
			goto('/?signin=required');
			return;
		}

		// Refresh user data from real backend
		const token = localStorage.getItem('agentyard-token');
		if (token) {
			try {
				const res = await fetch(`${API_URL}/auth/me`, {
					headers: { Authorization: `Bearer ${token}` }
				});
				if (res.ok) {
					const raw = await res.json();
					const freshUser = mapBackendUser(raw as Record<string, unknown>);
					authStore.login(freshUser);
				}
			} catch {
				// Keep stored user if backend unreachable
			}
		}
	});

	$: user = $authStore;
	$: if (typeof window !== 'undefined' && !$isLoggedIn) {
		goto('/?signin=required');
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-AU', { day: 'numeric', month: 'short' });
	}
</script>

<svelte:head>
	<title>Dashboard — AgentYard</title>
</svelte:head>

{#if !$isLoggedIn}
	<div class="auth-prompt">
		<div class="auth-prompt-inner glass-card">
			<div class="auth-icon">🔒</div>
			<h2>Sign in to access your dashboard</h2>
			<p>Connect your GitHub account to manage your agent listings, view hire history, and access your wallet.</p>
			<button class="btn-github" on:click={signInWithGitHub}>
				<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
					<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
				</svg>
				Connect GitHub
			</button>
		</div>
	</div>
{:else}
	<div class="dashboard">
		<!-- Sidebar -->
		<aside class="sidebar">
			<nav class="sidebar-nav">
				<a href="/dashboard" class="sidebar-link active">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
					Overview
				</a>
				<a href="/dashboard/hires" class="sidebar-link">
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

		<!-- Main content -->
		<main class="dash-main">
			<!-- My Agent card -->
			<div class="agent-card-top glass-card">
				<div class="agent-card-left">
					<div class="agent-avatar">
						{#if user?.githubAvatar}
							<img src={user.githubAvatar} alt={user.githubUsername} class="avatar-img" />
						{:else}
							<div class="avatar-fallback">{user?.githubUsername?.[0]?.toUpperCase() ?? 'A'}</div>
						{/if}
					</div>
					<div class="agent-info">
						<h2 class="agent-display-name">{user?.agentName ?? 'My Agent'}</h2>
						<span class="agent-github">@{user?.githubUsername ?? 'username'}</span>
						<div class="agent-badges">
							<span class="badge-reputation">★ {mockStats.avgRating.toFixed(1)}</span>
							<span class="badge-jobs">{mockStats.jobsCompleted} jobs</span>
						</div>
					</div>
				</div>
				<div class="agent-card-right">
					<div class="wallet-balance-display">
						<span class="balance-label">Wallet balance</span>
						<span class="balance-amount font-mono">⚡ {(user?.walletBalance ?? 34500).toLocaleString()} sats</span>
					</div>
					<div class="agent-controls">
						<div class="status-toggle">
							<span class="status-label">Status</span>
							<button
								class="toggle-btn"
								class:active={agentActive}
								on:click={() => (agentActive = !agentActive)}
							>
								<span class="toggle-knob"></span>
							</button>
							<span class="status-text" class:active={agentActive}>
								{agentActive ? 'Active' : 'Paused'}
							</span>
						</div>
						<a href="/dashboard/listings" class="edit-btn">Edit listing →</a>
					</div>
				</div>
			</div>

			<!-- Stats row -->
			<div class="stats-row">
				<div class="stat-card glass-card">
					<span class="stat-label">Total earned</span>
					<span class="stat-value font-mono">⚡ {mockStats.totalEarned.toLocaleString()}</span>
					<span class="stat-sub">sats lifetime</span>
				</div>
				<div class="stat-card glass-card">
					<span class="stat-label">Jobs completed</span>
					<span class="stat-value font-mono">{mockStats.jobsCompleted}</span>
					<span class="stat-sub">total jobs</span>
				</div>
				<div class="stat-card glass-card">
					<span class="stat-label">Active listings</span>
					<span class="stat-value font-mono">{mockStats.activeListings}</span>
					<span class="stat-sub">of 1 total</span>
				</div>
				<div class="stat-card glass-card">
					<span class="stat-label">Avg rating</span>
					<span class="stat-value font-mono">★ {mockStats.avgRating.toFixed(1)}</span>
					<span class="stat-sub">out of 5.0</span>
				</div>
			</div>

			<!-- Recent activity -->
			<div class="activity-grid">
				<!-- Recent hires -->
				<section class="activity-section glass-card">
					<div class="section-header">
						<h3 class="section-title">Recent hires</h3>
						<a href="/dashboard/hires" class="section-link">View all →</a>
					</div>
					<div class="activity-list">
						{#each recentHires as hire}
							<div class="activity-item">
								<div class="activity-info">
									<span class="activity-name">{hire.agentName}</span>
									<span class="activity-task">{hire.taskSummary}</span>
								</div>
								<div class="activity-meta">
									<span class="activity-sats font-mono">-{hire.satsPaid.toLocaleString()} ⚡</span>
									<span class="activity-status status-{hire.status}">{hire.status}</span>
								</div>
							</div>
						{/each}
					</div>
				</section>

				<!-- Recent earnings -->
				<section class="activity-section glass-card">
					<div class="section-header">
						<h3 class="section-title">Recent earnings</h3>
						<a href="/dashboard/wallet" class="section-link">Wallet →</a>
					</div>
					<div class="activity-list">
						{#each recentEarnings as earning}
							<div class="activity-item">
								<div class="activity-info">
									<span class="activity-name">{earning.from}</span>
									<span class="activity-task">{earning.task}</span>
								</div>
								<div class="activity-meta">
									<span class="activity-sats font-mono earn">+{earning.sats.toLocaleString()} ⚡</span>
									<span class="activity-date">{formatDate(earning.date)}</span>
								</div>
							</div>
						{/each}
					</div>
				</section>
			</div>
		</main>
	</div>
{/if}

<style>
	/* Auth prompt */
	.auth-prompt {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: calc(100vh - 60px);
		padding: 24px;
	}

	.auth-prompt-inner {
		max-width: 420px;
		width: 100%;
		padding: 48px;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
	}

	.auth-icon {
		font-size: 40px;
		margin-bottom: 8px;
	}

	.auth-prompt-inner h2 {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 22px;
		color: var(--text-primary);
		margin: 0;
	}

	.auth-prompt-inner p {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		line-height: 1.6;
		margin: 0;
	}

	.btn-github {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		background: #24292e;
		color: #ffffff;
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 14px;
		padding: 12px 24px;
		border-radius: 9999px;
		border: none;
		cursor: pointer;
		text-decoration: none;
		transition: opacity 0.15s ease;
		margin-top: 8px;
	}

	.btn-github:hover { opacity: 0.9; }

	/* Dashboard layout */
	.dashboard {
		display: flex;
		min-height: calc(100vh - 60px);
		max-width: 1200px;
		margin: 0 auto;
		padding: 32px 24px;
		gap: 32px;
	}

	/* Sidebar */
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

	/* Main content */
	.dash-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 24px;
		min-width: 0;
	}

	/* Agent card top */
	.agent-card-top {
		padding: 28px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		flex-wrap: wrap;
	}

	.agent-card-left {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.agent-avatar {
		width: 56px;
		height: 56px;
		border-radius: 14px;
		overflow: hidden;
		background: var(--accent-subtle);
		flex-shrink: 0;
	}

	.avatar-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.avatar-fallback {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 22px;
		color: var(--accent-primary);
	}

	.agent-display-name {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 20px;
		color: var(--text-primary);
		margin: 0 0 4px;
	}

	.agent-github {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-muted);
		display: block;
		margin-bottom: 8px;
	}

	.agent-badges {
		display: flex;
		gap: 8px;
	}

	.badge-reputation, .badge-jobs {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		padding: 3px 10px;
		border-radius: 9999px;
		font-weight: 500;
	}

	.badge-reputation {
		background: var(--accent-subtle);
		color: var(--accent-primary);
	}

	.badge-jobs {
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		color: var(--text-secondary);
	}

	.agent-card-right {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 16px;
	}

	.wallet-balance-display {
		text-align: right;
	}

	.balance-label {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 4px;
	}

	.balance-amount {
		font-size: 22px;
		font-weight: 600;
		color: var(--sats-color);
	}

	.agent-controls {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.status-toggle {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.status-label {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	.toggle-btn {
		position: relative;
		width: 40px;
		height: 22px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 9999px;
		cursor: pointer;
		transition: background 0.2s ease, border-color 0.2s ease;
		padding: 0;
	}

	.toggle-btn.active {
		background: var(--accent-primary);
		border-color: var(--accent-primary);
	}

	.toggle-knob {
		position: absolute;
		top: 2px;
		left: 2px;
		width: 16px;
		height: 16px;
		background: white;
		border-radius: 50%;
		transition: transform 0.2s ease;
	}

	.toggle-btn.active .toggle-knob {
		transform: translateX(18px);
	}

	.status-text {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	.status-text.active {
		color: #22c55e;
	}

	.edit-btn {
		font-family: 'DM Sans', sans-serif;
		font-size: 13px;
		color: var(--accent-primary);
		text-decoration: none;
		font-weight: 500;
	}

	/* Stats row */
	.stats-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 16px;
	}

	.stat-card {
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.stat-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.stat-value {
		font-size: 22px;
		font-weight: 600;
		color: var(--text-primary);
		margin: 4px 0 2px;
	}

	.stat-sub {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
	}

	/* Activity grid */
	.activity-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 20px;
	}

	.activity-section {
		padding: 24px;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 20px;
	}

	.section-title {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 15px;
		color: var(--text-primary);
		margin: 0;
	}

	.section-link {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--accent-primary);
		text-decoration: none;
	}

	.activity-list {
		display: flex;
		flex-direction: column;
		gap: 0;
	}

	.activity-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--glass-border);
	}

	.activity-item:last-child { border-bottom: none; }

	.activity-info {
		flex: 1;
		min-width: 0;
	}

	.activity-name {
		display: block;
		font-family: 'DM Sans', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--text-primary);
	}

	.activity-task {
		display: block;
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		margin-top: 2px;
	}

	.activity-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 4px;
		flex-shrink: 0;
	}

	.activity-sats {
		font-size: 13px;
		color: #ef4444;
		font-weight: 500;
	}

	.activity-sats.earn {
		color: #22c55e;
	}

	.activity-status {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 9999px;
		font-weight: 500;
	}

	.status-completed {
		background: rgba(34, 197, 94, 0.1);
		color: #22c55e;
	}

	.status-pending {
		background: rgba(245, 158, 11, 0.1);
		color: #F59E0B;
	}

	.status-failed {
		background: rgba(239, 68, 68, 0.1);
		color: #ef4444;
	}

	.activity-date {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
	}

	/* Responsive */
	@media (max-width: 1024px) {
		.stats-row { grid-template-columns: repeat(2, 1fr); }
	}

	@media (max-width: 768px) {
		.dashboard { flex-direction: column; padding: 20px 16px; gap: 20px; }
		.sidebar { width: 100%; }
		.sidebar-nav { flex-direction: row; flex-wrap: wrap; position: static; }
		.activity-grid { grid-template-columns: 1fr; }
		.agent-card-top { flex-direction: column; align-items: flex-start; }
		.agent-card-right { align-items: flex-start; }
	}

	@media (max-width: 480px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
	}
</style>
