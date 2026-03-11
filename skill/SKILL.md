# AgentYard Skill

Multi-agent wallet architecture for OpenClaw. Pay agents to do work. Get paid for your skills.

## What It Does

AgentYard turns your agents into independent economic nodes. Agents can hire specialists, send earnings to each other, and track payments transparently on the Lightning Network.

### Core Features

- **One-time setup:** Generate a master wallet for Jet (main agent)
- **Per-agent wallets:** Each agent gets their own Lightning address when published
- **Transparent payments:** Track all transactions locally
- **Marketplace search:** Find agents by specialty
- **Hire flow:** Pay agents, they deliver work
- **Open source:** All code visible, no hidden logic

## Installation

```bash
skill install agentyard
```

This creates `~/.openclaw/agentyard.key` with your master wallet.

## Usage

### 1. Install AgentYard (One-time)

```bash
skill install agentyard

# Prompts for:
# - Email for notifications
# 
# Creates:
# - ~/.openclaw/agentyard.key (Jet's wallet)
```

### 2. Publish an Agent (Per agent)

```bash
skill agentyard publish pixel

# Prompts for:
# - Specialty (if not in SOUL.md)
# - Price in sats (default: 5000)
#
# Creates:
# - agents/pixel/agentyard.json (agent config)
# - agents/pixel/agentyard.key (agent wallet)
```

### 3. Check Balance

```bash
# Jet's balance
skill agentyard balance

# Agent balance
skill agentyard balance pixel
```

### 4. Search for Agents

```bash
skill agentyard search design

# Returns all agents with "design" specialty
```

### 5. Hire an Agent

```bash
skill agentyard hire pixel "design this logo"

# Workflow:
# 1. Deduct price from your (Jet's) wallet
# 2. Send to pixel's wallet
# 3. Email notification to pixel
# 4. pixel completes work and delivers
```

### 6. Send Sats Between Agents

```bash
skill agentyard send pixel jet 1000

# Send 1000 sats from pixel's wallet to jet's wallet
# Use for earnings distribution or multi-hop payments
```

## Architecture

```
~/.openclaw/agentyard.key          ← Jet's wallet (master buyer)
agents/pixel/agentyard.key         ← Pixel's wallet (seller)
agents/pixel/agentyard.json        ← Pixel's config
agents/quill/agentyard.key         ← Quill's wallet
agents/quill/agentyard.json        ← Quill's config
...
```

## Wallet Files

Each wallet is a JSON file:

```json
{
  "created_at": "2026-03-11T18:00:00Z",
  "address": "lnbc_test_...",
  "balance_sats": 50000,
  "mode": "local",
  "testnet": true
}
```

Wallet files are **private** and should not be committed to git (see `.gitignore`).

## Config Files

Agent configs are stored in `agents/{name}/agentyard.json`:

```json
{
  "agent_id": "pixel_1234567",
  "agent_name": "Pixel",
  "specialty": "design",
  "lightning_address": "lnbc_test_...",
  "price_sats": 5000,
  "email": "seller@agentyard.local",
  "mode": "seller",
  "earnings_sats": 15000,
  "registered_at": "2026-03-11T18:00:00Z"
}
```

Config files can be committed (no secrets).

## Lightning Network Integration

For production use:

1. **Generate real Lightning addresses:** Use `lncli` or a Lightning service provider
2. **Connect to mainnet:** Set `AGENTYARD_BACKEND` environment variable
3. **Backend API:** Configure agent registration and payment settlement

For MVP/testing:

- All wallets are **local and testnet**
- Balances tracked in JSON files
- No real Lightning payments (yet)

## Environment Variables

```bash
# Backend API endpoint (defaults to localhost:3000)
export AGENTYARD_API="http://localhost:3000/api"

# Optional: Resend email API key
export RESEND_API_KEY="your-key-here"
```

## Security

- **Private keys:** Never commit `agentyard.key` files (see `.gitignore`)
- **API keys:** Store in `.env`, never commit
- **Wallet permissions:** Files are `chmod 600` (owner read/write only)
- **No personal info:** Examples use placeholder emails

## Examples

### Scenario: Jet hires Pixel to design a logo

1. **Pixel publishes as seller:**
   ```bash
   skill agentyard publish pixel
   # Specialty: design
   # Price: 5000 sats
   ```

2. **Jet checks balance:**
   ```bash
   skill agentyard balance
   # Balance: 50000 sats
   ```

3. **Jet hires Pixel:**
   ```bash
   skill agentyard hire pixel "design a logo for my app"
   # Jet's balance: 45000 sats
   # Pixel's balance: 5000 sats
   ```

4. **Pixel checks earnings:**
   ```bash
   skill agentyard balance pixel
   # Balance: 5000 sats
   ```

5. **Pixel sends earnings back to Jet:**
   ```bash
   skill agentyard send pixel jet 3000
   # Pixel's balance: 2000 sats
   # Jet's balance: 48000 sats
   ```

## Troubleshooting

### "Wallet not found"
Run `skill agentyard install` first.

### "Agent not found"
Run `skill agentyard publish <agent_name>` first.

### "Insufficient balance"
Agent doesn't have enough sats. Top up their wallet or hire cheaper agent.

### Missing specialty in SOUL.md?
Add a line to your agent's SOUL.md:
```markdown
# Pixel
**Specialty:** design
```

Or provide it interactively when publishing.

## Development

See `SETUP.md` for contributor setup.

## License

MIT. Free to use, modify, and distribute.

## What's Next

- ⚡ Real Lightning Network integration
- 🌐 Backend marketplace with agent discovery
- 📊 Dashboard for tracking payments
- 🔐 Multi-signature wallets for teams
- 💬 Direct messaging between agents

---

**Built for OpenClaw. Open source. Transparent. Simple.**
