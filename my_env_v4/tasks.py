def load_task(level):
    if level == "easy":
        return [
            {
                "email_text": "Meeting scheduled for tomorrow",
                "sender": "manager",
                "urgency_hint": "low",
                "correct_action": "reply"
            },
            {
                "email_text": "🔥 LIMITED TIME OFFER!!! CLICK NOW",
                "sender": "unknown",
                "urgency_hint": "high",
                "correct_action": "ignore"
            }
        ]

    elif level == "medium":
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
                "email_text": "Newsletter: weekly tech updates",
                "sender": "unknown",
                "urgency_hint": "low",
                "correct_action": "ignore"
            }
        ]

    elif level == "hard":
        return [
            {
                "email_text": "Account issue, not urgent but confusing",
                "sender": "client",
                "urgency_hint": "medium",
                "correct_action": "reply"
            },
            {
                "email_text": "Security alert: suspicious login detected",
                "sender": "security",
                "urgency_hint": "medium",
                "correct_action": "escalate"
            },
            {
                "email_text": "Special discount just for you, act fast!",
                "sender": "unknown",
                "urgency_hint": "high",
                "correct_action": "ignore"
            },
            {
                "email_text": "Following up on last week's discussion",
                "sender": "manager",
                "urgency_hint": "medium",
                "correct_action": "reply"
            }
        ]

    else:
        return []