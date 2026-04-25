import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def plot_reward_comparison():
    data = _load_json(ROOT / "training" / "reward_improvement.json")

    levels = list(data["baseline"].keys())
    baseline = [data["baseline"][lvl] for lvl in levels]
    improved = [data["improved"][lvl] for lvl in levels]

    x = range(len(levels))
    width = 0.35

    plt.figure(figsize=(9, 5))
    plt.bar([i - width / 2 for i in x], baseline, width=width, label="Baseline")
    plt.bar([i + width / 2 for i in x], improved, width=width, label="Improved")
    plt.xticks(list(x), levels)
    plt.xlabel("Task level")
    plt.ylabel("Total reward")
    plt.title("Baseline vs Improved Reward by Level")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ASSETS / "reward_comparison.png", dpi=180)
    plt.close()


def plot_training_curve():
    data = _load_json(ROOT / "training" / "train_metrics.json")

    steps = data["steps"]
    loss = data["loss"]
    accuracy = data["mean_token_accuracy"]

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(steps, loss, marker="o", color="#d62728", label="Loss")
    ax1.set_xlabel("Training step")
    ax1.set_ylabel("Loss", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#d62728")

    ax2 = ax1.twinx()
    ax2.plot(steps, accuracy, marker="s", color="#2ca02c", label="Mean token accuracy")
    ax2.set_ylabel("Mean token accuracy", color="#2ca02c")
    ax2.tick_params(axis="y", labelcolor="#2ca02c")

    fig.suptitle("Training Progress (loss and accuracy)")
    fig.tight_layout()
    plt.savefig(ASSETS / "training_curve.png", dpi=180)
    plt.close()


if __name__ == "__main__":
    plot_reward_comparison()
    plot_training_curve()
    print("Saved assets/reward_comparison.png and assets/training_curve.png")
