from fastapi import FastAPI

from my_env_v4.env import EmailEnv
from my_env_v4.models import Action

app = FastAPI()
_env = EmailEnv(task_level="easy")

@app.get("/")
def home():
    return {"message": "Email OpenEnv is running"}

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

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()