<script lang="ts">
	import '../app.css';
	import Header from '$lib/components/Header.svelte';
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores/theme';

	// Enable smooth theme transitions after initial mount (prevents flash)
	onMount(() => {
		// Small delay to ensure initial theme is applied without transition
		requestAnimationFrame(() => {
			document.documentElement.classList.add('theme-ready');
		});
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

	@media (max-width: 480px) {
		.footer-inner {
			flex-direction: column;
			align-items: flex-start;
		}
	}
</style>
