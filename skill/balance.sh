#!/bin/bash
# balance.sh - Check wallet balance

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"

# Get agent name from argument (optional, defaults to Jet)
agent_name="${1:-}"

echo ""

if [[ -z "$agent_name" ]]; then
  # Show Jet's balance
  wallet_path="$HOME/.openclaw/agentyard.key"
  
  if [[ ! -f "$wallet_path" ]]; then
    echo "❌ Jet's wallet not found. Run 'skill agentyard install' first."
    exit 1
  fi
  
  balance=$(get_wallet_balance "$wallet_path")
  address=$(get_wallet_address "$wallet_path")
  
  echo "💰 Jet's Balance"
  echo "==============="
  echo "Balance: $balance sats"
  echo "Address: $address"
  echo ""
else
  # Show agent balance
  wallet_path="agents/${agent_name}/agentyard.key"
  
  if [[ ! -f "$wallet_path" ]]; then
    echo "❌ Agent '$agent_name' wallet not found."
    echo "   Run: skill agentyard publish $agent_name"
    exit 1
  fi
  
  balance=$(get_wallet_balance "$wallet_path")
  address=$(get_wallet_address "$wallet_path")
  
  echo "💰 $agent_name's Balance"
  echo "=========================="
  echo "Balance: $balance sats"
  echo "Address: $address"
  echo ""
fi
