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

/**
 * Decode JWT payload and extract user (no signature verification — client side only).
 */
export function getUser(): GitHubUser | null {
	if (typeof localStorage === 'undefined') return null;
	const token = localStorage.getItem(TOKEN_KEY);
	if (!token) return null;
	try {
		const parts = token.split('.');
		if (parts.length < 2) return null;
		const payload = JSON.parse(atob(parts[1]));
		return payload.user ?? null;
	} catch {
		return null;
	}
}

export function setUser(user: GitHubUser) {
	if (typeof localStorage === 'undefined') return;
	// Create a minimal fake JWT for dev login
	const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
	const payload = btoa(JSON.stringify({ user, iat: Date.now() }));
	const fakeToken = `${header}.${payload}.dev-signature`;
	localStorage.setItem(TOKEN_KEY, fakeToken);
}

export function signOut() {
	if (typeof localStorage !== 'undefined') {
		localStorage.removeItem(TOKEN_KEY);
	}
}

export function getToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem(TOKEN_KEY);
}
