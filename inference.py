import os
import asyncio
from typing import List, Optional
from openai import OpenAI

from my_env_v4.env import MyEnvV4Env
from my_env_v4.models import MyEnvV4Action

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")

LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME", "my-env-image")

MAX_STEPS = 3


def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)


def log_end(success: bool, steps: int, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    score = sum(rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


async def main():
    if not API_KEY:
        print("[WARNING] No API key found, using fallback policy", flush=True)
        client = None
    else:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    env = await MyEnvV4Env.from_docker_image(LOCAL_IMAGE_NAME)

    rewards = []
    steps = 0

    log_start("email_task", "my_env_v4", MODEL_NAME)

    try:
        result = await env.reset()

        for step in range(1, MAX_STEPS + 1):
            obs = result.observation

            prompt = f"""
You are an intelligent email assistant.

Inbox:
{obs.emails}

History:
{obs.history}

You must decide the correct action for the CURRENT email.

Allowed actions:
- reply
- ignore
- escalate

Only output ONE word.
"""

            if client:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                )
                action_text = completion.choices[0].message.content.strip().lower()
            else:
                # fallback rule-based policy (improved)
                current_email = obs.emails[min(step-1, len(obs.emails)-1)]
                text = current_email["email_text"].lower()
                urgency = current_email.get("urgency_hint", "").lower()

                # better priority: spam -> ignore, high urgency -> escalate, else reply
                if any(word in text for word in ["offer", "newsletter", "click", "discount", "subscribe", "promotion"]):
                    action_text = "ignore"
                elif urgency == "high":
                    action_text = "escalate"
                else:
                    action_text = "reply"

            if action_text not in ["reply", "ignore", "escalate"]:
                action_text = "ignore"

            result = await env.step(MyEnvV4Action(decision=action_text))

            reward = result.reward
            done = result.done

            rewards.append(reward)
            steps = step

            log_step(step, action_text, reward, done, None)

            if done:
                break

        success = sum(rewards) >= 0.4

    finally:
        await env.close()
        log_end(success, steps, rewards)


if __name__ == "__main__":
    asyncio.run(main())