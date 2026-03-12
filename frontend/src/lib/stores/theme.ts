import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'dark' | 'light';

const stored: Theme =
	browser && localStorage.getItem('agentyard-theme') === 'dark' ? 'dark' : 'light';

export const theme = writable<Theme>(stored);

export function toggleTheme() {
	theme.update((current) => {
		const next: Theme = current === 'dark' ? 'light' : 'dark';
		if (browser) {
			localStorage.setItem('agentyard-theme', next);
			if (next === 'dark') {
				document.documentElement.classList.add('dark');
			} else {
				document.documentElement.classList.remove('dark');
			}
		}
		return next;
	});
}
