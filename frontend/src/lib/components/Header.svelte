<script lang="ts">
	import { page } from '$app/stores';
	import { authStore, isLoggedIn } from '$lib/stores/auth';
	import { theme, toggleTheme } from '$lib/stores/theme';
	import { dev } from '$app/environment';
	import { signInWithGitHub, type GitHubUser } from '$lib/auth';

	let menuOpen = false;
	let userMenuOpen = false;

	$: currentPath = $page.url.pathname;
	$: user = $authStore as GitHubUser | null;

	function handleNavClick() {
		menuOpen = false;
		userMenuOpen = false;
	}

	function handleSignIn() {
		signInWithGitHub();
	}

	function handleSignOut() {
		authStore.logout();
		userMenuOpen = false;
	}

	function setMockLogin() {
		authStore.login({
			id: 'dev-user-001',
			githubUsername: 'm-maciver',
			githubAvatar: 'https://avatars.githubusercontent.com/u/1?v=4',
			agentName: 'Atlas',
			walletBalance: 34500
		});
		userMenuOpen = false;
	}

	function handleOutsideClick(e: MouseEvent) {
		if (userMenuOpen) {
			userMenuOpen = false;
		}
	}
</script>

<svelte:window on:click={handleOutsideClick} />

<header class="header">
	<div class="header-inner">
		<!-- Wordmark -->
		<a href="/" class="wordmark" on:click={handleNavClick}>
			<span class="wordmark-text">AgentYard</span>
			<span class="lightning">⚡</span>
		</a>

		<!-- Center nav (desktop) -->
		<nav class="center-nav">
			<a href="/" class="nav-link" class:active={currentPath === '/'} on:click={handleNavClick}>
				Marketplace
			</a>
			<a href="/how-it-works" class="nav-link" class:active={currentPath === '/how-it-works'} on:click={handleNavClick}>
				How It Works
			</a>
			<a href="/docs" class="nav-link" class:active={currentPath === '/docs'} on:click={handleNavClick}>
				Docs
			</a>
		</nav>

		<!-- Right actions -->
		<div class="header-right">
			<!-- Theme toggle -->
			<button class="theme-toggle" on:click|stopPropagation={toggleTheme} aria-label="Toggle theme" title="Toggle light/dark mode">
				{#if $theme === 'dark'}
					<!-- Sun icon -->
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
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
					<!-- Moon icon -->
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
						<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
					</svg>
				{/if}
			</button>

			{#if $isLoggedIn && user}
				<!-- User menu -->
				<div class="user-menu-wrap">
					<button
						class="user-btn"
						on:click|stopPropagation={() => (userMenuOpen = !userMenuOpen)}
						aria-label="User menu"
					>
						{#if user.githubAvatar}
							<img src={user.githubAvatar} alt={user.githubUsername} class="avatar-img" />
						{:else}
							<div class="avatar-fallback">{user.githubUsername[0].toUpperCase()}</div>
						{/if}
						<span class="username">@{user.githubUsername}</span>
						<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5">
							<path d="M2 4l4 4 4-4" stroke-linecap="round"/>
						</svg>
					</button>

					{#if userMenuOpen}
						<div class="user-dropdown glass-card" role="menu" on:click|stopPropagation={() => {}} on:keydown={() => {}}>
							{#if user.walletBalance !== undefined}
								<div class="wallet-balance-row">
									<span class="wallet-label">Balance</span>
									<span class="wallet-amount">⚡ {user.walletBalance.toLocaleString()} sats</span>
								</div>
								<div class="dropdown-divider"></div>
							{/if}
							<a href="/dashboard" class="dropdown-item" on:click={handleNavClick}>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
								My Dashboard
							</a>
							<a href="/dashboard/listings" class="dropdown-item" on:click={handleNavClick}>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
								My Listings
							</a>
							<a href="/dashboard/wallet" class="dropdown-item" on:click={handleNavClick}>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 12V8H6a2 2 0 01-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12c-1.1 0-2 .9-2 2s.9 2 2 2h4v-4h-4z"/></svg>
								Wallet
							</a>
							<div class="dropdown-divider"></div>
							<button class="dropdown-item dropdown-signout" on:click={handleSignOut}>
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/></svg>
								Sign out
							</button>
						</div>
					{/if}
				</div>
			{:else}
				<!-- Connect GitHub -->
				<button class="connect-btn" on:click={handleSignIn}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
						<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
					</svg>
					Connect GitHub
				</button>

				{#if dev}
					<button class="dev-login-btn" on:click={setMockLogin} title="Dev login">
						Dev Login
					</button>
				{/if}
			{/if}

			<!-- Mobile hamburger -->
			<button class="hamburger" on:click|stopPropagation={() => (menuOpen = !menuOpen)} aria-label="Menu">
				{#if menuOpen}
					<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
				{:else}
					<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
				{/if}
			</button>
		</div>
	</div>

	<!-- Mobile drawer -->
	{#if menuOpen}
		<div class="mobile-drawer">
			<a href="/" class="mobile-nav-link" class:active={currentPath === '/'} on:click={handleNavClick}>Marketplace</a>
			<a href="/how-it-works" class="mobile-nav-link" on:click={handleNavClick}>How It Works</a>
			<a href="/docs" class="mobile-nav-link" on:click={handleNavClick}>Docs</a>
			{#if $isLoggedIn}
				<div class="mobile-divider"></div>
				<a href="/dashboard" class="mobile-nav-link" on:click={handleNavClick}>Dashboard</a>
				<a href="/dashboard/listings" class="mobile-nav-link" on:click={handleNavClick}>My Listings</a>
				<a href="/dashboard/wallet" class="mobile-nav-link" on:click={handleNavClick}>Wallet</a>
				<button class="mobile-nav-link mobile-signout" on:click={handleSignOut}>Sign out</button>
			{:else}
				<div class="mobile-divider"></div>
				<button class="mobile-connect-btn" on:click={() => { handleNavClick(); handleSignIn(); }}>
					⚡ Connect GitHub
				</button>
				{#if dev}
					<button class="mobile-nav-link" on:click={() => { handleNavClick(); setMockLogin(); }}>
						Dev Login
					</button>
				{/if}
			{/if}
		</div>
	{/if}
</header>

<style>
	.header {
		position: sticky;
		top: 0;
		z-index: 100;
		height: 60px;
		background: var(--glass-bg);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		border-bottom: 1px solid var(--glass-border);
	}

	.header-inner {
		max-width: 1200px;
		margin: 0 auto;
		height: 100%;
		padding: 0 24px;
		display: flex;
		align-items: center;
		gap: 24px;
	}

	/* Wordmark */
	.wordmark {
		display: flex;
		align-items: center;
		gap: 6px;
		text-decoration: none;
		flex-shrink: 0;
	}

	.wordmark-text {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 700;
		font-size: 18px;
		color: var(--text-primary);
		letter-spacing: -0.01em;
	}

	.lightning {
		font-size: 16px;
		line-height: 1;
	}

	/* Center nav */
	.center-nav {
		display: flex;
		align-items: center;
		gap: 8px;
		flex: 1;
		justify-content: center;
	}

	.nav-link {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 500;
		font-size: 14px;
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
		color: var(--accent-primary);
	}

	/* Right section */
	.header-right {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-shrink: 0;
	}

	/* Theme toggle */
	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: transparent;
		border: 1px solid var(--glass-border);
		border-radius: 8px;
		color: var(--text-secondary);
		cursor: pointer;
		transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
	}

	.theme-toggle:hover {
		color: var(--text-primary);
		border-color: var(--border-strong);
		background: var(--glass-hover);
	}

	/* Connect button — purple CTA */
	.connect-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		background: var(--accent-primary);
		color: #ffffff;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 13px;
		padding: 8px 18px;
		border: none;
		border-radius: 9999px;
		cursor: pointer;
		transition: opacity 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
		white-space: nowrap;
		letter-spacing: 0.01em;
	}

	.connect-btn:hover {
		opacity: 0.9;
		transform: translateY(-1px);
		box-shadow: 0 4px 16px var(--accent-glow);
	}

	/* Dev login button */
	.dev-login-btn {
		background: rgba(59, 130, 246, 0.15);
		color: #3b82f6;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 500;
		font-size: 12px;
		padding: 6px 12px;
		border: 1px solid rgba(59, 130, 246, 0.3);
		border-radius: 6px;
		cursor: pointer;
		transition: opacity 0.15s ease;
	}

	.dev-login-btn:hover {
		opacity: 0.8;
	}

	/* User menu */
	.user-menu-wrap {
		position: relative;
	}

	.user-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		background: var(--glass-bg);
		border: 1px solid var(--glass-border);
		border-radius: 9999px;
		padding: 4px 12px 4px 4px;
		cursor: pointer;
		color: var(--text-secondary);
		transition: border-color 0.15s ease, background 0.15s ease;
	}

	.user-btn:hover {
		border-color: var(--border-strong);
		background: var(--glass-hover);
		color: var(--text-primary);
	}

	.avatar-img {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		object-fit: cover;
	}

	.avatar-fallback {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--accent-primary);
		color: #ffffff;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 700;
		font-size: 12px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.username {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 500;
		font-size: 13px;
	}

	/* Dropdown */
	.user-dropdown {
		position: absolute;
		top: calc(100% + 8px);
		right: 0;
		min-width: 200px;
		padding: 8px;
		z-index: 200;
		display: flex;
		flex-direction: column;
		gap: 2px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
	}

	.wallet-balance-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8px 12px;
	}

	.wallet-label {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-size: 12px;
		color: var(--text-muted);
	}

	.wallet-amount {
		font-family: var(--font-mono, monospace);
		font-size: 13px;
		color: var(--sats-color);
		font-weight: 500;
	}

	.dropdown-divider {
		height: 1px;
		background: var(--glass-border);
		margin: 4px 0;
	}

	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 8px 12px;
		border-radius: 8px;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-size: 14px;
		color: var(--text-secondary);
		text-decoration: none;
		background: none;
		border: none;
		cursor: pointer;
		width: 100%;
		text-align: left;
		transition: background 0.1s ease, color 0.1s ease;
	}

	.dropdown-item:hover {
		background: var(--glass-hover);
		color: var(--text-primary);
	}

	.dropdown-signout {
		color: var(--destructive) !important;
	}

	.dropdown-signout:hover {
		background: rgba(239, 68, 68, 0.1) !important;
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
		top: 60px;
		left: 0;
		right: 0;
		background: var(--bg-surface);
		border-bottom: 1px solid var(--glass-border);
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 4px;
		z-index: 99;
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
	}

	.mobile-nav-link {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-size: 15px;
		font-weight: 500;
		color: var(--text-secondary);
		text-decoration: none;
		padding: 12px 16px;
		border-radius: 10px;
		background: none;
		border: none;
		cursor: pointer;
		text-align: left;
		transition: background 0.15s ease, color 0.15s ease;
	}

	.mobile-nav-link:hover,
	.mobile-nav-link.active {
		background: var(--glass-hover);
		color: var(--text-primary);
	}

	.mobile-nav-link.active {
		color: var(--accent-primary);
	}

	.mobile-signout {
		color: var(--destructive) !important;
	}

	.mobile-divider {
		height: 1px;
		background: var(--glass-border);
		margin: 8px 0;
	}

	.mobile-connect-btn {
		background: var(--accent-primary);
		color: #ffffff;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 15px;
		padding: 12px 16px;
		border: none;
		border-radius: 10px;
		cursor: pointer;
		text-align: center;
		margin-top: 4px;
	}

	@media (max-width: 768px) {
		.center-nav {
			display: none;
		}
		.hamburger {
			display: flex;
		}
		.connect-btn {
			display: none;
		}
		.dev-login-btn {
			display: none;
		}
		.username {
			display: none;
		}
	}

	@media (max-width: 480px) {
		.header-inner {
			padding: 0 16px;
		}
	}
</style>
