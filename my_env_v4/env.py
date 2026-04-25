from .models import Observation, Action, StepResult, Email, PublicEmail
from .tasks import load_task
from .grader import *

class EmailEnv:
    def __init__(self, task_level="easy"):
        self.task_level = task_level
        self.completed = set()
        self.steps = 0
        self.reset()

    def _step_penalty(self):
        return {
            "easy": 0.02,
            "medium": 0.03,
            "hard": 0.05,
            "round2": 0.08,
        }.get(self.task_level, 0.02)

    def _completion_bonus(self):
        return {
            "easy": 0.5,
            "medium": 0.4,
            "hard": 0.25,
            "round2": 0.15,
        }.get(self.task_level, 0.5)

    def reset(self):
        self.emails = load_task(self.task_level)
        self.history = []
        self.done = False
        self.completed = set()
        self.steps = 0
        self.current_day = 1
        self.user_trust = 1.0
        self.world_model = {
            "work_actions": 0,
            "personal_actions": 0,
            "feedback_count": 0,
            "feedback_sum": 0.0,
            "spawned_followups": [],
        }
        return self._observation()

    def _public_email(self, email: Email) -> PublicEmail:
        return PublicEmail(
            id=email.id,
            subject=email.subject,
            body=email.body,
            priority=email.priority,
            domain=email.domain,
            due_day=email.due_day,
            dependency_ids=email.dependency_ids,
        )

    def _observation(self) -> Observation:
        return Observation(
            emails=[self._public_email(e) for e in self.emails],
            history=self.history,
            current_day=self.current_day,
            user_trust=self.user_trust,
            world_model=self.world_model,
        )

    def _spawn_followup_if_needed(self, email: Email, action_type: str, info: dict) -> float:
        if self.task_level not in {"hard", "round2"}:
            return 0.0
        if email.priority != "high":
            return 0.0
        if action_type == "escalate":
            return 0.0

        spawned = self.world_model.setdefault("spawned_followups", [])
        if email.id in spawned:
            return 0.0

        next_id = max([e.id for e in self.emails], default=0) + 1
        followup = Email(
            id=next_id,
            subject=f"Follow-up required: {email.subject}",
            body="Issue is still unresolved. Immediate escalation required.",
            label="complaint",
            priority="high",
            domain=email.domain,
            due_day=min(14, self.current_day + 1),
            dependency_ids=[email.id],
        )
        self.emails.append(followup)
        spawned.append(email.id)
        info["follow_up_created"] = True
        return -0.25

    def state(self):
        return {
            "emails": [self._public_email(e).model_dump() for e in self.emails],
            "history": self.history,
            "current_day": self.current_day,
            "user_trust": self.user_trust,
            "world_model": self.world_model,
        }
    
    def step(self, action: Action):
        reward = 0.0
        self.steps += 1
        reward -= self._step_penalty()
        info = {}

        email = next((e for e in self.emails if e.id == action.email_id), None)


        if not email:
            return StepResult(
                observation=self._observation(),
                reward=-0.2,
                done=False,
                info={"error": "Invalid email_id"}
            )

        if action.email_id in self.completed:
            reward = -0.2
            return StepResult(
                observation=self._observation(),
                reward=reward,
                done=False,
                info={"error": "Email already processed"}
            )

        # --- Task-level grading ---
        state = {
            "label": email.label,
            "body": email.body,
            "priority": email.priority,
            "domain": email.domain,
            "due_day": email.due_day,
            "dependency_ids": email.dependency_ids,
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
        elif self.task_level == "round2":
            task_reward, _ = grade_email_round2(state, action_dict, self.world_model)
        else:
            task_reward = 0.0

        reward += task_reward

        # Unresolved high-priority items spawn follow-up emails in later steps.
        reward += self._spawn_followup_if_needed(email, action.action_type, info)

        # Encourage specialist collaboration only after useful base actions.
        if self.task_level == "round2" and task_reward > 0 and action.actor in {
            "triage_agent", "planning_agent", "communication_agent"
        }:
            reward += 0.02

        # Penalize dependency violations (e.g., confirming a call before preparing report).
        if self.task_level == "round2" and email.dependency_ids:
            unmet = [dep_id for dep_id in email.dependency_ids if dep_id not in self.completed]
            if unmet:
                reward -= 0.25

        # Due-day pressure over a 14-day horizon.
        if self.task_level == "round2" and self.current_day > email.due_day and action.action_type == "ignore":
            reward -= 0.35

        # Feedback signal to support post-training/self-improvement loops.
        if self.task_level == "round2" and action.feedback is not None:
            self.world_model["feedback_count"] += 1
            self.world_model["feedback_sum"] += action.feedback
            reward += 0.02 * max(-1.0, min(1.0, action.feedback))

        # Only allow completion if either:
        # 1. This email is high priority OR
        # 2. No high-priority emails remain
        high_priority_exists = any(
            e.id not in self.completed and e.priority == "high"
            for e in self.emails
        )

        # Prevent completing low-priority emails if high-priority ones exist
        if task_reward > 0 and not (high_priority_exists and email.priority != "high"):
            self.completed.add(action.email_id)

        if len(self.completed) == len(self.emails):
            self.done = True
            reward += self._completion_bonus()

        if self.task_level == "round2":
            # Advance one simulated day every two actions.
            self.current_day = min(14, 1 + (self.steps // 2))

            # Trust changes with outcome quality.
            if reward < 0:
                self.user_trust = max(0.0, self.user_trust - 0.05)
            elif reward > 0.8:
                self.user_trust = min(1.5, self.user_trust + 0.03)

        self.history.append(str(action.dict()))

        return StepResult(
            observation=self._observation(),
            reward=reward,
            done=self.done,
            info=info
        )