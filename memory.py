"""
memory.py | Recursive Intelligence Kernel (RIK)
-----------------------------------------------
Handles persistent episodic and semantic memory.
Now includes:
✅ Centralized DB path management
✅ Exception handling via DatabaseException
✅ Semantic TF-IDF search
✅ DBSCAN consolidation
✅ Legacy alias (init_memory_db)
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np
from exceptions import DatabaseException


# ============================================================
# 🔹 Database Path Management
# ============================================================

def get_db_path() -> str:
    """Return the absolute path to the memory database."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "memory.db")


# ============================================================
# 🔹 Initialization
# ============================================================

def initialize_database():
    """Create the database and required tables if not exist."""
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        # episodes table
        c.execute(
            """CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task TEXT,
                reflection TEXT
            )"""
        )

        # episodic_memory table for fail-safe / fallback learning
        c.execute(
            """CREATE TABLE IF NOT EXISTS episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event TEXT,
                outcome TEXT
            )"""
        )

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseException(f"Database initialization failed: {e}")


# ============================================================
# 🔹 Episode Management
# ============================================================

def save_episode(task: str, reflection: str = "") -> None:
    """Save a new episode to memory."""
    initialize_database()
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        c.execute(
            "INSERT INTO episodes (timestamp, task, reflection) VALUES (?, ?, ?)",
            (timestamp, task, reflection),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseException(f"Failed to save episode: {e}")


def get_recent_episodes(limit: int = 5):
    """
    Return the most recent episodic memory entries from the database.

    Args:
        limit: Maximum number of episodes to retrieve

    Returns:
        List of episode dictionaries

    Raises:
        DatabaseException: If database query fails
    """
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute(
            "SELECT id, timestamp, task, reflection FROM episodes ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "task": r[2],
                "reflection": r[3],
            }
            for r in rows
        ]
    except sqlite3.Error as e:
        raise DatabaseException(f"Database query failed: {e}")


# ============================================================
# 🔹 Semantic Retrieval
# ============================================================

def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Perform semantic search to retrieve top-k related episodes.
    """
    initialize_database()
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT id, task, reflection FROM episodes")
        rows = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseException(f"Failed to fetch episodes for semantic search: {e}")

    if not rows:
        return []

    docs = [f"{r[1]} {r[2]}" for r in rows]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(docs + [query])
    similarities = np.dot(vectors[-1].toarray(), vectors[:-1].T.toarray())[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    return [
        {
            "id": rows[i][0],
            "task": rows[i][1],
            "reflection": rows[i][2],
            "score": float(similarities[i]),
        }
        for i in top_indices
    ]


# ============================================================
# 🔹 Consolidation with DBSCAN
# ============================================================

def consolidate_episodes(eps: float = 0.5, min_samples: int = 2) -> Dict[str, Any]:
    """
    Cluster similar episodes and consolidate reflections.
    """
    initialize_database()
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute("SELECT id, task, reflection FROM episodes")
        rows = c.fetchall()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseException(f"Failed to fetch episodes for consolidation: {e}")

    if not rows:
        return {"clusters": 0, "consolidated": []}

    tasks = [r[1] for r in rows]
    reflections = [r[2] for r in rows]

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(tasks)
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X.toarray())

    clusters = {}
    for label, row in zip(clustering.labels_, rows):
        clusters.setdefault(label, []).append(row)

    consolidated = []
    for label, items in clusters.items():
        if label == -1:
            continue  # noise
        combined_task = " ".join([i[1] for i in items])
        combined_reflection = " ".join([i[2] for i in items])
        save_episode(f"consolidated_cluster_{label}", combined_reflection)
        consolidated.append(
            {
                "cluster_id": label,
                "task": combined_task,
                "reflection": combined_reflection,
                "count": len(items),
            }
        )

    return {"clusters": len(clusters), "consolidated": consolidated}


# ============================================================
# 🔹 Legacy Compatibility Alias
# ============================================================

# Old test suite calls this older function name:
init_memory_db = initialize_database