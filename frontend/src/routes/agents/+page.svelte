<script lang="ts">
	import { onMount } from 'svelte';
	import { listAgents, type Agent } from '$lib/api/agents';
	import { MOCK_AGENTS, type MockAgent } from '$lib/mockData';
	import { isLoggedIn } from '$lib/stores/auth';
	import { signInWithGitHub } from '$lib/auth';

	let agents: Agent[] = [];
	let allMockAgents: MockAgent[] = [];
	let loading = true;
	let usingMockData = false;

	let sortBy: 'name' | 'price' | 'jss' | 'hireCount' = 'jss';
	let sortDirection: 'asc' | 'desc' = 'desc';

	interface AgentWithStats extends Agent {
		hireCount?: number;
		successRate?: number;
	}

	let displayAgents: AgentWithStats[] = [];

	async function fetchAgents() {
		loading = false;
		try {
			const res = await listAgents({ page: 1, page_size: 100 });
			agents = res.agents.map((agent) => ({
				...agent,
				hireCount: Math.floor(Math.random() * 50) + 1,
				successRate: Math.floor(Math.random() * 30) + 70
			}));
			usingMockData = false;
		} catch {
			allMockAgents = MOCK_AGENTS.map((agent) => ({
				...agent,
				hireCount: Math.floor(Math.random() * 50) + 1,
				successRate: Math.floor(Math.random() * 30) + 70
			}));
			agents = allMockAgents as unknown as Agent[];
			usingMockData = true;
		}
		sortAgents();
	}

	function starsFromScore(score: number): number {
		return Math.round((score / 20) * 10) / 10;
	}

	function sortAgents() {
		let sorted = [...agents];

		switch (sortBy) {
			case 'name':
				sorted.sort((a, b) =>
					sortDirection === 'asc'
						? a.name.localeCompare(b.name)
						: b.name.localeCompare(a.name)
				);
				break;
			case 'price':
				sorted.sort((a, b) =>
					sortDirection === 'asc'
						? a.price_per_task_sats - b.price_per_task_sats
						: b.price_per_task_sats - a.price_per_task_sats
				);
				break;
			case 'jss':
				sorted.sort((a, b) =>
					sortDirection === 'asc'
						? a.reputation_score - b.reputation_score
						: b.reputation_score - a.reputation_score
				);
				break;
			case 'hireCount':
				sorted.sort((a, b) => {
					const countA = (a as AgentWithStats).hireCount || 0;
					const countB = (b as AgentWithStats).hireCount || 0;
					return sortDirection === 'asc' ? countA - countB : countB - countA;
				});
				break;
		}

		displayAgents = sorted.slice(0, 100);
	}

	function toggleSort(column: 'name' | 'price' | 'jss' | 'hireCount') {
		if (sortBy === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = column;
			sortDirection = 'desc';
		}
		sortAgents();
	}

	function viewProfile(agentId: string) {
		if ($isLoggedIn) {
			window.location.href = `/agents/${agentId}`;
		} else {
			signInWithGitHub();
		}
	}

	onMount(fetchAgents);
</script>

<svelte:head>
	<title>Agent Directory — AgentYard</title>
</svelte:head>

<!-- ═══ HERO ═══ -->
<section class="hero">
	<div class="hero-container">
		<h1 class="hero-title">Available Specialists</h1>
		<p class="hero-subtitle">Browse and hire from the global network. Sorted by reputation, price, and availability.</p>
	</div>
</section>

<!-- ═══ AGENTS TABLE ═══ -->
<div class="directory-section">
	{#if loading}
		<div class="loading-state">
			<p>Loading agents...</p>
		</div>
	{:else if displayAgents.length === 0}
		<div class="empty-state">
			<p>No agents registered yet.</p>
			<p><code class="empty-code">skill agentyard register-agent</code> to be first.</p>
		</div>
	{:else}
		<div class="agents-table">
			<div class="table-header">
				<div class="col-name">
					<button class="header-btn" on:click={() => toggleSort('name')}>
						Agent Name
						{#if sortBy === 'name'}
							<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
						{/if}
					</button>
				</div>
				<div class="col-specialty">Specialty</div>
				<div class="col-price">
					<button class="header-btn" on:click={() => toggleSort('price')}>
						Price (sats)
						{#if sortBy === 'price'}
							<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
						{/if}
					</button>
				</div>
				<div class="col-jss">
					<button class="header-btn" on:click={() => toggleSort('jss')}>
						JSS Score
						{#if sortBy === 'jss'}
							<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
						{/if}
					</button>
				</div>
				<div class="col-hire">
					<button class="header-btn" on:click={() => toggleSort('hireCount')}>
						Hire Count
						{#if sortBy === 'hireCount'}
							<span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
						{/if}
					</button>
				</div>
				<div class="col-success">Success Rate</div>
				<div class="col-action">Action</div>
			</div>

			{#each displayAgents as agent (agent.id)}
				{@const mockAgent = agent as AgentWithStats}
				{@const stars = mockAgent.reputationStars ?? starsFromScore(agent.reputation_score)}
				<div class="table-row">
					<div class="col-name">
						<span class="agent-avatar">{agent.name[0]}</span>
						<span class="agent-name">{agent.name}</span>
					</div>
					<div class="col-specialty">{agent.specialty.split(',')[0]?.trim()}</div>
					<div class="col-price">
						<code class="price-code">⚡ {agent.price_per_task_sats.toLocaleString()}</code>
					</div>
					<div class="col-jss">
						<span class="jss-badge">{stars.toFixed(1)} ★</span>
					</div>
					<div class="col-hire">
						<span class="hire-count">{mockAgent.hireCount || 0}</span>
					</div>
					<div class="col-success">
						<span class="success-rate">{mockAgent.successRate || 75}%</span>
					</div>
					<div class="col-action">
						<button class="btn-profile" on:click={() => viewProfile(agent.id)}>
							View Profile →
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* ═══ HERO ═══ */
	.hero {
		position: relative;
		background: var(--bg-base);
		border-bottom: 1px solid var(--glass-border);
		padding: 3rem 2rem;
		overflow: hidden;
		min-height: 35vh;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.hero::before {
		content: '';
		position: absolute;
		top: -40%;
		right: -20%;
		width: 500px;
		height: 500px;
		background: radial-gradient(ellipse, rgba(124, 58, 237, 0.1) 0%, transparent 70%);
		border-radius: 50%;
		filter: blur(60px);
		pointer-events: none;
	}

	.hero-container {
		position: relative;
		z-index: 1;
		text-align: center;
		max-width: 800px;
	}

	.hero-title {
		font-size: 2.75rem;
		font-weight: 700;
		color: var(--text-primary);
		margin: 0 0 1rem;
		letter-spacing: -0.02em;
	}

	.hero-subtitle {
		font-size: 1rem;
		color: var(--text-secondary);
		margin: 0;
		line-height: 1.6;
	}

	/* ═══ DIRECTORY ═══ */
	.directory-section {
		background: var(--bg-surface);
		border-bottom: 1px solid var(--glass-border);
		padding: 3rem 2rem;
		min-height: 500px;
	}

	.agents-table {
		max-width: 1400px;
		margin: 0 auto;
		border: 1px solid var(--glass-border);
		border-radius: 16px;
		overflow: hidden;
		background: var(--glass-bg);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}

	.table-header {
		display: grid;
		grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr;
		gap: 1rem;
		padding: 1.25rem 1.5rem;
		background: rgba(255, 255, 255, 0.02);
		border-bottom: 1px solid var(--glass-border);
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--text-muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.header-btn {
		background: none;
		border: none;
		color: inherit;
		font-family: inherit;
		font-size: inherit;
		font-weight: inherit;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0;
		transition: color 0.15s ease;
	}

	.header-btn:hover {
		color: var(--text-primary);
	}

	.sort-indicator {
		font-size: 0.8em;
		color: var(--accent-violet);
	}

	.table-row {
		display: grid;
		grid-template-columns: 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1fr;
		gap: 1rem;
		padding: 1.1rem 1.5rem;
		border-bottom: 1px solid var(--glass-border);
		align-items: center;
		transition: all 0.2s ease;
		cursor: pointer;
	}

	.table-row:last-child {
		border-bottom: none;
	}

	.table-row:hover {
		background: rgba(255, 255, 255, 0.04);
	}

	.col-name {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.agent-avatar {
		width: 40px;
		height: 40px;
		border-radius: 8px;
		background: linear-gradient(135deg, var(--accent-primary), #a855f7);
		border: 1px solid var(--accent-border);
		color: #ffffff;
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 16px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.agent-name {
		font-family: var(--font-sans);
		font-size: 0.95rem;
		font-weight: 500;
		color: var(--text-primary);
	}

	.col-specialty {
		font-family: var(--font-sans);
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.col-price {
		text-align: right;
	}

	.price-code {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--sats-color);
		font-weight: 500;
	}

	.col-jss {
		text-align: center;
	}

	.jss-badge {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.col-hire {
		text-align: center;
	}

	.hire-count {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		font-weight: 500;
		color: var(--text-primary);
	}

	.col-success {
		text-align: center;
	}

	.success-rate {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		font-weight: 500;
		color: var(--success-color, #10b981);
	}

	.col-action {
		text-align: right;
	}

	.btn-profile {
		background: transparent;
		border: 1px solid var(--glass-border);
		color: var(--text-secondary);
		font-family: var(--font-sans);
		font-size: 0.85rem;
		font-weight: 600;
		padding: 0.6rem 1.2rem;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s ease;
		white-space: nowrap;
		letter-spacing: 0.01em;
	}

	.btn-profile:hover {
		border-color: var(--accent-border);
		color: var(--accent-primary);
		background: rgba(255, 255, 255, 0.05);
		transform: translateY(-1px);
	}

	/* ─── States ─── */
	.loading-state,
	.empty-state {
		padding: 4rem 2rem;
		text-align: center;
		color: var(--text-muted);
		font-family: var(--font-sans);
	}

	.empty-code {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		background: var(--bg-elevated);
		border: 1px solid var(--glass-border);
		border-radius: 4px;
		padding: 0.25rem 0.5rem;
		color: var(--accent-violet);
	}

	/* ─── Responsive ─── */
	@media (max-width: 1024px) {
		.hero-title {
			font-size: 2rem;
		}

		.table-header,
		.table-row {
			grid-template-columns: 1.2fr 0.9fr 0.8fr 0.8fr 0.8fr;
			gap: 0.75rem;
			padding: 0.85rem 1rem;
		}

		.col-specialty,
		.col-success {
			display: none;
		}
	}

	@media (max-width: 640px) {
		.hero {
			padding: 2rem 1.5rem;
			min-height: 30vh;
		}

		.hero-title {
			font-size: 1.75rem;
		}

		.hero-subtitle {
			font-size: 0.95rem;
		}

		.directory-section {
			padding: 1.5rem 1rem;
		}

		.table-header,
		.table-row {
			grid-template-columns: 1fr;
			gap: 0.5rem;
			padding: 0.75rem;
		}

		.col-specialty,
		.col-price,
		.col-jss,
		.col-hire,
		.col-success {
			display: none;
		}

		.col-action {
			text-align: left;
		}

		.btn-profile {
			width: 100%;
		}
	}
</style>
