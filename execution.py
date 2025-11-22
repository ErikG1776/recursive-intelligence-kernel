"""
execution.py | Recursive Intelligence Algorithm (RIA) v5.0
Brick 9: Concurrency Locks (final stable version)
------------------------------------------------------------
Provides single-connection exclusive transactions for
safe multi-agent database access.
"""

from datetime import datetime
from config import setup_logging, DB_PATH, DB_TIMEOUT
from db import exclusive_lock, get_cursor

logger = setup_logging("rik.execution")


# ==========================================================
# === Core Locking Utilities ===============================
# ==========================================================

def execute_with_lock(query: str, params: tuple = ()) -> None:
    """
    Executes a simple SQL write operation under exclusive lock.

    Example:
        execute_with_lock("INSERT INTO ...", (val1, val2))
    """
    with exclusive_lock() as conn:
        conn.execute(query, params)
    logger.debug(f"Executed query with lock: {query[:50]}...")


def execute_batch_with_lock(query: str, params_list: list[tuple]) -> int:
    """
    Execute batch operations under exclusive lock.

    Args:
        query: SQL query with placeholders.
        params_list: List of parameter tuples.

    Returns:
        Number of rows affected.
    """
    with exclusive_lock() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor.rowcount


# ==========================================================
# === Demo Write Test ======================================
# ==========================================================

def _demo_write() -> None:
    """Single-connection demo write to verify locking behavior."""
    with exclusive_lock() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concurrency_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO concurrency_test (message, timestamp) VALUES (?, ?)",
            ("lock_test", datetime.utcnow().isoformat())
        )
    logger.info("Demo write completed successfully")


if __name__ == "__main__":
    logger.info("Testing SQLite concurrency lock system...")
    _demo_write()
