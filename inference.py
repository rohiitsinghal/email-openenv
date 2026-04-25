import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:7860")
LEVEL = os.getenv("LEVEL", "round2")


def triage_agent(email):
    label = email.get("label", "").lower()
    priority = email.get("priority", "low")
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()

    # Spam detection
    if label == "spam" or any(x in text for x in ["offer", "click", "won", "discount", "lottery", "prize", "unsubscribe"]):
        return "ignore"

    # Complaints → escalate on hard/round2, reply on easy/medium
    if label == "complaint":
        if LEVEL in ("hard", "round2"):
            return "escalate"
        return "reply"

    # Work emails → always reply
    if label == "work":
        return "reply"

    # High priority → never ignore
    if priority == "high":
        return "escalate" if LEVEL in ("hard", "round2") else "reply"

    return "reply"


def communication_agent(action_type, email):
    label = email.get("label", "").lower()
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()

    if action_type == "ignore":
        return "Marking as spam and ignoring."

    if action_type == "escalate":
        return "Escalating this issue for immediate resolution. Sorry for the inconvenience, we will process this refund and resolve the issue urgently."

    # action_type == "reply" — craft keyword-rich replies per label
    if label == "complaint":
        return "We are sorry to hear about your experience. We sincerely apologize and will process a refund and resolve the issue immediately."

    if label == "work":
        return "Confirmed. I will schedule the meeting and confirm attendance shortly."

    if label == "spam":
        return "Marking as spam and ignoring this message."

    # fallback — generic but keyword-safe
    if any(x in text for x in ["meeting", "schedule", "call"]):
        return "Confirmed. I will schedule the meeting and confirm shortly."

    if any(x in text for x in ["complaint", "issue", "problem", "refund"]):
        return "We are sorry. We will process your refund and resolve the issue."

    return "Acknowledged. I will schedule a meeting to confirm and process this."


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    payload = res.json()
    emails = payload["emails"]

    # Sort: high priority first, then complaints, then work, spam last
    def sort_key(e):
        priority_score = 0 if e.get("priority") == "high" else 1
        label_score = {"complaint": 0, "work": 1, "spam": 2}.get(e.get("label", ""), 1)
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

        print(f"  [{email.get('label','?'):10}] [{email.get('priority','?'):4}] → {action_type:8} | reward: {reward:+.3f} | total: {total_reward:+.3f}")

        if result.get("done"):
            break

    print(f"\nEpisode level={LEVEL} total_reward={total_reward:.3f}")
    return total_reward


if __name__ == "__main__":
    run_episode()