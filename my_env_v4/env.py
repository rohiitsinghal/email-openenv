from .models import Observation, MyEnvV4Action, StepResult
from .tasks import load_task
from .grader import *

class MyEnvV4Env:
    def __init__(self, task_level="easy"):
        self.task_level = task_level
        self.completed = set()
        self.steps= 0
        pass

    @classmethod
    async def from_docker_image(cls, image_name: str):
        return cls()

    async def reset(self):
        self.emails = load_task(self.task_level)
        self.history = []
        self.done = False
        self.completed = set()
        self.steps = 0
        self.current_index = 0
        return StepResult(
            observation=Observation(emails=self.emails, history=[]),
            reward=0.0,
            done=False,
            info={}
        )

    def state(self):
        return {
            "emails": [e.dict() for e in self.emails],
            "history": self.history
        }
    
    async def step(self, action: MyEnvV4Action):
        reward = 0.0
        self.steps += 1

        # small penalty for inefficiency
        reward -= 0.01

        current_email = self.emails[self.current_index]
        correct = current_email["correct_action"]

        if action.decision == correct:
            reward += 0.5
            self.completed.add(self.current_index)

        # move to next email
        self.current_index += 1

        # done condition
        if self.current_index >= len(self.emails):
            self.done = True

            # bonus for finishing correctly
            if len(self.completed) == len(self.emails):
                reward += 0.5

        reward = max(0.0, min(1.0, reward))

        return StepResult(
            observation=Observation(
                emails=self.emails,
                history=self.history
            ),
            reward=reward,
            done=self.done,
            info={}
        )

    async def close(self):
        pass