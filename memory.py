"""
memory.py | Recursive Intelligence Kernel (RIK)
--------------------------------------------------------------------
Manages multi-type memory persistence for the Recursive Intelligence Kernel.
Handles episodic storage, semantic mappings, and dependency-aware consolidation.
"""

import sqlite3
import json
from datetime import datetime


# ==========================================================
# 🧠  INITIALIZATION
# ==========================================================

def init_memory_db():
    """
    Initialize the SQLite memory database with required tables if missing.
    """
    conn = sqlite3.connect("data/memory.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            result TEXT,
            reflection TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            component TEXT,
            change_description TEXT,
            performance_before REAL,
            performance_after REAL,
            rollback_code TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT,
            success_rate REAL,
            avg_confidence REAL,
            last_updated TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ==========================================================
# 💾  EPISODIC MEMORY
# ==========================================================

def save_episode(task: str, result: str, reflection: str):
    """
    Save a new episodic memory entry to the database.
    """
    conn = sqlite3.connect("data/memory.db")
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO episodes (timestamp, task, result, reflection) VALUES (?, ?, ?, ?)",
        (timestamp, task, result, reflection),
    )
    conn.commit()
    conn.close()
    print(f"[MEMORY] Episode saved at {timestamp}")


def get_recent_episodes(limit: int = 5):
    """
    Return the most recent episodic memory entries from the database.
    """
    conn = sqlite3.connect("data/memory.db")
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        episodes = []
        for row in rows:
            episodes.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "task": row[2],
                    "result": row[3],
                    "reflection": row[4],
                }
            )
        return episodes
    except Exception as e:
        print(f"[MEMORY-ERROR] {e}")
        return [{"error": str(e)}]
    finally:
        conn.close()


# ==========================================================
# 🧩  CONSOLIDATION AND PRUNING
# ==========================================================

def consolidate_episodes():
    """
    Placeholder for DBSCAN-style consolidation logic.
    Groups similar episodes into higher-level abstractions.
    """
    print("[MEMORY] Consolidation step executed.")
    return True


# ==========================================================
# 🧠  MEMORY RETRIEVAL / UTILITY
# ==========================================================

def retrieve_context(task: str):
    """
    Retrieve memory context similar to the provided task.
    """
    conn = sqlite3.connect("data/memory.db")
    c = conn.cursor()
    try:
        c.execute("SELECT reflection FROM episodes ORDER BY id DESC LIMIT 1")
        last_reflection = c.fetchone()
        if last_reflection:
            return {"context": last_reflection[0]}
        return {"context": None}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


# ==========================================================
# 🧪  SELF-TEST
# ==========================================================

if __name__ == "__main__":
    init_memory_db()
    save_episode("System boot test", "success", "RIK initialized correctly.")
    print(get_recent_episodes())