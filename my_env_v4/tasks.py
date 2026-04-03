
def load_task(level):
    return [
        {
            "email_text": "Client angry: payment failed twice",
            "sender": "client",
            "urgency_hint": "high",
            "correct_action": "escalate"
        },
        {
            "email_text": "Weekly newsletter subscription",
            "sender": "marketing",
            "urgency_hint": "low",
            "correct_action": "ignore"
        },
        {
            "email_text": "Meeting reschedule request",
            "sender": "manager",
            "urgency_hint": "medium",
            "correct_action": "reply"
        }
    ]