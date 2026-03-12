#!/bin/bash
# publish.sh - Publish agent as marketplace seller

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"
source "${script_dir}/lib/api.sh"

# Get agent name from argument
agent_name="${1:-}"

if [[ -z "$agent_name" ]]; then
  echo "Usage: $0 <agent_name>"
  echo "Example: $0 pixel"
  exit 1
fi

validate_agent_name "$agent_name" || exit 1

# Check if agent exists
if [[ ! -d "agents/${agent_name}" ]]; then
  echo "Error: Agent 'agents/${agent_name}' not found"
  exit 1
fi

echo ""
echo "📢 Publishing Agent: $agent_name"
echo "=============================="
echo ""

# Read SOUL.md if it exists
soul_content=""
if [[ -f "agents/${agent_name}/SOUL.md" ]]; then
  soul_content=$(read_agent_soul "$agent_name")
fi

# Extract agent info
agent_display_name=$(extract_agent_name "$agent_name" "$soul_content")
specialty=$(extract_specialty "$soul_content")

# Prompt for specialty if not found
if [[ -z "$specialty" ]]; then
  read -p "🎯 Enter agent specialty (e.g., design, coding, writing): " specialty
  if [[ -z "$specialty" ]]; then
    echo "Error: Specialty required"
    exit 1
  fi
fi

# Prompt for price
read -p "💰 Enter price in sats (default 5000): " price_sats
price_sats="${price_sats:-5000}"

# Validate price is a number
if ! [[ "$price_sats" =~ ^[0-9]+$ ]]; then
  echo "Error: Price must be a number"
  exit 1
fi

echo ""
echo "⏳ Creating wallet for $agent_display_name..."

# Create wallet for this agent
wallet_address=$(create_wallet_file "agents/${agent_name}/agentyard.key")
echo "✓ Wallet created: $wallet_address"
echo ""

# Create config
agent_id="${agent_name}_$(date +%s | tail -c 7)"
config="{
  \"agent_id\": \"$agent_id\",
  \"agent_name\": \"$agent_display_name\",
  \"specialty\": \"$specialty\",
  \"lightning_address\": \"$wallet_address\",
  \"price_sats\": $price_sats,
  \"email\": \"seller@agentyard.local\",
  \"mode\": \"seller\",
  \"earnings_sats\": 0,
  \"registered_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
}"

# Save config
write_agent_config "$agent_name" "$config"
echo "✓ Config saved"
echo ""

# Register with backend (local for MVP)
register_agent "$config"
echo ""

echo "✓ Agent published!"
echo ""
echo "📊 Agent Details:"
echo "  Name: $agent_display_name"
echo "  Specialty: $specialty"
echo "  Price: $price_sats sats"
echo "  Wallet: $wallet_address"
echo "  ID: $agent_id"
echo ""
echo "🔗 Marketplace: https://agentyard.local/agents/$agent_id"
echo ""
