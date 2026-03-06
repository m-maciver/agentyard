import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { getUser, setUser, signOut as authSignOut, type GitHubUser } from '$lib/auth';

function createAuthStore() {
	const initial = browser ? getUser() : null;
	const { subscribe, set, update } = writable<GitHubUser | null>(initial);

	return {
		subscribe,
		login: (user: GitHubUser) => {
			setUser(user);
			set(user);
		},
		logout: () => {
			authSignOut();
			set(null);
		},
		refresh: () => {
			if (browser) set(getUser());
		},
		// Legacy compat: setUser with token pattern (for real JWT callback)
		setUserFromToken: (user: GitHubUser) => {
			setUser(user);
			set(user);
		}
	};
}

export const authStore = createAuthStore();
export const isLoggedIn = derived(authStore, ($user) => $user !== null);
export const currentUser = derived(authStore, ($user) => $user);

// Legacy export kept for existing components
export { isLoggedIn as isLoggedIn };
