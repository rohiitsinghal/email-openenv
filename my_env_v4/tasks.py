from .models import Email


def load_task(level):
    if level == "easy":
        return [
            Email(id=1, subject="Meeting tomorrow", body="Please confirm meeting time.", label="work", priority="medium"),
            Email(id=2, subject="Limited-time offer", body="Click now to claim prize.", label="spam", priority="low"),
            Email(id=3, subject="Project update needed", body="Can you share the latest status on the project?", label="work", priority="medium"),
            Email(id=4, subject="You have won a lottery", body="Claim your lottery prize now by clicking here.", label="spam", priority="low"),
        ]

    if level == "medium":
        return [
            Email(id=1, subject="Client payment failed", body="Please help urgently.", label="complaint", priority="high"),
            Email(id=2, subject="Weekly check-in", body="No rush, share updates.", label="work", priority="low"),
            Email(id=3, subject="Weekly newsletter", body="Top tech stories this week.", label="spam", priority="low"),
            Email(id=4, subject="Refund not received", body="I have been waiting 2 weeks for my refund.", label="complaint", priority="high"),
            Email(id=5, subject="Team lunch tomorrow", body="Please confirm if you can join team lunch.", label="work", priority="low"),
        ]

    if level == "hard":
        return [
            Email(id=1, subject="Security alert", body="Suspicious login detected.", label="complaint", priority="high"),
            Email(id=2, subject="CEO review prep", body="Need final deck by 5 PM.", label="work", priority="high"),
            Email(id=3, subject="You won", body="Claim your reward instantly.", label="spam", priority="low"),
            Email(id=4, subject="Order charged twice", body="Please resolve billing issue.", label="complaint", priority="medium"),
            Email(id=5, subject="Sprint planning invite", body="Confirm attendance for sprint planning session.", label="work", priority="medium"),
            Email(id=6, subject="Free iPhone giveaway", body="You have been selected for a free iPhone.", label="spam", priority="low"),
        ]

    if level == "round2":
        return load_round2_task()

    return []


def load_round2_task():
    return [
        Email(id=1, subject="Client escalation: payment failed", body="Major account blocked. Needs urgent follow-up.", label="complaint", priority="high", domain="work", due_day=2),
        Email(id=6, subject="Client review call confirmation", body="Confirm agenda and final report attachment.", label="work", priority="high", domain="work", due_day=4),
        Email(id=5, subject="Quarterly report draft needed", body="Complete report before client review call.", label="work", priority="medium", domain="work", due_day=5, dependency_ids=[6]),
        Email(id=2, subject="Team standup reschedule", body="Please confirm a new slot for tomorrow.", label="work", priority="medium", domain="work", due_day=6),
        Email(id=3, subject="School reminder: parent meeting", body="Reminder for Friday evening parent meeting.", label="work", priority="high", domain="personal", due_day=7),
        Email(id=4, subject="Electricity bill due", body="Bill payment due this week to avoid late fee.", label="work", priority="high", domain="personal", due_day=8),
        Email(id=7, subject="Limited offer! Click now", body="This is likely promotional spam.", label="spam", priority="low", domain="personal", due_day=10),
    ]
