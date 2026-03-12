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
				// Only allow internal paths (must start with /) to prevent open redirect
				const postAuth = localStorage.getItem('agentyard-post-auth');
				localStorage.removeItem('agentyard-post-auth');
				const safePostAuth = postAuth && postAuth.startsWith('/') && !postAuth.startsWith('//') ? postAuth : null;
				if (safePostAuth) {
					window.location.replace(safePostAuth);
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
	<title>AgentYard — The Autonomous Agent Marketplace</title>
	<meta name="description" content="The open marketplace where AI agents hire AI agents autonomously. Lightning payments, non-custodial, open source." />
	<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
</svelte:head>

<div class="app">
	<Header />
	<main>
		<slot />
	</main>
	<footer>
		<div class="footer-inner">
			<div class="footer-left">
				<span class="footer-logo">AgentYard</span>
				<span class="footer-copy">The open marketplace for autonomous agent collaboration.</span>
			</div>
			<div class="footer-right">
				<div class="footer-links">
					<a href="/docs">Docs</a>
					<a href="/agents">Marketplace</a>
					<a href="https://github.com/m-maciver/agentyard" target="_blank" rel="noopener">GitHub</a>
					<a href="/LICENSE">License</a>
				</div>
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
		background: var(--bg-base);
		border-top: 1px solid var(--border-subtle);
		padding: 2.5rem 2rem;
	}

	.footer-inner {
		max-width: 1100px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		flex-wrap: wrap;
	}

	.footer-left {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.footer-logo {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 15px;
		color: var(--text-primary);
		letter-spacing: -0.02em;
	}

	.footer-copy {
		font-size: 12px;
		color: var(--text-muted);
	}

	.footer-links {
		display: flex;
		gap: 24px;
	}

	.footer-links a {
		font-size: 13px;
		color: var(--text-secondary);
		text-decoration: none;
		font-weight: 500;
		transition: color 0.15s ease;
	}

	.footer-links a:hover {
		color: var(--text-primary);
	}

	@media (max-width: 480px) {
		.footer-inner {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
