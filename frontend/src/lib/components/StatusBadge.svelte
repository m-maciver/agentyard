<script lang="ts">
	import type { JobStatus } from '$lib/api/jobs';

	export let status: JobStatus;

	const config: Record<JobStatus, { label: string; bg: string; color: string; dot: string }> = {
		draft: { label: 'DRAFT', bg: 'rgba(107,107,138,0.12)', color: '#6b6b8a', dot: '#6b6b8a' },
		awaiting_payment: { label: 'PENDING', bg: 'rgba(247,147,26,0.12)', color: '#F7931A', dot: '#F7931A' },
		escrowed: { label: 'PENDING', bg: 'rgba(247,147,26,0.12)', color: '#F7931A', dot: '#F7931A' },
		in_progress: { label: 'ACTIVE', bg: 'rgba(59,130,246,0.12)', color: '#3b82f6', dot: '#3b82f6' },
		delivered: { label: 'DELIVERED', bg: 'rgba(168,85,247,0.12)', color: '#a855f7', dot: '#a855f7' },
		disputed: { label: 'DISPUTED', bg: 'rgba(239,68,68,0.12)', color: '#ef4444', dot: '#ef4444' },
		complete: { label: 'COMPLETE', bg: 'rgba(34,197,94,0.12)', color: '#22c55e', dot: '#22c55e' },
		cancelled: { label: 'CANCELLED', bg: 'rgba(107,107,138,0.12)', color: '#6b6b8a', dot: '#6b6b8a' }
	};

	$: cfg = config[status] ?? config.draft;
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide"
	style="background: {cfg.bg}; color: {cfg.color}; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;"
>
	<span
		class="block rounded-full"
		class:pulse-dot={status === 'in_progress'}
		style="width: 6px; height: 6px; background: {cfg.dot}; border-radius: 50%;"
	></span>
	{cfg.label}
</span>
