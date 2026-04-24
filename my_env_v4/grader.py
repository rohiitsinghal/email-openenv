def grade_classification(pred, truth):
    return 1.0 if pred.lower() == truth.lower() else 0.0


def grade_extraction(pred, truth):
    if pred.lower() in truth.lower():
        return 1.0
    elif len(pred) > 0:
        return 0.5
    return 0.0


def grade_reply(reply, label):
    reply = reply.lower()
    score = 0.0

    if label == "complaint":
        if any(word in reply for word in ["sorry", "apologize"]):
            score += 0.5
        if any(word in reply for word in ["refund", "process", "issue"]):
            score += 0.5

    elif label == "work":
        if any(word in reply for word in ["meeting", "schedule", "confirm"]):
            score += 1.0

    elif label == "spam":
        if any(word in reply for word in ["ignore", "spam", "block"]):
            score += 1.0

    return min(score, 1.0)


# --- OpenEnv Task-Level Graders ---

def grade_email_easy(state, action):
    label = state.get("label", "")

    if action.get("type") == "reply":
        reward = grade_reply(action.get("content", ""), label)
    else:
        reward = 0.0

    return reward, True


def grade_email_medium(state, action):
    label = state.get("label", "")

    if action.get("type") == "reply":
        reward = grade_reply(action.get("content", ""), label)
    elif action.get("type") == "escalate":
        reward = 0.5
    else:
        reward = 0.0

    return reward, True


def grade_email_hard(state, action):
    label = state.get("label", "")
    priority = state.get("priority", "")
    act = action.get("type")

    reward = 0.0

    # --- Best actions (full reward) ---
    if label == "complaint" and act == "escalate":
        reward = 1.0
    elif label == "work" and act == "reply":
        reward = 0.8
    elif label == "spam" and act == "ignore":
        reward = 0.7

    # --- Partially correct actions ---
    elif label == "complaint" and act == "reply":
        reward = 0.5
    elif label == "work" and act == "ignore":
        reward = 0.3

    # --- Wrong / harmful actions ---
    elif label == "spam" and act == "reply":
        reward = -0.5
    elif act == "ignore" and priority == "high":
        reward = -0.7

    return reward, True


def grade_email_round2(state, action, world_model):
    label = state.get("label", "")
    priority = state.get("priority", "")
    domain = state.get("domain", "work")
    act = action.get("type")

    reward = 0.0

    if label == "spam" and act == "ignore":
        reward += 0.9
    elif label == "complaint" and act == "escalate":
        reward += 1.0
    elif label == "work" and act == "reply":
        reward += 0.8
    elif act in ["reply", "ignore", "escalate"]:
        reward += 0.2

    if priority == "high" and act == "ignore":
        reward -= 0.9

    if domain == "work":
        world_model["work_actions"] = world_model.get("work_actions", 0) + 1
    else:
        world_model["personal_actions"] = world_model.get("personal_actions", 0) + 1

    work_actions = world_model.get("work_actions", 0)
    personal_actions = world_model.get("personal_actions", 0)
    if personal_actions > 0 and work_actions > 0:
        ratio = min(work_actions, personal_actions) / max(work_actions, personal_actions)
        reward += 0.2 * ratio

    return reward, True