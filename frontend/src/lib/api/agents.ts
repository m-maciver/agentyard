import { api } from './client';

export interface Agent {
	id: string;
	name: string;
	specialty: string;
	soul_excerpt: string;
	skills_config: Record<string, unknown>;
	price_per_task_sats: number;
	sample_outputs: string[];
	owner_id: string;
	lnbits_wallet_id: string;
	webhook_url: string;
	is_active: boolean;
	is_verified: boolean;
	job_count: number;
	jobs_completed: number;
	jobs_disputed: number;
	jobs_won: number;
	reputation_score: number;
	stake_percent: number;
	max_job_sats: number;
	created_at: string;
	updated_at: string;
}

export interface AgentListResponse {
	agents: Agent[];
	total: number;
	page: number;
}

export interface AgentListParams {
	specialty?: string;
	price_max_sats?: number;
	reputation_min?: number;
	available?: boolean;
	page?: number;
	page_size?: number;
}

export interface CreateAgentPayload {
	name: string;
	specialty: string;
	soul_excerpt: string;
	price_per_task_sats: number;
	webhook_url: string;
	lnbits_wallet_id: string;
	lnbits_invoice_key?: string;
	skills_config?: Record<string, unknown>;
	sample_outputs?: string[];
}

export async function listAgents(params?: AgentListParams): Promise<AgentListResponse> {
	const queryParams: Record<string, string | number | boolean> = {};
	if (params?.specialty) queryParams.specialty = params.specialty;
	if (params?.price_max_sats !== undefined) queryParams.price_max_sats = params.price_max_sats;
	if (params?.reputation_min !== undefined) queryParams.reputation_min = params.reputation_min;
	if (params?.available !== undefined) queryParams.available = params.available;
	if (params?.page !== undefined) queryParams.page = params.page;
	if (params?.page_size !== undefined) queryParams.page_size = params.page_size;
	return api.get<AgentListResponse>('/agents', queryParams);
}

export async function getAgent(agentId: string): Promise<Agent> {
	return api.get<Agent>(`/agents/${agentId}`);
}

export async function createAgent(payload: CreateAgentPayload): Promise<Agent & { api_key: string }> {
	return api.post<Agent & { api_key: string }>('/agents', payload);
}

export async function updateAgent(agentId: string, payload: Partial<CreateAgentPayload>, apiKey: string): Promise<Agent> {
	return api.put<Agent>(`/agents/${agentId}`, payload, apiKey);
}
