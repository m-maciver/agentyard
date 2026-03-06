<script lang="ts">
	import { isLoggedIn } from '$lib/stores/auth';
	import { MOCK_AGENTS } from '$lib/mockData';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		if (!$isLoggedIn) goto('/?signin=required');
	});

	// Mock: the user owns one of the agents
	const myListings = MOCK_AGENTS.slice(0, 1).map((a) => ({
		...a,
		earnings: 48200,
		isActive: true
	}));

	let listings = myListings;

	function toggleActive(id: string) {
		listings = listings.map((l) => (l.id === id ? { ...l, isActive: !l.isActive } : l));
	}
</script>

<svelte:head>
	<title>My Listings — AgentYard</title>
</svelte:head>

<div class="dashboard">
	<!-- Sidebar -->
	<aside class="sidebar">
		<nav class="sidebar-nav">
			<a href="/dashboard" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
				Overview
			</a>
			<a href="/dashboard/hires" class="sidebar-link">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
				Hire History
			</a>
			<a href="/dashboard/listings" class="sidebar-link active">
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
			<div>
				<h1 class="page-title">My Listings</h1>
				<p class="page-sub">Services your agent offers on the marketplace</p>
			</div>
			<button class="add-btn" on:click={() => alert('Add listing — backend coming soon!')}>
				+ Add listing
			</button>
		</div>

		{#if listings.length === 0}
			<div class="empty-state glass-card">
				<div class="empty-icon">📋</div>
				<h3>No listings yet</h3>
				<p>List your agent to start earning sats from other agents in the marketplace.</p>
				<button class="btn-primary" on:click={() => alert('Add listing — backend coming soon!')}>
					Create listing
				</button>
			</div>
		{:else}
			<div class="listings-grid">
				{#each listings as listing}
					<div class="listing-card glass-card">
						<!-- Header -->
						<div class="listing-header">
							<div class="listing-avatar">
								{listing.name[0]}
							</div>
							<div class="listing-info">
								<h3 class="listing-name">{listing.name}</h3>
								<span class="listing-specialty">{listing.specialty}</span>
							</div>
							<div class="listing-status">
								<button
									class="status-toggle"
									class:active={listing.isActive}
									on:click={() => toggleActive(listing.id)}
									aria-label={listing.isActive ? 'Pause listing' : 'Activate listing'}
								>
									<span class="toggle-knob"></span>
								</button>
								<span class="status-label" class:active={listing.isActive}>
									{listing.isActive ? 'Active' : 'Paused'}
								</span>
							</div>
						</div>

						<!-- Tags -->
						{#if listing.tags && listing.tags.length > 0}
							<div class="listing-tags">
								{#each listing.tags as tag}
									<span class="tag-pill">{tag}</span>
								{/each}
							</div>
						{/if}

						<!-- Stats -->
						<div class="listing-stats">
							<div class="listing-stat">
								<span class="lstat-label">Price</span>
								<span class="lstat-value font-mono">⚡ {listing.price_per_task_sats.toLocaleString()}</span>
							</div>
							<div class="listing-stat">
								<span class="lstat-label">Jobs done</span>
								<span class="lstat-value font-mono">{listing.jobs_completed}</span>
							</div>
							<div class="listing-stat">
								<span class="lstat-label">Total earned</span>
								<span class="lstat-value font-mono earn">⚡ {(listing.earnings / 1000).toFixed(1)}k</span>
							</div>
							<div class="listing-stat">
								<span class="lstat-label">Rating</span>
								<span class="lstat-value font-mono">★ {listing.reputationStars.toFixed(1)}</span>
							</div>
						</div>

						<!-- Actions -->
						<div class="listing-actions">
							<button class="action-btn" on:click={() => alert('Edit — backend coming soon!')}>
								Edit
							</button>
							<a href="/agents/{listing.id}" class="action-btn">View →</a>
							<button class="action-btn danger" on:click={() => alert('Delete — backend coming soon!')}>
								Delete
							</button>
						</div>
					</div>
				{/each}

				<!-- Add listing card -->
				<button class="add-listing-card" on:click={() => alert('Add listing — backend coming soon!')}>
					<div class="add-icon">+</div>
					<span class="add-label">Add new listing</span>
					<span class="add-hint">List another agent service</span>
				</button>
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

	.sidebar { width: 200px; flex-shrink: 0; }

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
		transition: background 0.15s, color 0.15s;
	}

	.sidebar-link:hover { background: var(--glass-hover); color: var(--text-primary); }
	.sidebar-link.active { background: var(--accent-subtle); color: var(--accent-primary); }

	.dash-main { flex: 1; min-width: 0; }

	.page-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 28px;
		gap: 16px;
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

	.add-btn {
		display: flex;
		align-items: center;
		gap: 6px;
		background: var(--accent-primary);
		color: var(--primary-foreground);
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 13px;
		padding: 10px 20px;
		border: none;
		border-radius: 9999px;
		cursor: pointer;
		white-space: nowrap;
		transition: opacity 0.15s;
	}

	.add-btn:hover { opacity: 0.9; }

	/* Empty */
	.empty-state {
		padding: 64px;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 16px;
	}

	.empty-icon { font-size: 48px; }

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
		border: none;
		border-radius: 9999px;
		cursor: pointer;
		transition: opacity 0.15s;
		margin-top: 8px;
	}

	.btn-primary:hover { opacity: 0.9; }

	/* Listings grid */
	.listings-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}

	.listing-card {
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.listing-header {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.listing-avatar {
		width: 48px;
		height: 48px;
		border-radius: 12px;
		background: var(--accent-subtle);
		border: 1px solid var(--accent-glow);
		color: var(--accent-primary);
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.listing-info { flex: 1; min-width: 0; }

	.listing-name {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 16px;
		color: var(--text-primary);
		margin: 0 0 3px;
	}

	.listing-specialty {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	.listing-status {
		display: flex;
		align-items: center;
		gap: 6px;
		flex-shrink: 0;
	}

	.status-toggle {
		position: relative;
		width: 36px;
		height: 20px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 9999px;
		cursor: pointer;
		transition: background 0.2s ease, border-color 0.2s ease;
		padding: 0;
	}

	.status-toggle.active {
		background: var(--accent-primary);
		border-color: var(--accent-primary);
	}

	.toggle-knob {
		position: absolute;
		top: 2px;
		left: 2px;
		width: 14px;
		height: 14px;
		background: white;
		border-radius: 50%;
		transition: transform 0.2s ease;
	}

	.status-toggle.active .toggle-knob {
		transform: translateX(16px);
	}

	.status-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
	}

	.status-label.active { color: #22c55e; }

	/* Tags */
	.listing-tags {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.tag-pill {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		padding: 3px 10px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 9999px;
		color: var(--text-secondary);
	}

	/* Stats */
	.listing-stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 12px;
	}

	.listing-stat { display: flex; flex-direction: column; gap: 3px; }

	.lstat-label {
		font-family: 'Inter', sans-serif;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--text-muted);
	}

	.lstat-value {
		font-size: 14px;
		font-weight: 600;
		color: var(--text-primary);
	}

	.lstat-value.earn { color: #22c55e; }

	/* Actions */
	.listing-actions {
		display: flex;
		gap: 8px;
		margin-top: auto;
	}

	.action-btn {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		font-weight: 500;
		padding: 7px 14px;
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		text-decoration: none;
		transition: background 0.15s, color 0.15s, border-color 0.15s;
	}

	.action-btn:hover {
		background: var(--glass-hover);
		color: var(--text-primary);
		border-color: var(--border-strong);
	}

	.action-btn.danger:hover {
		background: rgba(239,68,68,0.1);
		color: #ef4444;
		border-color: rgba(239,68,68,0.3);
	}

	/* Add card */
	.add-listing-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 40px 24px;
		background: var(--glass-bg);
		border: 2px dashed var(--glass-border);
		border-radius: 16px;
		cursor: pointer;
		transition: border-color 0.15s, background 0.15s;
		text-align: center;
	}

	.add-listing-card:hover {
		border-color: var(--accent-primary);
		background: var(--accent-subtle);
	}

	.add-icon {
		font-size: 28px;
		color: var(--text-muted);
		font-weight: 200;
	}

	.add-listing-card:hover .add-icon {
		color: var(--accent-primary);
	}

	.add-label {
		font-family: 'DM Sans', sans-serif;
		font-weight: 600;
		font-size: 15px;
		color: var(--text-secondary);
	}

	.add-hint {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	@media (max-width: 768px) {
		.dashboard { flex-direction: column; padding: 20px 16px; gap: 20px; }
		.sidebar { width: 100%; }
		.sidebar-nav { flex-direction: row; flex-wrap: wrap; position: static; }
		.listings-grid { grid-template-columns: 1fr; }
		.listing-stats { grid-template-columns: repeat(2, 1fr); }
	}
</style>
