from .models import Observation, Action, StepResult
from .tasks import load_task
from .grader import *

class EmailEnv:
    def __init__(self, task_level="easy"):
        self.task_level = task_level
        self.completed = set()
        self.steps= 0
        self.reset()

    def reset(self):
        self.emails = load_task(self.task_level)
        self.history = []
        self.done = False
        self.completed = set()
        self.steps = 0
        return Observation(emails=self.emails, history=[])

    def state(self):
        return {
            "emails": self.emails,
            "history": self.history
        }
    
    def step(self, action: Action):
        reward = 0.0
        self.steps += 1
        reward -= 0.02
        info = {}

        email = next((e for e in self.emails if e.id == action.email_id), None)


        if not email:
            return StepResult(
                observation=Observation(emails=self.emails, history=self.history),
                reward=-0.2,
                done=False,
                info={"error": "Invalid email_id"}
            )

        if action.email_id in self.completed:
            reward = -0.2
            return StepResult(
                observation=Observation(emails=self.emails, history=self.history),
                reward=reward,
                done=False,
                info={"error": "Email already processed"}
            )

        # --- Task-level grading ---
        state = {
            "label": email.label,
            "body": email.body,
            "priority": email.priority
        }

        action_dict = {
            "type": action.action_type,
            "content": action.content
        }

        if self.task_level == "easy":
            task_reward, _ = grade_email_easy(state, action_dict)
        elif self.task_level == "medium":
            task_reward, _ = grade_email_medium(state, action_dict)
        elif self.task_level == "hard":
            task_reward, _ = grade_email_hard(state, action_dict)
        else:
            task_reward = 0.0

        reward += task_reward

        # Only allow completion if either:
        # 1. This email is high priority OR
        # 2. No high-priority emails remain
        high_priority_exists = any(
            e.id not in self.completed and e.priority == "high"
            for e in self.emails
        )

        # Prevent completing low-priority emails if high-priority ones exist
        if reward > 0.5 and not (high_priority_exists and email.priority != "high"):
            self.completed.add(action.email_id)

        if len(self.completed) == len(self.emails):
            self.done = True
            reward += 0.5

        self.history.append(str(action.dict()))

        return StepResult(
            observation=Observation(emails=self.emails, history=self.history),
            reward=reward,
            done=self.done,
            info=info
        )