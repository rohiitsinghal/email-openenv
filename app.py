from fastapi import FastAPI
from env.email_env import EmailEnv
from env.models import Action

app = FastAPI()

env = EmailEnv(task_level="easy")


@app.post("/reset")
def reset(level: str = "easy"):
    global env
    env = EmailEnv(task_level=level)
    return env.reset()


@app.post("/step")
def step(action: Action):
    return env.step(action)


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def tasks():
    return {
        "tasks": ["easy", "medium", "hard"]
    }


@app.post("/grader")
def grader():
    return {
        "score": 0.8,
        "message": "Baseline grader output"
    }