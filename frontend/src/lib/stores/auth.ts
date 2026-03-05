import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/api/auth';

function createAuthStore() {
	const { subscribe, set, update } = writable<{
		user: User | null;
		token: string | null;
		loading: boolean;
	}>({
		user: null,
		token: browser ? localStorage.getItem('ay_token') : null,
		loading: false
	});

	return {
		subscribe,
		setUser: (user: User, token: string) => {
			if (browser) localStorage.setItem('ay_token', token);
			set({ user, token, loading: false });
		},
		logout: () => {
			if (browser) localStorage.removeItem('ay_token');
			set({ user: null, token: null, loading: false });
		},
		setLoading: (loading: boolean) => update(s => ({ ...s, loading })),
		setToken: (token: string) => {
			if (browser) localStorage.setItem('ay_token', token);
			update(s => ({ ...s, token }));
		}
	};
}

export const authStore = createAuthStore();
export const isLoggedIn = derived(authStore, $auth => !!$auth.token);
export const currentUser = derived(authStore, $auth => $auth.user);
