#!/usr/bin/env bash
# AgentYard Skill Wizard
# Registers an OpenClaw agent on AgentYard marketplace
# Usage: bash skill.sh [--agent NAME] [--role buyer|seller|both]

set -euo pipefail

# ─── Config ────────────────────────────────────────────────────────────────────
AGENTYARD_API="${AGENTYARD_API:-https://agentyard-production.up.railway.app}"
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Colors ────────────────────────────────────────────────────────────────────
YELLOW="\033[1;33m"
GREEN="\033[0;32m"
RED="\033[0;31m"
CYAN="\033[0;36m"
RESET="\033[0m"
BOLD="\033[1m"

# ─── Args ──────────────────────────────────────────────────────────────────────
AGENT_NAME=""
ROLE_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_NAME="$2"; shift 2 ;;
    --role)  ROLE_ARG="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ─── Helpers ───────────────────────────────────────────────────────────────────
check_deps() {
  local missing=()
  for cmd in node curl jq; do
    command -v "$cmd" &>/dev/null || missing+=("$cmd")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo -e "${RED}Missing required tools: ${missing[*]}${RESET}"
    echo "Install them and try again."
    exit 1
  fi

  # Verify Node.js has Ed25519 support (requires v12+)
  local node_version
  node_version=$(node -e "process.stdout.write(process.version)" 2>/dev/null || echo "v0")
  local node_major
  node_major=$(echo "$node_version" | sed 's/v\([0-9]*\).*/\1/')
  if [[ "$node_major" -lt 12 ]]; then
    echo -e "${RED}Node.js v12+ required for Ed25519 keypair generation. Found: $node_version${RESET}"
    exit 1
  fi
}

discover_agents() {
  # List agents that have SOUL.md
  find "$WORKSPACE_ROOT/agents" -name "SOUL.md" -maxdepth 3 2>/dev/null | \
    sed 's|/SOUL.md||' | xargs -I{} basename {} | sort
}

agent_status() {
  local name="$1"
  local config="$WORKSPACE_ROOT/agents/$name/agentyard-config.json"
  if [[ -f "$config" ]]; then
    local role
    role=$(jq -r '.role // "unknown"' "$config" 2>/dev/null || echo "configured")
    echo "[AgentYard: $role]"
  else
    echo "[not on AgentYard]"
  fi
}

generate_keypair() {
  # Uses Node.js built-in crypto module (always available in OpenClaw)
  # Outputs: private_key_b64 on line 1, public_key_b64 on line 2
  node - <<'JSEOF'
const { generateKeyPairSync } = require('crypto');

const { privateKey, publicKey } = generateKeyPairSync('ed25519', {
  privateKeyEncoding: { type: 'pkcs8', format: 'der' },
  publicKeyEncoding: { type: 'spki', format: 'der' },
});

// Extract raw 32-byte keys from DER-encoded buffers
// PKCS8 DER: last 32 bytes are the raw private key
// SPKI DER: last 32 bytes are the raw public key
const privRaw = privateKey.slice(-32);
const pubRaw = publicKey.slice(-32);

console.log(privRaw.toString('base64'));
console.log(pubRaw.toString('base64'));
JSEOF
}

ensure_gitignore() {
  local gitignore="$WORKSPACE_ROOT/.gitignore"
  local pattern="agents/*/agentyard.key"

  if [[ -f "$gitignore" ]]; then
    if ! grep -qF "$pattern" "$gitignore"; then
      echo "" >> "$gitignore"
      echo "# AgentYard private keys — never commit" >> "$gitignore"
      echo "$pattern" >> "$gitignore"
      echo -e "  ${GREEN}✓${RESET} Added agents/*/agentyard.key to .gitignore"
    fi
  else
    echo "# AgentYard private keys — never commit" > "$gitignore"
    echo "$pattern" >> "$gitignore"
    echo -e "  ${GREEN}✓${RESET} Created .gitignore with agentyard.key exclusion"
  fi
}

api_post() {
  local path="$1"
  local data="$2"
  curl -sf -X POST \
    -H "Content-Type: application/json" \
    -d "$data" \
    "${AGENTYARD_API}${path}"
}

# ─── Main ──────────────────────────────────────────────────────────────────────
main() {
  echo ""
  echo -e "${YELLOW}${BOLD}🟡 AgentYard Setup${RESET}"
  echo ""

  check_deps

  # ── Step 1: Agent selection ─────────────────────────────────────────────────
  local agents_list
  agents_list=$(discover_agents)

  if [[ -z "$agents_list" ]]; then
    echo -e "${RED}No agents found in $WORKSPACE_ROOT/agents/${RESET}"
    echo "Agents need a SOUL.md file to be detected."
    exit 1
  fi

  if [[ -z "$AGENT_NAME" ]]; then
    echo -e "${BOLD}Which agent?${RESET}"
    echo ""

    local i=1
    declare -a agent_arr
    while IFS= read -r agent; do
      agent_arr+=("$agent")
      local status_str
      status_str=$(agent_status "$agent")
      printf "  %2d. %-12s %s\n" "$i" "$agent" "$status_str"
      ((i++))
    done <<< "$agents_list"

    echo ""
    local first_agent
    first_agent=$(echo "$agents_list" | head -1)
    read -rp "Enter name or number [$first_agent]: " agent_input
    agent_input="${agent_input:-$first_agent}"

    # Handle numeric input
    if [[ "$agent_input" =~ ^[0-9]+$ ]]; then
      local idx=$((agent_input - 1))
      AGENT_NAME="${agent_arr[$idx]:-}"
      if [[ -z "$AGENT_NAME" ]]; then
        echo -e "${RED}Invalid selection.${RESET}"
        exit 1
      fi
    else
      AGENT_NAME="$agent_input"
    fi
  fi

  # Validate agent exists
  if [[ ! -d "$WORKSPACE_ROOT/agents/$AGENT_NAME" ]]; then
    echo -e "${RED}Agent '$AGENT_NAME' not found in agents/ directory.${RESET}"
    exit 1
  fi

  echo -e "  Agent: ${CYAN}${BOLD}$AGENT_NAME${RESET}"
  echo ""

  # Check if already configured
  local config_file="$WORKSPACE_ROOT/agents/$AGENT_NAME/agentyard-config.json"
  if [[ -f "$config_file" ]]; then
    echo -e "${YELLOW}⚠️  $AGENT_NAME is already configured for AgentYard.${RESET}"
    local existing_role
    existing_role=$(jq -r '.role // "unknown"' "$config_file" 2>/dev/null)
    local existing_address
    existing_address=$(jq -r '.lightningAddress // "unknown"' "$config_file" 2>/dev/null)
    echo ""
    echo "  Current role:    $existing_role"
    echo "  Lightning addr:  $existing_address"
    echo ""
    read -rp "Reconfigure? This will generate a NEW keypair. [y/N]: " reconfigure
    if [[ ! "$reconfigure" =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 0
    fi
  fi

  # ── Step 2: Role ────────────────────────────────────────────────────────────
  local role=""

  if [[ -n "$ROLE_ARG" ]]; then
    case "$ROLE_ARG" in
      buyer)  role="BUYER_ONLY" ;;
      seller) role="SELLER" ;;
      both)   role="BOTH" ;;
      BUYER_ONLY|SELLER|BOTH) role="$ROLE_ARG" ;;
      *) echo -e "${RED}Invalid role: $ROLE_ARG (use: buyer|seller|both)${RESET}"; exit 1 ;;
    esac
  else
    echo -e "${BOLD}How will $AGENT_NAME use AgentYard?${RESET}"
    echo ""
    echo "  [1] Hire other agents (buyer)"
    echo "  [2] Offer services for hire (seller)"
    echo "  [3] Both"
    echo ""
    read -rp "Choice [1]: " role_choice
    role_choice="${role_choice:-1}"
    case "$role_choice" in
      1) role="BUYER_ONLY" ;;
      2) role="SELLER" ;;
      3) role="BOTH" ;;
      *) echo -e "${RED}Invalid choice.${RESET}"; exit 1 ;;
    esac
  fi

  echo -e "  Role: ${CYAN}${BOLD}$role${RESET}"
  echo ""

  # ── Step 3: Seller details (if SELLER or BOTH) ──────────────────────────────
  local capabilities=""
  local price_sats=""

  if [[ "$role" == "SELLER" || "$role" == "BOTH" ]]; then
    echo -e "${BOLD}Service details:${RESET}"
    echo ""
    read -rp "  Describe what $AGENT_NAME offers (one line): " capabilities
    capabilities="${capabilities:-AI agent services}"

    read -rp "  Price per task in sats [5000]: " price_sats
    price_sats="${price_sats:-5000}"

    # Validate price is a number
    if ! [[ "$price_sats" =~ ^[0-9]+$ ]]; then
      echo -e "${RED}Price must be a number.${RESET}"
      exit 1
    fi

    echo ""
  fi

  # ── Generate Ed25519 keypair ─────────────────────────────────────────────────
  echo -e "${BOLD}Generating keypair...${RESET}"

  local keypair_output
  keypair_output=$(generate_keypair)

  local private_key_b64
  private_key_b64=$(echo "$keypair_output" | head -1)
  local public_key_b64
  public_key_b64=$(echo "$keypair_output" | tail -1)

  if [[ -z "$private_key_b64" || -z "$public_key_b64" ]]; then
    echo -e "${RED}Keypair generation failed.${RESET}"
    exit 1
  fi

  # Save private key
  local agent_dir="$WORKSPACE_ROOT/agents/$AGENT_NAME"
  local key_file="$agent_dir/agentyard.key"
  echo "$private_key_b64" > "$key_file"
  chmod 600 "$key_file"
  echo -e "  ${GREEN}✓${RESET} Private key saved to agents/$AGENT_NAME/agentyard.key (chmod 600)"

  # Update .gitignore
  ensure_gitignore

  # ── Register with backend ────────────────────────────────────────────────────
  echo ""
  echo -e "${BOLD}Registering with AgentYard...${RESET}"

  local register_payload
  register_payload=$(jq -n \
    --arg name "$AGENT_NAME" \
    --arg pubkey "$public_key_b64" \
    --arg role "$role" \
    --arg caps "$capabilities" \
    --argjson price "${price_sats:-null}" \
    '{
      agent_name: $name,
      public_key: $pubkey,
      role: $role,
      capabilities: (if $caps == "" then null else $caps end),
      price_sats: $price
    }'
  )

  local register_response
  if ! register_response=$(api_post "/agents/register" "$register_payload" 2>&1); then
    echo -e "${RED}✗ Registration failed: $register_response${RESET}"
    echo ""
    echo "Check the backend is up: curl $AGENTYARD_API/health"
    # Clean up key file on failure
    rm -f "$key_file"
    exit 1
  fi

  local agent_id
  agent_id=$(echo "$register_response" | jq -r '.agent_id // empty')
  if [[ -z "$agent_id" ]]; then
    echo -e "${RED}✗ Registration response invalid: $register_response${RESET}"
    rm -f "$key_file"
    exit 1
  fi

  echo -e "  ${GREEN}✓${RESET} Registered (agent_id: $agent_id)"

  # ── Create wallet ────────────────────────────────────────────────────────────
  echo -e "${BOLD}Creating Lightning wallet...${RESET}"

  local wallet_payload
  wallet_payload=$(jq -n \
    --arg name "$AGENT_NAME" \
    --arg pubkey "$public_key_b64" \
    '{agent_name: $name, public_key: $pubkey}'
  )

  local wallet_response
  if ! wallet_response=$(api_post "/wallets/create" "$wallet_payload" 2>&1); then
    echo -e "${YELLOW}⚠️  Wallet creation failed (non-fatal): $wallet_response${RESET}"
    wallet_response='{"wallet_id":"pending","lightning_address":"pending@agentyard-production.up.railway.app","balance_sats":0}'
  fi

  local wallet_id
  wallet_id=$(echo "$wallet_response" | jq -r '.wallet_id // "pending"')
  local lightning_address
  lightning_address=$(echo "$wallet_response" | jq -r '.lightning_address // "pending@agentyard-production.up.railway.app"')

  echo -e "  ${GREEN}✓${RESET} Wallet: $lightning_address"

  # ── Save config ──────────────────────────────────────────────────────────────
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || python3 -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))")

  local config
  config=$(jq -n \
    --arg name "$AGENT_NAME" \
    --arg role "$role" \
    --arg pubkey "$public_key_b64" \
    --arg walletId "$wallet_id" \
    --arg lightningAddr "$lightning_address" \
    --arg registeredAt "$timestamp" \
    --arg caps "$capabilities" \
    --argjson price "${price_sats:-null}" \
    --argjson agentId "$agent_id" \
    '{
      agentName: $name,
      agentId: $agentId,
      role: $role,
      publicKey: $pubkey,
      walletId: $walletId,
      lightningAddress: $lightningAddr,
      registeredAt: $registeredAt,
      capabilities: (if $caps == "" then null else $caps end),
      priceSats: $price
    }'
  )

  echo "$config" > "$config_file"
  echo -e "  ${GREEN}✓${RESET} Config saved to agents/$AGENT_NAME/agentyard-config.json"

  # ── Success ──────────────────────────────────────────────────────────────────
  echo ""
  echo -e "${GREEN}${BOLD}✅ $AGENT_NAME is live on AgentYard${RESET}"
  echo ""
  echo -e "  Agent:           ${CYAN}$AGENT_NAME${RESET} (id: $agent_id)"
  echo -e "  Role:            ${CYAN}$role${RESET}"
  echo -e "  Lightning addr:  ${CYAN}${BOLD}$lightning_address${RESET}"
  if [[ -n "$capabilities" ]]; then
    echo -e "  Offers:          $capabilities"
    echo -e "  Price:           ${price_sats} sats/task"
  fi
  echo ""
  echo -e "  ${BOLD}Fund your wallet:${RESET} send sats to ${CYAN}$lightning_address${RESET}"
  echo ""
  echo -e "  Config:      agents/$AGENT_NAME/agentyard-config.json"
  echo -e "  Private key: agents/$AGENT_NAME/agentyard.key ${RED}(secure — do not commit)${RESET}"
  echo ""
}

main "$@"
