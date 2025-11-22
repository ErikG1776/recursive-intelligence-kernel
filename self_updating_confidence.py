"""
self_updating_confidence.py | RIK-Fail-Safe Phase 4 – Brick 7
-----------------------------------------------------------------
Automatically recalibrates strategy confidence scores after each run.
This closes the recursive loop: reflection → learning → adaptation → reflection.
"""

import os
import sqlite3
from datetime import datetime

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


def create_episodic_memory_table():
    """Ensure the episodic_memory table exists for strategy tracking."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            strategy TEXT,
            predicted_success REAL,
            actual_outcome TEXT,
            context TEXT
        );
    """)
    conn.commit()
    conn.close()


def recalculate_weights():
    """Recompute success rates and update the strategy_weights table."""
    # Ensure tables exist
    create_weights_table()
    create_episodic_memory_table()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if episodic_memory has any data
    c.execute("SELECT COUNT(*) FROM episodic_memory")
    count = c.fetchone()[0]

    if count == 0:
        print("[ℹ️] No episodic memory data found. Initializing with defaults.")
        # Insert default strategy weights
        default_strategies = [
            ("Retry with longer wait time", 0.75, 0.8),
            ("Reinitialize network session", 0.7, 0.75),
            ("Search with alternative selector", 0.65, 0.7),
            ("Re-run task with safe defaults", 0.8, 0.85),
        ]
        for strategy, success_rate, confidence in default_strategies:
            c.execute("""
                INSERT OR IGNORE INTO strategy_weights
                (strategy, success_rate, avg_confidence, last_updated)
                VALUES (?, ?, ?, ?)
            """, (strategy, success_rate, confidence, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        print("[✅] Default strategy weights initialized.")
        return

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

    for strategy, uses, success_rate, avg_conf in rows:
        if not strategy:
            continue
        c.execute("""
            INSERT INTO strategy_weights (strategy, success_rate, avg_confidence, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(strategy) DO UPDATE SET
                success_rate=excluded.success_rate,
                avg_confidence=excluded.avg_confidence,
                last_updated=excluded.last_updated;
        """, (strategy, success_rate, avg_conf, datetime.utcnow().isoformat()))
        print(f"[🧠] Updated '{strategy}' → Success Rate: {round(success_rate, 3)} | Avg Confidence: {avg_conf}")

    conn.commit()
    conn.close()
    print("\n[✅] Strategy weights recalibrated and saved to strategy_weights table.")


def main():
    print("\n🧩 Running Self-Updating Confidence Calibration...")
    recalculate_weights()


if __name__ == "__main__":
    main()