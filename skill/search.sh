#!/bin/bash
# search.sh - Search marketplace for agents

set -e

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source library files
source "${script_dir}/lib/api.sh"

# Parse arguments
specialty="${1:-}"

if [[ -z "$specialty" ]]; then
  echo "Usage: $0 <specialty>"
  echo "Examples: $0 design"
  echo "          $0 coding"
  echo "          $0 writing"
  exit 1
fi

echo ""
search_agents "$specialty"
echo ""
