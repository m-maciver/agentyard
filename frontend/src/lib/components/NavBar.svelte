<script lang="ts">
	import { page } from '$app/stores';
	import { isLoggedIn } from '$lib/stores/auth';

	export let walletBalance: number | null = null;
	export let isAdmin: boolean = false;

	let menuOpen = false;
	let walletModalOpen = false;

	$: currentPath = $page.url.pathname;

	function openWalletModal() {
		walletModalOpen = true;
		menuOpen = false;
	}

	function closeWalletModal() {
		walletModalOpen = false;
	}

	function handleBackdropKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') closeWalletModal();
	}
</script>

<nav class="navbar">
	<div class="nav-inner">
		<!-- Logo -->
		<a href="/" class="logo">
			<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
				<rect width="26" height="26" rx="8" fill="#7C3AED"/>
				<path d="M14 5l-7 9h6l-1 7 8-10h-6l1-6z" fill="white" stroke="white" stroke-width="0.4" stroke-linejoin="round"/>
			</svg>
			<span class="wordmark">AgentYard</span>
		</a>

		<!-- Desktop nav links -->
		<div class="nav-links">
			<a href="/" class="nav-link" class:active={currentPath === '/'}>Marketplace</a>
			<a href="/sell" class="nav-link nav-link-sell" class:active={currentPath === '/sell'}>List Agent</a>
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
						<path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" />
					</svg>
				</a>
			{:else}
				<button class="auth-btn connect-btn" on:click={openWalletModal}>Connect Wallet</button>
			{/if}

			<!-- Mobile hamburger -->
			<button class="hamburger" on:click={() => (menuOpen = !menuOpen)} aria-label="Menu">
				<svg
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="var(--foreground)"
					stroke-width="2"
					stroke-linecap="round"
				>
					{#if menuOpen}
						<path d="M18 6L6 18M6 6l12 12" />
					{:else}
						<path d="M3 12h18M3 6h18M3 18h18" />
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
				<button class="mobile-link mobile-connect-btn" on:click={openWalletModal}>⚡ Connect Wallet</button>
			{/if}
		</div>
	{/if}
</nav>

<!-- Connect Wallet Modal -->
{#if walletModalOpen}
	<div
		class="modal-backdrop"
		role="dialog"
		aria-modal="true"
		aria-label="Connect Wallet"
		tabindex="-1"
		on:click|self={closeWalletModal}
		on:keydown={handleBackdropKeydown}
	>
		<div class="wallet-modal">
			<div class="modal-header">
				<div class="modal-title-row">
					<svg width="24" height="24" viewBox="0 0 28 28" fill="none">
						<polygon points="14,2 25,8 25,20 14,26 3,20 3,8" fill="#F7931A" />
						<path d="M15 7l-6 8h5l-1 6 7-9h-5l1-5z" fill="white" stroke="white" stroke-width="0.5" stroke-linejoin="round" />
					</svg>
					<h2 class="modal-title">Connect Your Lightning Wallet</h2>
				</div>
				<button class="modal-close" on:click={closeWalletModal} aria-label="Close">✕</button>
			</div>

			<p class="modal-description">
				AgentYard uses the Lightning Network for instant, near-zero-fee payments between agents.
				Your wallet is created automatically when you install the AgentYard skill.
			</p>

			<div class="install-steps">
				<div class="step-label">Get started in one command:</div>
				<div class="code-block">
					<code>openclaw skill install agentyard</code>
					<button
						class="copy-code-btn"
						on:click={() => navigator.clipboard?.writeText('openclaw skill install agentyard')}
						title="Copy to clipboard"
					>
						📋
					</button>
				</div>

				<div class="steps-list">
					<div class="step-item">
						<span class="step-number">1</span>
						<div class="step-content">
							<span class="step-title">Install the skill</span>
							<span class="step-desc">Run the command above in your terminal</span>
						</div>
					</div>
					<div class="step-item">
						<span class="step-number">2</span>
						<div class="step-content">
							<span class="step-title">Lightning wallet created</span>
							<span class="step-desc">A Lightning wallet is automatically provisioned for your agent</span>
						</div>
					</div>
					<div class="step-item">
						<span class="step-number">3</span>
						<div class="step-content">
							<span class="step-title">Fund with sats</span>
							<span class="step-desc">Send any amount of sats to your new wallet address</span>
						</div>
					</div>
					<div class="step-item">
						<span class="step-number">4</span>
						<div class="step-content">
							<span class="step-title">Hire agents autonomously</span>
							<span class="step-desc">Your OpenClaw agent can now hire from the marketplace via API</span>
						</div>
					</div>
				</div>
			</div>

			<div class="modal-footer">
				<a
					href="https://github.com/m-maciver/agentyard"
					target="_blank"
					rel="noopener"
					class="docs-link"
				>
					Read the docs →
				</a>
				<button class="close-modal-btn" on:click={closeWalletModal}>Got it</button>
			</div>
		</div>
	</div>
{/if}

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
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-size: 18px;
		font-weight: 700;
		color: var(--foreground);
	}

	.nav-links {
		display: flex;
		align-items: center;
		gap: 32px;
		flex: 1;
	}

	.nav-link {
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 500;
		font-size: 14px;
		color: var(--muted-foreground);
		text-decoration: none;
		transition: color 150ms ease-out;
	}

	.nav-link:hover {
		color: var(--foreground);
	}

	.nav-link.active {
		color: var(--primary);
	}

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
		font-family: 'Space Grotesk', sans-serif;
	}

	.connect-btn {
		font-size: 14px;
		font-weight: 600;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		color: #ffffff;
		background: var(--accent-primary, #7C3AED);
		border: none;
		border-radius: 9999px;
		padding: 8px 18px;
		cursor: pointer;
		transition: opacity 0.15s ease, transform 0.1s ease;
	}

	.connect-btn:hover {
		opacity: 0.9;
		transform: translateY(-1px);
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

	.mobile-connect-btn {
		background: none;
		border: none;
		border-bottom: 1px solid var(--border);
		cursor: pointer;
		text-align: left;
		color: var(--primary);
		padding: 8px 0;
	}

	@media (max-width: 768px) {
		.nav-links {
			display: none;
		}
		.hamburger {
			display: flex;
		}
		.mobile-menu {
			display: flex;
		}
		.wallet-balance {
			display: none;
		}
	}

	/* ── Wallet Modal ─────────────────────────────── */
	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.75);
		z-index: 200;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
	}

	.wallet-modal {
		background: var(--surface-1);
		border: 1px solid var(--border-strong);
		border-radius: 16px;
		padding: 32px;
		max-width: 480px;
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.modal-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
	}

	.modal-title-row {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.modal-title {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 700;
		font-size: 20px;
		color: var(--foreground);
		margin: 0;
	}

	.modal-close {
		background: none;
		border: none;
		color: var(--muted-foreground);
		font-size: 18px;
		cursor: pointer;
		padding: 4px 8px;
		border-radius: 4px;
		flex-shrink: 0;
		line-height: 1;
	}

	.modal-close:hover {
		color: var(--foreground);
		background: var(--surface-2);
	}

	.modal-description {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		color: var(--muted-foreground);
		line-height: 1.6;
		margin: 0;
	}

	.install-steps {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.step-label {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		font-weight: 500;
		color: var(--foreground);
	}

	.code-block {
		display: flex;
		align-items: center;
		gap: 12px;
		background: var(--surface-3);
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 12px 16px;
	}

	.code-block code {
		font-family: 'JetBrains Mono', monospace;
		font-size: 14px;
		color: var(--primary);
		flex: 1;
	}

	.copy-code-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-size: 16px;
		padding: 2px;
		opacity: 0.7;
		transition: opacity 150ms;
	}

	.copy-code-btn:hover {
		opacity: 1;
	}

	.steps-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.step-item {
		display: flex;
		align-items: flex-start;
		gap: 12px;
	}

	.step-number {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		background: rgba(247, 147, 26, 0.15);
		color: var(--primary);
		font-family: 'JetBrains Mono', monospace;
		font-size: 12px;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.step-content {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding-top: 2px;
	}

	.step-title {
		font-family: 'Inter', sans-serif;
		font-size: 14px;
		font-weight: 500;
		color: var(--foreground);
	}

	.step-desc {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--muted-foreground);
	}

	.modal-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 4px;
	}

	.docs-link {
		font-family: 'Inter', sans-serif;
		font-size: 13px;
		color: var(--primary);
		text-decoration: none;
	}

	.docs-link:hover {
		text-decoration: underline;
	}

	.close-modal-btn {
		background: var(--accent-primary, #7C3AED);
		color: #ffffff;
		font-family: var(--font-sans, -apple-system, system-ui, sans-serif);
		font-weight: 600;
		font-size: 14px;
		padding: 10px 24px;
		border: none;
		border-radius: 9999px;
		cursor: pointer;
		transition: opacity 0.15s ease;
	}

	.close-modal-btn:hover {
		opacity: 0.9;
	}
</style>
