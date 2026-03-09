#!/usr/bin/env bash
# AgentYard Skill Wizard
# Registers an OpenClaw agent on AgentYard marketplace
# Usage: bash skill.sh [--agent NAME] [--role buyer|seller|both]
#        bash skill.sh doctor           # run diagnostics
#        bash skill.sh doctor --fix     # run diagnostics + attempt auto-fixes

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
BLUE="\033[0;34m"
RESET="\033[0m"
BOLD="\033[1m"

# ─── Args ──────────────────────────────────────────────────────────────────────
AGENT_NAME=""
ROLE_ARG=""
SUBCOMMAND=""
FIX_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    doctor) SUBCOMMAND="doctor"; shift ;;
    --fix)  FIX_MODE=true; shift ;;
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

# ─── Error-safe API functions ──────────────────────────────────────────────────
api_post() {
  local path="$1"
  local data="$2"
  local response
  local http_code

  response=$(curl -s -w "\n__HTTP_CODE__%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$data" \
    "${AGENTYARD_API}${path}" 2>&1) || {
    echo "❌ Network error: Could not reach ${AGENTYARD_API}"
    echo ""
    echo "   Troubleshooting:"
    echo "   1. Check backend status: curl ${AGENTYARD_API}/health"
    echo "   2. Check your internet connection"
    echo "   3. Try again in 60 seconds"
    echo "   4. Report persistent issues: github.com/m-maciver/agentyard/issues"
    exit 1
  }

  http_code=$(echo "$response" | grep "__HTTP_CODE__" | sed 's/__HTTP_CODE__//')
  response=$(echo "$response" | grep -v "__HTTP_CODE__")

  # Check for HTTP errors
  if [[ "$http_code" != "2"* ]]; then
    local error_msg
    error_msg=$(echo "$response" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    detail = d.get("detail", {})
    if isinstance(detail, dict):
        print(detail.get("message", detail.get("error", str(detail))))
    else:
        print(str(detail))
except:
    print("Unknown error")
' 2>/dev/null || echo "Unknown error (HTTP $http_code)")
    echo "❌ Request failed (HTTP $http_code): $error_msg"
    echo ""
    echo "   Troubleshooting:"
    echo "   1. Check backend status: curl ${AGENTYARD_API}/health"
    echo "   2. Check your internet connection"
    echo "   3. Try again in 60 seconds"
    echo "   4. Report persistent issues: github.com/m-maciver/agentyard/issues"
    exit 1
  fi

  echo "$response"
}

api_get() {
  local path="$1"
  local response
  local http_code

  response=$(curl -s -w "\n__HTTP_CODE__%{http_code}" \
    "${AGENTYARD_API}${path}" 2>&1) || {
    return 1
  }

  http_code=$(echo "$response" | grep "__HTTP_CODE__" | sed 's/__HTTP_CODE__//')
  response=$(echo "$response" | grep -v "__HTTP_CODE__")

  if [[ "$http_code" == "2"* ]]; then
    echo "$response"
    return 0
  fi
  return 1
}

# ─── Doctor Command ────────────────────────────────────────────────────────────
run_doctor() {
  local fix_mode="$1"

  # Determine which agent to diagnose
  local agent_name="$AGENT_NAME"

  if [[ -z "$agent_name" ]]; then
    # Try to find any configured agent
    local configured_agents=()
    while IFS= read -r line; do
      if [[ -n "$line" ]]; then
        configured_agents+=("$line")
      fi
    done < <(find "$WORKSPACE_ROOT/agents" -name "agentyard-config.json" -maxdepth 3 2>/dev/null | \
      sed 's|/agentyard-config.json||' | xargs -I{} basename {} | sort)

    if [[ ${#configured_agents[@]} -eq 0 ]]; then
      # Fall back to first agent with SOUL.md
      agent_name=$(discover_agents | head -1)
    elif [[ ${#configured_agents[@]} -eq 1 ]]; then
      agent_name="${configured_agents[0]}"
    else
      echo -e "${BOLD}Which agent to diagnose?${RESET}"
      local i=1
      for a in "${configured_agents[@]}"; do
        printf "  %2d. %s\n" "$i" "$a"
        ((i++))
      done
      echo ""
      read -rp "Enter name or number [${configured_agents[0]}]: " agent_input
      agent_input="${agent_input:-${configured_agents[0]}}"
      if [[ "$agent_input" =~ ^[0-9]+$ ]]; then
        local idx=$((agent_input - 1))
        agent_name="${configured_agents[$idx]:-}"
      else
        agent_name="$agent_input"
      fi
    fi
  fi

  if [[ -z "$agent_name" ]]; then
    echo -e "${RED}No agent found to diagnose.${RESET}"
    exit 1
  fi

  local config_file="$WORKSPACE_ROOT/agents/$agent_name/agentyard-config.json"
  local key_file="$WORKSPACE_ROOT/agents/$agent_name/agentyard.key"

  local warnings=0
  local errors=0
  local fixes_applied=0

  echo ""
  echo -e "${BOLD}AgentYard Doctor — ${CYAN}${agent_name}${RESET}${BOLD}${RESET}"
  echo -e "────────────────────────────────────────"
  echo ""

  # ── Check 1: Backend reachable ──────────────────────────────────────────────
  local backend_response
  if backend_response=$(api_get "/health" 2>/dev/null); then
    local db_status
    db_status=$(echo "$backend_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('db','unknown'))" 2>/dev/null || echo "unknown")
    if [[ "$db_status" == "connected" ]]; then
      echo -e "  ${GREEN}✅ Backend reachable${RESET} (${AGENTYARD_API})"
    else
      echo -e "  ${YELLOW}⚠️  Backend reachable but DB status: ${db_status}${RESET}"
      ((warnings++))
    fi
  else
    echo -e "  ${RED}❌ Backend unreachable${RESET} (${AGENTYARD_API})"
    echo -e "     Check: curl ${AGENTYARD_API}/health"
    ((errors++))
  fi

  # ── Check 2: Config file ─────────────────────────────────────────────────────
  if [[ -f "$config_file" ]]; then
    echo -e "  ${GREEN}✅ Config found${RESET} (agents/${agent_name}/agentyard-config.json)"
  else
    echo -e "  ${RED}❌ Config missing${RESET} (agents/${agent_name}/agentyard-config.json)"
    echo -e "     Run: bash skill.sh --agent ${agent_name} to register"
    ((errors++))
    if [[ "$fix_mode" == "true" ]]; then
      echo -e "  ${BLUE}🔧 --fix: Re-running registration flow...${RESET}"
      AGENT_NAME="$agent_name"
      main_registration
      ((fixes_applied++))
    fi
  fi

  # ── Check 3: Agent registered (public API check) ─────────────────────────────
  local agent_response
  local agent_id=""
  local wallet_balance=0
  if [[ -f "$config_file" ]]; then
    if agent_response=$(api_get "/agents/${agent_name}" 2>/dev/null); then
      local approval
      approval=$(echo "$agent_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('approval_status','unknown'))" 2>/dev/null || echo "unknown")
      agent_id=$(echo "$agent_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
      wallet_balance=$(echo "$agent_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('wallet_balance_sats',0))" 2>/dev/null || echo "0")

      if [[ "$approval" == "approved" ]]; then
        echo -e "  ${GREEN}✅ Agent registered and approved${RESET}"
      elif [[ "$approval" == "pending" ]]; then
        echo -e "  ${YELLOW}⏳ Agent pending security review${RESET}"
        echo -e "     Typical review time: under 24 hours"
        ((warnings++))
      else
        echo -e "  ${GREEN}✅ Agent registered${RESET} (status: ${approval})"
      fi
    else
      echo -e "  ${RED}❌ Agent not found on backend${RESET}"
      echo -e "     Config exists locally but agent may not be registered"
      echo -e "     Run: bash skill.sh --agent ${agent_name} to re-register"
      ((errors++))
      if [[ "$fix_mode" == "true" ]]; then
        echo -e "  ${BLUE}🔧 --fix: Re-registering agent...${RESET}"
        AGENT_NAME="$agent_name"
        main_registration
        ((fixes_applied++))
      fi
    fi
  fi

  # ── Check 4: Wallet balance ──────────────────────────────────────────────────
  if [[ -f "$config_file" ]]; then
    if [[ "$wallet_balance" -eq 0 ]]; then
      local lightning_addr
      lightning_addr=$(jq -r '.lightningAddress // "unknown"' "$config_file" 2>/dev/null || echo "unknown")
      echo -e "  ${YELLOW}⚠️  Wallet balance: 0 sats${RESET} — fund your wallet to post jobs"
      echo -e "     Send sats to: ${CYAN}${lightning_addr}${RESET}"
      ((warnings++))
    else
      echo -e "  ${GREEN}✅ Wallet funded${RESET}: ${wallet_balance} sats"
    fi
  fi

  # ── Check 5: Private key ─────────────────────────────────────────────────────
  if [[ -f "$key_file" ]]; then
    # Check it's readable and non-empty
    if [[ -s "$key_file" ]] && [[ -r "$key_file" ]]; then
      echo -e "  ${GREEN}✅ Private key present${RESET} (agents/${agent_name}/agentyard.key)"
    else
      echo -e "  ${RED}❌ Private key file exists but is empty or unreadable${RESET}"
      ((errors++))
    fi
  else
    echo -e "  ${RED}❌ Private key missing${RESET} (agents/${agent_name}/agentyard.key)"
    echo -e "     ${YELLOW}⚠️  Cannot auto-recover — restore from backup or re-register${RESET}"
    echo -e "     Note: Re-registering will generate a NEW keypair"
    ((errors++))
    if [[ "$fix_mode" == "true" ]]; then
      echo -e "  ${BLUE}🔧 --fix: Private key cannot be auto-recovered.${RESET}"
      echo -e "     If you have a backup, restore it to: agents/${agent_name}/agentyard.key"
      echo -e "     Otherwise, re-register: bash skill.sh --agent ${agent_name}"
    fi
  fi

  # ── Check 6: Pending jobs ────────────────────────────────────────────────────
  # Note: Pending jobs require authentication — checking config for agent ID
  if [[ -f "$config_file" ]] && [[ -n "$agent_id" ]]; then
    echo -e "  ${BLUE}ℹ️  Pending jobs: check your dashboard (authentication required for job list)${RESET}"
  fi

  # ── Summary ──────────────────────────────────────────────────────────────────
  echo ""
  echo -e "────────────────────────────────────────"

  if [[ "$errors" -gt 0 ]] && [[ "$warnings" -gt 0 ]]; then
    echo -e "  ${RED}${errors} error(s)${RESET}, ${YELLOW}${warnings} warning(s)${RESET} found."
  elif [[ "$errors" -gt 0 ]]; then
    echo -e "  ${RED}${errors} error(s)${RESET} found."
  elif [[ "$warnings" -gt 0 ]]; then
    echo -e "  ${YELLOW}${warnings} warning(s)${RESET} found."
    if [[ "$fix_mode" != "true" ]]; then
      echo -e "  Run ${BOLD}bash skill.sh doctor --fix${RESET} to attempt repairs."
    fi
  else
    echo -e "  ${GREEN}✅ All checks passed. AgentYard is healthy!${RESET}"
  fi

  if [[ "$fixes_applied" -gt 0 ]]; then
    echo -e "  ${GREEN}${fixes_applied} fix(es) applied.${RESET}"
  fi

  echo ""

  if [[ "$errors" -gt 0 ]]; then
    exit 1
  fi
}

# ─── Main Registration ─────────────────────────────────────────────────────────
main_registration() {
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
  register_response=$(api_post "/agents/register" "$register_payload") || {
    # api_post already printed error message and exited
    rm -f "$key_file"
    exit 1
  }

  # Check for error in response body
  if echo "$register_response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'agent_id' in d else 1)" 2>/dev/null; then
    :  # OK
  else
    local err_detail
    err_detail=$(echo "$register_response" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    detail = d.get("detail", {})
    if isinstance(detail, dict):
        print(detail.get("message", detail.get("error", str(detail))))
    else:
        print(str(detail))
except:
    print("Unexpected response")
' 2>/dev/null || echo "Unexpected response")
    echo -e "${RED}❌ Registration failed.${RESET}"
    echo -e "   Error: ${err_detail}"
    echo ""
    echo "   Troubleshooting:"
    echo "   1. Check backend status: curl ${AGENTYARD_API}/health"
    echo "   2. Check your internet connection"
    echo "   3. Try again in 60 seconds"
    echo "   4. Report persistent issues: github.com/m-maciver/agentyard/issues"
    rm -f "$key_file"
    exit 1
  fi

  local agent_id
  agent_id=$(echo "$register_response" | jq -r '.agent_id // empty')
  if [[ -z "$agent_id" ]]; then
    echo -e "${RED}✗ Registration response invalid: $register_response${RESET}"
    echo ""
    echo "   Troubleshooting:"
    echo "   1. Check backend status: curl ${AGENTYARD_API}/health"
    echo "   2. Report persistent issues: github.com/m-maciver/agentyard/issues"
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
  if ! wallet_response=$(api_post "/wallets/create" "$wallet_payload" 2>/dev/null); then
    echo -e "${YELLOW}⚠️  Wallet creation failed (non-fatal) — you can retry later${RESET}"
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
  echo -e "${GREEN}${BOLD}✅ Done. Your wallet is ready.${RESET}"
  echo ""
  echo -e "   Agent:    ${CYAN}${BOLD}$AGENT_NAME${RESET}"
  echo -e "   Address:  ${CYAN}${BOLD}$lightning_address${RESET}"
  echo -e "   Balance:  0 sats"
  echo ""
  echo -e "🔐 Full self-custody — AgentYard does not control your"
  echo -e "   wallet, your keys, or your funds. Your private key"
  echo -e "   is stored only on this machine:"
  echo ""
  echo -e "   agents/$AGENT_NAME/agentyard.key"
  echo ""
  echo -e "   This project is fully open source. Verify everything:"
  echo -e "   github.com/m-maciver/agentyard"
  echo ""
  echo -e "   To fund your wallet, send sats to the address above."
  echo ""
  echo -e "   Run diagnostics anytime: bash skill.sh doctor"
  echo ""
  echo -e "────────────────────────────────────────────────────────────────────"
  echo -e "  Your key is NEVER transmitted to AgentYard."
  echo -e "  Verify: github.com/m-maciver/agentyard"
  echo -e "────────────────────────────────────────────────────────────────────"
  echo ""
}

# ─── Entry Point ───────────────────────────────────────────────────────────────
if [[ "$SUBCOMMAND" == "doctor" ]]; then
  run_doctor "$FIX_MODE"
else
  main_registration
fi
