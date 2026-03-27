import requests

BASE_URL = "http://localhost:8000"

def run():
    requests.post(f"{BASE_URL}/reset?level=easy")

    steps = [
        {"action_type": "classify", "email_id": 1, "content": "complaint"},
        {"action_type": "extract", "email_id": 1, "content": "refund"},
        {"action_type": "reply", "email_id": 1, "content": "Sorry, your refund is processed"}
    ]

    for i, action in enumerate(steps):
        r = requests.post(f"{BASE_URL}/step", json=action).json()
        print(f"Step {i+1} Reward:", r["reward"])


if __name__ == "__main__":
    run()