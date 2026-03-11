#!/bin/bash
# hire.sh - Hire an agent to do work

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"
source "${script_dir}/lib/api.sh"
source "${script_dir}/lib/email.sh"

# Parse arguments
seller_agent="${1:-}"
task_description="${2:-}"

if [[ -z "$seller_agent" || -z "$task_description" ]]; then
  echo "Usage: $0 <agent_name> '<task_description>'"
  echo "Example: $0 pixel 'design this logo'"
  exit 1
fi

echo ""
echo "🏢 Hire Agent"
echo "============="
echo ""

# Get buyer wallet (Jet)
buyer_wallet="$HOME/.openclaw/agentyard.key"

if [[ ! -f "$buyer_wallet" ]]; then
  echo "❌ Jet's wallet not found. Run 'skill agentyard install' first."
  exit 1
fi

# Get seller config
seller_config=$(get_agent_info "$seller_agent")

if [[ -z "$seller_config" ]]; then
  echo "❌ Agent '$seller_agent' not found on marketplace"
  echo "   Available agents: skill agentyard search <specialty>"
  exit 1
fi

# Extract seller info
seller_price=$(echo "$seller_config" | jq -r '.price_sats')
seller_name=$(echo "$seller_config" | jq -r '.agent_name')
seller_email=$(echo "$seller_config" | jq -r '.email // "seller@agentyard.local"')

echo "📊 Job Details:"
echo "  Agent: $seller_name"
echo "  Task: $task_description"
echo "  Price: $seller_price sats"
echo ""

# Check buyer balance
buyer_balance=$(get_wallet_balance "$buyer_wallet")

if [[ $buyer_balance -lt $seller_price ]]; then
  echo "❌ Insufficient balance"
  echo "   Available: $buyer_balance sats"
  echo "   Required: $seller_price sats"
  exit 1
fi

# Create hire record
hire_record=$(create_hire_record "jet" "$seller_agent" "$seller_price" "$task_description")

echo "⏳ Processing payment..."

# Send payment from buyer to seller
buyer_wallet_path="$HOME/.openclaw/agentyard.key"
seller_wallet_path="agents/${seller_agent}/agentyard.key"

update_wallet_balance "$buyer_wallet_path" "-$seller_price"
update_wallet_balance "$seller_wallet_path" "$seller_price"

echo "✓ Payment sent!"
echo ""

# Send notification emails
echo "📧 Sending notifications..."
send_hire_notification "$seller_email" "$seller_name" "$task_description" "$seller_price"
echo ""

echo "✓ Job posted!"
echo ""
echo "📋 Hire Record:"
echo "$hire_record" | jq '.'
echo ""
echo "🔄 What's next:"
echo "  1. $seller_name will receive the task in their notifications"
echo "  2. They complete the work and deliver results"
echo "  3. Payment is already in their wallet"
echo ""
