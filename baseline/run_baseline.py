import requests
import os

BASE_URL = "http://localhost:8000"

def simple_agent(email):
    subject = email["subject"].lower()
    body = email["body"].lower()

    # classification
    if "refund" in subject or "refund" in body:
        return "complaint"
    elif "win" in body or "offer" in subject:
        return "spam"
    elif "meeting" in subject or "schedule" in body:
        return "work"
    else:
        return "work"


def generate_reply(label):
    if label == "complaint":
        return "Sorry, your refund will be processed"
    elif label == "work":
        return "Your meeting has been scheduled"
    else:
        return "This looks like spam, ignoring it"


def run():
    # reset env
    res = requests.post(f"{BASE_URL}/reset?level=hard").json()
    emails = res["emails"]

    total_reward = 0

    for email in emails:
        email_id = email["id"]

        # Step 1: classify
        label = simple_agent(email)
        action = {
            "action_type": "classify",
            "email_id": email_id,
            "content": label
        }
        r = requests.post(f"{BASE_URL}/step", json=action).json()
        total_reward += r["reward"]

        # Step 2: reply
        reply = generate_reply(label)
        action = {
            "action_type": "reply",
            "email_id": email_id,
            "content": reply
        }
        r = requests.post(f"{BASE_URL}/step", json=action).json()
        total_reward += r["reward"]

    print("Final Reward:", total_reward)


if __name__ == "__main__":
    run()