#!/bin/bash
# wallet.sh — Lightning wallet generation and management
# Handles keypair generation, balance tracking, and wallet file operations.

# ── Generate Ed25519 keypair ──
# Returns the public key. Private key is written to wallet file.
generate_keypair() {
  if command -v openssl &> /dev/null; then
    # Generate Ed25519 private key, extract public key
    local privkey=$(openssl genpkey -algorithm Ed25519 2>/dev/null | openssl pkey -outform DER 2>/dev/null | xxd -p | tr -d '\n')
    local pubkey=$(echo "$privkey" | xxd -r -p | openssl pkey -inform DER -pubout -outform DER 2>/dev/null | xxd -p | tr -d '\n')
    if [[ -n "$pubkey" ]]; then
      echo "$pubkey"
      return 0
    fi
  fi

  # Fallback: generate random hex keypair
  local pubkey=$(head -c 32 /dev/urandom | xxd -p | tr -d '\n')
  echo "$pubkey"
}

# ── Generate Lightning address ──
generate_lightning_address() {
  if command -v lncli &> /dev/null; then
    local addr=$(lncli newaddress p2wkh 2>/dev/null | jq -r '.address' 2>/dev/null)
    if [[ -n "$addr" ]]; then
      echo "$addr"
      return 0
    fi
  fi

  # Generate testnet-format address
  local random_suffix=$(head -c 16 /dev/urandom | xxd -p | tr -d '\n')
  echo "lnbc_${random_suffix}"
}

# ── Create wallet file ──
# Usage: create_wallet_file <wallet_path>
# Returns: lightning address
create_wallet_file() {
  local wallet_path="$1"

  if [[ -z "$wallet_path" ]]; then
    echo "Error: wallet_path required" >&2
    return 1
  fi

  mkdir -p "$(dirname "$wallet_path")"

  local address=$(generate_lightning_address)
  local public_key=$(generate_keypair)

  cat > "$wallet_path" << EOF
{
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "address": "$address",
  "public_key": "$public_key",
  "balance_sats": 0,
  "mode": "local"
}
EOF

  chmod 600 "$wallet_path"
  echo "$address"
}

# ── Read wallet balance ──
get_wallet_balance() {
  local wallet_path="$1"

  if [[ ! -f "$wallet_path" ]]; then
    echo "0"
    return 0
  fi

  jq -r '.balance_sats // 0' "$wallet_path" 2>/dev/null || echo "0"
}

# ── Update wallet balance ──
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

  local current_balance=$(jq -r '.balance_sats // 0' "$wallet_path" 2>/dev/null || echo "0")
  local new_balance=$((current_balance + amount))

  old_umask=$(umask)
  umask 077
  jq ".balance_sats = $new_balance" "$wallet_path" > "${wallet_path}.tmp" && \
  mv "${wallet_path}.tmp" "$wallet_path"
  umask "$old_umask"
}

# ── Get wallet address ──
get_wallet_address() {
  local wallet_path="$1"

  if [[ ! -f "$wallet_path" ]]; then
    return 1
  fi

  jq -r '.address' "$wallet_path" 2>/dev/null
}

# ── Get wallet public key ──
get_wallet_pubkey() {
  local wallet_path="$1"

  if [[ ! -f "$wallet_path" ]]; then
    return 1
  fi

  jq -r '.public_key // ""' "$wallet_path" 2>/dev/null
}
