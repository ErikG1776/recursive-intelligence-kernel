"""
self_updating_confidence.py | RIK-Fail-Safe Phase 4 – Brick 7
-----------------------------------------------------------------
Automatically recalibrates strategy confidence scores after each run.
This closes the recursive loop: reflection → learning → adaptation → reflection.
"""

import os
import sqlite3

# === Correct path to main memory.db ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "memory.db"))
def create_weights_table():
    """Ensure the strategy_weights table exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS strategy_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT UNIQUE,
            success_rate REAL,
            avg_confidence REAL,
            last_updated TEXT
        );
    """)
    conn.commit()
    conn.close()

def recalculate_weights():
    """Recompute success rates and update the strategy_weights table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Compute metrics from episodic_memory
    c.execute("""
        SELECT strategy,
               COUNT(*) AS uses,
               SUM(CASE WHEN actual_outcome='success' THEN 1 ELSE 0 END)*1.0 / COUNT(*) AS success_rate,
               ROUND(AVG(predicted_success), 3) AS avg_conf
        FROM episodic_memory
        GROUP BY strategy;
    """)
    rows = c.fetchall()

    if not rows:
        print("No episodic memory data found.")
        conn.close()
        return

    # Create weights table if not already present
    create_weights_table()

    for strategy, uses, success_rate, avg_conf in rows:
        if not strategy:
            continue
        c.execute("""
            INSERT INTO strategy_weights (strategy, success_rate, avg_confidence, last_updated)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(strategy) DO UPDATE SET
                success_rate=excluded.success_rate,
                avg_confidence=excluded.avg_confidence,
                last_updated=datetime('now');
        """, (strategy, success_rate, avg_conf))
        print(f"🧠 Updated '{strategy}' → Success Rate: {round(success_rate,3)} | Avg Confidence: {avg_conf}")

    conn.commit()
    conn.close()
    print("\n✅ Strategy weights recalibrated and saved to strategy_weights table.")

def main():
    print("\n🧩 Running Self-Updating Confidence Calibration...")
    recalculate_weights()

if __name__ == "__main__":
    main()