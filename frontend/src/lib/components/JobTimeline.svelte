<script lang="ts">
	import type { Job, JobStatus } from '$lib/api/jobs';
	import { formatDateTime } from '$lib/utils/format';

	export let job: Job;

	type Step = {
		key: string;
		label: string;
		timestamp?: string;
	};

	const baseSteps: Step[] = [
		{ key: 'created', label: 'Created', timestamp: job.created_at },
		{ key: 'paid', label: 'Paid', timestamp: job.status !== 'draft' && job.status !== 'awaiting_payment' ? job.created_at : undefined },
		{ key: 'delivered', label: 'Delivered', timestamp: job.delivered_at },
		{ key: 'complete', label: 'Complete', timestamp: job.completed_at }
	];

	const statusOrder: Record<string, number> = {
		draft: 0,
		awaiting_payment: 0,
		escrowed: 1,
		in_progress: 1,
		delivered: 2,
		disputed: 2,
		complete: 3,
		cancelled: 3
	};

	$: currentStep = statusOrder[job.status] ?? 0;
	$: isDisputed = job.status === 'disputed';
</script>

<div class="timeline">
	{#each baseSteps as step, i}
		<div class="step-wrapper">
			<!-- Node -->
			<div
				class="node"
				class:past={i < currentStep}
				class:current={i === currentStep && !isDisputed}
				class:future={i > currentStep}
			>
				{#if i < currentStep}
					<svg width="12" height="12" viewBox="0 0 12 12" fill="white">
						<path d="M2 6l3 3 5-5" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round"/>
					</svg>
				{:else if i === currentStep}
					<div class="current-dot"></div>
				{/if}
			</div>

			<!-- Connector -->
			{#if i < baseSteps.length - 1}
				<div class="connector" class:filled={i < currentStep}></div>
			{/if}

			<!-- Labels -->
			<div class="step-labels">
				<span class="step-label" class:active={i <= currentStep}>{step.label}</span>
				{#if step.timestamp && i <= currentStep}
					<span class="step-time">{formatDateTime(step.timestamp)}</span>
				{/if}
			</div>
		</div>
	{/each}

	{#if isDisputed}
		<div class="disputed-branch">
			<div class="dispute-line"></div>
			<div class="dispute-node">
				<span class="dispute-label">Disputed</span>
				{#if job.dispute_reason}
					<span class="dispute-reason">"{job.dispute_reason.slice(0, 80)}..."</span>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.timeline {
		display: flex;
		align-items: flex-start;
		gap: 0;
		position: relative;
		padding: 16px 0;
		overflow-x: auto;
	}

	.step-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
		flex: 1;
		position: relative;
	}

	.node {
		width: 24px;
		height: 24px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		z-index: 1;
	}

	.node.past {
		background: var(--primary);
	}

	.node.current {
		background: rgba(247, 147, 26, 0.3);
		border: 2px solid var(--primary);
	}

	.node.future {
		background: var(--surface-2);
		border: 2px solid var(--border-strong);
	}

	.current-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--primary);
	}

	.connector {
		position: absolute;
		top: 12px;
		left: 50%;
		width: 100%;
		height: 1px;
		background: var(--border-strong);
		z-index: 0;
	}

	.connector.filled {
		background: var(--primary);
		height: 2px;
		top: 11px;
	}

	.step-labels {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
		margin-top: 8px;
	}

	.step-label {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 500;
		font-size: 12px;
		color: var(--muted-foreground);
	}

	.step-label.active {
		color: var(--foreground);
	}

	.step-time {
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		color: var(--muted-foreground);
		text-align: center;
	}

	.disputed-branch {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-left: 16px;
	}

	.dispute-line {
		width: 2px;
		height: 24px;
		background: var(--destructive);
	}

	.dispute-node {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--destructive);
		border-radius: 8px;
		padding: 8px 12px;
	}

	.dispute-label {
		font-family: 'Space Grotesk', sans-serif;
		font-weight: 600;
		font-size: 12px;
		color: var(--destructive);
	}

	.dispute-reason {
		font-family: 'Inter', sans-serif;
		font-size: 11px;
		color: var(--muted-foreground);
		text-align: center;
	}
</style>
