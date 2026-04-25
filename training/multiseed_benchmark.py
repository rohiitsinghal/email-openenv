import argparse
import json
import os
import random
import sys
from statistics import mean, pstdev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from my_env_v4.env import EmailEnv
from my_env_v4.models import Action


LEVELS = ["easy", "medium", "hard", "round2"]


def policy_naive(email, recent_feedback):
    _ = recent_feedback
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


def policy_priority_first(email, recent_feedback):
    _ = recent_feedback
    text = f"{email.subject} {email.body}".lower()
    if any(x in text for x in ["offer", "click", "won", "lottery", "prize", "discount"]):
        return "ignore"
    if email.priority == "high":
        return "escalate"
    if any(x in text for x in ["meeting", "report", "review", "confirm"]):
        return "reply"
    return "reply"


def run_episode(level, policy_fn, seed):
    env = EmailEnv(task_level=level)
    obs = env.reset()

    # Seeded inbox shuffle creates controlled variation and tests policy robustness
    # without changing grading logic.
    rng = random.Random(f"{seed}-{level}")
    shuffled = list(obs.emails)
    rng.shuffle(shuffled)
    env.emails = shuffled
    obs.emails = shuffled

    total = 0.0
    feedback = 0.0
    email_count = len(obs.emails) or 1

    for email in obs.emails:
        action_type = policy_fn(email, feedback)
        result = env.step(
            Action(
                action_type=action_type,
                email_id=email.id,
                content="evaluation",
                actor="coordinator",
                feedback=feedback,
            )
        )
        total += result.reward
        feedback = 1.0 if result.reward > 0 else -1.0
        if result.done:
            break

    return round(total / email_count, 4)


def summarize(values):
    return {
        "mean": round(mean(values), 4),
        "std": round(pstdev(values), 4),
        "values": [round(v, 4) for v in values],
    }


def evaluate_policy(policy_name, policy_fn, seeds):
    per_level = {}
    for level in LEVELS:
        level_values = [run_episode(level, policy_fn, seed) for seed in seeds]
        per_level[level] = summarize(level_values)

    overall_values = [mean([per_level[level]["values"][i] for level in LEVELS]) for i in range(len(seeds))]

    return {
        "policy": policy_name,
        "metric": "reward_per_email",
        "per_level": per_level,
        "overall": summarize(overall_values),
    }


def to_markdown_table(summary):
    lines = []
    lines.append("# Judge Summary (Multi-Seed)")
    lines.append("")
    lines.append(f"Metric: {summary['metric']}")
    lines.append(f"Seeds: {summary['seeds']}")
    lines.append("")
    lines.append("| Policy | Easy | Medium | Hard | Round2 | Overall |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for policy in summary["ranked_policies"]:
        pdata = summary["policies"][policy]
        easy = pdata["per_level"]["easy"]
        medium = pdata["per_level"]["medium"]
        hard = pdata["per_level"]["hard"]
        round2 = pdata["per_level"]["round2"]
        overall = pdata["overall"]

        lines.append(
            f"| {policy} | {easy['mean']:.4f} +/- {easy['std']:.4f} | "
            f"{medium['mean']:.4f} +/- {medium['std']:.4f} | "
            f"{hard['mean']:.4f} +/- {hard['std']:.4f} | "
            f"{round2['mean']:.4f} +/- {round2['std']:.4f} | "
            f"{overall['mean']:.4f} +/- {overall['std']:.4f} |"
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run a multi-seed reward benchmark")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run")
    parser.add_argument("--start-seed", type=int, default=0, help="Starting seed value")
    args = parser.parse_args()

    seeds = [args.start_seed + i for i in range(args.seeds)]

    policies = {
        "naive_reply": policy_naive,
        "adaptive_keyword": policy_adaptive,
        "priority_first": policy_priority_first,
    }

    policy_results = {
        name: evaluate_policy(name, fn, seeds)
        for name, fn in policies.items()
    }

    ranked = sorted(
        policy_results.keys(),
        key=lambda name: policy_results[name]["overall"]["mean"],
        reverse=True,
    )

    summary = {
        "metric": "reward_per_email",
        "seeds": seeds,
        "policies": policy_results,
        "ranked_policies": ranked,
    }

    json_path = os.path.join(ROOT, "training", "multiseed_benchmark.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md_path = os.path.join(ROOT, "training", "judge_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown_table(summary))

    print(json.dumps(summary, indent=2))
    print(f"Saved {json_path}")
    print(f"Saved {md_path}")


if __name__ == "__main__":
    main()
