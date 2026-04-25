EPS = 1e-6


def _strict_unit(value):
    return min(max(float(value), EPS), 1.0 - EPS)


def grade_classification(pred, truth):
    return _strict_unit(1.0 if pred.lower() == truth.lower() else 0.0)


def grade_extraction(pred, truth):
    if pred.lower() in truth.lower():
        return _strict_unit(1.0)
    elif len(pred) > 0:
        return _strict_unit(0.5)
    return _strict_unit(0.0)


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

    return _strict_unit(min(score, 1.0))


# --- OpenEnv Task-Level Graders ---

def grade_email_easy(state, action):
    label = state.get("label", "")

    if action.get("type") == "reply":
        reward = grade_reply(action.get("content", ""), label)
    else:
        reward = 0.0

    return _strict_unit(reward), True


def grade_email_medium(state, action):
    label = state.get("label", "")

    if action.get("type") == "reply":
        reward = grade_reply(action.get("content", ""), label)
    elif action.get("type") == "escalate":
        reward = 0.5
    else:
        reward = 0.0

    return _strict_unit(reward), True


def grade_email_hard(state, action):
    label = state.get("label", "")
    reward = 0.0

    if action.get("type") == "reply":
        reward += grade_reply(action.get("content", ""), label)

    if action.get("type") == "ignore" and label == "spam":
        reward += 0.5

    return _strict_unit(min(reward, 1.0)), True