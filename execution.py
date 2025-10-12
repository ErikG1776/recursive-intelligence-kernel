"""
execution.py | Recursive Intelligence Kernel (RIK) v5.0
Brick 9: Concurrency Locks (final stable version)
------------------------------------------------------------
Provides single-connection exclusive transactions for
safe multi-agent database access.
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "memory.db")


# ==========================================================
# === Core Locking Utilities ===============================
# ==========================================================
@contextmanager
def sqlite_lock(timeout: int = 30):
    """
    Opens one connection, takes exclusive control of the DB,
    performs operations, then commits or rolls back safely.
    """
    conn = sqlite3.connect(DB_PATH, timeout=timeout)
    conn.isolation_level = None  # Manual control
    try:
        conn.execute("BEGIN EXCLUSIVE")
        yield conn
        conn.commit()
        print(f"[🔒] Transaction committed at {datetime.utcnow().isoformat()}")
    except Exception as e:
        conn.rollback()
        print(f"[⚠️] Transaction rolled back due to: {e}")
    finally:
        conn.close()


def execute_with_lock(query: str, params: tuple = ()):
    """
    Executes a simple SQL write operation under exclusive lock.
    Example:
        execute_with_lock("INSERT INTO ...", (val1, val2))
    """
    with sqlite_lock() as conn:
        conn.execute(query, params)


# ==========================================================
# === Demo Write Test ======================================
# ==========================================================
def _demo_write():
    """Single-connection demo write to verify locking behavior."""
    with sqlite_lock() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS concurrency_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                timestamp TEXT
            )
        """)
        c.execute(
            "INSERT INTO concurrency_test (message, timestamp) VALUES (?, ?)",
            ("lock_test", datetime.utcnow().isoformat())
        )
        print("[✅] Demo write completed.")


if __name__ == "__main__":
    print("[ℹ️] Testing SQLite concurrency lock system (final version)...")
    _demo_write()