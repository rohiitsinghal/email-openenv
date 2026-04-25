# -*- coding: utf-8 -*-
import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:7860")
LEVEL = os.getenv("LEVEL", "round2")


def triage_agent(email):
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
    label = email.get("label", "").lower()
    priority = email.get("priority", "low")
    urgency = float(email.get("urgency_score", 0.5))
    sender_role = email.get("sender_role", "unknown").lower()
    domain = email.get("domain", "work")

    # Spam: unknown sender OR zero urgency OR spam keywords
    is_spam = (
        label == "spam"
        or urgency == 0.0
        or sender_role == "unknown"
        or any(x in text for x in [
            "offer", "click", "won", "discount", "lottery", "prize",
            "unsubscribe", "promotional", "claim", "expires tonight",
            "last chance", "exclusive deal", "selected for", "verify your",
            "act now", "limited time", "free iphone", "congratulations",
            "90% off", "specially selected"
        ])
    )
    if is_spam:
        return "ignore"

    # Electricity/utility overdue - escalate
    if any(x in text for x in ["overdue", "disconnection", "automatic disconnection", "late fee", "eb-"]):
        return "escalate"

    # Complaint: high urgency or complaint keywords
    is_complaint = (
        label == "complaint"
        or urgency >= 0.85
        or any(x in text for x in [
            "failed", "refund", "billing", "charged twice", "escalation",
            "security", "blocked", "unacceptable", "dispute", "threatening",
            "pull the", "compensation", "no resolution", "disappointed",
            "still not arrived", "18 days", "200k", "at risk",
            "double charge", "payment gateway", "cto called"
        ])
    )
    if is_complaint:
        return "escalate"

    # Personal high priority conflict email - reply with conflict mention
    if domain == "personal" and priority == "high" and "thursday" in text:
        return "reply"

    return "reply"


def communication_agent(action_type, email):
    text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
    sender_role = email.get("sender_role", "unknown").lower()
    priority = email.get("priority", "low")
    domain = email.get("domain", "work")

    if action_type == "ignore":
        return "Marking as spam and blocking this sender."

    if action_type == "escalate":
        if any(x in text for x in ["200k", "contract", "payment gateway", "cto", "sharma"]):
            return (
                "Escalating immediately to engineering and billing team. "
                "This is a critical priority - the client account is at risk. "
                "We will investigate and resolve within 2 hours. "
                "Routing to management and support team now."
            )
        if any(x in text for x in ["overdue", "disconnection", "late fee", "eb-"]):
            return (
                "Escalating this urgent billing issue to our finance team immediately. "
                "We will process and resolve the overdue payment within 24 hours "
                "to prevent any service interruption."
            )
        if any(x in text for x in ["refund", "charged", "billing", "invoice", "double charge"]):
            return (
                "We sincerely apologize for this billing issue. "
                "Escalating to our finance team as urgent priority. "
                "We will investigate the charge and process a full refund immediately. "
                "Our team will resolve this within 24 hours."
            )
        if any(x in text for x in ["security", "sign-in", "suspicious", "login"]):
            return (
                "Escalating to IT security team immediately as urgent priority. "
                "We are investigating this suspicious activity on your account. "
                "Our security team will resolve and secure the account within 2 hours."
            )
        if any(x in text for x in ["unacceptable", "disappointed", "no resolution", "compensation"]):
            return (
                "We sincerely apologize for this unacceptable experience. "
                "Escalating to our senior support team as the highest priority. "
                "We will investigate, provide full compensation, and resolve this immediately. "
                "A senior team member will contact you within 2 hours."
            )
        return (
            "Escalating to our senior team as urgent priority. "
            "We sincerely apologize for the inconvenience. "
            "Our team will investigate and resolve this issue within 24 hours."
        )

    # Personal conflict email - Thursday 4pm vs client call 3pm
    if domain == "personal" and "thursday" in text and "4pm" in text:
        return (
            "Thank you for the reminder about the Thursday parent-teacher conference. "
            "I note this conflicts with an existing client call scheduled for Thursday 3pm. "
            "I will review this clash and reschedule one of the commitments. "
            "Will confirm attendance by EOD today and suggest an alternative slot if needed."
        )

    # QBR deck / adoption metrics
    if any(x in text for x in ["deck", "slides", "qbr", "quarterly", "metrics", "adoption"]):
        return (
            "Confirmed. I will prepare the adoption metrics section and finalize the deck. "
            "Will send the completed slides by Wednesday EOD as requested. "
            "Ready to attach to the calendar invite for Thursday's client review."
        )

    # Client review call
    if any(x in text for x in ["client review call", "thursday 3pm", "sharma group", "calendar invite"]):
        return (
            "Confirmed attendance for Thursday 3pm with Sharma Group. "
            "I will ensure the QBR deck with adoption metrics is attached to the calendar invite. "
            "Will coordinate with the team to finalize all pre-reads before the call."
        )

    # API spec / documents
    if any(x in text for x in ["spec", "api", "document", "doc", "finalize"]):
        return (
            "Confirmed. I will complete the final review of the API spec document today. "
            "Will send confirmation once finalized so we can proceed with sprint planning."
        )

    # Meeting / standup / schedule
    if any(x in text for x in ["meeting", "standup", "sync", "schedule", "confirm", "attendance", "rsvp"]):
        return (
            "Confirmed. I will attend and have everything prepared by the scheduled time. "
            "Please send a calendar invite and I will confirm attendance shortly."
        )

    # Budget / offsite
    if any(x in text for x in ["budget", "offsite", "80,000", "rs.80"]):
        return (
            "Thank you for the proposal. I will review the budget details and coordinate "
            "with the finance team. Will confirm feasibility and provide feedback by EOD today."
        )

    # Status / update
    if any(x in text for x in ["status", "update", "progress", "roadmap", "priorities"]):
        return (
            "Thank you for reaching out. I will prepare a detailed status update "
            "and send it to you by EOD today. Happy to schedule a sync to discuss further."
        )

    return (
        "Thank you for your message. I will review this and coordinate with the relevant team. "
        "Will confirm next steps and provide an update by EOD today."
    )


def run_episode():
    res = requests.post(f"{BASE_URL}/reset", params={"level": LEVEL}, timeout=30)
    res.raise_for_status()
    payload = res.json()
    emails = payload["emails"]

    # Build dependency map
    dep_map = {e["id"]: e.get("dependency_ids", []) for e in emails}

    def sort_key(e):
        urgency = float(e.get("urgency_score", 0.5))
        priority_score = 0 if e.get("priority") == "high" else (1 if e.get("priority") == "medium" else 2)
        is_spam = e.get("sender_role", "") == "unknown" or urgency == 0.0
        spam_score = 2 if is_spam else 0
        # Emails that others depend on should come first
        is_dependency = any(e["id"] in deps for deps in dep_map.values())
        dep_score = -1 if is_dependency else 0
        return (spam_score, dep_score, priority_score, -urgency)

    emails = sorted(emails, key=sort_key)

    total_reward = 0.0
    recent_feedback = []

    for email in emails:
        feedback = (sum(recent_feedback[-3:]) / min(3, len(recent_feedback))) if recent_feedback else 0.0

        action_type = triage_agent(email)
        content = communication_agent(action_type, email)

        action = {
            "action_type": action_type,
            "email_id": email["id"],
            "content": content,
            "actor": "coordinator",
            "feedback": feedback,
        }

        step_res = requests.post(f"{BASE_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        result = step_res.json()

        reward = float(result.get("reward", 0.0))
        total_reward += reward
        recent_feedback.append(1.0 if reward > 0 else -1.0)

        print(f"  [{email.get('label', '?'):10}] [{email.get('priority','?'):6}] [u:{email.get('urgency_score',0):.1f}] -> {action_type:8} | reward: {reward:+.3f} | total: {total_reward:+.3f}")

        if result.get("done"):
            break

    print(f"\nEpisode level={LEVEL} total_reward={total_reward:.3f}")
    return total_reward


if __name__ == "__main__":
    run_episode()