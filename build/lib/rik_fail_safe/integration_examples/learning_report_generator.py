"""
learning_report_generator.py | RIK-Fail-Safe Phase 4 – Brick 5
-----------------------------------------------------------------
Generates a shareable learning report summarizing episodic memory,
strategy effectiveness, and learning progress for presentations.
"""

import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def fetch_memory_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, error_type, strategy, predicted_success, actual_outcome
        FROM episodic_memory
        ORDER BY timestamp ASC;
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def summarize_strategies(rows):
    summary = {}
    for ts, err, strat, pred, outcome in rows:
        if not strat:
            continue
        if strat not in summary:
            summary[strat] = {"uses": 0, "successes": 0, "avg_conf": 0.0}
        summary[strat]["uses"] += 1
        if outcome == "success":
            summary[strat]["successes"] += 1
        summary[strat]["avg_conf"] += (pred or 0)
    for strat in summary:
        uses = summary[strat]["uses"]
        summary[strat]["avg_conf"] = round(summary[strat]["avg_conf"] / uses, 3)
    return summary

def generate_learning_chart(rows, output_path):
    timestamps = [datetime.fromisoformat(r[0]) for r in rows]
    confidences = [r[3] or 0 for r in rows]
    outcomes = [1 if r[4] == "success" else 0 for r in rows]

    plt.figure(figsize=(8,4))
    plt.plot(timestamps, confidences, label="Predicted Confidence", color="#3c78d8", marker="o")
    plt.plot(timestamps, outcomes, label="Actual Success (1=Success)", color="#6aa84f", linestyle="--")
    plt.title("RIK-Fail-Safe Learning Progress")
    plt.xlabel("Time")
    plt.ylabel("Confidence / Success")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_text_report(summary, chart_file):
    report_file = os.path.join(REPORTS_DIR, "learning_report.txt")
    with open(report_file, "w") as f:
        f.write("RIK-Fail-Safe Learning Report\n")
        f.write("="*40 + "\n\n")
        f.write("📅 Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        for strat, stats in summary.items():
            rate = (stats["successes"]/stats["uses"])*100
            f.write(f"🧠 {strat}\n")
            f.write(f"   • Uses: {stats['uses']}\n")
            f.write(f"   • Successes: {stats['successes']}\n")
            f.write(f"   • Success Rate: {rate:.1f}%\n")
            f.write(f"   • Avg Confidence: {stats['avg_conf']}\n\n")
        f.write(f"📊 Learning Chart: {chart_file}\n")
    print(f"✅ Text report generated: {report_file}")

def main():
    rows = fetch_memory_data()
    if not rows:
        print("No episodic memory data found.")
        return
    summary = summarize_strategies(rows)
    chart_file = os.path.join(REPORTS_DIR, "learning_progress.png")
    generate_learning_chart(rows, chart_file)
    generate_text_report(summary, chart_file)
    print(f"✅ Learning chart saved at: {chart_file}")

if __name__ == "__main__":
    main()