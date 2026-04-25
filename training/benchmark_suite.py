import json
import os
import sys
from pathlib import Path
from statistics import mean

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from my_env_v4.env import EmailEnv
from my_env_v4.models import Action


ROOT = ROOT_DIR
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)

LEVELS = ["easy", "medium", "hard", "round2"]


def triage_agent(email):
    text = f"{email.subject} {email.body}".lower()
    if any(x in text for x in ["offer", "click", "won", "discount", "lottery", "prize"]):
        return "ignore"
    if email.priority == "high" and any(x in text for x in ["failed", "security", "urgent", "escalation"]):
        return "escalate"
    return "reply"


def planning_agent(email):
    if email.domain == "personal" and email.priority == "high":
        return "protect_personal_commitment"
    if email.due_day <= 3:
        return "prioritize_immediately"
    return "handle_in_cycle"


def communication_agent(action_type):
    if action_type == "reply":
        return "Acknowledged. I will take action and follow up shortly."
    if action_type == "escalate":
        return "Escalating this issue to the right owner now."
    return "No response required."


def run_policy(level, policy_name):
    env = EmailEnv(task_level=level)
    obs = env.reset()
    total_reward = 0.0
    trace = []
    recent_feedback = []

    for email in obs.emails:
        role_decision = triage_agent(email)
        plan_decision = planning_agent(email)

        if policy_name == "baseline":
            action_type = "reply"
        elif policy_name == "adaptive":
            feedback = sum(recent_feedback[-3:]) / min(3, len(recent_feedback)) if recent_feedback else 0.0
            action_type = role_decision
            if email.domain == "personal" and email.priority == "high":
                action_type = "reply"
            if email.due_day <= 3 and action_type == "reply":
                action_type = "escalate" if email.priority == "high" else "reply"
            if feedback < 0 and email.priority == "high" and action_type == "reply":
                action_type = "escalate"
        else:
            action_type = "reply"

        action = Action(
            action_type=action_type,
            email_id=email.id,
            content=communication_agent(action_type),
            actor="coordinator",
            feedback=(sum(recent_feedback[-3:]) / min(3, len(recent_feedback))) if recent_feedback else 0.0,
        )
        result = env.step(action)
        total_reward += result.reward
        recent_feedback.append(1.0 if result.reward > 0 else -1.0)

        trace.append({
            "email_id": email.id,
            "triage_agent": role_decision,
            "planning_agent": plan_decision,
            "communication_agent": action.content,
            "final_action": action_type,
            "reward": result.reward,
        })

        if result.done:
            break

    return round(total_reward, 4), trace


def main():
    summary = {}
    sample_traces = {}

    for policy_name in ["baseline", "adaptive"]:
        policy_scores = {}
        for level in LEVELS:
            score, trace = run_policy(level, policy_name)
            policy_scores[level] = score
            if level == "round2":
                sample_traces[policy_name] = trace
        summary[policy_name] = policy_scores

    summary["baseline_avg"] = round(mean(summary["baseline"].values()), 4)
    summary["adaptive_avg"] = round(mean(summary["adaptive"].values()), 4)
    summary["delta_avg"] = round(summary["adaptive_avg"] - summary["baseline_avg"], 4)
    summary["sample_trace_note"] = "Each action shows triage, planning, communication, and final coordinator decision."

    report = {
        "summary": summary,
        "sample_traces": sample_traces,
    }

    with (OUT_DIR / "benchmark_report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
