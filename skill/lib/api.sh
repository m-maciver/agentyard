#!/bin/bash
# api.sh - Backend API integration

# Default backend URL (can be overridden by environment)
AGENTYARD_API="${AGENTYARD_API:-http://localhost:3000/api}"

# Register agent on marketplace
# Usage: register_agent <agent_config_json>
register_agent() {
  local agent_config="$1"
  
  if [[ -z "$agent_config" ]]; then
    echo "Error: agent_config required" >&2
    return 1
  fi
  
  # For MVP: Just validate the config locally
  # Backend registration would go here:
  # curl -X POST "$AGENTYARD_API/agents/register" \
  #   -H "Content-Type: application/json" \
  #   -d "$agent_config"
  
  echo "✓ Agent registered locally (backend endpoint: $AGENTYARD_API/agents/register)"
  return 0
}

# Search marketplace for agents
# Usage: search_agents <specialty>
search_agents() {
  local specialty="$1"
  
  if [[ -z "$specialty" ]]; then
    echo "Error: specialty required" >&2
    return 1
  fi
  
  # For MVP: Search local agent directories
  # Backend search would go here:
  # curl -X GET "$AGENTYARD_API/agents/search?specialty=$specialty"
  
  search_local_agents "$specialty"
}

# Search local agents
# Usage: search_local_agents <specialty>
search_local_agents() {
  local specialty="$1"
  
  if [[ ! -d "agents" ]]; then
    return 0
  fi
  
  echo "📋 Agents matching '$specialty':"
  echo ""
  
  for agent_dir in agents/*/; do
    if [[ -f "${agent_dir}agentyard.json" ]]; then
      local config=$(cat "${agent_dir}agentyard.json" 2>/dev/null)
      local agent_specialty=$(echo "$config" | jq -r '.specialty // ""')
      
      if [[ "$agent_specialty" == *"$specialty"* ]]; then
        local agent_name=$(echo "$config" | jq -r '.agent_name // ""')
        local price=$(echo "$config" | jq -r '.price_sats // 0')
        
        echo "  • $agent_name (specialty: $agent_specialty) - $price sats"
      fi
    fi
  done
}

# Query agent from marketplace
# Usage: get_agent_info <agent_name>
get_agent_info() {
  local agent_name="$1"
  
  if [[ -z "$agent_name" ]]; then
    echo "Error: agent_name required" >&2
    return 1
  fi
  
  # Check local config first
  if [[ -f "agents/${agent_name}/agentyard.json" ]]; then
    cat "agents/${agent_name}/agentyard.json"
    return 0
  fi
  
  # Backend query would go here:
  # curl -X GET "$AGENTYARD_API/agents/${agent_name}"
  
  return 1
}

# Create hiring record
# Usage: create_hire_record <buyer_agent> <seller_agent> <amount_sats> <task_description>
create_hire_record() {
  local buyer_agent="$1"
  local seller_agent="$2"
  local amount="$3"
  local task_desc="$4"
  
  if [[ -z "$buyer_agent" || -z "$seller_agent" || -z "$amount" ]]; then
    echo "Error: buyer_agent, seller_agent, and amount required" >&2
    return 1
  fi
  
  # Create hire record locally
  local hire_id=$(date +%s)-$(head -c 8 /dev/urandom | xxd -p)
  local hire_record="{
    \"hire_id\": \"$hire_id\",
    \"buyer\": \"$buyer_agent\",
    \"seller\": \"$seller_agent\",
    \"amount_sats\": $amount,
    \"task\": \"$task_desc\",
    \"created_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"status\": \"pending\"
  }"
  
  echo "$hire_record"
}
