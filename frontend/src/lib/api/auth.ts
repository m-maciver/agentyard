import { api } from './client';

export interface LoginPayload {
	email: string;
	password: string;
}

export interface RegisterPayload {
	email: string;
	password: string;
}

export interface AuthResponse {
	access_token: string;
	token_type: string;
}

export interface User {
	id: string;
	email: string;
	lnbits_wallet_id?: string;
	created_at: string;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
	return api.post<AuthResponse>('/auth/login', payload);
}

export async function register(payload: RegisterPayload): Promise<User> {
	return api.post<User>('/auth/register', payload);
}

export async function getMe(): Promise<User> {
	return api.get<User>('/auth/me');
}

export async function generateAgentKey(agentId: string): Promise<{ api_key: string }> {
	return api.post<{ api_key: string }>('/auth/agent-key', { agent_id: agentId });
}
