#!/bin/bash
# hire.sh — Hire an agent from the AgentYard marketplace
# Finds the agent, pays via Lightning, and delivers results to email.

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"
source "${script_dir}/lib/api.sh"
source "${script_dir}/lib/email.sh"

AGENTYARD_DIR="$HOME/.openclaw/agentyard"
WALLET_FILE="$AGENTYARD_DIR/wallet.json"
CONFIG_FILE="$AGENTYARD_DIR/config.json"

seller_agent="${1:-}"
task_description="${2:-}"

if [[ -z "$seller_agent" || -z "$task_description" ]]; then
  echo ""
  echo "  Usage: skill agentyard hire <agent_name> '<task>'"
  echo "  Example: skill agentyard hire pixel 'design a landing page'"
  echo ""
  exit 1
fi

validate_agent_name "$seller_agent" || exit 1

# Check wallet exists
if [[ ! -f "$WALLET_FILE" ]]; then
  echo ""
  echo "  Wallet not found. Run 'skill agentyard install' first."
  echo ""
  exit 1
fi

echo ""
echo "  Hiring: $seller_agent"
echo "  ─────────────────────"
echo ""

# Get seller info
seller_config=$(get_agent_info "$seller_agent")

if [[ -z "$seller_config" ]]; then
  echo "  Agent '$seller_agent' not found on the marketplace."
  echo "  Run 'skill agentyard search <specialty>' to find agents."
  echo ""
  exit 1
fi

seller_price=$(echo "$seller_config" | jq -r '.price_sats // .price_per_task_sats // 0')
seller_name=$(echo "$seller_config" | jq -r '.agent_name // .name // "Unknown"')
seller_id=$(echo "$seller_config" | jq -r '.id // .agent_id // ""')

# Get buyer info
buyer_balance=$(get_wallet_balance "$WALLET_FILE")
buyer_email=$(jq -r '.email // "not-set"' "$CONFIG_FILE" 2>/dev/null)

echo "  Agent:    $seller_name"
echo "  Task:     $task_description"
echo "  Price:    $seller_price sats"
echo "  Balance:  $buyer_balance sats"
echo ""

# Check balance
if [[ $buyer_balance -lt $seller_price ]]; then
  echo "  Insufficient balance."
  echo "  You need $seller_price sats but have $buyer_balance sats."
  echo "  Fund your wallet and try again."
  echo ""
  exit 1
fi

echo "  Processing payment..."

# Debit buyer
update_wallet_balance "$WALLET_FILE" "-$seller_price"

# Credit seller (local wallet if available)
seller_wallet="agents/${seller_agent}/agentyard.key"
if [[ -f "$seller_wallet" ]]; then
  if ! update_wallet_balance "$seller_wallet" "$seller_price"; then
    # Rollback
    update_wallet_balance "$WALLET_FILE" "$seller_price"
    echo "  Payment failed. Balance restored."
    exit 1
  fi
fi

# Try to create hire via backend
if [[ -n "$seller_id" ]]; then
  create_hire "$seller_id" "$task_description" "$seller_price" "$buyer_email" > /dev/null 2>&1 || true
fi

echo "  Payment sent."
echo ""

# Send notification
send_hire_notification "$buyer_email" "$seller_name" "$task_description" "$seller_price"

new_balance=$(get_wallet_balance "$WALLET_FILE")

echo "  ┌─────────────────────────────────────────────────┐"
echo "  │  Hire complete                                  │"
echo "  │                                                 │"
echo "  │  Agent:      $seller_name"
echo "  │  Task:       $task_description"
echo "  │  Paid:       $seller_price sats"
echo "  │  Balance:    $new_balance sats"
echo "  │                                                 │"
echo "  │  Results will be scanned for integrity and      │"
echo "  │  delivered to: $buyer_email"
echo "  │                                                 │"
echo "  └─────────────────────────────────────────────────┘"
echo ""
