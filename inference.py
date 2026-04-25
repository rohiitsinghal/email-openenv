import os
import requests

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
LEVEL = os.getenv("LEVEL", "round2")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_LLM_POLICY = os.getenv("USE_LLM_POLICY", "false").lower() == "true"


PRIORITY_WEIGHT = {
    "high": 3.0,
    "medium": 2.0,
    "low": 1.0,
}


def dependency_blocked(email, available_ids):
    deps = email.get("dependency_ids", [])
    return any(dep_id in available_ids for dep_id in deps)


def planning_agent(observation):
    emails = observation.get("emails", [])
    current_day = int(observation.get("current_day", 1))
    world_model = observation.get("world_model", {})
    available_ids = {e["id"] for e in emails}

    ranked = []
    for email in emails:
        due_day = int(email.get("due_day", current_day))
        due_pressure = max(0.0, 4.0 - (due_day - current_day))
        domain = email.get("domain", "work")
        domain_bias = 0.2 if domain == "work" else 0.0
        dep_penalty = 2.0 if dependency_blocked(email, available_ids) else 0.0

        # If trust is low, prioritize safer escalation on high-priority items.
        trust = float(observation.get("user_trust", 1.0))
        trust_pressure = (1.0 - trust) if email.get("priority") == "high" else 0.0

        score = PRIORITY_WEIGHT.get(email.get("priority", "low"), 1.0) + due_pressure + domain_bias + trust_pressure - dep_penalty
        ranked.append((score, email))

    ranked.sort(key=lambda x: x[0], reverse=True)

    # If there is strong work/personal imbalance, prioritize the minority domain next.
    work_actions = int(world_model.get("work_actions", 0))
    personal_actions = int(world_model.get("personal_actions", 0))
    if abs(work_actions - personal_actions) >= 2:
        minority = "personal" if work_actions > personal_actions else "work"
        for _, email in ranked:
            if email.get("domain") == minority:
                return email

    return ranked[0][1] if ranked else None


def heuristic_action(email, observation, recent_feedback):
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
    priority = email.get("priority", "low")
    due_day = int(email.get("due_day", 99))
    current_day = int(observation.get("current_day", 1))

    if any(x in text for x in ["offer", "click", "won", "discount", "lottery", "prize", "promo"]):
        return "ignore"

    if priority == "high":
        return "escalate"

    if due_day <= current_day + 1:
        return "escalate"

    if any(x in text for x in ["security", "failed", "urgent", "escalation", "blocked", "breach"]):
        return "escalate"

    if recent_feedback < 0 and priority in {"high", "medium"}:
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
        return "Acknowledged. I have scheduled the next action and will follow up."
    if action_type == "escalate":
        return "Escalating now due to urgency/risk to avoid downstream failures."
    return "No response required."


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    payload = res.json()
    observation = {
        "emails": payload.get("emails", []),
        "history": payload.get("history", []),
        "current_day": payload.get("state", {}).get("current_day", 1),
        "user_trust": payload.get("state", {}).get("user_trust", 1.0),
        "world_model": payload.get("state", {}).get("world_model", {}),
    }

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
        action_type = triage_agent(email, observation, feedback)

        if feedback < 0 and email.get("priority") == "high" and action_type == "reply":
            action_type = "escalate"

        action = {
            "action_type": action_type,
            "email_id": email["id"],
            "content": communication_agent(action_type),
            "actor": "coordinator",
            "feedback": feedback,
        }

        step_res = requests.post(f"{BASE_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        result = step_res.json()

        reward = float(result.get("reward", 0.0))
        total_reward += reward
        recent_feedback.append(1.0 if reward > 0 else -1.0)

        next_obs = result.get("observation", {})
        observation = {
            "emails": next_obs.get("emails", []),
            "history": next_obs.get("history", []),
            "current_day": next_obs.get("current_day", observation.get("current_day", 1)),
            "user_trust": next_obs.get("user_trust", observation.get("user_trust", 1.0)),
            "world_model": next_obs.get("world_model", observation.get("world_model", {})),
        }

        if result.get("done"):
            break

    print(f"Episode level={LEVEL} total_reward={total_reward:.3f} steps={steps}")


if __name__ == "__main__":
    run_episode()
