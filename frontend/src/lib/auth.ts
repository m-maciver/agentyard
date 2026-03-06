/**
 * GitHub OAuth auth utilities — frontend only.
 * Backend handles the actual OAuth callback and issues JWTs.
 */

export interface GitHubUser {
	id: string;
	githubUsername: string;
	githubAvatar: string;
	agentName?: string;
	walletBalance?: number; // sats
}

const TOKEN_KEY = 'agentyard-token';
const USER_KEY = 'agentyard-user';

const API_URL = 'https://agentyard-production.up.railway.app';

/**
 * Read the stored user profile from localStorage.
 */
export function getUser(): GitHubUser | null {
	if (typeof localStorage === 'undefined') return null;
	const stored = localStorage.getItem(USER_KEY);
	if (!stored) return null;
	try {
		return JSON.parse(stored);
	} catch {
		return null;
	}
}

/**
 * Store a user profile in localStorage.
 */
export function setUser(user: GitHubUser) {
	if (typeof localStorage === 'undefined') return;
	localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Clear all auth state from localStorage.
 */
export function signOut() {
	if (typeof localStorage === 'undefined') return;
	localStorage.removeItem(TOKEN_KEY);
	localStorage.removeItem(USER_KEY);
}

/**
 * Get the stored JWT token.
 */
export function getToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem(TOKEN_KEY);
}

/**
 * Redirect to GitHub OAuth via the live backend.
 */
export function signInWithGitHub() {
	window.location.href = `${API_URL}/auth/github`;
}

/**
 * Map a raw backend /auth/me response to our GitHubUser shape.
 * Handles both snake_case (real backend) and camelCase (mock).
 */
export function mapBackendUser(raw: Record<string, unknown>): GitHubUser {
	return {
		id: String(raw.id ?? raw.github_id ?? ''),
		githubUsername: String(raw.github_username ?? raw.githubUsername ?? raw.login ?? ''),
		githubAvatar: String(raw.github_avatar_url ?? raw.githubAvatar ?? raw.avatar_url ?? ''),
		agentName: raw.agent_name != null ? String(raw.agent_name) : undefined,
		walletBalance: raw.wallet_balance != null ? Number(raw.wallet_balance) : undefined
	};
}
