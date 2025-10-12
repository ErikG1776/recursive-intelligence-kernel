"""
episodic_memory_analyzer.py | RIK-Fail-Safe Phase 4 – Brick 2
--------------------------------------------------------------
Analyzes the episodic_memory table to find which recovery
strategies work best over time.
"""

import os
import sqlite3
from collections import defaultdict

# === Correct path to the main memory.db ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))

def analyze_strategies():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT strategy, COUNT(*), 
               ROUND(AVG(predicted_success), 3) AS avg_predicted_success,
               SUM(CASE WHEN actual_outcome = 'success' THEN 1 ELSE 0 END) AS successes
        FROM episodic_memory
        GROUP BY strategy
        ORDER BY successes DESC;
    """)
    results = c.fetchall()
    conn.close()

    if not results:
        print("No episodes found in episodic_memory.")
        return

    print("\n📊 Strategy Effectiveness Summary:\n")
    for strategy, count, avg_conf, successes in results:
        success_rate = (successes / count) * 100 if count else 0
        print(f"🧠 {strategy or 'Unknown Strategy'}")
        print(f"   • Uses: {count}")
        print(f"   • Successes: {successes}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Avg Predicted Confidence: {avg_conf}\n")

def main():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return
    analyze_strategies()

if __name__ == "__main__":
    main()