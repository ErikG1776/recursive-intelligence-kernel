"""
learning_progress_dashboard.py | RIK-Fail-Safe Phase 4 – Brick 4
-----------------------------------------------------------------
Visualizes how the system's learning (success rates and confidence)
improves over time from the episodic_memory table.
"""

import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# === Correct path to main memory.db ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))

def fetch_learning_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, predicted_success, actual_outcome
        FROM episodic_memory
        ORDER BY timestamp ASC;
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def plot_learning_curve(data):
    if not data:
        print("No episodic memory data available.")
        return

    timestamps = []
    confidence_scores = []
    success_points = []

    for ts, pred, outcome in data:
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            continue
        timestamps.append(dt)
        confidence_scores.append(pred or 0)
        success_points.append(1 if outcome == "success" else 0)

    plt.figure(figsize=(10,5))
    plt.plot(timestamps, confidence_scores, label="Predicted Confidence", color="#3c78d8", marker="o")
    plt.plot(timestamps, success_points, label="Actual Success (1=Success)", color="#6aa84f", linestyle="--")
    plt.title("RIK-Fail-Safe Learning Progress Over Time")
    plt.xlabel("Time")
    plt.ylabel("Confidence / Success")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    data = fetch_learning_data()
    if not data:
        print("No data found in episodic_memory.")
        return
    print(f"Loaded {len(data)} episodes for visualization.")
    plot_learning_curve(data)

if __name__ == "__main__":
    main()