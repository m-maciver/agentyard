#!/bin/bash
# wallet.sh - Lightning wallet generation and management

# Generate a testnet Lightning address
# Usage: generate_lightning_address
generate_lightning_address() {
  # For MVP: Generate a deterministic testnet Lightning address
  # Format: lnbc{amount}n{random}
  
  # If lncli is available, use it
  if command -v lncli &> /dev/null; then
    local pubkey=$(lncli newaddress p2wkh 2>/dev/null | jq -r '.address' 2>/dev/null)
    if [[ -n "$pubkey" ]]; then
      echo "$pubkey"
      return 0
    fi
  fi
  
  # Fallback: Generate testnet address (clearly labeled as test)
  # Format: lnbc[test-addr-{random}]
  local random_suffix=$(head -c 16 /dev/urandom | xxd -p)
  echo "lnbc_test_${random_suffix}"
}

# Generate wallet file for agent
# Usage: create_wallet_file <wallet_path>
create_wallet_file() {
  local wallet_path="$1"
  
  if [[ -z "$wallet_path" ]]; then
    echo "Error: wallet_path required" >&2
    return 1
  fi
  
  # Ensure directory exists
  mkdir -p "$(dirname "$wallet_path")"
  
  # Generate address
  local address=$(generate_lightning_address)
  
  # Create wallet file with metadata
  cat > "$wallet_path" << EOF
{
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "address": "$address",
  "balance_sats": 0,
  "mode": "local",
  "testnet": true
}
EOF
  
  # Restrict permissions (local security)
  chmod 600 "$wallet_path"
  
  echo "$address"
}

# Read wallet balance
# Usage: get_wallet_balance <wallet_path>
get_wallet_balance() {
  local wallet_path="$1"
  
  if [[ ! -f "$wallet_path" ]]; then
    echo "0"
    return 0
  fi
  
  jq -r '.balance_sats // 0' "$wallet_path" 2>/dev/null || echo "0"
}

# Update wallet balance (local tracking only for MVP)
# Usage: update_wallet_balance <wallet_path> <amount_sats>
update_wallet_balance() {
  local wallet_path="$1"
  local amount="$2"
  
  if [[ -z "$wallet_path" || -z "$amount" ]]; then
    echo "Error: wallet_path and amount required" >&2
    return 1
  fi
  
  if [[ ! -f "$wallet_path" ]]; then
    return 1
  fi
  
  # Update balance in place
  local current_balance=$(jq -r '.balance_sats // 0' "$wallet_path" 2>/dev/null || echo "0")
  local new_balance=$((current_balance + amount))
  
  old_umask=$(umask)
  umask 077
  jq ".balance_sats = $new_balance" "$wallet_path" > "${wallet_path}.tmp" && \
  mv "${wallet_path}.tmp" "$wallet_path"
  umask "$old_umask"
}

# Get wallet address
# Usage: get_wallet_address <wallet_path>
get_wallet_address() {
  local wallet_path="$1"
  
  if [[ ! -f "$wallet_path" ]]; then
    return 1
  fi
  
  jq -r '.address' "$wallet_path" 2>/dev/null
}
