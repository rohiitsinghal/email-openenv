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