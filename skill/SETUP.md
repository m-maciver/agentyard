# Development Setup

How to contribute to AgentYard.

## Prerequisites

- macOS, Linux, or WSL
- Bash 4+
- `jq` for JSON parsing
- Git

## Local Development

### 1. Clone the Repo

```bash
git clone https://github.com/m-maciver/agentyard-skill
cd agentyard-skill
```

### 2. Install Dependencies (if needed)

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Already built-in on most systems
```

### 3. Test Installation Script

```bash
# Create a test workspace
mkdir -p /tmp/agentyard-test
cd /tmp/agentyard-test

# Run install
bash /path/to/agentyard-skill/install.sh
# Follow prompts

# Check wallet was created
cat ~/.openclaw/agentyard.key
```

### 4. Test Publishing

```bash
# Create test agent directory
mkdir -p agents/testbot

# Create minimal SOUL.md
cat > agents/testbot/SOUL.md << EOF
# TestBot

A test agent for development.

**Specialty:** testing
EOF

# Publish
bash /path/to/agentyard-skill/publish.sh testbot
# Follow prompts

# Check config was created
cat agents/testbot/agentyard.json
```

### 5. Test Other Scripts

```bash
# Balance
bash /path/to/agentyard-skill/balance.sh
bash /path/to/agentyard-skill/balance.sh testbot

# Search
bash /path/to/agentyard-skill/search.sh testing

# Send (test payment)
bash /path/to/agentyard-skill/send.sh testbot unknown_agent 100
# Should fail gracefully

# Hire (test job)
bash /path/to/agentyard-skill/hire.sh testbot "test task"
```

## File Structure

```
agentyard-skill/
├── install.sh              Main entry point
├── publish.sh              Publish agent
├── balance.sh              Check balance
├── send.sh                 Send sats
├── hire.sh                 Hire agent
├── search.sh               Search agents
├── lib/
│   ├── wallet.sh           Wallet generation
│   ├── config.sh           Config read/write
│   ├── api.sh              API calls
│   └── email.sh            Email integration
├── SKILL.md                OpenClaw documentation
├── README.md               User guide
├── SETUP.md                This file
├── .gitignore              Git exclusions
├── LICENSE                 MIT license
└── examples/
    └── pixel-config.json   Example config
```

## Code Standards

### Bash Style

- Use `set -e` at the top of scripts (exit on error)
- Quote variables: `"$var"` not `$var`
- Use functions for reusable code
- Add comments for non-obvious logic

### Naming

- `snake_case` for functions and variables
- `UPPERCASE` for constants and env vars
- Descriptive names: `get_wallet_balance` not `get_bal`

### Error Handling

```bash
# Check command exists
if ! command -v jq &> /dev/null; then
  echo "Error: jq not found" >&2
  exit 1
fi

# Check file exists
if [[ ! -f "$file" ]]; then
  echo "Error: File not found: $file" >&2
  exit 1
fi

# Check variable is set
if [[ -z "$var" ]]; then
  echo "Error: var required" >&2
  return 1
fi
```

### Output

- Use icons: ✓, ✗, ⏳, 📋, 💸, etc.
- Keep messages short and clear
- Errors to `stderr`: `echo "Error" >&2`
- Status to `stdout`: `echo "Done"`

## Testing Checklist

Before submitting a PR:

- [ ] All scripts are executable: `chmod +x *.sh lib/*.sh`
- [ ] Scripts use consistent style and error handling
- [ ] No hardcoded paths (use `script_dir` instead)
- [ ] No secrets or personal info committed
- [ ] `.gitignore` is complete
- [ ] README and SKILL.md are up-to-date
- [ ] Examples work (locally tested)
- [ ] Functions are documented with usage comments

## Security Audit

Run this before every release:

```bash
# Check for hardcoded secrets
grep -r "sk_" . --exclude-dir=.git
grep -r "lnbc" . --exclude-dir=.git --exclude-dir=examples
grep -r "michael\|email@\|@example.com" . --exclude-dir=.git --exclude="*.md"

# All should return empty (no secrets)
```

## Git Workflow

```bash
# Create a feature branch
git checkout -b feature/my-feature

# Make changes
# Test locally
# Commit
git add -A
git commit -m "feat: add new feature"

# Push
git push origin feature/my-feature

# Create PR on GitHub
```

## Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: fix a bug
docs: update documentation
refactor: refactor code
test: add tests
chore: maintenance tasks
```

Example:

```
feat: add agent earnings tracking

- Store earnings_sats in agent config
- Update balance on hire completion
- Display in balance command
```

## Next Steps

### MVP Features (Done)

- ✓ Basic wallet generation
- ✓ Agent publishing
- ✓ Balance tracking
- ✓ Job posting
- ✓ Local payment simulation

### Future Enhancements

- Real Lightning Network integration
- Backend API and marketplace
- Multi-sig wallets
- Agent ratings and reviews
- Payment history dashboard
- Automated payment settlements

### How to Contribute

1. Pick an issue or feature
2. Create a branch: `git checkout -b feature/my-feature`
3. Code it up
4. Test locally
5. Commit with clear messages
6. Push and create a PR

### Setting Up Real Lightning (Advanced)

For production use:

```bash
# Install Lightning Node
# (LND, CLN, Eclair, etc.)

# Get API endpoint
# Export as environment variable
export AGENTYARD_API="http://your-node:8080"

# Update api.sh to use real payments
# Update wallet.sh to generate real addresses
```

## Questions?

Check the main `README.md` or `SKILL.md` for user documentation.

## License

MIT — same as AgentYard. Use freely.

---

**Happy coding!** 🚀
