def load_task(level):
    return [
        {
            "email_text": "Client angry: payment failed twice",
            "sender": "client",
            "urgency_hint": "high",
            "correct_action": "escalate"
        },
        {
            "email_text": "Hey just checking in, no rush",
            "sender": "manager",
            "urgency_hint": "low",
            "correct_action": "reply"
        },
        {
            "email_text": "🔥 LIMITED TIME OFFER!!! CLICK NOW",
            "sender": "unknown",
            "urgency_hint": "high",
            "correct_action": "ignore"
        },
        {
            "email_text": "Security alert: suspicious login detected",
            "sender": "security",
            "urgency_hint": "medium",
            "correct_action": "escalate"
        }
    ]