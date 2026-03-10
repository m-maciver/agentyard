<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore, isLoggedIn } from '$lib/stores/auth';
	import { signInWithGitHub, mapBackendUser, type GitHubUser } from '$lib/auth';
	import CountdownTimer from '$lib/components/CountdownTimer.svelte';
	import EscrowWindow from '$lib/components/EscrowWindow.svelte';
	import { PUBLIC_API_URL } from '$env/static/public';

	const API_URL = PUBLIC_API_URL || 'https://agentyard-production.up.railway.app';

	let user: GitHubUser | null = null;
	let agentActive = true;

	// Real job data from API
	interface HiringJob {
		id: string;
		task_description: string;
		status: string;
		price_sats: number;
		fee_sats: number;
		created_at: string;
		provider_agent_id: string;
		client_agent_id?: string;
	}

	let recentJobs: HiringJob[] = [];
	let jobsLoading = true;
	let expandedJobId: string | null = null;
	let refreshInterval: NodeJS.Timeout | undefined;

	// Mock stats for now (would come from API)
	const mockStats = {
		totalEarned: 125000,
		jobsCompleted: 18,
		activeListings: 1,
		avgRating: 4.7
	};

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

			// Fetch real jobs
			await fetchJobs(token);

			// Auto-refresh every 5s for active escrow windows
			refreshInterval = setInterval(() => fetchJobs(token), 5000);
		} else {
			jobsLoading = false;
		}
	});

	async function fetchJobs(token: string) {
		try {
			const jobsRes = await fetch(`${API_URL}/jobs`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (jobsRes.ok) {
				const data = await jobsRes.json();
				recentJobs = (data.jobs ?? data ?? []).slice(0, 10);
			}
		} catch {
			// Jobs unavailable
		} finally {
			jobsLoading = false;
		}
	}

	function handleAcceptJob(jobId: string) {
		// TODO: Call API to accept job
		console.log('Accept job:', jobId);
	}

	function handleDisputeJob(jobId: string) {
		// TODO: Call API to dispute job
		console.log('Dispute job:', jobId);
	}

	function toggleExpanded(jobId: string) {
		expandedJobId = expandedJobId === jobId ? null : jobId;
	}

	function isWithinEscrowWindow(createdAt: string, windowMinutes: number = 10): boolean {
		const now = new Date();
		const created = new Date(createdAt);
		const diff = now.getTime() - created.getTime();
		return diff < windowMinutes * 60 * 1000;
	}

	$: user = $authStore;
	$: if (typeof window !== 'undefined' && !$isLoggedIn) {
		goto('/?signin=required');
	}

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-AU', { day: 'numeric', month: 'short' });
	}

	function formatTime(dateStr: string) {
		return new Date(dateStr).toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' });
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

			<!-- Hiring feed (autonomous hiring timeline) -->
			<section class="hiring-feed">
				<div class="feed-header">
					<h2 class="feed-title">⚡ Autonomous hiring feed</h2>
					<p class="feed-sub">Jobs your agent is managing and agents it has hired</p>
					<a href="/dashboard/hires" class="feed-link">View full history →</a>
				</div>

				{#if jobsLoading}
					<div class="feed-loading">
						<div class="feed-spinner"></div>
						<p>Loading hiring timeline…</p>
					</div>
				{:else if recentJobs.length === 0}
					<div class="feed-empty glass-card">
						<div class="empty-icon">🤝</div>
						<h3>No hiring activity yet</h3>
						<p>Your agent hasn't hired specialists yet. When it does, you'll see the entire collaboration here.</p>
						<a href="/" class="btn-hire-first">Hire an agent →</a>
					</div>
				{:else}
					<div class="feed-timeline">
						{#each recentJobs as job (job.id)}
							{@const isEscrow = ['escrowed', 'in_progress'].includes(job.status)}
							{@const withinWindow = isWithinEscrowWindow(job.created_at)}
							<div class="feed-card glass-card" class:escrow-active={isEscrow && withinWindow}>
								<div class="card-timeline-marker"></div>

								<!-- Card header -->
								<div class="card-top">
									<div class="card-title-row">
										<span class="card-icon">⚙️</span>
										<div class="card-title-info">
											<h3 class="card-title">Hired <strong>{job.provider_agent_id}</strong></h3>
											<p class="card-subtitle">for: {job.task_description.slice(0, 80)}{job.task_description.length > 80 ? '…' : ''}</p>
										</div>
									</div>
									<div class="card-meta">
										<span class="card-date font-mono">{formatDate(job.created_at)}</span>
										<span class="card-time font-mono">{formatTime(job.created_at)}</span>
									</div>
								</div>

								<!-- Status and cost row -->
								<div class="card-status-row">
									<span class="status-badge status-{job.status}">{job.status}</span>
									<span class="cost-sats font-mono">⚡ {job.price_sats.toLocaleString()} sats</span>
								</div>

								<!-- Escrow window (if active) -->
								{#if isEscrow && withinWindow}
									<div class="card-escrow-section">
										<CountdownTimer
											createdAt={job.created_at}
											windowMinutes={10}
											onExpire={() => console.log('Escrow window expired for', job.id)}
										/>
										<EscrowWindow priceInSats={job.price_sats} platformFeePercent={0.12} />
									</div>
								{/if}

								<!-- Expandable details -->
								<button
									class="card-expand-btn"
									on:click={() => toggleExpanded(job.id)}
									class:expanded={expandedJobId === job.id}
								>
									<span class="expand-text">{expandedJobId === job.id ? 'Hide details' : 'Show details'}</span>
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<polyline points="6 9 12 15 18 9"></polyline>
									</svg>
								</button>

								{#if expandedJobId === job.id}
									<div class="card-details">
										<div class="detail-row">
											<span class="detail-key">Job ID:</span>
											<span class="detail-val font-mono">{job.id.slice(0, 12)}…</span>
										</div>
										<div class="detail-row">
											<span class="detail-key">Seller:</span>
											<a href="/agents/{job.provider_agent_id}" class="detail-val agent-link">@{job.provider_agent_id}</a>
										</div>
										<div class="detail-row">
											<span class="detail-key">Full task:</span>
											<span class="detail-val detail-wrap">{job.task_description}</span>
										</div>
										<div class="detail-row">
											<span class="detail-key">Payment:</span>
											<span class="detail-val font-mono">⚡ {job.price_sats.toLocaleString()} + {job.fee_sats?.toLocaleString() ?? 0} fee</span>
										</div>
									</div>
								{/if}

								<!-- Action buttons (if within escrow window) -->
								{#if isEscrow && withinWindow}
									<div class="card-actions">
										<button class="btn-action btn-accept" on:click={() => handleAcceptJob(job.id)}>
											✓ Accept delivery
										</button>
										<button class="btn-action btn-dispute" on:click={() => handleDisputeJob(job.id)}>
											⚠ Dispute
										</button>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</section>
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
		background: var(--accent-primary);
		color: #ffffff;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 14px;
		padding: 12px 24px;
		border-radius: 9999px;
		border: none;
		cursor: pointer;
		text-decoration: none;
		transition: opacity 0.15s ease, box-shadow 0.15s ease;
		margin-top: 8px;
	}

	.btn-github:hover {
		opacity: 0.9;
		box-shadow: 0 4px 16px var(--accent-glow);
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

	/* ═══ HIRING FEED ═══ */
	.hiring-feed {
		margin-top: 32px;
	}

	.feed-header {
		margin-bottom: 24px;
	}

	.feed-title {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 700;
		font-size: 24px;
		color: var(--text-primary);
		margin: 0 0 6px;
		letter-spacing: -0.01em;
	}

	.feed-sub {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		margin: 0 0 12px;
	}

	.feed-link {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--accent-primary);
		text-decoration: none;
		font-weight: 500;
	}

	.feed-link:hover {
		text-decoration: underline;
	}

	.feed-loading {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
		padding: 48px;
		color: var(--text-muted);
	}

	.feed-spinner {
		width: 24px;
		height: 24px;
		border: 2px solid rgba(255, 255, 255, 0.1);
		border-top-color: var(--accent-primary);
		border-radius: 50%;
		animation: feed-spin 0.6s linear infinite;
	}

	@keyframes feed-spin {
		to { transform: rotate(360deg); }
	}

	.feed-empty {
		padding: 64px 24px;
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
	}

	.empty-icon {
		font-size: 48px;
		line-height: 1;
		margin-bottom: 8px;
	}

	.feed-empty h3 {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 18px;
		color: var(--text-primary);
		margin: 0;
	}

	.feed-empty p {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--text-secondary);
		margin: 0;
		max-width: 380px;
	}

	.btn-hire-first {
		display: inline-flex;
		background: var(--accent-primary);
		color: white;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 14px;
		padding: 10px 24px;
		border: none;
		border-radius: 9999px;
		text-decoration: none;
		cursor: pointer;
		transition: opacity 0.15s;
		margin-top: 8px;
	}

	.btn-hire-first:hover {
		opacity: 0.9;
	}

	.feed-timeline {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	/* Feed card */
	.feed-card {
		position: relative;
		padding: 20px;
		border: 1px solid var(--glass-border);
		border-radius: 14px;
		background: var(--glass-bg);
		transition: all 0.2s ease;
	}

	.feed-card.escrow-active {
		border-color: rgba(245, 158, 11, 0.3);
		background: linear-gradient(135deg, var(--glass-bg), rgba(245, 158, 11, 0.05));
		box-shadow: 0 0 20px rgba(245, 158, 11, 0.1);
	}

	.card-timeline-marker {
		position: absolute;
		left: -12px;
		top: 28px;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--accent-primary);
		border: 3px solid var(--bg-base);
	}

	.card-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		margin-bottom: 12px;
	}

	.card-title-row {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		flex: 1;
	}

	.card-icon {
		font-size: 20px;
		line-height: 1;
		flex-shrink: 0;
		margin-top: 2px;
	}

	.card-title-info {
		flex: 1;
	}

	.card-title {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 15px;
		color: var(--text-primary);
		margin: 0 0 3px;
	}

	.card-title strong {
		color: var(--accent-violet);
		font-weight: 700;
	}

	.card-subtitle {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		margin: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.card-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 2px;
		flex-shrink: 0;
	}

	.card-date, .card-time {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
	}

	.card-status-row {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-bottom: 12px;
	}

	.status-badge {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		font-weight: 600;
		padding: 3px 10px;
		border-radius: 20px;
		text-transform: capitalize;
	}

	.status-escrowed {
		background: rgba(245, 158, 11, 0.15);
		color: #f7931a;
	}

	.status-in_progress {
		background: rgba(59, 130, 246, 0.15);
		color: #3b82f6;
	}

	.status-completed {
		background: rgba(34, 197, 94, 0.15);
		color: #22c55e;
	}

	.status-disputed {
		background: rgba(239, 68, 68, 0.15);
		color: #ef4444;
	}

	.cost-sats {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--sats-color);
		font-weight: 500;
		margin-left: auto;
	}

	.card-escrow-section {
		display: flex;
		gap: 16px;
		margin: 16px 0;
		padding: 12px 0;
		border-top: 1px solid var(--glass-border);
		border-bottom: 1px solid var(--glass-border);
	}

	.card-expand-btn {
		display: flex;
		align-items: center;
		gap: 6px;
		background: transparent;
		border: none;
		color: var(--accent-primary);
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		font-weight: 500;
		padding: 6px 0;
		cursor: pointer;
		transition: opacity 0.15s;
		margin-top: 8px;
	}

	.card-expand-btn:hover {
		opacity: 0.8;
	}

	.card-expand-btn svg {
		transition: transform 0.2s ease;
	}

	.card-expand-btn.expanded svg {
		transform: rotate(180deg);
	}

	.card-details {
		margin-top: 12px;
		padding: 12px;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 8px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.detail-row {
		display: flex;
		align-items: flex-start;
		gap: 12px;
	}

	.detail-key {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
		font-weight: 500;
		flex-shrink: 0;
		width: 80px;
	}

	.detail-val {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-secondary);
		flex: 1;
	}

	.detail-wrap {
		word-break: break-word;
	}

	.agent-link {
		color: var(--accent-primary);
		text-decoration: none;
	}

	.agent-link:hover {
		text-decoration: underline;
	}

	.card-actions {
		display: flex;
		gap: 8px;
		margin-top: 12px;
		padding-top: 12px;
		border-top: 1px solid var(--glass-border);
	}

	.btn-action {
		flex: 1;
		padding: 9px 14px;
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		font-family: 'Inter', sans-serif;
		font-weight: 500;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.btn-accept {
		background: rgba(34, 197, 94, 0.12);
		color: #22c55e;
		border-color: rgba(34, 197, 94, 0.3);
	}

	.btn-accept:hover {
		background: rgba(34, 197, 94, 0.2);
		border-color: #22c55e;
	}

	.btn-dispute {
		background: rgba(239, 68, 68, 0.12);
		color: #ef4444;
		border-color: rgba(239, 68, 68, 0.3);
	}

	.btn-dispute:hover {
		background: rgba(239, 68, 68, 0.2);
		border-color: #ef4444;
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
		.card-escrow-section { flex-direction: column; }
		.card-top { flex-direction: column; }
		.card-meta { align-items: flex-start; }
	}

	@media (max-width: 480px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
	}
</style>
