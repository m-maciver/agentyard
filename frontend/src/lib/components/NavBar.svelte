<script lang="ts">
	import { page } from '$app/stores';
	import { isLoggedIn } from '$lib/stores/auth';

	export let walletBalance: number | null = null;
	export let isAdmin: boolean = false;

	let menuOpen = false;

	$: currentPath = $page.url.pathname;
</script>

<nav class="navbar">
	<div class="nav-inner">
		<!-- Logo -->
		<a href="/" class="logo">
			<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
				<polygon points="14,2 25,8 25,20 14,26 3,20 3,8" fill="#F7931A"/>
				<path d="M15 7l-6 8h5l-1 6 7-9h-5l1-5z" fill="white" stroke="white" stroke-width="0.5" stroke-linejoin="round"/>
			</svg>
			<span class="wordmark">
				<span style="font-weight: 400;">agent</span><span style="font-weight: 700;">Yard</span>
			</span>
		</a>

		<!-- Desktop nav links -->
		<div class="nav-links">
			<a href="/" class="nav-link" class:active={currentPath === '/'}>Marketplace</a>
			{#if $isLoggedIn}
				<a href="/dashboard" class="nav-link" class:active={currentPath === '/dashboard'}>Dashboard</a>
			{/if}
			{#if isAdmin}
				<a href="/admin" class="nav-link admin-link" class:active={currentPath === '/admin'}>Admin</a>
			{/if}
		</div>

		<!-- Right section -->
		<div class="nav-right">
			{#if walletBalance !== null && $isLoggedIn}
				<a href="/dashboard" class="wallet-balance">
					⚡ <span class="balance-amount">{walletBalance.toLocaleString()} sats</span>
				</a>
			{/if}

			{#if $isLoggedIn}
				<a href="/dashboard" class="auth-btn avatar-btn">
					<div class="user-avatar">J</div>
					<svg width="12" height="12" viewBox="0 0 12 12" fill="var(--muted-foreground)">
						<path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>
					</svg>
				</a>
			{:else}
				<a href="/dashboard" class="auth-btn connect-btn">Connect</a>
			{/if}

			<!-- Mobile hamburger -->
			<button class="hamburger" on:click={() => (menuOpen = !menuOpen)} aria-label="Menu">
				<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--foreground)" stroke-width="2" stroke-linecap="round">
					{#if menuOpen}
						<path d="M18 6L6 18M6 6l12 12"/>
					{:else}
						<path d="M3 12h18M3 6h18M3 18h18"/>
					{/if}
				</svg>
			</button>
		</div>
	</div>

	<!-- Mobile menu drawer -->
	{#if menuOpen}
		<div class="mobile-menu">
			<a href="/" class="mobile-link" class:mobile-active={currentPath === '/'} on:click={() => (menuOpen = false)}>Marketplace</a>
			{#if $isLoggedIn}
				<a href="/dashboard" class="mobile-link" class:mobile-active={currentPath === '/dashboard'} on:click={() => (menuOpen = false)}>Dashboard</a>
			{/if}
			{#if isAdmin}
				<a href="/admin" class="mobile-link mobile-admin" class:mobile-active={currentPath === '/admin'} on:click={() => (menuOpen = false)}>Admin</a>
			{/if}
			{#if !$isLoggedIn}
				<a href="/dashboard" class="mobile-link" on:click={() => (menuOpen = false)}>Connect</a>
			{/if}
		</div>
	{/if}
</nav>

<style>
	.navbar {
		position: sticky;
		top: 0;
		z-index: 100;
		height: 56px;
		background: rgba(17, 17, 24, 0.85);
		backdrop-filter: blur(12px);
		border-bottom: 1px solid var(--border);
	}

	.nav-inner {
		max-width: 1200px;
		margin: 0 auto;
		height: 100%;
		padding: 0 24px;
		display: flex;
		align-items: center;
		gap: 32px;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 10px;
		text-decoration: none;
		color: var(--foreground);
		flex-shrink: 0;
	}

	.wordmark {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 18px;
		color: var(--foreground);
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: 32px;
		flex: 1;
	}

	.nav-link {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 14px;
		color: var(--muted-foreground);
		text-decoration: none;
		transition: color 150ms ease-out;
	}

	.nav-link:hover { color: var(--foreground); }
	.nav-link.active { color: var(--primary); }

	.admin-link {
		padding: 4px 8px;
		border-radius: 9999px;
		background: rgba(239, 68, 68, 0.15);
		color: var(--destructive) !important;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.05em;
	}

	.nav-right {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-left: auto;
	}

	.wallet-balance {
		font-family: 'JetBrains Mono', monospace;
		font-weight: 500;
		font-size: 14px;
		color: var(--foreground);
		text-decoration: none;
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.balance-amount {
		font-family: 'JetBrains Mono', monospace;
	}

	.auth-btn {
		text-decoration: none;
		transition: all 150ms ease-out;
	}

	.connect-btn {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 14px;
		color: var(--foreground);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 8px 16px;
	}

	.connect-btn:hover {
		border-color: var(--border-strong);
		background: var(--surface-2);
	}

	.avatar-btn {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.user-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: var(--primary);
		color: var(--primary-foreground);
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 13px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.hamburger {
		display: none;
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px;
	}

	.mobile-menu {
		display: none;
		position: absolute;
		top: 56px;
		left: 0;
		right: 0;
		background: var(--surface-1);
		border-bottom: 1px solid var(--border);
		padding: 16px 24px;
		flex-direction: column;
		gap: 16px;
		z-index: 99;
	}

	.mobile-link {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 15px;
		color: var(--foreground);
		text-decoration: none;
		padding: 8px 0;
		border-bottom: 1px solid var(--border);
	}

	.mobile-link.mobile-active {
		color: var(--primary);
	}

	.mobile-link.mobile-admin {
		color: var(--destructive);
	}

	@media (max-width: 768px) {
		.nav-links { display: none; }
		.hamburger { display: flex; }
		.mobile-menu { display: flex; }
		.wallet-balance { display: none; }
	}
</style>
