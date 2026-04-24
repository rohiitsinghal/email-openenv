import requests

BASE_URL = "http://localhost:8000"

def triage_agent(email):
    text = f"{email['subject']} {email['body']}".lower()
    if any(x in text for x in ["offer", "click", "won", "discount", "lottery", "prize"]):
        return "ignore"
    if email.get("priority") == "high" and "client" in text:
        return "escalate"
    if "failed" in text or "urgent" in text or "security" in text:
        return "escalate"
    return "reply"


def planning_agent(email):
    if email.get("domain") == "personal" and email.get("priority") == "high":
        return "Protect this slot today"
    if email.get("due_day", 14) <= 3:
        return "Schedule immediate handling"
    return "Handle in current cycle"


def communication_agent(action_type):
    if action_type == "reply":
        return "Acknowledged. I will take action and follow up shortly."
    if action_type == "escalate":
        return "Escalating this issue to the right owner now."
    return "No response required."


def run():
    res = requests.post(f"{BASE_URL}/reset?level=round2").json()
    emails = res["emails"]

    total_reward = 0
    recent_feedback = []

    for email in emails:
        email_id = email["id"]
        proposed_action = triage_agent(email)
        _ = planning_agent(email)
        message = communication_agent(proposed_action)

        feedback = 0.0
        if recent_feedback:
            feedback = sum(recent_feedback[-3:]) / min(3, len(recent_feedback))

        # If recent outcomes are weak, become more conservative on high-priority items.
        if feedback < 0 and email.get("priority") == "high" and proposed_action == "reply":
            proposed_action = "escalate"

        action = {
            "action_type": proposed_action,
            "email_id": email_id,
            "content": message,
            "actor": "coordinator",
            "feedback": feedback,
        }
        r = requests.post(f"{BASE_URL}/step", json=action).json()
        reward = r["reward"]
        total_reward += reward
        recent_feedback.append(1.0 if reward > 0 else -1.0)

        if r.get("done"):
            break

    print("Final Reward:", total_reward)


if __name__ == "__main__":
    run()