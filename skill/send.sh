#!/bin/bash
# send.sh - Send sats between wallets

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"
source "${script_dir}/lib/email.sh"

# Parse arguments
sender_agent="${1:-}"
receiver_agent="${2:-}"
amount="${3:-}"

if [[ -z "$sender_agent" || -z "$receiver_agent" || -z "$amount" ]]; then
  echo "Usage: $0 <sender_agent> <receiver_agent> <amount_sats>"
  echo "Example: $0 pixel jet 2000"
  exit 1
fi

# Validate amount
if ! [[ "$amount" =~ ^[0-9]+$ ]]; then
  echo "Error: Amount must be a number"
  exit 1
fi

echo ""
echo "💸 Send Sats"
echo "============"
echo ""

# Get sender wallet
sender_wallet="agents/${sender_agent}/agentyard.key"
if [[ ! -f "$sender_wallet" ]]; then
  echo "Error: Sender wallet 'agents/${sender_agent}/agentyard.key' not found"
  exit 1
fi

# Get receiver wallet
receiver_wallet="agents/${receiver_agent}/agentyard.key"
if [[ ! -f "$receiver_wallet" ]]; then
  receiver_wallet="$HOME/.openclaw/agentyard.key"
fi

if [[ ! -f "$receiver_wallet" ]]; then
  echo "Error: Receiver wallet 'agents/${receiver_agent}/agentyard.key' or Jet's wallet not found"
  exit 1
fi

# Check sender balance
sender_balance=$(get_wallet_balance "$sender_wallet")

if [[ $sender_balance -lt $amount ]]; then
  echo "❌ Insufficient balance"
  echo "   Available: $sender_balance sats"
  echo "   Requested: $amount sats"
  exit 1
fi

echo "⏳ Processing payment..."
echo "  From: $sender_agent"
echo "  To: $receiver_agent"
echo "  Amount: $amount sats"
echo ""

# Deduct from sender
update_wallet_balance "$sender_wallet" "-$amount"

# Add to receiver
update_wallet_balance "$receiver_wallet" "$amount"

echo "✓ Payment sent!"
echo ""
echo "📊 Updated Balances:"

sender_new_balance=$(get_wallet_balance "$sender_wallet")
receiver_new_balance=$(get_wallet_balance "$receiver_wallet")

echo "  $sender_agent: $sender_new_balance sats"
echo "  $receiver_agent: $receiver_new_balance sats"
echo ""
