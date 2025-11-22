"""
db.py | Recursive Intelligence Algorithm (RIA) v5.0
----------------------------------------------------
Database connection management with proper context managers and pooling.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional, Any
from config import DB_PATH, DB_TIMEOUT, setup_logging

logger = setup_logging("rik.db")

# ==========================================================
# === Connection Manager ===================================
# ==========================================================

@contextmanager
def get_connection(timeout: int = DB_TIMEOUT) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with automatic cleanup.

    Usage:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=timeout)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_cursor(commit: bool = True) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager that provides a cursor with automatic commit/rollback.

    Usage:
        with get_cursor() as cursor:
            cursor.execute("INSERT INTO table VALUES (?)", (value,))
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed, rolling back: {e}")
            raise


@contextmanager
def exclusive_lock(timeout: int = DB_TIMEOUT) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for exclusive database access (for concurrent operations).

    Usage:
        with exclusive_lock() as conn:
            conn.execute("INSERT INTO table VALUES (?)", (value,))
    """
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=timeout)
        conn.isolation_level = None  # Manual control
        conn.execute("BEGIN EXCLUSIVE")
        yield conn
        conn.commit()
        logger.debug("Exclusive transaction committed")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Exclusive transaction rolled back: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ==========================================================
# === Utility Functions ====================================
# ==========================================================

def execute_query(query: str, params: tuple = (), fetch: bool = False) -> Optional[list]:
    """
    Execute a query with automatic connection management.

    Args:
        query: SQL query string
        params: Query parameters
        fetch: If True, return results; otherwise return None

    Returns:
        List of rows if fetch=True, else None
    """
    with get_cursor() as cursor:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
    return None


def execute_many(query: str, params_list: list[tuple]) -> int:
    """
    Execute batch insert/update operations efficiently.

    Args:
        query: SQL query string with placeholders
        params_list: List of parameter tuples

    Returns:
        Number of rows affected
    """
    with get_cursor() as cursor:
        cursor.executemany(query, params_list)
        return cursor.rowcount


def init_table(create_statement: str) -> None:
    """Initialize a table if it doesn't exist."""
    with get_cursor() as cursor:
        cursor.execute(create_statement)


# ==========================================================
# === Index Management =====================================
# ==========================================================

def create_indexes() -> None:
    """Create indexes for frequently queried columns."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_strategy_weights_strategy ON strategy_weights(strategy)",
        "CREATE INDEX IF NOT EXISTS idx_episodic_memory_strategy ON episodic_memory(strategy)",
        "CREATE INDEX IF NOT EXISTS idx_episodic_memory_outcome ON episodic_memory(actual_outcome)",
        "CREATE INDEX IF NOT EXISTS idx_modifications_component ON modifications(component)",
    ]
    with get_cursor() as cursor:
        for idx_sql in indexes:
            try:
                cursor.execute(idx_sql)
            except sqlite3.OperationalError:
                pass  # Table may not exist yet
    logger.info("Database indexes created/verified")
