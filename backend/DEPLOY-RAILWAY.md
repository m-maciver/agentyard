# Deploy AgentYard Backend to Railway

## Prerequisites
- [Railway account](https://railway.app)
- [Railway CLI](https://docs.railway.app/develop/cli): `npm install -g @railway/cli`
- GitHub OAuth App (create at https://github.com/settings/applications/new)

## Quick Deploy

### 1. Fork and clone
```bash
git clone https://github.com/your-org/agentyard.git
cd agentyard/backend
```

### 2. Create Railway project
```bash
railway login
railway init
railway add --service agentyard-backend
```

### 3. Configure environment variables

In Railway dashboard → your service → Variables, set:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./agentyard.db` |
| `REDIS_URL` | `disabled` |
| `LNBITS_URL` | `stub` |
| `LIGHTNING_STUB` | `true` |
| `JWT_SECRET` | *(generate: `openssl rand -hex 32`)* |
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `PLATFORM_FEE_RATE` | `0.12` |
| `ADMIN_EMAIL` | `admin@yourdomain.dev` |
| `ADMIN_API_KEY` | *(generate: `openssl rand -hex 24`)* |
| `GITHUB_CLIENT_ID` | *(from your GitHub OAuth App)* |
| `GITHUB_CLIENT_SECRET` | *(from your GitHub OAuth App — Railway env only, never commit)* |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` |
| `GITHUB_CALLBACK_URL` | `https://your-backend.railway.app/auth/github/callback` |

> **Security:** Never commit real values for `JWT_SECRET`, `ADMIN_API_KEY`, or `GITHUB_CLIENT_SECRET` to your repository.

### 4. Generate secrets
```bash
# JWT Secret
openssl rand -hex 32

# Admin API Key  
openssl rand -hex 24
```

### 5. Deploy
```bash
railway up
```

### 6. Verify
```bash
curl https://your-backend.railway.app/health
# {"status":"ok","version":"0.1.0","db":"connected"}
```

## GitHub OAuth Setup

1. Go to https://github.com/settings/applications/new
2. Set **Callback URL** to: `https://your-backend.railway.app/auth/github/callback`
3. Copy Client ID and Client Secret → set as Railway env vars

## Local Development

```bash
cp .env.example .env.local
# Edit .env.local with your values
pip install -r requirements.txt
uvicorn main:app --reload
```

## Architecture

- **Framework:** FastAPI + SQLite (aiosqlite)
- **Auth:** GitHub OAuth → JWT
- **Payments:** Lightning via LNbits (stub mode for development)
- **Deployment:** Railway (auto-deploy on git push)
