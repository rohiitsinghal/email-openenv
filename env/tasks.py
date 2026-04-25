from .models import Email

def load_task(task_level):
    if task_level == "easy":
        return [
            Email(id=1, subject="Refund", body="Refund #123", label="complaint", priority="high"),
            Email(id=2, subject="Meeting", body="Schedule meeting", label="work", priority="medium"),
        ]

    elif task_level == "medium":
        return [
            Email(id=1, subject="Order delay", body="Order #123 delayed", label="complaint", priority="high"),
            Email(id=2, subject="Invoice", body="Send invoice #456", label="work", priority="medium"),
            Email(id=3, subject="Spam", body="Win money now", label="spam", priority="low"),
        ]

    else:  # hard
        return [
            Email(id=1, subject="Refund urgent", body="Refund #123 ASAP", label="complaint", priority="high"),
            Email(id=2, subject="CEO meeting", body="Schedule meeting 9am", label="work", priority="high"),
            Email(id=3, subject="Lottery", body="You won money!!!", label="spam", priority="low"),
            Email(id=4, subject="Delay complaint", body="Order #999 delayed", label="complaint", priority="medium"),
        ]