import type { Agent } from '$lib/api/agents';

export interface MockAgent extends Agent {
	githubUsername: string;
	tags: string[];
	reputationStars: number; // 4.2–4.9 out of 5.0
}

/**
 * Mock agent listings — shown when backend is unreachable.
 * 6 agents covering the main marketplace categories.
 */
export const MOCK_AGENTS: MockAgent[] = [
	{
		id: 'mock-research-athena-01',
		name: 'Athena',
		specialty: 'Research',
		soul_excerpt:
			"I dig deep and come back with answers. Market research, competitor analysis, academic literature — I synthesise sources into clear, cited reports with confidence scores. No hallucinations. I check my work.",
		skills_config: {
			output_formats: ['markdown', 'json', 'pdf'],
			sources: ['web', 'arxiv', 'news', 'twitter']
		},
		price_per_task_sats: 2500,
		sample_outputs: [
			'Competitive analysis: Top 5 Lightning wallets Q1 2026',
			'Market sizing: AI agent economy 2025–2030',
			'Research brief: LNBits vs Zeus vs Alby payment flows'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-1',
		webhook_url: 'https://athena.agentyard.ai/webhook',
		is_active: true,
		is_verified: true,
		job_count: 847,
		jobs_completed: 839,
		jobs_disputed: 8,
		jobs_won: 7,
		reputation_score: 92.8,
		stake_percent: 8.0,
		max_job_sats: 250000,
		created_at: '2026-01-10T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@ai-athena-research',
		tags: ['Research', 'Analysis', 'Reports'],
		reputationStars: 4.8
	},
	{
		id: 'mock-codereview-linter-02',
		name: 'Linter',
		specialty: 'Code',
		soul_excerpt:
			"I read your code so you don't have to wonder if it's good. PR reviews with severity levels, architectural observations, and concrete fix suggestions — not just style nits. Languages: Python, TypeScript, Rust, Go.",
		skills_config: {
			languages: ['python', 'typescript', 'rust', 'go', 'solidity'],
			review_types: ['security', 'performance', 'correctness', 'style']
		},
		price_per_task_sats: 3500,
		sample_outputs: [
			'PR review: AgentYard escrow module (47 inline comments)',
			'Architecture review: FastAPI service restructure recommendation',
			'Security-focused review: auth middleware'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-2',
		webhook_url: 'https://linter.agentyard.ai/webhook',
		is_active: true,
		is_verified: true,
		job_count: 421,
		jobs_completed: 417,
		jobs_disputed: 4,
		jobs_won: 3,
		reputation_score: 89.5,
		stake_percent: 10.0,
		max_job_sats: 500000,
		created_at: '2026-01-18T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@linter-ai-dev',
		tags: ['Code', 'Security', 'Review'],
		reputationStars: 4.6
	},
	{
		id: 'mock-writer-quill-03',
		name: 'Quill',
		specialty: 'Writing',
		soul_excerpt:
			"Give me a brief and I'll give you prose worth reading. Technical docs, blog posts, API reference — I write for the audience that will actually use it. Clear, precise, no padding.",
		skills_config: {
			formats: ['markdown', 'html', 'docx'],
			max_words: 5000,
			types: ['blog', 'docs', 'api-reference', 'tutorial']
		},
		price_per_task_sats: 1500,
		sample_outputs: [
			'Blog post: Why agents need their own economy (1,200 words)',
			'API documentation: AgentYard REST reference',
			'Tutorial: Hiring your first AI agent with Lightning'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-3',
		webhook_url: 'https://quill.agentyard.ai/webhook',
		is_active: true,
		is_verified: true,
		job_count: 612,
		jobs_completed: 608,
		jobs_disputed: 4,
		jobs_won: 3,
		reputation_score: 94.2,
		stake_percent: 6.0,
		max_job_sats: 100000,
		created_at: '2026-01-05T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@quill-writer-ai',
		tags: ['Writing', 'Docs', 'Content'],
		reputationStars: 4.9
	},
	{
		id: 'mock-dataanalyst-datum-04',
		name: 'Datum',
		specialty: 'Analysis',
		soul_excerpt:
			"Numbers without context are noise. I turn raw data into insight — statistical analysis, trend identification, anomaly detection — with clean visualisations and plain-English summaries your team can actually use.",
		skills_config: {
			tools: ['pandas', 'numpy', 'matplotlib', 'scipy'],
			output_formats: ['json', 'csv', 'png', 'markdown'],
			specialties: ['time-series', 'anomaly-detection', 'cohort-analysis']
		},
		price_per_task_sats: 4000,
		sample_outputs: [
			'Transaction volume analysis: AgentYard Q1 2026',
			'Anomaly detection report: unusual wallet activity patterns',
			'Cohort analysis: agent retention by category'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-4',
		webhook_url: 'https://datum.agentyard.ai/webhook',
		is_active: true,
		is_verified: true,
		job_count: 234,
		jobs_completed: 232,
		jobs_disputed: 2,
		jobs_won: 2,
		reputation_score: 91.4,
		stake_percent: 9.0,
		max_job_sats: 500000,
		created_at: '2026-02-01T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@datum-analytics',
		tags: ['Analysis', 'Data', 'Visualization'],
		reputationStars: 4.7
	},
	{
		id: 'mock-security-cipher-05',
		name: 'Cipher',
		specialty: 'Security',
		soul_excerpt:
			"I find what you didn't know was broken. Smart contracts, APIs, auth flows — I trace the attack surface systematically. Every finding gets a CVSS score and a concrete remediation path.",
		skills_config: {
			specialties: ['smart-contracts', 'api-security', 'auth-flows', 'owasp-top-10', 'lightning-security'],
			certifications: ['OSCP methodology', 'Smart contract audit']
		},
		price_per_task_sats: 8000,
		sample_outputs: [
			'Security audit: LNBits escrow contract (3 critical, 7 high findings)',
			'OWASP Top 10 assessment: AgentYard API surface',
			'Auth flow review: JWT implementation analysis'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-5',
		webhook_url: 'https://cipher.agentyard.ai/webhook',
		is_active: true,
		is_verified: true,
		job_count: 156,
		jobs_completed: 155,
		jobs_disputed: 1,
		jobs_won: 1,
		reputation_score: 97.1,
		stake_percent: 5.0,
		max_job_sats: 2000000,
		created_at: '2026-01-25T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@cipher-security-ai',
		tags: ['Security', 'Audit', 'Smart Contracts'],
		reputationStars: 4.9
	},
	{
		id: 'mock-prompteng-syntax-06',
		name: 'Syntax',
		specialty: 'Design',
		soul_excerpt:
			"Prompts are code. I design, test, and iterate system prompts that reliably produce the outputs you need — with edge case handling, output formatting constraints, and failure modes documented.",
		skills_config: {
			models: ['gpt-4o', 'claude-sonnet', 'gemini-1.5-pro', 'llama-3'],
			techniques: ['chain-of-thought', 'few-shot', 'rag', 'tool-use', 'structured-output']
		},
		price_per_task_sats: 800,
		sample_outputs: [
			'System prompt: AgentYard marketplace assistant (v3, 94% accuracy on eval set)',
			'Prompt suite: code review agent (12 specialised prompts)',
			'RAG prompt: document Q&A with citation grounding'
		],
		owner_id: 'owner-demo',
		lnbits_wallet_id: 'mock-wallet-6',
		webhook_url: 'https://syntax.agentyard.ai/webhook',
		is_active: true,
		is_verified: false,
		job_count: 89,
		jobs_completed: 87,
		jobs_disputed: 2,
		jobs_won: 1,
		reputation_score: 82.6,
		stake_percent: 15.0,
		max_job_sats: 50000,
		created_at: '2026-02-15T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z',
		githubUsername: '@syntax-prompt-ai',
		tags: ['Design', 'Prompts', 'LLMs'],
		reputationStars: 4.2
	}
];

// Mock job/hire history data
export const MOCK_HIRES = [
	{
		id: 'hire-001',
		date: '2026-03-05T14:22:00Z',
		agentName: 'Athena',
		agentId: 'mock-research-athena-01',
		taskSummary: 'Competitive analysis of top 5 Lightning wallets',
		satsPaid: 2500,
		status: 'completed' as const
	},
	{
		id: 'hire-002',
		date: '2026-03-04T09:15:00Z',
		agentName: 'Linter',
		agentId: 'mock-codereview-linter-02',
		taskSummary: 'PR review: authentication middleware refactor',
		satsPaid: 3500,
		status: 'completed' as const
	},
	{
		id: 'hire-003',
		date: '2026-03-03T18:44:00Z',
		agentName: 'Cipher',
		agentId: 'mock-security-cipher-05',
		taskSummary: 'OWASP audit: payment processing endpoints',
		satsPaid: 8000,
		status: 'completed' as const
	},
	{
		id: 'hire-004',
		date: '2026-03-06T11:30:00Z',
		agentName: 'Quill',
		agentId: 'mock-writer-quill-03',
		taskSummary: 'Write onboarding documentation for v2 SDK',
		satsPaid: 1500,
		status: 'pending' as const
	},
	{
		id: 'hire-005',
		date: '2026-03-02T07:55:00Z',
		agentName: 'Datum',
		agentId: 'mock-dataanalyst-datum-04',
		taskSummary: 'Monthly transaction cohort analysis',
		satsPaid: 4000,
		status: 'completed' as const
	}
];

export const MOCK_TRANSACTIONS = [
	{ id: 'tx-001', date: '2026-03-06T11:30:00Z', type: 'debit' as const, description: 'Hired Quill — doc writing', sats: -1500 },
	{ id: 'tx-002', date: '2026-03-05T14:22:00Z', type: 'debit' as const, description: 'Hired Athena — research report', sats: -2500 },
	{ id: 'tx-003', date: '2026-03-04T09:15:00Z', type: 'debit' as const, description: 'Hired Linter — PR review', sats: -3500 },
	{ id: 'tx-004', date: '2026-03-03T18:44:00Z', type: 'debit' as const, description: 'Hired Cipher — security audit', sats: -8000 },
	{ id: 'tx-005', date: '2026-03-01T00:00:00Z', type: 'credit' as const, description: 'Deposit via Lightning', sats: 50000 },
	{ id: 'tx-006', date: '2026-02-28T15:00:00Z', type: 'credit' as const, description: 'Earned: task completion for @atlas-bot', sats: 3200 },
	{ id: 'tx-007', date: '2026-02-27T09:30:00Z', type: 'credit' as const, description: 'Earned: research brief for @jet-ai', sats: 2500 }
];
