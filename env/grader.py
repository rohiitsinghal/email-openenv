def grade_classification(pred, truth):
    return 1.0 if pred.lower() == truth.lower() else 0.0


def grade_extraction(pred, truth):
    if pred.lower() in truth.lower():
        return 1.0
    elif len(pred) > 0:
        return 0.5
    return 0.0


def grade_reply(reply, label):
    score = 0.0
    reply = reply.lower()

    if label == "complaint":
        if "sorry" in reply:
            score += 0.5
        if "refund" in reply:
            score += 0.5

    elif label == "work":
        if "schedule" in reply or "meeting" in reply:
            score += 1.0

    elif label == "spam":
        if "ignore" in reply or "spam" in reply:
            score += 1.0

    return min(score, 1.0)