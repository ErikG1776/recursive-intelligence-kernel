"""
episodic_memory_loader.py | RIK-Fail-Safe Phase 4 – Brick 1 (Fixed Path)
-----------------------------------------------------------------------
Reads JSON audit logs and stores summarized experiences
into the episodic_memory table inside rik_v5/data/memory.db.
"""

import os, json, sqlite3, datetime

# === Correct absolute path to the real memory.db ===
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/memory.db"))
LOG_DIR = os.path.join(os.path.dirname(__file__), "audit_logs")

def connect_db():
    """Connect to the existing memory.db and ensure episodic_memory table exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            error_type TEXT,
            strategy TEXT,
            predicted_success REAL,
            actual_outcome TEXT,
            context TEXT
        );
    """)
    conn.commit()
    return conn, c

def parse_logs():
    """Read audit log files and extract recovery episodes."""
    episodes = []
    for file in os.listdir(LOG_DIR):
        if not file.startswith("audit_") or not file.endswith(".json"):
            continue
        with open(os.path.join(LOG_DIR, file)) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry["event"] == "RECOVERY":
                    strategy_data = entry["data"].get("strategy", {})
                    episodes.append({
                        "timestamp": entry["timestamp"],
                        "error_type": entry["message"],
                        "strategy": strategy_data.get("chosen_strategy"),
                        "predicted_success": strategy_data.get("predicted_success"),
                        "actual_outcome": strategy_data.get("status"),
                        "context": json.dumps(entry.get("data", {}))
                    })
    return episodes

def load_to_db(episodes):
    """Write parsed episodes into episodic_memory."""
    conn, c = connect_db()
    for e in episodes:
        c.execute("""
            INSERT INTO episodic_memory
            (timestamp, error_type, strategy, predicted_success, actual_outcome, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            e["timestamp"], e["error_type"], e["strategy"],
            e["predicted_success"], e["actual_outcome"], e["context"]
        ))
    conn.commit()
    conn.close()
    print(f"✅  {len(episodes)} episodes written to episodic_memory.")

def main():
    if not os.path.exists(LOG_DIR):
        print("No audit_logs folder found.")
        return
    episodes = parse_logs()
    if not episodes:
        print("No recovery episodes found in logs.")
        return
    load_to_db(episodes)

if __name__ == "__main__":
    main()