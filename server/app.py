from fastapi import FastAPI
from my_env_v4.env import EmailEnv
from my_env_v4.models import Action

app = FastAPI(
    title="Email Triage OpenEnv",
    description="A multi-step decision environment for evaluating AI agents on email triage tasks.",
    version="2.0.0"
)
_env = EmailEnv(task_level="easy")


@app.get("/")
def home():
    return {
        "message": "Email OpenEnv is running",
        "docs": "/docs",
        "benchmark": "/benchmark",
        "levels": ["easy", "medium", "hard", "round2"]
    }


@app.post("/reset")
def reset(level: str = "easy"):
    global _env
    _env = EmailEnv(task_level=level)
    obs = _env.reset()
    return {"emails": [e.model_dump() for e in obs.emails], "history": obs.history, "state": _env.state()}


@app.post("/step")
def step(action: Action):
    result = _env.step(action)
    return {
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
        "observation": result.observation.model_dump(),
    }


@app.get("/state")
def state():
    return _env.state()


@app.get("/benchmark")
def benchmark():
    return {
        "environment": "Email Triage OpenEnv",
        "version": "2.0.0",
        "levels": ["easy", "medium", "hard", "round2"],
        "baseline_agent_scores": {
            "easy": 1.92,
            "medium": 3.90,
            "hard": 5.38,
            "round2": 7.89
        },
        "reward_improvement": {
            "naive_baseline_avg": 1.69,
            "adaptive_agent_avg": 2.62,
            "delta": "+0.93"
        },
        "agent_architecture": ["triage_agent", "communication_agent", "coordinator"],
        "actions": ["reply", "ignore", "escalate"],
        "email_fields": ["subject", "body", "priority", "domain", "sender_role", "urgency_score", "context_clue"],
        "openenv_compliant": True
    }


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
