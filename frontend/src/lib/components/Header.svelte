<script lang="ts">
	import { page } from '$app/stores';
	import { theme, toggleTheme } from '$lib/stores/theme';

	let menuOpen = false;

	$: currentPath = $page.url.pathname;

	function handleNavClick() {
		menuOpen = false;
	}
</script>

<header class="header">
	<div class="header-inner">
		<!-- Logo -->
		<a href="/" class="logo" on:click={handleNavClick}>
			<span class="logo-text">AgentYard</span>
		</a>

		<!-- Center nav (desktop) -->
		<nav class="center-nav">
			<a href="/agents" class="nav-link" class:active={currentPath === '/agents'} on:click={handleNavClick}>
				Marketplace
			</a>
			<a href="/docs" class="nav-link" class:active={currentPath === '/docs'} on:click={handleNavClick}>
				Docs
			</a>
			<a href="https://github.com/m-maciver/agentyard" class="nav-link" target="_blank" rel="noopener">
				GitHub
			</a>
		</nav>

		<!-- Right actions -->
		<div class="header-right">
			<!-- Theme toggle -->
			<button class="theme-toggle" on:click|stopPropagation={toggleTheme} aria-label="Toggle theme" title="Toggle light/dark mode">
				{#if $theme === 'dark'}
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<circle cx="12" cy="12" r="5"/>
						<line x1="12" y1="1" x2="12" y2="3"/>
						<line x1="12" y1="21" x2="12" y2="23"/>
						<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
						<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
						<line x1="1" y1="12" x2="3" y2="12"/>
						<line x1="21" y1="12" x2="23" y2="12"/>
						<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
						<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
					</svg>
				{:else}
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
					</svg>
				{/if}
			</button>

			<!-- Mobile hamburger -->
			<button class="hamburger" on:click|stopPropagation={() => (menuOpen = !menuOpen)} aria-label="Menu">
				{#if menuOpen}
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
				{:else}
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
				{/if}
			</button>
		</div>
	</div>

	<!-- Mobile drawer -->
	{#if menuOpen}
		<div class="mobile-drawer">
			<a href="/agents" class="mobile-link" class:active={currentPath === '/agents'} on:click={handleNavClick}>Marketplace</a>
			<a href="/docs" class="mobile-link" class:active={currentPath === '/docs'} on:click={handleNavClick}>Docs</a>
			<a href="https://github.com/m-maciver/agentyard" class="mobile-link" target="_blank" rel="noopener">GitHub</a>
		</div>
	{/if}
</header>

<style>
	.header {
		position: sticky;
		top: 0;
		z-index: 100;
		height: 56px;
		background: var(--glass-bg);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border-bottom: 1px solid var(--border-subtle);
	}

	.header-inner {
		max-width: 1100px;
		margin: 0 auto;
		height: 100%;
		padding: 0 24px;
		display: flex;
		align-items: center;
		gap: 24px;
	}

	/* Logo */
	.logo {
		display: flex;
		align-items: center;
		text-decoration: none;
		flex-shrink: 0;
	}

	.logo-text {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 17px;
		color: var(--text-primary);
		letter-spacing: -0.03em;
	}

	/* Center nav */
	.center-nav {
		display: flex;
		align-items: center;
		gap: 4px;
		flex: 1;
		justify-content: center;
	}

	.nav-link {
		font-weight: 500;
		font-size: 13.5px;
		color: var(--text-secondary);
		text-decoration: none;
		padding: 6px 12px;
		border-radius: 8px;
		transition: color 0.15s ease, background 0.15s ease;
	}

	.nav-link:hover {
		color: var(--text-primary);
		background: var(--glass-hover);
	}

	.nav-link.active {
		color: var(--text-primary);
		font-weight: 600;
	}

	/* Right section */
	.header-right {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}

	/* Theme toggle */
	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		background: transparent;
		border: 1px solid var(--border-subtle);
		border-radius: 8px;
		color: var(--text-muted);
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.theme-toggle:hover {
		color: var(--text-primary);
		border-color: var(--border-strong);
		background: var(--glass-hover);
	}

	/* Hamburger */
	.hamburger {
		display: none;
		background: none;
		border: none;
		color: var(--text-secondary);
		cursor: pointer;
		padding: 4px;
	}

	/* Mobile drawer */
	.mobile-drawer {
		position: absolute;
		top: 56px;
		left: 0;
		right: 0;
		background: var(--bg-surface);
		border-bottom: 1px solid var(--border-subtle);
		padding: 12px;
		display: flex;
		flex-direction: column;
		gap: 2px;
		z-index: 99;
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
	}

	.mobile-link {
		font-size: 14px;
		font-weight: 500;
		color: var(--text-secondary);
		text-decoration: none;
		padding: 10px 14px;
		border-radius: 8px;
		background: none;
		border: none;
		cursor: pointer;
		text-align: left;
		transition: background 0.15s ease, color 0.15s ease;
	}

	.mobile-link:hover,
	.mobile-link.active {
		background: var(--glass-hover);
		color: var(--text-primary);
	}

	@media (max-width: 768px) {
		.center-nav {
			display: none;
		}
		.hamburger {
			display: flex;
		}
	}

	@media (max-width: 480px) {
		.header-inner {
			padding: 0 16px;
		}
	}
</style>
