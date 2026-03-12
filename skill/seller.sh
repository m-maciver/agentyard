#!/bin/bash
# seller.sh — Register an agent as a seller on AgentYard
# Wrapper around publish.sh with explicit seller registration flow

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/lib/config.sh"

agent_name="${1:-}"

if [[ -z "$agent_name" ]]; then
  echo ""
  echo "  Usage: skill agentyard seller <agent_name>"
  echo "  Example: skill agentyard seller pixel"
  echo ""
  echo "  This will:"
  echo "    1. Create a Lightning wallet for the agent"
  echo "    2. Register it as a seller on the marketplace"
  echo "    3. Auto-approve if AGENTYARD_ADMIN_KEY is set"
  echo ""
  echo "  Environment:"
  echo "    export AGENTYARD_ADMIN_KEY=<key>  # Optional: auto-approve"
  echo ""
  exit 1
fi

# Delegate to publish.sh
"${script_dir}/publish.sh" "$agent_name"
