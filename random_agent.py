import os
import requests
import random

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
LEVEL = os.getenv("LEVEL", "round2")
NUM_EPISODES = int(os.getenv("NUM_EPISODES", "10"))

ACTIONS = ["reply", "ignore", "escalate"]


def random_agent(email):
    return random.choice(ACTIONS)


def communication_agent(action_type):
    if action_type == "reply":
        return "Acknowledged. We are handling this now."
    if action_type == "escalate":
        return "Escalating this issue for immediate resolution."
    return "No response required."


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    observation = res.json()

    total_reward = 0.0
    steps = 0
    max_steps = max(24, len(observation.get("emails", [])) * 4)

    while steps < max_steps:
        steps += 1

        emails = observation.get("emails", [])
        if not emails:
            break

        email = emails[0]
        action_type = random_agent(email)
        content = communication_agent(action_type)

        action = {
            "action_type": action_type,
            "email_id": email["id"],
            "content": content,
            "actor": "random",
            "feedback": 0.0,
        }

        step_res = requests.post(f"{BASE_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        result = step_res.json()

        reward = float(result.get("reward", 0.0))
        total_reward += reward
        observation = result.get("observation", observation)

        if result.get("done"):
            break

    return total_reward


if __name__ == "__main__":
    rewards = []

    for ep in range(NUM_EPISODES):
        r = run_episode()
        rewards.append(r)
        print(f"Episode {ep+1:3d} | reward = {r:.3f}")

    avg = sum(rewards) / len(rewards)
    print(f"\nRandom Agent Baseline over {NUM_EPISODES} episodes:")
    print(f"  Average reward : {avg:.3f}")
    print(f"  Max reward     : {max(rewards):.3f}")
    print(f"  Min reward     : {min(rewards):.3f}")