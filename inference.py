import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
LEVEL = os.getenv("LEVEL", "round2")


def triage_agent(email):
    text = f"{email['subject']} {email['body']}".lower()
    if any(x in text for x in ["offer", "click", "won", "discount", "lottery", "prize"]):
        return "ignore"
    if email.get("priority") == "high" and any(x in text for x in ["failed", "security", "urgent", "escalation"]):
        return "escalate"
    return "reply"


def llm_action(email, observation):
    if not USE_LLM_POLICY or OpenAI is None or not os.getenv("OPENAI_API_KEY"):
        return None

    client = OpenAI()
    prompt = (
        "Choose exactly one action: reply, ignore, escalate.\n"
        f"Subject: {email.get('subject', '')}\n"
        f"Body: {email.get('body', '')}\n"
        f"Priority: {email.get('priority', 'low')}\n"
        f"Domain: {email.get('domain', 'work')}\n"
        f"Due day: {email.get('due_day', 1)}\n"
        f"Current day: {observation.get('current_day', 1)}\n"
        f"User trust: {observation.get('user_trust', 1.0)}\n"
        "Return one token only."
    )

    try:
        response = client.responses.create(model=OPENAI_MODEL, input=prompt)
        text = (response.output_text or "").strip().lower()
        for action in ["escalate", "ignore", "reply"]:
            if action in text:
                return action
    except Exception:
        return None

    return None


def triage_agent(email, observation, recent_feedback):
    llm_choice = llm_action(email, observation)
    if llm_choice in {"reply", "ignore", "escalate"}:
        return llm_choice
    return heuristic_action(email, observation, recent_feedback)


def communication_agent(action_type):
    if action_type == "reply":
        return "Acknowledged. We are handling this now."
    if action_type == "escalate":
        return "Escalating this issue for immediate resolution."
    return "No response required."


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    payload = res.json()
    emails = payload["emails"]

    total_reward = 0.0
    recent_feedback = []
    steps = 0
    max_steps = max(24, len(observation["emails"]) * 4)

    while not (steps >= max_steps or not observation.get("emails")):
        steps += 1
        email = planning_agent(observation)
        if email is None:
            break

        feedback = (sum(recent_feedback[-3:]) / min(3, len(recent_feedback))) if recent_feedback else 0.0
        action_type = triage_agent(email)

        if feedback < 0 and email.get("priority") == "high" and action_type == "reply":
            action_type = "escalate"

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

        if result.get("done"):
            break

    print(f"Episode level={LEVEL} total_reward={total_reward:.3f}")


if __name__ == "__main__":
    run_episode()
