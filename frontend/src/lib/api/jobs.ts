import { api } from './client';

export type JobStatus =
	| 'draft'
	| 'awaiting_payment'
	| 'escrowed'
	| 'in_progress'
	| 'delivered'
	| 'disputed'
	| 'complete'
	| 'cancelled';

export interface Job {
	id: string;
	client_agent_id: string;
	provider_agent_id: string;
	status: JobStatus;
	task_description: string;
	task_input: Record<string, unknown>;
	price_sats: number;
	fee_sats: number;
	stake_sats: number;
	client_invoice: string;
	payment_hash: string;
	delivery_channel: string;
	delivery_target: string;
	output_payload?: Record<string, unknown>;
	auto_release_at?: string;
	dispute_reason?: string;
	dispute_resolution?: string;
	created_at: string;
	started_at?: string;
	delivered_at?: string;
	completed_at?: string;
}

export interface CreateJobPayload {
	provider_agent_id: string;
	task_description: string;
	task_input?: Record<string, unknown>;
	delivery_channel: 'webhook' | 'discord' | 'email';
	delivery_target: string;
}

export interface CreateJobResponse {
	job_id: string;
	invoice: string;
	amount_sats: number;
	breakdown: {
		task_price_sats: number;
		platform_fee_sats: number;
	};
	pay_by: string;
	status: JobStatus;
}

export interface JobListResponse {
	jobs: Job[];
	total: number;
}

export interface DeliverJobPayload {
	output: {
		type: string;
		content: string;
		metadata?: Record<string, unknown>;
	};
}

export interface DisputeJobPayload {
	reason: string;
}

export async function createJob(payload: CreateJobPayload): Promise<CreateJobResponse> {
	return api.post<CreateJobResponse>('/jobs', payload);
}

export async function getJob(jobId: string): Promise<Job> {
	return api.get<Job>(`/jobs/${jobId}`);
}

export async function listJobs(): Promise<JobListResponse> {
	return api.get<JobListResponse>('/jobs');
}

export async function deliverJob(jobId: string, payload: DeliverJobPayload, apiKey: string): Promise<Job> {
	return api.post<Job>(`/jobs/${jobId}/deliver`, payload, apiKey);
}

export async function completeJob(jobId: string): Promise<Job> {
	return api.post<Job>(`/jobs/${jobId}/confirm`);
}

export async function disputeJob(jobId: string, payload: DisputeJobPayload): Promise<Job> {
	return api.post<Job>(`/jobs/${jobId}/dispute`, payload);
}
