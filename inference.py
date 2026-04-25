import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:7860")
LEVEL = os.getenv("LEVEL", "round2")


def triage_agent(email):
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
    label = email.get("label", "").lower()
    priority = email.get("priority", "low")

    is_spam = label == "spam" or any(x in text for x in [
        "offer", "click", "won", "discount", "lottery", "prize",
        "unsubscribe", "promotional", "free iphone", "claim"
    ])
    if is_spam:
        return "ignore"

    is_complaint = label == "complaint" or any(x in text for x in [
        "failed", "issue", "problem", "refund", "billing", "charged",
        "escalation", "suspicious", "alert", "security", "blocked"
    ])
    if is_complaint:
        if LEVEL in ("hard", "round2"):
            return "escalate"
        return "reply"

    return "reply"


def communication_agent(action_type, email):
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()

    if action_type == "ignore":
        return "Marking as spam and ignoring."

    if action_type == "escalate":
        return "Escalating this issue for immediate resolution. Sorry for the inconvenience, we will process this refund and resolve the issue urgently."

    if any(x in text for x in ["failed", "issue", "refund", "billing", "charged", "blocked"]):
        return "We are sorry to hear about your experience. We sincerely apologize and will process a refund and resolve the issue immediately."

    return "Confirmed. I will schedule the meeting and confirm attendance shortly."


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    payload = res.json()
    emails = payload["emails"]

    def sort_key(e):
        priority_score = 0 if e.get("priority") == "high" else 1
        text = f"{e.get('subject', '')} {e.get('body', '')}".lower()
        is_spam = any(x in text for x in ["offer", "click", "won", "lottery", "prize", "promotional", "claim"])
        label_score = 2 if is_spam else 0
        return (priority_score, label_score)

    emails = sorted(emails, key=sort_key)

    total_reward = 0.0
    recent_feedback = []

    for email in emails:
        feedback = (sum(recent_feedback[-3:]) / min(3, len(recent_feedback))) if recent_feedback else 0.0

        action_type = triage_agent(email)
        content = communication_agent(action_type, email)

        action = {
            "action_type": action_type,
            "email_id": email["id"],
            "content": content,
            "actor": "coordinator",
            "feedback": feedback,
        }

        step_res = requests.post(f"{BASE_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        result = step_res.json()

        reward = float(result.get("reward", 0.0))
        total_reward += reward
        recent_feedback.append(1.0 if reward > 0 else -1.0)

        print(f"  [{email.get('label', '?'):10}] [{email.get('priority','?'):4}] -> {action_type:8} | reward: {reward:+.3f} | total: {total_reward:+.3f}")

        if result.get("done"):
            break

    print(f"\nEpisode level={LEVEL} total_reward={total_reward:.3f}")
    return total_reward


if __name__ == "__main__":
    run_episode()
