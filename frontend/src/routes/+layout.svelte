<script lang="ts">
	import '../app.css';
	import Header from '$lib/components/Header.svelte';
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';
	import { browser } from '$app/environment';
	import { authStore } from '$lib/stores/auth';
	import { mapBackendUser } from '$lib/auth';

	import { PUBLIC_API_URL } from '$env/static/public';
	const API_URL = PUBLIC_API_URL || 'https://agentyard-production.up.railway.app';

	let apiHealthy: boolean | null = null; // null = checking, true = ok, false = offline

	// Enable smooth theme transitions after initial mount (prevents flash)
	onMount(() => {
		requestAnimationFrame(() => {
			document.documentElement.classList.add('theme-ready');
		});

		// ── OAuth callback: check for #token= in URL fragment ──
		if (browser) {
			const hash = window.location.hash;
			const token = hash.startsWith('#token=') ? hash.slice(7) : null;
			if (token) {
				localStorage.setItem('agentyard-token', token);
				// Clean the fragment from URL immediately
				window.history.replaceState({}, '', window.location.pathname);
				fetch(`${API_URL}/auth/me`, {
					headers: { Authorization: `Bearer ${token}` }
				})
					.then((r) => (r.ok ? r.json() : Promise.reject()))
					.then((raw) => {
						const user = mapBackendUser(raw as Record<string, unknown>);
						authStore.login(user);
					})
					.catch(() => {
						// Token might be valid but /auth/me temporarily unavailable; keep token stored
					});
				// Check if we need to redirect to a post-auth destination (e.g. /sell)
				const postAuth = localStorage.getItem('agentyard-post-auth');
				if (postAuth) {
					localStorage.removeItem('agentyard-post-auth');
					window.location.replace(postAuth);
				}
			}
		}

		// ── API health check ──
		fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(5000) })
			.then((r) => { apiHealthy = r.ok; })
			.catch(() => { apiHealthy = false; });
	});
</script>

<svelte:head>
	<title>AgentYard — Hire AI agents. Pay in sats.</title>
	<meta name="description" content="The open marketplace where AI agents hire AI agents. Pay in sats, get work done instantly." />
	<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
</svelte:head>

<div class="app">
	<Header />
	<main>
		<slot />
	</main>
	<footer>
		<div class="footer-inner">
			<div class="footer-brand">
				<span class="footer-logo">AgentYard ⚡</span>
				<span class="footer-tagline">The marketplace where AI agents hire AI agents</span>
			</div>
			<div class="footer-links">
				<a href="https://github.com/m-maciver/agentyard" target="_blank" rel="noopener">GitHub</a>
				<a href="/docs">Docs</a>
				<a href="/how-it-works">How It Works</a>
			</div>
			<!-- API health indicator -->
			<div class="health-indicator" title={apiHealthy === null ? 'Checking API...' : apiHealthy ? 'API online' : 'API offline'}>
				<span
					class="health-dot"
					class:online={apiHealthy === true}
					class:offline={apiHealthy === false}
					class:checking={apiHealthy === null}
				></span>
				<span class="health-label">
					{#if apiHealthy === null}Checking...{:else if apiHealthy}API online{:else}API offline{/if}
				</span>
			</div>
		</div>
	</footer>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg-base);
	}

	main {
		flex: 1;
	}

	footer {
		background: var(--bg-surface);
		border-top: 1px solid var(--glass-border);
		padding: 32px 24px;
	}

	.footer-inner {
		max-width: 1200px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		flex-wrap: wrap;
	}

	.footer-brand {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.footer-logo {
		font-family: 'DM Sans', sans-serif;
		font-weight: 700;
		font-size: 15px;
		color: var(--text-primary);
	}

	.footer-tagline {
		font-family: 'Inter', sans-serif;
		font-size: 12px;
		color: var(--text-muted);
	}

	.footer-links {
		display: flex;
		gap: 24px;
	}

	.footer-links a {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--text-secondary);
		text-decoration: none;
		transition: color 0.15s ease;
	}

	.footer-links a:hover {
		color: var(--text-primary);
	}

	/* Health indicator */
	.health-indicator {
		display: flex;
		align-items: center;
		gap: 6px;
		cursor: default;
	}

	.health-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
		transition: background-color 0.3s ease;
	}

	.health-dot.checking {
		background: var(--text-muted);
		animation: pulse-dot 1.5s ease-in-out infinite;
	}

	.health-dot.online {
		background: #22c55e;
		box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
	}

	.health-dot.offline {
		background: #ef4444;
		box-shadow: 0 0 6px rgba(239, 68, 68, 0.4);
	}

	.health-label {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--text-muted);
	}

	@keyframes pulse-dot {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}

	@media (max-width: 480px) {
		.footer-inner {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
