from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

def plot_event_study():
    df = pd.read_csv(RESULTS / "event_study.csv").sort_values("event_time")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        df["event_time"], df["coef"],
        yerr=1.96 * df["se"], fmt="o", capsize=3
    )
    ax.axhline(0, linewidth=1)
    ax.axvline(-1, linestyle="--", linewidth=1)
    ax.set_xlabel("Weeks relative to advertising adoption")
    ax.set_ylabel("Effect on log(1 + bookings)")
    ax.set_title("Event Study: Dynamic Effect of Sponsored Advertising")
    fig.tight_layout()
    out = RESULTS / "event_study.png"
    fig.savefig(out, dpi=160)
    print(f"Saved {out}")

if __name__ == "__main__":
    plot_event_study()
