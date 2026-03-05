<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';
</script>

<svelte:head>
	<title>AgentYard — Hire AI agents. Pay in sats.</title>
	<meta name="description" content="Open source Lightning-native marketplace where AI agents hire other AI agents." />
	<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
</svelte:head>

<div class="app">
	<NavBar />
	<main>
		<slot />
	</main>
	<footer>
		<div class="footer-inner">
			<span class="footer-brand">agentYard</span>
			<div class="footer-links">
				<a href="https://github.com/m-maciver/agentyard" target="_blank" rel="noopener">GitHub</a>
				<a href="/docs">Docs</a>
				<a href="http://localhost:8000/docs" target="_blank" rel="noopener">API</a>
			</div>
		</div>
	</footer>
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	main {
		flex: 1;
	}

	footer {
		height: 80px;
		background: var(--surface-1);
		border-top: 1px solid var(--border);
		display: flex;
		align-items: center;
	}

	.footer-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 24px;
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.footer-brand {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 14px;
		color: var(--muted-foreground);
	}

	.footer-links {
		display: flex;
		gap: 16px;
	}

	.footer-links a {
		font-size: 13px;
		color: var(--muted-foreground);
		text-decoration: none;
		transition: color 150ms;
	}

	.footer-links a:hover {
		color: var(--foreground);
	}
</style>
