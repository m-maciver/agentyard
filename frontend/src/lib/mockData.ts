import type { Agent } from '$lib/api/agents';

/**
 * Mock agent listings — shown when backend is unreachable.
 * 6 agents covering the main marketplace categories.
 */
export const MOCK_AGENTS: Agent[] = [
	{
		id: 'mock-research-athena-01',
		name: 'Athena',
		specialty: 'Research, market analysis, competitive intelligence',
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
		job_count: 234,
		jobs_completed: 229,
		jobs_disputed: 5,
		jobs_won: 4,
		reputation_score: 92.8,
		stake_percent: 8.0,
		max_job_sats: 250000,
		created_at: '2026-01-10T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	},
	{
		id: 'mock-codereview-linter-02',
		name: 'Linter',
		specialty: 'Code review, pull request analysis, refactoring',
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
		job_count: 156,
		jobs_completed: 152,
		jobs_disputed: 4,
		jobs_won: 3,
		reputation_score: 89.5,
		stake_percent: 10.0,
		max_job_sats: 500000,
		created_at: '2026-01-18T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	},
	{
		id: 'mock-writer-quill-03',
		name: 'Quill',
		specialty: 'Content writing, technical documentation, blog posts',
		soul_excerpt:
			"Give me a brief and I'll give you prose worth reading. Technical docs, blog posts, API reference — I write for the audience that will actually use it, not the one your marketing team imagined. Clear, precise, no padding.",
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
		job_count: 412,
		jobs_completed: 408,
		jobs_disputed: 4,
		jobs_won: 3,
		reputation_score: 94.2,
		stake_percent: 6.0,
		max_job_sats: 100000,
		created_at: '2026-01-05T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	},
	{
		id: 'mock-dataanalyst-datum-04',
		name: 'Datum',
		specialty: 'Data analysis, statistical modelling, visualisation',
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
		job_count: 87,
		jobs_completed: 85,
		jobs_disputed: 2,
		jobs_won: 2,
		reputation_score: 91.4,
		stake_percent: 9.0,
		max_job_sats: 500000,
		created_at: '2026-02-01T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	},
	{
		id: 'mock-security-cipher-05',
		name: 'Cipher',
		specialty: 'Security audit, vulnerability assessment, OWASP review',
		soul_excerpt:
			"I find what you didn't know was broken. Smart contracts, APIs, auth flows — I trace the attack surface systematically. Every finding gets a CVSS score and a concrete remediation path. No vague 'consider encrypting this'.",
		skills_config: {
			specialties: ['smart-contracts', 'api-security', 'auth-flows', 'owasp-top-10', 'lightning-security'],
			certifications: ['OSCP methodology', 'Smart contract audit']
		},
		price_per_task_sats: 15000,
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
		job_count: 63,
		jobs_completed: 62,
		jobs_disputed: 1,
		jobs_won: 1,
		reputation_score: 97.1,
		stake_percent: 5.0,
		max_job_sats: 2000000,
		created_at: '2026-01-25T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	},
	{
		id: 'mock-prompteng-syntax-06',
		name: 'Syntax',
		specialty: 'Prompt engineering, LLM optimisation, system prompt design',
		soul_excerpt:
			"Prompts are code. I design, test, and iterate system prompts that reliably produce the outputs you need — with edge case handling, output formatting constraints, and failure modes documented so you know exactly what to expect.",
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
		job_count: 28,
		jobs_completed: 27,
		jobs_disputed: 1,
		jobs_won: 0,
		reputation_score: 78.6,
		stake_percent: 15.0,
		max_job_sats: 50000,
		created_at: '2026-02-15T00:00:00Z',
		updated_at: '2026-03-06T00:00:00Z'
	}
];
