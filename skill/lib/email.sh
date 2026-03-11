#!/bin/bash
# email.sh - Email integration (Resend API)

# Send hire notification email
# Usage: send_hire_notification <recipient_email> <agent_name> <task_description> <amount_sats>
send_hire_notification() {
  local recipient_email="$1"
  local agent_name="$2"
  local task_desc="$3"
  local amount="$4"
  
  if [[ -z "$recipient_email" || -z "$agent_name" || -z "$task_desc" || -z "$amount" ]]; then
    echo "Error: recipient_email, agent_name, task_desc, and amount required" >&2
    return 1
  fi
  
  # For MVP: Log locally instead of actually sending
  echo "[EMAIL] Hire notification to $recipient_email"
  echo "  Agent: $agent_name"
  echo "  Task: $task_desc"
  echo "  Amount: $amount sats"
  
  # Actual Resend integration would go here:
  # curl -X POST "https://api.resend.com/emails" \
  #   -H "Authorization: Bearer $RESEND_API_KEY" \
  #   -H "Content-Type: application/json" \
  #   -d "{
  #     \"from\": \"agentyard@example.com\",
  #     \"to\": \"$recipient_email\",
  #     \"subject\": \"You've been hired! 🎉\",
  #     \"html\": \"<p>$agent_name, you have a new job!</p><p>Task: $task_desc</p><p>Payment: $amount sats</p>\"
  #   }"
  
  return 0
}

# Send payment confirmation email
# Usage: send_payment_confirmation <recipient_email> <amount_sats> <sender_agent> <note>
send_payment_confirmation() {
  local recipient_email="$1"
  local amount="$2"
  local sender="$3"
  local note="${4:-No note}"
  
  if [[ -z "$recipient_email" || -z "$amount" || -z "$sender" ]]; then
    echo "Error: recipient_email, amount, and sender required" >&2
    return 1
  fi
  
  echo "[EMAIL] Payment confirmation to $recipient_email"
  echo "  From: $sender"
  echo "  Amount: $amount sats"
  echo "  Note: $note"
  
  return 0
}

# Send completion notification email
# Usage: send_completion_notification <recipient_email> <agent_name> <task_description>
send_completion_notification() {
  local recipient_email="$1"
  local agent_name="$2"
  local task_desc="$3"
  
  if [[ -z "$recipient_email" || -z "$agent_name" ]]; then
    echo "Error: recipient_email and agent_name required" >&2
    return 1
  fi
  
  echo "[EMAIL] Task completion notification to $recipient_email"
  echo "  Agent: $agent_name"
  echo "  Task completed: $task_desc"
  
  return 0
}
