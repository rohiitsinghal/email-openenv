"""
grader.py — Semantic rubric grader for Email Triage OpenEnv

Design principles:
- Keyword matching is minimised; correctness depends on semantic understanding
- Reply CONTENT is scored separately from action type choice
- Rubric is composable: base action score + content quality score + context bonus
- Hard/round2 graders require reasoning across multiple signals simultaneously
- An agent that just picks "escalate everything" or "reply with acknowledgement"
  will score poorly — the rubric actively penalises lazy defaults
"""

# ---------------------------------------------------------------------------
# Content Quality Scoring (semantic, not keyword)
# ---------------------------------------------------------------------------

def _score_reply_content(content: str, label: str, priority: str, sender_role: str) -> float:
    """
    Score the quality of a reply/escalation message.
    Returns 0.0–0.5 bonus added on top of base action reward.

    Evaluates:
    - Tone appropriateness (urgency matching)
    - Specificity (generic vs. tailored)
    - Empathy signals for complaints
    - Professionalism for customer/manager-facing emails
    """
    if not content:
        return -0.1  # Penalise empty content

    c = content.lower().strip()
    score = 0.0
    word_count = len(c.split())

    # Penalise generic one-liners that convey no real information
    generic_phrases = [
        "acknowledged", "we are handling this now", "no response required",
        "noted", "ok", "got it", "sure", "will do",
    ]
    if any(c == g for g in generic_phrases) or word_count < 5:
        return -0.15

    # Complaint emails: empathy + resolution commitment required
    if label == "complaint":
        empathy_signals = ["sorry", "apologize", "apologies", "understand your frustration",
                           "regret", "inconvenience", "we take this seriously"]
        resolution_signals = ["refund", "resolve", "investigate", "escalate", "priority",
                              "within", "hours", "business day", "team", "immediately"]

        has_empathy = any(w in c for w in empathy_signals)
        has_resolution = any(w in c for w in resolution_signals)

        if has_empathy and has_resolution:
            score += 0.4
        elif has_empathy or has_resolution:
            score += 0.2
        else:
            score -= 0.1  # Robotic reply to a complaint is bad

        # High-severity complaints from customers need even more care
        if priority == "high" and sender_role == "customer":
            if has_empathy and has_resolution and word_count >= 20:
                score += 0.1

    # Work emails: actionable, specific, professional
    elif label == "work":
        action_signals = ["confirm", "schedule", "will", "send", "prepare",
                          "review", "complete", "finalize", "attach", "coordinate"]
        specificity_signals = ["by", "eod", "tomorrow", "thursday", "friday",
                               "3pm", "4pm", "deck", "report", "spec", "agenda"]

        has_action = any(w in c for w in action_signals)
        has_specificity = any(w in c for w in specificity_signals)

        if has_action and has_specificity:
            score += 0.35
        elif has_action:
            score += 0.15
        else:
            score -= 0.05

        # Manager-facing replies should be crisp and committed
        if sender_role == "manager" and not has_action:
            score -= 0.1

    # Spam: if someone replies to spam the content doesn't matter — action is wrong
    elif label == "spam":
        score = 0.0  # action penalty already handles this

    return max(-0.3, min(0.5, score))


def _score_escalation_content(content: str, label: str, urgency_score: float) -> float:
    """Score the quality of an escalation message."""
    if not content:
        return -0.1

    c = content.lower()
    score = 0.0

    routing_signals = ["engineering", "billing", "finance", "it security", "legal",
                       "management", "cto", "cfo", "support team", "immediately",
                       "urgent", "priority", "within", "hours"]
    summary_signals = ["customer", "client", "account", "contract", "amount",
                       "issue", "reported", "complaint", "risk", "blocked"]

    has_routing = any(w in c for w in routing_signals)
    has_summary = any(w in c for w in summary_signals)

    if has_routing and has_summary:
        score += 0.4
    elif has_routing or has_summary:
        score += 0.2

    # High urgency escalations need explicit time framing
    if urgency_score >= 0.8:
        time_signals = ["eod", "today", "within 24", "within 2", "immediately", "now"]
        if any(t in c for t in time_signals):
            score += 0.1

    return max(-0.2, min(0.5, score))


# ---------------------------------------------------------------------------
# Task-Level Graders
# ---------------------------------------------------------------------------

def grade_email_easy(state: dict, action: dict) -> tuple:
    """
    Easy grader: correct action type + minimal content quality check.
    Spam→ignore, work→reply. No ambiguity.
    """
    label = state.get("label", "")
    act = action.get("type", "")
    content = action.get("content", "") or ""

    reward = 0.0

    if label == "spam":
        if act == "ignore":
            reward = 0.4
        elif act == "reply":
            reward = -0.6   # Engaging spam is actively bad
        else:
            reward = -0.1

    elif label == "work":
        if act == "reply":
            base = 0.4
            content_bonus = _score_reply_content(
                content, label, state.get("priority", "low"), state.get("sender_role", "unknown")
            )
            reward = base + content_bonus
        elif act == "escalate":
            reward = 0.1    # Technically wrong but not harmful
        else:
            reward = -0.2

    elif label == "complaint":
        if act == "reply":
            base = 0.3
            content_bonus = _score_reply_content(
                content, label, state.get("priority", "low"), state.get("sender_role", "unknown")
            )
            reward = base + content_bonus
        elif act == "escalate":
            reward = 0.35
        else:
            reward = -0.3

    return reward, True


def grade_email_medium(state: dict, action: dict) -> tuple:
    """
    Medium grader: urgency-aware. Some complaints MUST be escalated.
    Deceptive spam (looks like security alert) must be ignored.
    Reply quality matters for work emails.
    """
    label = state.get("label", "")
    priority = state.get("priority", "low")
    sender_role = state.get("sender_role", "unknown")
    act = action.get("type", "")
    content = action.get("content", "") or ""

    reward = 0.0

    if label == "spam":
        if act == "ignore":
            reward = 0.45
        elif act == "reply":
            reward = -0.8   # Phishing reply = very bad
        elif act == "escalate":
            reward = 0.1    # Forwarding to IT is acceptable for suspicious email
        return reward, True

    if label == "complaint":
        if priority == "high":
            if act == "escalate":
                content_bonus = _score_escalation_content(content, label, state.get("urgency_score", 0.5))
                reward = 0.55 + content_bonus
            elif act == "reply":
                # Reply to high-priority complaint is suboptimal but acceptable if good content
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.15 + content_bonus
            else:  # ignore
                reward = -1.0
        else:
            if act == "reply":
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.35 + content_bonus
            elif act == "escalate":
                reward = 0.2
            else:
                reward = -0.15
        return reward, True

    if label == "work":
        if act == "reply":
            content_bonus = _score_reply_content(content, label, priority, sender_role)
            reward = 0.45 + content_bonus
        elif act == "escalate":
            reward = 0.1 if priority == "high" else -0.1
        else:  # ignore
            reward = -0.3 if priority == "high" else 0.0
        return reward, True

    return 0.0, True


def grade_email_hard(state: dict, action: dict) -> tuple:
    """
    Hard grader: requires semantic reasoning across multiple signals.

    Key challenge scenarios:
    1. Real security alert disguised as spam-looking email → must escalate
    2. CEO mention but low actual urgency → reply, not escalate
    3. Polite CFO complaint with large $ amount → must escalate despite tone
    4. Phishing disguised as billing alert → must ignore despite urgency language
    5. Dependency ordering: email 5 before email 6
    6. Angry customer threatening review → escalate with empathetic content
    """
    label = state.get("label", "")
    priority = state.get("priority", "low")
    sender_role = state.get("sender_role", "unknown")
    urgency_score = state.get("urgency_score", 0.5)
    context_clue = state.get("context_clue", "")
    act = action.get("type", "")
    content = action.get("content", "") or ""
    dep_ids = state.get("dependency_ids", [])

    reward = 0.0

    # --- Spam (including deceptive phishing) ---
    if label == "spam":
        if act == "ignore":
            # Extra reward if agent correctly ignores despite urgency language
            reward = 0.5 if urgency_score < 0.2 else 0.6
        elif act == "escalate":
            # Forward suspicious email to IT — partial credit
            reward = 0.15
        elif act == "reply":
            reward = -1.0   # Replying to phishing is a critical failure
        return reward, True

    # --- Complaints ---
    if label == "complaint":
        if priority == "high":
            if act == "escalate":
                content_bonus = _score_escalation_content(content, label, urgency_score)
                # Extra reward for recognising high-severity despite polite tone
                politeness_bonus = 0.1 if "polite" in context_clue or "tone" in context_clue else 0.0
                reward = 0.6 + content_bonus + politeness_bonus
            elif act == "reply":
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.1 + content_bonus   # Suboptimal — should escalate
            else:
                reward = -1.2   # Ignoring high-priority complaint = critical failure
        else:
            if act == "reply":
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.4 + content_bonus
            elif act == "escalate":
                reward = 0.25
            else:
                reward = -0.2
        return reward, True

    # --- Work emails ---
    if label == "work":
        # Dependency check: if this email has unmet deps tracked in state
        has_unmet_deps = len(dep_ids) > 0  # env.py will penalise separately if not completed

        if act == "reply":
            content_bonus = _score_reply_content(content, label, priority, sender_role)
            # Manager/CEO emails need higher content quality
            if sender_role == "manager" and content_bonus < 0:
                reward = 0.1 + content_bonus   # Punish lazy replies to managers
            else:
                reward = 0.5 + content_bonus

        elif act == "escalate":
            # Escalating non-urgent work email = wrong choice
            reward = 0.05 if priority == "high" else -0.2

        else:  # ignore
            if priority == "high":
                reward = -1.0
            elif priority == "medium":
                reward = -0.3
            else:
                reward = 0.05   # Low-priority work email can be deferred
        return reward, True

    return 0.0, True


def grade_email_round2(state: dict, action: dict, world_model: dict) -> tuple:
    """
    Round2 grader: long-horizon, work+personal integration.

    World model context actively changes correct action:
    - Budget exhaustion changes correct response to budget request
    - Work/personal imbalance penalised over the episode
    - Trust decay affects score weighting
    - Conflict detection: personal email on same day as work email
    - Consequence chain: correct handling of email 1 prevents follow-up blocking email 6

    This grader is the hardest to exploit — correct action requires
    reasoning about the FULL inbox state, not just the current email.
    """
    label = state.get("label", "")
    priority = state.get("priority", "low")
    domain = state.get("domain", "work")
    sender_role = state.get("sender_role", "unknown")
    urgency_score = state.get("urgency_score", 0.5)
    context_clue = state.get("context_clue", "")
    due_day = state.get("due_day", 14)
    act = action.get("type", "")
    content = action.get("content", "") or ""
    dep_ids = state.get("dependency_ids", [])

    reward = 0.0

    # --- Update world model domain counters ---
    if domain == "work":
        world_model["work_actions"] = world_model.get("work_actions", 0) + 1
    else:
        world_model["personal_actions"] = world_model.get("personal_actions", 0) + 1

    # --- Spam ---
    if label == "spam":
        if act == "ignore":
            reward = 0.5
            # Bonus if agent correctly ignores despite all-caps urgency language
            if urgency_score == 0.0 and "all-caps" in context_clue:
                reward += 0.1
        elif act == "reply":
            reward = -0.9
        elif act == "escalate":
            reward = 0.1
        return _apply_balance_bonus(reward, world_model), True

    # --- Complaint ---
    if label == "complaint":
        if priority == "high":
            if act == "escalate":
                content_bonus = _score_escalation_content(content, label, urgency_score)
                # Critical path email (id=1 in round2): escalating correctly prevents follow-up penalty
                reward = 0.6 + content_bonus
                if urgency_score >= 0.9:
                    reward += 0.15   # Extra reward for recognising critical path
            elif act == "reply":
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.1 + content_bonus
            else:
                reward = -1.5   # Ignoring critical complaint with $200K at stake
        else:
            if act == "reply":
                content_bonus = _score_reply_content(content, label, priority, sender_role)
                reward = 0.4 + content_bonus
            elif act == "escalate":
                reward = 0.25
            else:
                reward = -0.25
        return _apply_balance_bonus(reward, world_model), True

    # --- Work ---
    if label == "work":
        # Budget-aware scoring for budget request emails
        budget_exhausted = world_model.get("budget_remaining", 100000) < 80000
        body = state.get("body", "").lower()
        is_budget_request = "budget" in body or "80,000" in body or "offsite" in body

        if is_budget_request and budget_exhausted:
            # Agent should decline/escalate budget request when budget is low
            if act == "reply" and any(w in content.lower() for w in ["decline", "unfortunately", "budget", "cannot approve", "not possible"]):
                reward = 0.5
            elif act == "reply":
                reward = -0.1   # Generic reply to budget request when broke = bad
            elif act == "escalate":
                reward = 0.35   # Escalate for approval = acceptable
            else:
                reward = -0.2
            return _apply_balance_bonus(reward, world_model), True

        # Conflict detection: personal Thursday 4pm vs client call Thursday 3pm
        conflict_signal = "conflict" in context_clue or ("thursday" in body and domain == "personal")
        if conflict_signal:
            # Agent should acknowledge conflict in reply content
            if act == "reply" and any(w in content.lower() for w in ["conflict", "clash", "same time", "thursday", "reschedule", "alternative"]):
                reward = 0.55
            elif act == "reply":
                reward = 0.2    # Reply without noting conflict = missed insight
            elif act == "ignore":
                reward = -0.5 if priority == "high" else -0.1
            else:
                reward = 0.2
            return _apply_balance_bonus(reward, world_model), True

        # Standard work email scoring
        if act == "reply":
            content_bonus = _score_reply_content(content, label, priority, sender_role)
            if priority == "high":
                reward = 0.55 + content_bonus
            elif priority == "medium":
                reward = 0.4 + content_bonus
            else:
                reward = 0.25 + content_bonus

        elif act == "escalate":
            if priority == "high" and sender_role == "manager":
                content_bonus = _score_escalation_content(content, label, urgency_score)
                reward = 0.45 + content_bonus
            elif priority == "high":
                reward = 0.3
            else:
                reward = -0.1

        else:  # ignore
            if priority == "high":
                reward = -1.2
            elif priority == "medium":
                reward = -0.35
            else:
                reward = 0.05

        return _apply_balance_bonus(reward, world_model), True

    return 0.0, True


def _apply_balance_bonus(reward: float, world_model: dict) -> float:
    """
    Apply a small bonus when the agent maintains balanced work/personal attention.
    This incentivises the agent to not ignore personal domain emails completely.
    """
    work = world_model.get("work_actions", 0)
    personal = world_model.get("personal_actions", 0)

    if reward > 0 and work > 0 and personal > 0:
        ratio = min(work, personal) / max(work, personal)
        reward += 0.06 * ratio   # Up to +0.06 for perfect balance

    return reward