import sys
import math
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


THRESHOLD_DEG = 10.0


def quat_to_roll_pitch(qr, qi, qj, qk):
    roll = math.degrees(math.atan2(2 * (qr * qi + qj * qk), 1 - 2 * (qi**2 + qj**2)))
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, 2 * (qr * qj - qk * qi)))))
    return roll, pitch


def load_csv(path):
    timestamps, rolls, pitches = [], [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S")
                qr, qi, qj, qk = float(row["qr"]), float(row["qi"]), float(row["qj"]), float(row["qk"])
            except (ValueError, KeyError):
                continue
            roll, pitch = quat_to_roll_pitch(qr, qi, qj, qk)
            timestamps.append(ts)
            rolls.append(roll)
            pitches.append(pitch)
    return timestamps, rolls, pitches


def make_time_axis(timestamps):
    if not timestamps:
        return []
    total = (timestamps[-1] - timestamps[0]).total_seconds()
    n = len(timestamps)
    return np.linspace(0, total, n)


def annotate_extremes(ax, t, values, color):
    i_max = int(np.argmax(values))
    i_min = int(np.argmin(values))
    for i, label in [(i_max, f"{values[i_max]:.1f}°"), (i_min, f"{values[i_min]:.1f}°")]:
        ax.annotate(
            label,
            xy=(t[i], values[i]),
            xytext=(t[i], values[i] + (6 if values[i] >= 0 else -6)),
            ha="center",
            fontsize=8,
            color=color,
            arrowprops=dict(arrowstyle="-", color=color, lw=0.8),
        )


def plot(path):
    timestamps, rolls, pitches = load_csv(path)
    if not timestamps:
        print(f"No valid data in {path}")
        return

    t = make_time_axis(timestamps)
    rolls = np.array(rolls)
    pitches = np.array(pitches)

    stem = os.path.splitext(os.path.basename(path))[0]
    out_dir = os.path.join("graphs", stem)
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(t, rolls, label="Roll", color="#2196F3", linewidth=0.8)
    ax.plot(t, pitches, label="Pitch", color="#FF5722", linewidth=0.8)

    ax.axhline(THRESHOLD_DEG, color="gray", linestyle="--", linewidth=0.8, label=f"+{THRESHOLD_DEG}°")
    ax.axhline(-THRESHOLD_DEG, color="gray", linestyle=":",  linewidth=0.8, label=f"-{THRESHOLD_DEG}°")

    annotate_extremes(ax, t, rolls, "#2196F3")
    annotate_extremes(ax, t, pitches, "#FF5722")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Angle (°)")
    ax.set_title(f"Roll & Pitch — {stem}")
    ax.legend(loc="upper right", fontsize=8)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="major", alpha=0.3)
    ax.grid(True, which="minor", alpha=0.1)

    out_path = os.path.join(out_dir, f"{stem}.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python graph.py <path/to/recording.csv>")
        sys.exit(1)
    plot(sys.argv[1])
