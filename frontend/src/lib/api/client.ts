import { PUBLIC_API_URL } from '$env/static/public';
import { browser } from '$app/environment';

const BASE_URL = PUBLIC_API_URL ?? 'http://localhost:8000';

function getToken(): string | null {
	if (!browser) return null;
	return localStorage.getItem('agentyard-token');
}

export interface ApiError {
	status: number;
	message: string;
	detail?: string;
}

export class ApiClient {
	private baseUrl: string;

	constructor(baseUrl = BASE_URL) {
		this.baseUrl = baseUrl;
	}

	private buildHeaders(extra: Record<string, string> = {}): Record<string, string> {
		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
			...extra
		};
		const token = getToken();
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		return headers;
	}

	private buildAgentHeaders(apiKey: string, extra: Record<string, string> = {}): Record<string, string> {
		return {
			'Content-Type': 'application/json',
			'X-Agent-Key': apiKey,
			...extra
		};
	}

	async get<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
		const url = new URL(`${this.baseUrl}${path}`);
		if (params) {
			Object.entries(params).forEach(([k, v]) => {
				if (v !== undefined && v !== null) {
					url.searchParams.set(k, String(v));
				}
			});
		}
		const response = await fetch(url.toString(), {
			method: 'GET',
			headers: this.buildHeaders()
		});
		return this.handleResponse<T>(response);
	}

	async post<T>(path: string, body?: unknown, apiKey?: string): Promise<T> {
		const headers = apiKey ? this.buildAgentHeaders(apiKey) : this.buildHeaders();
		const response = await fetch(`${this.baseUrl}${path}`, {
			method: 'POST',
			headers,
			body: body ? JSON.stringify(body) : undefined
		});
		return this.handleResponse<T>(response);
	}

	async put<T>(path: string, body?: unknown, apiKey?: string): Promise<T> {
		const headers = apiKey ? this.buildAgentHeaders(apiKey) : this.buildHeaders();
		const response = await fetch(`${this.baseUrl}${path}`, {
			method: 'PUT',
			headers,
			body: body ? JSON.stringify(body) : undefined
		});
		return this.handleResponse<T>(response);
	}

	async delete<T>(path: string): Promise<T> {
		const response = await fetch(`${this.baseUrl}${path}`, {
			method: 'DELETE',
			headers: this.buildHeaders()
		});
		return this.handleResponse<T>(response);
	}

	private async handleResponse<T>(response: Response): Promise<T> {
		if (!response.ok) {
			let message = `HTTP ${response.status}`;
			try {
				const data = await response.json();
				message = data.detail ?? data.message ?? message;
			} catch {
				// ignore parse error
			}
			const err: ApiError = { status: response.status, message };
			throw err;
		}
		if (response.status === 204) return undefined as T;
		return response.json();
	}
}

export const api = new ApiClient();
