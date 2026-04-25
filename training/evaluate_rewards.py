import json
import os
import sys
from statistics import mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from my_env_v4.env import EmailEnv
from my_env_v4.models import Action


LEVELS = ["easy", "medium", "hard", "round2"]


def policy_naive(email):
    return "reply"


def policy_adaptive(email, recent_feedback):
    text = f"{email.subject} {email.body}".lower()
    if any(x in text for x in ["offer", "click", "won", "lottery", "prize", "discount"]):
        return "ignore"
    if email.priority == "high" and any(x in text for x in ["security", "failed", "urgent", "escalation"]):
        return "escalate"
    if recent_feedback < 0 and email.priority == "high":
        return "escalate"
    return "reply"


def run_episode(level, policy):
    env = EmailEnv(task_level=level)
    obs = env.reset()
    total = 0.0
    feedback = 0.0
    email_count = len(obs.emails) or 1

    for email in obs.emails:
        action_type = policy(email, feedback) if policy is policy_adaptive else policy(email)
        result = env.step(Action(
            action_type=action_type,
            email_id=email.id,
            content="evaluation",
            actor="coordinator",
            feedback=feedback,
        ))
        total += result.reward
        feedback = 1.0 if result.reward > 0 else -1.0
        if result.done:
            break

    return round(total / email_count, 4)


def main():
    baseline = {level: run_episode(level, policy_naive) for level in LEVELS}
    improved = {level: run_episode(level, policy_adaptive) for level in LEVELS}

    summary = {
        "baseline": baseline,
        "improved": improved,
        "baseline_avg": round(mean(baseline.values()), 4),
        "improved_avg": round(mean(improved.values()), 4),
        "delta_avg": round(mean(improved.values()) - mean(baseline.values()), 4),
        "metric": "reward_per_email",
    }

    print(json.dumps(summary, indent=2))

    with open("training/reward_improvement.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
