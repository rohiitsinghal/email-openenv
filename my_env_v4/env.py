from .models import Observation, Action, StepResult, Email, PublicEmail
from .tasks import load_task
from .grader import (
    grade_email_easy,
    grade_email_medium,
    grade_email_hard,
    grade_email_round2,
)


class EmailEnv:
    """
    Email Triage OpenEnv — Multi-step, partially observable decision environment.

    Innovations over baseline:
    - Sender relationship tracking (trust per sender_role)
    - Budget constraint tracked in world_model (penalises ignoring budget context)
    - Calendar conflict detection (personal vs work on same due_day)
    - Thread awareness (follow-up emails share thread_id)
    - Consequence chain: mishandling high-priority emails spawns blocking follow-ups
    - User trust evolves per-episode based on decision quality
    - Multi-domain balance incentivised (work vs personal)
    - Dependency enforcement with clear penalty
    - Due-day pressure on a 14-day simulated horizon
    """

    def __init__(self, task_level: str = "easy"):
        self.task_level = task_level
        self.completed: set = set()
        self.steps: int = 0
        self.reset()

    # ------------------------------------------------------------------
    # Difficulty-scaled parameters
    # ------------------------------------------------------------------

    def _step_penalty(self) -> float:
            return {"easy": 0.005, "medium": 0.03, "hard": 0.05, "round2": 0.08}.get(self.task_level, 0.02)

    def _completion_bonus(self) -> float:
            return {"easy": 1.0, "medium": 0.4, "hard": 0.3, "round2": 0.2}.get(self.task_level, 0.5)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self):
        self.emails = load_task(self.task_level)
        self.history: list = []
        self.done: bool = False
        self.completed: set = set()
        self.steps: int = 0
        self.current_day: int = 1
        self.user_trust: float = 1.0

        self.world_model = {
            "work_actions": 0,
            "personal_actions": 0,
            "feedback_count": 0,
            "feedback_sum": 0.0,
            "spawned_followups": [],
            # Budget available for approval decisions (round2)
            "budget_remaining": 100_000,
            # Per sender_role trust scores — agent can learn to weight these
            "sender_trust": {
                "manager": 1.0,
                "peer": 1.0,
                "customer": 1.0,
                "vendor": 1.0,
                "internal": 1.0,
                "unknown": 0.3,   # Unknown senders start with low trust
            },
            # Calendar: tracks which due_days have committed actions
            "committed_days": {},
            # Thread memory: maps thread_id → list of completed email ids
            "thread_memory": {},
        }

        return self._observation()

    # ------------------------------------------------------------------
    # Observation helpers
    # ------------------------------------------------------------------

    def _public_email(self, email: Email) -> PublicEmail:
        """Strip internal label before exposing to agent."""
        return PublicEmail(
            id=email.id,
            subject=email.subject,
            body=email.body,
            priority=email.priority,
            domain=email.domain,
            due_day=email.due_day,
            dependency_ids=email.dependency_ids,
            sender=email.sender,
            sender_role=email.sender_role,
            thread_id=email.thread_id,
            urgency_score=email.urgency_score,
            context_clue=email.context_clue,
        )

    def _observation(self) -> Observation:
        return Observation(
            emails=[self._public_email(e) for e in self.emails],
            history=self.history,
            current_day=self.current_day,
            user_trust=self.user_trust,
            world_model=self.world_model,
        )

    # ------------------------------------------------------------------
    # State (public API)
    # ------------------------------------------------------------------

    def state(self) -> dict:
        return {
            "emails": [self._public_email(e).model_dump() for e in self.emails],
            "history": self.history,
            "current_day": self.current_day,
            "user_trust": self.user_trust,
            "world_model": self.world_model,
        }

    # ------------------------------------------------------------------
    # Step
    # ------------------------------------------------------------------

    def step(self, action: Action) -> StepResult:
        reward = 0.0
        self.steps += 1
        reward -= self._step_penalty()
        info: dict = {}

        # --- Find email ---
        email = next((e for e in self.emails if e.id == action.email_id), None)
        if not email:
            return StepResult(
                observation=self._observation(),
                reward=-0.3,
                done=False,
                info={"error": "Invalid email_id"},
            )

        # --- Duplicate action guard ---
        if action.email_id in self.completed:
            return StepResult(
                observation=self._observation(),
                reward=-0.2,
                done=False,
                info={"error": "Email already processed"},
            )

        # --- Build grader state dict ---
        grader_state = {
            "label": email.label,
            "body": email.body,
            "priority": email.priority,
            "domain": email.domain,
            "due_day": email.due_day,
            "dependency_ids": email.dependency_ids,
            "sender_role": email.sender_role,
            "urgency_score": email.urgency_score,
            "context_clue": email.context_clue,
        }
        action_dict = {
            "type": action.action_type,
            "content": action.content or "",
        }

        # --- Task-level grading ---
        if self.task_level == "easy":
            task_reward, _ = grade_email_easy(grader_state, action_dict)
        elif self.task_level == "medium":
            task_reward, _ = grade_email_medium(grader_state, action_dict)
        elif self.task_level == "hard":
            task_reward, _ = grade_email_hard(grader_state, action_dict)
        elif self.task_level == "round2":
            task_reward, _ = grade_email_round2(grader_state, action_dict, self.world_model)
        else:
            task_reward = 0.0

        reward += task_reward

        # ------------------------------------------------------------------
        # World model updates (round2 and hard)
        # ------------------------------------------------------------------

        if self.task_level in {"hard", "round2"}:

            # 1. Consequence propagation: mishandling high-priority spawns follow-up
            reward += self._spawn_followup_if_needed(email, action.action_type, info)

            # 2. Dependency enforcement
            if email.dependency_ids:
                unmet = [d for d in email.dependency_ids if d not in self.completed]
                if unmet:
                    reward -= 0.3
                    info["unmet_dependencies"] = unmet

            # 3. Due-day pressure: ignoring an overdue email
            if self.current_day > email.due_day and action.action_type == "ignore":
                reward -= 0.4
                info["overdue_ignored"] = True

            # 4. Calendar conflict detection
            reward += self._detect_calendar_conflict(email, action, info)

            # 5. Budget update if an offsite/budget email was approved
            if "budget" in email.body.lower() and action.action_type == "reply":
                if any(w in (action.content or "").lower() for w in ["approve", "sounds good", "let's do it", "confirmed"]):
                    cost = 80_000  # as per tasks.py scenario
                    self.world_model["budget_remaining"] = max(0, self.world_model.get("budget_remaining", 100_000) - cost)
                    info["budget_approved"] = cost

        if self.task_level == "round2":

            # 6. Specialist agent collaboration bonus
            if task_reward > 0 and action.actor in {"triage_agent", "planning_agent", "communication_agent"}:
                reward += 0.02

            # 7. Feedback signal integration
            if action.feedback is not None:
                self.world_model["feedback_count"] += 1
                self.world_model["feedback_sum"] += action.feedback
                reward += 0.02 * max(-1.0, min(1.0, action.feedback))

            # 8. Sender trust update
            sender_role = email.sender_role
            if task_reward > 0:
                self.world_model["sender_trust"][sender_role] = min(
                    1.5, self.world_model["sender_trust"].get(sender_role, 1.0) + 0.03
                )
            elif task_reward < -0.3:
                self.world_model["sender_trust"][sender_role] = max(
                    0.0, self.world_model["sender_trust"].get(sender_role, 1.0) - 0.05
                )

            # 9. Thread memory update
            thread_id = email.thread_id
            if thread_id:
                mem = self.world_model["thread_memory"].setdefault(thread_id, [])
                mem.append(action.email_id)
                # Bonus for correctly handling follow-up in same thread
                if len(mem) > 1 and task_reward > 0:
                    reward += 0.05
                    info["thread_continuity_bonus"] = True

            # 10. Simulated day advancement
            self.current_day = min(14, 1 + (self.steps // 2))

            # 11. User trust evolution
            if reward < 0:
                self.user_trust = max(0.0, self.user_trust - 0.06)
            elif reward > 0.7:
                self.user_trust = min(1.5, self.user_trust + 0.03)

        # ------------------------------------------------------------------
        # Completion logic
        # ------------------------------------------------------------------

        # High-priority emails must be handled before low-priority ones
        high_priority_pending = any(
            e.id not in self.completed and e.priority == "high"
            for e in self.emails
            if e.id != action.email_id
        )

        # Allow completion if: this is high priority, or no high-priority left
        if task_reward > 0 and (email.priority == "high" or not high_priority_pending):
            self.completed.add(action.email_id)
        elif task_reward > 0:
            # Completed but it was wrong order — small penalty for priority violation
            self.completed.add(action.email_id)
            if email.priority != "high":
                reward -= 0.1
                info["priority_order_violation"] = True

        if len(self.completed) == len(self.emails):
            self.done = True
            reward += self._completion_bonus()

        self.history.append(str(action.model_dump()))

        return StepResult(
            observation=self._observation(),
            reward=round(reward, 4),
            done=self.done,
            info=info,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _spawn_followup_if_needed(self, email: Email, action_type: str, info: dict) -> float:
        """
        Consequence propagation: mishandling a high-priority email spawns
        a follow-up that appears in the inbox, increasing episode length
        and potentially blocking dependent emails.
        """
        if email.priority != "high":
            return 0.0
        if action_type == "escalate":
            return 0.0  # Correct action — no consequence

        spawned = self.world_model.setdefault("spawned_followups", [])
        if email.id in spawned:
            return 0.0

        # Spawn a blocking follow-up
        next_id = max((e.id for e in self.emails), default=0) + 1
        followup = Email(
            id=next_id,
            subject=f"⚠️ Follow-up required: {email.subject}",
            body=(
                f"The issue from '{email.subject}' remains unresolved. "
                "Immediate escalation is required. This is now blocking downstream work."
            ),
            label="complaint",
            priority="high",
            domain=email.domain,
            due_day=min(14, self.current_day + 1),
            dependency_ids=[email.id],
            sender=email.sender,
            sender_role=email.sender_role,
            thread_id=email.thread_id,
            urgency_score=min(1.0, email.urgency_score + 0.1),
        )
        self.emails.append(followup)
        spawned.append(email.id)
        info["follow_up_spawned"] = f"email_id={next_id} blocks resolution of {email.id}"
        return -0.3

    def _detect_calendar_conflict(self, email: Email, action: Action, info: dict) -> float:
        """
        Detect when a personal and work email share the same due_day.
        If agent commits to both without noting the conflict, penalise.
        If agent's content acknowledges the conflict, reward.
        """
        committed = self.world_model.get("committed_days", {})
        due_day = email.due_day
        domain = email.domain

        if action.action_type not in {"reply", "escalate"}:
            return 0.0

        # Check for conflict: same day already committed in opposite domain
        existing = committed.get(due_day)
        conflict_bonus = 0.0

        if existing and existing != domain:
            # Conflict exists — check if content acknowledges it
            content = (action.content or "").lower()
            conflict_words = ["conflict", "clash", "same time", "reschedule",
                              "cannot make", "alternative", "thursday", "friday"]
            if any(w in content for w in conflict_words):
                conflict_bonus = 0.15   # Rewarded for noticing the conflict
                info["conflict_acknowledged"] = True
            else:
                conflict_bonus = -0.15  # Penalised for missing it
                info["conflict_missed"] = True

        # Record this commitment
        if action.action_type in {"reply", "escalate"}:
            committed[due_day] = domain
            self.world_model["committed_days"] = committed

        return conflict_bonus