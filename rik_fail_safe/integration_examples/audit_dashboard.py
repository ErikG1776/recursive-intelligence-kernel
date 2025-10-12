"""
audit_dashboard.py | RIK-Fail-Safe Audit Log Visualizer
-------------------------------------------------------
Reads JSON audit logs from the audit_logs/ folder and
displays success, failure, and recovery statistics.
"""

import os
import json
import matplotlib.pyplot as plt
from collections import Counter

# === Locate the audit log folder ===
LOG_DIR = os.path.join(os.path.dirname(__file__), "audit_logs")

def load_logs():
    logs = []
    for file in os.listdir(LOG_DIR):
        if file.startswith("audit_") and file.endswith(".json"):
            with open(os.path.join(LOG_DIR, file)) as f:
                for line in f:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return logs

def analyze_logs(logs):
    events = Counter([entry["event"] for entry in logs])
    recoveries = [entry for entry in logs if entry["event"] == "RECOVERY"]
    avg_conf = None
    if recoveries:
        confidences = [
            entry["data"]["strategy"].get("predicted_success", 0)
            for entry in recoveries if "strategy" in entry["data"]
        ]
        avg_conf = sum(confidences) / len(confidences)
    return events, avg_conf

def plot_events(events, avg_conf):
    labels = list(events.keys())
    values = [events[k] for k in labels]
    plt.figure(figsize=(8,5))
    plt.bar(labels, values, color=['#6aa84f','#e69138','#3c78d8','#cc0000','#674ea7','#45818e'])
    plt.title("RIK-Fail-Safe Event Frequency")
    plt.xlabel("Event Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    if avg_conf is not None:
        print(f"\n📈 Average recovery confidence: {avg_conf:.2f}")
    else:
        print("\n📊 No recovery events yet to analyze.")

def main():
    if not os.path.exists(LOG_DIR):
        print("No audit_logs folder found.")
        return
    logs = load_logs()
    if not logs:
        print("No logs found in audit_logs/")
        return
    events, avg_conf = analyze_logs(logs)
    print("\n=== Event Summary ===")
    for k,v in events.items():
        print(f"{k}: {v}")
    plot_events(events, avg_conf)

if __name__ == "__main__":
    main()