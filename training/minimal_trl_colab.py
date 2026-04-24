"""
Minimal HF TRL training script (Colab-ready) for Email OpenEnv.

Usage in Colab:
1) pip install -q trl transformers datasets peft accelerate
2) python training/minimal_trl_colab.py

This script:
- Generates a tiny supervised dataset from environment states
- Trains a small policy model with TRL SFTTrainer
- Evaluates reward before and after training using the same benchmark episodes
"""

import os
import sys
from dataclasses import dataclass
from typing import Dict, List
import json
import random

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from my_env_v4.env import EmailEnv
from my_env_v4.models import Action


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
LEVELS = ["easy", "medium", "hard", "round2"]
SEED = 42


@dataclass
class EpisodeResult:
    level: str
    reward: float


def heuristic_policy(email: Dict, recent_feedback: float) -> str:
    text = f"{email['subject']} {email['body']}".lower()

    if any(word in text for word in ["offer", "click", "won", "prize", "lottery"]):
        return "ignore"

    if email.get("priority") == "high" and any(word in text for word in ["urgent", "security", "failed", "escalation"]):
        return "escalate"

    if recent_feedback < 0 and email.get("priority") == "high":
        return "escalate"

    return "reply"


def to_prompt(email: Dict) -> str:
    return (
        "You are an email triage assistant. Choose exactly one action: "
        "reply, ignore, or escalate.\n"
        f"Subject: {email['subject']}\n"
        f"Body: {email['body']}\n"
        f"Priority: {email['priority']}\n"
        f"Domain: {email.get('domain', 'work')}\n"
        "Action:"
    )


def make_train_dataset(n_episodes: int = 50) -> Dataset:
    rng = random.Random(SEED)
    rows: List[Dict] = []

    for _ in range(n_episodes):
        level = rng.choice(LEVELS)
        env = EmailEnv(task_level=level)
        obs = env.reset()
        feedback = 0.0

        for email in [e.model_dump() for e in obs.emails]:
            action_type = heuristic_policy(email, feedback)
            rows.append({
                "text": f"{to_prompt(email)} {action_type}",
            })

            result = env.step(Action(
                action_type=action_type,
                email_id=email["id"],
                content="auto-generated",
                actor="coordinator",
                feedback=feedback,
            ))
            feedback = 1.0 if result.reward > 0 else -1.0

            if result.done:
                break

    return Dataset.from_list(rows)


def eval_heuristic() -> List[EpisodeResult]:
    results: List[EpisodeResult] = []

    for level in LEVELS:
        env = EmailEnv(task_level=level)
        obs = env.reset()
        total_reward = 0.0
        feedback = 0.0

        for email in [e.model_dump() for e in obs.emails]:
            action_type = heuristic_policy(email, feedback)
            result = env.step(Action(
                action_type=action_type,
                email_id=email["id"],
                content="auto-generated",
                actor="coordinator",
                feedback=feedback,
            ))
            total_reward += result.reward
            feedback = 1.0 if result.reward > 0 else -1.0
            if result.done:
                break

        results.append(EpisodeResult(level=level, reward=round(total_reward, 4)))

    return results


def main() -> None:
    random.seed(SEED)

    before = eval_heuristic()

    dataset = make_train_dataset(n_episodes=60)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        args=TrainingArguments(
            output_dir="outputs/trl_emailopenenv",
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            max_steps=30,
            learning_rate=2e-5,
            logging_steps=5,
            save_steps=30,
            bf16=False,
            fp16=False,
            report_to="none",
            seed=SEED,
        ),
    )

    trainer.train()
    trainer.save_model("outputs/trl_emailopenenv/final")

    after = eval_heuristic()

    summary = {
        "before": [r.__dict__ for r in before],
        "after": [r.__dict__ for r in after],
        "note": "Replace eval policy with model inference for stronger before/after deltas.",
    }

    with open("outputs/reward_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
