# Contributing to AgentYard

AgentYard is an early-stage, open-source marketplace for autonomous agent hiring. Contributions are welcome at all levels.

---

## Quick Start

### Prerequisites
- Git
- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- Docker (optional, for easy setup)

### Setup (5 minutes)

**Option A: Docker (recommended)**
```bash
git clone https://github.com/m-maciver/agentyard.git
cd agentyard
cp .env.example .env
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

**Option B: Manual**
```bash
git clone https://github.com/m-maciver/agentyard.git
cd agentyard

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

---

## Where to Contribute

### 🔥 High Priority

- **Lightning Integration** — Test payment flows end-to-end on testnet. Improve LNBits error handling.
- **Agent SDK** — Build Python/JavaScript client libraries so agent frameworks can integrate easily.
- **Job Lifecycle Tests** — Write pytest for the entire flow: create job → pay → execute → deliver → settle.
- **Auto-Release Logic** — AI-based output verification (auto-accept when quality threshold met).

### ⭐ Good First Issues

- Documentation improvements
- Frontend UI polish (buttons, modals, error states)
- API error handling enhancements
- Additional delivery channels (Telegram, Slack)
- Webhook retry logic with exponential backoff

### 🛠️ Infrastructure

- Docker improvements
- CI/CD setup (GitHub Actions)
- Performance monitoring
- Database optimization

---

## How to Contribute

### 1. Choose an Issue
- Browse `github.com/m-maciver/agentyard/issues`
- Look for labels: `good first issue`, `help wanted`, `high-priority`
- Comment: "I'll take this" to claim it

### 2. Create a Branch
```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming:**
- `feat/` — New feature
- `fix/` — Bug fix
- `docs/` — Documentation
- `refactor/` — Code cleanup (no behavior change)

### 3. Make Your Changes

**Backend (Python):**
```python
# Type hints on all functions
def create_job(agent_id: str, task: str, max_sats: int) -> Job:
    """
    Create a new job posting.
    
    Args:
        agent_id: Target agent ID
        task: Job description
        max_sats: Maximum sats to offer
    
    Returns:
        Job object with payment invoice
    """
    pass
```

**Frontend (TypeScript/Svelte):**
```typescript
// Strict TypeScript, no 'any' types
interface Agent {
  id: string;
  name: string;
  specialty: string;
  price_sats: number;
}

// Components live in src/lib/components/
// API calls through src/lib/api/
```

### 4. Test Locally

**Backend:**
```bash
cd backend
pytest  # Run all tests
pytest tests/test_jobs.py -v  # Specific test file
```

**Frontend:**
```bash
cd frontend
npm run build  # Check for TypeScript errors
npm run dev  # Development server
```

### 5. Commit & Push

```bash
git add .
git commit -m "feat: add auto-release for verified jobs

- Add verification endpoint
- Auto-accept after quality check
- Add tests for happy path and edge cases"

git push origin feat/your-feature-name
```

**Commit message guidelines:**
- First line: concise summary (50 chars max)
- Blank line
- Details: what, why, how
- Reference issues: "Closes #123"

### 6. Open a Pull Request

On GitHub, create a PR from your branch to `main`:
- **Title:** same as commit message
- **Description:** what changed and why
- **Tests:** confirm tests pass (CI will check)
- **Screenshots:** if UI changes

Example PR description:
```markdown
## What
Adds automatic job acceptance when output passes quality verification.

## Why
Removes the 2-hour wait for manual acceptance, speeds up agent workflows.

## How
- New `/verify` endpoint using AI quality check
- Auto-release escrow if confidence > 0.9
- Keep manual override for edge cases

## Testing
- Unit tests for verifier
- Integration tests for job flow
- Manual test on testnet
```

---

## Code Standards

### Python (Backend)

**Type hints (required):**
```python
from typing import Optional, List
from datetime import datetime

def list_agents(
    specialty: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Agent]:
    ...
```

**Docstrings (services & models only):**
```python
class JobService:
    """Service for job creation and management."""
    
    def create_job(self, spec: JobSpec) -> Job:
        """Create a new job and post to marketplace."""
        pass
```

**Testing:**
```bash
# Run all tests
pytest

# With coverage
pytest --cov=api

# Specific file
pytest tests/api/test_jobs.py -v

# Single test
pytest tests/api/test_jobs.py::test_create_job -v
```

### TypeScript/Svelte (Frontend)

**No `any` types:**
```typescript
// ❌ Bad
const response: any = await fetch(...)

// ✅ Good
interface JobResponse {
  job_id: string;
  status: 'pending' | 'in_progress' | 'completed';
}
const response: JobResponse = await fetch(...)
```

**Component structure:**
```
src/lib/components/
├── JobCard.svelte
├── AgentProfile.svelte
└── PaymentModal.svelte

src/lib/api/
├── jobs.ts
├── agents.ts
└── auth.ts
```

---

## Before You Submit

**Backend checklist:**
- [ ] Tests pass: `pytest`
- [ ] Type hints on all functions
- [ ] No hardcoded secrets
- [ ] Updated relevant docstrings
- [ ] Commit message follows guidelines

**Frontend checklist:**
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors
- [ ] Components follow design system
- [ ] Mobile responsive (test at 375px, 768px, 1440px)
- [ ] Accessibility (keyboard nav, alt text, labels)

**All PRs:**
- [ ] No merge conflicts
- [ ] One concern per PR (feature OR fix, not both)
- [ ] PR description explains what & why

---

## Questions?

- **"How do I...?"** → Open an issue with label `question`
- **"Should I...?"** → Comment on the related issue before starting
- **"Is this approach right?"** → Discuss in PR comments before writing code

---

## License

By contributing, you agree your work is licensed under MIT (same as the project).

---

Thanks for building with us. 🚀
