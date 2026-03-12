#!/bin/bash
# email.sh — Email delivery via Resend API
# Sends task output and notifications to users.

RESEND_API_KEY="${RESEND_API_KEY:-}"
RESEND_FROM="${RESEND_FROM:-AgentYard <notifications@agentyard.dev>}"

# ── Check if email is configured ──
_email_configured() {
  [[ -n "$RESEND_API_KEY" ]]
}

# ── Send email via Resend ──
# Usage: _send_email <to> <subject> <html_body>
_send_email() {
  local to="$1"
  local subject="$2"
  local html_body="$3"

  if ! _email_configured; then
    echo "  [email] Would send to $to: $subject" >&2
    return 0
  fi

  local response
  response=$(curl -s -w "\n%{http_code}" \
    --connect-timeout 10 --max-time 15 \
    -X POST "https://api.resend.com/emails" \
    -H "Authorization: Bearer $RESEND_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"from\": \"$RESEND_FROM\",
      \"to\": \"$to\",
      \"subject\": \"$subject\",
      \"html\": \"$html_body\"
    }" 2>/dev/null)

  local http_code=$(echo "$response" | tail -1)

  if [[ "$http_code" == "200" || "$http_code" == "201" ]]; then
    return 0
  fi

  echo "  [email] Failed to send (HTTP $http_code)" >&2
  return 1
}

# ── Send hire notification ──
# Usage: send_hire_notification <email> <agent_name> <task> <amount_sats>
send_hire_notification() {
  local email="$1"
  local agent_name="$2"
  local task="$3"
  local amount="$4"

  if [[ -z "$email" || "$email" == "not-set" ]]; then
    return 0
  fi

  local subject="Task assigned to ${agent_name} — ${amount} sats"
  local body="<div style='font-family: Inter, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 0;'>"
  body+="<h2 style='font-size: 20px; font-weight: 700; margin: 0 0 16px;'>Task assigned</h2>"
  body+="<p style='color: #71717a; line-height: 1.6;'><strong style='color: #09090b;'>${agent_name}</strong> has been hired for this task:</p>"
  body+="<div style='background: #f4f4f5; border-radius: 8px; padding: 16px; margin: 16px 0;'>"
  body+="<p style='margin: 0; color: #09090b;'>${task}</p></div>"
  body+="<p style='color: #71717a;'>Payment: <strong style='color: #09090b;'>${amount} sats</strong></p>"
  body+="<p style='color: #a1a1aa; font-size: 13px; margin-top: 24px;'>Results will be delivered to this email once complete.</p>"
  body+="</div>"

  _send_email "$email" "$subject" "$body"
}

# ── Send task delivery ──
# Usage: send_task_delivery <email> <agent_name> <task> <output_content>
send_task_delivery() {
  local email="$1"
  local agent_name="$2"
  local task="$3"
  local output="$4"

  if [[ -z "$email" || "$email" == "not-set" ]]; then
    return 0
  fi

  local subject="Task complete — ${agent_name} delivered results"
  local body="<div style='font-family: Inter, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 0;'>"
  body+="<h2 style='font-size: 20px; font-weight: 700; margin: 0 0 16px;'>Task complete</h2>"
  body+="<p style='color: #71717a; line-height: 1.6;'><strong style='color: #09090b;'>${agent_name}</strong> has completed the task:</p>"
  body+="<div style='background: #f4f4f5; border-radius: 8px; padding: 16px; margin: 16px 0;'>"
  body+="<p style='margin: 0 0 8px; color: #a1a1aa; font-size: 13px;'>Task</p>"
  body+="<p style='margin: 0; color: #09090b;'>${task}</p></div>"
  body+="<div style='background: #f4f4f5; border-radius: 8px; padding: 16px; margin: 16px 0;'>"
  body+="<p style='margin: 0 0 8px; color: #a1a1aa; font-size: 13px;'>Output</p>"
  body+="<pre style='margin: 0; color: #09090b; white-space: pre-wrap; font-size: 14px;'>${output}</pre></div>"
  body+="<p style='color: #a1a1aa; font-size: 13px; margin-top: 24px;'>This output was scanned for integrity before delivery.</p>"
  body+="</div>"

  _send_email "$email" "$subject" "$body"
}

# ── Send payment confirmation ──
# Usage: send_payment_confirmation <email> <amount_sats> <sender> <note>
send_payment_confirmation() {
  local email="$1"
  local amount="$2"
  local sender="$3"
  local note="${4:-}"

  if [[ -z "$email" || "$email" == "not-set" ]]; then
    return 0
  fi

  local subject="Payment received — ${amount} sats from ${sender}"
  local body="<div style='font-family: Inter, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 0;'>"
  body+="<h2 style='font-size: 20px; font-weight: 700; margin: 0 0 16px;'>Payment received</h2>"
  body+="<p style='color: #71717a;'>Amount: <strong style='color: #09090b;'>${amount} sats</strong></p>"
  body+="<p style='color: #71717a;'>From: <strong style='color: #09090b;'>${sender}</strong></p>"
  [[ -n "$note" ]] && body+="<p style='color: #71717a;'>Note: ${note}</p>"
  body+="</div>"

  _send_email "$email" "$subject" "$body"
}
