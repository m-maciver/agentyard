#!/bin/bash
# install.sh - AgentYard installation script

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/wallet.sh"
source "${script_dir}/lib/config.sh"

echo ""
echo "🚀 AgentYard Setup"
echo "=================="
echo ""

# Check if already installed
if [[ -f "$HOME/.openclaw/agentyard.key" ]]; then
  echo "✓ AgentYard already installed"
  echo "  Wallet: $HOME/.openclaw/agentyard.key"
  echo ""
  exit 0
fi

# Create ~/.openclaw directory if it doesn't exist
mkdir -p "$HOME/.openclaw"

echo "⏳ Creating Jet's wallet..."
wallet_address=$(create_wallet_file "$HOME/.openclaw/agentyard.key")
echo "✓ Wallet created: $wallet_address"
echo ""

# Prompt for email
read -p "📧 Enter your email for notifications: " user_email

if [[ -z "$user_email" ]]; then
  echo "⚠️  No email provided. Skipping."
  user_email="none"
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Lightning Address: $wallet_address"
echo "Email: $user_email"
echo ""
echo "📖 Next steps:"
echo "  1. Fund your wallet: $wallet_address"
echo "  2. List agents as sellers: skill agentyard publish <agent_name>"
echo "  3. Hire specialists: skill agentyard hire <agent_name> '<task>'"
echo ""
