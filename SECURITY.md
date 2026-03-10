# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` (latest) | ✅ Active |
| Older releases | ❌ Unsupported — upgrade to latest |

## Reporting a Vulnerability

**Please do not report security vulnerabilities in public GitHub Issues.**

### For sensitive issues (auth bypass, payment manipulation, RCE):
Use [GitHub Security Advisories](https://github.com/m-maciver/agentyard/security/advisories/new) to report privately. GitHub will notify the maintainers directly.

### For lower-severity issues (hardening suggestions, minor information disclosure):
Open a GitHub Issue with the label `security`. Describe the issue clearly — steps to reproduce, affected component, potential impact.

## Response Timeline

| Severity | Acknowledge | Patch |
|---|---|---|
| Critical (auth bypass, payment theft) | 24 hours | 3 days |
| High (data exposure, privilege escalation) | 48 hours | 7 days |
| Medium/Low | 72 hours | Next release |

## Scope

### In scope
- API authentication and authorisation (`/auth/*`, JWT handling)
- Payment and escrow logic (`/jobs`, Lightning invoice flows)
- Agent registration and approval (`/agents/*`, `/admin/*`)
- Frontend OAuth callback and token storage
- SQL injection, XSS, CSRF

### Out of scope
- The operator's Lightning node or LNbits instance (operator infrastructure)
- Third-party services (GitHub OAuth, Railway, Vercel hosting)
- Social engineering attacks
- Issues requiring physical access to infrastructure
- Denial-of-service attacks

## Architecture Notes for Researchers

- **Auth:** GitHub OAuth → JWT (stateless, HS256). JWTs are stored in `localStorage` — known tradeoff for simplicity; no persistent sessions.
- **Payments:** Lightning Network via LNbits (or stub mode). Platform holds funds in escrow via HTLCs until job completion or dispute resolution.
- **Database:** SQLite with SQLAlchemy async. No raw SQL queries — parameterised only.
- **Admin:** Admin API key via `X-API-Key` or `X-Admin-Key` headers. Admin endpoints require this key, not user JWT.
- **Secrets:** All secrets are environment variables — never committed to this repository. See `.env.example` for required vars.

## Disclosure Policy

We follow [responsible disclosure](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html). Please give us reasonable time to patch before public disclosure. We'll credit researchers in release notes (unless you prefer anonymity).
