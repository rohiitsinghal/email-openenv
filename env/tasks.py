from .models import Email

def load_task(task_level):
    if task_level == "easy":
        return [
            Email(id=1, subject="Refund", body="Refund #123", label="complaint"),
            Email(id=2, subject="Meeting", body="Schedule meeting", label="work"),
        ]

    elif task_level == "medium":
        return [
            Email(id=1, subject="Order delay", body="Order #123 delayed", label="complaint"),
            Email(id=2, subject="Invoice", body="Send invoice #456", label="work"),
            Email(id=3, subject="Spam", body="Win money now", label="spam"),
        ]

    else:
        return [
            Email(id=1, subject="Refund urgent", body="Refund #123 ASAP", label="complaint"),
            Email(id=2, subject="CEO meeting", body="Schedule meeting 9am", label="work"),
            Email(id=3, subject="Lottery", body="You won money!!!", label="spam"),
            Email(id=4, subject="Delay complaint", body="Order #999 delayed", label="complaint"),
        ]