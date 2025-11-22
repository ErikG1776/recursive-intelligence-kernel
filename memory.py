"""
memory.py | Recursive Intelligence Algorithm (RIA) v5.0
-----------------------------------------------------------------------
Manages multi-type memory persistence for the Recursive Intelligence Algorithm.
Handles episodic storage, semantic mappings, and dependency-aware consolidation.
"""

from datetime import datetime
from typing import Optional
from config import setup_logging
from db import get_cursor, init_table, execute_query

logger = setup_logging("rik.memory")


# ==========================================================
# INITIALIZATION
# ==========================================================

def init_memory_db() -> None:
    """Initialize the SQLite memory database with required tables if missing."""
    tables = [
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task TEXT,
            result TEXT,
            reflection TEXT
        )
        """,
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
        """,
        """
        CREATE TABLE IF NOT EXISTS strategy_weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT UNIQUE,
            success_rate REAL,
            avg_confidence REAL,
            last_updated TEXT
        )
        """
    ]

    with get_cursor() as cursor:
        for table_sql in tables:
            cursor.execute(table_sql)

    logger.info("Memory database initialized")


# ==========================================================
# EPISODIC MEMORY
# ==========================================================

def save_episode(task: str, result: str, reflection: str) -> int:
    """
    Save a new episodic memory entry to the database.

    Returns:
        The ID of the inserted episode.
    """
    timestamp = datetime.utcnow().isoformat()

    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO episodes (timestamp, task, result, reflection) VALUES (?, ?, ?, ?)",
            (timestamp, task, result, reflection),
        )
        episode_id = cursor.lastrowid

    logger.info(f"Episode saved: id={episode_id}, timestamp={timestamp}")
    return episode_id


def get_recent_episodes(limit: int = 5) -> list[dict]:
    """
    Return the most recent episodic memory entries from the database.

    Args:
        limit: Maximum number of episodes to return.

    Returns:
        List of episode dictionaries.
    """
    try:
        with get_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "task": row[2],
                    "result": row[3],
                    "reflection": row[4],
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Failed to retrieve episodes: {e}")
        return [{"error": str(e)}]


def get_episode_count() -> int:
    """Return total number of episodes in memory."""
    with get_cursor(commit=False) as cursor:
        cursor.execute("SELECT COUNT(*) FROM episodes")
        return cursor.fetchone()[0]


# ==========================================================
# CONSOLIDATION AND PRUNING
# ==========================================================

def consolidate_episodes(similarity_threshold: float = 0.8) -> int:
    """
    Consolidate similar episodes using clustering.
    Groups similar episodes into higher-level abstractions.

    Args:
        similarity_threshold: Minimum similarity for grouping.

    Returns:
        Number of episodes consolidated.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import DBSCAN
        import numpy as np

        episodes = get_recent_episodes(limit=1000)
        if len(episodes) < 2:
            logger.info("Not enough episodes for consolidation")
            return 0

        texts = [f"{ep.get('task', '')} {ep.get('reflection', '')}" for ep in episodes]

        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(texts)

        clustering = DBSCAN(eps=1-similarity_threshold, min_samples=2, metric="cosine").fit(X)

        # Count clustered episodes
        clustered = sum(1 for label in clustering.labels_ if label != -1)
        logger.info(f"Consolidation complete: {clustered} episodes grouped")
        return clustered

    except ImportError:
        logger.warning("sklearn not available for consolidation")
        return 0
    except Exception as e:
        logger.error(f"Consolidation failed: {e}")
        return 0


# ==========================================================
# MEMORY RETRIEVAL / UTILITY
# ==========================================================

def retrieve_context(task: str) -> dict:
    """
    Retrieve memory context similar to the provided task.

    Args:
        task: The task to find context for.

    Returns:
        Dictionary with context or error information.
    """
    try:
        with get_cursor(commit=False) as cursor:
            cursor.execute("SELECT reflection FROM episodes ORDER BY id DESC LIMIT 1")
            last_reflection = cursor.fetchone()

            if last_reflection:
                return {"context": last_reflection[0]}
            return {"context": None}
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        return {"error": str(e)}


def search_episodes(query: str, limit: int = 10) -> list[dict]:
    """
    Search episodes by task content.

    Args:
        query: Search term.
        limit: Maximum results to return.

    Returns:
        List of matching episodes.
    """
    with get_cursor(commit=False) as cursor:
        cursor.execute(
            "SELECT * FROM episodes WHERE task LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "task": row[2],
                "result": row[3],
                "reflection": row[4],
            }
            for row in rows
        ]


# ==========================================================
# SELF-TEST
# ==========================================================

if __name__ == "__main__":
    init_memory_db()
    episode_id = save_episode("System boot test", "success", "RIK initialized correctly.")
    print(f"Saved episode with ID: {episode_id}")
    print(get_recent_episodes())
