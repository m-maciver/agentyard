import { writable } from 'svelte/store';
import type { Agent } from '$lib/api/agents';

export const agentsStore = writable<{
	agents: Agent[];
	total: number;
	loading: boolean;
	error: string | null;
}>({
	agents: [],
	total: 0,
	loading: false,
	error: null
});

export const selectedAgent = writable<Agent | null>(null);
