import { writable } from 'svelte/store';
import type { Job } from '$lib/api/jobs';

export const jobsStore = writable<{
	jobs: Job[];
	loading: boolean;
	error: string | null;
}>({
	jobs: [],
	loading: false,
	error: null
});

export const activeJob = writable<Job | null>(null);
