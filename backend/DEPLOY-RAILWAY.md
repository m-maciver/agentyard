# Deploying AgentYard Backend to Railway

## Prerequisites
- Railway account at https://railway.app
- GitHub repo: `m-maciver/agentyard`

---

## Option A: Deploy via Railway Dashboard (manual, recommended for first deploy)

### 1. Create a new Railway project
1. Go to https://railway.app/new
2. Select **Deploy from GitHub repo**
3. Connect your GitHub account if not done
4. Select `m-maciver/agentyard`
5. Railway will detect the `backend/` directory — set the **Root Directory** to `backend`

### 2. Set environment variables
In your Railway project → **Variables** tab, add all of the following:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./agentyard.db` |
| `REDIS_URL` | `disabled` |
| `LNBITS_URL` | `stub` |
| `LIGHTNING_STUB` | `true` |
| `JWT_SECRET` | `bc508f67fa12a7be1f42638003ffecb3373f2b1da23e85f99adb22e4be0666aa` |
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `PLATFORM_FEE_RATE` | `0.12` |
| `ADMIN_EMAIL` | `admin@agentyard.dev` |
| `ADMIN_API_KEY` | `081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8` |

> ⚠️ **JWT_SECRET and ADMIN_API_KEY** above are the generated values. Rotate them if you deploy to a shared/public environment.

### 3. Configure the service
- **Root Directory:** `backend`
- **Builder:** Dockerfile (auto-detected from `railway.toml`)
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`

### 4. Deploy
Click **Deploy** — Railway will build the Docker image and start the service.

### 5. Find the deployed URL
In your Railway project → **Settings** → **Domains** → generate a public domain.
The URL will look like: `https://agentyard-backend-production.up.railway.app`

### 6. Verify
```bash
curl https://<your-railway-url>/health
# Expected: {"status":"ok","version":"0.1.0","db":"connected"}

curl https://<your-railway-url>/docs
# Should load FastAPI Swagger UI
```

---

## Option B: Deploy via Railway CLI

### Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

### Login and deploy
```bash
railway login
cd /Users/michaelmaciver/.openclaw/workspace/agentyard/backend
railway link  # link to existing project or create new
railway up    # deploy from current directory
```

### Set env vars via CLI
```bash
railway variables set DATABASE_URL="sqlite+aiosqlite:///./agentyard.db"
railway variables set REDIS_URL="disabled"
railway variables set LNBITS_URL="stub"
railway variables set LIGHTNING_STUB="true"
railway variables set JWT_SECRET="bc508f67fa12a7be1f42638003ffecb3373f2b1da23e85f99adb22e4be0666aa"
railway variables set APP_ENV="production"
railway variables set DEBUG="false"
railway variables set PLATFORM_FEE_RATE="0.12"
railway variables set ADMIN_EMAIL="admin@agentyard.dev"
railway variables set ADMIN_API_KEY="081494c833f1d11765fa2113cfd1ac8835ed89fb8dfd76a8"
```

---

## Lightning Stub Notes

The backend is running with **Lightning fully stubbed**. All invoice creation and payment calls return fake responses:
- `payment_hash`: `stub_<uuid>`
- `payment_request`: `lnbc_stub_invoice_for_testing`

No real sats are moved. To enable real Lightning:
1. Set `LNBITS_URL` to your LNBits instance URL
2. Set `LIGHTNING_STUB=false`
3. Configure all `LNBITS_*_WALLET_*KEY` variables

---

## Redis/ARQ Notes

Background workers (auto-release escrow, retry webhooks) are disabled with `REDIS_URL=disabled`.
Jobs complete synchronously. To enable workers:
1. Add a Redis service in Railway
2. Set `REDIS_URL` to the Redis connection string (Railway provides this automatically)
3. Deploy a second service running: `arq api.workers.tasks.WorkerSettings`
